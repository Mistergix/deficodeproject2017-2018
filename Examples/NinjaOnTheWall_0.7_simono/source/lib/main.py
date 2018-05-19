'''
simono

a fake object that manages the game state and pygame
'''

#stdlib
import time
import math
from random import randint
import pickle
#lib
import pygame
from pygame.locals import *
#custom
import data
from util import * # yes yes...
import gameobjects
import explosions

SCREENWIDTH = 800
SCREENHEIGHT = 600


def sortObstaclesByY(a,b):
	if a.position.y > b.position.y:
		return 1
	if a.position.y < b.position.y:
		return -1
	return 0

def main():
	print "Starting up..."
	noa = NotAnObject()
	noa.gameLoop()
	try:
		import psyco
		psyco.full()
	except ImportError:
		pass

class MixerControl(Borg):
	sound = "on" # on/off
	maxSounds = 50
	sounds = []
	music = "on"

	def __init__(self):
		pygame.mixer.set_num_channels(self.maxSounds)

		pygame.mixer.music.load(data.loadMusic())
		pygame.mixer.music.play(-1)

	def toggleMusic(self):
		if self.music == "on":
			pygame.mixer.music.stop()
			self.music = "off"
		else:
			pygame.mixer.music.play(-1)
			self.music = "on"


	def play(self,sound):
		if self.sound == "off":
			return
		if len(self.sounds) > self.maxSounds:
			self.sounds[0].stop()
			self.sounds = self.sounds[1:]
		s = data.loadSound(sound)
		s.play(0)
		self.sounds.append(s)


class NotAnObject:

	def __init__(self):
		pygame.init() # magic
		#self.window = pygame.display.set_mode( (SCREENWIDTH,SCREENHEIGHT),pygame.FULLSCREEN ) # get a surface to draw on
		self.fullscreen = 0
		self.window = pygame.display.set_mode( (SCREENWIDTH,SCREENHEIGHT)) # get a surface to draw on
		pygame.display.set_caption( 'Ninja On the Wall' ) # set a window caption
		self.backgroundSrf  = pygame.Surface( self.window.get_size() ) # create a surface, same size as window
		self.backgroundSrf.fill( (191,191,191) ) # fill surface with black color
		self.window.blit(self.backgroundSrf, (0,0) ) # blit (=put) background on window
#		self.gameFont=pygame.font.SysFont(pygame.font.get_default_font(), 40)
#		self.gameFontSmall=pygame.font.SysFont(pygame.font.get_default_font(), 20)
#		self.gameFontMedium=pygame.font.SysFont(pygame.font.get_default_font(), 30)
		self.gameFont=pygame.font.SysFont("Lucida Console", 40)
		self.gameFontSmall=pygame.font.SysFont("Lucida Console", 20)
		self.gameFontMedium=pygame.font.SysFont("Lucida Console", 30)

		pygame.display.flip() # magic, needed to display window updates

		self.running = 1
		self.lastFrametime = 0
		self.fps = 70.0 # target fps

		# difficulty.... effects actor health
		self.difficulty = 1 # 0 => easy, 1=> normal, 3 => hard
		self.lastLevel = 0 # if this is the last level and all enemies are dead => game won!!

		self.endlessMode = 0 # if in endless, dont load level, but generate on the fly

		self.editorMode = 0 # in editor mode, other loop

		self.levelSelectMode = 0 # in level selct screen, other loop

		self.state = "WAIT" # WAIT => SHRINK => DROP
		self.stateWaitStart = time.time()
		self.stateWaitDuration = 15

		self.srfCrosshair = data.loadImage("crosshair.png")

		# for dropping bottom part
		self.dropWidth = SCREENWIDTH
		self.dropHeight = None # different.. depend on where lowest plattform is

		self.initialDropSpeed = 100
		self.dropSpeed = self.initialDropSpeed

		self.lastShrinkSurface = None


		# for falling top part
		self.fallHeight = 0

		self.mixer = MixerControl()

		self.inMenu = 1 # 1 if player pressed escape

		pygame.mouse.set_visible(0)

		self.tutorialMaps = ["customtut0.lvl","customtut1.lvl","customtut2.lvl","customtut3.lvl"]
		self.tutorialInfo = ["tut0.png","tut1.png","tut2.png","tut3.png"]
		self.tutorialMap = -1
		self.tutorialInfoShown = 0
		self.levelName = "customtut0.lvl"
		
		self.mapComplete = 0

		self.startUp()

	def startUp(self):
		"""
		sets all important info, that must be present before startup
		can also be used for a complete reset
		"""
		self.mapComplete = 0

		self.actor = None
		self.obstacles = []
		self.bullets = []
		self.explosions = []
		self.enemies = []
		self.boxes = []
		self.lastLevel = 0
		self.state = "WAIT"
		self.stateWaitStart = time.time()

		self.ydiff = 0 # current y diff due to dropping

		self.loadedObjects = None
		# ACTOR create
		self.actor = gameobjects.Actor(SCREENWIDTH-50,SCREENHEIGHT-50)

		if self.difficulty == 0.5:
			self.actor.health = 200
		elif self.difficulty == 2:
			self.actor.health = 50

		if self.endlessMode:
			# auto generate
			# enemies, obstacles
			lasti = 0
			i = 100
			while i <= SCREENHEIGHT-150:
				# important: -30 hier sind min abstand von zwei levels!!!!!
				(enemies,obstacles,boxes) = self.createNewLevel( (lasti,i-30))
				# on first starat we have bottom obstacle
				# create bottom obstacle
				self.obstacles.append( gameobjects.Obstacle(0,SCREENHEIGHT-11,SCREENWIDTH,11))
				self.obstacles += obstacles
				self.enemies += enemies
				self.boxes += boxes
				lasti = i
				i += randint(50,150)
		else:
			# load from file
			if self.editorMode == 1:
				# load all
				self.loadNewLevel(-1,-1)
				# calc drop lines
				self.calcDropLines()
			else:
				self.loadNewLevel(0,SCREENHEIGHT) # set loadedObjects for use in loadNewLevel

		self.calcDropHeight() # set dropheight

	def gameLoop(self):
		"""
		this is UGLY.
		dont look at me. if you want to understand how i work, plesae take
		a look at gameobjects first, makes more sense

		or look at seperate loops within the while block
		"""

		realBoxes = [gameobjects.WoodBarrel,gameobjects.MetalBarrel,gameobjects.Box]


		self.lastFrametime = time.time()
		cc = 0 # for frame printing
		fpslist = []
		while self.running == 1:

			fTime = time.time()
			nowtime = fTime
			timeElapsed = fTime - self.lastFrametime
			if timeElapsed > 1/self.fps:
				self.lastFrametime = fTime
