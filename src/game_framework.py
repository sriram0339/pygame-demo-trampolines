import pygame 
import random

class Game:

    def __init__(self,  initial_entities, window_dims=(640, 480), caption="Simple Game", bg_color=(255, 255, 255), time_step=60):
        pygame.init()
        (width, height) = window_dims
        self.screen = pygame.display.set_mode((width, height))
        self.screen.fill(bg_color)
        self.bg_color = bg_color
        self.time_step = time_step
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.ents = initial_entities
        self.running = True
        self.listeners = {}
        self.event_queue = [] 
        for e in self.ents:
            e.init(self)
        
    def add_entity(self, entity):
        self.ents.append(entity)
        entity.init(self)
        
    def add_listener(self, entity, event, callback):
        if event not in self.listeners:
            self.listeners[event] = []
        self.listeners[event].append((entity, callback))

    def send_event(self, event, params):
        if event in self.listeners:
            lambs = self.listeners[event]
            new_lambs = [] 
            for entity, callback in lambs:
                rval = callback(self, params)
                if rval:
                    new_lambs.append((entity, callback))
            self.listeners[event] = new_lambs

    def game_over(self):
        self.running = False
        return False

    def run(self, keypress_events):
        # first run all the keypress events 
        while self.running:
            self.clock.tick(self.time_step)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                    # check if the event is a keypress event
                    for key, event_name in keypress_events:
                        if event.key == key:
                            self.send_event(event_name, None)
            # first call update on all the entities 
            new_entities = [] 
            for entity in self.ents:
                new_entities += entity.update(self)
            self.ents = new_entities
            # then draw all the entities
            self.screen.fill(self.bg_color)
            for entity in self.ents:
                entity.draw(self.screen)
            pygame.display.update()