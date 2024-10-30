from socket import *
import time

# Configurações do cliente
server_name = 'localhost'
server_port = 12000
heartbeat_interval = 10  # Intervalo de tempo entre os heartbeats (em segundos)

# Criar o socket UDP
client_socket = socket(AF_INET, SOCK_DGRAM)

sequence_number = 0

try:
    while True:
        # Criar a mensagem com número de sequência e timestamp
        timestamp = time.time()
        message = f"{sequence_number},{timestamp}"

        # Enviar o heartbeat para o servidor
        client_socket.sendto(message.encode(), (server_name, server_port))
        print(f"Heartbeat enviado - Seq: {sequence_number}, Timestamp: {timestamp}")

        # Incrementar número de sequência e esperar até o próximo heartbeat
        sequence_number += 1
        time.sleep(heartbeat_interval)

except KeyboardInterrupt:
    print("Cliente interrompido pelo usuário.")
finally:
    # Fechar o socket ao finalizar o cliente
    client_socket.close()