##				if cc > 10:
##					fps = sum(fpslist) / 10.0
##					fpslist = []
##					print "FPS "+str(fps)
##					cc = 0
##				else:
##					fpslist.append(1/timeElapsed)
##					cc += 1
				# clear screen
				self.window.blit(self.backgroundSrf, (0,0) ) # blit (=put) background on window




				# editormode check AFTER selectmode!
				if self.levelSelectMode == 0 and self.editorMode == 1:
					self.editorLoop(timeElapsed)
					continue



## OBSTACLES draw
				for o in self.obstacles:
					o.draw(self.window)				# USER INPUT
## actor update
				if self.inMenu == 0 and self.levelSelectMode == 0:
					self.handleKbdMouse()
				elif self.inMenu == 1:
					self.handleKbdMouseMenu()

				newBullets = self.actor.update(timeElapsed)
				if len(newBullets):
					self.bullets += newBullets
					if self.actor.weapon == "spread":
						self.mixer.play("shotgun.wav")
					else:
						self.mixer.play("gun.wav")

## enemies <-> bullets (both must be non-stuck)
				for b in [xb for xb in self.bullets if xb.stuck == 0 and xb.type == 0]:
					for e in [xe for xe in self.enemies if xe.stuck == 0]:
						if e.getRect().collidepoint(b.position.x,b.position.y):
							# kill enemy
							killEnemy = e.hitByBullet()
							if killEnemy:
								self.explosions.append( explosions.HumanExplosion( b.position))
								# add counter if bullet is from player
								if b.type == 0:
									if isinstance(e,gameobjects.DevilEnemy):
										# devil counts *2
										self.actor.counter["enemykill"] += 2
										self.mixer.play("devildying.wav")
									elif isinstance(e,gameobjects.RobotEnemy):
										self.actor.counter["enemykill"] += 3
										self.mixer.play("robotdying.wav")
									else:
										self.actor.counter["enemykill"] += 1
										self.mixer.play("dying.wav")
							else:
								self.explosions.append( explosions.BloodExplosion( b.position))
							b.stuck = 1
							self.bullets.remove(b)
							break

## ENEMIES draw, update
				for e in self.enemies:
					newBullets = e.update(timeElapsed,self.actor,self.obstacles)
					if len(newBullets):
						self.bullets += newBullets
					e.draw(self.window)

				dropoff = SCREENHEIGHT - self.dropHeight # need this
					# dropoff... because obst dont collide if below this


## actor <-> bullets
				for b in [xb for xb in self.bullets if xb.stuck == 0 and xb.type == 1]:
					if self.actor.getRect().collidepoint(b.position.x,b.position.y):
						self.actor.hitByBullet()
						self.explosions.append( explosions.BloodExplosion( b.position))
						b.stuck = 1
						self.bullets.remove(b)

## rope <-> obstacle
				if self.actor.ropeStatus == "shoot":
					ropeHeadPosition = self.actor.getRopeHeadPosition()
					ropeHeadRect = pygame.Rect(ropeHeadPosition.x,
												ropeHeadPosition.y,
												5,5)
					for o in self.obstacles:
						# if obst is dropping.. forget it
						if o.position.y >= dropoff and (self.state in ["SHRINK"]):
							continue
						if o.rect.colliderect( ropeHeadRect) == True:
							self.actor.ropeCollideUpdate( ropeHeadPosition)
							break
## actor <-> obstacle
				elif self.actor.ropeStatus == "none" and self.actor.obstacle is None:
					origRect = self.actor.getRect()
					hitHeight = 5
					hitWidth = 5
					actorRect = pygame.Rect(origRect.midbottom[0]-hitWidth/2.0,origRect.midbottom[1]-hitHeight/2.0,hitWidth,hitHeight)
					for o in self.obstacles:
						# if obst is dropping.. forget it
						if o.position.y >= dropoff and (self.state in ["SHRINK"]):
							continue
						topRect = pygame.Rect(o.rect.x,o.rect.y,o.rect.width,2)
						if topRect.colliderect(actorRect):
							self.actor.landedOnObstacle(o)
							break

## bullets <-> obstacles
				for b in self.bullets:
					b.update(timeElapsed)
					for o in self.obstacles:
						if o.rect.collidepoint(b.position.x,b.position.y):
							b.stuck = 1
					b.draw(self.window)


## BOXES draw+update
				for b in self.boxes:
					# boxes <-> obstacles
					for o in self.obstacles:
						if o.rect.colliderect(b.getRect()):
							b.stuck = 1
					b.update(timeElapsed)
					b.draw(self.window)
					# no boxes<->bullets if its health
					if isinstance(b,(gameobjects.HealthBox,gameobjects.CashBox,gameobjects.SpreadWeaponBox,gameobjects.FastWeaponBox)):
						# healt/cash/etc<-> actor
						if self.actor.getRect().colliderect(b.getRect()):
							b.applyEffect(self.actor)
							if isinstance(b,gameobjects.CashBox):
								self.mixer.play("cashreg.wav")
							if isinstance(b,gameobjects.HealthBox):
								self.mixer.play("healthpickup.wav")
							elif isinstance(b,(gameobjects.SpreadWeaponBox,gameobjects.FastWeaponBox)):
								self.mixer.play("reload.wav")
							self.boxes.remove(b)
						continue

					# boxes <-> bullets
					for bull in [xb for xb in self.bullets if xb.stuck == 0]:
						if b.getRect().collidepoint(bull.position.x,bull.position.y):
							killBox = b.hitByBullet(bull)
							bull.stuck = 1
							self.bullets.remove(bull)
							if killBox:
								self.boxes.remove(b)
								# create an explosion
								self.explosions.append( explosions.BoxExplosion( b.position) )
								# add counter if bullet is from player
								if bull.type == 0:
									self.actor.counter["boxkill"] += 1
								break
							else:
								self.explosions.append( explosions.WoodExplosion( b.position) )



