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