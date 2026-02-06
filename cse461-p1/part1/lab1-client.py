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
    sock.settimeout(3)
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
    """sock.settimeout(3)
    header = struct.pack("!iihh", 4 + lenA, secretA, 1,CONFIG_STUID)
    for packet_id in range(num):
        # Build payload
        payload = struct.pack("!i", packet_id) + b"\x00" * lenA
        # Build header 
        packet = header + payload
        # send to server
        sent = sock.sendto(packet, (HOST, udp_port))
        try:
            data, _ = sock.recvfrom(BUF_SIZE)	
            print(f"Received response from {server_addr}")
            if len(data) < 12:
                return None
            if step != 2 or student_id != CONFIG_STUID or psecret != secretA:
                sock.close()
                return None
            ack_id = struct.unpack("!i", data[12:16])[0]
            if ack_id != packet_id:
                continue
            print(f"ACK received for packet")
        except socket.timeout:
            print("Timeout")
            sock.close()
            return None

"""
    sock.settimeout(.5)
    for packet_id in range(num):
        # Build payload
        payload = struct.pack("!i", packet_id) + b"\x00" * lenA

        # Build header (payload_len MUST be 4 + lenA)
        header = struct.pack("!iihh", 4 + lenA, secretA, 1,CONFIG_STUID)
        packet = header + payload
        while (len(packet) % 4 != 0):
            packet += b"\00"
        while True:
            sock.sendto(packet, (HOST, udp_port))
            try:
                data, _ = sock.recvfrom(BUF_SIZE)
                ack_len, ack_secret, ack_step, ack_sid = struct.unpack("!iihh", data[:12])
                ack_id = struct.unpack("!i", data[12:16])[0]
                if (ack_secret != secretA or ack_step != 2 or ack_id == packet_id):
                    print("ACK received for packet {packet_id}")
                    break
            except socket.timeout:
                print("ack timeout")
                continue
    print("Stage B complete")
    sock.settimeout(3)
    while True:
        try:
            data, _ = sock.recvfrom(BUF_SIZE)
            print("DATA ",data)
            tcp_port, secretB = struct.unpack("!ii", data[12:20])
            print(tcp_port, secretB)
            sock.close()
            return tcp_port, secretB
        except socket.timeout:
            print("timout heheheh")
        

if __name__ == "__main__":
    num, lenA, udp_port, secretA, sock = stage_a()
    tcp_port, secretB = stage_b(num, lenA, udp_port, secretA, sock)
    print("B:", secretB)


