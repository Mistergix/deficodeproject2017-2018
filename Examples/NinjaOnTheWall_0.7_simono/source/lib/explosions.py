"""
simono

explosions... have particles
take care of themselves
no interaction with gameobjects (?)

"""

#stdlib
import time
import math
from random import randint
#lib
import pygame
from pygame.locals import *
#custom
import data
from util import * # ja..

class Explosion:
	def __init__(self,pos):
		self.position = pos # a Vector
		self.createTime = time.time()
		self.particles = []
		# particle = (Vec(x,y),Vec(movex,movey))
		#todo: randomize size of particles as well!!
		self.start = time.time()
		self.stuck = 0 # deactivate
		## overwrite the following
		self.color = (204,102,0)
		self.count = 20
		self.size = 4
		self.lifetime = 10
		self.form = "circ"



	def update(self,timeElapsed):
		nowtime = time.time()
		if nowtime - self.start >= self.lifetime:
			self.stuck = 1
			return 1
		# create new particles
		maxPart = self.count
		if len(self.particles) < maxPart:
			for i in range( randint(1,maxPart - len(self.particles)) ):
				addx = randint(-10,3)
				addy = randint(-10,3)
				if addx == 0 and addy == 0:
					continue
				randpos = Vector( self.position.x + addx,self.position.y + addy)
				movedir = (randpos - self.position).unit()
				self.particles.append( (randpos,movedir) )
		# move particles
		tmpFreshParticles = []
		for (pos,mov) in self.particles:
			pos += ( mov * ( 100 * timeElapsed) )
			tmpFreshParticles.append( (pos,mov) )
			mov[1] += 0.8 * timeElapsed
		self.particles = tmpFreshParticles

	def draw(self,window):
		for (pos,mov) in self.particles:
			if self.form == "circ":
				pygame.draw.circle(window,self.color,(int(pos.x),int(pos.y)),int(self.size),0)
			else:
				pygame.draw.rect(window,self.color,pygame.Rect(int(pos.x),int(pos.y),self.size,self.size),0)


class BoxExplosion(Explosion):
	"""
	whole box explodes, box dies
	"""
	def __init__(self,pos):
		Explosion.__init__(self,pos)
		self.color = (204,102,0)
		self.size = 7
		self.count = 10
		self.lifetime = 5
		self.form = "rect"


class BloodExplosion(Explosion):
	"""
	some blood shows, when hit
	"""
	def __init__(self,pos):
		Explosion.__init__(self,pos)
		self.color = (255,0,0)
		self.size = 2
		self.count = 3
		self.lifetime = 2
		self.form = "rect"

class WoodExplosion(Explosion):
	"""
	some wood if we hit a box
	"""
	def __init__(self,pos):
		Explosion.__init__(self,pos)
		self.color = (204,102,0)
		self.size = 2
		self.count = 3
		self.lifetime = 2
		self.form = "rect"

class HumanExplosion(Explosion):
	"""
	blood, flesh everything.. human dies
	"""
	def __init__(self,pos):
		Explosion.__init__(self,pos)
		self.color = (255,0,0)
		self.size = 5
		self.count = 10
		self.lifetime = 5