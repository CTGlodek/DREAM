import pygame
import math

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
                 energy=1000,
                 speed = 2, # not used currently
                 mode='idle'):

        self.position = pygame.Vector2(x,y)     # Vector 2 object
        self.radius = radius                    # sensor radius
        self.coverage_range = coverage_range    # how far the sensors can detect targets
        self.comm_range = comm_range            # how far the sensor can communicate with other sensors
        self.fov = fov                          # how large is the field of view - default of 90
        self.energy = energy                    # amount of energy remaining
        self.energy_start = 1000                # initial amount of energy
        self.speed = speed                      # speed 
        self.mode = mode                        # the mode of the sensor: idle, active, wake_up, and sleep
        self.angle = 270                        # angle between sensor and the target being tracked actively # 270 used for initialization
        self.detected = []                      # targets that are currently detected

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
                    #pygame.draw.line(screen, (0, 0, 0), (self.position.x, self.postion.y), target, 2)
                    pygame.draw.line(screen, (0, 0, 0), self.position, target.position, 2)
            self.position.angle_to()
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

        if method == 'directed':
            self.angle = angle_update

        # Clear the detected_targets list for the current sensor
        self.detected = []

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
                    self.mode = 'active'
                    #print('active')
                    #break  # use if single target tracking is wanted, else it will track multiple targets

        if len(self.detected) == 0:
            # Mark the sensor as inactive and clear the detected_targets list
            self.mode = 'idle'
            self.detected = []
    
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
            self.energy = self.energy - 1
        
        # energy consumption when active - this includes movement
        if self.mode == 'active':
            self.energy = self.energy - 2
        
        # wake up from sleep  # not used yet
        if self.mode == 'wake_up':
            self.energy = self.energy - 5
        
        # if the energy level drops to zero, or below, set the energy to 0 and mode to sleep
        if self.energy <= 0:
            self.energy = 0
            self.mode = 'sleep'


        
