from socket import *
import time
from aux_functions import extract_packet, send_packet, wait_for_ack, send_ack, packet_loss, Packet
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB

class RDT:
  #projeto ja se inicia com valores pré-setados
  def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
    self.sender_addr = 0
    self.seq_num = 0 
    self.addressPort = addressPort
    self.bufferSize = bufferSize
    self.UDPSocket = socket(AF_INET, SOCK_DGRAM)
    self.isServer = isServer

  #faz a checagem pra ver se trata de um servidor, caso sim alocamos uma porta e um endereçoIP para o pacote
    if isServer:
        self.UDPSocket.bind(self.addressPort)
        self.UDPSocket.settimeout(2.0)
        """print("Server running")"""
    else:
        """ print("Client running") """

  #função para transferencia de pacotes
  def send(self, data):
    if self.isServer:
        """ print("Sending to client") """
        self.UDPSocket.sendto(data, self.sender_addr)
    else:
        """ print("Sending to server") """
        self.UDPSocket.sendto(data, self.addressPort)

  def send_pkg(self, data):
    data = self.create_header(data.decode())
    ack = False

        #envia o pacote enquanto o bit ACK for falso
    while not ack:
      self.send(data)

      try:
        data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
      except socket.timeout:
            print("Did not receive ACK. Sending again.")
      else:
        ack = self.rcv_ack(data)

  def rcv_pkg(self, data):
    data = eval(data.decode())
    seq_num = data['seq']
    checksum = data['checksum']
    payload = data['payload']

    #Verifica se a mensagem chegou por completo ao checar o checksum e sinaliza ACK ou NACK
    if self.checksum_(checksum, payload) and seq_num == self.seq_num:
      self.send_ack(1)
      self.seq_num = 1 - self.seq_num
      return payload
    else:
      self.send_ack(0)
      return ""
  
  #Funcao de recepcao de pacotes entre cliente e servidor
  def receive(self):
    """ print("Receveing package") """
    self.UDPSocket.settimeout(20.0) 
    data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
    data = self.rcv_pkg(data)

    if data != "":
      buffer = data
      
      """ print("Received") """
      return buffer.encode()

  #Funcao que sinaliza no cabecalho o bit ACK ou NACK    
  def send_ack(self, ack):
    if ack:
        data = self.create_header("ACK")
    else:
        data = self.create_header("NACK")
    self.send(data)

  #Funcao que verifica o bit ACK recebido, e se o bit eh valido
  def rcv_ack(self, data):
    data = eval(data.decode())
    seq_num = data['seq']
    checksum = data['checksum']
    payload = data['payload']

    if self.checksum_(checksum, payload) and seq_num == self.seq_num and payload == "ACK":
      self.seq_num = 1 - self.seq_num
      return True
    else:
      return False

  #Funcao que chama o checksum para fazer a verificacao
  def checksum_(self, chcksum, payload):
    if checksum(payload) == chcksum:
        return True
    else:
        return False

  #Funcao que cria o cabecalho do pacote
  def create_header(self, data):

    chcksum = checksum(data)

    return str({
        'seq': self.seq_num,
        'checksum': chcksum,
        'payload' : data
    }).encode()

  #Funcao que encerra a conexao
  def close_connection(self):
    """ print("Closing socket") """
    self.UDPSocket.close()