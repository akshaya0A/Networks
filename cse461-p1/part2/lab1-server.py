import socket
import socketserver
import threading
import random
import struct
import string
import sys

STEP = 2
#psecret = random.randint(0, 100)
#num = random.randint(0, 100)
#len_val = random.randint(0, 100)
#udp_port = random.randint(00000, 41200)
PORT = int(sys.argv[2])
HOST = sys.argv[1]
HEADER_SIZE = 12
BUF_SIZE = 1024
# _,client_addr = s_udp.recvfrom(PORT)	        #receive data from client

class MyServer(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def valid_port(self):
        temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp.bind(("", 0))
        port = temp.getsockname()[1]
        temp.close()
        return port


    def handle(self):
        # determine the client and their current stage
        data= self.request[0]
        udp_socket = self.request[1]
        client_addr = self.client_address
        print("{} wrote:".format(self.client_address[0]))
        print(data)

        self.handle_stage_a(data, udp_socket, client_addr)


    def handle_stage_a(self, data, udp_socket, client_addr):
        # parse the mesage and payload
        payload = data[HEADER_SIZE:]
        print(payload)
        header = data[:HEADER_SIZE]
        payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
        print(payload_len)
        print(psecret)
        print(step)
        print(student_id)
        if payload != b"hello world\x00" or step != 1 or psecret != 0 or payload_len != len(payload):
            print("invalid")
            return
    
        # random reponses for stage A
        num = random.randint(1, 10)
        len_val = random.randint(1, 33)
        secretA = random.randint(0, 100)
        udp_port = self.valid_port()

        # Pack stage A 
        payload_a2 = struct.pack("!iiii", num, len_val, udp_port, secretA)
        header_a2 = struct.pack("!iihh", len(payload_a2), 0, 2, student_id)
        # print(payload_a2)
        # print(header_a2)
        udp_socket.sendto(header_a2 + payload_a2, client_addr)
        threading.Thread(target=self.handle_stage_b, args=(udp_port, len_val, secretA, num, student_id)).start()


    def handle_stage_b(self, udp_port, len_val, secretA, num, stuid):
        # create new udp connection for stage b
        print("stage b on port: ", udp_port)
        stageb_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        stageb_socket.bind(("", udp_port))
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
                ack_payload = struct.pack("!i", packet_id)
                ack_header = struct.pack("!iihh", len(ack_payload), secretA, 2, student_id)
                stageb_socket.sendto(ack_header + ack_payload, client_addr)
                packet_id_want += 1
            except socket.timeout:
                timeouts += 1
                continue
        
        # all packets sent so send tcp port info and start part c
        tcp_port = self.valid_port()
        secretB = random.randint(1, 1000)
        new_payload = struct.pack("!ii", tcp_port, secretB)
        final_header = struct.pack("!iihh", len(new_payload), secretA, 2, student_id)
        new_packet = final_header + new_payload
        stageb_socket.sendto(new_packet, client_addr)
        stageb_socket.close()
        threading.Thread(target=self.handle_stage_c, args=(tcp_port, secretB, student_id), daemon=True).start()


    def handle_stage_c(self, tcp_port, secretB, student_id):
        print("Stage C")
        # create new tcp connection for stage b
        print("stage c on port: ", tcp_port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            sock.settimeout(3)
            sock.bind(("", tcp_port))
        except socket.timeout:
            print("Client failed to connect within 3 seconds")
            return
        
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
            print("Client disconnected")
        except OSError as e:
            print("Socket error", e)

        self.handle_stage_d(connection, secretC, len2, sock, student_id)


    def handle_stage_d(self, connection, secretC, len2, sock, stuid):
        print("Stage D")
        try:
            data = connection.recv(1024)
            header = data[:HEADER_SIZE]
            payload = data[HEADER_SIZE:]
            payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
            # validate header
            if psecret != secretC or step != 1 or student_id != stuid:
                connection.close()
            # Payload length needs to be 4 + len_val
            if payload_len != len2:
                connection.close()

            return
        except socket.timeout:
            return
		

if __name__ == "__main__":
    with socketserver.ThreadingUDPServer((HOST, PORT), MyServer) as server:
        print(f"UDP Server listening on {HOST}:{PORT}")
        server.serve_forever()