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
data_household = pd.read_csv('core/static/data/household_power_consumption_processed_15min.csv', sep=',', low_memory=False)
data_household['DateTime'] = pd.to_datetime(data_household[['Year', 'Month', 'Day', 'Hour', 'Minute']])
data_household['FormattedDateTime'] = data_household['DateTime'].dt.strftime('%Y-%m-%d %H:%M:%S')

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

current_index_pv = 0
current_index_household = 0

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
    new_index_pv = current_index_pv + 1
    session['index_pv'] = new_index_pv

    datetime = data_pv.iloc[new_index_pv]['DateTime']
    PV_productie = data_pv.iloc[new_index_pv]['PV Productie (W)']
    print(session['index_pv'])

    return jsonify({
        'DateTime': datetime,
        'PV Productie (W)': PV_productie,
    })

@chart_data.route('/get_csv_data_household_power_consumption', methods=['GET'])
def get_csv_data_household_power_consumption():
    new_index_household = current_index_household + 1
    session['index_household_power_consumption'] = new_index_household
    
    formatted_datetime = data_household.iloc[new_index_household]['FormattedDateTime']
    global_active_power = data_household.iloc[new_index_household]['Global_active_power']

    return jsonify({
        'DateTime': formatted_datetime,
        'Global_active_power': global_active_power
    })


@chart_data.route('/get_pv_prediction', methods=['GET'])
def get_pv_prediction():
    global current_index_pv

    model_type = request.args.get('model', default='lstm', type=str).lower()
    seq_length_pv = 720

    current_index_pv = current_index_pv if current_index_pv is not None else int(len(data_pv) * 0.7)
    if current_index_pv + seq_length_pv > len(data_pv):
        current_index_pv = int(len(data_pv) * 0.7)

    # get train data so the dimension can be used for the new data
    train_data_pv = data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    train_scaled_pv_gru = scaler_pv_gru.fit_transform(train_data_pv)
    train_scaled_pv_lstm = scaler_pv_lstm.fit_transform(train_data_pv)

    # get the new data for prediction using the sliding window
    new_data_pv = data_pv.iloc[current_index_pv:current_index_pv + seq_length_pv]
    new_data_pv = new_data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    new_data_scaled_pv_gru = scaler_pv_gru.transform(new_data_pv)
    new_data_scaled_pv_lstm = scaler_pv_lstm.transform(new_data_pv)
    current_index_pv += 1

    # split into sequences
    X_new_pv_gru = create_new_sequences(new_data_scaled_pv_gru, seq_length_pv)
    X_new_pv_lstm = create_new_sequences(new_data_scaled_pv_lstm, seq_length_pv)

    # predict
    y_new_pred_scaled_pv_gru = model_pv_gru.predict(X_new_pv_gru)
    y_new_pred_reshaped_pv_gru = y_new_pred_scaled_pv_gru.reshape(-1, 1)
    y_new_pred_scaled_pv_lstm = model_pv_lstm.predict(X_new_pv_lstm)
    y_new_pred_reshaped_pv_lstm = y_new_pred_scaled_pv_lstm.reshape(-1, 1)

    dummy_features_new_pv_gru = np.zeros((y_new_pred_reshaped_pv_gru.shape[0], train_scaled_pv_gru.shape[1] - 1))
    y_new_pred_inv_pv_gru = scaler_pv_gru.inverse_transform(np.concatenate((y_new_pred_reshaped_pv_gru, dummy_features_new_pv_gru), axis=1))[:, 0]
    dummy_features_new_pv_lstm = np.zeros((y_new_pred_reshaped_pv_lstm.shape[0], train_scaled_pv_lstm.shape[1] - 1))
    y_new_pred_inv_pv_lstm = scaler_pv_lstm.inverse_transform(np.concatenate((y_new_pred_reshaped_pv_lstm, dummy_features_new_pv_lstm), axis=1))[:, 0]

    # get average of the predictions from both models
    y_new_pred_avg = (y_new_pred_inv_pv_gru + y_new_pred_inv_pv_lstm) / 2

    # return the predictions as a json response
    if model_type == 'gru':
        return jsonify({'predictions': y_new_pred_inv_pv_gru.tolist()})
    if model_type == 'lstm':
        return jsonify({'predictions': y_new_pred_inv_pv_lstm.tolist()})
    if model_type == 'ensemble':
        return jsonify({'predictions': y_new_pred_avg.tolist()})

@chart_data.route('/get_household_power_consumption_prediction', methods=['GET'])
def get_household_power_consumption_prediction():
    global current_index_household

    model_type = request.args.get('model', default='lstm', type=str).lower()
    seq_length_household = 720

    current_index_household = current_index_household if current_index_household is not None else int(len(data_household) * 0.7)
    if current_index_household + seq_length_household > len(data_household):
        current_index_household = int(len(data_household) * 0.7)

    # get train data so the dimension can be used for the new data
    train_data_household = data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour', 'Minute']]
    train_scaled_household_gru = scaler_household_gru.fit_transform(train_data_household)
    train_scaled_household_lstm = scaler_household_lstm.fit_transform(train_data_household)

    # get the new data for prediction using the sliding window
    new_data_household = data_household.iloc[current_index_household:current_index_household + seq_length_household]
    new_data_household = new_data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour', 'Minute']]
    new_data_scaled_household_gru = scaler_household_gru.transform(new_data_household)
    new_data_scaled_household_lstm = scaler_household_lstm.transform(new_data_household)
    current_index_household += 1

    # split into sequences
    X_new_household_gru = create_new_sequences(new_data_scaled_household_gru, seq_length_household)
    X_new_household_lstm = create_new_sequences(new_data_scaled_household_lstm, seq_length_household)

    # predict
    y_new_pred_scaled_household_gru = model_household_gru.predict(X_new_household_gru)
    y_new_pred_reshaped_household_gru = y_new_pred_scaled_household_gru.reshape(-1, 1)
    y_new_pred_scaled_household_lstm = model_household_lstm.predict(X_new_household_lstm)
    y_new_pred_reshaped_household_lstm = y_new_pred_scaled_household_lstm.reshape(-1, 1)

    dummy_features_new_household_gru = np.zeros((y_new_pred_reshaped_household_gru.shape[0], train_scaled_household_gru.shape[1] - 1))
    y_new_pred_inv_household_gru = scaler_household_gru.inverse_transform(np.concatenate((y_new_pred_reshaped_household_gru, dummy_features_new_household_gru), axis=1))[:, 0]
    dummy_features_new_household_lstm = np.zeros((y_new_pred_reshaped_household_lstm.shape[0], train_scaled_household_lstm.shape[1] - 1))
    y_new_pred_inv_household_lstm = scaler_household_lstm.inverse_transform(np.concatenate((y_new_pred_reshaped_household_lstm, dummy_features_new_household_lstm), axis=1))[:, 0]

    # compute the average of the predictions from both models
    y_new_pred_avg = (y_new_pred_inv_household_gru + y_new_pred_inv_household_lstm) / 2

    # Return the predictions as a JSON response
    if model_type == 'gru':
        return jsonify({'predictions': y_new_pred_inv_household_gru.tolist()})
    if model_type == 'lstm':
        return jsonify({'predictions': y_new_pred_inv_household_lstm.tolist()})
    if model_type == 'ensemble':
        return jsonify({'predictions': y_new_pred_avg.tolist()})
