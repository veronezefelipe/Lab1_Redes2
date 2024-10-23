import threading
from socket import *
import sys

def handle_client(connectionSocket): #sempre   quee um cliente conectar, ele chama esta  função
    try:
        message = connectionSocket.recv(1024).decode()  
        filename = message.split()[1]  
        f = open(filename[1:])  
        outputdata = f.read()  
        f.close()

        # Enviar cabeçalhos HTTP de sucesso
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())

        # Enviar o conteúdo do arquivo
        connectionSocket.send(outputdata.encode())

    except IOError:
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

    connectionSocket.close()  # Fechar a conexão


# Configurar o servidor
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', 5000))  
serverSocket.listen(5)  # Permite até 5 conexões na fila

while True:
    print('Pronto para servir...')
    connectionSocket, addr = serverSocket.accept()  # Aceitar conexão
    print(f'Conexão estabelecida com {addr}')

    
    client_thread = threading.Thread(target=handle_client, args=(connectionSocket,))
    client_thread.start()  # Iniciar a thread, permitindo que possam haver novas conexões

serverSocket.close()
sys.exit()