import os
import sys
import struct
import time
import select
import socket
from socket import *

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2


def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xFFFFFFFF
        count = count + 2

    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)
    return answer


def build_packet():
    my_checksum = 0
    my_id = os.getpid() & 0xFFFF
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, my_checksum, my_id, 1)
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, 0, htons(my_checksum), my_id, 1
    )
    return header + data


def get_route(hostname):
    dest_addr = gethostbyname(hostname)
    print(f"Traceroute para {hostname} ({dest_addr}):")

    for ttl in range(1, MAX_HOPS + 1):
        for tries in range(TRIES):
            try:
                my_socket = socket(AF_INET, SOCK_RAW, getprotobyname("icmp"))
            except PermissionError:
                print("Erro: Permissões insuficientes. Rode o script como root.")
                sys.exit()

            my_socket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack("I", ttl))
            my_socket.settimeout(TIMEOUT)

            try:
                packet = build_packet()
                my_socket.sendto(packet, (hostname, 0))
                t_start = time.time()

                ready = select.select([my_socket], [], [], TIMEOUT)
                if not ready[0]:
                    print(f"{ttl}\tTimed out.")
                    continue

                recv_packet, addr = my_socket.recvfrom(1024)
                t_end = time.time()

                try:
                    host_name = gethostbyaddr(addr[0])[0]
                except herror:
                    host_name = addr[0]

                icmp_header = recv_packet[20:28]
                icmp_type, _, _, _, _ = struct.unpack("bbHHh", icmp_header)

                if icmp_type == 11:  
                    print(f"{ttl}\trtt={int((t_end - t_start) * 1000)} ms\t{host_name}")
                elif icmp_type == 3:  
                    print(f"{ttl}\trtt={int((t_end - t_start) * 1000)} ms\t{host_name}")
                elif icmp_type == 0:  
                    print(f"{ttl}\trtt={int((t_end - t_start) * 1000)} ms\t{host_name}")
                    print("Destino alcançado.")
                    return
                else:
                    print(f"{ttl}\tResposta ICMP inesperada.")

            except timeout:
                print(f"{ttl}\tTimed out.")
            finally:
                my_socket.close()


if __name__ == "__main__":
    get_route("veroneze.com")        
    #get_route("www.bbc.co.uk")        
    #get_route("www.alibaba.com")       
    #get_route("www.sydneyoperahouse.com")  
