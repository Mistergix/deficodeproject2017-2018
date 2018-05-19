"""
simono

utility stuff, math

"""

import math
import pygame

def _is_numeric(obj):
	if isinstance(obj, (int, long, float)):
		return True
	else:
		return False


class Borg:
	_state = {}
	def __init__(self):
		self.__dict__ = self._state





class Vector(object):
	"""
	Basic 2D Vector class (originally from http://gflanagan.net/site/python/sci/2dvector.html, adapted)
	"""
	def __init__(self, a, b=None):
		if b == None:
			#assume tuple of 2 vectors
			self.x=a[0]
			self.y=a[1]
		elif _is_numeric(a):
			#assume two numbers
			self.x = a
			self.y = b
		else:
			#assume Vectors/tuples
			self.x = b[0] - a[0]
			self.y = b[1] - a[1]


	def __getitem__(self, index):
		if index == 0:
			return self.x
		elif index == 1:
			return self.y
		else:
			raise IndexError

	def __setitem__(self, index,value):
		if index == 0:
			self.x=value
		elif index == 1:
			self.y=value
		else:
			raise IndexError

	def __len__(self):
		return 2

	def __add__(self, other):
		return Vector(self.x + other.x, self.y + other.y)

	def __sub__(self, other):
		return Vector(self.x - other.x, self.y - other.y)

	def __mul__(self, other):
		try:
			other = other - 0
		except:
			raise TypeError, "Only scalar multiplication is supported."
		return Vector( other * self.x, other * self.y )

	def __rmul__(self, other):
		return self.__mul__(other)

	def __div__(self, other):
		return Vector( self.x / other, self.y / other )

	def __neg__(self):
		return Vector(-self.x, -self.y)

	def __abs__(self):
		return self.length()

	def __repr__(self):
		return '(%s, %s)' % (self.x, self.y)

	def __str__(self):
		return '(%s, %s)' % (self.x, self.y)

	def dot(self, vector):
		return self.x * vector.x + self.y * vector.y

	def cross(self, vector):
		return self.x * vector.y - self.y * vector.x

	def length(self):
		return math.sqrt( self.dot(self) )

	def perpindicular(self):
		return Vector(-self.y, self.x)

	def unit(self):
		return self / self.length()

	def projection(self, vector):
		k = (self.dot(vector)) / vector.length()
		return k * vector.unit()

	def angle(self, vector=None):
		if vector == None:
			vector = Vector(1,0)
		#print (self,vector)
		return math.acos((self.dot(vector))/(self.length() * vector.length()))

	def angle_in_degrees(self, vector=None):
		return (self.angle(vector) * 180) /math.pi

	def rotate(self, phi):
		return Vector(self.x*math.cos(phi)-self.y*math.sin(phi),self.y*math.cos(phi)+self.x*math.sin(phi))
