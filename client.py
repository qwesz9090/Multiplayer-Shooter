import socket
from _thread import *
import sys
import pygame
import math
import time
ip = "localhost"
port = 5555
#Color definitions
BLACK = (0,0,0)
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)
CYAN = (0,255,255)
YELLOW = (255,255,0)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
def text_objects(text,font):
	textSurface = font.render(text,True,BLACK)
	return textSurface, textSurface.get_rect()

def message_display(text):
	largeText = pygame.font.Font("freesansbold.ttf", 115)
	TextSurf, TextRect = text_objects(text,largeText)
	TextRect.center = (200,200)


class HUD():
	def __init__(self,game):
		self.game = game
		self.width = self.game.width
		self.height = 100
		self.largeText = pygame.font.Font("freesansbold.ttf", 100)
		self.mediumText = pygame.font.Font("freesansbold.ttf", 40)
	def message_display(self,text,pos,large=False):
		if large:
			TextSurf, TextRect = text_objects(text, self.largeText)
		else:
			TextSurf, TextRect = text_objects(text, self.mediumText)

		TextRect.center = pos
		self.game.screen.blit(TextSurf,TextRect)

	def draw(self):
		pygame.draw.line(self.game.screen,BLACK,(0,self.height),(self.width,self.height),3)
		pygame.draw.line(self.game.screen,BLACK, (self.width/2 + 100, 0), (self.width/2 +100,self.height),3)
		pygame.draw.line(self.game.screen, BLACK, (self.width / 2 - 100, 0), (self.width / 2 - 100, self.height),3)
		self.message_display("Player 1",(100,30))
		self.message_display("Player 2", (self.width-100,30))
		self.shortTime = float((int(self.game.time*10))/10)
		self.message_display(str(self.shortTime),(self.width/2,self.height/2),large=True)
		self.message_display(str(self.game.score1),(int(self.width*0.35),self.height/2),large=True)
		self.message_display(str(self.game.score2), (int(self.width * 0.65), self.height / 2), large=True)
		self.message_display("HP: "+str(self.game.player1.hp), (int(self.width * 0.06), self.height *0.7))
		self.message_display("HP: " + str(self.game.player2.hp), (int(self.width * 0.94), self.height * 0.7))
		self.message_display("Ammo: " + str(self.game.player1.ammo), (int(self.width * 0.2), self.height * 0.7))
		self.message_display("Ammo: " + str(self.game.player2.ammo), (int(self.width * 0.8), self.height * 0.7))
class Wall():
	def __init__(self,rect,game):
		self.rect = rect
		self.game = game
		self.game.drawObjects.append(self)
	def draw(self):
		pygame.draw.rect(self.game.screen,BLACK,self.rect)
class player():
	def __init__(self,id,game):
		self.game = game
		self.game.gameObjects.append(self)
		if id == 1:
			self.mainPlayer = True
		else:
			self.mainPlayer = False
		self.width = 47
		self.height = 47
		self.size = 47
		self.halfsize = int(self.size/2)
		self.color = RED
		self.pointer_length = 10
		self.xpos = 300
		self.ypos = 300
		self.hp = 10
		self.points = 0
		self.ammo = 6
		self.mouseX = 0
		self.mouseY = 0
		self.movement = [0,0]
		if self.mainPlayer:
			self.image = game.red_player
		else:
			self.image = game.blue_player
		self.middle = (self.xpos, self.ypos)

	def update(self):
		self.rad = (math.atan2((self.mouseY - self.ypos), (self.mouseX - self.xpos)))
		self.rotation = pygame.transform.rotate(self.image, -(math.degrees(self.rad) - 90))
		#self.offset = self.size * math.sin(self.rad) * math.sqrt(2)
		self.width = self.rotation.get_width()
		self.height = self.rotation.get_height()



	def draw(self):
		self.rotation = pygame.transform.rotate(self.image,-(math.degrees(math.atan2((self.mouseY-self.ypos),(self.mouseX-self.xpos))))-90)
		self.game.screen.blit(self.rotation,(int(self.xpos - self.width / 2),int(self.ypos - self.height / 2)))
		pygame.draw.circle(self.game.screen,BLUE,(self.xpos,self.ypos),2)

