import socket
from _thread import *
import sys
import pygame
import time
import math
import random
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
def generate_walls():
	minWalls = 10
	maxWalls = 15
	maxSize = 300
	mediumSize = 100
	minSize = 50
	gameboardSizeX = (0,1300)
	gameboardSizeY = (100,700)
	out = []
	for i in range(random.randint(minWalls,maxWalls)):
		if random.randint(0,1) == 1:
			out.append((random.randint(gameboardSizeX[0],gameboardSizeX[1]),random.randint(gameboardSizeY[0],gameboardSizeY[1]),
					random.randint(mediumSize,maxSize),random.randint(minSize,mediumSize)))
		else:
			out.append((random.randint(gameboardSizeX[0], gameboardSizeX[1]),
						random.randint(gameboardSizeY[0], gameboardSizeY[1]),
						random.randint(minSize,mediumSize), random.randint(mediumSize,maxSize)))
	return out

def threaded_client(conn,serv,wallinfo):
	Controlled_player = PLAYERS
	walldata = ""
	for i in wallinfo:
		wall = ""
		for k in i:
			wall += str(k)
			wall += ","
		wall = wall[:-1]
		walldata += wall
		walldata += ":"
	walldata = walldata[:-1]
	conn.send(str.encode("HEY! You Are Player " + str(PLAYERS) + "\n"))
	while PLAYERS != 2:
		time.sleep(1)
	print ("Two players, starting game.")
	conn.sendall(str.encode(str(Controlled_player)+walldata))
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
		if self.owner == "1" and math.hypot(self.pos[0]-self.game.player2pos[0],self.pos[1]-self.game.player2pos[1]) < 10:
			self.game.player2info[2] += 1
			return True
		if self.owner == "2" and math.hypot(self.pos[0]-self.game.player1pos[0],self.pos[1]-self.game.player1pos[1]) < 10:
			self.game.player1info[2] += 1
			return True
		else:
			return False
	def move(self,x,y):
		self.pos = [x,y]
class Wall():
	def __init__(self,rect):
		self.rect = rect
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
	def __init__(self,walls):
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
		self.walllist = walls
		self.wallcords = [[False for i in range(self.screenheight + 500)] for l in range(self.screenwidth + 500)]
		for i in self.walllist:
			for o in range(i[2]):
				for p in range(i[3]):
					self.wallcords[i[0] + o][i[1] + p] = True

	def illegal_place(self,cords):
		return self.wallcords[cords[0]][cords[1]]


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
		self.memory1pos = list(self.player1pos)
		self.memory1pos = list(self.player1pos)
		self.memory2pos = list(self.player2pos)
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

		self.player1pos[0] += self.player1speed[0]
		self.player1pos[1] += self.player1speed[1]


		self.player2pos[0] += self.player2speed[0]
		self.player2pos[1] += self.player2speed[1]

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
			if self.illegal_place([int(k.pos[0]),int(k.pos[1])]):
				k.destroyed = True
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
		if math.hypot(self.player1pos[0]-self.player2pos[0],self.player1pos[1]-self.player2pos[1]) < 40:
			self.player1pos = list(self.memory1pos)
		if math.hypot(self.player1pos[0]-self.player2pos[0],self.player1pos[1]-self.player2pos[1]) < 40:
			self.player2pos = list(self.memory2pos)
		if self.illegal_place(self.player1pos):
			self.player1pos = list(self.memory1pos)
		if self.illegal_place(self.player2pos):
			self.player2pos = list(self.memory2pos)
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
	def placePlayers(self):
		while self.illegal_place(self.player1pos):
			self.player1pos = [random.randint(1,self.screenwidth),random.randint(1,self.screenheight)]
		while self.illegal_place(self.player2pos):
			self.player2pos = [random.randint(1,self.screenwidth),random.randint(1,self.screenheight)]
	def start(self):
		self.playing = True
		self.round = True
		self.placePlayers()
		while self.playing:
			self.new_round()
			while self.round:
				self.update()





wallmap = generate_walls()

server = TopDownGame(wallmap)
while PLAYERS != 2:
	conn,addr = s.accept()
	print("Connected to: " +addr[0]+":"+str(addr[1]))

	PLAYERS += 1

	start_new_thread(threaded_client,(conn,server,wallmap))
	if PLAYERS == 2:
		server.start()
