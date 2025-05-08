from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import pigpio
from time import sleep

LED_GPIO_PIN = 13, 25, 26
pi = pigpio.pi()
app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('skru_paa_led')
def skru(data):
    lystyrke = int(data['lysstyrke'])
    if lystyrke < 0:
        lystyrke = 0
    if lystyrke > 255:
        lystyrke = 255
    pi.set_PWM_dutycycle(LED_GPIO_PIN, lystyrke)

@app.route('/')
def index():
    return render_template('ovelse3.html')  

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