class TopDownGame():
	def __init__(self,connection,walls):
		pygame.init()
		self.connection = connection
		self.width, self.height = 1300,700
		self.screen = pygame.display.set_mode((self.width,self.height))
		pygame.display.set_caption("Topdown-shooter")
		self.clock = pygame.time.Clock()
		self.red_player = pygame.image.load("images\Red_player1.png")
		self.blue_player = pygame.image.load("images\Blue_player1.png")
		self.gameObjects = []
		self.player1_speed = [0,0]
		self.player2_speed = [0,0]
		self.player1_mouse = [0,0]
		self.player2_mouse = [0,0]
		self.time = 10.0
		self.score1 = 0
		self.score2 = 0
		self.speed = 3
		self.power = 0
		self.HUD = HUD(self)
		self.drawObjects = [self.HUD]
		self.setup()
		self.goal1 = [0,0]
		self.goal2 = [0,0]
		self.bullets = []
		for i in walls:
			Wall(i,self)


	def setup(self):
		self.player1 = player(1,self)
		self.player2 = player(2,self)
		self.drawObjects.append(self.player1)
		self.drawObjects.append(self.player2)
	def new_round(self):
		pass

	def update(self):
		self.clock.tick(60)
		#HERE WE GET PLAYER INPUT
		self.main_mouse = pygame.mouse.get_pos()
		self.wPressed = 0
		self.aPressed = 0
		self.sPressed = 0
		self.dPressed = 0
		self.PowerPressed = 0
		self.ShootPressed = 0
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.connection.sendall(str.encode("Closing"))
				self.connection.close()
				exit()
		self.pressedKeys = pygame.key.get_pressed()
		if self.pressedKeys[pygame.K_a]:
			self.aPressed = 1
		else:
			self.aPressed = 0
		if self.pressedKeys[pygame.K_w]:
			self.wPressed = 1
		else:
			self.wPressed = 0
		if self.pressedKeys[pygame.K_s]:
			self.sPressed = 1
		else:
			self.sPressed = 0
		if self.pressedKeys[pygame.K_d]:
			self.dPressed = 1
		else:
			self.dPressed = 0
		if self.pressedKeys[pygame.K_SPACE]:
			self.ShootPressed = 1
		else:
			self.ShootPressed = 0
		if self.pressedKeys[pygame.K_LSHIFT]:
			self.PowerPressed = 1
		else:
			self.PowerPressed = 0
		#DRAW HERE

		#HERE WE SEND INPUTS TO SERVER
		# Data StructureIN: Mpos:0,0;w:0;a:0;s:0;d:0;p:0;s:0
		self.connection.sendall(str.encode("Mpos:{};w:{};a:{};s:{};d:{};p:{};s:{}".format(pygame.mouse.get_pos(),
		self.wPressed,self.aPressed,self.sPressed,self.dPressed,self.PowerPressed,self.ShootPressed)))
		#HERE WE RECIEVE INFO
		# Data StructureOUT: p1pos:0,0;p2pos:0,0;p1Mpos:0,0;p2Mpos:0,0;p1info:0,0,0;p2info:0,0,0;time:0;power:0;goal1:0,0;goal2:0,0;BULLETS
		data = self.connection.recv(2048)
		data = data.decode("utf-8")
		data = data.split(";")
		data0 = data[0][7:].split(",")
		data1 = data[1][7:].split(",")
		data2 = data[2][8:].split(",")
		data3 = data[3][8:].split(",")
		data4 = data[4][8:].split(",")
		data5 = data[5][8:].split(",")
		data6 = data[6][5:]
		data7 = data[7][6:]
		data8 = data[8][7:].split(",")
		data9 = data[9][7:].split(",")
		data10 = data[10]
		self.player1.xpos = int(data0[0])
		self.player1.ypos = int(data0[1][:-1])
		self.player2.xpos = int(data1[0])
		self.player2.ypos = int(data1[1][:-1])
		self.player1_mouse = [int(data2[0]),int(data2[1][:-1])]
		self.player2_mouse = [int(data3[0]), int(data3[1][:-1])]
		self.player1.hp = int(data4[0])
		self.player1.ammo = int(data4[1])
		self.score1 = int(data4[2][:-1])
		self.player2.hp = int(data5[0])
		self.player2.ammo = int(data5[1])
		self.score2 = int(data5[2][:-1])
		self.time = float(data6)
		self.power = int(data7)
		self.goal1 = [int(data8[0]),int(data8[1][:-1])]
		self.goal2 = [int(data9[0]),int(data9[1][:-1])]
		self.bulletdata = data10
		self.player1.mouseX = self.player1_mouse[0]
		self.player1.mouseY = self.player1_mouse[1]
		self.player2.mouseX = self.player2_mouse[0]
		self.player2.mouseY = self.player2_mouse[1]
		self.bullets = []
		# Here we look at the bullets
		if self.bulletdata != "":
			self.bulletsdata = self.bulletdata.split(":")
			for bullet in self.bulletsdata:
				self.bulletinfo = bullet.split(",")
				self.bullets.append([int(self.bulletinfo[0]),int(self.bulletinfo[1]),float(self.bulletinfo[2]),float(self.bulletinfo[3]),str(self.bulletinfo[4])])

		for k in self.gameObjects:
			k.update()
		#HERE WE DRAW
		self.screen.fill(WHITE)
		pygame.draw.circle(self.screen,RED,(self.goal1[0],self.goal1[1]),15)
		pygame.draw.circle(self.screen,BLUE, (self.goal2[0], self.goal2[1]),15)
		for k in self.drawObjects:
			k.draw()
		for bullet in self.bullets:
			pygame.draw.circle(self.screen,BLACK,(bullet[0],bullet[1]),4)

		pygame.display.flip()


try:
	s.connect((ip,port))
except socket.error as e:
	print(str(e))

print ("Waiting for a connection with server")
data = s.recv(2048)
print ("Connection Established")
print ("Server: " + data.decode("utf-8") + "\n")
while data[0] != "1" and data[0] != "2":
	data = s.recv(2048)
	data = data.decode("utf-8")
	time.sleep(1)
	print ("waiting for players... ")
walls = data[1:].split(":")
walllist = list()
for i in walls:
	temp = i.split(",")
	walllist.append((int(temp[0]),int(temp[1]),int(temp[2]),int(temp[3])))
TheGame = TopDownGame(s,walllist)
while True:
	TheGame.update()

s.sendall(str.encode("error"))
s.close()
exit()

