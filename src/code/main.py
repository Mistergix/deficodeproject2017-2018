import pygame as pg
import os
from sprites import *
import animation as ani
from settings import Settings
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((Settings.WIDTH, Settings.HEIGHT)) # Crée un écran pygame de taille Settings.WIDTH x Settings.HEIGHT
        pg.display.set_caption(Settings.TITLE) # Donner Settings.TITLE en tire à la fenêtre
        self.clock = pg.time.Clock() # Un objet de type Clock
        self.running = True # Le jeu doit tourner
        self.bgcolor = Settings.BLACK # Black
        self.LoadData()

    def LoadData(self):
        self.dir = os.path.dirname(__file__)
        data_dir = os.path.join(self.dir, 'data')
        self.spritesheet = ani.Spritesheet(os.path.join(data_dir, Settings.SPRITESHEET))

    def Launch(self):
        self.all_sprites = pg.sprite.Group() # Une liste de sprites
        self.ennemies = pg.sprite.Group() # Une autre

        player1_stand = [ani.Frame((614, 1063, 120, 191))]
        player2_stand = [ani.Frame((581, 1265, 121, 191))]

        player1_animation = ani.Animation(self.spritesheet, player1_stand)
        player2_animation = ani.Animation(self.spritesheet, player2_stand)

        player1_animator = ani.Animator(player1_animation)
        player2_animator = ani.Animator(player2_animation)

        self.player1 = Player1(player1_animator)
        self.player2 = Player2(player2_animator)

        self.all_sprites.add(self.player1)
        self.all_sprites.add(self.player2)

        for i in range(10):
            ennemi_stand = [ani.Frame((568, 1671, 122, 139))]
            ennemi_animation = ani.Animation(self.spritesheet, ennemi_stand)
            ennemi_animator = ani.Animator(ennemi_animation)
            ennemi = Ennemi(ennemi_animator, 50, 10, 10, self.player1)
            self.all_sprites.add(ennemi)
            self.ennemies.add(ennemi)

        self.Run()

    def Run(self):
        while self.running:
            self.clock.tick(Settings.FPS)
            self.Events()
            self.Update()
            self.Draw()

    def Events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.running = False

    def Update(self):
        self.all_sprites.update()

    def Draw(self):
        self.screen.fill(self.bgcolor)
        self.all_sprites.draw(self.screen)
        #######
        pg.display.flip()

        
g = Game()
g.Launch()
pg.quit()
