import pygame
import math

# target.py 
# version 0.2 : initial development

class Target:

    def __init__(self,
                 x,
                 y,
                 direction,
                 speed = 1,
                 id = None,
                 size=8):
        
        self.id = id                # unique id for the target 
        self.position = pygame.Vector2(x,y)     # pygame vector object
        self.direction = direction  # direction of travel
        self.speed = speed          # rate of travel to be used for movement
        self.size = size            # Determines how large the target will be drawn
        self.angle = 0              # the angle of movment of the target


    # draw the target
    def draw_target(self,
                    screen, 
                    color=(0,0,0)):
        """
        Draws the target on the screen
        
        variables:
        screen (pygame display object) : display object to draw upon
        color (tuple) : default to black

        returns:
        None

        """
        pygame.draw.circle(screen, color, self.position, self.size)



    # move the target
    def move(self, 
             method=None):
        """
        Moves the target based on the selected method
        
        Variables:
            method (string): determines the method of movement. Default is None and will move in its direction of travel at a consistent rate
        
        return:
            None

        """
        
        # if no method is selected the target will move in its direction at a constant rate
        if method == None:

            x1 = self.position.x
            y1 = self.position.y # before move - not used yet

            if self.direction == 'right':
                self.position.x += self.speed
            
            if self.direction == 'left':
                self.position.x -= self.speed

            if self.direction == 'down':
                self.position.y += self.speed # just a horizontal movement for initial testing

            if self.direction == 'up':
                self.position.y -= self.speed # just a horizontal movement for initial testing

            # not used yet
            x2 = self.position.x
            y2 = self.position.y  # after move

            x,y = (x2-x1, y2-y1)   
            self.angle = pygame.math.Vector2(x, -y).angle_to((1, 0))  # the angle of movment Note: 90 is straight down
            #print(self.angle)
            

    