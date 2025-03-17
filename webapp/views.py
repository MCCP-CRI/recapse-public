import io
import os
import re
import shutil
import time
import zipfile

from flask import (
    Blueprint, flash, redirect, render_template, request, url_for, current_app as app, send_file
)
from werkzeug.utils import secure_filename

from . import preprocess, predict, executor, task_meta_data

bp = Blueprint('views', __name__)


@bp.route("/")
def index():
    return render_template('index.html.j2')


@bp.route("/predict", methods=['GET'])
def view_predict():
    return render_template('predict.html.j2')


@bp.route("/predict", methods=['POST'])
def submit_predict():
    errors = False
    error_msg = ""
    # get parameters from form
    sc = request.form['sc']
    fs = request.form['fs']
    model = request.form['model']
    method = int(request.form['method'])
    cutoff = float(request.form['cutoff'])
    user = request.form['user']

    # save files in new directory name based on user and microtime
    micro_time = time.time_ns() // 1000000
    work_folder = f"prediction_{user}_{micro_time}"
    work_dir = os.path.join(app.instance_path, work_folder)
    in_dir = os.path.join(work_dir, 'input')
    out_dir = os.path.join(work_dir, 'output')
    os.makedirs(work_dir)
    os.makedirs(in_dir)
    os.makedirs(out_dir)

    if not errors and 'chrname' in request.files:
        chrfile = request.files['chrname']
        chrfileFilename = secure_filename(chrfile.filename)
        chrfile.save(os.path.join(in_dir, chrfileFilename))
    else:
        errors = True
        error_msg = "Metadata CSV required"

    if not errors and 'inputname' in request.files:
        infile = request.files['inputname']
        infileFilename = secure_filename(infile.filename)
        infile.save(os.path.join(in_dir, infileFilename))
    else:
        errors = True
        error_msg = "Medicare Claims file required"

    if not errors:
        # save run info and pass info off to prediction function
        task_meta_data[work_folder] = {}
        task_meta_data[work_folder]['start_time'] = time.strftime('%m/%d/%Y %H:%M:%S')
        task_meta_data[work_folder]['run_options'] = {
            'feature_set': fs,
            'model': model,
            'cutoff': cutoff
        }
        executor.submit_stored(work_folder, predict.predict, fs, sc, model, infileFilename, chrfileFilename, cutoff,
                               method,
                               out_dir, in_dir)
        flash(f"Prediction task {work_folder} started.")
        return redirect(url_for('views.view_tasks'))
    else:
        flash(error_msg)
    return render_template('predict.html.j2')


@bp.route("/preprocess", methods=['GET'])
def view_preprocess():
    return render_template('preprocess.html.j2')


@bp.route("/preprocess", methods=['POST'])
def submit_preprocess():
    errors = False
    error_msg = ""
    # get parameters from form
    user = request.form['user']
    num_data = request.form['numdata']

    if 'mld' in request.form and request.form['mld'] is not None and request.form['mld'] != '':
        month_len_medicaid = int(request.form['mld'])
    else:
        month_len_medicaid = 0

    if 'mle' in request.form and request.form['mle'] is not None and request.form['mle'] != '':
        month_len_medicare = int(request.form['mle'])
    else:
        month_len_medicare = 0

    if 'sd' in request.form:
        start_medicaid = request.form['sd']
    else: 
        start_medicaid = 0

    if 'se' in request.form: 
        start_medicare = request.form['se']
    else:
        start_medicare = 0
    drug_code = request.form['dc']

    # save files in new directory name based on user and microtime
    user = re.sub(r'\s+', '_', user)
    user = re.sub(os.path.sep, '_', user)
    micro_time = time.time_ns() // 1000000
    job_name = f"preprocess_{user}_{micro_time}"
    work_dir = os.path.join(app.instance_path, job_name)
    in_dir = os.path.join(work_dir, 'input')
    out_dir = os.path.join(work_dir, 'output')
    os.makedirs(work_dir)
    os.makedirs(in_dir)
    os.makedirs(out_dir)
    metacsvFilename = None
    mecareClaimsFilename = None
    mecareEnrollFilename = None
    mecaidClaimsFilename = None
    mecaidClaims2Filename = None
    mecaidEnrollFilename = None

    if not errors and 'metacsv' in request.files and request.files['metacsv'].filename != '':
        metacsv = request.files['metacsv']
        metacsvFilename = secure_filename(metacsv.filename)
        metacsv.save(os.path.join(in_dir, metacsvFilename))
    else:
        errors = True
        error_msg = "Incidence Metadata CSV required"

    if num_data == "0" or num_data == "1":
        if not errors and 'mecareClaims' in request.files and request.files['mecareClaims'].filename != '':
            mecareClaims = request.files['mecareClaims']
            mecareClaimsFilename = secure_filename(mecareClaims.filename)
            mecareClaims.save(os.path.join(in_dir, mecareClaimsFilename))
        else:
            errors = True
            error_msg = "Medicare Claims file required"

        if not errors and 'mecareEnroll' in request.files and request.files['mecareEnroll'].filename != '':
            mecareEnroll = request.files['mecareEnroll']
            mecareEnrollFilename = secure_filename(mecareEnroll.filename)
            mecareEnroll.save(os.path.join(in_dir, mecareEnrollFilename))
        else:
            errors = True
            error_msg = "Medicare Enrollment file required"

    if num_data == "0" or num_data == "2":
        if not errors and 'mecaidClaims' in request.files and request.files['mecaidClaims'].filename != '':
            mecaidClaims = request.files['mecaidClaims']
            mecaidClaimsFilename = secure_filename(mecaidClaims.filename)
            mecaidClaims.save(os.path.join(in_dir, mecaidClaimsFilename))
        else:
            errors = True
            error_msg = "Medicaid/Other Claims file required"

        if not errors and 'mecaidClaims2' in request.files and request.files['mecaidClaims2'].filename != '':
            mecaidClaims2 = request.files['mecaidClaims2']
            mecaidClaims2Filename = secure_filename(mecaidClaims2.filename)
            mecaidClaims2.save(os.path.join(in_dir, mecaidClaims2Filename))
        else:
            errors = True
            error_msg = "Medicaid/Other Pharmacy Claims file required"

        if not errors and 'mecaidEnroll' in request.files and request.files['mecaidEnroll'].filename != '':
            mecaidEnroll = request.files['mecaidEnroll']
            mecaidEnrollFilename = secure_filename(mecaidEnroll.filename)
            mecaidEnroll.save(os.path.join(in_dir, mecaidEnrollFilename))
        else:
            errors = True
            error_msg = "Medicaid/Other Enrollment file required"

    # pass info off to executor
    if not errors:
        executor.submit_stored(job_name, preprocess.preprocess_data,
                               user, num_data, in_dir, out_dir, metacsvFilename, mecareClaimsFilename,
                               mecareEnrollFilename,
                               mecaidClaimsFilename, mecaidClaims2Filename, mecaidEnrollFilename, month_len_medicaid,
                               month_len_medicare,
                               start_medicaid, start_medicare, drug_code)
        flash(f"Task {job_name} started")
        task_meta_data[job_name] = {}
        task_meta_data[job_name]['start_time'] = time.strftime('%m/%d/%Y %H:%M:%S')
        task_meta_data[job_name]['run_options'] = {
            'num_data': num_data,
            'mon_len_medicaid': month_len_medicaid,
            'mon_len_medicare': month_len_medicare,
            'start_medicaid': start_medicaid,
            'start_medicare': start_medicare,
            'drug_code': drug_code
        }
        return redirect(url_for('views.view_tasks'))
    else:
        flash(error_msg)
    return render_template('preprocess.html.j2')


