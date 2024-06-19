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

# dataframes
data_pv = pd.read_csv('core/static/data/2022_15min_data_with_GHI.csv', sep=',', low_memory=False)
data_household = pd.read_csv('core/static/data/household_power_consumption_processed.csv', sep=';', low_memory=False)

# load lstm models + scalers
model_pv = load_model('core/static/data/lstm_model_pv.h5')
scaler_pv = pickle.load(open('core/static/data/lstm_scaler_pv.pkl', 'rb'))

model_household = load_model('core/static/data/lstm_model_household.h5')
scaler_household = pickle.load(open('core/static/data/lstm_scaler_household.pkl', 'rb'))

# load gru models + scalers
model_pv_gru = load_model('core/static/data/gru_model_pv.h5')
scaler_pv_gru = pickle.load(open('core/static/data/gru_scaler_pv.pkl', 'rb'))

model_household_gru = load_model('core/static/data/gru_model_household.h5')
scaler_household_gru = pickle.load(open('core/static/data/gru_scaler_household.pkl', 'rb'))
# please use python 3.10.14 and transformers 2.10.0 for this code to work, the models were made in this for compatibility reasons

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

    return jsonify({
        'DateTime': data_household.iloc[new_index]['DateTime'],
        'Global_active_power': data_household.iloc[new_index]['Global_active_power'],
        'Global_reactive_power': data_household.iloc[new_index]['Global_reactive_power']
    })
    

@chart_data.route('/get_pv_prediction', methods=['GET'])
def get_pv_prediction():
    train_data_pv = data_pv
    # Get train data so athe dimension can be used for the new data
    train_data_pv = train_data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    train_scaled_pv = scaler_pv.fit_transform(train_data_pv)
    seq_length_pv = 720
    # new_data = the input, SHOULD BE CHANGED TO ACTUAL INPUT or SIMULATED DATA TODO maybe forloop through testset?
    new_data_pv = data_pv.tail(seq_length_pv) # THIS IS DUMMY INPUT
    new_data_pv = new_data_pv[['PV Productie (W)', 'Month', 'Day', 'Hour', 'Minute', 'Weekday', 'GHI (W/m^2)']]
    new_data_scaled_pv = scaler_pv.transform(new_data_pv)
    # split into sequences
    X_new_pv = create_new_sequences(new_data_scaled_pv, seq_length_pv)
    #predict
    y_new_pred_scaled_pv = model_pv.predict(X_new_pv)
    y_new_pred_reshaped_pv = y_new_pred_scaled_pv.reshape(-1, 1)
    dummy_features_new_pv = np.zeros((y_new_pred_reshaped_pv.shape[0], train_scaled_pv.shape[1] - 1))
    y_new_pred_inv_pv = scaler_pv.inverse_transform(np.concatenate((y_new_pred_reshaped_pv, dummy_features_new_pv), axis=1))[:, 0]

    return jsonify({'predictions': y_new_pred_inv_pv.tolist()})

@chart_data.route('/get_household_power_consumption_prediction', methods=['GET'])
def get_household_power_consumption_prediction():
    train_data_household = data_household
    # Get train data so athe dimension can be used for the new data
    train_data_household = train_data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour']]
    train_scaled_household = scaler_household.fit_transform(train_data_household)
    seq_length_household = 720
    # new_data = the input, SHOULD BE CHANGED TO ACTUAL INPUT or SIMULATED DATA TODO maybe forloop through testset?
    new_data_household = data_household.tail(seq_length_household) # THIS IS DUMMY INPUT
    new_data_household = new_data_household[['Global_active_power', 'Month', 'Day', 'Weekday', 'Hour']]
    new_data_scaled_household = scaler_household.transform(new_data_household)
    # split into sequences
    X_new_household = create_new_sequences(new_data_scaled_household, seq_length_household)
    #predict
    y_new_pred_scaled_household = model_household.predict(X_new_household)
    y_new_pred_reshaped_household = y_new_pred_scaled_household.reshape(-1, 1)
    dummy_features_new_household = np.zeros((y_new_pred_reshaped_household.shape[0], train_scaled_household.shape[1] - 1))
    y_new_pred_inv_household = scaler_household.inverse_transform(np.concatenate((y_new_pred_reshaped_household, dummy_features_new_household), axis=1))[:, 0]

    return jsonify({'predictions': y_new_pred_inv_household.tolist()})
