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
# from keras.src.legacy.saving import legacy_h5_format
import pickle


# dir_path = os.path.dirname(os.path.realpath(__file__))
# print(dir_path)
chart_data = Blueprint('chart_data', __name__,
    static_folder='static',
    static_url_path='/core/static',
    template_folder='templates')

# Dataframes
data_pv = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False)
data_household = pd.read_csv('core/static/data/household_power_consumption_processed.csv', sep=',', low_memory=False)

# Load the pre-trained LSTM models and the Scalers
model_pv_lstm = load_model('core/static/data/lstm_model_pv.h5')
scaler_pv_lstm = pickle.load(open('core/static/data/lstm_scaler_pv.pkl', 'rb'))

model_household_lstm = load_model('core/static/data/lstm_model_household.h5')
scaler_household_lstm = pickle.load(open('core/static/data/lstm_scaler_household.pkl', 'rb'))

# Load the pre-trained GRU models and the Scalers
model_pv_gru = load_model('core/static/data/gru_model_pv.h5')
scaler_pv_gru = pickle.load(open('core/static/data/gru_scaler_pv.pkl', 'rb'))

model_household_gru = load_model('core/static/data/gru_model_household.h5')
scaler_household_gru = pickle.load(open('core/static/data/gru_scaler_household.pkl', 'rb'))
# NOTE: Please use python 3.10.14 and transformers 2.10.0 for this code to work, the models were made in this for compatibility reasons

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
        'Time': data_pv.iloc[current_index]['DateTime'],
        'PV Productie (W)': data_pv.iloc[current_index]['PV Productie (W)']
    })

@chart_data.route('/get_csv_data_household_power_consumption', methods=['GET'])
def get_csv_data_household_power_consumption():
    index = session.get(
        'index_houshold_power_consumption', 0)

    new_index = index + 1
    session['index_houshold_power_consumption'] = new_index
    
    data_household['DateTime'] = pd.to_datetime(data_household[['Year', 'Month', 'Day', 'Hour', 'Minute']])

    return jsonify({
        'DateTime': data_household.iloc[new_index]['DateTime'],
        'Global_active_power': data_household.iloc[new_index]['Global_active_power'],
        'Global_reactive_power': data_household.iloc[new_index]['Global_reactive_power']
    })
    
current_index = None

@chart_data.route('/get_pv_prediction', methods=['GET'])
def get_pv_prediction():
    global current_index

    model_type = request.args.get('model', default='lstm', type=str).lower()
    seq_length_pv = 720

    current_index = current_index if current_index is not None else int(len(data_pv) * 0.7)
    if current_index + seq_length_pv > len(data_pv):
        current_index = int(len(data_pv) * 0.7)

    # Get train data so the dimension can be used for the new data
    train_data_pv = data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    train_scaled_pv_gru = scaler_pv_gru.fit_transform(train_data_pv)
    train_scaled_pv_lstm = scaler_pv_lstm.fit_transform(train_data_pv)

    # Get the new data for prediction using the sliding window
    new_data_pv = data_pv.iloc[current_index:current_index + seq_length_pv]
    new_data_pv = new_data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    new_data_scaled_pv_gru = scaler_pv_gru.transform(new_data_pv)
    new_data_scaled_pv_lstm = scaler_pv_lstm.transform(new_data_pv)
    current_index += 1

    # Split into sequences
    X_new_pv_gru = create_new_sequences(new_data_scaled_pv_gru, seq_length_pv)
    X_new_pv_lstm = create_new_sequences(new_data_scaled_pv_lstm, seq_length_pv)

    # Predict
    y_new_pred_scaled_pv_gru = model_pv_gru.predict(X_new_pv_gru)
    y_new_pred_reshaped_pv_gru = y_new_pred_scaled_pv_gru.reshape(-1, 1)
    y_new_pred_scaled_pv_lstm = model_pv_lstm.predict(X_new_pv_lstm)
    y_new_pred_reshaped_pv_lstm = y_new_pred_scaled_pv_lstm.reshape(-1, 1)

    dummy_features_new_pv_gru = np.zeros((y_new_pred_reshaped_pv_gru.shape[0], train_scaled_pv_gru.shape[1] - 1))
    y_new_pred_inv_pv_gru = scaler_pv_gru.inverse_transform(np.concatenate((y_new_pred_reshaped_pv_gru, dummy_features_new_pv_gru), axis=1))[:, 0]
    dummy_features_new_pv_lstm = np.zeros((y_new_pred_reshaped_pv_lstm.shape[0], train_scaled_pv_lstm.shape[1] - 1))
    y_new_pred_inv_pv_lstm = scaler_pv_lstm.inverse_transform(np.concatenate((y_new_pred_reshaped_pv_lstm, dummy_features_new_pv_lstm), axis=1))[:, 0]

    # Compute the average of the predictions from both models
    y_new_pred_avg = (y_new_pred_inv_pv_gru + y_new_pred_inv_pv_lstm) / 2

    # Return the predictions as a JSON response
    if model_type == 'gru':
        return jsonify({'predictions': y_new_pred_inv_pv_gru.tolist()})
    if model_type == 'lstm':
        return jsonify({'predictions': y_new_pred_inv_pv_lstm.tolist()})
    if model_type == 'ensemble':
        return jsonify({'predictions': y_new_pred_avg.tolist()})

@chart_data.route('/get_household_power_consumption_prediction', methods=['GET'])
def get_household_power_consumption_prediction():
    model_type = request.args.get('model', default='lstm', type=str).lower()
    
    if model_type == 'gru':
        model_household = model_household_gru
        scaler_household = scaler_household_gru
    else:
        model_household = model_household_lstm
        scaler_household = scaler_household_lstm
    
    train_data_household = data_household
    
    # Get train data so the dimension can be used for the new data
    train_data_household = train_data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour', 'Minute']]
    train_scaled_household = scaler_household.fit_transform(train_data_household)
    seq_length_household = 720
    
    # new_data = the input, SHOULD BE CHANGED TO ACTUAL INPUT or SIMULATED DATA TODO maybe forloop through testset?
    new_data_household = data_household.tail(720) # THIS IS DUMMY INPUT
    new_data_household = new_data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour', 'Minute']]
    new_data_scaled_household = scaler_household.transform(new_data_household)
    
    # Split into sequences
    X_new_household = create_new_sequences(new_data_scaled_household, seq_length_household)
    
    # Predict
    y_new_pred_scaled_household = model_household.predict(X_new_household)
    y_new_pred_reshaped_household = y_new_pred_scaled_household.reshape(-1, 1)
    dummy_features_new_household = np.zeros((y_new_pred_reshaped_household.shape[0], train_scaled_household.shape[1] - 1))
    y_new_pred_inv_household = scaler_household.inverse_transform(np.concatenate((y_new_pred_reshaped_household, dummy_features_new_household), axis=1))[:, 0]

    return jsonify({'predictions': y_new_pred_inv_household.tolist()})
