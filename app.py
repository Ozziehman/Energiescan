from flask import Flask
from core.core import core
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.register_blueprint(core)
Bootstrap(app)
