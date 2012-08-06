# About
# Pong written (to run on CPython) using pygame

# Imports
import pygame, pygame.draw as draw, random
from pygame.locals import *
from utilities import *
from random import randint
color = pygame.color.Color

def combine_by(fn, *args):
	""" Combines iterables into a list by position using the function supplied like: ret[0] = fn(list1[0], list2[0]...). """
	return map(fn, zip(*args))
	
def diff(*args):
	""" Same as sum, but returns the difference of the arguments. """
	return reduce(lambda x, y: x - y, *args)
	
def percent_of_screen(axis, p = 1):
	""" Returns some percentage of the screen by the axis given in pixels, or one percentage if called with one parameter only. """ 
	return p * config['gamearea'][axis] / 100

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
		self.x 					= config['gamearea'][X] / 2 + randint(-50, 50)
		self.y 					= config['gamearea'][Y] / 2 + randint(-50, 50)
		self.speed  			= [randint(15, 30), randint(0, 20)]
		self.direction			= [random.choice([-1, 1]), random.choice([-1, 1])]
		self.max_acceleration 	= 10
		self.rect 				= pygame.rect.Rect(self.x, self.y, self.width, self.height)
		self.image 				= pygame.surface.Surface(self.rect.size)
		self.image.fill(WHITE)
		
	def update(self, time):
		# Y axis update
		self.y += (self.speed[Y] * self.direction[Y] * time) * percent_of_screen(Y)
		posy = boundscheck(0, config['gamearea'][Y] - self.height, self.y)
		if posy != self.y:
			self.y = abs(posy - (posy - self.y))
			self.direction[Y] *= -1
		# X axis update
		self.x += (self.speed[X] * self.direction[X] * time) * percent_of_screen(X)
		# check for collisions
		player = state['player1' if self.x < config['gamearea'][X] / 2 else 'player2']
		leftbound  = config['paddle_offset'] + state['player1'].paddlewidth - 1
		rightbound = config['gamearea'][X] - (config['paddle_offset'] + state['player2'].paddlewidth + self.width) + 1
		out_of_bounds_x = boundscheck(leftbound, rightbound, self.x) != self.x
		touching_paddle = boundscheck(player.y, player.y + player.paddlelength, self.y) == self.y
		collision = out_of_bounds_x and touching_paddle
		if collision:
			# change direction, add a small random value to the X speed, and then a fraction of the paddle speed to the Y speed
			self.direction[X] = 1 if player.player == PLAYER1 else -1 # cannot use *= -1 because there may still be a collision next update
			self.speed[X] += random.random()*2
			self.speed[Y] += player.speed / 6 * self.direction[Y]
		# check for out of bounds
		if not collision and (self.x <= 0 or self.x >= config['gamearea'][X] - self.width):
			state['score'][PLAYER2 if self.x <= 0 else PLAYER1] += 1
			self.setup()
			
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
		self.paddlelength 	= 17 * percent_of_screen(Y)				# length of the paddle (in y-axis), by percentage of screen
		self.paddlewidth  	= 1.5 * percent_of_screen(X)			# the width of the paddle
		self.y 				= config['gamearea'][Y] / 2 - (self.paddlelength / 2) 
		self.x 				= config['paddle_offset'] if player == PLAYER1 else config['gamearea'][X] - (config['paddle_offset'] + self.paddlewidth)
		self.speed			= 0										# current speed of the paddle, also: percentage of the screen to move per second
		self.maxspeed		= 20 * percent_of_screen(Y)#1 * self.paddlelength 				# the max speed of the paddle
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
		self.speed = 0 if (self.y == 0 or self.y == config['gamearea'][Y] - self.paddlelength) and abs(self.speed) > 5 else self.speed
		self.speed -= .3 * (-1 if self.speed < 0 else 1) 		# Simulate friction, reduce speed over time
		self.speed = 0 if abs(self.speed) < .4 else self.speed	# Set the speed to zero if less than the friction speed so it doesn't bounce back and forth
		# now update our position based on our speed
		self.y += (self.speed * time) * percent_of_screen(Y) # '(config['resolution'][Y] / 100)' == percentage of the screen
		self.y = boundscheck(0, config['gamearea'][Y] - self.paddlelength, self.y) 
		# finally, update where the top of the paddle is so it can redraw properly
		self.rect.top = self.y

# Constants
DEBUG			= True
PLAYER1			= 0
PLAYER2 		= 1
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
window = None
clock = pygame.time.Clock()
# configuration
config = dict()
config['resolution'] 	= (800, 600)
config['name'] 			= "Pong"
config['players'] 		= 2
config['framerate']	 	= 80
config['screen_offset'] = (0, 12)
config['gamearea']		= combine_by(diff, config['resolution'], map(lambda x: x*2, config['screen_offset']))
config['divide_height'] = 14
config['paddle_offset'] = 10
# game state
state = dict()
state['paddlelength'] 	= 20
state['player1'] 		= Paddle(PLAYER1)
state['player2'] 		= Paddle(PLAYER2)
state['players_group']	= pygame.sprite.Group(state['player1'], state['player2'])
state['ball'] 			= Ball()
state['objects_group']	= pygame.sprite.Group(state['player1'], state['player2'], state['ball'])
state['score']			= [0,0]
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
window = pygame.display.get_surface()
screen = window.subsurface(pygame.rect.Rect(config['screen_offset'], config['gamearea']))
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
	# erase previous screen
	window.fill(WHITE) # makes top and bottom white lines =)
	screen.fill(BLACK)
	# debug info
	if DEBUG:
		drawText("Speed: " + str(state['player1'].speed))
		drawText("FPS " + str(clock.get_fps()), location = (config['gamearea'][X]/5, 0))
	# scores
	for player, pos in ((PLAYER1, PLAYER2), (1,2)):
		drawText(str(state['score'][player]), location = (config['gamearea'][X] * (pos/3.0), config['gamearea'][Y] * (1/10.0)), size = 72, color = WHITE)
	# middle line
	linewidth = 8
	lineheight = config['divide_height']
	for i in xrange(0, config['gamearea'][Y], 2 * lineheight):
		draw.rect(screen, WHITE, pygame.rect.Rect((config['gamearea'][X] - linewidth) / 2, i, linewidth, lineheight)) 
	# ball and paddles
	state['objects_group'].draw(screen)

def gameloop():
	time = 0
	while not input['quit']:
		time = clock.tick(config['framerate']) / 1000.0 # time is number of seconds since last loop
		updateInput(pygame.event.get(), time)
		updateGame(time)
		updateScreen(time)
		pygame.display.flip()
		pygame.event.pump()
		
def main():
	gameloop()

if __name__ == "__main__":
	main()