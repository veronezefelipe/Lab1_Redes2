from socket import *
import sys

if len(sys.argv) <= 1:
    print('Uso: "python ProxyServer.py server_ip"\n[server_ip: Endereço IP do Servidor Proxy]')
    sys.exit(2)

# Cria um socket do servidor, vincula-o a uma porta e começa a escutar
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind((sys.argv[1], 8888))
tcpSerSock.listen(10)

while True:
    try:
        print('Pronto para servir...')
        tcpCliSock, addr = tcpSerSock.accept()
        print('Conexão recebida de:', addr)

        message = tcpCliSock.recv(1024).decode()
        print(message)
        
        filename = message.split()[1].partition("//")[2].replace('/', '_')
        print("Arquivo requisitado:", filename)

        try:
            # Tenta ler do cache
            with open(filename, "rb") as f:
                body = f.read()  # Lê apenas o corpo do cache

            # Cria o cabeçalho HTTP
            header = (
                f"HTTP/1.1 200 OK\r\n"
                f"Content-Type: text/html\r\n"
                f"Content-Length: {len(body)}\r\n\r\n"
            )
            tcpCliSock.sendall(header.encode() + body)
            print('Lido do cache e enviado ao cliente')
        except IOError:
            print(f"{filename} não encontrado no cache.")
            try:
                # Extrai o hostname e o arquivo requisitado
                hostn = message.split()[1].partition("//")[2].partition("/")[0]
                askFile = '/' + message.split()[1].partition("//")[2].partition("/")[2]
                
                # Conecta ao servidor remoto
                with socket(AF_INET, SOCK_STREAM) as c:
                    c.connect((hostn, 80))  # Conexão com o servidor remoto
                    c.sendall(f"GET {askFile} HTTP/1.1\r\nHost: {hostn}\r\nConnection: close\r\n\r\n".encode())
                    
                    # Recebe a resposta completa
                    response = b""
                    while True:
                        chunk = c.recv(1024)
                        if not chunk:
                            break
                        response += chunk

                # Valida se a resposta contém cabeçalho e corpo
                if b'\r\n\r\n' in response:
                    header, body = response.split(b'\r\n\r\n', 1)
                else:
                    header, body = response, b""

                # Salva apenas o corpo no cache
                if body.strip():
                    with open(filename, "wb") as f:
                        f.write(body)  # Salva apenas o corpo no cache
                    print("Lido do servidor remoto e armazenado no cache")
                else:
                    print("Resposta do servidor remoto está vazia ou incompleta.")

                # Envia a resposta completa ao cliente
                tcpCliSock.sendall(response)
            except Exception as e:
                print(f"Erro ao conectar ao servidor remoto: {e}")
                tcpCliSock.sendall("HTTP/1.0 404 Not Found\r\nContent-Length: 0\r\n\r\n".encode())

    except Exception as e:
        print(f"Erro ao processar solicitação: {e}")
    finally:
        tcpCliSock.close()

tcpSerSock.close()
