import pygame as pg
from settings import *

class Frame:
    def __init__(self, xywh):
        """
        x : x-coord of the image in the spritesheet
        y : y-coord of the image in the spritesheet
        w : width of the image
        h : height of the image
        """
        assert len(xywh) == 4, "The frame must contain four elements"
        self.xywh = xywh

class Spritesheet:
    # utility class for loading and parsing spritesheets
    def __init__(self, filename):
        self.sheet = pg.image.load(filename).convert()

    def get_image(self, frame):
        """
        Frame
        Loads the image on the spritesheet, given its x, y coordinate and its width and height
        """
        assert type(frame) is Frame, "{} isn't a frame".format(frame)
        x,y,w,h = frame.xywh
        image = pg.Surface((w,h))
        image.blit(self.sheet, (0,0), (x,y,w,h))
        image.set_colorkey(BLACK)
        image = pg.transform.scale(image, (w//2, h//2))
        return image

class AnimationBuilder:
    def __init__(self, idle_frame_list, spritesheet):
        """
        idle animation : list[Frame]
        The list mustn't be empty
        """
        self._image_dict = dict()
        self.spritesheet = spritesheet
        self.add_animation(Animation.IDLE, idle_frame_list)

    def add_animation(self, key, frame_list):
        """
        str, list[Frame]
        The list mustn't be empty
        Return self for chain building
        """
        assert len(frame_list) > 0, "There must be at least on frame in the idle animation"
        image_list = []
        for frame in frame_list:
            image = self.spritesheet.get_image(frame)
            image_list.append(image)
        self._image_dict[key] = image_list
        return self

    def build(self):
        return Animation(self._image_dict)
    

class Animation:
    IDLE = "idle"
    WALK = "walk"
    JUMP = "jump"
    def __init__(self, dictionnary):
        """
        dict[list[pg.image]]
        Build the animation with the AnimationBuilder class
        """
        self._image_dict = dictionnary
        self._frame_dict = dict()
        for key in self._image_dict:
            self._frame_dict[key] = 0

    def __getitem__(self, key):
        """
        Returns a list of images
        """
        return self._image_dict[key]

    def get_current_frame(self, key):
        if key not in self._frame_dict:
            return 0
        return self._frame_dict[key]

    

class Animator:
    def __init__(self, anims):
        """
        Animation
        """

        self.anims = anims
        self.idle_image = self.anims[Animation.IDLE][0]

        self.last_update = pg.time.get_ticks()
        self.update_time = 350

    def get_current_image(self, key):
        now = pg.time.get_ticks()
        if now - self.last_update > self.update_time:
            self.last_update = now
            frame = self._update_frame(key)
        else :
            frame = self.anims._frame_dict[key]
        return self.anims._image_dict[key][frame]

    def _update_frame(self, key):
        l = len(self.anims._image_dict[key])
        self.anims._frame_dict[key] += 1
        self.anims._frame_dict[key] %= l
        return self.anims._frame_dict[key]
