__author__ = 'Anbcorp'

import numpy
import pygame
import random

from lib import resources
from lib.animations import EffectAnimation
from lib.utils import DIRECTIONS, DOWN, LEFT, RIGHT, UP

class ScrolledGroup(pygame.sprite.LayeredUpdates):
    """
    This is a sprite Group() whose drawn surface is controlled by camera position

    This suppose all sprites for the level are kept in memory
    """

    def __init__(self, *sprites):
        super(ScrolledGroup, self).__init__(*sprites)
        self._camera_x = 0
        self._camera_y = 0
        self.e_time = 0
        self.debug = False

    @property
    def camera(self):

        return (self._camera_x, self._camera_y)
    @camera.setter
    def camera(self, value):
        self._camera_x = value[0]
        self._camera_y = value[1]

    def update(self, dt, game, *args):
        super(ScrolledGroup, self).update(dt, game, *args)
        self.e_time += dt
        if self.e_time > 1 and self.debug:
            print self.camera
            self.e_time = 0
        # TODO : screen size constants
        cam_x = game.player.rect.x - 320
        cam_y = game.player.rect.y - 240
        if cam_x < 0:
            cam_x = 0
        elif cam_x > game.current_level.h_size*32 - 640:
            cam_x = game.current_level.h_size*32 - 640
        if cam_y < 0:
            cam_y = 0
        elif cam_y > game.current_level.v_size*32 - 480:
            cam_y = game.current_level.v_size*32 - 480
        self.camera = (cam_x, cam_y)

    def draw(self, surface):
        for sprite in self.sprites():
            try:
                surface.blit(sprite.image, (
                    sprite.rect.x - self._camera_x,
                    sprite.rect.y - self._camera_y)
                )
            except Exception as excep:
                print sprite.image, sprite
                raise excep

class Level(object):
    """
    Basic level object
    """
    def __init__(self):
        self.blockers = ScrolledGroup()
        self.tiles = ScrolledGroup()

        (self.h_size, self.v_size) = resources.getValue('level.size')
        self.start_pos = pygame.Rect(64,64,0,0)

        self.generate()


    def generate(self):
        raise RuntimeError('not implemented')

    def update(self, dt, game):
        self.tiles.update(dt, game)
        self.blockers.update(dt, game)

    def draw(self, screen):
        self.blockers.draw(screen)
        self.tiles.draw(screen)



class BasicLevel(Level):

    def __init__(self):
        super(BasicLevel, self).__init__()

    def generate(self):
        # we use pixels instead of tiles
        h_size = self.h_size*32
        v_size = self.v_size*32
        tiles = pygame.image.load(resources.getImage('level'))
        # TODO: load a specific tile from resources
        block = tiles.subsurface(pygame.Rect(6*32,3*32,32,32))

        self.empty_tile = tiles.subsurface(pygame.Rect(0,0,32,32))
        # TODO: level generation here
        # TODO: arbitrary level sizes do not work (empty wall) is not a multiple of 32
        for x in range(0, h_size, 32):
            for y in range(0,v_size,32):
                if x in (0,h_size-32) or y in (0, v_size-32):
                    # Sprite(*groups) add the new sprites in the groups
                    wall = pygame.sprite.Sprite(self.blockers)
                    wall.image = block
                    wall.rect = pygame.rect.Rect((x,y), block.get_size())
                else:
                    if random.randint(0,12) == 0:
                        tile = pygame.sprite.Sprite(self.blockers)
                        tile.image = block
                    else:
                        tile = pygame.sprite.Sprite(self.tiles)
                        tile.image = self.empty_tile
                    tile.rect = pygame.rect.Rect((x,y), tile.image.get_size())


