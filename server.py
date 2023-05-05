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

#objeto RDT instanciado, indicando ser um servidor
RDTSocket = RDT(1)
data = RDTSocket.receive()

#espera a mensagem 'chefia'
data = hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()

#continua o mesmo processo, enquanto não receber um `chefia`
while(data.decode() != "chefia"):
  data = hour() + " cliente:"
  RDTSocket.send_pkg(data.encode())
  data = RDTSocket.receive()

#espera o cliente pedir uma mesa, e armazena a info
data = hour() + " CINtofome: Digite Sua mesa\n" + hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()
table = data.decode()

#espera o cliente dizer o nome, e armazena a info
data = hour() + " CINtofome: Digite Seu nome: \n" + hour() + " cliente: "
RDTSocket.send_pkg(data.encode())
data = RDTSocket.receive()
name = data.decode()

#tupla com IP e porta do cliente
ipPorta = RDTSocket.sender_addr

#insere mesa
if table not in orders:
  orders[table] = {
    "total": 0.0 
    }
  
#insere cliente
orders[table].update({
  name: {
      "nome": name, 
      "comanda": 0.0,
      "socket": ipPorta,
      "pedidos": []
    }
  })

#informa os comandos disponiveis do ChatBot
data = f"{hour()} CINtofome: Digite uma das opcoes a seguir (ou numero ou por extenso) \n {options}{hour()} {name}: "
RDTSocket.send_pkg(data.encode())

payment = True

#pós cadastro, entra num loop até receber o comando levantar
while True:
  #recebe o comando do cliente
  req = RDTSocket.receive()
  data = req.decode('utf8')

  match data:
    #opção para mostrar o cardápio
    case '1' | 'cardápio':
      res = hour() + " CINtofome:\n" + showMenu() + hour() + " " + name + ": "
    #opção para fazer o pedido
    case '2' | 'pedir':
      res = hour() + " CINtofome: Digite o primeiro item que gostaria (número) \n" + hour() +" " + name +": "  
      RDTSocket.send_pkg(res.encode())
      data = RDTSocket.receive()
      #entra num loop, enquanto o cliente não encerrar o pedido com o comando "não", o server continua perguntando se tem mais algo
      while True:
        allOrders(table,name,data)

        resp = hour() + " CINtofome : Gostaria de mais algum item? (número ou por extenso) \n" + hour() +" " + name + ": "
        RDTSocket.send_pkg(resp.encode())
        data = RDTSocket.receive() 

        if(str(data.decode()) == "nao"):
          break
      resp = hour() + " CINtofome: É pra já! \n" + hour() +" " + name + ": "
      payment = False

    #opção para a conta ser apenas do cliente em contato com o servidor
    case '3' | 'conta individual':
      total,value = getOrdersByClient(table,name)
      res = f"CINtofome: Sua conta total é:\n{total}-------------\nValor: {str(value)}"
      res += f"\n{hour()} {name}: "

    #opção para a conta ser de toda a mesa, na qual está sentado o cliente em contato com o servidor
    case '4'| 'conta da mesa':
      total = str(orders[table]["total"])
      res = f"CINtofome:\n"

      for client in orders[table]:
        if client != "total":
          total,value = getOrdersByClient(table,client)
          if value > 0:
            res += f"\n{client}\n{total}-------------\nValor: {str(value)}\n-------------"

        res += f"\nValor total da mesa: {total}" 
        res += f"\n{hour()} {name}: "

    #opção para que seja realizado o pagamento
    case '5' | 'pagar':
      bill = orders[table][name]["comanda"]
      closed = orders[table]["total"]
      valid = False
      dif = 0

      #mostra o valor tal da conta do cliente, e da mesa. e aguarda o comando de pagamento
      base = f"Sua conta foi {bill} e a da mesa foi {closed}. Digite o valor a ser pago. \n{hour()} {name}: "
      res = f"{hour()} CINtofome: {base}"
      RDTSocket.send_pkg(res.encode())
      data = RDTSocket.receive() 
      data = data.decode()

      #loop para validação do pagamento 
      while True:
        if str(data) == 'nao':  
          res = f"{hour()} CINtofome: Operação de pagamento cancelada!"
          break

        if (valid and str(data) == 'sim'):   
          #remove pedido dos clientes da tabela     
          orders[table][name]["comanda"] = 0.0
          orders[table][name]["pedidos"] = []
          orders[table]["total"] -= bill

          #calculo do troco
          if dif > 0: 
            orders[table]["total"] -= dif
    
            #mostra e divide o valor extra dos clientes com pendencia
            pendingBill = [c for c in orders[table] if c != "total" and orders[table][c]["comanda"] > 0]
            dif_ind = dif/len(pendingBill)

            for client in pendingBill:
              orders[table][client]["comanda"] -= dif

          res = f"{hour()} CINtofome: Conta paga, obrigado! \n" 
          payment = True
          break

        if (float(data) > bill) and float(data) <= total: # Se tiver inserido um valor válido 
          dif = float(data) - bill
          res = f"{hour()} Cintofome: Você está pagando {dif} a mais que sua conta.\n{hour()} Cintofome: O valor excedente será distribuído.\n{hour()} Cintofome: "
          valido = True
          RDTSocket.send_pkg(resp.encode())
        elif (float(data) == bill): # Pagamento exato
          res = f"{hour()} Cintofome: "
          valido = True
        elif (float(data) > total): # Se tiver inserido um valor maior do que a conta da mesa
          res = f"{hour()} Cintofome: Valor maior do que o esperado, no momento não aceitamos gorjetas. \n" + base
        elif (float(data) < bill): # Se tiver inserido um valor menor que a conta individual
          res = f"{hour()} Cintofome: Pagamento menor que o devido, nao fazemos fiado. \n" + base

        if valido:
          res += f"Deseja confirmar o pagamento? (digite sim para confirmar)\n{hour()} {name}: "

        RDTSocket.send_pkg(res.encode())
        data = RDTSocket.receive()
        data = data.decode()

      res += f"{hour()} {name}: "

    #opção para levantar e encerrar conexão
    case ('6' | 'levantar'):
      #se não tiver pago, nn permite encerrar a conexão
      if(not payment):
        res = hour() + " " + name + ": Você ainda não pagou sua conta\n" + hour() + " " + name + ": "

      #se tiver pago, libera o cliente e encerra conexão
      if(payment):
        res = "ok"
        del orders[table][name]
        RDTSocket.send_pkg(resp.encode())
        break

      RDTSocket.send_pkg(resp.encode())

# se despede termina a conexão
data = hour() + " " + name + ": Volte sempre ^^ \n"
RDTSocket.send_pkg(data.encode())

RDTSocket.close_connection()