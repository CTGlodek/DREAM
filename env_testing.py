import pygame
import numpy as np
from environment import *
from sensor import *
from target import *

# env_testing.py 
# version 0.1 : initial development - saved as v_0_1 files

env_test = Environment((1200, 800))

#target_list = [((env_test.screen.get_width() / 2), -45, 1) , ((env_test.screen.get_width() / 2)+5, 0, 2)] # fixed target drops x2
target_list = env_test.generate_target_list(5) # generate a batch of targets

# two fixed sensors
#sensor_list = [(((env_test).screen.get_width()-125) / 2, env_test.screen.get_height() / 2, 90), (env_test.screen.get_width() / 2, env_test.screen.get_height() / 2, 90)]
# 4 fixed sensors at the intersection
sensor_list = [(650,450, 90), (550,450, 90), (550,350, 90), (650,350, 90)]

# create the environment
target_1, sensor_1 =env_test.create_env(target_list, sensor_list)

# run the simulation
env_test.run_env(target_1, sensor_1)

env_test.env_stats()



