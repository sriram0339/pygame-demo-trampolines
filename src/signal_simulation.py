import pygame 
import random 
from game_framework import Game 

# Signal Simulator 


class GameParams:
    width = 640
    height = 480 
    keypress_events = [  (pygame.K_SPACE, 'space_keypress')]
    
def get_color(state):
    if state == 'red':
        return (255, 0, 0)  # Red color
    elif state == 'green':
        return (0, 255, 0)  # Green color
    else:
        return (255, 255, 0)  # Yellow color

class Signal: 
    def __init__(self, x, y, init_state='red', init_counter=0):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.state = init_state
        self.counter = init_counter
        self.color = get_color(self.state)
        self.emergency = False 

    def draw(self, screen):
        # draw black border 
        pygame.draw.rect(screen, (0,0,0), (self.x-1, self.y-1, self.width+2, self.height+2), 1)
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 0)
        

    def emergency_on(self, game_state, params):
        self.emergency = True 
        game_state.add_listener(self, 'emergency_off', self.emergency_off)
        return False  # do not listen to any more emergency_on messages 
    
    def emergency_off(self, game_state, params):
        self.emergency = False 
        game_state.add_listener(self, 'emergency_on', self.emergency_on)
        return False # Do not listen to any more emergency_off messages 

    def update(self, game_state):
        # increment the counter 
        if self.emergency: 
            self.state = 'red'
        else: 
            self.counter += 1
            if self.counter > 120 and self.counter <= 240:
                self.state = 'green'
            elif self.counter > 240 and self.counter <= 300: 
                self.state = 'yellow'
            elif self.counter > 300: 
                self.state = 'red'
                self.counter = 0
        self.color = get_color(self.state)
        return [self]
    
    def init(self, game_state):
        # listen to event called 'emergency_on' 
        game_state.add_listener(self, 'emergency_on', self.emergency_on)
        pass 

class EmergencyVehicle:
    def __init__(self):
        self.emergency = False 
        self.counter = 0
        self.emergency_duration = 100 

    def init(self, game_state):
        game_state.add_listener(self, 'space_keypress', self.emergency_toggle)
        return 

    def emergency_toggle(self, game_state, params):
        if not self.emergency:
            self.emergency = True
            self.counter = 0  
            print('emergency vehicle on')
            game_state.send_event('emergency_on', None)
        return True 
    
    def draw(self, screen):
        pass 

    def update(self, game_state):
        if self.emergency: 
            self.counter += 1
            if self.counter > self.emergency_duration:
                game_state.send_event('emergency_off', None)
                print('emergency vehicle off')
                self.emergency = False
                self.counter = 0
        return [self]


def initialize_simulation():
    game = Game([
       Signal(20+i*60, 115+50*j, init_state='red', init_counter=random.randint(0, 300)) for i in range(10) for j in range(5)
    ] + [ EmergencyVehicle() ], window_dims=(GameParams.width, GameParams.height), caption="Traffic Signals", bg_color=(255, 255, 255), time_step=60)
    game.run(GameParams.keypress_events)
    pygame.quit()
    print("Game Over")

if __name__ == "__main__":
    initialize_simulation()
