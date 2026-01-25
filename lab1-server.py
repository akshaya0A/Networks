import socket
import socketserver
import threading
import random
import struct

CONFIG_STUID = 811
STEP = 2
psecret = random.randint(0, 100)
num = random.randint(0, 100)
len = random.randint(0, 100)
udp_port = random.randint(00000, 41200)
PORT = 41201
HOST = "attu2.cs.washington.edu"

class MyServer(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    
    
    def handle_udp(self, data):
        data = self.request[0].strip()
        socket = self.request[1]
        print("{} wrote:".format(self.client_address[0]))
        print(data)
        self.helper(data)
        msg = data.decode('utf-8')
        socket.sendto(udp_packet, self.client_address)
		# since we made sure eveyrhting is valid start new thread
		# create new random stuff
		psecret = random.randint(0, 100)
		num = random.randint(0,100)
		len = random.randint(0, 100)
		# new UDP port each time no repeats
		udp_port = random.randint(00000, 41200)

		
	def helper(self, data):
		msg = data[12:]
        data = data[0:12]
        unpacked_data = struct.unpack("iihh", data)
        udp_packet = struct.pack("iihh", len(msg), 0, STEP, CONFIG_STUID) 

    if __name__ == "__main__":
        s_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP socket object
        ret = socket.getaddrinfo(HOST, PORT)
        print(ret[0])
        s_udp.bind(ret[0][4])
        s_udp.listen()
        with socketserver.UDPServer((HOST, PORT), MyServer) as server:
            server.serve_forever()
            while True:
                print ("Waiting for client...")
                data,addr = s_udp.recvfrom(PORT)	        #receive data from client
                print ("Received Messages:",data," from",addr)
                handle_udp(data)
            





           
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
