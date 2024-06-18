import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import datetime
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from keras.src.legacy.saving import legacy_h5_format

def create_new_sequences(data, seq_length):
    X = []
    for i in range(len(data) - seq_length + 1):
        seq = data[i:(i + seq_length), :]
        X.append(seq)
    return np.array(X)

model = load_model('core/static/data/lstm_model_pv.h5', custom_objects={'mae': 'mae'})
scaler = MinMaxScaler()
train_data = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False)
train_data = train_data[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
train_scaled = scaler.fit_transform(train_data)
seq_length = 720
new_data = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False).tail(720)
new_data = new_data[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
new_data_scaled = scaler.transform(new_data)
X_new = create_new_sequences(new_data_scaled, seq_length)
y_new_pred_scaled = model.predict(X_new)
y_new_pred_reshaped = y_new_pred_scaled.reshape(-1, 1)
dummy_features_new = np.zeros((y_new_pred_reshaped.shape[0], train_scaled.shape[1] - 1))
y_new_pred_inv = scaler.inverse_transform(np.concatenate((y_new_pred_reshaped, dummy_features_new), axis=1))[:, 0]
