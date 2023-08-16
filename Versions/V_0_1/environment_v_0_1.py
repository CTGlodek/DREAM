import pygame
import math
import random
from sensor import *
from target import *

# environment.py 
# version 0.1 : initial development

class Environment:
    def __init__(self,
                 screen_size):
        self.screen_size= screen_size
        self.running = False
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_size))
        self.tracked = []

    def create_env(self, 
                   target_info, 
                   sensor_info):

        """
        Creates the target and sensor objects
        
        Variables:
        target_info (list): a list of parameters needed to generate the individual targets objects
        sensor_info (list): a list of parameters needed to generate the individual sensors objects

        returns:
        targets (list): a list of target objects
        sensors (list): a list of sensor objects

        """
        targets = []
        sensors = []

        for target in target_info: 
            #print('target Starting postion: ', target)
            targets.append(Target(target[0], target[1],id=target[2]))

        for sensor in sensor_info:
            sensors.append(Sensor(sensor[0],sensor[1],fov=sensor[2]))

        return targets, sensors

    def generate_target_list(self, num_targets):
        """
        Creates a batch of information used to create targets in a semi random 
        distro near the middle of the board width. Currently used for testing

        Variables:
            num_targets (int): how many target are to be created
        
        Returns:
            list_o_targets (list): the x coordinate, y coordinate, and id number

        """

        list_o_targets = []

        for i in range(num_targets):
            temp =((random.randint(0,(i*2)+1)*25 + 500), random.randint(-250,0),i+1)
            list_o_targets.append(temp)

        return list_o_targets

    def run_env(self, targets, sensors):
        
        # pygame setup
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()

        while self.running:
                # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("purple")

            covered_targets = []

            #for target, sensor in zip(targets, sensors):
             #   target.move()
              #  sensor.update_sensor_fov(targets)
               # if len(sensor.detected) > 0: 
                #    for var in sensor.detected:
                 #       covered_targets.append(var.id)
                #target.draw_target(self.screen)
                #sensor.draw_sensors(self.screen)
            for target in targets:
                target.move()
                target.draw_target(self.screen)

            for sensor in sensors:
                sensor.update_sensor_fov(targets)
                sensor.update_energy()
                if len(sensor.detected) > 0: 
                    for var in sensor.detected:
                        covered_targets.append(var.id)
                sensor.draw_sensors(self.screen)
                    
            
            

            self.tracked.append(covered_targets)
            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.clock.tick(60) / 1000

        pygame.quit()

        return 