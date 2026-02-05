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
HEADER_SIZE = 12
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
        if step != 2 or student_id != CONFIG_STUID:
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

    len_align = lenA
    while (len_align % 4 != 0):
        len_align+=1

    for packet_id in range(num):
        # Build payload
        payload = struct.pack("!i", packet_id) + b"\x00" * len_align

        retries = 0

        # Build header (payload_len MUST be 4 + lenA)
        header = struct.pack("!iihh", 4 + lenA, secretA, 1, CONFIG_STUID)
        packet = header + payload
        while retries < 10:
            sock.sendto(packet, (HOST, udp_port))
            try:
                data, _ = sock.recvfrom(BUF_SIZE)
                ack_len, ack_secret, ack_step, ack_sid = struct.unpack("!iihh", data[:12])
                ack_id = struct.unpack("!i", data[12:16])[0]
                if (ack_len == 4 and ack_secret == secretA and ack_step == 2 and
                        ack_sid == CONFIG_STUID and ack_id == packet_id):
                    print(f"ACK received for packet {packet_id}")
                    break
            except socket.timeout:
                retries += 1
                continue
    # get the tcp port
    timeouts = 0
    while timeouts < 5:
        try:
            data, client_addr = sock.recvfrom(BUF_SIZE)
            ack_len, ack_secret, ack_step, ack_sid = struct.unpack("!iihh", data[:12])
            if ack_secret == secretA and ack_step == 2:
                tcp_port, secretB = struct.unpack("!ii", data[12:20])
                print("TCP Port: ", tcp_port)
                print("B: ", secretB)
                return tcp_port, secretB
        except socket.timeout:
            timeouts += 1
    
    raise RuntimeError("Stage B failed")

def stage_c(tcp_port, secretB):
    # connect to the socket
    print("Stage 3 port: ", tcp_port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        sock.connect((SERVER_ADDR, tcp_port))
    except socket.timeout:
        print("Failed to connect")
    except ConnectionRefusedError:
        print("Server didn't accept connection")
    except OSError as e:
        print("Socket error: ", e)

    data = b""
    bytes_wanted = HEADER_SIZE + 16
    while len(data) < bytes_wanted:
        try:
            block = sock.recv(bytes_wanted - len(data))
        except OSError as e:
            raise RuntimeError(e)
        if not block:
            raise RuntimeError("Connection closed")
        
        data += block

    # receive the data
    print(data)
    payload_len, psecret, step, student_id = struct.unpack("!iihh", data[:12])
    if psecret != secretB or step != 2 or student_id != CONFIG_STUID:
        sock.close()
        return None
    num2, len2, secretC, c = struct.unpack("!iii4s", data[12:])
    print(f"num: {num2}")
    print(f"len: {len2}")
    print(f"secretC: {secretC}")
    print(f"c: {c[:1]}")
    return num2, len2, secretC, c[:1], sock


def stage_d(num2, len2, secretC, c, sock):
    print("Stage D")

    payload = c * len2
    padding_needed = (4 - (len2 % 4)) % 4
    payload += b'\x00' * padding_needed

    for i in range(num2):
        header = struct.pack("!iihh", len2, secretC, 1, CONFIG_STUID)
        sock.sendall(header + payload)

    sock.close()


if __name__ == "__main__":
    num, lenA, udp_port, secretA, sock = stage_a()
    tcp_port, secretB = stage_b(num, lenA, udp_port, secretA, sock)
    num2, len2, secretC, c, sock = stage_c(tcp_port, secretB)
    stage_d(num2, len2, secretC, c, sock)
