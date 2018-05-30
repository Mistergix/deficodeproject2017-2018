import pygame as pg
import animation as ani

vec = pg.math.Vector2 # Un vecteur permettant de représenter la position des objets

# Commentaires avec des # : Explications
# Commentaires avec des """" : Consignes

class Cible(ani.Box):
    def __init__(self, animator):
        ani.Box.__init__(self, animator) # On initialise la super classe
        self.position = vec(0,0)

class PlayerItem(ani.Box):
    def __init__(self, animator):
        ani.Box.__init__(self, animator) # On initialise la super classe

class Grappin(PlayerItem):
    def __init__(self, animator, distance):
        PlayerItem.__init__(self, animator)
        self.distance = distance
        self.launched = False

class Grappin1(Grappin):
    def __init__(self, animator):
        Grappin.__init__(animator, 50)

class Bouclier(PlayerItem):
    def __init__(self, animator, resistance):
        PlayerItem.__init__(self, animator)
        self.resistance = resistance

class Bouclier1(Bouclier):
    def __init__(self, animator):
        Bouclier.__init__(animator, 10)

class Player(ani.Box):
    def __init__(self, animator, item):
        ani.Box.__init__(self, animator) # On initialise la super classe
        assert type(item) is PlayerItem
        self.item = item
        self.position = vec(0,0)
        self.HP = 100
        self.selected = False # Le joueur est-il joueur 1 ?

    def update(self):
        self.Animate()
        if self.selected :
            keys = pg.key.get_pressed()
            if keys[pg.K_q] : # TOUCHE q PRESSSEE
                ... # Le joueur va à gauche
            elif keys[...] : # TOUCHE d PRESSEE
                ... # Le joueur va à droite
            elif keys[...] : # TOUCHE espace PRESSEE
                ... # Action2 du joueur

        self.rect.midbottom = ... # Position du joueur

    def Action1(self, cible):
        assert type(cible) is Cible
        pass
    def Action2(self):
        pass

    def Animate(self):
        pass

class Player1(Player):
    def __init__(self, animator):
        grappinAnimator = None
        Player.__init__(self, animator, Grappin1(grappinAnimator))
        self.selected = ... # Joueur 1 doit être selectionné
        self.jumpHeight = -20
        self.isOnGround = True # Permet de savoir si le joueur touche le sol

    def Action1(self, cible):
        pass

    def Action2(self): # Sauter
        if ... : # Le joueur touche-t-il le sol ?
            self.position. ... += ... # On rajoute jumpHeight à l'ordonnée du joueur


class Player2(Player):
    def __init__(self, animator):
        bouclierAnimator = None
        Player.__init__(self, animator, Bouclier1(bouclierAnimator))