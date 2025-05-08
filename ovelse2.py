from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pigpio

BUTTON_GPIO_PIN = 4

pi = pigpio.pi()
app = Flask(__name__)
socketio = SocketIO(app)

def tilstand():
    button_state = pi.read(BUTTON_GPIO_PIN)
    socketio.emit('button_state', button_state)

@socketio.on('connect')
def connect():
    tilstand()

def cbf(gpio, level, tick):
    tilstand()

pi.callback(BUTTON_GPIO_PIN, pigpio.EITHER_EDGE, cbf)

@app.route('/')
def index():
    return render_template('ovelse2.html',
tilstand=pi.read(BUTTON_GPIO_PIN))

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)