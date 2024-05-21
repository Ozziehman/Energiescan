import os
from flask import Blueprint, render_template, request, redirect, url_for, flash
import datetime

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
core = Blueprint('core', __name__,
    static_folder='static',
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
