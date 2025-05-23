from flask import Flask, render_template
from flask_socketio import SocketIO


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/debug_485")
def debug_485():
    return render_template("rs485.html")

@app.route("/debug_can")
def debug_can():
    return render_template("can.html")

@app.route("/debug_io")
def debug_io():
    return render_template("io.html")
