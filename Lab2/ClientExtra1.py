import time
from socket import *

# Configurações do cliente
server_name = 'localhost'  
server_port = 12000  

client_socket = socket(AF_INET, SOCK_DGRAM)

client_socket.settimeout(1) 

rtts = []
pings_enviados = 10
pings_ok = 0

for i in range(1, pings_enviados + 1):
    message = f'Ping {i}'
    try:
        start_time = time.time()  # Horário do envio da mensagem
        client_socket.sendto(message.encode(), (server_name, server_port))  # Enviando mensagem ao servidor

        response, server_address = client_socket.recvfrom(1024)  # Recebendo resposta do servidor
        rtt = time.time() - start_time  # Tempo de resposta (RTT)

        
        rtts.append(rtt) # Adc o rtt ao array
        pings_ok += 1

        print(f'Ping {i} {response.decode()} {rtt:.6f} segundos')

    except socket.timeout:
        print(f'Ping {i}: Timed out')

client_socket.close()

# Cálculo dos RTTs mínimo, máximo e médio
if pings_ok > 0:
    min_rtt = min(rtts)
    max_rtt = max(rtts)
    avg_rtt = sum(rtts) / pings_ok
else:
    min_rtt = max_rtt = avg_rtt = float('nan')  # Se não houver pings bem-sucedidos

percent = ((10 - pings_ok) / pings_enviados) * 100

# Exibição dos resultados

print(f'Percentual: {percent:.2f}%')
print(f'Mín: {min_rtt:.6f} segundos')
print(f'Máx: {max_rtt:.6f} segundos')
print(f'Médio: {avg_rtt:.6f} segundos')
