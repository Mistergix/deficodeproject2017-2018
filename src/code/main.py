import pygame as pg
from sprites import *
import animator as ani
from settings import Settings


class Game:
    def __init__(self):
        pg.init()
        self.screen = ... # Crée un écran pygame de taille Settings.WIDTH x Settings.HEIGHT
        ... # Donner Settings.TITLE en tire à la fenêtre
        self.clock = ... # Un objet de type Clock
        self.running = ... # Le jeu doit tourner
        self.LoadData()

    def LoadData(self):
        self.dir = os.path.dirname(__file__)
        data_dir = os.path.join(self.dir, 'data')
        self.spritesheet = ani.Spritesheet(os.path.join(data_dir, Settings.SPRITESHEET))

    def Launch(self):
        self.all_sprites = pg.sprite.Group() # Une liste de sprites
        self.ennemies = ... # Une autre

        
