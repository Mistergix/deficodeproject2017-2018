import pygame as pg
import animation as ani

vec = pg.math.Vector2 # 

# Commentaires avec des # : Explications
# Commentaires avec des """" : Consignes

class Cible(ani.Box):
    def __init__(self, animator, mobile):
        ani.Box.__init__(self, animator) # On initialise la super classe
        self.position = vec(...,...) #Aleatoirement sur l'ecran
        self.mobile = ... # La cible est-elle un objet mouvant(joueur, ennemi) ou inanimé (plateforme)
        self.attire = None
        self.attireur = None
        self.occupe = False # La cible est elle en train d'être tirée (ou tire-t-elle) avec un grappin ?
        self.traction = 0 # De combien de pixels l'attiré bouge

    def Reset(self):
        self.attireur = None
        self.attire = None

    def update(self):
        self.Animate()
################################################################################################
class PlayerItem(ani.Box):
    def __init__(self, animator):
        ani.Box.__init__(self, animator) # On initialise la super classe
################################################################################################
class Grappin(PlayerItem):
    def __init__(self, animator, distance, traction):
        PlayerItem.__init__(self, animator)
        self.distance = distance
        self.traction = traction

    def Attirer(self, attireur, attire):
        assert type(attire) is Cible
        assert type(attireur) is Cible
        attire.attireur = attireur # qui attire l'attiré ?
        attireur.attire = attire # l'attireur attire qui ?
        attireur.occupe = ... # L'attireur est occupé
        attire.occupe = ... # L'attiré est occupé
        attire.traction = self.traction
        attireur.traction = ...
        

class Grappin1(Grappin):
    def __init__(self, animator):
        Grappin.__init__(self, animator, 50, 10)
#################################################################################################
class Bouclier(PlayerItem):
    def __init__(self, animator, resistance):
        PlayerItem.__init__(self, animator)
        self.resistance = resistance

class Bouclier1(Bouclier):
    def __init__(self, animator):
        Bouclier.__init__(self, animator, 10)
###############################################################################################
class Weapon(PlayerItem):
    def __init__(self, animator, degat, portee):
        PlayerItem.__init__(self, animator)
        self.degat = degat
        self.portee = ...
class Weapon1(Weapon):
    def __init__(self, animator):
        Weapon.__init__(self, animator, 20, 20)

#############################################################################################
class Player(Cible):
    def __init__(self, animator):
        Cible.__init__(self, animator, mobile)
        assert type(item) is PlayerItem
        
        self.position = vec(400, 300) 
        self.HP = 100
        self.selected = False 

    def update(self):
        Cible.update(self)
        if self.selected and not self.occupe:
            keys = pg.key.get_pressed()
            if keys[pg.K_q] : 
                self.position -= vec(10,0)
            elif keys[pg.K_d] :
                self.position += vec(10,0) 
            elif keys[pg.K_SPACE] : 
                self.Action2() # Action2 du joueur

        if self.occupe: 
            self.UpdateGrappin()

        self.rect.midbottom = self.position 


    def UpdateGrappin(self):
        if self.attire != None or self.attireur != None : 
            if self.attire != None:
                attire = self.attire
                attireur = self
            elif self.attireur != None :
                attire = self
                attireur = self.attire

            collided = pg.sprite.spritecollide(attire, [attireur], False) 

            if ... : # Les deux ont collisioné
                attireur.Reset()
                attire.Reset()
            else:
                x1, y1 = attireur.position
                x2, y2 = attire.position

                if x1 < x2 : # L'attiré est à droite de l'attireur
                    if y1 < y2 : # L'attiré est en bas de l'attireur
                        attire.position += vec(-self.traction, -self.traction)
                    else:
                        attire.position += vec(..., ...)
                else:
                    if y1 < y2:
                        attire.position += vec(..., ...)
                    else:
                        attire.position += vec(..., ...)

    def Action1(self, cible):
        pass
        
    def Action2(self):
        pass

    def Animate(self):
        pass

class Player1(Player):
    def __init__(self, animator):
        grappinAnimator = None
        Player.__init__(self, animator)
        self.grappin = Grappin1(grappinAnimator)
        self.selected = True
        self.jumpHeight = -20
        self.isOnGround = True

    def Action1(self, cible):
        assert type(cible) is Cible
        if cible.mobile == True : 
            attireur = self
            attire = cible
        else:
            attireur = cible
            attire = self

        self.grappin.Attirer(attireur, attire)

    def Action2(self):
        if self.isOnGround == False : 
            self.position += vec(0, jumpHeight) 


class Player2(Player):
    def __init__(self, animator):
        bouclierAnimator = None
        weaponAnimator = None
        Player.__init__(self, animator)
        self.bouclier = Bouclier1(bouclierAnimator)
        self.weapon = Weapon1(weaponAnimator)

    def Action1(self, cible):
        assert type(cible) is Ennemi
        distance = cible.position.distance_to(self.position)
        if distance < self.weapon.portee :
            cible.TakeDamage(self.weapon.degat)

    def Action2(self):
        pass
########################################################################################
class Ennemi(Cible):
    def __init__(self, animator, HP, degat, portee, target):
        Cible.__init__(self, animator, mobile) # L'ennemi doit-être mobile
        self.HP = ...
        self.degat = ...
        self.portee = ... 
        self.target = ... # La cible de l'ennemi

    def update(self):
        Cible.update(self)  # On appelle le update de la super classe
        distance = self.position.distance_to(self.target.position)
        if ... : # La distance entre l'ennemi et le joueur est inférieure à la portée (utiliser la fonction valeur absolue abs)
            self.Attaquer(self.target)
        else :
            self.BougerVers(self.target)
        self.rect.midbottom = self.position

    def Attaquer(self, player):
        assert type(player) is Player
        pass

    def TakeDamage(self, degat):
        pass

    def BougerVers(self, target):
        pass
