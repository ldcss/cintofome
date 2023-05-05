from socket import *
from rdt import *

#instanciando um cliente
RDTSocket = Rdt()

#mensagem vazia pra o contato com servidor
data = ''


while True:
	msg = RDTSocket.receive()

	#receber 'ok', encerra a conexão
	if('ok' == msg.decode('utf-8')):
			break
	data = RDTSocket.receive()

msg = RDTSocket.receive()
print(msg.decode())

RDTSocket.close_connection()