import os
from flask import Blueprint, render_template, request, redirect, url_for, flash

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
core = Blueprint('site', __name__,
    static_folder='static',
    template_folder='templates')

@core.route('/')
def index():
    return render_template('index.html')

@core.route('/dummy_button_press', methods=['POST'])
def dummy_action():
    return render_template('dummy_page.html')
