import base64
import pigpio
import threading
import os
from datetime import datetime as dt
from time import sleep
from io import BytesIO
from pigpio_dht import DHT11
from flask import Flask, render_template
from picamera2 import Picamera2, Preview
from flask_socketio import SocketIO, emit


BUTTON_GPIO_PIN = 4
LED_GPIO_PIN = 14
DHT11_PIN = 19
sensor = DHT11(DHT11_PIN)
sidste_temp = None
pi = pigpio.pi()

app = Flask(__name__)

socketio = SocketIO(app)
"""
def stue_temp():
    timestamps, temp, hum = get_stue_data(10)
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom = 0.3)
    ax.tick_params(axis="x", which='both', rotation=45, colors="black") 
    ax.set_facecolor("none")
    ax.plot(timestamps, temp, linestyle="--", c="black", linewidth=.5, marker=".", mec="blue", mfc="red", ms=7)
    #ax.set_title("temperature")
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.set_xlabel("timestamp")
    ax.set_ylabel("temperature")
    fig.patch.set_facecolor("none")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data
def stue_hum():
    timestamps, temp, hum = get_stue_data(10)
    fig = Figure()
    ax = fig.subplots()
    fig.subplots_adjust(bottom = 0.3)
    ax.tick_params(axis="x", which='both', rotation=45)
    ax.set_facecolor("none")
    ax.plot(timestamps, hum, linestyle="--", c="black", linewidth=.5, marker=".", mec="blue", mfc="red", ms=7)
    #ax.set_title("humidity")
    ax.spines.right.set_visible(False)
    ax.spines.top.set_visible(False)
    ax.set_xlabel("timestamp")
    ax.set_ylabel("humidity")
    fig.patch.set_facecolor("none")
    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return data
"""


@app.route('/')
def home():
    return render_template('index.html')


def tilstand():
    button_state = pi.read(BUTTON_GPIO_PIN)
    socketio.emit('button_state', button_state)

@socketio.on('connect')
def connect():
    tilstand()

def cbf(gpio, level, tick):
    tilstand()

pi.callback(BUTTON_GPIO_PIN, pigpio.EITHER_EDGE, cbf)

@app.route('/ovelse2')
def ovelse2():
    return render_template('ovelse2.html',
tilstand=pi.read(BUTTON_GPIO_PIN))


@socketio.on('skru_paa_led')
def skru(data):
    lystyrke = int(data['lysstyrke'])
    if lystyrke < 0:
        lystyrke = 0
    if lystyrke > 255:
        lystyrke = 255
    pi.set_PWM_dutycycle(LED_GPIO_PIN, lystyrke)

@app.route('/ovelse3')
def ovelse3():
    return render_template('ovelse3.html') 

@socketio.on('hent_temp')
def hent_temp():
    sleep(5)
    socketio.emit('temp', sidste_temp)

@app.route('/tempar')
def tempar():
    return render_template('tempar.html')

def read_temp():
    global sidste_temp
    while True:
        sleep(2)
        try:
            sidste_temp = sensor.read()
        except:
            sidste_temp = None

            
def refresh_pictures():
    snaps_folder = "/home/sorent/kea/vhus/static/snaps/"
    if not os.path.exists(snaps_folder):
        print(f"Folder does not exist: {snaps_folder}")
        return []
    file_list = os.listdir(snaps_folder)
    pictures = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(snaps_folder, x)), reverse=True)
    return pictures[:3]

@app.route('/photo')
def shoot():
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        day = dt.now()
        pic_name = f"{day.strftime('%d%m%y_%H%M%S')}.jpg"
        pic_path = os.path.join("/home/sorent/kea/vhus/static/snaps/", pic_name)
        os.makedirs(os.path.dirname(pic_path), exist_ok=True)
        picam2.capture_file(pic_path)
        picam2.close()
        pics = refresh_pictures()
        return render_template('photo.html', pics=pics, pic_name=pic_name)

    except Exception as e:
        return str(e), 500


@app.route('/soil')
def soil(): 
    return render_template('soil.html')

@app.route('/weather')
def weather(): 
    return render_template('weather.html')

temp_thread = threading.Thread(target=read_temp)
temp_thread.start()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)