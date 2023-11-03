
from environment import *
from sensor import *
from target import *
from data_analysis import *

# env_testing.py 
# version 0.2 : initial development 

show_vis = True

env_test = Environment((1200, 800), show = show_vis)
#env_test = Environment((800, 600))
#env_test = Environment((600, 400))

rl_agent = False
federated_learning = False

saving = False

episode_start = 0
episode_end = 2000

#target_list = env_test.generate_target_list(10) # generate a batch of targets

# 4 fixed sensors at the intersection
#sensor_list = [(650,450, 90), (550,450, 90), (550,350, 90), (650,350, 90)]
sensor_list = [(325,200, 90, rl_agent), (760,300, 90, rl_agent), (425, 600,90, rl_agent)] # 2x2 
#sensor_list = [(650,450, 90, rl_agent), (550,350, 90, rl_agent)] # bottom right & top left 1x1, True indicates that it should use a DQN agent
# create the environment
target_1, sensor_1, buildings =env_test.create_env(0, # number of targets 
                                                   sensor_list, # list of sensor positions
                                                   2, # number of vertical lanes
                                                   2) # number of horizontal lanes

reload = None
#reload = 'test_model_0_0k_1000k.keras'
visualize = True
# run the simulation

if visualize:
    ep_map, ep_targets, ep_sensors = env_test.run_env(target_1, 
                                                        sensor_1, 
                                                        buildings, 
                                                        fed = federated_learning,   # federated learning flag
                                                        explore = 1,  # length of time the agents will freely explore
                                                        train = 1,     # length of time the agents will train with decaying epsilon
                                                        test = episode_end,
                                                        episode = episode_start,
                                                        reload = reload,
                                                        show = show_vis)    # length of time the agents will tested

else:
    # run the simulation # started at 11:04
    ep_map, ep_targets, ep_sensors = env_test.run_env_test(target_1, 
                                                        sensor_1, 
                                                        buildings, 
                                                        fed = federated_learning,   # federated learning flag
                                                        explore = 1,  # length of time the agents will freely explore
                                                        train = 1,     # length of time the agents will train with decaying epsilon
                                                        test = episode_end,
                                                        episode = episode_start,
                                                        reload = reload)    # length of time the agents will tested


#env_test.env_stats()

if saving:
    tracked_df, _, _, _, _ =env_test.env_stats(plot=True);
    tracked_df = pd.DataFrame(tracked_df)
    unique_df = unique_per_step(tracked_df, to_plot=True)
    losses = model_losses_df(ep_sensors, to_plot=False);

    tracked_df.to_csv( 'tracked_per_timestep_{}_{}.csv'.format(episode_start,episode_end))
    unique_df.to_csv('num_o_unique_per_timestep_{}_{}.csv'.format(episode_start,episode_end))
    losses.to_csv('losses_per_timestep_{}_{}.csv'.format(episode_start,episode_end))

    # save the models
    for i, var in enumerate(ep_sensors):
        var.agent.model.save('test_model_{}_{}_{}.keras'.format(i, episode_start, episode_end))



