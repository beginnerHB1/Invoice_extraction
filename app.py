from flask import Flask, flash, request,render_template,  redirect, url_for
import json
import os
from werkzeug.utils import secure_filename
from all_functions import *


try:
    os.mkdir("data")
except:
    pass

UPLOAD_FOLDER = "data/"
ALLOWED_EXTENSIONS = set(['pdf'])

app = Flask(__name__)
app.secret_key = '1242341515136'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        # try:

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        global filename
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            flash('file {} saved'.format(file.filename))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # file1 = open("/home/senseque/Desktop/new/testing/myfile.txt","w")
            # file1.write(f"{filename}")
            # file1.close()
            z = extract_detail(f"data/{filename}")
            print(filename)
            return z

    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)