## fall, drop, managing
				if self.state == "WAIT":
					if (nowtime - self.stateWaitStart >= self.stateWaitDuration) and (self.lastLevel == 0):
						self.mixer.play("shrink.wav")
						self.state = "SHRINK"
						if self.actor.health > 0:
							self.actor.counter["drop"] += 1
					elif (self.lastLevel == 0):
						width = int(5 * ( (nowtime - self.stateWaitStart) / float(self.stateWaitDuration)))
						p1 = (0,SCREENHEIGHT-self.dropHeight)
						p2 = (SCREENWIDTH,SCREENHEIGHT-self.dropHeight)
						linecolor = (0,0,0)
						pygame.draw.line(self.window,linecolor,p1,p2,width)
				elif self.state == "SHRINK":
					self.shrinkBottom(timeElapsed)
				elif self.state == "DROP":
					self.dropDown(timeElapsed)

## drop the actor of the obstacle, if he is standing on
				# on that is shrinking
				if self.state == "SHRINK":
					if (self.actor.obstacle is not None) and (self.actor.obstacle.position.y >= dropoff):
						self.actor.obstacle = None


## draw actor - after bottom falling
				self.actor.draw(self.window)

				# help image
				#self.window.blit(self.helpImage,(2,SCREENHEIGHT-145))


## EXPLOSIONS update, draw
				for e in self.explosions:
					e.update(timeElapsed)
					e.draw(self.window)
					if e.stuck == 1:
						self.explosions.remove(e)

## score
				score = (self.actor.counter["enemykill"]*10 +
						self.actor.counter["boxkill"]*2 +
						self.actor.counter["cash"]*50+
						self.actor.counter["drop"] * 5
						)
				score = "%08d"%score
				scoreSrf = self.gameFont.render(str(score),1,(0,0,0))
				self.window.blit(scoreSrf,(SCREENWIDTH-max(80,scoreSrf.get_rect().width),2))
## healt bar
				self.actor.health  = min(100,self.actor.health ) # cap health
				health = self.actor.health * 1.5
				color = (0,255,0)
				if self.actor.health <= 35:
					color = (255,0,0)
				elif self.actor.health <= 60:
					color = (255,204,0)

				pygame.draw.rect(self.window,color,pygame.Rect(SCREENWIDTH-int(health)-2,scoreSrf.get_rect().height,int(health),20))
				pygame.draw.rect(self.window,(0,0,0),pygame.Rect(SCREENWIDTH-152,scoreSrf.get_rect().height,150,20),3)
				self.window.blit(data.loadImage("health_jump_0.png"),(SCREENWIDTH-180,scoreSrf.get_rect().height-12))

## weapon reset bar
				if self.actor.weaponRecieved > 0:
					maxWidth = 150
					width = ( (nowtime - self.actor.weaponRecieved) / float(self.actor.weaponReset) )
					width = (1-width) * maxWidth
					pygame.draw.rect(self.window,(0,0,0),pygame.Rect(SCREENWIDTH-maxWidth-2,scoreSrf.get_rect().height+25,maxWidth,20),3)
					pygame.draw.rect(self.window,(50,50,50),pygame.Rect(SCREENWIDTH-width-2,scoreSrf.get_rect().height+25,width,20),0)
					image = "defaultweapon_pause_0.png"
					if self.actor.weapon == "spread":
						image = "spreadweapon_pause_0.png"
					self.window.blit(data.loadImage(image),(SCREENWIDTH-maxWidth-32,scoreSrf.get_rect().height+20))

## check for death
				if self.actor.position.y >= SCREENHEIGHT+100:
					self.actor.health = 0
				# check for death condition
				if self.actor.health <= 0:
					gameoverSrf = data.loadImage("gameover.png")
					grect = gameoverSrf.get_rect()
					self.window.blit(gameoverSrf,((SCREENWIDTH/2.0)-(grect.width/2.0),SCREENHEIGHT/2.0 - (grect.height/2.0)))

## check for win
				else:
					if self.lastLevel == 1 and ( len( [e for e in self.enemies if e.stuck == 0]) <= 0):
						if len(self.tutorialMaps) <= self.tutorialMap+1:
							gameoverSrf = data.loadImage("tutorialcomplete.png")
						else:
							gameoverSrf = data.loadImage("levelcomplete.png")
						grect = gameoverSrf.get_rect()
						self.window.blit(gameoverSrf,((SCREENWIDTH/2.0)-(grect.width/2.0),SCREENHEIGHT/2.0 - (grect.height/2.0)))
						self.mapComplete = 1

## draw tut info 
				if self.tutorialMap >= 0 and self.tutorialInfoShown == 0:					
						tutInfoSrf= data.loadImage(self.tutorialInfo[self.tutorialMap])
						grect = tutInfoSrf.get_rect()
						self.window.blit(tutInfoSrf,((SCREENWIDTH/2.0)-(grect.width/2.0),SCREENHEIGHT/2.0 - (grect.height/2.0)))



## draw menu if applicable
				if self.levelSelectMode == 1:
					self.drawLevelSelect("custom")
				elif self.inMenu == 1:
					self.drawMenu()

## CROSSHIAR
				self.window.blit(self.srfCrosshair,pygame.mouse.get_pos())

				pygame.display.flip()

				if len(self.bullets) > 300:
					self.bullets = self.bullets[-(len(self.bullets)-100):]
					#print "capped bullet count"




