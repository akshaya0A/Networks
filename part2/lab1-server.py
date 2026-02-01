import socket
import socketserver
import threading
import random
import struct

CONFIG_STUID = 811
STEP = 2
psecret = random.randint(0, 100)
num = random.randint(0, 100)
len_val = random.randint(0, 100)
udp_port = random.randint(00000, 41200)
PORT = 41201
HOST = "attu2.cs.washington.edu"
_,addr = s_udp.recvfrom(PORT)	        #receive data from client

class MyServer(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    def handle(self):
        data= self.request[0].strip()
        socket = self.request[1]

        print("{} wrote:".format(self.client_address[0]))
        print(data)
        # parse the mesage and payload
        payload = data[12:]
        header = data[:12]
        payload_len, psecret, step, student_id = struct.unpack("iihh", header)
        if payload != b"hello world\x00":
            return
    
        # random reponses
        num = random.randint(1, 100)
        len_val = random.randint(1, 100)
        secret_a = random.randint(0, 100)
        # pack the reponse payload
        payload_a2 = struct.pack("iiii", num, len_val, udp_port, secret_a)
        # pack the reposne header
        header_a2 = struct.pack("iihh", len(payload_a2), 0, 2, student_id)

        # send packet
        udp_socket = self.request[1]
        udp_socket.sendto(header_a2 + payload_a2, addr)

        #udp_packet = struct.pack("iihh", len(msg), 0, STEP, CONFIG_STUID)
        #msg = data.decode('utf-8')
        #socket.sendto(udp_packet, self.client_address)
		
    def parsed(self, data):
        payload = data[12:]
        header = data[0:12]
        payload_len, psecret, step, student_id  = struct.unpack("iihh", header)
        return msg, payload_len, psecret, step, student_id

    def helper(self):
        expected_id = 0
        dropped = False
        while expected_id < num:
            data, addr = stageb_socket.recvfrom(udp_port)
            header = data[:12]
            payload = data[12:]
            payload_len, psecret, step, student_id  = struct.unpack("iihh", header)
            if psecret != secretA or step != 1:
                return 
            if payload_len != 4 + len_val:
                return
            # get the packed id
            if packed_id != expected_id:
                continue 
    def valid_port(self):
         temp= socket.socket()
         # tells os to bind to unesd port
         temp.bind(("", 0))
         port = temp.getsockname()[1]
         temp.close()
         return port

    if __name__ == "__main__":
        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket object
        ret = socket.getaddrinfo(HOST, PORT)
        print(ret[0])
        s_udp.bind(ret[0][4])
        #s_udp.listen()
        with socketserver.UDPServer((HOST, PORT), MyServer) as server:
            server.serve_forever()
            while True:
                # Start a thread with the server -- that thread will then start one
                # more thread for each request
                server_thread = threading.Thread(target=handle_client, args=(None, None, server_socket))
                # Exit the server thread when the main thread terminates
                server_thread.daemon = True
                server_thread.start()
                print("Server loop running in thread:", server_thread.name)
            



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
