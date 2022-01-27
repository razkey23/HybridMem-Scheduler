'''
    This class is used to deploy a per-page LSTM model
    First the input should be configured using the LSTM_input class like this
        1. Input should be page-counts per scheduling interval 
            cnts = prof.hmem.page_list[pages_ordered[0]].oracle_counts_binned_ep
            input = LSTM_input(cnts)
        2. Timeseries should be converted to history sequence like this
            input.timeseries_to_history_seq(history_length)
        3. Then data should be split
            input.split_data(ratio)
        4. Find number of classes and use to_categor for the input (convert to np.array e.g. [1,0...,0] belongs to first class)
            num_classes = max(set(cnts))+1
            input.to_categor(num_classes)
    Input is now ready to be fed into the LSTM
        1. Initiliaze the LSTM 
            model = LSTM_model(input)
        2.  Create it and then train it
            model.create(256, 0.00001, 0, history_length, num_classes)
            model.train()
        3. Infer it 
            model.predict()
            
'''


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


# CUSTOM LOSS
def weighted_categorical_crossentropy(weights):
    '''
        A weighted version of keras.objectives.categorical_crossentropy
    
        Variables:
            weights: numpy array of shape (C,) where C is the number of classes
    
        Usage:
            weights = np.array([0.5,2,10]) # Class one at 0.5, class 2 twice the normal weights, class 3 10x.
            loss = weighted_categorical_crossentropy(weights)
            model.compile(loss=loss,optimizer='adam')
    '''
    weights = K.variable(weights)
    def loss(y_true, y_pred):
        # scale predictions so that the class probas of each sample sum to 1
        y_pred /= K.sum(y_pred, axis=-1, keepdims=True)
        # clip to prevent NaN's and Inf's
        y_pred = K.clip(y_pred, K.epsilon(), 1 - K.epsilon())
        # calc
        loss = y_true * K.log(y_pred) * weights
        loss = -K.sum(loss, -1)
        return loss
    return loss





class LSTM_model:
    def __init__(self, input):
        self.input = input
        self.model = None

    def create(self, layers, learning_rate, dropout, history_length, num_classes,weights):
        self.model = Sequential()
        self.model.add(LSTM(layers, input_shape=(history_length, num_classes), return_sequences=True, recurrent_dropout=dropout))
        #self.model.add(LSTM(layers, return_sequences=True, recurrent_dropout=dropout))
        self.model.add(LSTM(layers))
        self.model.add(Dense(num_classes, activation='relu')) #not softmax
  
        # Optimizer, loss function, accuracy metrics
        #metrics=['categorical_accuracy']
        #tf.keras.metrics.
        #self.model.compile(optimizer=Adam(lr=learning_rate), loss=weighted_categorical_crossentropy(weights),metrics=[TopKCategoricalAccuracy(k=2)])
        self.model.compile(optimizer=Adam(lr=learning_rate), loss=weighted_categorical_crossentropy(weights),metrics ='categorical_accuracy')
        #self.model.compile(optimizer=Adam(lr=learning_rate), loss='mean_squared_error',metrics ='categorical_accuracy')
        #self.model.compile(optimizer=SGD(lr=learning_rate), loss=weighted_categorical_crossentropy(weights),metrics=[TopKCategoricalAccuracy(k=3)])
        #self.model.compile(optimizer=SGD(lr=learning_rate), loss=weighted_categorical_crossentropy(weights),metrics ='categorical_accuracy')
        #self.model.compile(optimizer=Adam(lr=learning_rate), loss = 'mean_squared_error')

        print (self.model.summary())
    
    def train(self):

        self.model.fit(self.input.trainX_categor, self.input.trainY_categor, batch_size=len(self.input.trainX_categor),epochs = 100, validation_data=(self.input.valX_categor, self.input.valY_categor))
        #self.model.fit(self.input.dataX_in, self.input.dataY_in, epochs = 100)
        #self.model.save("lstm_page_539")
    
    def infer(self):
        predictY = self.model.predict(self.input.trainX_categor)
        print("Predict Y")
        print (predictY)
        
        dataY = np.array([np.argmax(x) for x in self.input.trainY_categor])
        predictY = np.array([np.argmax(x) for x in predictY])
        return dataY,predictY

    def calculate_prediction_error(self, dataY, predictY):
        print (dataY.shape, predictY.shape)
        err = 0.0
        dataY = np.array([np.argmax(x) for x in dataY])
        predictY = np.array([np.argmax(x) for x in predictY])
        for i in range(0, dataY.shape[0]):
            if dataY[i] != predictY[i]:
                err += 1
        error = (err / dataY.shape[0]) * 100
        return error












class LSTM_model:
    def __init__(self, input):
        self.input = input
        self.model = None

    def create(self, layers, learning_rate, dropout, history_length, num_classes):
        self.model = Sequential()
        self.model.add(LSTM(layers, input_shape=(history_length, num_classes), return_sequences=True, recurrent_dropout=dropout))
        self.model.add(LSTM(layers))
        self.model.add(Dense(num_classes, activation='softmax')) #not softmax
  
        # Optimizer, loss function, accuracy metrics
        self.model.compile(optimizer=SGD(lr=learning_rate), loss='categorical_crossentropy', metrics=['categorical_accuracy'])
        #self.model.compile(optimizer=Adam(lr=learning_rate), loss = 'mean_squared_error')

        print (self.model.summary())
    
    def train(self):
        self.model.fit(self.input.trainX_categor, self.input.trainY_categor, batch_size=len(self.input.trainX_categor),epochs = 100, validation_data=(self.input.trainX_categor, self.input.trainY_categor))
        #self.model.fit(self.input.dataX_in, self.input.dataY_in, epochs = 100)
        #self.model.save("lstm_page_539")
    
    def infer(self):
        predictY = self.model.predict(self.input.trainX_categor)
        
        #print self.input.dataY_in
        print("Predict Y")
        print (predictY)
        
        dataY = np.array([np.argmax(x) for x in self.input.trainY_categor])
        predictY = np.array([np.argmax(x) for x in predictY])
        return dataY,predictY
        print (dataY)
        print (predictY)

    def calculate_prediction_error(self, dataY, predictY):
        print (dataY.shape, predictY.shape)
        err = 0.0
        dataY = np.array([np.argmax(x) for x in dataY])
        predictY = np.array([np.argmax(x) for x in predictY])
        for i in range(0, dataY.shape[0]):
            if dataY[i] != predictY[i]:
                err += 1
        error = (err / dataY.shape[0]) * 100
        return error