import pygame
import random
import environment

# target.py 
# version 0.2 : initial development

class Target:

    def __init__(self,
                 x,
                 y,
                 direction,
                 id = None,
                 size=8):
        
        self.id = id                # unique id for the target 
        self.position = pygame.Vector2(x,y)     # pygame vector object
        self.direction = direction  # direction of travel
        self.speed = 1              # rate of travel to be used for movement    # random.choice([0.25,.5,1])     # can be used for random speeds.    
        self.size = size            # Determines how large the target will be drawn
        self.angle = 0              # the angle of movment of the target
        self.to_turn = False           # Flag to indicate if a turn should be made


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

    def turn(self, env):

        chance_to_turn = random.randint(0,100)

        if chance_to_turn < 100:
            self.to_turn = True

        if self.to_turn:
            turn_direction = random.randint(0,1)

            w_building_lane_interval = int(env.building_width + env.lane_width)
            h_building_lane_interval = int(env.building_height + env.lane_width)

            if self.direction == 'right' or self.direction == 'left': # and self.position.x > env.building_width:
                
                #print(self.position.x % building_lane_interval)
                if turn_direction == 0 and self.position.x in env.turn_points and self.position.x% w_building_lane_interval  == w_building_lane_interval-75:
                    #print('building width: ', env.building_width)
                    #print('Current position: ', self.position.x)
                    self.direction = 'down'
                    #print('Turning down at: ', self.position.x)

                if turn_direction== 1 and self.position.x in env.turn_points and self.position.x % w_building_lane_interval == w_building_lane_interval - 25:
                    self.direction = 'up'
                    #print('Turning up at: ',self.position.x)
                self.to_turn = False

            elif self.direction == 'up' or self.direction == 'down':

                if turn_direction == 0 and self.position.y in env.turn_points and self.position.y % h_building_lane_interval == h_building_lane_interval -75:
                    self.direction = 'left'
                    #print('turning left at: ', self.position.y)

                if turn_direction == 1 and self.position.y in env.turn_points and self.position.y % h_building_lane_interval == h_building_lane_interval -25:
                    self.direction = 'right'
                    #print('turning right at: ', self.position.y)
                self.to_turn = False  

    