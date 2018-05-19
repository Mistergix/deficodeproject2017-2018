'''Simple data loader module.

Loads data files from the "data" directory shipped with a game.

Enhancing this to handle caching etc. is left as an exercise for the reader.
'''
#stdlib
import os
import copy
#lib
import pygame
#custom

data_py = os.path.abspath(os.path.dirname(__file__))
data_dir = os.path.normpath(os.path.join(data_py, '..', 'data'))

def load(filename, mode='rb'):
    '''Open a file in the data directory.

    "mode" is passed as the second arg to open().
    '''
    return open(os.path.join(data_dir, filename), mode)

soundCache = {}
def loadSound(sound):
	if sound not in soundCache.keys():
		soundCache[sound] = pygame.mixer.Sound( os.path.join(data_dir,sound) )
	return soundCache[sound]


def loadMusic():
	return os.path.join(data_dir,"edge_track.ogg")

#--- image cache
imgCache = {}
def loadImage(pImage):
	if pImage not in imgCache.keys():
		imgCache[pImage] = pygame.image.load( os.path.join(data_dir,pImage) ).convert_alpha()
	return imgCache[pImage]


def newSaveFile(lvlname):
	return open(os.path.join(data_dir,str(lvlname)),"wb")


def getLevels(prefix="custom"):
	allData = os.listdir( data_dir)
	levelFiles = []
	for data in allData:
		if data[-4:] == ".lvl" and data[0:len(prefix)] == prefix:
			levelFiles.append(data)
	return levelFiles
