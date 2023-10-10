import pandas as pd
import numpy as np

def unique_per_step(df, to_plot=False):
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

