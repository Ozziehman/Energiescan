import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import datetime
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# dir_path = os.path.dirname(os.path.realpath(__file__))
# print(dir_path)
chart_data = Blueprint('chart_data', __name__,
    static_folder='static',
    static_url_path='/core/static',
    template_folder='templates')

# Global variables for the data
data_pv = pd.read_csv('core/static/data/2022_15min_data.csv')
data_household_power_consumption = pd.read_csv('core/static/data/household_power_consumption.csv', low_memory=False)

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