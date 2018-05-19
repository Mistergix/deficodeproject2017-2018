"""
simono

a lot of objects that are drawable and have an update
they interact!

"""


#stdlib
import time
import math
from random import randint
import random
#lib
import pygame
from pygame.locals import *
#custom
import data
from util import * # ja..


class Box:
	width=32
	height=32
	def __init__(self,pos,obstacle=None):
		self.obstacle=obstacle
		self.position = pos
		self.type = 1 # unused
		self.stuck = 0 # if its stuck on a surface
		self.moveVector = Vector(0,0) # not unit! implicit speed
		self.rect = None # set for optimization if box is stuck
		self.collRect = None # for optim, this is for collision only

		self.hits = 0 # number of hits

		self.animator = Animator("box")
		self.animator.start("hits0")

	def applyEffect(self,actor):
		# does nothing
		pass

	def draw(self,window):
		window.blit(self.animator.image,(self.position.x,self.position.y+5))
		return 1

	def getRect(self):
		if self.stuck == 1 and (self.rect is not None): # optimization
			return self.rect
		self.rect = pygame.Rect(self.position.x,self.position.y,self.width,self.height)
		return self.rect


	def update(self,timeElapsed):
		if self.stuck == 1:
			return 1
		self.position += self.moveVector * timeElapsed
		# add some gravity
		self.moveVector += Vector(0,100*timeElapsed)
		return 1

	def hitByBullet(self,bullet):
		# not stuck anymore
		# add move vec
		# fly abit up, only if we are not stuck
		if self.stuck == 1:
			self.position += Vector(0,-8)
		self.rect = None
		self.stuck = 0
		# addapt moveVector
		self.moveVector = bullet.moveVector.unit() * 10 # only a fraction of force
		self.hits += 1
		if self.hits > 8:
			return 1
		elif self.hits > 6:
			self.animator.start("hits2")
		elif self.hits > 3:
			self.animator.start("hits1")
		return 0


