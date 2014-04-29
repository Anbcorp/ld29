import math
import pygame

from lib import resources
from lib.utils import UP, DOWN, LEFT, RIGHT
from lib.animations import EntityAnimation, StaticAnimation
from lib.physics import BaseDisplacement, ReboundDisplacement
from lib.ai import WandererBrain, DumbBrain
from lib.entities import Entity
from lib.sounds import SoundFx

class Bullet(pygame.sprite.Sprite):
    """
    Bullets going straight once launched
    """
    def __init__(self, direction, firepos, *groups):
        super(Bullet, self).__init__(*groups)
        self.image = pygame.image.load(resources.getImage('bullet'))

        self.rect = firepos
        self.direction = direction
        self.speed = 800

    def update(self, dt, game):

        if self.direction == LEFT:
            self.rect.x -= self.speed * dt
        if self.direction == RIGHT:
            self.rect.x += self.speed * dt
        if self.direction == UP:
            self.rect.y -= self.speed * dt
        if self.direction == DOWN:
            self.rect.y += self.speed * dt

class Arrow(Entity):
    """
    A projectile with an origin and an attack target used to compute its
    direction
    """

    def __init__(self, origin, atkpos, game, *groups):
        super(Arrow, self).__init__('bullet', *groups)

        self.animation = StaticAnimation(self)
        self.displacement = ReboundDisplacement(self)
        self.displacement.set_speed(300)

        self.rect = pygame.Rect((origin.x, origin.y), (16, 16))

        self.solid_objects = game.current_level.blockers

        distance = math.sqrt(
                    math.pow(320 - atkpos[0], 2) +
                    math.pow(240 - atkpos[1], 2)
                    )

        self.vector = [
            (atkpos[0] - 320)/distance * self.displacement.h_speed,
            (atkpos[1] - 240)/distance * self.displacement.v_speed,
            ]

        self.sound_fx = SoundFx('bullet')

    def move(self, delta_time, game):
        vector = self.vector[:]
        vector[0] *= delta_time
        vector[1] *= delta_time
        self.displacement.move(vector[0], vector[1], self.solid_objects)

    def touched_by(self, entities):
        self.sound_fx.play_sound('hit')

class Enemy(Entity):

    def __init__(self, name, *groups):
        super(Enemy, self).__init__(name, *groups)

        self.animation = EntityAnimation(self)
        self.displacement = BaseDisplacement(self)
        self.displacement.set_speed(resources.getValue('%s.speed' % name))
        self.brain = WandererBrain(self)

    def move(self, delta_time, game):
        self.displacement.move(self.vector[0], self.vector[1],
            game.current_level.blockers)

    def touched_by(self, sprite):
        if sprite and self.brain:
            self.brain.touched_by(sprite)

class PlayerControlledBrain(DumbBrain):

    def __init__(self, entity):
        super(PlayerControlledBrain, self).__init__(entity)

        self.key_pressed = set()
        self.button_pressed = set()
        self.interact_position = None
        self.dig_delay = 0
        self.jump_delay = 0

    def think(self, delta_time, game):
        self.processInput(delta_time, game)

    def process_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            self.key_pressed.add(event.key)
        if event.type == pygame.KEYUP:
            # Sometime we release a key that was pressed out of game. Ignore
            # that
            try:
                self.key_pressed.remove(event.key)
            except KeyError:
                pass

    def process_mouse_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
                # flag the down button and save the clicked position
                self.button_pressed.add(event.button)
                self.interact_position = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            try:
                self.button_pressed.remove(event.button)
                self.interact_position = None
            except KeyError:
                pass

        if event.type == pygame.MOUSEMOTION and 1 in self.button_pressed:
            self.interact_position = event.pos

    def processInput(self, delta_time, game):
        atkpos = self.entity.rect.copy()
        atkpos.x += 8
        atkpos.y += 10
        self.entity.vector = [0,0]
        self.dig_delay -= 1
        self.jump_delay -= 1
        for key in self.key_pressed:
            if key in (pygame.K_LEFT, pygame.K_a, pygame.K_q):
                self.entity.vector[0] = -self.entity.h_speed * delta_time
                self.entity.direction = LEFT
            if key in(pygame.K_RIGHT, pygame.K_d):
                self.entity.vector[0] = +self.entity.h_speed * delta_time
                self.entity.direction = RIGHT
            if key in (pygame.K_UP, pygame.K_z, pygame.K_w):
                self.entity.direction = UP
                if self.jump_delay <= 0 and self.entity.resting:
                    self.jump_delay = 0.3*30
            if key in (pygame.K_DOWN, pygame.K_s):
                # self.entity.vector[1] = +self.entity.v_speed * delta_time
                self.entity.direction = DOWN

        # process attacks
        if 1 in self.button_pressed and self.dig_delay < 0:
            self.dig_delay = 15


