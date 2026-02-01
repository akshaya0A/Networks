import socket
import struct
import time
import errno
import numpy as np

import sys

CONFIG_STUID = 811
STEP = 1
SERVER_ADDR: str = "attu2.cs.washington.edu"
#SERVER_ADDR: str = "attu3.cs.washington.edu"
PORT = 41201
HOST = socket.gethostbyname(SERVER_ADDR)
# packet_data = struct.pack("iihh", payload_len, psecret, STEP, CONFIG_STUID)

def stage_a():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    print ("UDP target IP:", HOST)
    print ("UDP target Port:", PORT)
    msg = b"hello world\x00"

    header = struct.pack("iihh", len(msg), 0, STEP, CONFIG_STUID)
    packet = header + msg

    # send to server
    sent = sock.sendto(packet, (HOST, PORT))
    print(f"Bytes sent: {sent}")
    # get reponse
    try:
        data, server_addr = sock.recvfrom(41201)	
        print(f"Received response from {server_addr}")
        if len(data) < 12:
            return None
        payload_len, psecret, step, student_id = struct.unpack("iihh", data[:12])
        # fix syntax
        if not(payload_len, psecret, step, student_id):
                sock.close()
                return None
        num, len_val, udp_port, secretA = struct.unpack("iiii", data[12:28])
        print(f"num: {num}")
        print(f"len: {len_val}")
        print(f"udp_port: {udp_port}")
        print(f"secretA: {secretA}")
        return num, len_val, udp_port, secretA, sock
    except socket.timeout:
        print("Timeout")
        sock.close()
        return None
def stage_b(num, lenA, udp_port, secretA, sock):
    stage_b_socket = sock
    stage_b_socket.settimeout(5)
    # need to change addr?? 

    #tcp uses packets
    packets = []
    sent = [False] * num
    for i in range(num):
        payload = struct.pack("i", i)
        header =struct.pack("iihh", len(payload), secretA, 1, CONFIG_STUID)
        packets.append(header+payload)
    
    while True:
        for i in range(num):
            if not sent[i]:
                stage_b_socket.sendto(packets[i], SERVER_ADDR)
        try:
            data, client_addr = stage_b_socket.recvfrom(41201)	
            payload_len, psecret, step, student_id = struct.unpack("iihh", data[:12])
            #
            sent_id = struct.unpack("i", data[12:16])[0]
            if psecret == secretA and step == 2:
                sent[sent_id] = True
        except socket.timeout:
            continue
    data, client_addr = stage_b_socket.recvfrom(41201)	
    tcp_port, secretB = struct.unpack("ii", data[12:20])
    print("B:", secretB)
    return tcp_port, secretB        
        
    if __name__ == "__main__":
        num, lenA, udp_port, secretA, sock = stage_a()
        tcp_port, secretB = stage_b(num, lenB, udp_port, secretA, sock)


# tcp 
# def setup_tcp():
#     port = socket.gethostbyname(HOST)
#     s_tcp = socket.socket()		# TCP socket object
#     s_tcp.connect((HOST, PORT))
#     s_tcp.sendall('This will be sent to server')    # Send This message to server
#     data = s_tcp.recv(1024)	    # Now, receive the echoed
#     print (data)		# Print received(echoed) data
#     s_tcp.close()				# close the connection