#--- drop and shrinkage

	def shrinkBottom(self,timeElapsed):
		"""
		cut the lower part of the screen and let it shrink
		should look like falling into the screen
		"""
		if self.dropWidth <= 100:
			self.dropWidth = SCREENWIDTH
			self.dropSpeed = self.initialDropSpeed
			self.bottomKillLevel()
			self.ydiff -= self.dropHeight

			if self.endlessMode:
				self.topCreateLevel()
			else:
				self.loadNewLevel(self.ydiff, (self.ydiff + self.dropHeight))
			self.mixer.play("drop.wav")
			self.state = "DROP"
			return 1
		dropHeight= int(self.dropHeight) # part of orig screen we are shrking
		self.dropWidth -= int( (self.dropSpeed*timeElapsed) )# width after shrink
		self.dropSpeed *= 1.01
		newDropWidth  = self.dropWidth
		newDropHeight = int(0.9* (newDropWidth/float(SCREENWIDTH)) * dropHeight )# height after shrink
		blackSurface = pygame.Surface((SCREENWIDTH,dropHeight)) # black for screen overdraw
		origDropTopLeft = (0,SCREENHEIGHT-dropHeight) # pos of drop area in orig screen
		temp= pygame.Surface((SCREENWIDTH,dropHeight)) # shrinkable surface
		temp.blit(self.window,(0,0),pygame.Rect((0,SCREENHEIGHT-dropHeight,SCREENWIDTH,dropHeight)))
		temp = pygame.transform.scale(temp,(newDropWidth,newDropHeight))

		self.window.blit(blackSurface,origDropTopLeft)
		newDropTopLeft = ( origDropTopLeft[0] + (SCREENWIDTH - newDropWidth)/2.0,
							origDropTopLeft[1] + (dropHeight - newDropHeight) / 2.0)
		self.window.blit(temp,newDropTopLeft)
		self.lastShrinkSurface = self.backgroundSrf.copy()
		self.lastShrinkSurface.blit(blackSurface,(0,origDropTopLeft[1]))
		self.lastShrinkSurface.blit(temp,newDropTopLeft)
		# draw wall lines
		lines = []
		linecolor = (120,120,120)
		#lines.append( ( newDropTopLeft,(newDropTopLeft[0]+newDropWidth,newDropTopLeft[1]+newDropHeight) ) )
		lines.append( ( (0,SCREENHEIGHT),(newDropTopLeft[0],newDropTopLeft[1]+newDropHeight) ) )
		lines.append(
					  ( (SCREENWIDTH,SCREENHEIGHT),(newDropTopLeft[0]+newDropWidth,newDropTopLeft[1]+newDropHeight))
					)

		lines.append( ( origDropTopLeft,(newDropTopLeft) ) )
		lines.append(
					  ( (SCREENWIDTH,origDropTopLeft[1]),(newDropTopLeft[0]+newDropWidth,newDropTopLeft[1]))
					)

		aathick = 10
		thick = max(1, int(5 * (self.dropWidth/800.0)) )
		for a,b in lines:
			pygame.draw.aaline(self.lastShrinkSurface,linecolor ,a,b,aathick)
			pygame.draw.aaline(self.lastShrinkSurface,linecolor ,a,b,aathick)
			pygame.draw.aaline(self.window,linecolor ,a,b,aathick)
			pygame.draw.aaline(self.window,linecolor ,a,b,aathick)

		pygame.draw.rect(self.window,linecolor,pygame.Rect(newDropTopLeft,(newDropWidth,newDropHeight)),thick)
		pygame.draw.rect(self.lastShrinkSurface,linecolor,pygame.Rect(newDropTopLeft,(newDropWidth,newDropHeight)),thick)

		return 1

	def bottomKillLevel(self):
		"""
		kill off all objects that where in the falling part at the bottom
		"""
		dropoff = SCREENHEIGHT - self.dropHeight
##		print "killing after "+str(dropoff)
		objectlists = {"obstacle":self.obstacles,
						"box":self.boxes,
						"enemy":self.enemies,
						"bullet":self.bullets,
						"explosion":self.explosions}

		for oname,olist in objectlists.items():
			newlist = []
			for o in olist:
				if o.position.y <= dropoff:
					newlist.append(o)
			if oname == "obstacle":
				self.obstacles = newlist
			elif oname == "box":
				self.boxes = newlist
			elif oname == "enemy":
				self.enemies = newlist
			elif oname == "bullet":
				self.bullets = newlist
			elif oname == "explosion":
				self.explosions = newlist


		# kill actor
		if self.actor.position.y >= dropoff:
			self.actor.health = 0
		return 1


	def topCreateLevel(self):
		"""
		create new objects over screen
		"""
		if self.dropHeight < 50:
##			print "didnt create new level.. not enogh space"
			return 1
		(enemies,obstacles,boxes) = self.createNewLevel( (0-self.dropHeight,-50))
		self.obstacles += obstacles
		self.enemies += enemies
		self.boxes += boxes
##		print "created new level"
		return 1


	def dropDown(self,timeElapsed):

		"""
		move ALL OBJECTS down
		"""

		if self.fallHeight < self.dropHeight:
			fallamount = 30* timeElapsed
			if self.fallHeight + fallamount > self.dropHeight:
				fallamount = self.dropHeight - self.fallHeight
			self.fallHeight += fallamount
		else:
##			print "finished droppping"
			self.fallHeight = 0
			self.state = "WAIT"
			self.calcDropHeight()
			self.stateWaitStart = time.time()
			return 1

		objectlists = {"obstacle":self.obstacles,
						"box":self.boxes,
						"enemy":self.enemies,
						"bullet":self.bullets,
						"explosion":self.explosions
						}
		for oname,olist in objectlists.items():
			for o in olist:
				o.position[1] += fallamount
				if oname == "obstacle":
					o.recalcRect()
				elif oname == "box":
					o.rect = None
					o.getRect()

		# extra code to drop the actor
		self.actor.position[1] += fallamount
		if self.actor.ropeHeadPosition is not None:
			self.actor.ropeHeadPosition[1] += fallamount

		# print black area
		blackheight = self.dropHeight - self.fallHeight
		self.window.set_clip(pygame.Rect(0,SCREENHEIGHT-blackheight,SCREENWIDTH,blackheight))
		self.window.blit(self.lastShrinkSurface,(0,0))
		self.window.set_clip()
