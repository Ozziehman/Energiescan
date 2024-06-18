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

# dir_path = os.path.dirname(os.path.realpath(__file__))
# print(dir_path)
chart_data = Blueprint('chart_data', __name__,
    static_folder='static',
    static_url_path='/core/static',
    template_folder='templates')

# Global variables for the data
data_pv = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv')
df_pv = data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
data_household_power_consumption = pd.read_csv('core/static/data/household_power_consumption.csv', sep=';', low_memory=False)

# Load the trained LSTM model
model_pv = legacy_h5_format.load_model_from_hdf5('core/static/data/lstm_model_pv.h5', custom_objects={'mae': 'mae'})
# model_household = legacy_h5_format.load_model_from_hdf5(('core/static/data/lstm_model_household.h5')

# Initialize and fit the scaler on the historical data
scaler = MinMaxScaler(feature_range=(0, 1))

def create_sequences(data, seq_length, prediction_length):
    X, y = [], []
    for i in range(len(data) - seq_length - prediction_length + 1):
        seq = data[i:(i + seq_length), :]  # All columns for X
        label = data[(i + seq_length):(i + seq_length + prediction_length), 0]  # First column is the target
        X.append(seq)
        y.append(label)
    arrayX = np.array(X)
    arrayY = np.array(y)
    print(f"Shapes: X={arrayX.shape}, y={arrayY.shape}")
    return arrayX, arrayY

def create_new_sequences(data, seq_length):
    X = []
    for i in range(len(data) - seq_length + 1):
        seq = data[i:(i + seq_length), :]
        X.append(seq)
    return np.array(X)


@chart_data.route('/get_csv_data_pv', methods=['GET'])
def get_csv_data_pv():
    index = session.get('index_pv', 0)

    new_index = index + 1
    session['index_pv'] = new_index

    # print(data.iloc[new_index]['Time'])
    # print(data.iloc[new_index]['PV Productie (W)'])

    return jsonify({
        'Time': data_pv.iloc[new_index]['Time'],
        'PV Productie (W)': data_pv.iloc[new_index]['PV Productie (W)']
    })

@chart_data.route('/get_csv_data_household_power_consumption', methods=['GET'])
def get_csv_data_household_power_consumption():
    index = session.get('index_houshold_power_consumption', 0)

    new_index = index + 1
    session['index_houshold_power_consumption'] = new_index

    #print(data_household_power_consumption.iloc[new_index]['Global_active_power'])

    return jsonify({
        'DateTime': data_household_power_consumption.iloc[new_index]['Date'] + " " + data_household_power_consumption.iloc[new_index]['Time'],
        'Global_active_power': data_household_power_consumption.iloc[new_index]['Global_active_power'],
        'Global_reactive_power': data_household_power_consumption.iloc[new_index]['Global_reactive_power']
    })
    
    
# @chart_data.route('/get_pv_prediction', methods=['GET'])
# def get_pv_prediction():
#     # Fetch past & ahead amount
#     n_sequence_past = 720
#     n_ahead_prediction = 154

#     # Error handling
#     index = 0
#     if index + n_sequence_past + n_ahead_prediction > len(df_pv):
#         return jsonify({'error': 'Not enough data for prediction'})

#     # Get the required data slice
#     data_slice = df_pv.iloc[index:index + n_sequence_past + n_ahead_prediction].values

#     # Create sequences
#     X, y = create_sequences(data_slice, seq_length=n_sequence_past, prediction_length=n_ahead_prediction)

#     # Predict (only take the first prediction for the given range)
#     predictions = model_pv.predict(X)[0]

#     return jsonify({'predictions': predictions.tolist()})

@chart_data.route('/get_pv_prediction', methods=['GET'])
def get_pv_prediction():
    model = load_model('core/static/data/lstm_model_pv.h5', custom_objects={'mae': 'mae'})
    scaler = MinMaxScaler()
    train_data = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False)
    train_data = train_data[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    train_scaled = scaler.fit_transform(train_data)
    seq_length = 720
    # new_data = the input, SHOULD BE CHANGED TO ACTUAL INPUT or SIMULATED DATA TODO maybe forloop through testset?
    new_data = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False).tail(720)
    new_data = new_data[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    new_data_scaled = scaler.transform(new_data)
    X_new = create_new_sequences(new_data_scaled, seq_length)
    y_new_pred_scaled = model.predict(X_new)
    y_new_pred_reshaped = y_new_pred_scaled.reshape(-1, 1)
    dummy_features_new = np.zeros((y_new_pred_reshaped.shape[0], train_scaled.shape[1] - 1))
    y_new_pred_inv = scaler.inverse_transform(np.concatenate((y_new_pred_reshaped, dummy_features_new), axis=1))[:, 0]
    return jsonify({'predictions': y_new_pred_inv.tolist()})

@chart_data.route('/get_household_power_consumption_prediction', methods=['GET'])
def get_household_power_consumption_prediction():
    # Fetch past & ahead amount
    n_sequence_past = 720
    n_ahead_prediction = 154
    
    # Error handling
    index = session.get('index_household_power_consumption', 0)
    if index + n_sequence_past + n_ahead_prediction > len(data_household_power_consumption):
        return jsonify({'error': 'Not enough data for prediction'})

    # Get the required data slice
    data_slice = data_household_power_consumption.iloc[index:index + n_sequence_past + n_ahead_prediction]

    # Preprocess the data slice
    data_scaled = scaler.transform(data_slice)
    X_input = data_scaled[:n_sequence_past].reshape(1, n_sequence_past, -1)

    # Predict
    predictions_scaled = model_household.predict(X_input)
    
    # Inverse transform the predictions
    dummy_features = np.zeros((predictions_scaled.shape[1], data_scaled.shape[1] - 1))
    predictions_inv = scaler.inverse_transform(np.concatenate((predictions_scaled.reshape(-1, 1), dummy_features), axis=1))[:, 0]

    return jsonify({'predictions': predictions_inv.tolist()})