class MazeLevel(Level):

    def __init__(self):
        super(MazeLevel, self).__init__()
        self.set_tiles()
        self.sprites = numpy.empty( (self.h_size, self.v_size),
            dtype=pygame.sprite.Sprite)
        self.select_sprite = pygame.image.load('res/selected.png')
        self.selected_orig = None

        for y in range(0, self.v_size):
            for x in range(0, self.h_size):
                self.autolayout(x, y)

    def set_tiles(self):
        self.tileset = pygame.image.load(resources.getImage('level'))
        # TODO: load a specific tile from resources
        (base_x, base_y) = (4,14)
        self.blocks = self.get_blocks(base_x, base_y)
        self.empty_tile = self.tileset.subsurface(pygame.Rect(0,0,32,32))

    def get_blocks(self, base_x, base_y):
        """
        Return a dicts of blocks variant from a NW corner, suitable for
        autolayouting
        """
        return {
            'N1':self.getTile(base_x+1,base_y),
            'N2':self.getTile(base_x+2,base_y),
            'S1':self.getTile(base_x+1,base_y+3),
            'S2':self.getTile(base_x+2,base_y+3),
            'E1':self.getTile(base_x+3,base_y+1),
            'E2':self.getTile(base_x+3,base_y+2),
            'W1':self.getTile(base_x,base_y+1),
            'W2':self.getTile(base_x,base_y+2),
            'NW':self.getTile(base_x,base_y),
            'NE':self.getTile(base_x+3,base_y),
            'SW':self.getTile(base_x,base_y+3),
            'SE':self.getTile(base_x+3,base_y+3),
            'mNW':self.getTile(base_x+1,base_y+1),
            'mNE':self.getTile(base_x+2,base_y+1),
            'mSW':self.getTile(base_x+1,base_y+2),
            'mSE':self.getTile(base_x+2,base_y+2),
            'iNW':self.getTile(base_x+2,base_y-2),
            'iNE':self.getTile(base_x+3,base_y-2),
            'iSE':self.getTile(base_x+3,base_y-1),
            'iSW':self.getTile(base_x+2,base_y-1),
        }

    def getTile(self, x, y,size=16):
            return self.tileset.subsurface(pygame.Rect(x*16,y*16,16,16))

    def generate(self):
        h_size = self.h_size
        v_size = self.v_size


        self.level = numpy.zeros((h_size, v_size))

        pos = [
            random.randint(1, h_size - 2),
            random.randint(1, v_size - 2)
            ]
        self.start_pos = pygame.Rect(pos[0]*32, pos[1]*32, 0, 0)

        self.start_dir = random.choice(DIRECTIONS)
        dire = self.start_dir

        self.level[pos[0],pos[1]] = 1
        for i in range(0,50):
            for step in range(4,random.randint(5,25)):
                if dire == UP:
                    pos[1] -= 1
                    if pos[1] < 1 :
                        pos[1] = 1
                        dire = random.choice((DOWN,LEFT,RIGHT))

                if dire == DOWN:
                    pos[1] += 1
                    if pos[1] > v_size - 2:
                        pos[1] = v_size- 2
                        dire = random.choice((LEFT,RIGHT,UP))

                if dire == LEFT:
                    pos[0] += 1
                    if pos[0] > h_size - 2:
                        pos[0] = h_size - 2
                        dire = random.choice((DOWN,RIGHT,UP))

                if dire == RIGHT:
                    pos[0] -= 1
                    if pos[0] < 1:
                        pos[0] = 1
                        dire = random.choice((DOWN,LEFT,UP))

                self.level[pos[0],pos[1]] = 1
            choices = DIRECTIONS[:]
            choices.pop(dire)
            dire = random.choice(choices)
        print "map ok"

    def autolayout(self, x, y):
        if self.level[x,y] == 0:
            # place tiles according to surroundings
            # the resulting surface is 32x32
            if self.sprites[x, y]:
                tile = self.sprites[x, y]
            else:
                tile = pygame.sprite.Sprite(self.blockers)

            tile.image = pygame.Surface((32,32))
            # get value for 8 tiles surroundings
            def get_adj_tile(x, y):
                if x > self.h_size-1 or x < 0 :
                    return 0
                if y > self.v_size-1 or y < 0 :
                    return 0
                return int(self.level[x,y])

            n  = int(get_adj_tile(x,y-1))   << 0
            ne = int(get_adj_tile(x+1,y-1)) << 1
            e  = int(get_adj_tile(x+1,y))   << 2
            se = int(get_adj_tile(x+1,y+1)) << 3
            s  = int(get_adj_tile(x,y+1))   << 4
            sw = int(get_adj_tile(x-1,y+1)) << 5
            w  = int(get_adj_tile(x-1,y))   << 6
            nw = int(get_adj_tile(x-1,y-1)) << 7

            v = n+s+e+w+nw+ne+sw+se
            # Assign a bit for each tile surrounding
            # | 128 |   1 |   2 |
            # |  64 | til |   4 |
            # |  32 |  16 |   8 |
            #
            # then for each quadrant of our tile, the surroudings are
            # represented by values
            qNW = v & 0b11000001
            qNE = v & 0b00000111
            qSE = v & 0b00011100
            qSW = v & 0b01110000

            # O is empty (==1)
            # X is filled (==0)
            # add the values for Os

            # for the NW quadrant (x is our tile, O is empty, X is
            # filled)
            if qNW == 193 or qNW == 65:
                # OO XO
                # Ox Ox
                tNW = self.blocks['NW']
            elif qNW == 1 or qNW == 129:
                # OO XO
                # Xx Xx
                tNW = self.blocks['N1']
            elif qNW == 192 or qNW == 64:
                # OX XX
                # Ox Ox
                tNW = self.blocks['W1']
            elif qNW == 128:
                # OX
                # Xx
                tNW = self.blocks['iNW']
            else:
                # XX
                # Xx
                tNW = self.blocks['mNW']

            if qNE == 7 or qNE == 5:
                # 111
                # OO OX
                # xO xO
                tNE = self.blocks['NE']
            elif qNE == 3 or qNE == 1:
                # OO OX
                # xX xX
                tNE = self.blocks['N2']
            elif qNE == 6 or qNE == 4:
                # XO XX
                # xO xO
                tNE = self.blocks['E1']
            elif qNE == 2:
                # X0
                # xX
                tNE = self.blocks['iNE']
            else:
                # XX
                # xX
                tNE = self.blocks['mNE']

            if qSE == 28 or qSE == 20:
                # 111
                # xO xO
                # OO OX
                tSE = self.blocks['SE']
            elif qSE == 12 or qSE == 4:
                # xO xO
                # XO XX
                tSE = self.blocks['E2']
            elif qSE == 24 or qSE == 16:
                # xX xX
                # OO OX
                tSE = self.blocks['S2']
            elif qSE == 8:
                # xX
                # XO
                tSE = self.blocks['iSE']
            else:
                # xX
                # XX
                tSE = self.blocks['mSE']

            if qSW == 112 or qSW == 80:
                # 111
                # Ox Ox
                # OO XO
                tSW = self.blocks['SW']
            elif qSW == 48 or qSW == 16:
                # Xx Xx
                # OO XO
                tSW = self.blocks['S1']
            elif qSW == 96 or qSW == 64:
                # Ox Ox
                # OX XX
                tSW = self.blocks['W2']
            elif qSW == 32:
                # Xx
                # OX
                tSW = self.blocks['iSW']
            else:
                # Xx
                # XX
                tSW = self.blocks['mSW']


            # We blit the smaller tiles into a larger one
            tile.image.blit(tNW, (0,0))
            tile.image.blit(tNE, (16,0))
            tile.image.blit(tSE, (16,16))
            tile.image.blit(tSW, (0,16))
            tile.rect = pygame.rect.Rect((x*32,y*32), (32,32))
            self.outline(tile)
            self.add_bonuses(tile)

        else:
            tile = pygame.sprite.Sprite(self.tiles)
            tile.image = self.empty_tile
            tile.rect = pygame.rect.Rect((x*32,y*32), self.empty_tile.get_size())

        self.sprites[x,y] = tile

    def outline(self, tile, color=(0,0,0)):
        pixels = pygame.surfarray.array3d(tile.image)
        pixels[::,::31] = [0,0,0]
        pixels[::31,::] = [0,0,0]
        tile.image = pygame.surfarray.make_surface(pixels)

    def select(self, x, y):
        tile = self.sprites[x,y]
        self.selected_orig = tile.image
        newimg = tile.image.copy()
        # groups = tile.groups()
        # tile.remove(groups)
        newimg.blit(self.select_sprite, (0,0))
        tile.image = newimg
        # tile.add(groups)

    def unselect(self, x, y):
        tile = self.sprites[x,y]
        if self.selected_orig:
            tile.image = self.selected_orig
            self.selected_orig = None

    def add_bonuses(self, tile):
        pass