class Player(Entity):

    def __init__(self, game, *groups):
        super(Player, self).__init__('player', *groups)
        self.solid = True

        self.brain = PlayerControlledBrain(self)
        self.game = game
        game.event_listener.register_listener(self.brain, pygame.KEYDOWN)
        game.event_listener.register_listener(self.brain,
            pygame.MOUSEBUTTONDOWN)

        self.animation = EntityAnimation(self)
        self.rect = pygame.Rect((0,0), (16,24))

        self.displacement = BaseDisplacement(self, self.game)
        self.displacement.set_speed(resources.getValue('%s.speed' % 'player'))

        self.e_time = 0
        self.digged = False
        self.score = 0

    @property
    def digging(self):
        return self.brain.dig_delay > 0

    @property
    def jumping(self):
        return self.brain.jump_delay > 0

    def update(self, delta_time, game):
        self.e_time += delta_time
        super(Player, self).update(delta_time, game)
        if self.e_time >= 1:
            # print self.rect.centerx/32, self.rect.centery/32
            self.e_time = 0

    def animate(self, delta_time, game):
        # Do not animate if entity have no speed or is not moving
        if self.h_speed == 0 :
            return
        if self.vector[0] == 0 and self.vector[1] == 0:
            return
        super(Player, self).animate(delta_time, game)

    def move_to(self, new_position):
        if isinstance(new_position, list) or isinstance(new_position, tuple):
            self.rect.x = new_position[0]
            self.rect.y = new_position[1]
        elif isinstance(new_position, pygame.Rect):
            self.rect.x = new_position.x
            self.rect.y = new_position.y
        else:
            raise ValueError("%s.move_to " % (self.__class__) +
                "takes a tuple of coordinates (x,y) or a Rect()")

    def think(self, delta_time, game):
        self.brain.think(delta_time, game)
        if self.digged :
            self.digged = self.digging
        if self.digging and self.brain.interact_position and not self.digged:
            dig_x = self.brain.interact_position[0] + self.game.entities.camera[0]
            # adjusting for camera offset
            dig_x /= 32
            dig_y = self.brain.interact_position[1] + self.game.entities.camera[1]
            dig_y /= 32

            # Can't dig blocks that are too far away
            (self_x, self_y) = (self.rect.centerx/32, self.rect.centery/32)
            block_distance = math.sqrt(
                math.pow(dig_x - self_x, 2) +
                math.pow(dig_y - self_y, 2)
                )
            if block_distance >= 2.5:
                return
            dig_ent = self.game.current_level.sprites[dig_x, dig_y]
            self.dig(dig_ent)
        # digged will remain true until digging switch back to false


    def move(self, delta_time, game):
        if self.jumping:
            self.vector[1] -= 20
            self.resting = False
        self.displacement.apply_gravity()



        self.displacement.move(self.vector[0], self.vector[1],
            game.current_level.blockers)

    def touched_by(self, entity):
        if entity in self.game.current_level.blockers :
            (x,y) = (entity.rect.x/32, entity.rect.y/32)
            if y == self.rect.centery/32+1 and x == self.rect.centerx/32:
                self.resting = True

    def dig(self, block):
        if block in self.game.current_level.blockers and self.digging:
            # Hack, use the down animation for digging
            self.direction = DOWN
            digvalue = self.game.current_level.dig_out(block)
            if digvalue < 0 :
                self.game.add_time()
            else :
                self.score += digvalue
            self.digged = True
