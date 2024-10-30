import time
from socket import *

server_name = 'localhost'  
server_port = 12000  

client_socket = socket(AF_INET, SOCK_DGRAM)

client_socket.settimeout(1) 

for i in range(1, 11):
    message = f'Ping {i}'
    try:
        
        start_time = time.time() # Horário do envio da mensagem

        client_socket.sendto(message.encode(), (server_name, server_port))  # Enviando msg ao servidor

        response, server_address = client_socket.recvfrom(1024)  # Recebendo resposta do server

        rtt = time.time() - start_time # Tempo de resposta (RTT)

        print(f'Ping {i} {rtt:.6f} segundos')

    except socket.timeout:
        print(f'Ping {i} Timed out')

# Fechar o socket
client_socket.close()
