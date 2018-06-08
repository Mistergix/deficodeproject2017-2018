import pygame as pg
from pytmx.util_pygame import load_pygame
import pyscroll
import os
from sprites import *
import animation as ani
from settings import Settings
class Game:
    def __init__(self):
        pg.init()
        self.w, self.h = (Settings.WIDTH, Settings.HEIGHT)
        self.screen = pg.display.set_mode((self.w, self.h)) # Crée un écran pygame de taille Settings.WIDTH x Settings.HEIGHT
        pg.display.set_caption(Settings.TITLE) # Donner Settings.TITLE en tire à la fenêtre
        self.clock = pg.time.Clock() # Un objet de type Clock
        self.running = True # Le jeu doit tourner
        self.bgcolor = Settings.BLACK # Black
        self.g = 2 # gravity
        self.LoadData()
        

    def LoadData(self):
        self.dir = os.path.dirname(__file__)
        data_dir = os.path.join(self.dir, 'data')
        self.spritesheet = ani.Spritesheet(os.path.join(data_dir, Settings.SPRITESHEET))
        self.tmx_data = load_pygame(os.path.join(data_dir, 'map.tmx'))

    def Launch(self):
        map_data = pyscroll.TiledMapData(self.tmx_data)
        self.map_layer = pyscroll.BufferedRenderer(map_data, (self.w, self.h), clamp_camera=True)
        self.all_sprites = pyscroll.PyscrollGroup(map_layer=self.map_layer)
          
         # Une liste de sprites
        self.ennemies = pg.sprite.Group() # Une autre
        self.platforms = pg.sprite.Group()

        player1_stand = [ani.Frame((614, 1063, 120, 191))]
        player2_stand = [ani.Frame((581, 1265, 121, 191))]

        player1_animation = ani.Animation(self.spritesheet, player1_stand)
        player2_animation = ani.Animation(self.spritesheet, player2_stand)

        player1_animator = ani.Animator(player1_animation)
        player2_animator = ani.Animator(player2_animation)

        self.player1 = Player1(player1_animator)
        self.player2 = Player2(player2_animator)

        self.player1.position = self.map_layer.map_rect.center
        self.player2.position = self.player1.position

        self.all_sprites.add(self.player1)
        self.all_sprites.add(self.player2)

        collisions = self.tmx_data.get_layer_by_name("collision")
        for obj in collisions:
            box = ani.Box(None, obj.width, obj.height)
            box.rect.topleft = (obj.x, obj.y)
            self.platforms.add(box)
            self.all_sprites.add(box)
        
        

        """
        for i in range(10):
            ennemi_stand = [ani.Frame((568, 1671, 122, 139))]
            ennemi_animation = ani.Animation(self.spritesheet, ennemi_stand)
            ennemi_animator = ani.Animator(ennemi_animation)
            ennemi = Ennemi(ennemi_animator, 50, 10, 10, self.player1)
            ennemi.position = self.player1.position
            self.all_sprites.add(ennemi)
            self.ennemies.add(ennemi)"""
        self.selectedPlayer = self.player1
        self.Run()

    def Run(self):
        while self.running:
            dt = self.clock.tick(Settings.FPS)/1000
            self.Events()
            self.Update(dt)
            self.Draw()

    def Events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.running = False
            elif ev.type == pg.KEYDOWN :
                key = ev.key
                if key == pg.K_f :
                    self.SwitchPlayer()

    def Update(self,dt):
        self.all_sprites.update(dt, self.g)
        """
        A ameliorer
        """
        hits = pg.sprite.spritecollide(self.player1, self.platforms, False)
        if hits:
            self.player1.position.y = hits[0].rect.top
            self.player1.isOnGround = True
        else:
            self.player1.isOnGround = False
        hits = pg.sprite.spritecollide(self.player2, self.platforms, False)
        if hits:
            self.player2.position.y = hits[0].rect.top + 1
            self.player2.isOnGround = True
        else:
            self.player2.isOnGround = False

    def Draw(self):
        self.screen.fill(self.bgcolor)
        self.all_sprites.center(self.selectedPlayer.rect.center)
        self.all_sprites.draw(self.screen)
        #######
        pg.display.flip()

    def SwitchPlayer(self):
        if self.selectedPlayer == self.player1 :
            old = self.player1
            new = self.player2
        
        else :
            old = self.player2
            new = self.player1
        
        old.selected = False
        new.selected = True
        self.selectedPlayer = new

        
g = Game()
g.Launch()
pg.quit()
