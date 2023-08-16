import pygame
import numpy as np
from environment import *
from sensor import *
from target import *

# env_testing.py 
# version 0.1 : initial development

env_test = Environment((1280, 720))

#target_list = [((env_test.screen.get_width() / 2), -45, 1) , ((env_test.screen.get_width() / 2)+5, 0, 2)] # fixed target drops x2
target_list = env_test.generate_target_list(5) # generate a batch of targets

# two fixed sensors
sensor_list = [(((env_test).screen.get_width()-125) / 2, env_test.screen.get_height() / 2, 90), (env_test.screen.get_width() / 2, env_test.screen.get_height() / 2, 90)]

# create the environment
target_1, sensor_1 =env_test.create_env(target_list, sensor_list)

# run the simulation
env_test.run_env(target_1, sensor_1)

# pull the tracking info
tracking = env_test.tracked

#print(tracking)

# equalize the array sizes for processing
temp = np.zeros([len(tracking),len(max(tracking,key = lambda x: len(x)))])
for i,j in enumerate(tracking):
    temp[i][0:len(j)] = j

# show the number of targets tracked and their IDs
print('The unique targets tracked: ',np.unique(temp)[1:])
print('The number of unique targets tracked: ', len(np.unique(temp))-1)


