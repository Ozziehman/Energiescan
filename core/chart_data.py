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

# dir_path = os.path.dirname(os.path.realpath(__file__))
# print(dir_path)
chart_data = Blueprint('chart_data', __name__,
    static_folder='static',
    static_url_path='/core/static',
    template_folder='templates')

# Global variables for the data
data_pv = pd.read_csv('core/static/data/2022_15min_data.csv')
data_household_power_consumption = pd.read_csv('core/static/data/household_power_consumption.csv', sep=';', low_memory=False)

# Load the trained LSTM model
model_pv = load_model('core/static/data/lstm_model_pv.h5')
model_household = load_model('core/static/data/lstm_model_household.h5')

# Initialize and fit the scaler on the historical data
scaler = MinMaxScaler(feature_range=(0, 1))

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
    
    
@chart_data.route('/get_pv_prediction', methods=['GET'])
def get_pv_prediction():
    # Fetch past & ahead amount
    n_sequence_past = 720
    n_ahead_prediction = 154
    
    # Error handling
    index = session.get('index_pv', 0)
    if index + n_sequence_past + n_ahead_prediction > len(data_pv):
        return jsonify({'error': 'Not enough data for prediction'})

    # Get the required data slice
    data_slice = data_pv.iloc[index:index + n_sequence_past + n_ahead_prediction]

    # Preprocess the data slice
    data_scaled = scaler.transform(data_slice)
    X_input = data_scaled[:n_sequence_past].reshape(1, n_sequence_past, -1)

    # Predict
    predictions_scaled = model_pv.predict(X_input)
    
    # Inverse transform the predictions
    dummy_features = np.zeros((predictions_scaled.shape[1], data_scaled.shape[1] - 1))
    predictions_inv = scaler.inverse_transform(np.concatenate((predictions_scaled.reshape(-1, 1), dummy_features), axis=1))[:, 0]

    return jsonify({'predictions': predictions_inv.tolist()})


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