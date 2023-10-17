import pygame
import math
import numpy as np
from agent import *
from federated import *

# sensor.py 
# version 0.2 : initial development

class Sensor:

    def __init__(self,
                 x,
                 y,
                 radius=20,
                 coverage_range=100,
                 comm_range=100,
                 fov=90,
                 energy=10000,
                 speed = 2, # not used currently
                 mode='idle',
                 agent_type = None):

        self.position = pygame.Vector2(x,y)     # Vector 2 object
        self.radius = radius                    # sensor radius
        self.coverage_range = coverage_range    # how far the sensors can detect targets
        self.comm_range = comm_range            # how far the sensor can communicate with other sensors
        self.fov = fov                          # how large is the field of view - default of 90
        self.energy = energy                    # amount of energy remaining
        self.energy_start = energy              # initial amount of energy
        self.speed = speed                      # speed 
        self.mode = mode                        # the mode of the sensor: idle, active, wake_up, and sleep
        self.angle = 180                        # angle between sensor and the target being tracked actively # 270 used for initialization
        self.detected = []                      # targets that are currently detected
        self.region_map = np.zeros((self.coverage_range, self.coverage_range)) # initialize the region map
        self.agent = agent_type

        # Function to draw each sensor as a disk with lines representing the active FOV
    def draw_sensors(self, screen):
        """
        Function draws the sensor, FOV, and battery level on the provided display object

        Variables:
        screen (pygame display object)

        returns:
        None

        """

        # if active or idle, show the FOV
        if self.mode == 'active' or self.mode == 'idle':
            # Draw the sensor as a solid blue circle with a black border
            pygame.draw.circle(screen, (0, 0, 255), self.position, self.radius)
            pygame.draw.circle(screen, (0, 0, 0), self.position, self.radius, 2)

            # Draw the active FOV as a filled sector in white color
            angle_start = math.radians(self.angle - self.fov / 2)
            angle_end = math.radians(self.angle + self.fov / 2)

            # Use two points to create a triangle to draw the filled sector
            p1 = (self.position.x, self.position.y)
            p2 = (self.position.x + int(self.radius * math.cos(angle_start)), self.position.y + int(self.radius * math.sin(angle_start)))
            p3 = (self.position.x + int(self.radius * math.cos(angle_end)), self.position.y + int(self.radius * math.sin(angle_end)))

            # Draw the filled sector as a triangle
            pygame.draw.polygon(screen, (255, 255, 255), [p1, p2, p3])


        if self.mode == 'active': 

            # Draw line connecting sensor to target within FOV (only if sensor is covering the target)
            for target in self.detected:
                distance_to_target = self.position.distance_to(target.position)
                if distance_to_target <= self.coverage_range:
                    pygame.draw.line(screen, (0, 0, 0), self.position, target.position, 2)

        # Check if the sensor is in idle mode and draw the entire disk in dark gray
        if self.mode == 'idle':
            surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(surface,(100,100,100,150),self.position,self.radius) #(30,224,33,100) green
            screen.blit(surface, (0,0))
        
        # Check if the sensor is in sleep mode and draw the entire disk in dark gray
        if self.mode == 'sleep':
            pygame.draw.circle(screen, (100, 100, 100), self.position, self.radius) # (100,100,100) sleep mode color?

        # Draw energy level as a battery next to the sensor
        battery_width = 8
        battery_height = self.radius * 2
        battery_x = self.position.x + self.radius + 5
        battery_y = self.position.y - self.radius
        battery_level = int((self.energy / self.energy_start) * battery_height)

        # Calculate the battery color based on the battery level
        if battery_level > 0:
            battery_color = (0, 255, 0)  
        else:
            battery_color = (255, 0, 0)

        pygame.draw.rect(screen, (0, 0, 0), (battery_x, battery_y, battery_width, battery_height), 1)

        if battery_level > 0:
            pygame.draw.rect(screen, battery_color, (battery_x + 1, battery_y + battery_height - battery_level + 1, battery_width - 2, battery_level - 2))
        else:
            pygame.draw.rect(screen, battery_color, (battery_x, battery_y, battery_width, battery_height))
            self.mode = 'sleep'
            pygame.draw.circle(screen, (100, 100, 100), self.position, self.radius)

        # Check if the sensor is a cluster head and draw the entire disk in pink
        #if sensor.get("is_cluster_head"):
            # Draw the filled sector as a triangle for cluster heads
            #pygame.draw.polygon(screen, (255, 192, 203), [p1, p2, p3])

    def update_sensor_fov(self, 
                          targets,
                          episode,
                          method=None,
                          angle_update=270):
        """
        Function to update sensor angles and active FOV based on the target's position 

        Variables:
            targets (list)      : a list of target objects 
            method (string)     : indicates the method to be used for updating the sensor.
                                    None:  Tracks targets that enter the FOV until they exit - No heuristics or other logic
                                    'directed': updates the fov based on user defined angle_update.
            angle_update (int)  : the user defined angle for the sensor to be updated

        returns:
            None
        
        """
        if method == None:
            # updates the angle if detected is not empty
            if len(self.detected) > 0: 
                self.angle = math.degrees(math.atan2(self.detected[0].position.y - self.position.y, self.detected[0].position.x - self.position.x)) % 360 

        if method == 'intializing':
            self.mode = 'sleep'
        
        if method == 'random':
            move = random.randint(0,2)

            if move == 0: self.angle += -5

            elif move == 2: self.angle += 5

        if method == 'fixed':
            self.angle = self.angle

        # updates the fov angle based on the user define value
        if method == 'directed' or method == 'explore':
            
            if self.mode == 'sleep':
                self.mode = 'idle'

            angle_update = self.agent.next_move(episode)

            self.angle += angle_update

        # Clear the detected_targets list for the current sensor
        self.detected = []

        if not self.mode == 'sleep':

            # resets the region map 2d array to zeros
            self.region_map = np.zeros((self.coverage_range*2, self.coverage_range*2)) 
            
            # Loop through all targets and check if they are within the coverage distance of the sensor and within FOV
            for target in targets:

                distance_to_target = self.position.distance_to(target.position)
                #print('distance to: ', distance_to_target )

                # Check if the target is within the sensor's 90-degree FOV
                if distance_to_target <= self.coverage_range:
                    angle_to_target = math.degrees(math.atan2(target.position.y - self.position.y, target.position.x - self.position.x)) % 360

                    # Calculate the angle difference between the sensor and the target
                    angle_diff = (angle_to_target - self.angle + 360) % 360

                    # Check if the target is within the sensor's FOV
                    if angle_diff <= self.fov/2 or angle_diff >= (360-self.fov/2): 
                        self.detected.append(target)  # Convert to a tuple
                        location_temp = target.position - self.position # identify its location

                        #print(location_temp)

                        # update the region map with the targets location only if it is in the FOV
                        self.region_map[int(location_temp.x + 100), int(location_temp.y + 100)] = 1
                        self.mode = 'active'

                        #break  # use if single target tracking is wanted, else it will track multiple targets
            ##################################################
            #### it is fitting the data 
            ###################################################
            if self.agent:
                # update s with the state from which the action was chosen
                self.agent.s = self.agent.s_prime

                # update s_prime to the post action
                self.agent.s_prime = self.region_map

                # get future action prob
                self.agent.a_prime = self.agent.model.predict(np.expand_dims(self.agent.s_prime, axis=0))[0]
                
                # calculate the reward (without discount) and update the qtable

                # location of the best action
                idx = np.argmax(self.agent.a)

                # current Q(s|a) value
                current_val = np.max(self.agent.a)
                #self.agent.a[idx] = len(self.detected) # update to averaged sum 

                if self.mode == 'idle':
                    #self.agent.a[idx] = current_val + self.agent.alpha * (-1 + self.agent.gamma * np.max(self.agent.a_prime) - current_val)
                    reward = -1
                if self.mode == 'active':
                    # calculate the reward with discounted future reward and update the qtable
                    #self.agent.a[idx] = current_val + self.agent.alpha * (len(self.detected) + self.agent.gamma * np.max(self.agent.a_prime) - current_val)
                    reward = len(self.detected)

                # bellman equation
                self.agent.a[idx] = current_val + self.agent.alpha * (reward + self.agent.gamma * np.max(self.agent.a_prime) - current_val)         

                loss = self.agent.model.fit(np.expand_dims(self.agent.s, axis=0), np.expand_dims(self.agent.a, axis=0), verbose=0)
                
                self.agent.loss_history.append(loss.history['loss'][0])

                #print(loss.history['loss'])

                self.agent.a = self.agent.a_prime

            ###################################################
            if len(self.detected) == 0:
                # Mark the sensor as inactive and clear the detected_targets list
                self.mode = 'idle'
                self.detected = []
        # return the region map for use in a learning model
        return self.region_map
    
    def update_energy(self):
        """
        Updates the energy used based on the sensors mode

        Variables:
            None

        Returns:
            None

        """
        # initial energy consumption based on modes. Maybe update later with additional logic

        # initial energy consuption when idle
        if self.mode == 'idle':
            self.energy = self.energy - .1
        
        # energy consumption when active - this includes movement
        if self.mode == 'active':
            self.energy = self.energy - .2
        
        # wake up from sleep  # not used yet
        if self.mode == 'wake_up':
            self.energy = self.energy - 5
        
        # if the energy level drops to zero, or below, set the energy to 0 and mode to sleep
        if self.energy <= 0:
            self.energy = 0
            self.mode = 'sleep'


        
