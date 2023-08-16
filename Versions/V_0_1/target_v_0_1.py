import pygame
import math

# target.py 
# version 0.1 : initial development

class Target:

    def __init__(self,
                 x,
                 y,
                 speed = 1,
                 id = None,
                 size=8):
        
        self.id = id       # unique id for the target 
        self.position = pygame.Vector2(x,y)     # pygame vector object
        self.speed = speed  # rate of travel to be used for movement
        self.size = size    # Determines how large the target will be drawn


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
            method (string): determines the method of movement. Default is None and will move from top to bottom at a consistent rate
        
        return:
            None

        """
        
        # if no method is selected the target will move from top to bottom at a consitent rate
        if method == None:
            self.position.y += self.speed # just a horizontal movement for initial testing

    