##		blackheight = self.dropHeight - self.fallHeight
##		blackSurface = pygame.Surface((SCREENWIDTH,blackheight)) # black for screen overdraw
##		self.window.blit( blackSurface, (0,SCREENHEIGHT-blackheight))

		# todo: print white lines - ie copy surface from shrink


#--- helpers

	def loadNewLevel(self,miny,maxy):
		if not self.loadedObjects:
			self.loadedObjects = pickle.load(data.load(self.levelName))
		self.lastLevel = 1
		for oname,olist in self.loadedObjects.items():
			for o in olist:
				if (miny == -1 and maxy == -1) or (o.position.y >= miny and o.position.y <= maxy):
					# insert new object
					if oname == "box":
						o.animator.update()
						self.boxes.append(o)
					elif oname == "enemy":
						o.animator.update()
						self.enemies.append(o)
					elif oname == "obstacle":
						self.obstacles.append(o)
				if o.position.y <= miny:
					self.lastLevel = 0


	def createNewLevel(self,yinterval):
		(miny,maxy) = yinterval
##		print "new level for "+str(yinterval)
		y = randint(int(miny),int(maxy))
		levelMaxWidth = 800

		obstDone = 0
		obstMin = 80 # min width obstacle
		obstMax = 200 # max width
		obstHeight = 11 # obst height
		spaceMin = 30 # space between 2 obstacles min
		spaceMax = 200 # space between 2 obstacles max
		newObstacles = []
		cx = 0
		# create obstacles at one y pos
		while obstDone == 0:
			cx += randint(spaceMin,spaceMax)
			w = randint(min(obstMin,abs(levelMaxWidth-cx)),min(abs(levelMaxWidth-cx),obstMax))
			newObstacles.append( gameobjects.Obstacle( cx,y,w, obstHeight))
			cx += w
			if cx + obstMax + 5 >= levelMaxWidth:
				obstDone = 1

		# create enemies and boxes on the obstacles
		minEnemySpace = obstMin-10 # min pixels an enemy needs on an obstacle
		minBoxSpace = obstMin-30	# min pixels a box needs per obstacle
		minHealthBoxSpace = obstMin
		newEnemies = []
		newBoxes = []
		for ob in newObstacles:
			cx = ob.position.x
			# enemies
			for i in range(randint(0,round(ob.w/minEnemySpace))):
				cx += randint(0,min(minEnemySpace,(ob.position.x+ob.w-cx)))
				# sometimes add devil
				randDevil = 5
				randRobot = 8
				if self.difficulty == 2:
					randDevil = 2
					randRobot = 5
				elif self.difficulty == 0.5:
					randDevil = 15
					randRobot = 8
				if randint(0,randDevil) == 1:
					newEnemies.append( gameobjects.DevilEnemy(Vector(cx,y-gameobjects.DevilEnemy.height),ob))
				if randint(0,randRobot) == 1:
					newEnemies.append( gameobjects.RobotEnemy(Vector(cx,y+11),ob))
				newEnemies.append( gameobjects.Enemy(Vector(cx,y-gameobjects.Enemy.height),ob))
			offsetitems = 10
			# boxes
			for i in range(randint(0,round(ob.w/minBoxSpace))):
				cx = randint(ob.position.x+offsetitems,ob.position.x+ob.w-offsetitems)
				type = randint(0,2)
				if type == 0:
					newBoxes.append( gameobjects.Box(Vector(cx,y-gameobjects.Box.height-1),ob))
				elif type == 1:
					newBoxes.append( gameobjects.MetalBarrel(Vector(cx,y-gameobjects.Box.height-1),ob))
				else:
					newBoxes.append( gameobjects.WoodBarrel(Vector(cx,y-gameobjects.Box.height-1),ob))
			# healthboxes
			if randint(0,5) == 5:
				cx = randint(ob.position.x+offsetitems,ob.position.x+ob.w-offsetitems)
				newBoxes.append( gameobjects.HealthBox(Vector(cx,y-gameobjects.HealthBox.height-1),ob))
			# cash boxes
			if randint(0,8) == 8:
				cx = randint(ob.position.x+offsetitems,ob.position.x+ob.w-offsetitems)
				newBoxes.append( gameobjects.CashBox(Vector(cx,y-gameobjects.CashBox.height-1),ob))

			# spread boxes
			if randint(0,20) == 1:
				cx = randint(ob.position.x+offsetitems,ob.position.x+ob.w-offsetitems)
				newBoxes.append( gameobjects.SpreadWeaponBox(Vector(cx,y-gameobjects.SpreadWeaponBox.height-1),ob))
			# fast wewapon
			if randint(0,10) == 1:
				cx = randint(ob.position.x+offsetitems,ob.position.x+ob.w-offsetitems)
				newBoxes.append( gameobjects.FastWeaponBox(Vector(cx,y-gameobjects.FastWeaponBox.height-1),ob))







		return (newEnemies,newObstacles,newBoxes)

	def calcDropHeight(self):
		"""
		stor dropHeight for later use
		"""
		lowest = None
		for o in self.obstacles:
			if lowest is None or (o.position.y > lowest.position.y):
##				print "lowest is "+str(o.position.y)
				lowest = o
		self.dropHeight = int(SCREENHEIGHT - lowest.position.y + 50)


	def handleKbdMouse(self):
		"""
		handle keyboard and mouse events
		this includes creating nets in the self.nets list when necessary
		## see http://www.pygame.org/docs/ref/event.html
		"""
		for event in pygame.event.get():
			if event.type == QUIT: # user closed the window
				self.running = 0 # stop game loop
			elif event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					#self.running = 0 # stop game loop
					self.inMenu = 1
				elif event.key in [K_SPACE,K_RCTRL]:
					self.actor.dropRopeRequest()
				elif event.key == K_RETURN:
					if self.mapComplete == 1 and (self.endlessMode == 0) and len(self.tutorialMaps) > self.tutorialMap+1:
						self.tutorialMap += 1
						self.tutorialInfoShown = 0
						self.levelName = self.tutorialMaps[self.tutorialMap]
					else:
						self.tutorialInfoShown = 1
					self.startUp()
				elif event.key in (K_w,K_a,K_s,K_d,K_DOWN,K_RIGHT,K_LEFT,K_UP):
					self.actor.keyDown(event.key)
			elif event.type == KEYUP:
				if event.key in (K_w,K_a,K_s,K_d,K_DOWN,K_RIGHT,K_LEFT,K_UP):
					self.actor.keyUp(event.key)
			elif event.type == MOUSEBUTTONDOWN:
				if event.button == 1:
					self.actor.shooting = 1
			elif event.type == MOUSEBUTTONUP:
				# but3 == shoot the rope
				if event.button == 3:
					self.actor.shootRopeRequest(event.pos)
				elif event.button == 1:
					self.actor.shooting = 0


