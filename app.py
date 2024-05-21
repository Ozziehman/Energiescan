from flask import Flask
import logging
from core.site import core

app = Flask(__name__)
app.register_blueprint(core)
