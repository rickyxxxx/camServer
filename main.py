from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import pyodbc
import os
from werkzeug.utils import secure_filename
import datetime
import threading
import cv2
import numpy as np

app = Flask(__name__, static_folder='static', template_folder='static/templates')


frame_lock = threading.Lock()
latest_frame = None


@app.route('/')
def index():
    return render_template('testing.html')


@app.route('/debug')
def debug():
    return render_template('gallery.html')


@app.route('/CMS')
def management_system():
    return render_template('login.html')


@app.route('/download_fits/<name>')
def download_fits(name):
    return send_from_directory(directory="static/images", path=name, as_attachment=True)


@app.route('/download_images', methods=['POST'])
def download_images():
    image_names = request.json.get('images', [])
    if not image_names:
        return jsonify({'status': 'error', 'message': 'No images selected'})

    download_folder = 'downloads'
    os.makedirs(download_folder, exist_ok=True)

    for img in image_names:
        img_path = os.path.join(IMAGE_FOLDER, img)
        if os.path.exists(img_path):
            os.system(f'cp "{img_path}" "{download_folder}/{secure_filename(img)}"')

    return send_from_directory(directory=download_folder, path='.', as_attachment=True)


@app.route('/get_cameras')
def get_cameras():
    cameras = ["Camera 1", "Camera 2", "Camera 3"]
    return jsonify({'cameras': cameras})


@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        file = request.files['file']
        camId = request.form['camId']
        location_lat = request.form['location_lat']
        location_lng = request.form['location_lng']
        datetime = request.form['datetime']
        filename = file.filename
    except Exception:
        return jsonify({'error': 'No file part in the request'}), 400

    # insert image info into the database

    if filename.endswith('.png'):
        folder = "png"
    elif filename.endswith('.fits'):
        folder = "fits"
    elif filename.endswith('.jpg'):
        folder = "jpg"
    else:
        return jsonify({'error': 'Invalid file format'}), 400

    path = os.path.join("app/static/images", folder, filename)
    file.save(path)
    return jsonify({'message': f"File {filename} uploaded"}), 201


@app.route('/upload_data/', methods=['POST'])
def upload_data():
    try:
        msg = request.form["msg"]
    except Exception:
        return jsonify({'error': 'No message provided'}), 400

    if len(temp_hum_list[0]) > 10:
        # append data to the csv file
        with open('camData.csv', 'a') as f:
            for i in range(len(temp_hum_list[0])):
                f.write(f'{temp_hum_list[0][i]},{temp_hum_list[1][i]},{temp_hum_list[2][i]}\n')
        temp_hum_list[0].clear()
        temp_hum_list[1].clear()
        temp_hum_list[2].clear()

    datetime, temp, hum = msg.split(',')
    temp_hum_list[0].append(datetime)
    temp_hum_list[1].append(float(temp))
    temp_hum_list[2].append(float(hum))

    return jsonify({'message': 'Data uploaded'}), 201


@app.route('/download_data_csv')
def download_data_csv():
    return send_from_directory(directory='.', path='camData.csv', as_attachment=True)


@app.route('/get_setting/<camId>')
def get_setting(camId):
    return jsonify(settings)


@app.route('/set_setting/<camId>', methods=['POST'])
def set_setting(camId):
    settings.update(request.json)
    return jsonify({'status': 'success'})


@app.route('/verify/<username>/<password>')
def verify(username, password):
    if username == 'admin' and password == 'admin':
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'})


@app.route('/images/<int:page>')
def images(page: int):

    def unpack_specs(f: str):
        _, dt = f.split('_')
        return dt, 0, 0

    img_w_specs = [
        (f, *unpack_specs(f))
        for f in internal_states['displaying_list']
    ]

    def sort_func(i):
        fname = i[0]
        fname = fname.split(".")[0]
        camid, timestamp_str = fname.split('_')
        timestamp_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
        return timestamp_dt

    img_w_specs = sorted(img_w_specs, key=sort_func, reverse=True)
    print(img_w_specs)
    page_start = page * 8
    page_end = page_start + 8

    return jsonify(img_w_specs[page_start: page_end])


def scan_images() -> list[str]:
    img_dir = 'app/static/images/'
    return [f.rstrip(".png") for f in os.listdir(img_dir) if f.endswith('.png')]


@app.route('/get_total_pages')
def get_total_pages():
    internal_states['displaying_list'] = scan_images()
    image_count = len(internal_states['displaying_list'])
    pages = (image_count + 8 - 1) // 8
    return jsonify({"totalPages": pages})


@app.route('/upload_live', methods=['POST'])
def upload_frame():
    global latest_frame
    data = request.data
    np_arr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    with frame_lock:
        latest_frame = frame
    return 'OK'


def generate_stream():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is None:
                continue
            # Encode the frame in JPEG
            ret, jpeg = cv2.imencode('.jpg', latest_frame)
            if not ret:
                continue
            frame_data = jpeg.tobytes()

        # MJPEG streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True, port=80, host='0.0.0.0')