#--- level select

	def drawLevelSelect(self,prefix):
		self.window.blit(data.loadImage("levelselect.png"),(0,0))
		levels = data.getLevels(prefix)
		# loop through levels, one rect per level
		offsetX = SCREENWIDTH/2.0 - 200
		offsetY = 115
		cY = offsetY
		lvlRects = {}
		# cap max levels to 20
		levels = levels[:10]
		for l in levels:
			name = l[:-4][len(prefix):]
			lvlSrf = self.gameFontSmall.render(name,1,(0,0,0))
			lvlRects[l] = lvlSrf.get_rect()
			lvlRects[l].x = offsetX
			lvlRects[l].y = cY
			pygame.draw.rect( self.window,(62,159,53),
			pygame.Rect(lvlRects[l].x-10,lvlRects[l].y-2,400,lvlRects[l].height+5)
			,0)
			self.window.blit(lvlSrf,(offsetX,cY))
			cY += lvlSrf.get_rect().height + 6

		self.handleKbdMouseLevelSelect(lvlRects)
		self.window.blit(self.srfCrosshair,pygame.mouse.get_pos())
		pygame.display.flip()



	def handleKbdMouseLevelSelect(self,lvlRects):
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.levelSelectMode = 0
					self.editorMode = 0
					self.inMenu = 1 # stop game loop
			if event.type == MOUSEBUTTONUP and event.button == 1:
				nohit = 1
				for lname,lrect in lvlRects.items():
					if lrect.collidepoint( event.pos[0],event.pos[1]):
						nohit = 0
						self.levelName = lname
						self.levelSelectMode = 0
						self.startUp()
						if self.editorMode == 1:
							self.initEditor()

					if nohit == 0:
						self.mixer.play("gun.wav")


#--- menu

	def handleKbdMouseMenu(self):
		start = pygame.Rect(36,14,365,125)
		endless = pygame.Rect(481,4,270,135)
		exit = pygame.Rect(454,461,300,115)

		diff3 = pygame.Rect(565,191,28,28)
		diff2 = pygame.Rect(565,226,28,28)
		diff1 = pygame.Rect(565,257,28,28)

		soundSwitch= pygame.Rect(565,303,28,28)
		musicSwitch= pygame.Rect(565,348,28,28)
		fullscreenSwitch= pygame.Rect(565,389,28,28)

		custStart = pygame.Rect(56,294,130,70)
		custEdit = pygame.Rect(200,299,150,70)
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if event.key == K_ESCAPE:
					self.inMenu = 0 # stop game loop
			if event.type == MOUSEBUTTONUP and event.button == 1:
				nohit = 0
				if start.collidepoint(event.pos[0],event.pos[1]):
					self.endlessMode = 0
					self.inMenu = 0
					self.editorMode = 0
					self.tutorialMap = 0
					self.tutorialInfoShown = 0
					self.levelName = self.tutorialMaps[self.tutorialMap]
					self.startUp()
				elif exit.collidepoint(event.pos[0],event.pos[1]):
					self.running = 0
				elif soundSwitch.collidepoint(event.pos[0],event.pos[1]):
					if self.mixer.sound == "on":
						self.mixer.sound = "off"
					else:
						self.mixer.sound = "on"
				elif fullscreenSwitch.collidepoint(event.pos[0],event.pos[1]):
					if self.fullscreen == 0:
						self.fullscreen = 1
						self.window = pygame.display.set_mode( (SCREENWIDTH,SCREENHEIGHT),pygame.FULLSCREEN )
					else:
						self.fullscreen = 0
						self.window = pygame.display.set_mode( (SCREENWIDTH,SCREENHEIGHT))
				elif diff3.collidepoint(event.pos[0],event.pos[1]):
					self.difficulty = 2
				elif diff2.collidepoint(event.pos[0],event.pos[1]):
					self.difficulty = 1
				elif diff1.collidepoint(event.pos[0],event.pos[1]):
					self.difficulty = 0.5
				elif endless.collidepoint(event.pos[0],event.pos[1]):
					self.endlessMode = 1
					self.tutorialMap = -1
					self.editorMode = 0
					self.inMenu = 0
					self.startUp()
				elif custStart.collidepoint(event.pos[0],event.pos[1]):
					self.tutorialMap = -1
					self.levelSelectMode = 1
					self.editorMode = 0
					#self.levelName = "custom.lvl"
					self.inMenu = 0
					self.endlessMode = 0
				elif custEdit.collidepoint(event.pos[0],event.pos[1]):
					self.tutorialMap = -1
					self.editorMode = 1
					self.inMenu = 0
					self.endlessMode = 0
					#self.levelName = "custom.lvl"
					self.levelSelectMode = 1
				elif musicSwitch.collidepoint(event.pos[0],event.pos[1]):
					self.mixer.toggleMusic()
				else:
					nohit = 1
				if nohit == 0:
					self.mixer.play("gun.wav")

	def drawMenu(self):
		self.window.blit(data.loadImage("menu.png"),(0,0))
		checkSrf= data.loadImage("checked.png")
		# draw checkboxes
		if self.mixer.sound == "on":
			self.window.blit(checkSrf,(565,303))
		if self.mixer.music == "on":
			self.window.blit(checkSrf,(565,348))

		if self.fullscreen == 1:
			self.window.blit(checkSrf,(565,389))

		if self.difficulty == 0.5:
			self.window.blit(checkSrf,(565,257))
		elif self.difficulty == 1:
			self.window.blit(checkSrf,(565,226))
		else:
			self.window.blit(checkSrf,(565,191))
