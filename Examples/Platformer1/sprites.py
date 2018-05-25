import pygame as pg

from settings import *
import animator as ani

vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, animator):
        pg.sprite.Sprite.__init__(self)
        self.image = animator.idle_image
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH//2, HEIGHT//2)
        self.pos = vec(WIDTH//2, HEIGHT//2)
        self.vel = vec(0,0)
        self.acc = vec(0,0)
        self.jumpHeight = -20

        # Animation 
        self.animator = animator
        self.walking = False
        self.jumping = False


    def update(self):
        self.animate()
        self.acc = vec(0,PLAYER_GRAV)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.acc.x = -PLAYER_ACC
        if keys[pg.K_RIGHT]:
            self.acc.x = PLAYER_ACC

        self.acc.x += self.vel.x * PLAYER_FRICTION

        self.vel += self.acc
        if abs(self.vel.x) < 0.1:
            self.vel.x = 0
        self.pos += self.vel + 0.5 * self.acc

        w = self.rect.width // 2
        if self.pos.x > WIDTH + w:
            self.pos.x = -w
        if self.pos.x < -w :
            self.pos.x = WIDTH + w


        self.rect.midbottom = self.pos

        

    def jump(self):
        self.vel.y = self.jumpHeight

    def animate(self):
        self.walking = (self.vel.x != 0)

        if self.walking:
            image = self.animator.get_current_image(ani.Animation.WALK)
            if self.vel.x < 0:
                image = pg.transform.flip(image, True, False)
        if not self.walking and not self.jumping:
            image = self.animator.get_current_image(ani.Animation.IDLE)
        
        self._update_image(image)

    def _update_image(self, image):
        self.image = image
        bottom = self.rect.bottom
        self.rect = self.image.get_rect()
        self.rect.bottom = bottom


class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.image = pg.Surface((w,h))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
