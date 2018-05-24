import pygame as pg

from settings import *

vec = pg.math.Vector2

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.sheet = pg.image.load(filename).convert()

    def get_image(self, x, y, w, h):
        """
        Loads the image on the spritesheet, given its x, y coordinate and its width and height
        """
        image = pg.Surface((w,h))
        image.blit(self.sheet, (0,0), (x,y,w,h))
        image.set_colorkey(BLACK)
        image = pg.transform.scale(image, (w//2, h//2))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, image):
        pg.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.pos = vec(WIDTH//2, HEIGHT//2)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumpHeight = -20

    def update(self):
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION

        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0 :
            self.pos.x = WIDTH


        self.rect.midbottom = self.pos

    def jump(self):
        self.vel.y = self.jumpHeight
class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w,h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
