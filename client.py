import socket
from _thread import *
import sys
ip = ""
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((ip,port))
except socket.error as e:
	print(str(e))
s.listen(5)
print ("Waiting for a connection with ip")
def threaded_client(conn):
	data = conn.recv(2048)
	print (data.decode("utf-8"))
	conn.send(str.encode("HEY: \n"))
	data = conn.recv(2048)
	print (data.decode("utf-8"))
	
	conn.close()

while True:
	conn,addr = s.accept()
	print("Connected to: " +addr[0]+":"+str(addr[1]))

	start_new_thread(threaded_client,(conn,))