@bp.route('/tasks')
def view_tasks():
    task_status = []
    for task_name in executor.futures._futures.keys():
        ts = {}
        ts['task_name'] = task_name
        ts['task_status'] = executor.futures._futures[task_name]._state
        if ts['task_status'] == 'FINISHED' and executor.futures._futures[task_name].exception() is not None:
            ts['task_message'] = executor.futures._futures[task_name].exception()
            ts['task_status'] = 'ERROR'
        else:
            if task_name in task_meta_data and 'start_time' in task_meta_data[task_name]:
                ts['task_message'] = task_meta_data[task_name]['start_time']
        task_status.append(ts)
    return render_template('tasks.html.j2', task_status=task_status)


@bp.route('/tasks/<string:task_name>/download')
def download_task(task_name: str):
    # work dir shouldn't contain slashes because of the flask string converter, but just in case sanitize the path to
    # prevent escape. it will remove the passed directory tree at the end of this so best to be extra safe...
    work_dir = os.path.relpath(os.path.normpath(os.path.join("/", task_name)), "/")
    work_dir = os.path.join(app.instance_path, work_dir)
    out_dir = os.path.join(work_dir, "output")

    # zip up output files - out_dir/*.csv
    files = []
    if task_name.startswith('preprocess'):
        for dirpath, dirnames, filenames in os.walk(out_dir):
            for file in filenames:
                if file.startswith('All_11E_') or file.startswith('8_PatientLevel_char_'):
                    files.append(os.path.join(dirpath, file))
    if task_name.startswith('prediction'):
        files = list(filter(lambda x: x.endswith('.csv'), os.listdir(out_dir)))

    file_obj = io.BytesIO()
    with zipfile.ZipFile(file_obj, 'w') as zip_file_handle:
        for file in files:
            zip_info = zipfile.ZipInfo(os.path.basename(file))
            zip_info.date_time = time.localtime(time.time())[:6]
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            with open(os.path.join(out_dir, file), 'rb') as read_file_handle:
                zip_file_handle.writestr(zip_info, read_file_handle.read())
    file_obj.seek(0)

    return send_file(file_obj, mimetype="application/zip", download_name=f'{task_name}.zip', as_attachment=True)


@bp.route("/tasks/<string:task_name>/view")
def view_task_result(task_name: str):
    # sanitize work dir
    work_dir = os.path.relpath(os.path.normpath(os.path.join("/", task_name)), "/")
    work_dir = os.path.join(app.instance_path, work_dir)
    if task_name.startswith('prediction'):
        stats = predict.summary_stats(work_dir)
        return render_template('predict_result.html.j2', task_name=task_name,
                               run_options=task_meta_data[task_name]['run_options'], results=stats)
    elif task_name.startswith('preprocess'):
        stats = preprocess.summary_stats(work_dir)
        return render_template('preprocess_result.html.j2', task_name=task_name,
                               run_options=task_meta_data[task_name]['run_options'], results=stats)


@bp.route('/tasks/<string:task_name>/remove')
def remove_task(task_name: str):
    # delete the whole working directory
    work_dir = os.path.relpath(os.path.normpath(os.path.join("/", task_name)), "/")
    work_dir = os.path.join(app.instance_path, work_dir)
    shutil.rmtree(work_dir)
    if task_name in task_meta_data:
        task_meta_data.pop(task_name)
    # remove the Future from the executor's list
    if executor.futures.pop(task_name) is not None:
        flash(f"Task {task_name} removed")
    return redirect(url_for('views.view_tasks'))

# @bp.route('/debug')
# """Function to invoke web debugger if debugging is enabled on flask server"""
# def break_stuff():
#     raise ValueError("you broke it")
