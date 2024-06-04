from flask import Flask
from core.core import core
from core.chart_data import chart_data
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'secret_key'
app.register_blueprint(core)
app.register_blueprint(chart_data)
Bootstrap(app)

if __name__ == '__main__':
    app.run()
