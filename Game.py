import pygame
import math
pygame.font.init()

#Color definitions
BLACK = (0,0,0)
RED = (255,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
BLUE = (0,0,255)
PURPLE = (255,0,255)
CYAN = (0,255,255)
YELLOW = (255,255,0)

def text_objects(text,font):
	textSurface = font.render(text,True,BLACK)
	return textSurface, textSurface.get_rect()

def message_display(text):
	largeText = pygame.font.Font("freesansbold.ttf", 115)
	TextSurf, TextRect = text_objects(text,largeText)
	TextRect.center = (200,200)


class goal():
	pass
class wall():
	pass
class bullet():
	def __init__(self,pos,vector):
		pass
	def draw(self):
		pass
	def update(self):
		pass
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
		self.message_display(str(self.game.time),(self.width/2,self.height/2),large=True)
		self.message_display(str(self.game.score1),(int(self.width*0.3),self.height/2),large=True)
		self.message_display(str(self.game.score2), (int(self.width * 0.7), self.height / 2), large=True)

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
		self.power = False
		self.mouseX = 0
		self.mouseY = 0
		self.movement = [0,0]
		if self.mainPlayer:
			self.image = game.red_player
		else:
			self.image = game.blue_player
		self.middle = (self.xpos, self.ypos)
	def move(self):
		self.xpos += self.movement[0]
		self.ypos += self.movement[1]
		if self.xpos < 0 + self.halfsize:
			self.xpos = 0 + self.halfsize
		elif self.xpos > self.game.width - self.halfsize:
			self.xpos = self.game.width - self.halfsize
		if self.ypos < self.game.HUD.height + self.halfsize:
			self.ypos = self.game.HUD.height + self.halfsize
		elif self.ypos > self.game.height - self.halfsize:
			self.ypos = self.game.height - self.halfsize

	def update(self):
		if self.mainPlayer:
			self.mouseX = self.game.main_mouse[0]
			self.mouseY = self.game.main_mouse[1]
		else:
			pass

		self.rotation = pygame.transform.rotate(self.image, -(
		math.degrees(math.atan2((self.mouseY - self.ypos), (self.mouseX - self.xpos)))) - 90)
		self.width = self.rotation.get_width()
		self.height = self.rotation.get_height()
		if self.mainPlayer:
			self.movement = self.game.player1_speed
		else:
			self.movement = self.game.player2_speed
		self.move()



	def draw(self):
		self.rotation = pygame.transform.rotate(self.image,-(math.degrees(math.atan2((self.mouseY-self.ypos),(self.mouseX-self.xpos))))-90)
		self.game.screen.blit(self.rotation,(self.xpos - self.width / 2, self.ypos - self.height / 2))
		pygame.draw.circle(self.game.screen,BLUE,(self.xpos,self.ypos),2)

class TopDownGame():
	def __init__(self,connection):
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
		self.HUD = HUD(self)
		self.drawObjects = [self.HUD]

	def update(self):
		self.clock.tick(60)
		self.main_mouse = pygame.mouse.get_pos()
		self.screen.fill(WHITE)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_a:
					self.player1_speed[0] -= self.speed
				if event.key == pygame.K_d:
					self.player1_speed[0] += self.speed
				if event.key == pygame.K_w:
					self.player1_speed[1] -= self.speed
				if event.key == pygame.K_s:
					self.player1_speed[1] += self.speed
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_a:
					self.player1_speed[0] += self.speed
				if event.key == pygame.K_d:
					self.player1_speed[0] -= self.speed
				if event.key == pygame.K_w:
					self.player1_speed[1] += self.speed
				if event.key == pygame.K_s:
					self.player1_speed[1] -= self.speed
		#DRAW HERE
		for k in self.gameObjects:
			k.update()

		for k in self.drawObjects:
			k.draw()
		pygame.display.flip()

g = TopDownGame()
p = player(1,g)
p2 = player(2,g)
g.drawObjects.append(p)
g.drawObjects.append(p2)
while True:
	g.update()

