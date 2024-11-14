import os 
import sys 
import socket 
import struct 
import select 
import time

default_timer = time.time
ICMP_ECHO_REQUEST = 8

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def receiveOnePing(my_socket, ID, timeout):
    timeLeft = timeout
    while True:
        startedSelect = default_timer()
        whatReady = select.select([my_socket], [], [], timeLeft)
        howLongInSelect = (default_timer() - startedSelect)
        if whatReady[0] == []:
            return

        timeReceived = default_timer()
        recPacket, addr = my_socket.recvfrom(1024)
        icmpHeader = recPacket[20:28]
        type, code, checksum, packetID, sequence = struct.unpack(
            "bbHHh", icmpHeader
        )
        if type == 3: 
            error_messages = {
                0: "Rede de Destino Inalcançável",
                1: "Host de Destino Inalcançável",
                2: "Protocolo de Destino Inalcançável",
                3: "Porta de Destino Inalcançável",
                4: "Fragmentação Necessária e DF Set",
                5: "Falha de Rota de Origem",
                6: "Rede de Destino Desconhecida",
                7: "Host de Destino Desconhecido",
                9: "Rede de Destino Proibida",
                10: "Host de Destino Proibido",
                13: "Comunicação Administrativamente Proibida"
            }
            error_message = error_messages.get(code, "Erro ICMP Desconhecido")
            print(f"Erro ICMP Recebido: {error_message} (Código {code})")
            return None

        if type == 0 and packetID == ID:  
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return

def sendOnePing(my_socket, dest_addr, ID):
    dest_addr = socket.gethostbyname(dest_addr)
    my_checksum = 0
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", default_timer()) + data.encode('utf-8')
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), ID, 1
    )
    packet = header + data
    my_socket.sendto(packet, (dest_addr, 1))

def doOnePing(dest_addr, timeout):
    icmp = socket.getprotobyname("icmp")
    try:
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        errno, msg = e.args
        if errno == 1:
            msg = msg + (
                " - Note that ICMP messages can only be sent from processes"
                " running as root."
            )
        raise socket.error(msg)

    my_ID = os.getpid() & 0xFFFF
    sendOnePing(my_socket, dest_addr, my_ID)
    delay = receiveOnePing(my_socket, my_ID, timeout)
    my_socket.close()
    return delay

def ping(dest_addr, timeout=1, count=4):
    rtts = []
    lost_packets = 0

    for i in range(count):
        print("Ping %d -" % (i + 1), end=" ")
        try:
            delay = doOnePing(dest_addr, timeout)
        except socket.gaierror as e:
            print("falhou. (socket error: '%s')" % e.args[1])
            lost_packets = count
            break

        if delay is None:
            print("falhou. (timeout dentro de %s sec.)" % timeout)
            lost_packets += 1
        else:
            delay = delay * 1000
            rtts.append(delay)
            print("%0.6f ms" % delay)

    if rtts:
        min_rtt = min(rtts)
        max_rtt = max(rtts)
        avg_rtt = sum(rtts) / len(rtts)
    else:
        min_rtt = max_rtt = avg_rtt = 0.0

    packet_loss = (lost_packets / count) * 100

    print("Pacotes recebidos: %d" % (count - lost_packets))
    print("Porcentagem de pacotes perdidos: %.1f%%" % (packet_loss))

    if rtts:
        print("RTT min = %.6f ms" % min_rtt)
        print("RTT avg = %.6f ms" % avg_rtt)
        print("RTT max = %.6f ms \n" % max_rtt)
    else:
        print("Sem resposta recebida. \n")

if __name__ == '__main__':
    ping("127.0.0.1")
    ping("store.steampowered.com")
    ping("sea.battle.net")
    ping("us1.vpnbook.com")
