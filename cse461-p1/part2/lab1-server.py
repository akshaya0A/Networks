import socket
import socketserver
import threading
import random
import struct
import string
import sys

STEP = 2
PORT = int(sys.argv[2])
HOST = sys.argv[1]
HEADER_SIZE = 12
BUF_SIZE = 1024

    
def valid_port_udp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    return sock, port


def valid_port_tcp():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(3)
        sock.bind(("", 0))
    except socket.timeout:
        return False, False
    port = sock.getsockname()[1]
    return sock, port


def handle_stage_a(data, udp_socket, client_addr):
    # parse the mesage and payload
    payload = data[HEADER_SIZE:]
    header = data[:HEADER_SIZE]
    payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
    if payload != b"hello world\x00" or step != 1 or psecret != 0 or payload_len != len(payload):
        return
    
    # random reponses for stage A
    num = random.randint(1, 10)
    len_val = random.randint(1, 33)
    secretA = random.randint(0, 100)
    sock, udp_port = valid_port_udp()

    # Pack stage A 
    payload_a2 = struct.pack("!iiii", num, len_val, udp_port, secretA)
    header_a2 = struct.pack("!iihh", len(payload_a2), 0, 2, student_id)
    udp_socket.sendto(header_a2 + payload_a2, client_addr)
    handle_stage_b(sock, len_val, secretA, num, student_id)


def handle_stage_b(stageb_socket, len_val, secretA, num, stuid):
    # create new udp connection for stage b
    stageb_socket.settimeout(5)

    len_align = len_val
    while (len_align % 4 != 0):
        len_align+=1
    packet_id_want = 0
    max_timeouts = 10
    timeouts = 0

    while packet_id_want < num and timeouts < max_timeouts:
        try:
            data, client_addr = stageb_socket.recvfrom(BUF_SIZE)
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
            # validate header
            if psecret != secretA or step != 1 or student_id != stuid:
                continue
            # Payload length needs to be 4 + len_val
            if payload_len != 4 + len_val:
                continue
            # packet id
            packet_id = struct.unpack("!i", payload[:4])[0]
            if packet_id != packet_id_want:
                continue
            # zero padding
            if payload[4:4+len_val] != b"\x00" * len_val:
                continue
            # ack
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
    stageb_socket.close()
    handle_stage_c(sock, secretB, student_id)


def handle_stage_c(sock, secretB, student_id):
    # create new tcp connection for stage b
    sock.listen(1)
    connection, client_addr = sock.accept()

    # random reponses
    num2 = random.randint(1, 10)
    len2 = random.randint(1, 33)
    secretC = random.randint(0, 100)
    char = random.choice(string.ascii_letters).encode('ascii')
    char_padded = char + b'\x00' * 3

    payload = struct.pack("!iii4s", num2, len2, secretC, char_padded)
    header = struct.pack("!iihh", len(payload), secretB, 2, student_id)
    try:
        connection.sendall(header + payload)
    except (BrokenPipeError, ConnectionResetError):
        print("broke")
    except OSError as e:
        print("os")

    handle_stage_d(connection, secretC, len2, student_id, char, num2)


def handle_stage_d(connection, secretC, len2, stuid, char, num2):
    payloads_received = 0
    len_padded = 0
    while (len2 + len_padded) % 4 != 0:
        len_padded += 1
    while payloads_received < num2:
        try:
            data = b''
            total_bytes = len2 + len_padded + HEADER_SIZE
            while len(data) < total_bytes:
                block = connection.recv(total_bytes - len(data))
                if not block:
                    connection.close()
                    return
                data += block
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
            # validate header
            if psecret != secretC:
                connection.close()
                return
            if step != 1:
                connection.close()
                return
            if student_id != stuid:
                connection.close()
                return
            if payload_len != len2:
                connection.close()
                return
            if payload[0:len2] != char * len2:
                connection.close()
                return
            payloads_received += 1
        except socket.timeout:
            connection.close()
            return
    secretD = random.randint(0, 100)
    payload = struct.pack("!i", secretD)
    header = struct.pack("!iihh", len(payload), secretC, 2, student_id)
    try:
        connection.sendall(header + payload)
    except (BrokenPipeError, ConnectionResetError):
        print("pipe")
    except OSError as e:
        print("os")
		

if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((HOST, PORT))
    try:
        while True:
            data, client_addr = server.recvfrom(BUF_SIZE)
            threading.Thread(target=handle_stage_a, args=(data, server, client_addr)).start()
    except KeyboardInterrupt:
        server.close()
        sys.exit(0)