#--- editor

	def initEditor(self):
		self.editorItems = {"box":"box_hits0_0.png",
						"woodbarrel":"woodbarrel_hits0_0.png",
						"metalbarrel":"metalbarrel_hits0_0.png",

					"devil":"devil_pause_0.png",
					"enemy":"enemy_pause_0.png",
					"robot":"robot_pause_0.png",

					"cash":"cash_pause_0.png",
					"health":"health_jump_0.png",

					"spreadweapon":"spreadweapon_pause_0.png",
					"fastweapon":"defaultweapon_pause_0.png",

					"obstacle":"editor_obstacle.png",
					"eraser":"editor_eraser.png"
					}

		self.brushType = "eraser" # current brush type
		self.brushRect = None # where's the brush at, sync with mousepos
		self.itemRects = {} # rects for selectable editor items
		self.ydiff = 0 # how far did we move down

		self.obstacleStartPos = None # start pos of obst currently being drawn

		self.objectlists= {"obstacle":self.obstacles,"enemy":self.enemies,"box":self.boxes}

		self.inputTextMode = 0
		self.newLevelName = self.levelName[len("custom"):][:-4]
		self.showSave = 0


	def editorLoop(self,timeElapsed):
		"""
		we do a lot of init here
		this is basically the gameLoop() without updates
		and a different kbdMousehandler
		"""
		for oname, objlist in self.objectlists.items():
			for o in objlist:
				o.draw(self.window)

		# draw editor items
		cx = 5
		for a,pic in self.editorItems.items() + [("help","editor_help.png"),("save","editor_save.png")]:
			srfPic = data.loadImage(pic)
			if a == "help":
				cx = SCREENWIDTH - 50
			elif a == "save":
				cx = SCREENWIDTH - 100
			self.itemRects[a] = pygame.Rect(cx,SCREENHEIGHT-40,
											srfPic.get_rect().width,srfPic.get_rect().height)
			pygame.draw.rect(self.window,(255,255,153),self.itemRects[a],0)
			self.window.blit(srfPic,(cx,SCREENHEIGHT-40))
			cx += srfPic.get_rect().width+5

		# draw surrounding rect for items
		#pygame.draw.rect(self.window,(0,0,0),pygame.Rect(5,SCREENHEIGHT-40,cx,40),3)

		# draw droplines
		for l in self.dropLines:
			pygame.draw.line(self.window,(255,210,0),(0,l),(SCREENWIDTH,l),1)

		# draw unfinished obstacles if any
		if self.obstacleStartPos is not None:
			mousepos = pygame.mouse.get_pos()
			width = mousepos[0] - self.obstacleStartPos.x
			if width >= 0:
				newObstacle = gameobjects.Obstacle(self.obstacleStartPos[0],self.obstacleStartPos[1],width,11)
				newObstacle.draw(self.window)

		# show save info
		if self.showSave >= 0:
			self.showSave -= timeElapsed
			srfSave = self.gameFont.render(self.newLevelName+" saved",1,(0,0,0))
			self.window.blit(srfSave,srfSave.get_rect())

		if self.inMenu == 0:
			self.handleKbdMouseEditor()
		else:
			self.drawMenu()
			self.handleKbdMouseMenu()

		# show save input text line
		if self.inputTextMode == 1:
			srfSaveInput = self.gameFont.render("Enter Level Name: "+str(self.newLevelName),1,(0,0,0))
			srfSaveHelp = self.gameFontSmall.render("Escape cancels // Enter saves",1,(0,0,0))
			inputRect = srfSaveInput.get_rect()
			self.window.blit(srfSaveInput,inputRect)
			self.window.blit(srfSaveHelp,(inputRect.x,inputRect.y+inputRect.height+3))


		# draw mouse cursor of type brushType
		if self.brushType == "help":
			self.window.blit(data.loadImage("bighelp.png"),(0,0))
		elif self.brushType == "save":
			self.inputTextMode = 1
		else:
			cursorImage = data.loadImage(self.editorItems[self.brushType])
			(mx,my) = pygame.mouse.get_pos()
			self.brushRect = pygame.Rect( mx-cursorImage.get_rect().width/2.0,my-cursorImage.get_rect().height/2.0,
										cursorImage.get_rect().width,cursorImage.get_rect().height)
			self.window.blit(cursorImage,self.brushRect)


		pygame.display.flip()


	def handleKbdMouseEditor(self):
		okaychars = ["a","b","c","d","e","f","g","h","i","j","k","l",
					"m","n","o","p","q","r","s","t","u","v","w","x","y","z",
					"0","1","2","3","4","5","6","7","8","9","-","_","."]
		mousepos = pygame.mouse.get_pos() # need @ serveral places
		for event in pygame.event.get():
			if event.type == KEYDOWN:
				if self.inputTextMode == 1:
					if event.unicode in okaychars:
						self.newLevelName += event.unicode
					elif event.key == K_BACKSPACE:
						self.newLevelName = self.newLevelName[:-1]
					elif event.key == K_RETURN:
						self.inputTextMode = 0
						self.brushType = "eraser"
						self.showSave = 5
						self.saveLevel("custom"+self.newLevelName+".lvl")
					elif event.key == K_ESCAPE:
						self.inputTextMode = 0
						self.brushType = "eraser"
				else:
					if event.key == K_ESCAPE:
						if self.brushType == "help":
							self.brushType = "eraser"
						else:
							self.inMenu = 1
					elif event.key == K_UP:
						self.editorMoveScreen(+70)
					elif event.key == K_DOWN:
						self.editorMoveScreen(-70)

					elif event.key == K_F5:
						self.inputTextMode = 1
			elif event.type == MOUSEBUTTONDOWN and event.button == 1:
				if self.brushType == "obstacle":
					self.obstacleStartPos = Vector(mousepos[0],mousepos[1])
			elif event.type == MOUSEBUTTONDOWN and event.button == 3:
				self.obstacleStartPos = None

			elif event.type == MOUSEBUTTONUP and event.button == 1:
				# change brush type?
				for brushType, rect in self.itemRects.items():
					if self.brushType in ["help","save"]:
						continue
					if rect.collidepoint(event.pos[0],event.pos[1]):
						self.brushType = brushType
						self.obstacleStartPos = None
