from socket import *
from rdt import *

#instanciando um cliente
RDTSocket = RDT()

#mensagem vazia pra o contato com servidor
data = ''

while True:
  
  RDTSocket.send_pkg(msg.encode())

  msg = RDTSocket.receive()

  #receber 'ok', encerra a conexão
  if('ok' == msg.decode('utf-8')):
    break
  
  data = input(msg.decode('utf8'))

msg = RDTSocket.receive()
print(msg.decode())

RDTSocket.close_connection()