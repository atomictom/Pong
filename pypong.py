# About
# Pong written (to run on CPython) using pygame

# Imports
import pygame, pygame.draw as draw, random
from pygame.locals import *
from utilities import *
from random import randint
color = pygame.color.Color

def boundscheck(lower, upper, value):
	""" Returns the value, or the closest bound it exceeds (i.e. boundscheck(0, 10, 100) == 10)"""
	return max(min(upper, value), lower) 
	
# Game Classes
class Ball(pygame.sprite.Sprite):
	""" Class representing a ball in pong """
	def __init__(self):
		super(Ball, self).__init__()
		self.setup()
		
	def setup(self):
		self.width 				= 10
		self.height 			= 10
		self.x 					= config['resolution'][X] / 2 + randint(-50, 50)
		self.y 					= config['resolution'][Y] / 2 + randint(-50, 50)
		self.velocity  			= [randint(15, 30) * random.choice([-1, 1]), randint(-15, 15)]
		self.max_acceleration 	= 10
		self.rect 				= pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.image 				= pygame.surface.Surface(self.rect.size)
		self.image.fill(WHITE)
		
	def update(self, time):
		# Y axis update
		self.y += (self.velocity[Y] * time) * (config['resolution'][Y] / 100)
		posy = boundscheck(0, config['resolution'][Y] - self.height, self.y)
		if posy != self.y:
			self.y = abs(posy - (posy - self.y))
			self.velocity[Y] *= -1
		# X axis update
		self.x += (self.velocity[X] * time) * (config['resolution'][X] / 100)
		# check for out of bounds
		if self.x <= 0 or self.x >= config['resolution'][X] - self.width:
			#state['score'] += 1
			self.setup()
		# check for collisions
		collisions = pygame.sprite.spritecollide(self, state['players_group'], False)
		if collisions:
			self.velocity[X] = abs(self.velocity[X]) * (1 if collisions[0] == state['player1'] else -1)
			
		# update rect
		self.rect.top = self.y
		self.rect.left = self.x

class Paddle(pygame.sprite.Sprite):
	""" Class representing a paddle in pong, instance variables hold all relevant information 
		and the update method performs game logic for the paddle. Drawing is done using the image attribute,
		the update method sets its location using the rect attribute """
	def __init__(self, player):
		super(Paddle, self).__init__()
		self.player 		= player
		self.paddlelength 	= 10 * (config['resolution'][Y] / 100)	# length of the paddle (in y-axis), by percentage of screen
		self.paddlewidth  	= 12									# the width of the paddle (for looks)
		self.y 				= config['resolution'][Y] / 2 - (self.paddlelength / 2) 
		self.x 				= 10 if player == PLAYER1 else config['resolution'][X] - (10 + self.paddlewidth)
		self.speed			= 0										# current speed of the paddle, also: percentage of the screen to move per second
		self.maxspeed		= 1 * self.paddlelength 				# the max speed of the paddle
		self.acceleration	= 2 * self.maxspeed						# how much the speed should change per second
		self.rect 			= pygame.rect.Rect(self.x, self.y, self.paddlewidth, self.paddlelength)
		self.image 			= pygame.surface.Surface(self.rect.size)
		self.image.fill(WHITE) 										# make the paddle white
	def update(self, time):
		# get the player's action, and determine which direction to move the paddle
		player_action = input['forPlayer'](self)
		direction = 0 if player_action['up'] and player_action['down'] else -1 if player_action['up'] else 1 if player_action['down'] else 0
		# find the change in speed since last update given the direction
		delta_speed = self.acceleration * time * direction
		# update our speed
		self.speed = boundscheck(-self.maxspeed, self.maxspeed, self.speed + delta_speed)
		# now update our position based on our speed
		self.y += (self.speed * time) * (config['resolution'][Y] / 100) # '(config['resolution'][Y] / 100)' == percentage of the screen
		self.y = boundscheck(0, config['resolution'][Y] - self.paddlelength, self.y) 
		# finally, update where the top of the paddle is so it can redraw properly
		self.rect.top = self.y

# Constants
PLAYER1			= 1
PLAYER2 		= 2
PADDLEWIDTH 	= 7
PADDLELENGTH	= 20
WHITE 			= color(255, 255, 255)
RED 			= color(255, 0, 0)
GREEN			= color(0, 255, 0)
BLUE			= color(0, 0, 255)
BLACK			= color(0, 0, 0)
X, Y 			= 0, 1

# Globals
screen = None
clock = pygame.time.Clock()
# configuration
config = dict()
config['resolution'] 	= (800, 600)
config['name'] 			= "Pong"
config['players'] 		= 2
config['framerate']	 	= 80
# game state
state = dict()
state['paddlelength'] 	= 20
state['player1'] 		= Paddle(PLAYER1)
state['player2'] 		= Paddle(PLAYER2)
state['players_group']	= pygame.sprite.Group(state['player1'], state['player2'])
state['ball'] 			= Ball()
state['objects_group']		= pygame.sprite.Group(state['player1'], state['player2'], state['ball'])
# input
input = dict()
input['player1'] 		= dict(up = False, down = False)
input['player2'] 		= dict(up = False, down = False)
input['forPlayer']		= lambda paddle: input['player1'] if paddle.player == PLAYER1 else input['player2']
input['quit']			= False

# Init
pygame.init()
pygame.display.set_mode(config['resolution'])
pygame.display.set_caption(config['name'])
screen = pygame.display.get_surface()

# Functions

#"FPS " + str(clock.get_fps())
def drawText(msg, location = (0,0), surf = screen, size = 20, color = BLUE):
	font = pygame.font.Font(None, size)
	msgsurface = font.render(msg, False, color)
	rect = msgsurface.get_rect()
	rect.topleft = location
	surf.blit(msgsurface, rect) 

def keytoggle(key, isPressed):
	lookup = {K_UP		: 'player1.up', \
			  K_DOWN 	: 'player1.down', \
			  K_w 		: 'player2.up', \
			  K_s		: 'player2.down'}
	try:
		key1, key2 = lookup[key].split('.')
	except KeyError as e:
		pass # Ignore, this is a key that we don't use 
	else:
		input[key1][key2] = isPressed
	
def updateInput(events, time): 
	for event in events: 
		if event.type == QUIT: 
			input['quit'] = True
		elif event.type == KEYDOWN:
			keytoggle(event.key, True)
		elif event.type == KEYUP:
			keytoggle(event.key, False)

def updateGame(time):
	state['objects_group'].update(time)

def updateScreen(time):
	drawText("Speed: " + str(state['player1'].speed))
	state['objects_group'].draw(screen)
	
def gameloop():
	time = 0
	while not input['quit']:
		screen.fill(BLACK)
		time = clock.tick(config['framerate']) / 1000.0 # time is number of seconds since last loop
		updateInput(pygame.event.get(), time)
		updateGame(time)
		updateScreen(time)
		pygame.display.update()
		pygame.event.pump()
		
def main():
	gameloop()

if __name__ == "__main__":
	main()