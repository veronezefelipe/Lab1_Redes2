from socket import *
import sys

serverSocket = socket(AF_INET, SOCK_STREAM) # Define IPV4 / Define conexao TCP *
serverSocket.bind(('', 5000))  # Vincula o socket à porta indicada
serverSocket.listen(1)  # Escuta 1 conexão por vez

while True:
    print('Pronto para servir...')
    connectionSocket, addr = serverSocket.accept()  # Cria o socket para comunicação com o cliente

    try:
        message = connectionSocket.recv(1024).decode()  # Recebe solicitação HTTP                                 
        filename = message.split()[1]  # Obter nome do arquivo                     Cabeçalho  HTTP
        f = open(filename[1:])  # Abrir o arquivo HTML
        outputdata = f.read()  # Ler conteúdo do arquivo
        f.close()

        # Enviar cabeçalhos HTTP de sucesso
        connectionSocket.send("HTTP/1.1 200 OK\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())

        # Enviar o conteúdo do arquivo
        connectionSocket.send(outputdata.encode())

    except IOError:
        # Enviar resposta 404
        connectionSocket.send("HTTP/1.1 404 Not Found\r\n".encode())
        connectionSocket.send("Content-Type: text/html\r\n\r\n".encode())
        connectionSocket.send("<html><body><h1>404 Not Found</h1></body></html>\r\n".encode())

    connectionSocket.close()  # Fechar a conexão

serverSocket.close()
sys.exit()  # Encerrar o programa após enviar os dados