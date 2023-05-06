from socket import *
from rdt import *

#instanciando um cliente
RDTSocket = RDT()

#mensagem vazia pra o contato com servidor
data = ''

while True:
  
  RDTSocket.send(data.encode())

  msg = RDTSocket.receive()

  #receber 'ok', encerra a conexão
  if('ok' == msg):
    break
  
  data = input(msg)

msg = RDTSocket.receive()
print(msg)

RDTSocket.close_connection()