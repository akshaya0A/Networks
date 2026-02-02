import socket
import socketserver
import threading
import random
import struct
import time
import sys

CONFIG_STUID = 811
STEP = 2
#psecret = random.randint(0, 100)
#num = random.randint(0, 100)
#len_val = random.randint(0, 100)
#udp_port = random.randint(00000, 41200)
PORT = int(sys.argv[2])
HOST = sys.argv[1]
HEADER_SIZE = struct.calcsize("!iihh")
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
        data= self.request[0]
        udp_socket = self.request[1]
        client_addr = self.client_address
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        # parse the mesage and payload
        payload = data[HEADER_SIZE:]
        print(payload)
        header = data[:HEADER_SIZE]
        payload_len, psecret, step, student_id = struct.unpack("!iihh", header)
        print(payload_len)
        print(psecret)
        print(step)
        print(student_id)
        if payload != b"hello world\x00":
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
        
        # stage B
        stageb_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        stageb_socket.bind(("", udp_port))
        # stageb_socket.settimeout(5)
        # id_num = struct.unpack("!i", payload[:4])[0]
        packet_id_want = 0
        while packet_id_want < num:
            try:
                data, client_addr = stageb_socket.recvfrom(BUF_SIZE)
                header = data[:HEADER_SIZE]
                payload = data[HEADER_SIZE:]
                id_num = int.from_bytes(payload[:4], "big")
                print("id_num:" + str(id_num) + ", packet_id_want:" + str(packet_id_want))
                payload_len, psecret, step, student_id  = struct.unpack("!iihh", header)
                if psecret != secretA or step != 1:
                    print('here1')
                    continue 
                if payload_len != 4 + len_val:
                    print('here2')
                    continue
                # get the packed id
                if id_num != packet_id_want:
                    print('here3')
                    continue 
                # we recieved the packet and send confirmation of recieving
                packet_id_want +=1
                sent_payload = struct.pack("!i", id_num)
                sent_header = struct.pack("!iihh", len(sent_payload), secretA, 2, student_id)
                stageb_socket.sendto(sent_header + sent_payload, client_addr)

            except socket.timeout:
                continue

        """        
        # all packets sent 
        tcp_port = self.valid_port()
        secretB = random.randint(1, 1000)
        new_payload = struct.pack("!ii", tcp_port, secretB)
        final_header = struct.pack("!iihh", len(new_payload), secretA, 2, student_id)
        # send back the final new info 
        new_packet = final_header + new_payload,
        stageb_socket.sendto(new_packet, client_addr)
        return num, len_val, udp_port, secretA, tcp_port, secretB
        #udp_packet = struct.pack("iihh", len(msg), 0, STEP, CONFIG_STUID)
        #msg = data.decode('utf-8')
        #socket.sendto(udp_packet, self.client_address)
        """
        print("success!")
        sys.exit(0)

		

if __name__ == "__main__":
    with socketserver.UDPServer((HOST, PORT), MyServer) as server:
        print(f"UDP Server listening on {HOST}:{PORT}")
        server.serve_forever()


            
"""

    # Create the server
    with socketserver.TCPServer((HOST, PORT), MyServer) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()



    def handle_tcp(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        # just send back the same data
        self.request.sendall(self.data)



class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        cur_thread = threading.current_thread()
        response = bytes("{}: {}".format(cur_thread.name, data), 'ascii')
        self.request.sendall(response)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((ip, port))
        sock.sendall(bytes(message, 'ascii'))
        response = str(sock.recv(1024), 'ascii')
        print("Received: {}".format(response))

if __name__ == "__main__":
    # Port 0 means to select an arbitrary unused port
    HOST, PORT = "localhost", 0

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address

        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.daemon = True
        server_thread.start()
        print("Server loop running in thread:", server_thread.name)

        client(ip, port, "Hello World 1")
        client(ip, port, "Hello World 2")
        client(ip, port, "Hello World 3")

        server.shutdown()


    def parsed(self, data):
        payload = data[12:]
        header = data[0:12]
        payload_len, psecret, step, student_id  = struct.unpack("iihh", header)
        return msg, payload_len, psecret, step, student_id

    def helper(self):
        dropped = False
        while packet_id_want < num:
            data, client_addr = stageb_socket.recvfrom(udp_port)
            header = data[:12]
            payload = data[12:]
            payload_len, psecret, step, student_id  = struct.unpack("iihh", header)
            if psecret != secretA or step != 1:
                return 
            if payload_len != 4 + len_val:
                return
            # get the packed id
            if packed_id != packet_id_want:
                continue 




while True:
	print ("Waiting for client...")
	data,addr = s_udp.recvfrom(port)	        #receive data from client
	print ("Received Messages:",data," from",addr)
	if (#TODOO):
		break

while True:
	data = conn.recv(1024)	    # Receive client data
	if not data: break	        # exit from loop if no data
	conn.sendall(data)	        # Send the received data back to client
conn.close()

s_tcp = socket.socket()		# TCP socket object
s_tcp.bind(host, port)

s_tcp.bind((host,port))
s_tcp.listen(5)
print ("Waiting for client...")
conn,addr = s_tcp.accept()	        # Accept connection when client connects
print ("Connected by ", addr)
###"""
