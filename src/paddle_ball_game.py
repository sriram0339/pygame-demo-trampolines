import pygame 
import random 
from game_framework import Game

class GameParams:
    width = 640
    height = 480 
    keypress_events = [ (pygame.K_LEFT, 'left_keypress'), 
                       (pygame.K_RIGHT, 'right_keypress'),
                       (pygame.K_SPACE, 'space_keypress')]
    ball_speed = 5
    paddle_speed = 25
    paddle_width = 100
    paddle_height = 10
    ball_radius = 10

class Ball:
    pass 

class Paddle: 
    pass 

def init_game(): 
    pass 


if __name__ == "__main__":
    init_game()
    #pygame.quit()