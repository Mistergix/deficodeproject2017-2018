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

        for plat in PLATFORM_LIST:
            self._add_platform(*plat)

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
        if self.player.vel.y > 0: # Only if the player is falling on the platform
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                self.player.pos.y = hits[0].rect.top + 1
                self.player.vel.y = 0

        if self.player.rect.top <= HEIGHT//4:
            vel = abs(self.player.vel.y)
            self.player.pos.y += vel
            for plat in self.platforms:
                plat.rect.y += vel   
                if plat.rect.top >= HEIGHT: # If the platform is down the screen, delete it
                    plat.kill()
                    # Add a new one 
                    
                    w = random.randrange(WIDTH//10, WIDTH//5)
                    h = 20
                    x = random.randrange(0, WIDTH - w)
                    y = random.randrange(-h - 55, -h -10)
                    self._add_platform(x, y, w, h)     

    def events(self):
        for ev in pg.event.get():
            if ev.type == pg.QUIT:
                self.playing = False
                self.running = False

            if ev.type == pg.KEYDOWN:
                key = ev.key
                if key == pg.K_SPACE:
                    hits = pg.sprite.spritecollide(self.player, self.platforms, False)
                    if hits:
                        self.player.jump()

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