class MetalBarrel(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("metalbarrel")
		self.animator.start("hits0")

class WoodBarrel(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("woodbarrel")
		self.animator.start("hits0")



class CashBox(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("cash")
		self.animator.start("pause")
		#self.animator.currAnimationStep = randint(0,self.animator.animations["jump"])

	def hitByBullet(self,bullet):
		return 0

	def applyEffect(self,actor):
		actor.counter["cash"] += 1


class SpreadWeaponBox(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("spreadweapon")
		self.animator.start("pause")
		#self.animator.currAnimationStep = randint(0,self.animator.animations["jump"])

	def hitByBullet(self,bullet):
		return 0

	def update(self,timeElapsed):
		Box.update(self,timeElapsed)
		self.animator.update()

	def applyEffect(self,actor):
		actor.weapon = "spread"
		actor.weaponRecieved = time.time()


class FastWeaponBox(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("defaultweapon")
		self.animator.start("pause")
		#self.animator.currAnimationStep = randint(0,self.animator.animations["jump"])

	def hitByBullet(self,bullet):
		return 0

	def update(self,timeElapsed):
		Box.update(self,timeElapsed)
		self.animator.update()

	def applyEffect(self,actor):
		actor.weapon = "fast"
		actor.weaponRecieved = time.time()


class HealthBox(Box):
	def __init__(self,pos,obstacle=None):
		Box.__init__(self,pos,obstacle)
		self.animator = Animator("health")
		self.animator.start("jump")
		self.animator.currAnimationStep = randint(0,self.animator.animations["jump"])

	def update(self,timeElapsed):
		Box.update(self,timeElapsed)
		self.animator.update()

	def hitByBullet(self,bullet):
		return 0

	def applyEffect(self,actor):
		actor.health += 20

class Animator:
	"""
	handles animation states for an object
	"""
	def __init__(self,prefix):
		self.animations ={
				"jump":3,
				"left":3,
				"leftshoot":1,
				"rightshoot":1,
				"right":3,
				"pause":1,
				"dead0":1,
				"dead1":1,
				"dead4":1,
				"hits0":1,
				"hits1":1,
				"hits2":1} # or "hits" for box
		self.currAnimation = "" # none
		self.currAnimationStep = 0
		self.lastFrametime = 0 # when did we last change frames
		self.fps = 10 # frames per sec
		self.prefix = prefix

		self.image = None

	def start(self,ani):
		# dont restart current ani
		if ani == self.currAnimation:
			return
		self.currAnimation = ani
		self.currAnimationStep = 0
		self.lastFrametime = 0 # immediatly change frame
		self.update()

	def update(self):
		nowtime = time.time()
		if not (nowtime - self.lastFrametime >= (1.0 / self.fps)):
			return 1
		if not (self.animations[self.currAnimation] == 1):
			self.currAnimationStep += 1
			if self.currAnimationStep >= self.animations[self.currAnimation]:
				self.currAnimationStep = 0
		self.image = data.loadImage(self.prefix+"_"+self.currAnimation+"_"+str(self.currAnimationStep)+".png")
		self.lastFrametime = nowtime






class Enemy:
	width = 24
	height = 32
	speed = 50
	def __init__(self,pos,obstacle):
		self.position = pos
		self.obstacle = obstacle
		self.state = "RANDOM" # RANDOM, TAKECOVER, SHOOT, TOATTACK, PAUSE
		self.stateStart = 0 # when did state start
		self.stateDuration = 5 # how long staying in one state?
		self.target = None
		self.shootMaxDistance = 250

		self.stuck = 0 # dead, name is strange.. see boxes

		self.shootLast = 0 # last time we shot
		self.shootInterval = 0.8 # all x secs

		self.kiUpdateInterval = 3 # every x seconds
		self.kiLastUpdate = time.time()+randint(2,5) # last time ki got update

		# initial animator setup
		self.animator = Animator("enemy")
		self.animator.start("pause")

		self.health = 3

	def hitByBullet(self):
		self.health -= 1
		if self.health < 0:
			self.stuck = 1
			self.position[1] += 10 # drop to floor
			self.animator.start("dead0")
			return 1
		return 0


	def getBullets(self,target):
		moveDir = Vector(self.position,target.position)
		# if actor is far away, vary height
		if moveDir.length() > self.shootMaxDistance / 2.0:
			bias = random.random() * moveDir.length() / self.shootMaxDistance
			moveDir = moveDir.unit()
			moveDir[1] -= bias
		moveDir = moveDir.unit()
		bulletPos = self.position+moveDir*5
		b = Bullet(bulletPos,moveDir,1)
		return [b]


	def getLeftPosition(self):
		return Vector( (self.obstacle.rect.topleft[0]+self.width,self.obstacle.rect.topleft[1]))

	def getRightPosition(self):
		return Vector( (self.obstacle.rect.topright[0]-self.width,self.obstacle.rect.topright[1]))

	def kiUpdate(self,actor,obstacles):
## STATE CHANGE
		self.animator.start("pause")
		self.target = None # gets set if we see smth
		self.state = "RANDOM"
		distance = (actor.position - self.position).length() # disct ene<->act
		if actor.obstacle:
			distanceObstacles = Vector(actor.obstacle.rect.midtop,self.obstacle.rect.midtop).length()
			if distanceObstacles - self.obstacle.rect.width >= self.shootMaxDistance:
				return
		# if actor within range, do visibility check
		if (actor.obstacle != self.obstacle):
			# lines we need to test:
			loslines = []
			# first losline is special, it tests between us and actor
			loslines.append( ((actor.position.x,actor.position.y),(self.position.x,self.position.y) ) )
			# LL RR LR RL
			if actor.obstacle:
				loslines.append( (actor.obstacle.rect.topleft,self.obstacle.rect.topleft) )
				loslines.append( (actor.obstacle.rect.topright,self.obstacle.rect.topleft) )
				loslines.append( (actor.obstacle.rect.topright,self.obstacle.rect.topright) )
				loslines.append( (actor.obstacle.rect.topleft,self.obstacle.rect.topright) )
			losi = 0
			for loslinepair in loslines:
				if self.state != "RANDOM":
					break
				intersection = 0
				for o in obstacles:
					# dont check own obstacales, if not checking enemy<->pos los
					if (loslinepair[0] != (actor.position.x,actor.position.y)) and ((o == self.obstacle) or (o == actor.obstacle)):
						continue
					x1 = loslinepair[0][0]
					x2 = loslinepair[1][0]
					x3 = o.rect.topleft[0]
					x4 = o.rect.topright[0]
					y1 = loslinepair[0][1]
					y2 = loslinepair[1][1]
					y3 = o.rect.topleft[1]
					y4 = o.rect.topright[1]
					#print "x1,x2,x3,x4,y1,y2,y3,y4 = " +str(( x1,x2,x3,x4,y1,y2,y3,y4))
					uadiv = ((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))
					ubdiv = ((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))
					if uadiv == 0 or ubdiv == 0:
						break
					ua= ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3)) / uadiv
					ub= ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3)) / ubdiv
					#print "ua/ub " +str((ua,ub))
					if (ua>=0 and ua<=1) and (ub>=0 and ub<=1):
						# intersection.. this is BAD
						intersection = 1
						break
				if intersection == 0:
					# we checked los enemy<->actor
					if (loslinepair[0] == (actor.position.x,actor.position.y)):
						# we have los to ACTOR!!!
						# lets kill him
## STATE CHANGE
						self.state = "SHOOT"
						if self.position.x <= actor.position.x:
							self.animator.start("rightshoot")
						else:
							self.animator.start("leftshoot")
						self.stateStart = time.time()
						break
					else:
## STATE CHANGE
						self.state = "TOATTACK"
						self.stateStart = time.time()
						if losi in [1,2]:
							#self.target=Vector(loslinepair[1]) # topleft, etc
							self.target=self.getLeftPosition() # topleft, etc
						else:
							self.target=self.getRightPosition()
						dir = None
						if self.target.x >= self.position.x:
							dir = "left"
						else:
							dir = "right"
						self.animator.start(dir)
						break
				losi += 1
		else:
			# actor on plattform?
			# if actor is on our obstacle, fuck it
			if actor.obstacle == self.obstacle:
				self.target = Vector(actor.position)
				self.state = "SHOOT"
##		print "KI state "+str(self.state)
##		print "\tKI target "+str(self.target)
##		print"\KI<->act "+str(distance)
##		print"\ob<->ob "+str(distanceObstacles)


	def update(self,timeElapsed,actor,obstacles):
		# what to do?
		# bin nur an actor interessiert, wenn einem endpunkt meines
		# obstacles und einem seines eine sichtlinie ist
		# ODER
		# wenn actor auf keinem obstacle und in meiner schussweite ist

		# enemy changes nur alle 5sec oder so seinen state
		# dazwischen verfolgt er dem plan
		if self.stuck == 1:
			# death animation is started in NotAnObject.gameLoop on coll detect
			return []

		self.animator.update()

		nowtime = time.time()
		if (nowtime - self.kiLastUpdate >= self.kiUpdateInterval) and ( (nowtime - self.stateStart >= self.stateDuration) or (self.state in ["TOATTACK","SHOOT","PAUSE" ])):
			self.kiUpdate(actor,obstacles)
			self.stateStart = nowtime
			self.kiLastUpdate = nowtime

		# do action, according to state
		if self.state == "TOATTACK":
			movedir = Vector( self.target.x - self.position.x,0) # not unit
			self.position += (movedir.unit() * self.speed * timeElapsed)
			if movedir.length() <= 10:
				# since we cant shoot.. we should be random again
## STATE CHANGE
				self.state = "RANDOM"
				self.stateStart = nowtime
				self.target = None
		elif self.state == "SHOOT":
			# return a bullet object
			# todo: abhaengig von entferungung etwas hoeher und so
			if nowtime - self.shootLast >= self.shootInterval:
				self.shootLast = nowtime
				return self.getBullets(actor)
		elif self.state == "RANDOM":
			movedir = Vector(0,1)
			if self.target:
				movedir = Vector(self.target.x - self.position.x,0) # not unit
			if (self.target is None):
				i = randint(0,1)
				self.target = Vector( randint(self.obstacle.rect.topleft[0]+self.width,self.obstacle.rect.topright[0]-self.width),self.position.y)
				self.stateStart = nowtime
				movedir = Vector(self.target.x - self.position.x,0) # not unit
				dir = None
				if movedir.x >= 0:
					dir = "right"
				else:
					dir = "left"
				self.animator.start(dir)
			else:
				if (movedir.length() <= 10):
## STATE CHANGE
					self.state = "PAUSE"
					self.stateStart = nowtime
					self.animator.start("pause")
			if (movedir.length() > 10):
				self.position += (movedir.unit() * self.speed * timeElapsed)
		elif self.state == "PAUSE":
			if nowtime - self.stateStart >= self.stateDuration:
## STATE CHANGE
				self.state = "RANDOM"
				self.stateStart = nowtime

		return []
	def getRect(self):
		return pygame.Rect(self.position.x,self.position.y,self.width,self.height)

	def draw(self,window):
		window.blit(self.animator.image,(self.position.x,self.position.y))



class RobotEnemy(Enemy):
	def __init__(self,pos,obstacle):
		Enemy.__init__(self,pos,obstacle)
		self.animator = Animator("robot")
		self.animator.animations["left"] = 1
		self.animator.animations["right"] = 1

		self.animator.start("pause")
		self.health = 5
		self.shootInterval = 0.35
		# robot enemy also got special code in Enemy.kiUpdate
		# because he is BELOW the plattform this plattform never
		# obstructs him


	def getBullets(self,target):
		moveDir = Vector(self.position,target.position)
		# if actor is far away, vary height
		# THIS IS LESS FOR ROBOT THEN FOR NORMAL ENEMY
##		if moveDir.length() > self.shootMaxDistance / 2.0:
##			bias = random.random() * moveDir.length() / (self.shootMaxDistance*2)
##			moveDir = moveDir.unit()
##			moveDir[1] -= bias
		moveDir = moveDir.unit()
		bulletPos = self.position+moveDir*5
		b = Bullet(bulletPos,moveDir,1)
		return [b]

	def hitByBullet(self):
		self.health -= 1
		if self.health < 0:
			self.stuck = 1
			#self.position[1] += 10 # drop to floor
			self.animator.start("dead0")
			return 1
		return 0

class DevilEnemy(Enemy):
	def __init__(self,pos,obstacle):
		Enemy.__init__(self,pos,obstacle)
		self.animator = Animator("devil")
		self.animator.start("pause")
		self.health = 5
		self.shootInterval = 0.9


	def getBullets(self,actor):
		moveDir = Vector(self.position,actor.position)
		# if actor is far away, vary height
		if moveDir.length() > self.shootMaxDistance / 2.0:
			bias = random.random() * moveDir.length() / self.shootMaxDistance
			moveDir = moveDir.unit()
			moveDir[1] -= bias
		moveDir = moveDir.unit()
		bulletPos = self.position+moveDir*5
		b1 = Bullet(bulletPos,moveDir,1)
		b2 = Bullet(bulletPos,moveDir.rotate(math.radians(5)),1)
		b3 = Bullet(bulletPos,moveDir.rotate(math.radians(-5)),1)
		return [b1,b2,b3]


class Actor:
	width = 24
	height= 32
	speed = 150
	def __init__(self,x,y):
		self.position = Vector(x,y)

		self.ropeStatus = "none" # none, shoot, fixed

		self.ropeDirection = Vector(0,0) # set, when we are currently shooting a rope
		self.ropeShootSpeed = 500.0 # pixels per sec
		self.ropeLength = 0 # set to something, when rope is shooting / finished
		self.ropeHeadPosition = None # set to smth, when rope is finished
		self.ropeObstacle = None # the obstacle the rope is attached to

		self.shortenRope = 0

		self.moveVector  = Vector(0,30)
		self.rotationSpeed = 0.0 # winkelgrad per sec


		self.keyMoveX = 0
		self.keyJump = 0

		self.obstacle = None # gets set, when actor is on an obstacle

		self.health = 100

		self.weapon = "normal" # normal, spread, fast
		self.shooting = 0 # if we are shooting or not
		self.shootLast = 0 # last time we shot
		self.shootInterval = 0.2 # all x secs

		self.weaponReset = 25 # sec after we get normal wepaon back
		self.weaponRecieved = 0 # check every time

		self.counter = {"enemykill":0,"boxkill":0,"cash":0,"drop":0}

		# init animator
		self.animator = Animator("actor")
		self.animator.start("pause")

	def draw(self,window):
		"""
		draw actor and rope
		"""
		# draw actor
		#pygame.draw.rect(window,(0,255,0), self.getRect(), 0)
		window.blit(self.animator.image,self.getRect())
		# draw rope
		if self.ropeStatus != "none":
			ropeHeadPosition = self.getRopeHeadPosition()
			pygame.draw.aaline(window,(204,103,0),(self.position.x+(self.width/2.0),self.position.y),
						(ropeHeadPosition.x,ropeHeadPosition.y),4)

	def update(self,timeElapsed):
		"""
		update actor position
		returns bullets or []
		"""
		newbullets = []
		if self.health <= 0:
			self.animator.start("dead4")
			self.ropeStatus = "none"
			return newbullets

		self.animator.update()

		# if shooting, shoot
		nowtime = time.time()
		shootI = self.shootInterval
		if self.weapon == "fast":
			shootI = self.shootInterval - 0.15
		elif self.weapon == "spread":
			shootI = self.shootInterval + 0.01
		if (nowtime - self.shootLast>= shootI) and self.shooting:
			newbullets = self.getBullets(pygame.mouse.get_pos())
			self.shootLast = nowtime

		# weapon reset
		if (nowtime - self.weaponRecieved) > self.weaponReset:
			self.weapon = "normal"
			self.weaponRecieved = 0


		if self.ropeStatus is not "none":
			if self.ropeStatus == "shoot":
				self.ropeLength += ( self.ropeShootSpeed * timeElapsed)
				if self.ropeLength > 600:
					self.ropeStatus = "none"
				if self.obstacle is None:
					self.moveGravity(timeElapsed)
			elif self.ropeStatus == "fixed":
				self.moveOnRope(timeElapsed)
			#elif self.ropeStatus == "none":


			if self.ropeStatus == "fixed" and self.shortenRope != 0:
				# shorten rope and recalc pos according to it
				shortenBy = 3.0 * self.shortenRope
				self.ropeLength -= shortenBy # not sure if we need to shorten length?
				ropeHead = self.getRopeHeadPosition()
				# if we got up to obstacle => jump up
				#print self.ropeLength
				if self.ropeLength <= 10:
					self.ropeStatus = "none"
					self.moveVector = Vector(0,-150)
				towardRopeHead = Vector(self.position,ropeHead).unit()
				self.position += towardRopeHead * shortenBy

		else:
			if self.obstacle is None:
				self.moveGravity(timeElapsed)
			else:
				# we are standing on an obstacles
				self.moveKeys(timeElapsed)
		return newbullets

#--- movement functions
	def moveKeys(self,timeElapsed):
		"""
		move with wasd
		"""
		self.position += Vector(self.speed * timeElapsed * self.keyMoveX,0)

		# check wether we are falling of the obstacle
		if (( self.position.x <= self.obstacle.rect.x) or
			( self.position.x >= self.obstacle.rect.x + self.obstacle.rect.width) ):
			self.obstacle = None
			self.moveVector = Vector(self.keyMoveX*50,0)


	def moveGravity(self,timeElapsed):
		"""
		movement in free fall
		"""
		self.moveVector += Vector(0,150*timeElapsed) #* timeElapsed
		self.position += (self.moveVector * timeElapsed)

	def moveOnRope(self,timeElapsed):
		"""
		position updates if we are on a rope.
		we just move in a circle, but have a strange if-clause, that causes
		as to swing forth and back
		"""
		# we change the rotationspeed if:
		# -- it is 0
		# -- or we are moving up a slope and are getting to slow => swing back
		ropeVector = self.getRopeHeadPosition() - self.position
		ropeAngle = ropeVector.angle_in_degrees( Vector(0,-1))
		if ((abs(self.rotationSpeed) <= 0.0001) or
				(
					( (abs(ropeAngle/self.rotationSpeed) >= 1.4) ) and
						(
						(self.rotationSpeed <= 0.0 and self.position.x > self.getRopeHeadPosition().x) or
						(self.rotationSpeed >= 0.0 and self.position.x < self.getRopeHeadPosition().x)
						)
				)
			):
			self.rotationSpeed *= -0.9
			if self.rotationSpeed == 0.0:
				self.rotationSpeed = 10
		ropeVector = ropeVector.rotate(math.radians(self.rotationSpeed)*timeElapsed)
		self.position = self.getRopeHeadPosition() - ropeVector

		slowDown = 180* timeElapsed
		speedUp = 150* timeElapsed
		slowDownAcc = 1.0
		speedUpAcc = 1.02
		# get slower, if we are already on other side of rope
		if self.rotationSpeed < 0.0:
			if (self.position.x > self.getRopeHeadPosition().x):
				self.rotationSpeed *= slowDownAcc
				self.rotationSpeed += slowDown
			else:
				# get faster
				self.rotationSpeed *=speedUpAcc
				self.rotationSpeed -=speedUp
		elif self.rotationSpeed > 0.0:
			if self.position.x < self.getRopeHeadPosition().x:
				self.rotationSpeed *= slowDownAcc
				self.rotationSpeed -= slowDown
			else:
				#get faster
				self.rotationSpeed *=speedUpAcc
				self.rotationSpeed +=speedUp
				#self.rotationSpeed += speedUp

		# cap rotationspeed
		maxRotSpeed = 170
		if self.rotationSpeed > maxRotSpeed:
			self.rotationSpeed = maxRotSpeed
		elif self.rotationSpeed < -maxRotSpeed:
			self.rotationSpeed = -maxRotSpeed



#--- helpers

	def keyUp(self,key):
		if (key in [K_a, K_LEFT]) and self.keyMoveX == -1:
			self.keyMoveX = 0
			self.animator.start("pause")
		if (key in [K_d,K_RIGHT]) and self.keyMoveX == 1:
			self.keyMoveX = 0
			self.animator.start("pause")
		elif key in [K_w,K_s, K_UP,K_DOWN]:
			self.shortenRope = 0

	def keyDown(self,key):
		if self.obstacle is not None:
			if key in [K_a,K_LEFT]:
				if self.keyMoveX != -1:
					self.animator.start("left")
				self.keyMoveX = -1
			elif key in [K_d,K_RIGHT]:
				if self.keyMoveX != 1:
					self.animator.start("right")
				self.keyMoveX = 1
		if key in [K_w,K_UP]:
			self.shortenRope = 1
		elif key in [K_s,K_DOWN]:
			self.shortenRope = -1

	def aquireRotationMoveVector(self):
		"""
		rotation speed to move vector... sort of, we just approximate
		the vector speed, when we let go of the rope
		"""
		#if self.rotationSpeed <= 0:
		ropeVector = self.getRopeHeadPosition() - self.position
		self.moveVector = ropeVector.perpindicular().unit() * self.rotationSpeed * -1
##		ropeHead = self.getRopeHeadPosition()
##		ropeVector = self.getRopeHeadPosition() - self.position
##		# perpindicular vector
##		if self.position.x > ropeHead.x:
##			self.moveVector = ropeVector.perpindicular().unit() * abs(self.rotationSpeed)
##		else:
##			self.moveVector = ropeVector.perpindicular().unit() * abs(self.rotationSpeed)
##			self.moveVector = Vector(self.moveVector.x * -1,self.moveVector.y)

	def aquireGravityRotationSpeed(self):
		"""
		vector speed to rotation speed - approximated.
		when we grab a rope from free fall, this gets the initial
		rotation speed
		"""
		ropeHead = self.getRopeHeadPosition()
		if self.position.x > ropeHead.x:
			self.rotationSpeed = self.moveVector.length() * 0.7
		else:
			self.rotationSpeed = - self.moveVector.length() * 0.7

	def getRopeHeadPosition(self):
		"""
		where is the rope head at?
		"""
		if self.ropeHeadPosition is not None:
			return self.ropeHeadPosition
		else:
			return ( self.position + ( self.ropeDirection  * self.ropeLength) )


	def getRect(self):
		return pygame.Rect(self.position.x,self.position.y,self.width,self.height)

#--- actor action requests


	def hitByBullet(self):
		self.health -= 5

	def getBullets(self,pos):
		"""
		returns a bullet shooting at given pos
		"""
		moveDir = Vector(self.position,pos).unit()
		bulletOrig = self.position + Vector(self.width/2.0,self.height/2.0)
		bulletPos = bulletOrig+moveDir*5
		blist = []
		if self.weapon == "spread":
			blist.append( Bullet(bulletPos,moveDir.rotate(math.radians(5))) )
			blist.append( Bullet(bulletPos,moveDir.rotate(math.radians(-5))) )
		blist.append( Bullet(bulletPos,moveDir) )
		return blist

	def landedOnObstacle(self,o):
		self.obstacle = o
		self.position.y = (self.obstacle.rect.topleft[1] - self.height +3)
		self.moveVector = Vector(0,0)


	def dropRopeRequest(self):
		"""
		player lets loose of the rope
		"""
		if self.ropeStatus == "fixed":
			self.aquireRotationMoveVector()
			self.rotationSpeed = 0
			self.ropeStatus = "none"

	def shootRopeRequest(self,mousepos):
		"""
		player shoots a rope in mouse direction
		"""
		# take move vec from current perp vector
		if self.ropeStatus == "fixed":
			self.aquireRotationMoveVector()

		#self.obstacle = None
		self.ropeStatus = "shoot"
		ropeDirection = Vector( self.position,mousepos).unit()
		self.ropeHeadPosition = None
		self.ropeDirection = ropeDirection
		self.ropeLength = 2

	def ropeCollideUpdate(self,collidepos):
		"""
		shot rope collided with smth at collidepos, so we
		can now svae the ropeHeadPos. this also fixes the length
		"""
		self.ropeStatus = "fixed"
		self.obstacle = None
		self.ropeHeadPosition = collidepos
		self.ropeDirection = None
		self.aquireGravityRotationSpeed()


class Obstacle:
	def __init__(self,x,y,w,h):
		self.position = Vector(x,y)
		self.w = w
		self.h = h
		self.rect = pygame.Rect(self.position.x,self.position.y,self.w,self.h)
		self.image = None


	def getRect(self):
		return self.rect

	def recalcRect(self):
		self.rect = pygame.Rect(self.position.x,self.position.y,self.w,self.h)


	def draw(self,window):
		# the real vect we will draw
		rectVerticalOffset = 3
		drawRect = pygame.Rect(self.rect.x,self.rect.y+rectVerticalOffset,self.rect.width,self.rect.height-rectVerticalOffset)
		topWidth = drawRect .width * 0.8
		sideOffset = (drawRect .width - topWidth) / 2.0
		verticalOffset = 10
		topLeft = (drawRect.topleft[0]+sideOffset,drawRect.y-verticalOffset )
		topRight = (drawRect.topright[0]-sideOffset,drawRect.y-verticalOffset )
		pygame.draw.aaline(window,(0,0,0),topLeft,drawRect.topleft,2)
		pygame.draw.aaline(window,(0,0,0),topRight,drawRect.topright,2)
		pygame.draw.aaline(window,(0,0,0),topRight,topLeft,4)
		pygame.draw.rect(window,(127,127,127),drawRect,0)
		pygame.draw.rect(window,(0,0,0),drawRect,1)


class Bullet:
	# types
	def __init__(self,pos,move,type=0):
		self.position = pos
		self.moveVector = move
		self.speed = 300.0
		self.type = type # 0 = actor, 1 = enemies
		# for better coll detec, save lastpos
		# and intersect line+other
		self.lastPosition = self.position
		self.stuck = 0 # 1 if bullet hit something.. like obastcle
		self.stuckTime = 0

	def draw(self,window):
		color = (50,50,50)
		if self.stuck == 1:
			color = (0,0,0)
		pygame.draw.circle(window,color,(int(self.position.x),int(self.position.y)),2,0)
		return 1

	def update(self,timeElapsed):
		if self.stuck == 1:
			return 1
		self.lastPosition = self.position
		self.position += self.moveVector * ( self.speed * timeElapsed )
		# add some gravity effect
		self.moveVector[1] += 0.5 * timeElapsed
		return 1

