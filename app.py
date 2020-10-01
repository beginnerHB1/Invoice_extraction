
from flask import Flask, flash, request,render_template,  redirect, url_for, jsonify
import json
from australia2 import *
from unicareer2 import *
from werkzeug.utils import secure_filename
import os

# UPLOAD_FOLDER = "data\\"
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = '1242341515136'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/test', methods=['GET', 'POST'])
def test():
    return {"response":"working"}


@app.route('/<company_name>', methods=['GET', 'POST'])
def upload_file1(company_name):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        global filename
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash('file {} saved'.format(file.filename))
            file.save(filename)

        if company_name == "australia":
            try:
                response = find_details_australia(filename)
                os.remove(filename)
                return json.dumps(response, ensure_ascii=False)
            except Exception as e:
                os.remove(filename)
                return json.dumps({"response":"please upload australia pdfs"}, ensure_ascii=False)

        elif company_name == "unicarriers":
            # return {"response":f"{filename}"}
            try:
                response = extract_detail(filename)
                os.remove(filename)
                return json.dumps(response, ensure_ascii=False)
            except Exception as e:
                os.remove(filename)
                return json.dumps({"response":"please upload unicareers pdfs"}, ensure_ascii=False)
    return render_template('home.html')


@app.route('/auto', methods=['GET', 'POST'])
def upload_file2():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        global filename
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash('file {} saved'.format(file.filename))
            file.save(filename)


        try:

            response = find_details_australia(filename)
            os.remove(filename)
            return json.dumps(response, ensure_ascii=False)

        except:

            try:
                response = extract_detail(filename)
                os.remove(filename)
                return json.dumps(response, ensure_ascii=False)

            except Exception as e:
                os.remove(filename)
                return json.dumps({"response":"Please upload pdf only for Unicareers/Australia's supplier for POC"}, ensure_ascii=False)
    return render_template('home.html')
if __name__ == '__main__':
	app.run(threaded=True,debug=True)
