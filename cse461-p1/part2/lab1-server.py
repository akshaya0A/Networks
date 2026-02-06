# Akshaya AKkugari, Medha Mittal, Keosha Chhajed 
# CSE 461: Lab 1: Socket Programming
# UDP/TCP multi-stage server implementation

import socket
import threading
import random
import struct
import string
import sys

STEP = 2
PORT = int(sys.argv[2])
HOST = sys.argv[1]
# 4 byets payload_len, 4 bytes psecret, 2bytes step, 2 bytesstudent_id
HEADER_SIZE = 12
BUF_SIZE = 1024
SIZE = 4

# Helper method to create a valid UDP port
# Caller needs to close the socket
# checks that the port isn't used
def valid_port_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    return sock, port

    
# Helper method to create a valid TCP port
# Caller needs to close the socket
# checks port isn't used
def valid_port_tcp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try catch to give the client only 3 seconds to connect
    try:
        sock.settimeout(3)
        sock.bind(("", 0))
    except socket.timeout:
        return False, False
    port = sock.getsockname()[1]

    return sock, port


# Verify the payload and respond with a UDP packet containing four integers
# (num, len, udp_port, secretA) that are randomly generated. 
# Then wait for the client's packet at udp_port.
def handle_stage_a(data, udp_socket, client_addr):
    # parse the mesage and payload
    payload = data[HEADER_SIZE:]
    header = data[:HEADER_SIZE]
    # unpack the header contents
    payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
    # validate stage A request
    if payload != b"hello world\x00" or step != 1 or psecret != 0 or payload_len != len(payload):
        return
    # random reponses for stage B
    num = random.randint(1, 10)
    len_val = random.randint(1, 33)
    secretA = random.randint(0, 100)

    # create new udp connection for stage b
    sock, udp_port = valid_port_udp()

    # pack stage A response into a payload
    payload_a2 = struct.pack("!iiii", num, len_val, udp_port, secretA)
    header_a2 = struct.pack("!iihh", len(payload_a2), 0, 2, student_id)
    # send response to client and start stage b
    udp_socket.sendto(header_a2 + payload_a2, client_addr)
    handle_stage_b(sock, len_val, secretA, num, student_id)


# The server receives, validates, and randomly acknowledges all num packets.
# Then, it sends a UDP packet containing two integers: a TCP port number and secretB.
# It then waits for a TCP connection from the client at TCP port number.
def handle_stage_b(stageb_socket, len_val, secretA, num, stuid):
    stageb_socket.settimeout(3)
    
    # find the padding for 4 byte
    len_align = len_val
    while (len_align % SIZE != 0):
        len_align+=1
    packet_id_want = 0
    max_timeouts = 10
    timeouts = 0

    # continue accepting packets until num packets have been recieved
    # and acknowledged or until max_timeouts have occurred
    while packet_id_want < num and timeouts < max_timeouts:
        try:
            # get data/packet from the udp connection
            data, client_addr = stageb_socket.recvfrom(BUF_SIZE)
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
            # validate the header
            if psecret != secretA or step != 1 or student_id != stuid or payload_len != 4 + len_val:
                continue
            packet_id = struct.unpack("!i", payload[:SIZE])[0]
            if packet_id != packet_id_want or payload[4:SIZE+len_val] != b"\x00" * len_val:
                continue
            # since the packet is valid, randomly decide whether to acknowledge it
            send = random.randint(1, 5)
            if (send != 1):
                ack_payload = struct.pack("!i", packet_id)
                ack_header = struct.pack("!iihh", len(ack_payload), secretA, 2, student_id)
                stageb_socket.sendto(ack_header + ack_payload, client_addr)
                packet_id_want += 1
        except socket.timeout:
            timeouts += 1
            continue
    
    # all packets sent so send tcp port info and start part c
    sock, tcp_port = valid_port_tcp()
    if not sock or not tcp_port:
        return
    secretB = random.randint(1, 1000)
    new_payload = struct.pack("!ii", tcp_port, secretB)
    final_header = struct.pack("!iihh", len(new_payload), secretA, 2, student_id)
    new_packet = final_header + new_payload
    stageb_socket.sendto(new_packet, client_addr)
    # close UDP socket for stage B 
    stageb_socket.close()
    handle_stage_c(sock, secretB, student_id)


# Establish the tcp connection with the client and send a packet with
# three integers: num2, len2, secretC, and a character: c.
def handle_stage_c(sock, secretB, student_id):
    # create new tcp connection for stage b
    sock.listen(1)
    sock.settimeout(3.0)
    try:
        connection, client_addr = sock.accept()
    except socket.timeout:
        sock.close()
        return
    # random responses to send to client
    num2 = random.randint(1, 10)
    len2 = random.randint(1, 33)
    secretC = random.randint(0, 100)
    # single char padded with 4 bytes
    char = random.choice(string.ascii_letters).encode('ascii')
    char_padded = char + b'\x00' * 3
    # send the packet with payload and header while checking for errors
    payload = struct.pack("!iii4s", num2, len2, secretC, char_padded)
    header = struct.pack("!iihh", len(payload), secretB, 2, student_id)
    try:
        connection.sendall(header + payload)
    except (BrokenPipeError, ConnectionResetError):
        connection.close()
        sock.close()
        print("Broken pipe")
        return
    except OSError as e:
        connection.close()
        sock.close()
        print("OS error")
        return
    # start stage d
    handle_stage_d(connection, secretC, len2, student_id, char, num2, sock)


# The server receives and validates num2 packets and then
# responds with one integer payload: secretD.
def handle_stage_d(connection, secretC, len2, stuid, char, num2, sock):
    payloads_received = 0
    # calculate the message padding
    len_padded = 0
    while (len2 + len_padded) % SIZE != 0:
        len_padded += 1
    # keep accepting packets until num2 packets have been received
    while payloads_received < num2:
        try:
            # read the packet the client sent, making sure the full packet is received
            data = b''
            total_bytes = len2 + len_padded + HEADER_SIZE
            while len(data) < total_bytes:
                block = connection.recv(total_bytes - len(data))
                if not block:
                    connection.close()
                    return
                data += block
            # get the header and payload from the data received
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
            # validate header
            if psecret != secretC or step != 1 or student_id != stuid or payload_len != len2 or payload[0:len2] != char * len2:
                print("invalid header")
                connection.close()
                sock.close()
                return
            payloads_received += 1
        except socket.timeout:
            connection.close()
            sock.close()
            return
    # send the final secret, checking for errors
    secretD = random.randint(0, 100)
    payload = struct.pack("!i", secretD)
    header = struct.pack("!iihh", len(payload), secretC, 2, student_id)
    try:
        connection.sendall(header + payload)
    except (BrokenPipeError, ConnectionResetError):
        connection.close()
        sock.close()
        print("Broken pipe")
        return
    except OSError as e:
        connection.close()
        sock.close()
        print("OS error")
        return
		

if __name__ == "__main__":
    # create a udp port where the server continues to recieve packages for stage a
    # until there's a keyboard interrupt (i.e. ctrl-C)
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    try:
        while True:
            # each client is handled in separate thread
            data, client_addr = server.recvfrom(BUF_SIZE)
            threading.Thread(target=handle_stage_a, args=(data, server, client_addr)).start()
    except KeyboardInterrupt:
        # shut down with ctrl-C
        print("shutting down")
        server.close()
        sys.exit(0)
