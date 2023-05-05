import socket
import time
from aux_functions import extract_packet, send_packet, wait_for_ack, send_ack, packet_loss, Packet
from constants import BUFFER_SIZE, TIMEOUT_LIMIT, UDP_IP, UDP_PORT, PACKET_LOSS_PROB

class RDT:
    #projeto ja se inicia com valores pré-setados
    def __init__(self, isServer = 0, addressPort = ("127.0.0.1", 20001), bufferSize = 1024):
        self.sender_addr = 0
        self.seq_num = 0 
        self.addressPort = addressPort
        self.bufferSize = bufferSize(AF_INET, SOCKET_DGRAM)
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

    def send_packet(self, data):
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