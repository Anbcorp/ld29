import pygame

from utils import UP, DOWN, LEFT, RIGHT


class Animation(object):

    def __init__(self, entity):
        self.entity = entity

    def animate(self, delta_time, game):
        pass

class StaticAnimation(Animation):
    """
    Mockup to handle non animated objects

    Use the tileset as the single animation frame.
    """
    def __init__(self, entity):
        super(StaticAnimation, self).__init__(entity)
        self.entity.image = self.entity.tileset

class EntityAnimation(Animation):
    """
    Animates entity or anything that have 4 animations (one per direction) of 3
    frames each
    """
    def __init__(self, entity):
        super(EntityAnimation, self).__init__(entity)
        # TODO: handles more (or less) than three frames per animation
        self.sprites = {
                'up':[
                    entity.tileset.subsurface(pygame.Rect(0,96,32,32)),
                    entity.tileset.subsurface(pygame.Rect(32,96,32,32)),
                    entity.tileset.subsurface(pygame.Rect(64,96,32,32)),
                    ],
                'down':[
                    entity.tileset.subsurface(pygame.Rect(0,0,32,32)),
                    entity.tileset.subsurface(pygame.Rect(32,0,32,32)),
                    entity.tileset.subsurface(pygame.Rect(64,0,32,32)),
                    ],
                'left':[
                    entity.tileset.subsurface(pygame.Rect(0,32,32,32)),
                    entity.tileset.subsurface(pygame.Rect(32,32,32,32)),
                    entity.tileset.subsurface(pygame.Rect(64,32,32,32)),
                    ],
                'right':[
                    entity.tileset.subsurface(pygame.Rect(0,64,32,32)),
                    entity.tileset.subsurface(pygame.Rect(32,64,32,32)),
                    entity.tileset.subsurface(pygame.Rect(64,64,32,32)),
                    ],
                }
        self.elapsed_time = 0
        self.frame = 0

        self.entity.image = self.sprites['right'][0]
        self.last_dir = self.entity.direction

    def animate(self, delta_time, game):
        speed = self.entity.h_speed
        self.elapsed_time += delta_time



        if self.elapsed_time > 10./speed*2:
            self.frame = (self.frame+1)%3
            self.elapsed_time = 0

        if self.entity.direction == LEFT:
            self.entity.image = self.sprites['left'][self.frame]
        if self.entity.direction == RIGHT:
            self.entity.image = self.sprites['right'][self.frame]
        # if self.entity.direction == UP:
        #     self.entity.image = self.sprites['up'][self.frame]
        if self.entity.direction == DOWN:
            self.entity.image = self.sprites['down'][self.frame]

class EffectAnimation(pygame.sprite.Sprite):

    tileset = pygame.image.load('res/dig.png')

    def __init__(self, tileno, *groups):
        super(EffectAnimation, self).__init__(*groups)

        yoffset = tileno*32
        self.sprites = [
                        self.tileset.subsurface(pygame.Rect(0,yoffset,32,32)),
                        self.tileset.subsurface(pygame.Rect(32,yoffset,32,32)),
                        self.tileset.subsurface(pygame.Rect(64,yoffset,32,32)),
                        self.tileset.subsurface(pygame.Rect(96,yoffset,32,32)),
                    ]
        self.elapsed_time = 0
        self.frame = 0
        self.image = self.sprites[0]
        self.layer=10

        self.sounds = [
            pygame.mixer.Sound('res/dig.ogg'),
            pygame.mixer.Sound('res/digout.ogg'),
        ]
        self.channel = pygame.mixer.Channel(1)
        self.play_sound(tileno)


    def update(self, delta_time, game):

        self.elapsed_time += delta_time
        if self.frame >= len(self.sprites)-1:
            self.kill()
            return

        if self.elapsed_time > 0.1:
            self.frame = (self.frame+1)%len(self.sprites)
            self.elapsed_time = 0

        self.image = self.sprites[self.frame]

    def play_sound(self, tileno):
        self.channel.play(self.sounds[tileno])

    def kill(self):
        self.channel.stop()
        super(EffectAnimation, self).kill()


