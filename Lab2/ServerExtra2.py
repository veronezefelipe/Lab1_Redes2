from socket import *
import time

# Configurações do servidor
server_port = 12000
heartbeat_interval = 2  # Intervalo de tempo esperado entre heartbeats (em segundos)

# Criar o socket UDP
server_socket = socket(AF_INET, SOCK_DGRAM)
server_socket.bind(('', server_port))
print("Servidor de Heartbeat UDP pronto para receber pacotes...")

last_sequence = -1
last_heartbeat_time = time.time()

while True:
    try:
        # Configuração de tempo limite para detectar perda de pacotes
        server_socket.settimeout(heartbeat_interval * 2)
        
        # Receber o pacote do cliente
        message, client_address = server_socket.recvfrom(1024)
        current_time = time.time()
        
        # Extrair número de sequência e timestamp do pacote
        message_parts = message.decode().split(",")
        sequence_number = int(message_parts[0])
        client_timestamp = float(message_parts[1])

        # Calcular diferença de tempo (RTT simulado) e pacotes perdidos
        time_difference = current_time - client_timestamp
        lost_packets = sequence_number - last_sequence - 1

        # Relatar perda de pacotes se houver
        if lost_packets > 0:
            print(f"Pacotes perdidos: {lost_packets}")

        # Exibir informações do heartbeat recebido
        print(f"Heartbeat recebido - Seq: {sequence_number}, RTT: {time_difference:.6f} segundos")

        # Atualizar número de sequência e tempo do último heartbeat recebido
        last_sequence = sequence_number
        last_heartbeat_time = current_time

    except socket.timeout:
        # Caso o heartbeat seja ausente por mais que o dobro do intervalo esperado
        print("Cliente inativo - Nenhum heartbeat recebido no intervalo esperado.")
        break
