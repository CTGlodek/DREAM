import pygame
import numpy as np
import matplotlib.pyplot as plt
import math
import random
from sensor import *
from target import *

# environment.py 
# version 0.2

class Environment:
    def __init__(self,
                 screen_size):
        self.screen_size= screen_size
        self.running = False
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.screen_size))
        self.tracked = []
        self.energy = []
        self.energy_total = 0

    def test():
        print('test')

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
            targets.append(Target(target[0], target[1], target[2], id=target[3]))

        for sensor in sensor_info:
            temp_sensor = Sensor(sensor[0],sensor[1],fov=sensor[2])
            sensors.append(temp_sensor)
            self.energy_total = self.energy_total + temp_sensor.energy_start

        print('Total inital sensor energy level: ', self.energy_total)

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
        list_o_directions = ['right', 'left', 'down', 'up']
        right = (0, self.screen.get_height()/2)
        left = (self.screen.get_width(), self.screen.get_height()/2)
        up = (self.screen.get_width()/2, self.screen.get_height())
        down = (self.screen.get_width()/2, 0)

        list_o_targets = []
        
        for i in range(num_targets):

            starting_offset = i * 25 # provide an offset for each target. Ensures they are not bunched together
            lane_offset = 25

            temp_dir = random.choice(list_o_directions) # pick a random starting point
            
            if temp_dir == 'right':    
                temp = (right[0] - starting_offset, right[1] + lane_offset, temp_dir, i+1)

            if temp_dir == 'left':
                temp = (left[0] + starting_offset, left[1] - lane_offset, temp_dir, i+1)
            
            if temp_dir == 'up':
                temp = (up[0] + lane_offset,up[1] + starting_offset, temp_dir, i+1)
            
            if temp_dir == 'down':
                temp = (down[0] - lane_offset, down[1] - starting_offset, temp_dir, i+1)

            list_o_targets.append(temp)

        return list_o_targets


    def env_stats(self, plot=False):

        # equalize the array sizes for processing
        track_temp = np.zeros([len(self.tracked),len(max(self.tracked,key = lambda x: len(x)))])
        energy_temp = self.energy

        for i,j in enumerate(self.tracked):
            track_temp[i][0:len(j)] = j

        # show the number of targets tracked and their IDs
        print('The unique targets tracked: ',np.unique(track_temp)[1:]) # excludes the zero used for padding the arrays.
        print('The number of unique targets tracked: ', len(np.unique(track_temp))-1) # -1 so we dont count the zero

        if plot:

            fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,5))
            #fig.suptitle('Vertically stacked subplots')
            ax1.plot(np.count_nonzero(track_temp, axis=1));
            ax1.set_title('Targets Tracked')
            ax2.plot(energy_temp);
            ax2.set_title('Total Energy Available')

        return track_temp, energy_temp
    

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
            current_energy = 0 # initialize available energy for this moment

            pygame.draw.rect(self.screen, (0,   0, 255), [0, 0, 550, 350], 0)  # top left
            pygame.draw.rect(self.screen, (0,   0, 255), [650, 0, 550, 350], 0) # top right
            pygame.draw.rect(self.screen, (0,   0, 255), [0, 450, 550, 350], 0) # bottom left
            pygame.draw.rect(self.screen, (0,   0, 255), [650, 450, 550, 350], 0) # bottom right

            for target in targets:
                target.move()
                target.draw_target(self.screen)  

            for sensor in sensors:
                sensor.update_sensor_fov(targets)
                sensor.update_energy()
                
                current_energy = current_energy + sensor.energy # tallies the energy

                if len(sensor.detected) > 0: 
                    for var in sensor.detected:
                        covered_targets.append(var.id)
                sensor.draw_sensors(self.screen)
                    
            # appends all the targets, by id, (if any) that were tracked in this round
            self.tracked.append(covered_targets)

            # appends the total available energy in this moment
            self.energy.append(current_energy)
            
            # flip() the display to put your work on screen
            pygame.display.flip()

            # limits FPS to 60
            # dt is delta time in seconds since last frame, used for framerate-
            # independent physics.
            dt = self.clock.tick(60) / 1000

        pygame.quit()

        return

    
    