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
class Goal():
	def __init__(self,game,pos,owner):
		self.pos = list(pos)
		self.owner = str(owner)
		self.game = game
	def taken(self):
		if self.owner == "1" and math.hypot(self.pos[0]-self.game.player2pos[0],self.pos[1]-self.game.player2pos[1]) < 5:
			self.game.player2info[2] += 1
			return True
		if self.owner == "2" and math.hypot(self.pos[0]-self.game.player1pos[0],self.pos[1]-self.game.player1pos[1]) < 5:
			self.game.player1info[2] += 1
			return True
		else:
			return False
	def move(self,x,y):
		self.pos = [x,y]

class Bullet():
	def __init__(self,game,pos,vector,owner):
		self.pos = [int(pos[0]),int(pos[1])]
		self.direction = list(vector)
		self.game = game
		self.destroyed = False
		self.owner = owner
		self.minDist = 25
		self.speed = 12
		self.dir = self.speed / math.hypot(self.direction[0], self.direction[1])

	def collision(self):
		self.dist = 100
		if self.owner == "1":
			self.dist = math.hypot(self.pos[0]-self.game.player2pos[0],self.pos[1]-self.game.player2pos[1])
		elif self.owner == "2":
			self.dist = math.hypot(self.pos[0] - self.game.player1pos[0], self.pos[1] - self.game.player1pos[1])
		return self.minDist > self.dist

	def outOfBounds(self):
		if self.pos[0] < 0 or self.pos[1] < 100 or self.pos[0] > self.game.screenwidth or self.pos[1] > self.game.screenheight:
			self.destroyed =  True

	def showInfo(self):
		self.string = "{},{},{},{},{}".format(int(self.pos[0]),int(self.pos[1]),int(self.direction[0]),int(self.direction[1]),str(self.owner))
		return self.string
	def update(self):
		self.dir = self.speed / math.hypot(self.direction[0],self.direction[1])
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
		self.player1respawn = [100, 200]
		self.player1mousepos = [0,0]
		self.player2pos = [600,300]
		self.player2respawn = [600, 300]
		self.player2mousepos = [0,0]
		self.player1info = [10,10,0]
		self.player2info = [10,10,0]
		self.player1speed = [0,0]
		self.player2speed = [0,0]
		self.player1reload = 1
		self.player2reload = 1
		self.timer = 10.0
		self.power = "1"
		self.reloadingtime = 0.8
		self.screenwidth = 1300
		self.screenheight = 700
		self.bulletlist = []
		self.bulletinfo = []
		self.goal1 = list(self.player1pos)
		self.goalFor1 = Goal(self,self.goal1,"1")
		self.goal2 = list(self.player2pos)
		self.goalFor2 = Goal(self,self.goal2,"2")
		self.speed1 = 3
		self.speed2 = 3
		self.lastFrame = 0
		self.lastreload = 0
	def send_to_clients(self):
		self.Pump = True
	def intT(self,x):
		return [math.floor(x[0]),math.floor(x[1])]
	def check_win(self):
		if self.goalFor1.taken() or self.goalFor2.taken():
			self.round = False
		if self.player1info[0] <= 0:
			self.player1info[0] = 10
			self.player2info[2] += 1
			self.round = False
			self.player1pos = self.player1respawn
		if self.player2info[0] <= 0:
			self.player2info[0] = 10
			self.player1info[2] += 1
			self.round = False
			self.player2pos = self.player2respawn
	def update(self):
		self.clock.tick(60)
		#Data StructureIN: Mpos:0,0;w:0;a:0;s:0;d:0;p:0;s:0
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
			#use power
			if self.power == "1" and self.data1[5][2] == "1":
				self.timer = 1
				self.power = "2"
			elif self.power == "2" and self.data2[5][2] == "1":
				self.timer = 1
				self.power = "1"

			#check for shooting
			if self.data1[6][2] == "1" and self.player1reload < 0 and self.player1info[1] > 0:
				self.bulletDir = [self.player1mousepos[0] - self.player1pos[0],
							   self.player1mousepos[1] - self.player1pos[1]]
				bullet = Bullet(self, self.player1pos, self.bulletDir, "1")
				self.player1reload = 0.2

				self.player1info[1] -= 1
				self.bulletlist.append(bullet)
			if self.data2[6][2] == "1" and self.player2reload < 0 and self.player2info[1] > 0:
				self.bulletDir = [self.player2mousepos[0]-self.player2pos[0],self.player2mousepos[1]-self.player2pos[1]]
				bullet = Bullet(self,self.player2pos,self.bulletDir,"2")
				self.player2reload = 0.2
				self.player2info[1] -= 1
				self.bulletlist.append(bullet)
		#do game stuff with commsIN
		#game logic
		self.goal1 = self.goalFor1.pos
		self.goal2 = self.goalFor2.pos
		self.check_win()
		#move the players
		self.memorypos = list(self.player1pos)
		self.player1pos[0] += self.player1speed[0]
		self.player1pos[1] += self.player1speed[1]
		if math.hypot(self.player1pos[0]-self.player2pos[0],self.player1pos[1]-self.player2pos[1]) < 40:
			self.player1pos = list(self.memorypos)
		self.memorypos = list(self.player2pos)
		self.player2pos[0] += self.player2speed[0]
		self.player2pos[1] += self.player2speed[1]
		if math.hypot(self.player1pos[0]-self.player2pos[0],self.player1pos[1]-self.player2pos[1]) < 40:
			self.player2pos = list(self.memorypos)
		#stop the player from going out of the screen
		if self.player1pos[0] < 0:
			self.player1pos[0] = 0
		if self.player1pos[0] > self.screenwidth:
			self.player1pos[0] = self.screenwidth
		if self.player1pos[1] < 100:
			self.player1pos[1] = 100
		if self.player1pos[1] > self.screenheight:
			self.player1pos[1] = self.screenheight
		if self.player2pos[0] < 0:
			self.player2pos[0] = 0
		if self.player2pos[0] > self.screenwidth:
			self.player2pos[0] = self.screenwidth
		if self.player2pos[1] < 100:
			self.player2pos[1] = 100
		if self.player2pos[1] > self.screenheight:
			self.player2pos[1] = self.screenheight
		#timer stuff
		self.timer -= time.perf_counter() - self.lastFrame
		self.lastreload += time.perf_counter() - self.lastFrame
		if self.timer <= 0:
			self.round = False
		if self.player2reload > -1:
			self.player2reload -= time.perf_counter() - self.lastFrame
		if self.player1reload > -1:
			self.player1reload -= time.perf_counter() - self.lastFrame
		self.lastFrame = time.perf_counter()
		#update the bullets
		if self.lastreload > self.reloadingtime and self.player1info[1] < 10:
			self.player1info[1] += 1
		if self.lastreload > self.reloadingtime and self.player2info[1] < 10:
			self.player2info[1] += 1
		if self.lastreload > self.reloadingtime:
			self.lastreload = 0

		if self.player1info[1] <= 10:
			self.player1info
		self.bulletinfo = ""
		for k in self.bulletlist:
			#check for collisions and destroy them on impact
			if k.collision():
				k.destroyed = True
				if k.owner == "1":
					self.player2info[0] -= 1
					self.player2pos[0] += int(k.direction[0] * k.dir)
					self.player2pos[1] += int(k.direction[1] * k.dir)
				elif k.owner == "2":
					self.player1info[0] -= 1
					self.player1pos[0] += int(k.direction[0] * k.dir)
					self.player1pos[1] += int(k.direction[1] * k.dir)
			k.update()
			if k.destroyed:
				self.bulletlist.remove(k)
			else:
				#add the info on the bullets so we can send it to clients
				self.bulletinfo += k.showInfo()
				self.bulletinfo += ":"
		if self.bulletinfo != "":
			self.bulletinfo = self.bulletinfo[:-1]

		#Data StructureOUT: p1pos:0,0;p2pos:0,0;p1Mpos:0,0;p2Mpos:0,0;p1info:0,0,0;p2info:0,0,0;time:0;power:0;goal1:0,0;goal2:0,0;BULLETS
		self.player2commsOut = "p1pos:{};p2pos:{};p1Mpos:{};p2Mpos:{};p1info:{};p2info:{};time:{};power:{};goal1:{};goal2:{};{}".format(
			self.intT(self.player1pos), self.intT(self.player2pos), self.player1mousepos, self.player2mousepos, self.player1info, self.player2info, self.timer,
			self.power, self.goal1, self.goal2,self.bulletinfo
		)
		self.player1commsOut = "p1pos:{};p2pos:{};p1Mpos:{};p2Mpos:{};p1info:{};p2info:{};time:{};power:{};goal1:{};goal2:{};{}".format(
			self.intT(self.player1pos), self.intT(self.player2pos), self.player1mousepos, self.player2mousepos, self.player1info,
			self.player2info, self.timer,
			self.power, self.goal1, self.goal2, self.bulletinfo
		)
		self.send_to_clients()
	def new_round(self):
		self.new_goals()
		self.player1info[1] = 6
		self.player2info[1] = 6
		self.round = True
	def new_goals(self):
		self.timer = 10

		self.goalFor1.move(self.player1pos[0],self.player1pos[1])
		self.goalFor2.move(self.player2pos[0], self.player2pos[1])
		self.goal1 = list(self.goalFor1.pos)
		self.goal2 = list(self.goalFor2.pos)
		self.player1respawn = list(self.goal1)
		self.player2respawn = list(self.goal2)

	def start(self):
		self.playing = True
		self.round = True
		while self.playing:
			self.new_round()
			while self.round:
				self.update()







server = TopDownGame()
while PLAYERS != 2:
	conn,addr = s.accept()
	print("Connected to: " +addr[0]+":"+str(addr[1]))

	PLAYERS += 1

	start_new_thread(threaded_client,(conn,server))
	if PLAYERS == 2:
		server.start()
