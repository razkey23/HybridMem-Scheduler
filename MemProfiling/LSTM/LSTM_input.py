from sklearn import preprocessing
import numpy as np
import math
from tensorflow.keras.utils import to_categorical
import numpy as np
import csv, math, os, time, sys, pickle, psutil, itertools
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM
from tensorflow.keras.optimizers import Adam, SGD
from keras.callbacks import TerminateOnNaN
from keras.callbacks import ModelCheckpoint
from keras.callbacks import EarlyStopping
from keras.callbacks import Callback
from keras import backend as K
from tensorflow.keras.metrics import TopKCategoricalAccuracy
#from tensorflow.keras.metrics import * as tf.keras.metrics

class LSTM_input:
    def __init__(self, timeseries):
        self.data_series = timeseries
        self.dataX = []
        self.dataY = []
        self.trainX = []
        self.trainY = []
        self.valX = []
        self.valY = []
        self.testX = []
        self.testY = []
        self.trainX_categor = []
        self.trainY_categor = []
        self.valX_categor = []
        self.valY_categor = []
        self.testX_categor = []
        self.testY_categor = []
        self.dataX_in = []
        self.dataY_in = []
        self.weights = []

    def timeseries_to_history_seq(self, history_length):
        dataX, dataY = [], []
        for i in range(len(self.data_series) - history_length):
            self.dataX.append(self.data_series[i: i + history_length])
            self.dataY.append(self.data_series[i + history_length])
        #print("Data X")
        #print(self.dataX)
        #print("Data Y")
        #print(self.dataY)
    
    def split_data(self, ratio):
        samples = np.array(self.dataY).shape[0]
        test_samples = (ratio) * samples
        samples_interval = 1
        if test_samples != 0:
            samples_interval = math.floor(samples / test_samples)
        s = 0
        while s < samples:
            if s % samples_interval == 0:
                self.valX.append(self.dataX[s])
                self.valY.append(self.dataY[s])
                s += 1
                self.testX.append(self.dataX[s])
                self.testY.append(self.dataY[s])
            else:
                self.trainX.append(self.dataX[s])
                self.trainY.append(self.dataY[s])
            s += 1
  
    def to_categor(self, num_classes):
        print(num_classes)
        # shape is [samples, time steps, features
        inter = to_categorical(np.array(self.trainX), num_classes = num_classes)
        self.trainX_categor = np.reshape(inter, (inter.shape[0], inter.shape[1], num_classes))
        inter = to_categorical(np.array(self.valX), num_classes = num_classes)
        self.valX_categor = np.reshape(inter, (inter.shape[0], inter.shape[1], num_classes))
        inter = to_categorical(np.array(self.testX), num_classes = num_classes)
        self.testX_categor = np.reshape(inter, (inter.shape[0], inter.shape[1], num_classes))

        # shape is [samples, features]
        self.trainY_categor = to_categorical(self.trainY, num_classes=num_classes)
        self.valY_categor = to_categorical(self.valY, num_classes=num_classes)
        self.testY_categor = to_categorical(self.testY, num_classes=num_classes)
        #print(self.trainX_categor)

    def prepare(self):
        # shape is [samples, time steps, features]
        self.dataX = np.array(self.dataX)
        self.dataX_in = np.reshape(np.array(self.dataX), (self.dataX.shape[0], self.dataX.shape[1], 1))
        # shape is [samples, features]
        self.dataY = np.array(self.dataY)
        self.dataY_in = np.reshape(np.array(self.dataY), (self.dataY.shape[0], 1))