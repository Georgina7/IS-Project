from flask import Flask, render_template, session, request, redirect, url_for
import os
# import cv2
# import numpy as np
import pickle
import pyrebase
import firebase_admin
from model import *
from firebase_admin import firestore
from firebase_admin import credentials

UPLOAD_FOLDER = './static/images'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

config = {
    'apiKey': "AIzaSyDun9D8j0McAzdocexs28MSVPJ4TwYnnEM",
    'authDomain': "is-project-d3db4.firebaseapp.com",
    'projectId': "is-project-d3db4",
    'storageBucket': "is-project-d3db4.appspot.com",
    'messagingSenderId': "101040743578",
    'appId': "1:101040743578:web:ee6a4164ab9321eb0b6b23",
    'measurementId': "G-6DH7ZZZ11R",
    'databaseURL': ""
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app.secret_key = 'secret'
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
# data = {
#     'case_no':101
# }

# case_ref = db.collection(u'cases').add(data)
# case_id = case_ref[1].id

# data = {
#     'day_no':1,
#     'case_id':case_id
# }
# day1_ref = db.collection(u'days').add(data)
# day1 = day1_ref[1].id

# data = {
#     'day_no':2,
#     'case_id':case_id
# }
# day2_ref = db.collection(u'days').add(data)
# day2 = day2_ref[1].id

# data = {
#         'case_id':case_id,
#         'day_id':day1,
#         'scan_no':1,
#         'scan_path':'scan_path_1'
#     }
# db.collection(u'mri_scans').add(data)

# data = {
#         'case_id':case_id,
#         'day_id':day1,
#         'scan_no':2,
#         'scan_path':'scan_path_2'
#     }
# db.collection(u'mri_scans').add(data)

# data = {
#         'case_id':case_id,
#         'day_id':day2,
#         'scan_no':1,
#         'scan_path':'scan_path_1'
#     }
# db.collection(u'mri_scans').add(data)



# db.collection(u'physicians').add(data)
# data = {
#     'first_name':'Charles',
#     'last_name':'Bonge',
#     'email':'charlesbonge@gmail.com'
# }
# db.collection(u'physicians').add(data)

# docs = db.collection(u'physicians').stream()
# for doc in docs:
#     print(f'{doc.id} => {doc.to_dict()}')

@app.route("/", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = email
            return redirect("/landing")
        except:
            return 'Failed to login'
    return render_template("login.html")

@app.route("/sign_up", methods=['POST', 'GET'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        if request.form.get('password') == request.form.get('confirm-password'):
            password = request.form.get('password')
        else:
            return 'Passwords do not match'
        try:
            user = auth.create_user_with_email_and_password(email, password)
            return redirect("/")
        except:
            return 'Failed to sign up'
    return render_template("sign_up.html")

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/")

# View all cases
@app.route("/landing", methods=['GET'])
def landing():
    if('user' in session):        
        case_docs = db.collection(u'cases').stream()
        cases = {}
        for case in case_docs:
            # cases[case.id] = case.to_dict()['case_no']
            days_docs = db.collection(u'days').where('case_id', u'==', case.id).stream()
            days = {}
            for day in days_docs:
                days[day.id] = day.to_dict()            
            cases[case.id] = [len(days), case.to_dict()['case_no']]
        return render_template("index.html", cases=cases)
    else:
        return redirect("/")

# View a case's days
@app.route("/cases/<case_id>/<case_no>", methods=['GET'])
def case(case_id=None, case_no=None):
    if('user' in session):
        session['case_id'] = case_id
        session['case_no'] = case_no
        days_docs = db.collection(u'days').where('case_id', u'==', case_id).stream()
        days = {}
        for day in days_docs:
            scans_docs = db.collection(u'mri_scans').where(u'day_id', u'==', day.id).stream()
            scans = {}
            for scan in scans_docs:
                scans[scan.id] = scan.to_dict()
            days[day.id] = [day.to_dict(), scans]
        

        # Change template name to case.html
        return render_template("case.html", days=days, case_no=case_no)
    else:
        return redirect("/")

# View a day's scans
@app.route("/days/<day_id>", methods=['GET'])
def day(day_id=None):
    if('user' in session):
        session['day_id'] = day_id
        docs = db.collection(u'mri_scans').where(u'day_id', u'==', day_id).stream()
        scans = {}
        for doc in docs:
            scans[doc.id] = doc.to_dict()
        
        # Change template name to case.html
        return render_template("case.html", scans=scans)
    else:
        return redirect("/")

# Add new day to case
@app.route("/add_day", methods=['POST'])
def add_day():
    try:
        day_no = request.form.get('day__number')
        data = {
            'day_no':day_no,
            'case_id':session['case_id']
        }
        db.collection(u'days').add(data)
        return redirect(url_for('case', case_id=session['case_id'], case_no=session['case_no']))
    except:
        return 'Failed to add day'

# Add a new scan to day
@app.route("/add_scan/<day_id>", methods=['POST'])
def add_scan(day_id=None):
    try:        
        scan = request.files['scan_file']
        path = os.path.join(app.config['UPLOAD_FOLDER'], scan.filename)
        scan.save(path)
        scan_no = request.form.get('scan__number')
        data = {
            'case_id':session['case_id'],
            'day_id':day_id,
            'scan_no': scan_no,
            'scan_path':path
        }
        
        db.collection(u'mri_scans').add(data)
        return redirect(url_for('case', case_id=session['case_id'], case_no=session['case_no']))
    except:
        return 'File not uploaded'

# Add new case
@app.route("/add_case", methods=['POST'])
def add_case():
    try:
        case_no = request.form.get('case__number')
        data = {
            'case_no':case_no
        }
        db.collection(u'cases').add(data)
        return redirect("/landing")
    except:
        return 'Failed to add case'

# Perform image segmentation
# Read image from database and preprocess,
# Pass image to model to segment
# model.predict -> show predictions
# overlap the mask on scan ?????
@app.route("/organ_contouring/<scan_id>", methods=['POST', 'GET'])
def organ_contouring(scan_id=None):
    if('user' in session):
        # Get scan path
        scan = db.collection(u'mri_scans').document(scan_id).get()
        path = scan.to_dict()['scan_path']
        predict(path)        
        return render_template("prediction.html")
    else:
        return redirect("/")
    
    
if __name__ == "__main__":
    app.run(debug=True)