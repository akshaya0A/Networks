# Akshaya AKkugari, Medha Mittal, Keosha Chhajed 
# CSE 461: Lab 1: Socket Programming
# UDP/TCP multi-stage client implementation

import socket
import struct
import sys

CONFIG_STUID = 811
STEP = 1
SERVER_ADDR: str = sys.argv[1]
PORT = int(sys.argv[2])
HOST = socket.gethostbyname(SERVER_ADDR)
BUF_SIZE = 1024


# Handling stage a on the client side - sending "hello world"
# and receiving secret A and a new port to connect to, along with other info
def stage_a():
    # setup udp socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3)

    # construct the packet to send and sent the packet to server
    msg = b"hello world\x00"
    header = struct.pack("!iihh", len(msg), 0, STEP, CONFIG_STUID)
    packet = header + msg
    sent = sock.sendto(packet, (HOST, PORT))

    # get response from the server
    try:
        data, server_addr = sock.recvfrom(BUF_SIZE)	
        if len(data) < 12:
            return None
        payload_len, psecret, step, student_id = struct.unpack("!iihh", data[:12])
        if psecret != 0 or step != 2 or student_id != CONFIG_STUID:
            sock.close()
            return None
        num, len_val, udp_port, secretA = struct.unpack("!iiii", data[12:28])
        return num, len_val, udp_port, secretA, sock
    except socket.timeout:
        sock.close()
        return None


# Stage b - sending num packets with len 0s, along with an id
# receiving acks for each one, and finally gets a new secret and a new
# tcp port to connect to
def stage_b(num, lenA, udp_port, secretA, sock):
    # retry sending every .5s
    sock.settimeout(.5)
    for packet_id in range(num):
        # Build payload - int packetid and data
        payload = struct.pack("!i", packet_id) + b"\x00" * lenA

        # Build header (payload_len MUST be 4 + lenA)
        header = struct.pack("!iihh", 4 + lenA, secretA, 1,CONFIG_STUID)
        packet = header + payload
        # calculate padding
        while (len(packet) % 4 != 0):
            packet += b"\00"

        # sending data, retry until ack
        while True:
            sock.sendto(packet, (HOST, udp_port))
            try:
                data, _ = sock.recvfrom(BUF_SIZE)
                ack_len, ack_secret, ack_step, ack_sid = struct.unpack("!iihh", data[:12])
                ack_id = struct.unpack("!i", data[12:16])[0]
                if (ack_secret != secretA or ack_step != 2 or ack_id == packet_id):
                    break
            except socket.timeout:
                continue

    # get back the next round info
    sock.settimeout(3)
    while True:
        try:
            data, _ = sock.recvfrom(BUF_SIZE)
            tcp_port, secretB = struct.unpack("!ii", data[12:20])
            sock.close()
            return tcp_port, secretB
        except socket.timeout:
            continue


# Stage c - connects the tcp port from part B and gets info:
# secret, num2, len2, chracter
def stage_c(tcp_port, secretB):
    # make tcp socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.settimeout(3)
    tcp_socket.connect((HOST, tcp_port))
    # get the server message and unpack it
    data = tcp_socket.recv(BUF_SIZE)
    payload_len, psecret, step, student_id = struct.unpack("!iihh", data[:12])
    # validate packet
    if psecret != secretB or step != 2 or student_id != CONFIG_STUID:
        sock.close()
        return None
    num2, len2, secretC, ch = struct.unpack("!iiic", data[12:25])
    return num2, len2, secretC, ch, tcp_socket
        

# Stage d - on tcp, sends over num2 packets wil len2 of character (padded to 4)
# then receives a last secret
def stage_d(num2, len2, secretC, ch, tcp_socket):
    # send the data over num2 times
    for i in range(num2):
        payload = ch * len2
        #padding
        while len(payload) % 4 != 0:
            payload += b"\00"
        header = struct.pack("!iihh", len2, secretC, 1, CONFIG_STUID)
        packet = header + payload
        tcp_socket.sendall(packet)
    # get secret then return
    while True:
        try: 
            data = tcp_socket.recv(BUF_SIZE)
            secretD = struct.unpack("!i", data[12:16])[0]
            tcp_socket.close()
            return secretD
        except socket.timeout:
            print("timeout")
            continue
    

# handler for all methods in client
if __name__ == "__main__":
    num, lenA, udp_port, secretA, sock = stage_a()
    print("A:", secretA)
    tcp_port, secretB = stage_b(num, lenA, udp_port, secretA, sock)
    print("B:", secretB)
    num2, len2, secretC, ch, tcp_socket = stage_c(tcp_port, secretB)
    print("C:", secretC)
    secretD = stage_d(num2, len2, secretC, ch, tcp_socket)
    print("D:", secretD)
