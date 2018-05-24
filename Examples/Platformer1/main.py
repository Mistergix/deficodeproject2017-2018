import pygame as pg
import os
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
        self.font_name = pg.font.match_font("arial")
        self.bgcolor = LIGHTBLUE
        self.load_data()

    def load_data(self):
        self.dir = os.path.dirname(__file__)
        data_dir = os.path.join(self.dir, 'data')
        self.spritesheet = Spritesheet(os.path.join(data_dir, SPRITESHEET))

    def _add_platform(self, x, y, w, h):
        p = Platform(x,y,w,h)
        self.all_sprites.add(p)
        self.platforms.add(p)
        return p

    def new(self):
        # CREATE THE SPRITES GROUPS
        self.score = 0
        self.all_sprites = pg.sprite.Group()
        self.platforms = pg.sprite.Group()

        # CREATE THE PLAYER
        player_image = self.spritesheet.get_image(614, 1063, 120, 191)
        self.player = Player(player_image)
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

                    self.score += 10

        if self.player.rect.bottom > HEIGHT:
            self.gameOver()    

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
        self.screen.fill(self.bgcolor)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH//2, 15)
        #######
        pg.display.flip()

    def gameOver(self):
        for sprite in self.all_sprites:
            sprite.rect.y -= max(self.player.vel.y, 10)
            if sprite.rect.bottom < 0:
                sprite.kill()

        if len(self.platforms) <= 0:
            self.playing = False

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for ev in pg.event.get():
                if ev.type == pg.QUIT:
                    waiting = False
                    self.running = False
                if ev.type == pg.KEYDOWN:
                    waiting = False


    def show_start_screen(self):
        self.screen.fill(self.bgcolor)
        self.draw_text(TITLE, 48, WHITE, WIDTH//2, HEIGHT//4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH//2, HEIGHT//2)
        self.draw_text("Press a key to play", 22, WHITE, WIDTH//2, HEIGHT * 3/4)
        pg.display.flip()
        self.wait_for_key()

    def show_go_screen(self):
        if not self.running:
            return
        self.screen.fill(RED)
        self.draw_text("Game over", 48, WHITE, WIDTH//2, HEIGHT//4)
        self.draw_text("Score : {}".format(self.score), 22, WHITE, WIDTH//2, HEIGHT//2)
        self.draw_text("Press a key to play again", 22, WHITE, WIDTH//2, HEIGHT * 3/4)
        pg.display.flip()
        self.wait_for_key()

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()