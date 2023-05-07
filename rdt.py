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
        # self.UDPSocket.sendto(data, self.sender_addr)
        self.seq_num = sock_send(data, self.UDPSocket, self.seq_num, self.sender_addr)
    else:
        """ print("Sending to server") """
        #self.UDPSocket.sendto(data, self.addressPort)
        self.seq_num = sock_send(data, self.UDPSocket, self.seq_num, self.addressPort)
  
  #Funcao de recepcao de pacotes entre cliente e servidor
  def receive(self):
    """ print("Receveing package") """
    self.UDPSocket.settimeout(20.0) 
    # data, self.sender_addr = self.UDPSocket.recvfrom(self.bufferSize)
    data, self.seq_num, self.sender_addr = sock_receive(self.UDPSocket, self.seq_num)

    if data != "":
      
      """ print("Received") """
      return data.decode('utf-8')

  #Funcao que encerra a conexao
  def close_connection(self):
    """ print("Closing socket") """
    self.UDPSocket.close()

def chunk_divide(data, head_size):
  data_bytes = data.encode('utf-8')

  chunk_size = BUFFER_SIZE - head_size

  chunks = [data_bytes[i:i+chunk_size] for i in range(0, len(data_bytes), chunk_size)]

  return chunks

def sock_receive(sock, expected_seq_num):
    received_data = "".encode('utf-8')

    while True:
        try:
          # Recebe um pacote 
            data, addr = sock.recvfrom(BUFFER_SIZE)
            packet = extract_packet(data)
            # filename = packet.data
            if packet.seq_n == expected_seq_num:
                # Avalia o checksum dele
                if packet.checksum == packet.real_checksum():
                    print(f"Pacote recebido: {packet.seq_n}")
                    send_ack(sock, packet.seq_n, addr)
                    expected_seq_num = 1 - expected_seq_num
                    received_data += packet.data.encode('utf-8')
                    if len(packet.data) + packet.reading_size() < BUFFER_SIZE:
                        break
                else:
                    print(f"Checksum incorreto: {packet.checksum}, esperado: {packet.real_checksum()}")
                    send_ack(sock, 1 - expected_seq_num, addr)
            else:
                print(f"Pacote incorreto: {packet.seq_n}, enviando ACK anterior")
                send_ack(sock, 1 - expected_seq_num, addr)
        except socket.timeout:
            print(
                f"Tempo limite de {TIMEOUT_LIMIT} segundos atingido. Encerrando conexão...")
            break

    return data, expected_seq_num, addr 

def sock_send(message, sock, seq_num, addr):

    packet = Packet(seq_num, False, "")

    chunks = sock.chunk_divide(message, packet.reading_size()) 

    for data in chunks:
        while True:
            # Envia o pedaço de arquivo para o cliente usando rdt3.0
            packet = Packet(seq_num, False, data.decode('utf-8'))
            # print(f"Enviando pacote {seq_num}")
            send_packet(sock, packet, addr)
            ack_received = wait_for_ack(sock, seq_num)
            if ack_received:
                seq_num = 1 - seq_num

                packet = Packet(seq_num, False, "")
                break
            else:
                print("Reenviando pacote...")
    
    return seq_num