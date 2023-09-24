import tensorflow as tf
import numpy as np
import random

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Activation

class Agent:
    def __init__(self,
                 state_space,
                 action_space,
                 model=None):
        self.state_space = state_space      # to accoutn for batch size
        self.action_space = action_space    #to account for batch size
        self.model = model
        self.s = np.zeros(state_space)          # previous state
        self.a = np.zeros(action_space)         # action taken from previous state
        self.s_prime = np.zeros(state_space)    # state after action (current)
        self.a_prime = None
        self.gamma = .3                         # gamma is the discount on future rewards

    def dqn(self):
        #learning_rate = 0.001

        model = Sequential([
            Conv2D(32,8, strides = 2, activation='relu', input_shape=(200,200,1)),
            Conv2D(64,4,strides = 2, activation='relu'),
            Conv2D(64,3,strides = 1, activation='relu'),
            Flatten(),
            Dense(self.action_space, activation='linear')
        ])

        model.compile(loss='mse', #'huber'
                      optimizer=tf.keras.optimizers.Adam(),
                      metrics=['MSE'])
        
        self.model = model
    
    def next_move(self, method):
        
        best_action = np.argmax(self.a)

        chance = random.randint(1,100)

        if chance > 85 or method == 'explore':
            best_action = random.randint(0,2)

        move = 0

        if best_action == 1: move = 0

        elif best_action == 0: move = -5

        elif best_action == 2: move = 5

        return move
    