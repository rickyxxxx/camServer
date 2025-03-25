from flask import Flask, render_template, request, jsonify, send_from_directory
import pyodbc
import os
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__, static_folder='static', template_folder='static/templates')


temp_hum_list = [[], [], []]
settings = {
    "day_gain": 10,
    "day_exp": 10,
    "day_int": 30,
    "night_gain": 10,
    "night_exp": 10,
    "night_int": 30
}

# Configuration for MSSQL
db_config = {
    'server': 'localhost',
    'database': 'cameraDB',
    'username': 'SA',
    'password': 'server@2025'
}

connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER=ALIENWARE;'
    f'DATABASE={db_config['database']};'
    f'Trusted_Connection=yes;'
)

IMAGE_FOLDER = 'image/png'


@app.route('/')
def index():
    return render_template('gallery.html')


@app.route('/CMS')
def management_system():
    return render_template('login.html')


@app.route('/get_images', methods=['POST'])
def get_images():
    offset = int(request.json.get('offset', 0))
    limit = int(request.json.get('limit', 20))
    cmd = 'SELECT imgName FROM ImageInfo ORDER BY [datetime] OFFSET ? ROWS FETCH NEXT ? ROWS ONLY'
    sql_query = request.json.get('query', cmd)

    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            if 'OFFSET' not in sql_query:
                sql_query += f' OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY'
            cursor.execute(sql_query)
            images = [row[0] for row in cursor.fetchall()]
        return jsonify({'status': 'success', 'images': images})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


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
    else:
        return jsonify({'error': 'Invalid file format'}), 400

    path = os.path.join("static/images", folder, filename)
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
        _, datetime, exp, gain = f.split('_')
        return datetime, exp, gain, 0

    img_w_specs = [
        (f, *unpack_specs(f))
        for f in internal_states['displaying_list']
    ]

    def sort_func(i):
        fname = i[0]
        _, timestamp_str, _, _ = fname.split('_')
        timestamp_dt = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return timestamp_dt

    img_w_specs = sorted(img_w_specs, key=sort_func, reverse=True)

    page_start = page * 8
    page_end = page_start + 8

    return jsonify(img_w_specs[page_start: page_end])


def scan_images() -> list[str]:
    img_dir = 'static/images/png'
    return [
        f.rstrip('.png')
        for f in os.listdir(img_dir)
        if f.endswith('.png')
    ]

@app.route('/get_total_pages')
def get_total_pages():
    internal_states['displaying_list'] = scan_images()
    image_count = len(internal_states['displaying_list'])
    pages = (image_count + 8 - 1) // 8
    return jsonify({"totalPages": pages})


if __name__ == '__main__':
    internal_states = {
        'settings': {'gain': 150, 'offset': 0, 'exposure': 100000, 'interval': 0},
        'current_tag': None,
        'displaying_list': scan_images(),
        'eta': "",
    }
#    app.run(port=5000, host='0.0.0.0')
    app.run(debug=True, port=80, host='0.0.0.0')
