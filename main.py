from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import re
import camelot
import pandas

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/history', methods=['POST'])
def get_history_data():
    file = request.files['file']
    file_path = save_file(file)

    history_tables = camelot.read_pdf(file_path, pages='all', line_scale=35)
    pending_courses = get_pending_courses(history_tables)

    return jsonify(pending_courses)


def save_file(file):
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    return file_path


def get_pending_courses(history_tables):
    pending_courses_tables = []

    for table in history_tables:
        if is_pending_courses_table(table):
            pending_courses_tables.append(table.df.iloc[1:, :])

    pending_courses = pandas.concat(pending_courses_tables)[0].to_numpy()

    return sanitize_courses(pending_courses)


def is_pending_courses_table(table):
    return len(table.df.columns) == 3 and table.df.iloc[0, 1] == "Componente Curricular"


def sanitize_courses(courses):
    regex = re.compile(r"[A-Z]{3}[0-9]{4}")
    return [i for i in courses if regex.match(i)]