## DONE HERE if brush was set
						return
				# check for coll with stuff on screen
				if self.brushType == "eraser":
					for oname,objlist in self.objectlists.items():
						for o in objlist:
							if self.brushRect.colliderect(o.getRect()):
								objlist.remove(o)
								if oname == "obstacle":
									self.calcDropLines()
								break
				elif self.brushType == "obstacle":
					# finished drawing obstacle
					width = mousepos[0] - self.obstacleStartPos.x
					if width <= 0:
						print "please draw obstacles from left to right"
						return
					newObstacle = gameobjects.Obstacle(self.obstacleStartPos[0],self.obstacleStartPos[1],width,11)
					self.obstacles.append(newObstacle)
					self.obstacleStartPos = None
					# recalc drop lines
					self.calcDropLines()
				elif self.brushType in ["enemy","devil","robot"]:
					# first we set the enemy
					# then we check wether he collides with obstacle
					# this is necessary!
					# then we adjust its x position according to obstacle
					newEnemy = None
					if self.brushType == "enemy":
						newEnemy = gameobjects.Enemy(Vector(mousepos[0],mousepos[1]),None)
					elif self.brushType == "devil":
						newEnemy = gameobjects.DevilEnemy(Vector(mousepos[0],mousepos[1]),None)
					else:
						newEnemy = gameobjects.RobotEnemy(Vector(mousepos[0],mousepos[1]),None)
					# get obstacle
					onObstacle = None
					for o in self.obstacles:
						if o.getRect().colliderect( newEnemy.getRect() ):
							onObstacle = o
							break
					if not onObstacle:
						print "enemy doesnt collide with rect.. dont know where to put it"
					else:
						newEnemy.obstacle = onObstacle
						newEnemy.position.y = onObstacle.position.y - newEnemy.height
						if self.brushType == "robot":
							newEnemy.position.y +=  onObstacle.h + newEnemy.height
						self.enemies.append(newEnemy)

				elif self.brushType in ["box","metalbarrel","woodbarrel","health","cash","spreadweapon","fastweapon"]:
					# try to put them on obstacles
					# it this doenst work => simply drop them on mousepos
					newBox = None
					posVec = Vector(self.brushRect.x,self.brushRect.y)
					if self.brushType == "health":
						newBox = gameobjects.HealthBox(posVec)
					elif self.brushType == "cash":
						newBox = gameobjects.CashBox(posVec)
					elif self.brushType == "spreadweapon":
						newBox = gameobjects.SpreadWeaponBox(posVec)
					elif self.brushType == "fastweapon":
						newBox = gameobjects.FastWeaponBox(posVec)
					elif self.brushType == "box":
						newBox = gameobjects.Box(posVec)
					elif self.brushType == "metalbarrel":
						newBox = gameobjects.MetalBarrel(posVec)
					elif self.brushType == "woodbarrel":
						newBox = gameobjects.WoodBarrel(posVec)

					# get obstacle if any
					onObstacle = None
					for o in self.obstacles:
						if o.getRect().colliderect( newBox.getRect() ):
							onObstacle = o
							break
					if onObstacle:
						newBox.position.y = onObstacle.position.y - newBox.width
						newBox.obstacle = onObstacle
					self.boxes.append( newBox)



	def calcDropLines(self):

##		lowest = None
##		for o in self.obstacles:
##			if lowest is None or (o.position.y > lowest.position.y):
##				print "lowest is "+str(o.position.y)
##				lowest = o
##		self.dropHeight = int(SCREENHEIGHT - lowest.position.y + 50)
		self.dropLines = []
		self.obstacles.sort(sortObstaclesByY)
		self.obstacles.reverse()
		cDropLine = 800 - self.ydiff
		for o in self.obstacles:
			# this obstacle will fall witht he last one
			if o.position.y >= cDropLine:
				continue
			cDropLine = o.position.y - 50
			self.dropLines.append( cDropLine)
		#print self.dropLines
		return

		self.obstacles.sort(sortObstaclesByY)
		self.obstacles.reverse()
		currDropLine = 800 + self.ydiff
		dropList = []
		nextScreenBorder = 0
		for o in self.obstacles:
			#print o.position.y
			if len(dropList) == 0:
				dropHeight = SCREENHEIGHT - o.position.y + 50
				currDropLine = SCREENHEIGHT - dropHeight
				dropList.append( currDropLine )
				nextScreenBorder = currDropLine - 800
				#print "nsb "+str(nextScreenBorder)
			if o.position.y <= nextScreenBorder:
				dropHeight = abs(o.position.y) - abs(nextScreenBorder)
				currDropLine = nextScreenBorder - dropHeight
				dropList.append( currDropLine )
				nextScreenBorder = currDropLine - 800
			else:
				# being dropped
				continue
		#print dropList
		self.dropLines = dropList


	def saveLevel(self,lvlname):
		# move screen back to get correct y
		origdiff = self.ydiff
		self.editorMoveScreen(-self.ydiff)
		# del all surfaces
		for oname,objlist in self.objectlists.items():
			for o in objlist:
				if oname != "obstacle":
					o.animator.image = None

		pickle.dump(self.objectlists,data.newSaveFile(lvlname))
		self.editorMoveScreen(origdiff)
		# create all surfaces
		for oname,objlist in self.objectlists.items():
			for o in objlist:
				if oname != "obstacle":
					o.animator.update()



	def editorMoveScreen(self,ydiff):
		self.ydiff += ydiff
		for oname,objlist in self.objectlists.items():
			for o in objlist:
				o.position.y += ydiff
				if oname == "obstacle":
					o.recalcRect()
				elif oname == "box":
					o.rect = None
					o.getRect()
		# move drop lines
		newDropLines= []
		for l in self.dropLines:
			newDropLines.append( l + ydiff)
		self.dropLines = newDropLines





if __name__ == "__main__":
    main()
