import socket
from _thread import *
import sys
import pygame
import time
import math
host = ""
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((host,port))
except socket.error as e:
	print(str(e))

s.listen(5)
print ("Waiting for a connection:")
PLAYERS = 0
def threaded_client(conn,serv):
	Controlled_player = PLAYERS
	conn.send(str.encode("HEY! You Are Player " + str(PLAYERS) + "\n"))
	while PLAYERS != 2:
		time.sleep(1)
	print ("Two players, starting game.")
	conn.sendall(str.encode(str(Controlled_player)))
	while True:
		data = conn.recv(2048)
		if Controlled_player == 1:
			serv.player1commsIn = data.decode("utf-8")
		elif Controlled_player == 2:
			serv.player2commsIn = data.decode("utf-8")
		if not data:
			break
		while not serv.Pump:
			pass
		if Controlled_player == 1:
			conn.sendall(str.encode(serv.player1commsOut))
			serv.player1commsOut = ""
		elif Controlled_player == 2:
			conn.sendall(str.encode(serv.player2commsOut))
			serv.player2commsOut = ""
		serv.Pump = False
	conn.close()
class Bullet():
	def __init__(self,game,pos,vector,owner):
		self.pos = pos
		self.direction = vector
		self.game = game
		self.destroyed = False
		self.owner = owner
		self.minDist = 30
		self.speed = 7

	def collision(self):
		self.dist = 100
		if self.owner == "1":
			self.dist = math.hypot(self.pos[0]-self.game.player2pos[0],self.pos[1]-self.game.player2pos[1])
		elif self.owner == "2":
			self.dist = math.hypot(self.pos[0] - self.game.player1pos[0], self.pos[1] - self.game.player1pos[1])
		return self.minDist > self.dist

	def outOfBounds(self):
		if self.pos[0] < 0 or self.pos[1] < 0 or self.pos[0] > self.game.screenwidth or self.pos[1] > self.game.screenheight:
			self.destroyed =  True

	def showInfo(self):
		self.string = "{},{},{},{},{}".format(int(self.pos[0]),int(self.pos[1]),int(self.direction[0]),int(self.direction[1]),str(self.owner))
		return self.string
	def update(self):
		self.dir = math.hypot(self.direction[0],self.direction[1]) / self.speed
		self.pos[0] += self.direction[0] * self.dir
		self.pos[1] += self.direction[1] * self.dir
		self.outOfBounds()



