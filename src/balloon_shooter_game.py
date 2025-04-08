import pygame 
import random 
from game_framework import Game 

class GameParams:
    width = 640
    height = 480 
    balloon_max_height = 15
    balloon_min_height = 120
    bullet_y_speed = 5
    revenge_brick_y_speed = 15
    keypress_events = [ (pygame.K_LEFT, 'left_keypress'), 
                       (pygame.K_RIGHT, 'right_keypress'),
                       (pygame.K_SPACE, 'space_keypress')]

class RevengeBrick:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 10
        self.color = (255, 0, 0)  # Red color for the revenge brick

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def move(self):
        # Move the revenge brick downwards
        self.y += GameParams.revenge_brick_y_speed
        return 
    
    def init(self, game_state):
        pass 

    def update(self, game_state):
        self.move()
        game_state.send_event('revenge_brick_position', (self.x, self.y))
        if self.y > GameParams.height:
            return []
        else:
            return [self]

class Shooter: 

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 10
        self.color = (0, 0, 255)  # Blue color for the shooter

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        #pygame.draw.rect(screen, self.color, (self.x + self.width//4, self.y - self.height//2, self.width//2, self.height//2))

    def move(self, dx):
        self.x += dx
        # Keep the shooter within the screen bounds
        if self.x < 0:
            self.x = 0
        elif self.x > GameParams.width - self.width:
            self.x = GameParams.width - self.width
        return True 

    def fire(self, game_state):
        # Create a new bullet and add it to the game state
        bullet = Bullet(self.x + self.width // 2, self.y - 10)
        game_state.add_entity(bullet)
        return True 
    
    def check_revenge_brick(self, game_state, pos):
        brick_x, brick_y = pos
        # check if the revenge brick hits the shooter
        if (brick_x - self.x)**2 + (brick_y - self.y)**2 < (self.width + 5)**2:
            game_state.game_over()
            return False
        else:
            return True
    

    def init(self, game_state):
        game_state.add_listener(self, 'left_keypress', lambda g,p: self.move(-2))
        game_state.add_listener(self, 'right_keypress', lambda g,p: self.move(2))
        game_state.add_listener(self, 'space_keypress', lambda g,p: self.fire(g))
        game_state.add_listener(self, 'revenge_brick_position', lambda g,p: self.check_revenge_brick(g, p))
        #game_state.add_listener(self, 'tick', lambda g: self.update(g))

    def update(self, game_state):
        return [self]

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 5
        self.color = (0, 255, 255)  # Green color for the bullet

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self):
        self.y -= GameParams.bullet_y_speed
        return 

    def update(self, game_state):
        game_state.send_event('bullet_position', (self.x, self.y))
        self.move()
        if self.y < 0:
            return []
        else:
            return [self]

    def init(self, game_state):
        pass

class Balloon:
    def __init__(self, x, y, dirn):
        self.x = x
        self.y = y
        self.radius = 20
        self.dirn = dirn
        self.color = (255, 0, 0)  # Red color for the balloon
        self.hit = False 

    def draw(self, screen):
        if not self.hit:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)

    def move(self):
        # balloon moves 
        self.x += random.uniform(-1.0, 4.0) * self.dirn
        self.y += random.uniform(-1, 1)
        # check if the balloon is out of bounds
        if self.y > GameParams.balloon_min_height:
            self.y = GameParams.balloon_min_height
        elif self.y < GameParams.balloon_max_height:
            self.y = GameParams.balloon_max_height
        if self.x < 0:
            self.x = 0
        if self.x > GameParams.width:
            self.x = GameParams.width
        return 

    def update(self, game_state):
        if self.hit: 
            # Generate revenge brick 
            if random.random() < 0.1:
                revenge_brick = RevengeBrick(self.x, self.y)
                revenge_brick.init(game_state)
                return [revenge_brick] 
            else:
                return []
        else:
            self.move()
            if self.dirn == 1 and self.x <= GameParams.width - self.radius:
                return [self]
            elif self.dirn == -1 and self.x >= self.radius:
                return [self]
            else:
                # if the balloon is out of bounds, remove it
                return []
        
    def bullet_pos(self, game_state, pos):
        bullet_x, bullet_y = pos
        # check if the bullet hits the balloon
        if not self.hit and (bullet_x - self.x)**2 + (bullet_y - self.y)**2 < (self.radius + 5)**2:
            # bullet hits the balloon
            self.hit = True
            game_state.send_event('balloon_hit', 0)
            return False 
        else:
            return True
        

    def balloon_hit(self, game_state):
        # balloon is hit by the shooter
        self.hit = True
        return False 
    
    def init(self, game_state):
        game_state.add_listener(self, 'bullet_position', lambda g,p: self.bullet_pos(g, p))
        pass 

class BalloonGenerator:
    def __init__(self):
        pass 

    def init(self, game_state):
        #game_state.add_listener(self, 'tick', lambda g: self.generate_balloons(g))
        pass

    def update(self, game_state):
        u = random.uniform(0.0, 10.0)
        if u < 0.1:
            # initialize a new balloon at the left hand corner of the screen 
            balloon = Balloon(10, random.randint(GameParams.balloon_max_height, GameParams.balloon_min_height), 1)
            balloon.init(game_state)
            return [self, balloon]
        elif u < 0.2:
            # initialize a new balloon at the right hand corner of the screen 
            balloon = Balloon(GameParams.width - 10, random.randint(GameParams.balloon_max_height, GameParams.balloon_min_height), -1)
            balloon.init(game_state)
            return [self, balloon]
        else:
            return [self]
        
    def draw(self, screen):
        # draw the balloon
        pass

class GameDisplay:
    def __init__(self):
        self.score = 0

    def init(self, game_state):
        game_state.add_listener(self, 'balloon_hit', lambda g,p: self.balloon_hit(g))

    def update(self, game_state):
        return [self]

    def balloon_hit(self, game_state):
        # draw a text box at the top right corner of the screen 
        self.score += 1
        return True

    def draw(self, screen):
        font = pygame.font.Font(None, 36)
        text = font.render(f"Score: {self.score}", True, (0, 0, 0))
        screen.blit(text, (GameParams.width - 100, 10))


if __name__ == "__main__":
    game = Game([
        BalloonGenerator(),
        Shooter(300, GameParams.height - 50),
        GameDisplay()
    ], window_dims=(GameParams.width, GameParams.height), caption="Balloon Shooter", bg_color=(255, 255, 255), time_step=60)
    game.run(GameParams.keypress_events)
    pygame.quit()
    print("Game Over")