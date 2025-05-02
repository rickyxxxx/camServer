import os
import datetime
import threading
import cv2
from astropy.io import fits
from flask_cors import CORS

from PIL import Image
from io import BytesIO

import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, send_file, abort


from app.database import Database

app = Flask(__name__, static_folder='static')
CORS(app)  # This will allow all domains by default
db = Database()

frame_lock = threading.Lock()
latest_frame = None


settings = {}


@app.route('/')
def index():
    return render_template('index.html')


# @app.route('/debug')
# def debug():
#     return render_template('gallery.html')
#
# @app.route('/CMS')
# def CMS():
#     return render_template('camera_manager.html')
#
# # return a list of image files path that matches the filtering condition
# @app.route('/search/<datetime_list>')
# def search(datetime_list):
#     if datetime_list == "None":
#         return jsonify(db.search_images_by_date())
#
#     datetime_periods = datetime_list.split(";")
#     datetime_periods = [dt.split(',') for dt in datetime_periods]
#
#     return jsonify(db.search_images_by_date(datetime_periods))


@app.route('/api/image/<path:filename>')
def serve_image(filename):
    return send_file(f"/{filename}", as_attachment=True)


@app.route('/api/query/')
def api_query():
    get = request.args.get

    # the number of images to be loaded, default 20 images per page
    pagesize = get('pagesize', 20)

    # sql query conditions (single string), default None
    conditions = get('conditions')

    # whether to display the images in an arising or declining order
    order = get('order', 'DESC')

    # image id of the last image, used to mark the start of pagination
    last_uid = get('lastUID')

    # generate a sql command
    header = ["image", "datetime", "expTime", "eGain", "siteName", "UID", "timeZone", "humidity", "temp"]
    fields = ["Images.ImgPath", "Images.Timestamp", "Images.ExpTime", "Images.Gain", "Cameras.SiteName", "Images.ImgId",
              "Images.timeZone", "Images.Humidity", "Images.Temperature"]
    table = "Images INNER JOIN Cameras ON Images.CamId = Cameras.CamId"
    sql = f"SELECT {",".join(fields)} FROM {table} "

    if conditions or last_uid:
        sql += "WHERE "

    if conditions:
        sql += f"{conditions} "

    if last_uid:
        if conditions:
            sql += "and "
        sql += f"Images.ImgId {order == "DESC" and "<" or ">"} {last_uid} "

    sql += f"ORDER BY Images.Timestamp {order} OFFSET 0 ROWS FETCH NEXT {pagesize} ROWS ONLY"

    result = db.query(sql)
    result = [{k: v for k, v in zip(header, row)} for row in result]
    return jsonify(result)


@app.route('/api/sites/')
def sites():
    try:
        header = ["index", "siteName", "lat", "long", "id"]
        sql = "SELECT UID, SiteName, GeoLoc.Lat, GeoLoc.Long, CamId from Cameras"
        result = db.query(sql)
        result = [{k: v for k, v in zip(header, row)} for row in result]
        return jsonify(result)
    except Exception:
        pass


# @app.route("/get_file/<path:filepath>")
# def get_file(filepath):
#     return send_file(f"/{filepath}", as_attachment=False)

@app.route("/temp/png/<path:filename>")
def get_png(filename):
    filename = f"/{filename}"
    try:
        # Open the FITS file
        with fits.open(filename) as hdul:
            data = hdul[0].data

        # Check if data is None
        if data is None:
            abort(400, description="No image data found in FITS file.")

        # Process the data based on its shape
        if data.ndim == 2:
            # Grayscale image
            image_data = normalize_data(data)
            image = Image.fromarray(image_data, mode='L')
        elif data.ndim == 3 and data.shape[0] == 3:
            # RGB image with shape (3, height, width)
            channels = [normalize_data(channel) for channel in data]
            rgb_array = np.stack(channels, axis=-1)  # Shape: (height, width, 3)
            image = Image.fromarray(rgb_array, mode='RGB')
        else:
            abort(400, description="Unsupported FITS image format.")

        # Save the image to a BytesIO object
        img_io = BytesIO()
        image.save(img_io, format='PNG')
        img_io.seek(0)

        download_filename = filename.split("/")[-1].strip('.fits') + '.png'
        print(download_filename)

        return send_file(img_io, mimetype='image/png', as_attachment=True, download_name=download_filename)

    except Exception as e:
        abort(500, description=f"An error occurred: {str(e)}")


