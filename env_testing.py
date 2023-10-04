
from environment import *
from sensor import *
from target import *

# env_testing.py 
# version 0.2 : initial development 

env_test = Environment((1200, 800))
#env_test = Environment((800, 600))
#env_test = Environment((600, 400))

#target_list = env_test.generate_target_list(10) # generate a batch of targets

# 4 fixed sensors at the intersection
#sensor_list = [(650,450, 90), (550,450, 90), (550,350, 90), (650,350, 90)]
#sensor_list = [(650,450, 90)] # bottom right 1x1 
sensor_list = [(650,450, 90), (550,350, 90)] # bottom right & top left 1x1 
# create the environment
target_1, sensor_1, buildings =env_test.create_env(0, # number of targets 
                                                   sensor_list, # list of sensor positions
                                                   1, # number of vertical lanes
                                                   1) # number of horizontal lanes

# run the simulation
env_test.run_env(target_1, sensor_1, buildings)

env_test.env_stats()