class WorldLevel(MazeLevel):
    bonus_set = pygame.image.load('res/gems.png')

    def __init__(self):
        self.bonuses = {
            'diamond':{'value':1000, 'rarity':2, 'mindepth':50, 'hardness':4,
                'sprite': self.bonus_set.subsurface(pygame.Rect(0,0,32,32))},
            'gold':{'value':500, 'rarity':5, 'mindepth':35, 'hardness':3,
                'sprite': self.bonus_set.subsurface(pygame.Rect(32,0,32,32))},
            'silver':{'value':250, 'rarity':15, 'mindepth':20, 'hardness':2,
                'sprite': self.bonus_set.subsurface(pygame.Rect(64,0,32,32))},
            'copper':{'value':100, 'rarity':25, 'mindepth':10, 'hardness':1,
                'sprite': self.bonus_set.subsurface(pygame.Rect(96,0,32,32))},
            'worm':{'value':-1, 'rarity':10, 'mindepth':1, 'hardness':0,
                'maxdepth':15,
                'sprite': self.bonus_set.subsurface(pygame.Rect(128,0,32,32))}
        }

        self.worms_count = 0
        self.worms_max = 20
        super(WorldLevel, self).__init__()



    def generate(self):
        self.level = numpy.zeros((self.h_size, self.v_size))
        self.level[::,0:4] = 1
        self.start_pos = pygame.Rect((64,64),(0,0))

    def set_tiles(self):
        self.tileset = pygame.image.load(resources.getImage('level'))
        # TODO: load a specific tile from resources
        (base_x, base_y) = (16,14)
        self.blocks = self.get_blocks(base_x, base_y)
        self.empty_tile = self.tileset.subsurface(pygame.Rect(0,32,32,32))

    def add_bonuses(self, tile):

        if not tile in self.blockers:
            return

        if hasattr(tile, 'bonus') and tile.bonus :
            # reset previous bonus
            self.set_bonus(tile, tile.bonus, reset=True)
        else:
            tile.bonus = 'None'
            tile.value = 0
            tile.hitpoints = 0
            # set random bonus
            rand = random.randint(0,100)
            if rand < 50:
                for bonus_name in self.bonuses:
                    bonus = self.bonuses[bonus_name]
                    if random.randint(0,100) < bonus['rarity']:
                        self.set_bonus(tile, bonus_name)
                        break;

    def add_worm(self):
        if self.worms_count >= self.worms_max:
            return False

        for i in range(0,100):
            tx = random.randint(0,self.h_size-1)
            ty = random.randint(
                min(self.bonuses['worm']['mindepth'], self.v_size-1),
                min(self.bonuses['worm']['maxdepth'], self.v_size-1)
                )

            tile = self.sprites[tx, ty]

            if self.level[tx, ty] or tile.bonus != 'None':
                continue

            return self.set_bonus(tile, 'worm')

    def set_bonus(self, tile, bonus_name, reset=False):
        bonus = self.bonuses.get(bonus_name, None)
        if not bonus :
            return False

        # do not set bonus if the depth is not proper
        if (tile.rect.y/32) < bonus['mindepth']:
            return False

        bonus_max_depth = bonus.get('maxdepth', 0)
        if bonus_max_depth > 0 and (tile.rect.y/32) > bonus_max_depth:
            return False

        tile.image.blit(bonus['sprite'], (0,0))
        if not reset :
            tile.value = bonus['value']
            tile.hitpoints = bonus['hardness']
            tile.bonus = bonus_name
            if tile.bonus == 'worm':
                self.worms_count += 1

    def dig_out(self, tile):
        if tile.hitpoints > 0:
            tile.hitpoints -= 1

            anim = EffectAnimation(0, [])
            anim.rect = tile.rect.copy()
            self.tiles.add(anim, layer=1)
        else:
            if tile in self.blockers:
                self.blockers.remove(tile)
                if tile.bonus == 'worm':
                    self.worms_count -= 1
                (x,y) = (tile.rect.x/32, tile.rect.y/32)
                self.level[x, y] = 1
                # We need to relayout surrounding tiles
                for ny in range(y-1,y+2):
                    for nx in range(x-1,x+2):
                        if nx > self.h_size - 1 or nx < 0:
                            continue
                        if ny > self.v_size - 1 or ny < 0:
                            continue
                        self.autolayout(nx, ny)
                self.select(x,y)
                anim = EffectAnimation(1, [])
                anim.rect = tile.rect.copy()
                self.tiles.add(anim, layer=1)
                return tile.value
        return 0

if __name__ == '__main__':
    m = MazeLevel()