@app.route('/temp/tiff/<path:filename>')
def get_tiff(filename):
    # Ensure the filename is safe and construct the absolute path
    fits_path = os.path.abspath(f"/{filename}")
    if not os.path.isfile(fits_path):
        abort(404, description="FITS file not found.")

    try:
        # Open the FITS file
        with fits.open(fits_path) as hdul:
            data = hdul[0].data

        # Check if data is None
        if data is None:
            abort(400, description="No image data found in FITS file.")

        # Process the data based on its shape
        if data.ndim == 2:
            # Grayscale image
            image_data = normalize_data(data)
            image = Image.fromarray(image_data, mode='L')
        elif data.ndim == 3 and data.shape[0] == 3:
            # RGB image with shape (3, height, width)
            channels = [normalize_data(channel) for channel in data]
            rgb_array = np.stack(channels, axis=-1)  # Shape: (height, width, 3)
            image = Image.fromarray(rgb_array, mode='RGB')
        else:
            abort(400, description="Unsupported FITS image format.")

        # Save the image to a BytesIO object
        img_io = BytesIO()
        image.save(img_io, format='TIFF')
        img_io.seek(0)

        # Construct the download filename by replacing the .fits extension with .tiff
        base_filename = os.path.basename(filename)
        download_filename = os.path.splitext(base_filename)[0] + '.tiff'

        return send_file(
            img_io,
            mimetype='image/tiff',
            as_attachment=True,
            download_name=download_filename
        )

    except Exception as e:
        abort(500, description=f"An error occurred: {str(e)}")


def normalize_data(data):
    """
    Normalize the data to the 0-255 range and convert to uint8.
    """
    data = np.nan_to_num(data)  # Replace NaNs with zero
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max - data_min == 0:
        return np.zeros(data.shape, dtype=np.uint8)
    normalized = (data - data_min) / (data_max - data_min)
    return (normalized * 255).astype(np.uint8)


# @app.route('/download_fits/<name>')
# def download_fits(name):
#     return send_from_directory(directory="static/images", path=name, as_attachment=True)


# @app.route('/download_images', methods=['POST'])
# def download_images():
#     image_names = request.json.get('images', [])
#     if not image_names:
#         return jsonify({'status': 'error', 'message': 'No images selected'})
#
#     download_folder = 'downloads'
#     os.makedirs(download_folder, exist_ok=True)
#
#     for img in image_names:
#         img_path = os.path.join(IMAGE_FOLDER, img)
#         if os.path.exists(img_path):
#             os.system(f'cp "{img_path}" "{download_folder}/{secure_filename(img)}"')
#
#     return send_from_directory(directory=download_folder, path='.', as_attachment=True)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        file = request.files['file']
        spec = request.form
        filename = file.filename
    except Exception:
        return jsonify({'error': 'No file part in the request'}), 400

    path = os.path.join("/mnt/CamData/images", filename)

    if filename.endswith(".jpg"):
        db.insert_image(path.rstrip(".jpg"), spec)

    file.save(path)
    return jsonify({'message': f"File {filename} uploaded"}), 201
#
#
# @app.route('/upload_data/', methods=['POST'])
# def upload_data():
#     try:
#         db.insert_temp_humidity(request.form)
#     except Exception as e:
#         print(e)
#         return jsonify({'error': 'No message provided'}), 400
#
#     return jsonify({'message': 'Data uploaded'}), 201


# @app.route('/download_data_csv')
# def download_data_csv():
#     return send_from_directory(directory='.', path='camData.csv', as_attachment=True)


# @app.route('/get_setting/<camId>')
# def get_setting(camId):
#     return jsonify(settings)
# #
# #
# @app.route('/set_setting/<camId>', methods=['POST'])
# def set_setting(camId):
#     settings.update(request.json)
#     return jsonify({'status':
#     'success'})


# @app.route('/verify/<username>/<password>')
# def verify(username, password):
#     if username == 'admin' and password == 'admin':
#         return jsonify({'status': 'success'})
#     else:
#         return jsonify({'status': 'error', 'message': 'Invalid username or password'})

# @app.route('/images/<int:page>')
# def images(page: int):
#
#     def unpack_specs(f: str):
#         _, dt = f.split('_')
#         return dt, 0, 0
#
#     img_w_specs = [
#         (f, *unpack_specs(f))
#         for f in internal_states['displaying_list']
#     ]
#
#     def sort_func(i):
#         fname = i[0]
#         fname = fname.split(".")[0]
#         camid, timestamp_str = fname.split('_')
#         timestamp_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S")
#         return timestamp_dt
#
#     img_w_specs = sorted(img_w_specs, key=sort_func, reverse=True)
#     print(img_w_specs)
#     page_start = page * 8
#     page_end = page_start + 8
#
#     return jsonify(img_w_specs[page_start: page_end])
#
#
# def scan_images() -> list[str]:
#     img_dir = 'app/static/images/'
#     return [f.rstrip(".png") for f in os.listdir(img_dir) if f.endswith('.png')]
#
#
# @app.route('/get_total_pages')
# def get_total_pages():
#     internal_states['displaying_list'] = scan_images()
#     image_count = len(internal_states['displaying_list'])
#     pages = (image_count + 8 - 1) // 8
#     return jsonify({"totalPages": pages})


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


@app.route('/live')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




if __name__ == "__main__":
    app.run(debug=True, port=80, host='0.0.0.0')
