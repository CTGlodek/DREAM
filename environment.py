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
        self.building_width = 0
        self.building_height = 0
        self.lane_width = 100
        self.target_count = 0

    def test():
        print('test')

    def create_env(self, 
                   num_o_targets, 
                   sensor_info,
                   vert_lane_num,
                   hor_lane_num):

        """
        Creates the target and sensor objects
        Creates the buildings and lanes to be drawn based on the number of vertical and horizontal lanes specified.
        
        Variables:
        num_o_targets (int): the number of targets to be generated
        sensor_info (list): a list of parameters needed to generate the individual sensors objects
        vert_lane_num (int): the number of vertical lanes
        hor_lane_num (int): the number of horizontal lanes

        returns:
        targets (list): a list of target objects
        sensors (list): a list of sensor objects
        buildings (list): a list of all the buildings

        """
        self.vert_lanes = vert_lane_num
        self.hort_lanes = hor_lane_num

        #print('the number of vertical lanes is: ', self.vert_lanes)

        targets = []
        sensors = []
        buildings = []

        self.building_width = (self.screen.get_width() - (self.vert_lanes * self.lane_width)) / (self.vert_lanes+1)
        self.building_height = (self.screen.get_height() - (self.hort_lanes * self.lane_width)) / (self.hort_lanes + 1)

        target_info = self.generate_target_list(num_o_targets)

        for i in range(self.vert_lanes+1):
            for j in range(self.hort_lanes+1):
                temp = [i*(self.building_width+self.lane_width), j*(self.building_height+self.lane_width), self.building_width, self.building_height]
                buildings.append(temp)

        for target in target_info: 
            #print('target Starting postion: ', target)
            targets.append(Target(target[0], target[1], target[2], id=target[3]))

        for sensor in sensor_info:
            temp_sensor = Sensor(sensor[0],sensor[1],fov=sensor[2])
            sensors.append(temp_sensor)
            self.energy_total = self.energy_total + temp_sensor.energy_start

        print('Total inital sensor energy level: ', self.energy_total)

        return targets, sensors, buildings

    def generate_target_list(self, num_targets):
        """
        Creates a batch of information used to create targets in a semi random 
        distro near the middle of the board width. Currently used for testing

        Variables:
            num_targets (int):   how many target are to be created
            vert_num (int):      the number of vertical lanes
            hor_num (int):       the number of horizaontal lanes
        
        Returns:
            list_o_targets (list): the x coordinate, y coordinate, and id number

        """
        list_o_directions = ['right', 'left', 'down', 'up']

        hor_start = []
        vert_start = []

        for i in range(self.vert_lanes+1):
            hor_temp = i*(self.building_height + self.lane_width) + self.building_height + self.lane_width/2
            hor_start.append(hor_temp)
        for i in range(self.hort_lanes+1):
            vert_temp = i*(self.building_width + self.lane_width) + self.building_width + self.lane_width/2
            vert_start.append(vert_temp)

        list_o_targets = []
        
        for i in range(num_targets):

            starting_offset = i * 25 # provide an offset for each target. Ensures they are not bunched together
            lane_offset = 25

            temp_dir = random.choice(list_o_directions) # pick a random starting point
            
            if temp_dir == 'right':    
                temp = (0 - starting_offset, random.choice(hor_start) + lane_offset, temp_dir, i+1)

            if temp_dir == 'left':
                temp = (self.screen.get_width() + starting_offset, random.choice(hor_start) - lane_offset, temp_dir, i+1)
            
            if temp_dir == 'up':
                temp = (random.choice(vert_start) + lane_offset, self.screen.get_height()+ starting_offset, temp_dir, i+1)
            
            if temp_dir == 'down':
                temp = (random.choice(vert_start) - lane_offset, 0 - starting_offset, temp_dir, i+1)

            list_o_targets.append(temp)

        return list_o_targets

    def gen_target(self):
        
        self.target_count += 1

        list_o_directions = ['right', 'left', 'down', 'up']

        hor_start = []
        vert_start = []

        for i in range(self.vert_lanes+1):
            hor_temp = i*(self.building_height + self.lane_width) + self.building_height + self.lane_width/2
            hor_start.append(hor_temp)

        for i in range(self.hort_lanes+1):
            vert_temp = i*(self.building_width + self.lane_width) + self.building_width + self.lane_width/2
            vert_start.append(vert_temp)

        lane_offset = 25

        temp_dir = random.choice(list_o_directions) # pick a random starting point
        
        if temp_dir == 'right':    
            target = (0 , random.choice(hor_start) + lane_offset, temp_dir, self.target_count )

        if temp_dir == 'left':
            target = (self.screen.get_width() , random.choice(hor_start) - lane_offset, temp_dir, self.target_count)
        
        if temp_dir == 'up':
            target = (random.choice(vert_start) + lane_offset, self.screen.get_height(), temp_dir, self.target_count)
        
        if temp_dir == 'down':
            target = (random.choice(vert_start) - lane_offset, 0, temp_dir, self.target_count )

        return target

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
    

    def run_env(self, targets, sensors, buildings):
        
        # pygame setup
        pygame.init()
        self.running = True
        self.clock = pygame.time.Clock()
        global_time = 0

        TARGET = pygame.USEREVENT + 1

        pygame.time.set_timer(TARGET, 250)
        #buildings = self.create_lanes(2,2)

        while self.running:
                # poll for events
            # pygame.QUIT event means the user clicked X to close your window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == TARGET:
                    new_target = self.gen_target()
                    targets.append(Target(new_target[0], new_target[1], new_target[2], id=new_target[3]))
            # fill the screen with a color to wipe away anything from last frame
            self.screen.fill("purple")

            covered_targets = []
            current_energy = 0 # initialize available energy for this moment

            # basic 'buildings' - helps to see the lanes
            for building in buildings:
                pygame.draw.rect(self.screen, (0,0,255), building, 0)

            for target in targets:
                target.move()
                target.draw_target(self.screen)  

            for sensor in sensors:
                region_map = sensor.update_sensor_fov(targets)
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
            global_time += dt

            if global_time % 1 == 0:
                print('The game time is: ', global_time)
        pygame.quit()

        return region_map

    
    