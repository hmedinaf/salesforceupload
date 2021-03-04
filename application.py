import os
import sys
import beatbox
import datetime
import csv

from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename

application = Flask(__name__)
application.secret_key = "SecretKey1234"

#UPLOAD_FOLDER="/home/ec2-user/environment/api_call/files"
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'files')
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'csv'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

sf = beatbox._tPartnerNS

# "salesforceusername and password"
username = 'hmedfrias@resilient-narwhal-hdgymy.com'
password = "H9Mekaaq"
token    = 'cXHXhY4XKqZxa2TuAQcG2rcm'
"""connect and authenticate"""
svc = beatbox.Client()
svc.login(username, password+token)

def new_lead(fname, lname, company):
    print("\ncreate")
    a = {'type': 'Lead',
        'FirstName': fname,
        'LastName': lname,
        'Company': company,
        'Status': 'Open - Not Contacted',
        'Description': 'Inserted with api call'
    }
    sr = svc.create([a])

    if str(sr[sf.success]) == 'true':
        print("id " + str(sr[sf.id]))
    else:
        print("error " + str(sr[sf.errors][sf.statusCode]) + ":" + str(sr[sf.errors][sf.message]))

"""Leer archivo y ejecutar servicio de alta de Leads"""
def process_file(filename):
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count=0
    
        for line in csv_reader:
            #quitar header
            if line_count==0:
                line_count += 1
            else:
                flash("insertando: %s %s %s" % (line[0], line[1], line[2]))
                new_lead(line[0], line[1], line[2])
                line_count += 1

@application.route('/')
def main():
    return ("Path %s" % UPLOAD_FOLDER)
    
@application.route('/upload')
def upload_form():
    return render_template('upload.html')

@application.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(application.config['UPLOAD_FOLDER'], filename))
            completefilename = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            flash('File successfully uploaded: %s' % filename)
            """Dar de alta en Salesforce"""
            process_file(completefilename)
            return redirect('/upload')
        else:
            flash('Allowed file types are txt, csv')
            return redirect(request.url)

if __name__ == '__main__':
    host=os.getenv('IP', '0.0.0.0')
    port=int(os.getenv('PORT', 5000))
    application.debug=True
    application.run(host=host, port=port)
    