import pygame



from lib.utils import *
from src import level
from src.entities import *

class EventListener(object):
    """
    Process pygame events, such as mouse or keyboard inputs
    """
    def __init__(self, game):
        self.key_listeners = set()
        self.mouse_listeners = set()
        self.game = game

    def register_listener(self, listener, event_type):
        if event_type == pygame.KEYDOWN:
            self.key_listeners.add(listener)
        if event_type == pygame.MOUSEBUTTONDOWN:
            self.mouse_listeners.add(listener)

    def process_events(self):
        events = [event for event in pygame.event.get()]

        for event in events:
            if event.type == pygame.QUIT:
                self.game.quit()
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                for listener in self.key_listeners:
                    listener.process_key_event(event)
            elif (event.type == pygame.MOUSEBUTTONDOWN or
                        event.type == pygame.MOUSEBUTTONUP):
                for listener in self.mouse_listeners:
                    listener.process_mouse_event(event)
            elif event.type == pygame.MOUSEMOTION:
                for listener in self.mouse_listeners:
                    listener.process_mouse_event(event)

class Game(object):

    # TODO: game is used everywhere, and we can't have multiple games instance
    # at the same time. Make it a singleton
    def __init__(self):
        self.event_listener = EventListener(self)
        self.running = True
        self.finishing = False
        self.level = level.WorldLevel
        self.selected_tile = None
        self.font = pygame.font.Font('res/tobago.ttf', 35)
        self.rem_time = 0.
        self.started = False

        print 'Started game', id(self)

    def process_key_event(self, event):
        if not self.started and not event.key == pygame.K_r:
            self.started = True
        if event.key == pygame.K_ESCAPE:
            self.quit()
        if event.key == pygame.K_r:
            self.running = True

    def process_mouse_event(self, event):
        if (event.type == pygame.MOUSEBUTTONDOWN or
            event.type == pygame.MOUSEBUTTONUP):
            self.started = True
        if event.type == pygame.MOUSEMOTION:
            (mx, my) = event.pos
            mx += self.entities.camera[0]
            mx /= 32
            my += self.entities.camera[1]
            my /= 32

            self.set_selected(mx, my)

    def quit(self):
        self.running = False
        self.finishing = False

    def set_selected(self, x, y):
        if self.selected_tile != None:
            if x != self.selected_tile[0] or y != self.selected_tile[1]:
                self.current_level.unselect(*self.selected_tile)
                self.current_level.select(x,y)
        else:
            self.current_level.select(x,y)
        self.selected_tile = (x,y)

    def do_splash(self, screen):
        color = (255,255,255)
        txt = self.font.render('YADIG', False, color)
        screen.blit(txt, (320 - txt.get_width()/2,40))
        txt = self.font.render('Loading...', False, color)
        screen.blit(txt, (320 - txt.get_width()/2, 400))
        screen.blit(pygame.image.load('res/splash.png'), (60,100))
        pygame.display.flip()

    def draw_gui(self, screen):
        score = self.font.render('%09d' % self.player.score,
                False, (255,255,255))
        screen.blit(score, (4,4))
        r_min = self.rem_time / 60
        r_sec = self.rem_time % 60
        r_time = self.font.render('%d:%02d'%(r_min, r_sec),
            False, (255,255,255))
        screen.blit(r_time, (640-r_time.get_width()-4, 4))

    def do_finish(self, screen):
        txt = self.font.render('Game Over !', False, (255,255,255))
        screen.blit(txt, (320-txt.get_width()/2, 40))
        txt = self.font.render('Press R to restart', False, (255,255,255))
        screen.blit(txt, (320-txt.get_width()/2, 70))
        pygame.display.flip()
        self.finishing = True

        while self.finishing:
            self.event_listener.process_events()
            if self.running:
                self.started = False
                self.finishing = False
                self.main(screen)

    def add_time(self):
        self.rem_time += 20

    def init(self, screen):
        self.event_listener.register_listener(self, pygame.KEYDOWN)
        self.event_listener.register_listener(self, pygame.MOUSEBUTTONDOWN)
        self.main(screen)

    def main(self, screen):
        clock = pygame.time.Clock()
        self.rem_time = 180.

        # draw screen
        screen.fill((0,0,0))
        pygame.display.flip()
        self.do_splash(screen)
        self.current_level = self.level()

        entities = level.ScrolledGroup()
        self.entities = entities
        self.entities.debug = False
        self.player = Player(self, entities)
        self.player.move_to(self.current_level.start_pos)

        e_time = 0
        w_time = 0
        while self.running:

            dt = clock.tick(30)

            if self.started:
                e_time += dt / 1000.
                w_time += dt / 1000.
            if e_time >= 1:
                self.rem_time -= int(e_time)
                e_time = 0
            if w_time >= 3:
                self.current_level.add_worm()
                print self.rem_time, self.current_level.worms_count
                w_time = 0
            # process events
            self.event_listener.process_events()

            # update state of game
            entities.update(dt / 1000., self)
            self.current_level.update(dt / 1000., self)

            self.current_level.draw(screen)
            entities.draw(screen)
            self.draw_gui(screen)

            if self.rem_time <= 0:
                self.started = False
                self.running = False
                self.finishing = True
                fog = pygame.Surface((640,480))
                fog.fill((128,128,128,120))
                screen.blit(fog, (0,0), special_flags = pygame.BLEND_RGBA_MULT)
            pygame.display.flip()

        if self.finishing:
            self.do_finish(screen)

if __name__ == '__main__':
    pygame.mixer.pre_init(buffer=2048)
    pygame.init()
    # TODO : screen size from conf ? Or at least constant
    screen = pygame.display.set_mode((640,480), pygame.HWSURFACE|pygame.DOUBLEBUF)

    Game().init(screen)
