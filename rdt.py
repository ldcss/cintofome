from socket import *
from aux_functions import checksum
import time

class Rdt:
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

    def shutDown(self):
         """ print("Closing socket") """
        self.UDPSocket.close()