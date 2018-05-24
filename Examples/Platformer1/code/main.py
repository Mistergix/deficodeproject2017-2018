import pygame as pg
import random
from settings import *
from sprites import *

class Game:
    def __init__(self):
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True

    def _add_platform(self, x, y, w, h):
        p = Platform(x,y,w,h)
        self.all_sprites.add(p)
        self.platforms.add(p)
        return p

    def new(self):
        # CREATE THE SPRITES GROUPS
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        # CREATE THE PLAYER
        self.player = Player()
        self.all_sprites.add(self.player)
        # CREATE THE PLATFORMS
        self._add_platform(0, HEIGHT-40, WIDTH, 40)
        self._add_platform(WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 20)

        self.run()

    def run(self):
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        self.all_sprites.update()
        hits = pg.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            self.player.pos.y = hits[0].rect.top + 1
            self.player.vel.y = 0

    def events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.playing = False
                self.running = False

    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)

        #######
        pg.display.flip()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass

g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()