import os
import datetime
import threading
import cv2
from flask_cors import CORS


import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory, Response, send_file


from app.database import Database

app = Flask(__name__, static_folder='static')
CORS(app)  # This will allow all domains by default
db = Database()

frame_lock = threading.Lock()
latest_frame = None


settings = {}


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
    header = ["image", "datetime", "expTime", "eGain", "siteName", "UID", "timeZone"]
    fields = ["Images.ImgPath", "Images.[Datetime]", "Images.ExpTime", "Images.Gain", "Cameras.SiteName", "Images.UID",
              "Images.timeZone"]
    table = "Images INNER JOIN Cameras ON Images.CamId = Cameras.CamId"
    sql = f"SELECT {",".join(fields)} FROM {table} "

    if conditions or last_uid:
        sql += "WHERE "

    if conditions:
        sql += f"{conditions} "

    if last_uid:
        if conditions:
            sql += "and "
        sql += f"Images.UID {order == "DESC" and "<" or ">"} {last_uid} "

    sql += f"ORDER BY Images.[Datetime] {order} OFFSET 0 ROWS FETCH NEXT {pagesize} ROWS ONLY"

    result = db.query(sql)
    result = [{k: v for k, v in zip(header, row)} for row in result]
    return jsonify(result)


@app.route("/get_file/<path:filepath>")
def get_file(filepath):
    return send_file(f"/{filepath}", as_attachment=False)


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


# @app.route('/upload_image', methods=['POST'])
# def upload_image():
#     try:
#         file = request.files['file']
#         spec = request.form
#         filename = file.filename
#     except Exception:
#         return jsonify({'error': 'No file part in the request'}), 400
#
#     path = os.path.join("/mnt/CamData/images", filename)
#
#     if filename.endswith(".jpg"):
#         db.insert_image(path.rstrip(".jpg"), spec)
#
#     file.save(path)
#     return jsonify({'message': f"File {filename} uploaded"}), 201
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
