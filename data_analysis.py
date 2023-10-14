import pandas as pd
import numpy as np

def unique_per_step(df, to_plot=False):
    """
    Creates a df with the number of unique targets being tracked per time step
    """
    df = df.fillna(0)
    unique_df = df.stack().groupby(level=0).apply(lambda x: x.unique().tolist())

    unique_list = np.zeros([len(unique_df),len(max(unique_df,key = lambda x: len(x)))])

    for i,j in enumerate(unique_df):
                unique_list[i][0:len(j)] = j

    unique_count_list = np.count_nonzero(unique_list, axis=1)

    new_df = pd.DataFrame(unique_count_list)

    if to_plot:
        new_df.plot()

    return new_df

def model_losses_df(sensors, to_plot= False):
    """
    Creates a df with the losses from all models passed in
    """
    loss_df = pd.DataFrame()
    
    for i, var in enumerate(sensors):
        loss_df[i] = var.agent.loss_history

    if to_plot:
          loss_df.plot()
    
    return loss_df


def save_models(sensors):
    """
    saves all the models
    """
    for i, var in enumerate(sensors):
        name = 'model_{}.keras'.format(i)
        var.agent.model.save(name)
    
def save_data(tracked, unique_per_step_df, loss_df):
     
     tracked.to_csv( 'tracked_per_timestep.csv')
     unique_per_step_df.to_csv('num_o_unique_per_timestep.csv')
     loss_df.to_csv('model_losses')
     