import socket
import struct
import time
import errno

import sys

CONFIG_STUID = 811
STEP = 1
SERVER_ADDR: str = "attu2.cs.washington.edu"
#SERVER_ADDR: str = "attu3.cs.washington.edu"
HOST: str = socket.gethostbyname(SERVER_ADDR)
# packet_data = struct.pack("iihh", payload_len, psecret, STEP, CONFIG_STUID)

# udp
def setup_udp(self, port, msg):
    # create socket
    s_udp = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)      # For UDP
    try:
        ret = socket.getaddrinfo(HOST, port)
    except socket.gaierror as e:
        print("Failed to get address info: {e}")
    print ("UDP target IP:", HOST)
    print ("UDP target Port:", port)
 
    s_udp.settimeout(5)

    # create and send packet
    packet = struct.pack("iihh", len(msg), 0, STEP, CONFIG_STUID)
    packet += msg
    sent = s_udp.sendto(packet,(HOST, port))		# Sending message to UDP server
    print("we sent ", sent)
    
    # receive reply from socket
    data, client_addr = s_udp.recvfrom(41201)	
    unpacked_data = struct.unpack("iiii", data)
    num = unpacked_data[0]
    data_len = unpacked_data[1]
    udp_port = unpacked_data[2]
    psecret = unpacked_data[3]
    print("A: ", psecret)
    print("num = ", num)
    print("len: ", data_len)
    print("port = ", udp_port)
        
if __name__ == "__main__":
    setup_udp(41201, b"hello world\0")


# tcp 
# def setup_tcp():
#     port = socket.gethostbyname(HOST)
#     s_tcp = socket.socket()		# TCP socket object
#     s_tcp.connect((HOST, PORT))
#     s_tcp.sendall('This will be sent to server')    # Send This message to server
#     data = s_tcp.recv(1024)	    # Now, receive the echoed
#     print (data)		# Print received(echoed) data
#     s_tcp.close()				# close the connection