class TopDownGame():
	def __init__(self):
		self.player1commsOut = ""
		self.player2commsIn = ""
		self.player1commsIn = ""
		self.player2commsOut = ""
		self.Pump = False
		self.clock = pygame.time.Clock()
		self.player1pos = [100,200]
		self.player1mousepos = [0,0]
		self.player2pos = [600,300]
		self.player2mousepos = [0,0]
		self.player1info = [10,6,0]
		self.player2info = [10,6,0]
		self.player1speed = [0,0]
		self.player2speed = [0,0]
		self.player1reload = 1
		self.player2reload = 1
		self.timer = 10.0
		self.power = 0
		self.screenwidth = 1300
		self.sceenheight = 700
		self.bulletlist = []
		self.bulletinfo = []
		self.goal1 = [10000,10000]
		self.goal2 = [10000,10000]
		self.speed1 = 3
		self.speed2 = 3
		self.bulletspeed = 7
		self.lastFrame = 0
	def send_to_clients(self):
		self.Pump = True
	def update(self):
		self.clock.tick(60)
		#Data StructureIN: Mpos:0,0;w:0;a:0;s:0;d:0;p:0;s:0
		print ("player 1 does:" + server.player1commsIn)
		print ("player 2 does:" + server.player2commsIn)
		self.data1 = server.player1commsIn.split(";")
		self.data2 = server.player2commsIn.split(";")

		if server.player1commsIn != "" and server.player2commsIn != "":
			self.player1mousepos = [int(self.data1[0][6:].split(",")[0]),int(self.data1[0][6:].split(",")[1][:-1])]
			self.player2mousepos = [int(self.data2[0][6:].split(",")[0]), int(self.data2[0][6:].split(",")[1][:-1])]
			#player 1 movements
			if self.data1[1][2] == "1" and self.data1[3][2] == "0":
				self.player1speed[1] = -self.speed1
			elif self.data1[1][2] == "1" and self.data1[3][2] == "1":
				self.player1speed[1] = 0
			elif self.data1[1][2] == "0" and self.data1[3][2] == "0":
				self.player1speed[1] = 0
			elif self.data1[1][2] == "0" and self.data1[3][2] == "1":
				self.player1speed[1] = self.speed1
			if self.data1[2][2] == "1" and self.data1[4][2] == "0":
				self.player1speed[0] = -self.speed1
			elif self.data1[2][2] == "0" and self.data1[4][2] == "1":
				self.player1speed[0] = self.speed1
			elif self.data1[2][2] == "1" and self.data1[4][2] == "1":
				self.player1speed[0] = 0
			elif self.data1[2][2] == "0" and self.data1[4][2] == "0":
				self.player1speed[0] = 0
			#Player 2 movements
			if self.data2[1][2] == "1" and self.data2[3][2] == "0":
				self.player2speed[1] = -self.speed2
			elif self.data2[1][2] == "1" and self.data2[3][2] == "1":
				self.player2speed[1] = 0
			elif self.data2[1][2] == "0" and self.data2[3][2] == "0":
				self.player2speed[1] = 0
			elif self.data2[1][2] == "0" and self.data2[3][2] == "1":
				self.player2speed[1] = self.speed2
			if self.data2[2][2] == "1" and self.data2[4][2] == "0":
				self.player2speed[0] = -self.speed2
			elif self.data2[2][2] == "0" and self.data2[4][2] == "1":
				self.player2speed[0] = self.speed2
			elif self.data2[2][2] == "1" and self.data2[4][2] == "1":
				self.player2speed[0] = 0
			elif self.data2[2][2] == "0" and self.data2[4][2] == "0":
				self.player2speed[0] = 0
			#check for shooting
			"""if self.data1[6][2] == "1" and self.player1reload < 0:
				#self.bulletDir = [self.player1pos[0] - self.player1mousepos[0],
				#			  self.player1pos[1] - self.player1mousepos[1]]
				#bullet = Bullet(self, self.player1pos, self.bulletDir, "1")
				#self.bulletlist.append(bullet)
			if self.data2[6][2] == "1" and self.player2reload < 0:
				self.bulletDir = [self.player2pos[0]-self.player2mousepos[0],self.player2pos[1]-self.player2mousepos[1]]
				bullet = Bullet(self,self.player2pos,self.bulletDir,"2")
				#self.bulletlist.append(bullet)"""

		#do game stuff with commsIN
		#game logic
		#move the players
		self.player1pos[0] += self.player1speed[0]
		self.player1pos[1] += self.player1speed[1]
		self.player2pos[0] += self.player2speed[0]
		self.player2pos[1] += self.player2speed[1]
		#timer stuff
		self.timer -= time.clock() - self.lastFrame
		print (self.player1reload)
		print(self.player2reload)
		"""if self.player2reload > -1:
			self.player2reload -= time.clock() - self.lastFrame
		if self.player1reload > -1:
			self.player1reload -= time.clock() - self.lastFrame"""
		self.lastFrame = time.clock()
		#update the bullets
		"""
		self.bulletinfo = ""
		for k in self.bulletlist:
			#check for collisions and destroy them on impact
			if k.collision():
				k.destroyed = True
				if k.owner == "1":
					self.player2info[0] -= 1
				elif k.owner == "2":
					self.player1info[0] -= 1
			k.update()
			if k.destroyed:
				self.bulletlist.remove(k)
			else:
				#add the info on the bullets so we can send it to clients
				self.bulletinfo += k.showInfo()
				self.bulletinfo += ":"
		if self.bulletinfo != "":
			self.bulletinfo = self.bulletinfo[:-1]
		#self.player1pos = [100,100]"""
		#Data StructureOUT: p1pos:0,0;p2pos:0,0;p1Mpos:0,0;p2Mpos:0,0;p1info:0,0,0;p2info:0,0,0;time:0;power:0;goal1:0,0;goal2:0,0;BULLETS
		self.player2commsOut = "p1pos:{};p2pos:{};p1Mpos:{};p2Mpos:{};p1info:{};p2info:{};time:{};power:{};goal1:{};goal2:{};{}".format(
			self.player1pos, self.player2pos, self.player1mousepos, self.player2mousepos, self.player1info, self.player2info, self.timer,
			self.power, self.goal1, self.goal2,self.bulletinfo
		)
		self.player1commsOut = "p1pos:{};p2pos:{};p1Mpos:{};p2Mpos:{};p1info:{};p2info:{};time:{};power:{};goal1:{};goal2:{};{}".format(
			self.player1pos, self.player2pos, self.player1mousepos, self.player2mousepos, self.player1info,
			self.player2info, self.timer,
			self.power, self.goal1, self.goal2, self.bulletinfo
		)
		print(self.player2commsOut)
		print(self.player1commsOut)
		self.send_to_clients()

	def start(self):
		self.playing = True
		while self.playing:
			self.update()







server = TopDownGame()
while PLAYERS != 2:
	conn,addr = s.accept()
	print("Connected to: " +addr[0]+":"+str(addr[1]))

	PLAYERS += 1

	start_new_thread(threaded_client,(conn,server))
	if PLAYERS == 2:
		server.start()
