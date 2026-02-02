import socket
import struct
import time
import errno

import sys

CONFIG_STUID = 811
STEP = 1
SERVER_ADDR: str = sys.argv[1]
#SERVER_ADDR: str = "attu3.cs.washington.edu"
PORT = int(sys.argv[2])
HOST = socket.gethostbyname(SERVER_ADDR)
BUF_SIZE = 1024
# packet_data = struct.pack("iihh", payload_len, psecret, STEP, CONFIG_STUID)

def stage_a():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5)
    print ("UDP target IP:", HOST)
    print ("UDP target Port:", PORT)
    msg = b"hello world\x00"

    header = struct.pack("!iihh", len(msg), 0, STEP, CONFIG_STUID)
    packet = header + msg

    # send to server
    sent = sock.sendto(packet, (HOST, PORT))
    print(f"Bytes sent: {sent}")
    # get reponse
    try:
        data, server_addr = sock.recvfrom(BUF_SIZE)	
        print(f"Received response from {server_addr}")
        if len(data) < 12:
            return None
        payload_len, psecret, step, student_id = struct.unpack("!iihh", data[:12])
        # fix syntax
        if not(payload_len, psecret, step, student_id):
                sock.close()
                return None
        num, len_val, udp_port, secretA = struct.unpack("!iiii", data[12:28])
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

    #udp uses packets
    packets = []
    # sent = [False] * num
    for i in range(num):
        payload = struct.pack("!i", i)
        payload += b'\x00' * lenA
        header = struct.pack("!iihh", len(payload), secretA, 1, CONFIG_STUID)
        packets.append(header + payload)

    num_sent = 0
    
    while num_sent < num:
        stage_b_socket.sendto(packets[num_sent], (SERVER_ADDR, udp_port))
        try:
            data, client_addr = stage_b_socket.recvfrom(BUF_SIZE)
            acked_packet_id = struct.unpack("!i", data[12:])
            print("acked_packet_id:" + str(acked_packet_id[0]) + "num_sent" + str(num_sent))
            if acked_packet_id[0] == num_sent:
                num_sent += 1
        except socket.timeout:
            continue

    print("success!")
    
    return 0, 0

    """
    data, client_addr = stage_b_socket.recvfrom(BUF_SIZE)	
    tcp_port, secretB = struct.unpack("!ii", data[12:20])
    print("B:", secretB)
    return tcp_port, secretB 
    """       
        

if __name__ == "__main__":
    num, lenA, udp_port, secretA, sock = stage_a()
    tcp_port, secretB = stage_b(num, lenA, udp_port, secretA, sock)


# tcp 
# def setup_tcp():
#     port = socket.gethostbyname(HOST)
#     s_tcp = socket.socket()		# TCP socket object
#     s_tcp.connect((HOST, PORT))
#     s_tcp.sendall('This will be sent to server')    # Send This message to server
#     data = s_tcp.recv(1024)	    # Now, receive the echoed
#     print (data)		# Print received(echoed) data
#     s_tcp.close()				# close the connection
