import pygame as pg
from settings import *

# Commentaires avec des # : Explications
# Commentaires avec des """" : Consignes

class Frame:
    # On repère la position d'une image sur une spritesheet à l'aide de 4 coordonnées :
    # x : abcisse du coin en haut à gauche de l'image
    # y : ordonnée du coin en haut à gauche de l'image
    # w : largeur de l'image
    # h : hauteur de l'image

    """
    Emile : - Crée la méthode __init__, elle contient les 4 coordonnées ci-dessus
    """
    def __init__(self, xywh):
        self.xywh = xywh
        
        
class Spritesheet:
    # Cette classe stocke une image qui représente une spritesheet
    def __init__(self, filepath):
        self.sheet = pg.image.load(filepath).convert() # A la création de l'objet, on charge la spritesheet
    """
    Emile : Complète le code ci-dessous
    """
    def GetImage(self, frame):
        # La méthode GetImage prends un objet de type Frame en argument et, en utilisant les coordonnées de l'objet Frame, renvoit le sprite associé
        assert type(frame) is Frame # On vérifie que l'objet est bien une Frame
        x,y,w,h = frame.xywh
        image = pg.Surface((w,h)) # Crée une image transparente
        image.blit(self.sheet, (0,0), (x,y,w,h)) # Colle sur cette image le sprite issu de la spritesheet
        image = pg.transform.scale(image, (w//2, h//2)) # Divise par 2 sa taille
        return image

class Animation:
    # Stocke toutes les animations d'un sprite
    # Chaque variable ci-dessous représente un type d'animation
    # STAND représente l'animation quand l'objet ne bouge pas par exemple. 
    # image_dict est un dictionnaire dont les clés sont les variables ci-dessous, chaque clé renvoit vers une liste d'image correspondant à l'animation
    # Par exemple self.image_dict[Animation.STAND] = [image_debout1.png, image_debout2.png]
    # frame_dict est un dictionnaire dont les clés sont les variables ci-dessous, chaque clé renvoit vers un entier qui indique l'état actuel de l'animation
    # Par exemple si self.frame_dict[Animation.STAND] vaut 1, cela veut dire que l'on se trouve à la 2ème image de la liste self.image_dict[Animation.STAND]
    STAND = "stand"
    WALK = "walk"
    JUMP = "jump"

    def __init__(self, spritesheet, stand_frame_list):
        self.spritesheet = ...
        self.image_dict = ... # DICTIONNAIRE VIDE
        self.frame_dict = ... # Dictionnaire vide
        self.AddAnimation(Animation.STAND, ...) # On rajoute l'animation quand l'objet est immobile

    """
    Emile : - Complète AddAnimation et GetCurrentFrame
    """
    def AddAnimation(self, key, frame_list):
        assert len(frame_list) > 0, "Il doit y avoir au moins un élément dans la liste"
        image_list = ... # Liste vide
        for frame in frame_list:
            image = ... # On utilise la méthode GetImage de self.spritesheet en passant frame en argument
            ... # On ajoute l'image dans la liste image_list
        self.frame_dict[key] = ... # On met l'image actuelle à 0
        ... = image_list # On met cette liste d'images dans image_dict

    def GetCurrentFrame(self, key):
        assert key in self.frame_dict, "L'animation n'existe pas"
        return ... # Etant donné une clé, il faut renvoyer l'entier correspondant à cette clé dans frame_dict 

    def __getitem__(self, key):
        # Permet d'accéder aux listes d'images comme ceci : 
        # animation[Animation.STAND] au lieu de animation.image_dict[Animation.STAND]
        return self.image_dict[key]

class Animator:
    # Cette class contient toutes les animations d'un sprite et permet de les mettre à jour
    """
    Emile : Complète __init__, NextFrame et NextImage
    """
    def __init__(self, animation):
        assert type(animation) is Animation
        self.animation = ...
        self.image = ... # On récupère la première image de l'animation STAND, en utilisant self.animation
        self.last_update = pg.time.get_ticks() # Permet de savoir quand l'objet a été animé pour la dernière fois
        self.update_time = 350 # Au bout de combien de temps on anime l'objet (plus le nombre est petit, plus l'objet sera animé vite)


    def NextFrame(self, key):
        longueur = ... # Longueur de la liste d'image correspondant à cette clé, utilise self.animation
        ... # rajoute 1 à l'entier se trouvant dans le dictionnaire de frame de self.animation
        self.animation._frame_dict[key] %= longueur # On s'assure que l'entier ne dépasse pas la taille de la liste
        return self.animation._frame_dict[key]

    def NextImage(self, key):
        now = pg.time.get_ticks()
        if ... : # La différence entre now et last_update est supérieure à update_time
            ... = now # on met last_update à now
            frame = ... # On utilise NextFrame
        else:
            frame = ... # On récupère la frame dans le dictionnaire frame_dict

        # Rappel : frame ici est un entier
        return ... # On renvoit la bonne image (grâce à l'entier frame) de la bonne liste (grâce à key) du dictionnaire image_dict

"""
Emile : - COmplète Box
"""
class Box(pg.sprite.Sprite):
    # Représente l'image de l'objet et ses animations
    # Tout objet qui va être dessiné à l'écran, devra hériter de Box
    def __init__(self, animator):
        pg.sprite.Sprite.__init__(self)
        if ... : # SI animator est None
            self.image = pg.Surface((50,50))
            self.image.fill(...) # On remplit le rectangle de bleu
        else :
            self.image = animator.image
        self.animator = animator
        self.rect = self.image.get_rect()

    def Animate(self):
        pass
