import tensorflow as tf
import numpy as np

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Flatten, Activation

class Agent:
    def __init__(self,
                 state_space,
                 action_space,
                 method):
        self.state_space = state_space
        self.action_space = action_space
        self.method = method

    def dqn(self):
        #learning_rate = 0.001

        model = Sequential([
            Conv2D(10,10, strides = 2, activation='relu', input_shape=self.state_space),
            Conv2D(10,10,strides = 2, activation='relu'),
            Flatten(),
            Dense(self.action_space, activation='softmax')
        ])

        model.compile(loss='categorical_crossentropy',
                      optimizer=tf.keras.optimizers.Adam(),
                      metrics=['accuracy'])
        
        return model
    