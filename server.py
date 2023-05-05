from socket import *
from rdt import *
from datetime import *
from utils import *

#pega a hora e formata (horario)
def hour():
    clock = datetime.now()
    return clock.strftime("%X")[:5]

#pedidos feitos (pedidos)
orders = {}

#mostra o cardapio (showCardapio)
def showMenu():
    card = ''
    for x, y in menu.items():
        card = card + " " + str(x) + " " + str(y[0]) + " " + " " + str(y[1]) + "\n"
    return card

#adiciona o pedido ao banco de dados de acordo com o cliente (pedido)
def allOrders(table, client, data):
  
  #pega o item do cardapio que foi pedido
  food = menu.get(int(data.decode()))

  #adiciona o pedido,e atualiza o valor na conta da mesa e do cliente
  orders[table][client]["pedidos"].append(food)
  orders[table]["total"] += float(food[1])
  orders[table][client]["comanda"] += float(food[1])
  
#retorna os pedidos de um cliente específico, e o valor total do pedidos (pedir_conta)	
def getOrdersByClient(table, client):
  total = '\n'
  value = orders[table][client]["comanda"]

  for produto in orders[table][client]["pedidos"]:
    total += f"{produto[0]} -> {str(produto[1])} '\n"
  
  return total,value

RDTSocket = Rdt('server')
data = RDTSocket.receive()
#espera a mensagem 'chefia'
data = hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()

while(data.decode() != "chefia"):
  data = hour() + " cliente:"
  RDTSocket.send_pkg(data.encode())
  data = RDTSocket.receive()


data = hour() + " CINtofome: Digite Sua mesa\n" + hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()
table = data.decode()

#manda uma requisição de nome pro cliente, e espera a resposta
data = hour() + " CINtofome: Digite Seu nome: \n" + hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()
nome = data.decode()

#tupla com IP e porta do cliente
ipPorta = RDTSocket.sender_addr

#insere mesa
if table not in orders:
  orders[table] = {
    "total": 0.0 
    }
  
#insere cliente
orders[table].update({
  nome: {
      "nome": nome, 
      "comanda": 0.0,
      "socket": ipPorta,
      "pedidos": []
    }
  })

#informa os comandos disponiveis
data = f"{hour()} CINtofome: Digite uma das opcoes a seguir (ou numero ou por extenso) \n {options}{hour()} {nome}: "
RDTSocket.send_pkg(data.encode())

not_payment = True

#depois de cadastrado, entra num loop até receber o comando levantar
while True:
   #recebe a opcao desejada
   req = RDTSocket.receive()
   data = req.decode('utf8')

   match data:
      
      case '1' | 'cardápio':
        res = hour() + " CINtofome:\n" + showMenu() + hour() + " " + nome + ": "

      case '2' | 'pedir':
        res = hour() + " CINtofome: Digite o primeiro item que gostaria (número) \n" + hour() +" " + nome +": "  
        RDTSocket.send_pkg(res.encode())
        data = RDTSocket.receive()

      case 'nao':
        res = hour() + " CINtofome: É pra já! \n" + hour() +" " + nome + ": "
        not_payment = False

      case '3' | 'conta individual':
        total,value = getOrdersByClient(table,nome)
        res = f"CINtofome: Sua conta total é:\n{value}-------------\nValor: {str(value)}"
        res += f"\n{hour()} {nome}: "

      case '4'| 'conta da mesa':
        total = str(orders[table]["total"])
        res = f"CINtofome:\n"

        for client in orders[table]:
          if client != "total":
            total,value = getOrdersByClient(table,client)
            if value > 0:
              res += f"\n{client}\n{total}-------------\nValor: {str(value)}\n-------------"

          res += f"\nValor total da mesa: {total}" 
          res += f"\n{hour()} {nome}: "

      case '5' | 'pagar':
        comanda = allOrders[table][nome]["comanda"]
        fechada = allOrders[table]["total"]
        valido = False
        dif = 0

        # Repassa valores para o cliente e aguarda pagamento
        base = f"Sua conta foi {comanda} e a da mesa foi {fechada}. Digite o valor a ser pago. \n{hour()} {nome}: "
        res = f"{hour()} CINtofome: {base}"
        RDTSocket.send_pkg(res.encode())
        data = RDTSocket.receive() 
        data = data.decode()

        while True:

          match data:  
            case 'nao':
              res = f"{horario()} CINtofome: Operação de pagamento cancelada!"
              break

            case valido & 'sim':       
              allOrders[table][nome]["comanda"] = 0.0
              allOrders[table][nome]["pedidos"] = []
              allOrders[table]["total"] -= comanda

              if dif > 0: 
                allOrders[table]["total"] -= dif
          
           
                com_conta = [c for c in allOrders[table] if c != "total" and allOrders[table][c]["comanda"] > 0]
                dif_ind = dif/len(com_conta)

                for cliente in com_conta:
                  allOrders[table][client]["comanda"] -= dif

              res = f"{hour()} CINtofome: Conta paga, obrigado! \n" 
              not_payment = True
              break

        if (float(data) > comanda) and float(data) <= fechada: # Se tiver inserido um valor válido 
          dif = float(data) - comanda
          res = f"{hour()} Cintofome: Você está pagando {dif} a mais que sua conta.\n{hour()} Cintofome: O valor excedente será distribuído.{new_line}{horario()} Cintofome: "
          valido = True
          RDTSocket.send_pkg(resp.encode())
        elif (float(data) == comanda): # Pagamento exato
          res = f"{hour()} Cintofome: "
          valido = True
        elif (float(data) > fechada): # Se tiver inserido um valor maior do que a conta da mesa
          res = f"{hour()} Cintofome: Valor maior do que o esperado, no momento não aceitamos gorjetas. \n" + base
        elif (float(data) < comanda): # Se tiver inserido um valor menor que a conta individual
          res = f"{hour()} Cintofome: Pagamento menor que o devido, nao fazemos fiado. \n" + base
            
        if valido:
          res += f"Deseja confirmar o pagamento? (digite sim para confirmar)\n{hour()} {nome}: "

        RDTSocket.send_pkg(res.encode())
        data = RDTSocket.receive()
        data = data.decode()
        
        res += f"{hour()} {nome}: "

      case ('6' | 'levantar') & ~pagamento:
        res = hour() + " " + nome + ": Você ainda não pagou sua conta\n" + hour() + " " + nome + ": "

      case '6' | 'levantar' and pagamento:
        res = "ok"
        del allOrders[table][nome]
        RDTSocket.send_pkg(resp.encode())

        RDTSocket.send_pkg(resp.encode())

        data = hour() + " " + nome + ": Volte sempre ^^ \n"
        RDTSocket.send_pkg(data.encode())

        RDTSocket.close_connection()
