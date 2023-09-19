import tensorflow as tf
import numpy as np

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
        self.s = np.zeros(state_space)                       # previous state
        self.a = np.zeros(action_space)                     # action taken from previous state
        self.s_prime = None                 # state after action (current)
        self.a_prime = None

    def dqn(self):
        #learning_rate = 0.001

        model = Sequential([
            Conv2D(10,10, strides = 2, activation='relu', input_shape=(100,100,1)),
            Conv2D(10,10,strides = 2, activation='relu'),
            Flatten(),
            Dense(self.action_space, activation='softmax')
        ])

        model.compile(loss='categorical_crossentropy',
                      optimizer=tf.keras.optimizers.Adam(),
                      metrics=['accuracy'])
        
        self.model = model
    