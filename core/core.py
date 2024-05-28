import os
import random
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import datetime
import numpy as np
import matplotlib
import pandas as pd
matplotlib.use('Agg')
import matplotlib.pyplot as plt

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
core = Blueprint('core', __name__,
    static_folder='static',
    static_url_path='/core/static',
    template_folder='templates')

@core.route('/')
def index():
    return render_template('index.html')

@core.route('/dummy_button_press', methods=['POST'])
def dummy_action():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    return render_template('dummy_page.html', name=name, email=email, message=message)

@core.route('/live_update_example_this_is_the_url')
def live_update_example():
    return render_template('live_update_example.html')

@core.route('/clock_update', methods=['GET'])
def clock_update():
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    return current_time

@core.route('/charts',  methods=['GET'])
def charts_simple():
    return render_template('charts_simple.html')

x_data = [np.arange(0, 10, 0.1) for _ in range(4)]
y_data = [np.random.rand(len(x_data[i])) for i in range(4)]

@core.route('/graph_update', methods=['GET'])
def graph_update():

    global x_data, y_data

    fig, axs = plt.subplots(2, 2, figsize=(10, 10))

    plot_types = ['line', 'scatter', 'bar', 'hist']

    for i in range(2):
        for j in range(2):
            #append data to end of array
            x_data[2*i + j] = np.append(x_data[2*i + j], x_data[2*i + j][-1] + 0.1)
            y_data[2*i + j] = np.append(y_data[2*i + j], np.random.rand(1))

            if len(x_data[2*i + j]) > 50:
                x_data[2*i + j] = x_data[2*i + j][-50:]
                y_data[2*i + j] = y_data[2*i + j][-50:]

            if plot_types[2*i + j] == 'line':
                axs[i, j].plot(x_data[2*i + j], y_data[2*i + j])
            elif plot_types[2*i + j] == 'scatter':
                axs[i, j].scatter(x_data[2*i + j], y_data[2*i + j])
            elif plot_types[2*i + j] == 'bar':
                axs[i, j].bar(x_data[2*i + j], y_data[2*i + j])
            elif plot_types[2*i + j] == 'hist':
                axs[i, j].hist(y_data[2*i + j], bins=10)

    file_path = os.path.join(dir_path, 'static/image', 'graph.png')
    plt.savefig(file_path)

    return "graph.png was changed" #could return the path but due to the way pahting works with blueprint this s just to tell the client that the image was saved

@core.route('/get_new_usage', methods=['GET'])
def get_new_usage():
    
    new_usage = random.randint(0, 100)

    return str(new_usage)

@core.route('/get_future_usage_prediction', methods=['GET'])
def get_future_usage_prediction():
    
    new_usage = random.randint(0, 100)

    return str(new_usage)

from flask import jsonify

@core.route('/get_csv_data', methods=['GET'])
def get_csv_data():
    index = session.get('index', 0)

    data = pd.read_csv('core/static/data/2022_15min_data.csv')

    new_index = index + 1
    session['index'] = new_index

    print(data.iloc[new_index]['Time'])
    print(data.iloc[new_index]['PV Productie (W)'])

    return jsonify({
        'Time': data.iloc[new_index]['Time'],
        'PV Productie (W)': data.iloc[new_index]['PV Productie (W)']
    })
