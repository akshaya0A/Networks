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
    print(f"Bytes sent: {sent}")ok
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
    sock.settimeout(2)

    for packet_id in range(num):
        # Build payload
        payload = struct.pack("!i", packet_id) + b"\x00" * lenA

        # Build header (payload_len MUST be 4 + lenA)
        header = struct.pack("!iihh", 4 + lenA, secretA, 1,CONFIG_STUID)
        packet = header + payload
        while True:
            sock.sendto(packet, (HOST, udp_port))
            try:
                data, _ = sock.recvfrom(BUF_SIZE)
                ack_len, ack_secret, ack_step, ack_sid = struct.unpack("!iihh", data[:12])
                ack_id = struct.unpack("!i", data[12:16])[0]
                if (ack_secret == secretA and ack_step == 2 and ack_id == packet_id):
                    print(f"ACK received for packet {packet_id}")
                    break
            except socket.timeout:
                continue
    print("Stage B complete")
    """
    data, client_addr = stage_b_socket.recvfrom(BUF_SIZE)	
    tcp_port, secretB = struct.unpack("!ii", data[12:20])
    print("B:", secretB)
    return tcp_port, secretB 
    """       
        

if __name__ == "__main__":
    num, lenA, udp_port, secretA, sock = stage_a()
    stage_b(num, lenA, udp_port, secretA, sock)



# tcp 
# def setup_tcp():
#     port = socket.gethostbyname(HOST)
#     s_tcp = socket.socket()		# TCP socket object
#     s_tcp.connect((HOST, PORT))
#     s_tcp.sendall('This will be sent to server')    # Send This message to server
#     data = s_tcp.recv(1024)	    # Now, receive the echoed
#     print (data)		# Print received(echoed) data
#     s_tcp.close()				# close the connection