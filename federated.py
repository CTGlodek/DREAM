
import numpy as np

def avg_weights(weights):

    w_total = np.zeros_like(weights[0])

    for w in weights:
        w_total += w

    w_avg = w_total / len(weights)

    print('Federated Learning Triggered')

    return w_avg