import pygame

import numpy as np
import matplotlib.pyplot as plt

import tensorflow as tf

import random

import config
from sensor import *
from target import *
from agent import *
from federated import *

if config.colab:
    #colab
    import cv2

    import os
    os.environ["SDL_VIDEODRIVER"] = "dummy"

    from google.colab.patches import cv2_imshow
    from google.colab import output

# environment.py 

class Environment:
    def __init__(self,
                 screen_size,
                 show = True):
        self.screen_size= screen_size       # establish the screen size
        self.running = False                # running flag
        if show:
            self.clock = pygame.time.Clock()    # initalize a pygame clock object
            self.screen = pygame.display.set_mode((self.screen_size))   # initialize the screen object
        self.tracked = []                   # a list of lists of the targets that have been tracked by time step
        self.energy = []                    # a list of available energy per time step
        self.energy_total = 0               # initial starting energy
        self.building_width = 0             # building width
        self.building_height = 0            # building hieght
        self.lane_width = 100               # lane width
        self.turn_points = set()         # all points for where a target can turn
        self.target_count = 0               # tracks the total number of targets generated
        self.auto_gen = False               # boolean flag for automatic target generation
        self.sensor_range = 100             # the sensing range for each sensor
        self.max_target = 100               # maximum number of targets at a time
        self.rl = False                     # agent flag
        self.fed_flag = False
        self.fed_freq = 25                # how often the federated update will occur - default 25

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

        targets = []
        sensors = []
        buildings = []
        
        #self.building_width = int((self.screen.get_width() - (self.vert_lanes * self.lane_width)) / (self.vert_lanes+1))# working
        self.building_width = int((self.screen_size[0] - (self.vert_lanes * self.lane_width)) / (self.vert_lanes+1))
        #self.building_height = int((self.screen.get_height() - (self.hort_lanes * self.lane_width)) / (self.hort_lanes + 1)) # working
        self.building_height = int((self.screen_size[1] - (self.hort_lanes * self.lane_width)) / (self.hort_lanes + 1))

        

        # establish locations for all building based on number of lanes and buidling dimensions
        for i in range(self.vert_lanes+1):
            for j in range(self.hort_lanes+1):
                temp = [i*(self.building_width+self.lane_width), j*(self.building_height+self.lane_width), self.building_width, self.building_height]
                buildings.append(temp)

                self.turn_points.add(int(self.building_width + 25)+ i*int(self.building_width+self.lane_width))
                self.turn_points.add(int(self.building_width + 75)+ i*int(self.building_width+self.lane_width))
                self.turn_points.add(int(self.building_height +25)+ j*int(self.building_height+self.lane_width))
                self.turn_points.add(int(self.building_height +75)+ j*int(self.building_height+self.lane_width))

        # all the apots where a target can turn
        #for i in range(self.vert_lanes):
            #for j in range(self.hort_lanes):    
                #self.turn_points.add(int(self.building_width + 25)+ i*int(self.building_width+self.lane_width))
                #self.turn_points.add(int(self.building_width + 75)+ i*int(self.building_width+self.lane_width))
                #self.turn_points.add(int(self.building_height +25)+ j*int(self.building_height+self.lane_width))
                #self.turn_points.add(int(self.building_height +75)+ j*int(self.building_height+self.lane_width))
                #print('turning points: ', self.turn_points)
        
        if num_o_targets > 0:

            #target_info = self.generate_target_list(num_o_targets)
            
            # generate targets if provided in a list format
            # can be used for specific testing
            for i in range(num_o_targets):
                targets.append(self.gen_target())
                #self.target_count += 1
        else:
            self.auto_gen = True

        # Generate sensors based on user defined list
        for sensor in sensor_info:
            # temporarily fixing dqn as the agent type
            if sensor[3] == True:
            
                temp_sensor = Sensor(sensor[0],sensor[1],
                                    fov=sensor[2], 
                                    coverage_range=self.sensor_range, 
                                    agent_type=Agent((self.sensor_range*2,self.sensor_range*2),(3)))
            
                temp_sensor.agent.dqn()
                self.rl_flag = True

            elif sensor[3] == False:
                temp_sensor = Sensor(sensor[0],sensor[1],
                                    fov=sensor[2], 
                                    coverage_range=self.sensor_range, 
                                    agent_type=None)
                self.rl_flag = False
            """
            #works
            temp_sensor = Sensor(sensor[0],sensor[1],
                                    fov=sensor[2], 
                                    coverage_range=self.sensor_range, 
                                    agent_type=Agent((self.sensor_range*2,self.sensor_range*2),(3)))
            
            temp_sensor.agent.dqn()
            """

            sensors.append(temp_sensor)
            self.energy_total = self.energy_total + temp_sensor.energy_start

        print('Total inital sensor energy level: ', self.energy_total)

        return targets, sensors, buildings

    def gen_target(self):
        """
        Creates a single target object

        Variables:
            none
        
        Returns:
            target (object)

        """
        self.target_count += 1

        list_o_directions = ['right', 'left', 'down', 'up']

        # lists of the potential starting target locations
        hor_start = []
        vert_start = []

        # generate a list of possible starting positions for the targets based on the number of lanes and building locations.
        for i in range(self.vert_lanes):
            hor_temp = i*(self.building_height + self.lane_width) + self.building_height + self.lane_width/2
            hor_start.append(hor_temp)

        for i in range(self.hort_lanes):
            vert_temp = i*(self.building_width + self.lane_width) + self.building_width + self.lane_width/2
            vert_start.append(vert_temp)
        
        #print('hor start: ', hor_start)
        #print('vert start: ', vert_start)

        lane_offset = 25

        temp_dir = random.choice(list_o_directions) # pick a random starting point
        
        if temp_dir == 'right':    
            target = (0 , random.choice(hor_start) + lane_offset, temp_dir, self.target_count )

        if temp_dir == 'left':
            #target = (self.screen.get_width() , random.choice(hor_start) - lane_offset, temp_dir, self.target_count) # working
            target = (self.screen_size[0] , random.choice(hor_start) - lane_offset, temp_dir, self.target_count)
        if temp_dir == 'up':
            #target = (random.choice(vert_start) + lane_offset, self.screen.get_height(), temp_dir, self.target_count)#working
            target = (random.choice(vert_start) + lane_offset, self.screen_size[1], temp_dir, self.target_count)
        if temp_dir == 'down':
            target = (random.choice(vert_start) - lane_offset, 0, temp_dir, self.target_count )

        return Target(target[0], target[1], target[2], id=target[3])
    
    def prepopoulate(self):
        
        prepop_targets =[]

        for i in range(self.max_target):
            pp_target = self.gen_target()

            #rand_pos_h = random.randint(0, self.screen.get_height()) # working
            #rand_pos_w = random.randint(0, self.screen.get_width()) # working
            rand_pos_h = random.randint(0, self.screen_size[1])
            rand_pos_w = random.randint(0, self.screen_size[0])

            if pp_target.direction == 'right':
                pp_target.position.x += rand_pos_w
            
            if pp_target.direction == 'left':
                pp_target.position.x -= rand_pos_w

            if pp_target.direction == 'down':
                pp_target.position.y += rand_pos_h # just a horizontal movement for initial testing

            if pp_target.direction == 'up':
                pp_target.position.y -= rand_pos_h # just a horizontal movement for initial testing

            prepop_targets.append(pp_target)

        return prepop_targets

    def delete_target(self, target, targets):
        """
        Removes a target object form teh tragets list if it is beyond ht ebounds of the screen

        Variables:
        target (object):    the target object being evaluated
        targets (list):     the list of targets

        returns:
        targets (list):     the list of targets

        """
        if target.position.x > (self.screen_size[0] + 50) or target.position.x < -25 or target.position.y > (self.screen_size[1] + 50) or target.position.y < -25: 
            #print(target.position.x)
            #print(target.position.y)
            targets.remove(target)
        
        return targets

    def env_stats(self, plot=False):

        """
        Provides the an ndarry of the targets that were tracked and available energy per time step. There is an option for plotting these data. 

        Variables:
            plot (boolean): the flag for ploting the data
        
        Returns:
            track_temp (ndarray): the number of targets tracked per time step
            energy_temp (list): a list of the energy available per time step
        
        """
        # equalize the array sizes for processing
        track_temp = np.zeros([len(self.tracked),len(max(self.tracked,key = lambda x: len(x)))])
        energy_temp = self.energy

        for i,j in enumerate(self.tracked):
            track_temp[i][0:len(j)] = j

        unique_tracked = np.unique(track_temp)[1:]
        num_unique_tracked = len(np.unique(track_temp))-1
        total_targets = self.target_count
        # show the number of targets tracked and their IDs
        print('The unique targets tracked: ',unique_tracked) # excludes the zero used for padding the arrays.
        print('The number of unique targets tracked: ', num_unique_tracked) # -1 so we dont count the zero
        print('The total number of targets generated: ', total_targets)
        if plot:

            fig, (ax1, ax2) = plt.subplots(1,2, figsize=(10,5))
            #fig.suptitle('Vertically stacked subplots')
            ax1.plot(np.count_nonzero(track_temp, axis=1));
            ax1.set_title('Targets Tracked')
            ax2.plot(energy_temp);
            ax2.set_title('Total Energy Available')

        return track_temp, energy_temp, unique_tracked, num_unique_tracked, total_targets
    

    def run_env(self, targets, sensors, buildings,fed, explore, train, test, episode = 0, reload = None, show = True):
        
        """
        The main function for running the simulation.

         Variables:
            targets (list): a list of target objects
            sensors (list): a list of sensor objects
            buildings(list): a list of buildings - specifically the location for each to be drawn
        
        Returns:
            region_map (2d numpy array): returns the last region map for the last sensor to allow for testing - this will be removed later
        """
        episode = episode

        # the amount of training without visuals
        explore_limit = explore
        train_limit = train
        test_limit = test

        if show:
            # pygame setup
            pygame.init()
            pygame.display.set_caption("2D Environment: Exploring")
            
            self.clock = pygame.time.Clock()
            global_time = 0

            # initalizing the font
            font = pygame.font.Font('freesansbold.ttf', 32)
            time_step_text = 'Time Step: ' + str(episode) # used to be len(self.tracked) allows for additional training 
            text = font.render(time_step_text, True, (0, 255, 0), (0, 0, 128)) # green , blue
            # create a rectangular object for the text surface object
            textRect = text.get_rect()
            # set the center of the rectangular object.
            textRect.center = (150, 50)
        
        self.running = True
        
        if fed == True:
            self.fed_flag = True

        # Allow for inital training
        sensor_method = 'explore'

        if not reload == None:
            for i, sensor in enumerate(sensors):
                sensor.agent.model = tf.keras.models.load_model(reload[0])
                print('Saved Model loaded successfully')
        
        # prepopulates upto the maximum number of targets prior
        targets = self.prepopoulate()
        
        # setting the seed
        random.seed(42) 
        np.random.seed(42)

        while self.running:

            if self.rl_flag:
                # poll for events
                if len(self.tracked) > explore_limit:
                    sensor_method = 'directed'
                    if show:
                        pygame.display.set_caption("2D Environment: DQN Directed - Training")

                # fill the screen with a color to wipe away anything from last frame
                if episode > train_limit and show:
                    self.screen.fill("purple")
                    pygame.display.set_caption("2D Environment: DQN Directed - Testing")

            elif self.rl_flag == False:
                #sensor_method = 'random'
                sensor_method = None
                if show:
                    self.screen.fill("purple")
                    pygame.display.set_caption("2D Environment: Random")

            if episode >= test_limit:
                self.running = False

            if self.auto_gen:
                if len(targets) < self.max_target:
                        new_target = self.gen_target()
                        targets.append(new_target)

            if show: 
                for event in pygame.event.get():
                    # pygame.QUIT event means the user clicked X to close your window
                    if event.type == pygame.QUIT:
                        self.running = False

            covered_targets = []
            current_energy = 0 # initialize available energy for this moment
            episode += 1 

            # basic 'buildings' - helps to see the lanes
            if episode > train_limit and show:
                for building in buildings:
                    pygame.draw.rect(self.screen, (0,0,255), building, 0)

            # trigger federated learning 
            if episode % self.fed_freq == 0 and self.fed_flag:
                weights = []
                for sensor in sensors:
                    w_temp = sensor.agent.grab_weights()
                    weights.append(w_temp)

                w_avg = avg_weights(weights)

                for sensor in sensors:
                    sensor.agent.update_weights(w_avg)

            for target in targets:
                target.move()
                target.turn(self)
                if episode > train_limit and show:
                    target.draw_target(self.screen)  
                self.delete_target(target, targets)

            for sensor in sensors:
                region_map = sensor.update_sensor_fov(targets, episode, method=sensor_method)
                #print(type(sensor.agent.model))
                sensor.update_energy()
                
                current_energy = current_energy + sensor.energy # tallies the energy

                if len(sensor.detected) > 0: 
                    for var in sensor.detected:
                        covered_targets.append(var.id)

                if episode > train_limit and show:
                    sensor.draw_sensors(self.screen)
                    
            # appends all the targets, by id, (if any) that were tracked in this round
            self.tracked.append(covered_targets)

            # appends the total available energy in this moment
            self.energy.append(current_energy)
            
            if show:
                time_step_text = 'Time Step: ' + str(episode)
                text = font.render(time_step_text, True, (0, 255, 0), (0, 0, 128)) # green , blue
                self.screen.blit(text, textRect)
            elif episode % 100 == 0:
                print('Time Step: ', episode)

            if episode > train_limit and show:
                
                if config.colab:
                    # colab
                    image = pygame.surfarray.array3d(self.screen)
                    image = image.transpose([1, 0, 2])
                    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                    
                    output.clear(wait=True)
                    cv2_imshow(image)

                else:
                    # flip() the display to put your work on screen
                    pygame.display.flip()
                    pygame.display.update()

            if show:
                dt = self.clock.tick(60) / 1000
                global_time += dt

                if global_time % 25 == 0:
                    print('The game time is: ', global_time)
        if show:        
            pygame.quit()
        print('Total number of active targets: ', len(targets))
        print('Total length of this episode: ', episode)
        return region_map, targets, sensors

    def run_env_test(self, targets, sensors, buildings,fed, explore, train, test, episode = 0, reload = None):
            
            """
            The main function for running the simulation.

            Variables:
                targets (list): a list of target objects
                sensors (list): a list of sensor objects
                buildings(list): a list of buildings - specifically the location for each to be drawn
            
            Returns:
                region_map (2d numpy array): returns the last region map for the last sensor to allow for testing - this will be removed later
            """
            
            self.running = True

            if fed == True:
                self.fed_flag = True

            episode = episode

            # the amount of training without visuals
            explore_limit = explore
            train_limit = train
            test_limit = test

            # Allow for inital training
            sensor_method = 'explore'

            if not reload == None:
                for sensor in sensors:
                    sensor.agent.model = tf.keras.models.load_model(reload)
                    print('Saved Model loaded successfully')
            
            # prepopulates upto the maximum number of targets prior
            targets = self.prepopoulate()
            
            # setting the seed
            random.seed(42) 
            np.random.seed(42)

            while self.running:

                if self.rl_flag:
                    # poll for events
                    if len(self.tracked) > explore_limit:
                        sensor_method = 'directed'

                # Override Sensor Method if needed
                #sensor_method = 'random'

                elif self.rl_flag == False:
                    sensor_method = 'random'

                if episode >= test_limit:
                    self.running = False

                if self.auto_gen:
                    if len(targets) < self.max_target:
                            new_target = self.gen_target()
                            targets.append(new_target)
                
                covered_targets = []
                current_energy = 0 # initialize available energy for this moment
                episode += 1 

                # trigger federated learning 
                if episode % self.fed_freq == 0 and self.fed_flag:
                    weights = []
                    for sensor in sensors:
                        w_temp = sensor.agent.grab_weights()
                        weights.append(w_temp)

                    w_avg = avg_weights(weights)

                    for sensor in sensors:
                        sensor.agent.update_weights(w_avg)

                for target in targets:
                    target.move()
                    target.turn(self)
                    self.delete_target(target, targets)

                for sensor in sensors:
                    region_map = sensor.update_sensor_fov(targets, episode, method=sensor_method)
                    #print(type(sensor.agent.model))
                    sensor.update_energy()
                    
                    current_energy = current_energy + sensor.energy # tallies the energy

                    if len(sensor.detected) > 0: 
                        for var in sensor.detected:
                            covered_targets.append(var.id)
                        
                # appends all the targets, by id, (if any) that were tracked in this round
                self.tracked.append(covered_targets)

                # appends the total available energy in this moment
                self.energy.append(current_energy)
                
                if episode % 100 == 0:
                    print('Time Step: ', episode)

            print('Total number of active targets: ', len(targets))
            print('Total length of this episode: ', episode)
            return region_map, targets, sensors
    
    