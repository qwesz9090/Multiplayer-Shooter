import socket
from _thread import *
import sys
ip = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.connect((ip,port))
except socket.error as e:
	print(str(e))

print ("Waiting for a connection with server")
data = s.recv(2048)
print ("Connection Established")
print ("Server: " + data.decode("utf-8") + "\n")
try:
	while True:
		s.sendall(str.encode(input("Send: ")))
		data = s.recv(2048)
		print (data.decode("utf-8"))
	s.close()
except:
	s.close()

