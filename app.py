from flask import Flask, request, redirect, url_for


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ovelse3')
def ovelse3():
    return render_template('ovelse3.html') 

@app.route('/tempar')
def tempar():
    return render_template('tempar.html')

            
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
if __name__ == '__main__':
    app.run(debug=True)