import pygame 
import pygame.font
import random 
from game_framework import Game 
import math 

class GameParams:
    width = 640
    height = 480 
    keypress_events = [ (pygame.K_LEFT, 'left_keypress'), 
                       (pygame.K_RIGHT, 'right_keypress'),
                        (pygame.K_w, 'w_keypress'), 
                        (pygame.K_s, 's_keypress')]
    g = 9.81
    m = 0.25 
    dt = 0.05
    Ixx = 0.01 
    K = [-0.1, -1.0, -30.0]  # PID controller gains
    pad_x = 290
    pad_y = 450
    pad_width = 60 
    ux_step=0.01
    uy_step=0.1
    min_ux = -0.5
    max_ux = 0.5
    min_uy = -5
    max_uy = 5



    
class Quadrotor: 
    def __init__(self, x, y, vx, vy, phi, dphi, ux, uy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.phi = phi 
        self.dphi = dphi
        self.ux = ux 
        self.uy = uy
        self.width = 50
        self.height = 20
        self.color = (0, 0, 255)  # Blue color for the quadrotor
        # load the quadrotor image file from quadrotor.png
        self.image = pygame.image.load('drone.png')
        # scale the image to the size of the quadrotor
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
    
    def init(self, game_state):
        self.x = random.uniform(1/3* GameParams.width, 2/3*GameParams.width)
        self.y = random.uniform(1/6* GameParams.height, 1/3*GameParams.height)
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.phi = random.uniform(-math.pi/6, math.pi/6)
        self.dphi = random.uniform(-0.01, 0.01)
        self.ux = 0
        self.uy = 0
        game_state.add_listener(self, 'left_keypress', self.on_left_keypress)
        game_state.add_listener(self, 'right_keypress', self.on_right_keypress)
        game_state.add_listener(self, 'w_keypress', self.on_w_keypress)
        game_state.add_listener(self, 's_keypress', self.on_s_keypress)




    def draw(self, screen):
        # draw a line from (x,y) to (x + width * cos(phi), y + height * sin(phi))
        #delta_x = self.width * math.cos(self.phi)/2.0
        #delta_y = self.height * math.sin(self.phi)/2.0
        #pygame.draw.line(screen, self.color, (self.x-delta_x, self.y-delta_y), (self.x + delta_x, self.y + delta_y), 5)
        # draw an image of a drone rotated by phi
        rotated_image = pygame.transform.rotate(self.image, math.degrees(-self.phi))
        image_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, image_rect.topleft)

    def update(self, game_state):
        # update the position of the quadrotor
        xp = self.x + self.vx * GameParams.dt
        yp = self.y + self.vy * GameParams.dt
        # update the velocity of the quadrotor
        phip = self.phi + self.dphi * GameParams.dt
        vxp = self.vx + GameParams.g * GameParams.dt * self.phi 
        vyp = self.vy  + GameParams.K[0] * GameParams.dt * self.vy + 1/GameParams.m * GameParams.dt * self.uy 
        dphip = self.dphi + GameParams.K[1] * GameParams.dt * self.phi + GameParams.K[2] * GameParams.dt * self.dphi + 1/GameParams.Ixx * GameParams.dt * self.ux
        self.x = xp
        self.y = yp
        self.vx = vxp
        self.vy = vyp
        self.phi = phip
        self.dphi = dphip
        game_state.send_event('quadrotor_position', (self.x, self.y, self.phi, self.vy))
        game_state.send_event('quadrotor_control', (self.ux, self.uy))
        return [self]
    


    def on_left_keypress(self, gstate,  p):
        # move the quadrotor to the left
        self.ux = self.ux - GameParams.ux_step 
        if self.ux <= GameParams.min_ux:
            self.ux = GameParams.min_ux
        return True 
    
    def on_right_keypress(self, gstate, p):
        # move the quadrotor to the right
        self.ux = self.ux + GameParams.ux_step
        if self.ux >= GameParams.max_ux:
            self.ux = GameParams.max_ux
        return True 

    def on_s_keypress(self, gstate, p):
        # move the quadrotor up
        self.uy = self.uy + GameParams.uy_step
        if self.uy >= GameParams.max_uy:
            self.uy = GameParams.max_uy
        return True 

    def on_w_keypress(self, gstate,  p):
        # move the quadrotor down
        self.uy = self.uy - GameParams.uy_step
        if self.uy <= GameParams.min_uy:
            self.uy = GameParams.min_uy
        return True 

    

class ThrottleDisplay:
    def __init__(self):
        self.ux = 0
        self.uy = 0
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)  # Default font and size
        self.color = (0, 0, 0)  # Black color for the text
        self.width = 50

    def init(self, game_state):
        game_state.add_listener(self, 'quadrotor_control', self.on_quadrotor_control) 

    def on_quadrotor_control(self, game_state, control):
        (ux, uy) = control
        self.ux = ux 
        self.uy = uy
        return True 


    def draw(self, screen):
        text = f"uy: {self.uy:.2f}"
        text_surface = self.font.render(text, True, self.color)
        screen.blit(text_surface, (10, 10))  # Draw at the top-left corner
        text = f"ux: {self.ux:.2f}"
        text_surface = self.font.render(text, True, self.color)
        screen.blit(text_surface, (10, 30))  # Draw at the top-left corner
        

    def update(self, game_state):
        return [self]


class GameStateMonitor:
    def __init__(self):
        self.quadrotor_positions = []
        self.game_over = False
        self.game_won = False
        self.score = 0
        self.time = 0
        self.start_time = None

    def init(self, game_state):
        game_state.add_listener(self, 'quadrotor_position', self.on_quadrotor_position)
    
    def on_quadrotor_position(self, game_state, pos):
        (x, y, phi, vy) = pos
        if x >= GameParams.pad_x and x <= GameParams.pad_x + GameParams.pad_width and y >= GameParams.pad_y and y <= GameParams.pad_y - 10 and phi >= -math.pi/6 and phi <= math.pi/6:
            self.game_won = True
            print("Game Won")
            game_state.game_over()
        elif y <= 10: 
            self.game_over = True
            print("Game Over -- unsafe landing -- crash ")
            game_state.game_over()
        elif y >= GameParams.height - 10:
            self.game_over = True
            print("Game Over -- unsafe landing -- crash ")
            game_state.game_over()
        elif x <= 10:
            self.game_over = True
            print("Game Over -- unsafe landing -- out of bounds")
            game_state.game_over()
        elif x >= GameParams.width - 10:
            self.game_over = True
            print("Game Over -- unsafe landing -- out of bounds")
            game_state.game_over()
        return True 
        
    def update(self, game_state):
        return [self]

    def draw(self, screen):
        # draw the pad 
        pygame.draw.rect(screen, (255, 0, 0), (GameParams.pad_x, GameParams.pad_y, GameParams.pad_width, 10))

    
def main():
    initial_entities = [Quadrotor(0, 0, 0, 0, 0, 0, 0, 0), GameStateMonitor(), ThrottleDisplay()]
    game = Game(initial_entities, window_dims=(GameParams.width, GameParams.height), caption="Quadrotor Landing Game", bg_color=(255, 255, 255), time_step=20)
    game.run(GameParams.keypress_events)

if __name__ == "__main__":
    main()
    pygame.quit()
    print("Game Over")