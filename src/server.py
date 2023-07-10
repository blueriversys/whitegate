"""
https://towardsdatascience.com/virtual-environments-104c62d48c54

How to set the virtual env:
. python3 -m venv <virtual-env-folder>  (ex. python3 -m venv myvenv)
. or
. virtualenv venv -p python3.7 (whichever you want)
. source myvenv/bin/activate (to activate)
. deactivate
. myvenv/bin/deactivate
. pip freeze > requirements.txt (creates a requirements.txt)
. pip install -r requirements.txt
. pip show pyrebase4

This has some interesting tips on how to set up Firebase:
https://pythonalgos.com/python-firebase-authentication-integration-with-fastapi/

These are the commands to install Firebase libraries:
. pip install pyrebase4
. pip install firebase-admin
. pip install requests-toolbelt==0.10.1

To run the server program:
. python server.py  (no need to say python3)

"""

from users import users_repository
from users import User
from datetime import timedelta, datetime

from flask import Flask, request, session, abort, redirect, Response, url_for, render_template, send_from_directory, flash
from flask_login import LoginManager, login_required, UserMixin, login_user, logout_user, current_user
import os
from glob import glob
from werkzeug.utils import secure_filename
import smtplib
import cgitb
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
from random import randint
#import pyrebase
#import firebase_admin
#from firebase_admin import credentials
#from firebase_admin import db
from firebase import Firebase
from uuid import uuid4

''' for simulation of long running tasks '''
from threading import Thread
import random
from time import sleep

#import logging
# https://realpython.com/python-logging/
#logging.basicConfig(filename='whitegate.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
#prevents http server messages from going to the log file
#logging.getLogger('werkzeug').disabled = True

app = Flask(
            __name__, 
            static_url_path='', 
            static_folder='static',
            template_folder='templates'
           )

app.config['SECRET_KEY'] = 'secret@whitegate#key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'login'
login_manager.needs_refresh_message = (u'Due to inactivity, you have been logged out. Please login again')
login_manager.needs_refresh_message_category = 'info'


WHITEGATE_EMAIL = 'info@whitegatecondo.com'
WHITEGATE_NAME = 'Whitegate Condo'
GMAIL_WHITEGATE_EMAIL = 'whitegatecondoinfo@gmail.com'
SERVER_FOLDER = 'serverfiles'
UPLOADED_FOLDER = 'uploadedfiles'
RESIDENTS_DB = SERVER_FOLDER + "/" + "residents.json"
ANNOUNCS_FILE = SERVER_FOLDER + "/" + "announcs.dat"
LOG_FILE = SERVER_FOLDER + "/" + "whitegate.log"
CONFIG_FILE = SERVER_FOLDER + "/" + "config.dat"
PROTECTED_FOLDER = UPLOADED_FOLDER + "/protected"
UNPROTECTED_FOLDER = UPLOADED_FOLDER + "/unprotected"
email_percent = 1

cgitb.enable()

# read config info to extract DB connection
with open(CONFIG_FILE, 'r') as f:
    strContent = f.read()
    jsonObj = json.loads(strContent)
    config = jsonObj['config']

print(f" service account: {config['service-account-filename']},   database url: {config['database-url']}")
fireDB = Firebase(config['service-account-filename'], config['database-url'])

'''
 This is invoked from main() to read the residents
 json file from disk and fill a user dict
'''
def load_users():
    with open(RESIDENTS_DB, 'r') as f:
        str_content = f.read()
        json_obj = json.loads(str_content)
        residents = json_obj['residents']
        for resident in residents:
            user = User(
                users_repository.next_index(),
                resident['unit'],
                resident['userid'],
                resident['password'],
                resident['name'],
                resident['email'],
                resident['startdt'],
                resident['phone'],
                resident['type'],
                resident['ownername'],
                resident['owneremail'],
                resident['ownerphone'],
                resident['occupants']
            )
            users_repository.add_user_to_dict(user)

''' These are long running related functions '''
def email_task(subject, body):
    global email_percent
    email_to = get_all_emails()
    total_count = len(email_to)
    print(f" total count {total_count}")
    count = 0
    for single_email_to in email_to:
        send_email_relay_host(single_email_to, subject, body)
        count += 1
        email_percent = int( (count / total_count ) * 100 )
        #sleep(2)

    #   FOR TESTING PURPOSES ONLY
    #    for single_email_to in emailto:
    #        print(f'sending email to {single_email_to}')
    #        subj = mailObj['request']['subject']
    #        subject = subj + ",   " + single_email_to
    #        single_email_to = GMAIL_WHITEGATE_EMAIL
    #        send_email_relay_host(single_email_to, subject, body)

    email_percent = 100


'''
  will send email to all residents, one by one
'''
@app.route('/sendmail', methods=['POST'])
def start_email_task():
    global email_percent
    email_percent = 1
    t1 = Thread(target=email_task, args=(request.get_json()['subject'], request.get_json()['body']))
    t1.start()
    status = {'percent': email_percent}
    return json.dumps(status)

@app.route('/getstatus', methods=['GET'])
def get_status():
    status = {'percent': email_percent}
    return json.dumps(status)


'''
  These are folder related routes
'''
@app.route('/docs/<path:filename>')
@login_required
def protected(filename):
    #return send_from_directory(app.static_folder + '/docs', filename)
    return send_from_directory(PROTECTED_FOLDER + '/docs', filename)

@app.route('/opendocs/<path:filename>')
def unprotected(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/opendocs', filename)

# Custom static data
@app.route('/pics/<path:filename>')
def custom_static(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/pics', filename)

@app.route('/logos/schools/<path:filename>')
def custom_static_schools(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/logos/schools', filename)

@app.route('/logos/employers/<path:filename>')
def custom_static_employers(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/logos/employers', filename)

@app.route('/logos/hospitals/<path:filename>')
def custom_static_hospitals(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/logos/hospitals', filename)

@app.route('/logos/shopping/<path:filename>')
def custom_static_shopping(filename):
    return send_from_directory(UNPROTECTED_FOLDER + '/logos/shopping', filename)

'''
  These are GET request routes
'''
@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/home')
def home():
#    return "<h1>" + current_user.username + "'s Home</h1>"
#
#    name = 'joe silva'
#    if not session.get("USERNAME") is None:
#        usern = session.get("USERNAME")
#        print(f"user name is {usern}")
#    else:
#        session['USERNAME'] = name
#        print(f"user name is now set to {name}")

#    if current_user.is_authenticated:
#        print(f'home(): authenticated request, loggedin user: {current_user.username}   user.type {current_user.type}')
#    else:
#        print(f'home(): non-authenticated request')

#    if session.get('USERNAME') is None:
#        name = 'session_name'
#        session['USERNAME'] = name
#        print(f"session['USERNAME'] is now set to {name}")

#    if session.get('USERNAME') is not None:
#        print(f'session["USERNAME"] is {session["USERNAME"]}')

    pictures = get_files(UNPROTECTED_FOLDER + '/pics', '')
    return render_template("home.html", pics=pictures)

@app.route('/about')
def about():
    employers = get_files(UNPROTECTED_FOLDER + '/logos/employers', '')
    schools = get_files(UNPROTECTED_FOLDER + '/logos/schools', '')
    hospitals = get_files(UNPROTECTED_FOLDER + '/logos/hospitals', '')
    shopping = get_files(UNPROTECTED_FOLDER + '/logos/shopping', '')
    return render_template("about.html", emp_logos=employers, school_logos=schools, hosp_logos=hospitals, shop_logos=shopping)

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/getannouncs')
def get_announc_list():
    announc_list = []
    with open(ANNOUNCS_FILE, 'r') as f:
        announc = ''
        for index, line in enumerate(f):
            if len(line.strip()):
                announc = announc + line
            else:
                if len(announc.strip()):
                    announc_list.append(announc)
                    announc = ''

    # append the last block of announc lines
    if len(announc.strip()):
        announc_list.append(announc)

    json_obj = {'announcs':announc_list}
    return json.dumps(json_obj)

@app.route('/announcs')
def announcs():
    openfiles = get_files(UNPROTECTED_FOLDER + '/opendocs/files', '')
    return render_template("announcs.html", openfiles=openfiles)

@app.route('/docs')
def get_docs():
    open_docs = get_files(UNPROTECTED_FOLDER + '/opendocs/files', '')
    if current_user.is_authenticated:
        docs2020 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2020')
        docs2021 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2021')
        docs2022 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2022')
        docs2023 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2023')
        bylaws = get_files(PROTECTED_FOLDER + '/docs/bylaws', '')
        other_docs = get_files(PROTECTED_FOLDER + '/docs/other', '')
        return render_template("docs.html", bylaws=bylaws, otherdocs=other_docs, opendocs=open_docs, findocs2020=docs2020, findocs2021=docs2021, findocs2022=docs2022, findocs2023=docs2023)
    else:
        return render_template("opendocs.html", opendocs=open_docs)

@app.route('/users')
@login_required
def get_users():
    all_users = []

    if current_user.is_authenticated and current_user.type == '0':
        for key in users_repository.get_users():
            user = users_repository.get_user_by_unit(key)
            all_users.append(user)
            #print(f' key {key}  id {user.id}  name {user.username}  pass {user.password}   type {user.get_type()}')

    return render_template("users.html", users=all_users)

@app.route('/residents')
def get_residents():
    all_users = []
    for key in users_repository.get_users():
        user = users_repository.get_user_by_unit(key)
        all_users.append(user)
    return render_template("residents.html", users=all_users)

@app.route('/getresidents')
def get_residents_json():
    resident_list = []
    i = 0

    for key in users_repository.get_users():
        user = users_repository.get_user_by_unit(key)
        if current_user.type == '0':
            passw = user.password
        else:
            passw = ''
        resident_list.append( {'unit':user.unit,
                               'userid':user.userid,
                               'password':passw,
                               'name':user.name,
                               'email':user.email,
                               'startdt':user.startdt,
                               'phone':user.phone,
                               'type':user.type,
                               'ownername': user.ownername,
                               'owneremail': user.owneremail,
                               'ownerphone': user.ownerphone,
                               'occupants': user.occupants
                               } )
        i += 1

    resident_list.sort(key=sort_criteria)
    json_obj = {'residents':resident_list}
    return json.dumps(json_obj)

@app.route('/getloggedinuser')
def get_loggedin_user():
    resident = {'userid':current_user.userid, 'unit':current_user.unit}
    return_obj = {'status': 'success', 'resident':resident}
    return json.dumps({'response': return_obj})

@app.route('/pics')
def pics():
    if 'event' in request.args:
        event = request.args['event']
        pictures = get_files(UNPROTECTED_FOLDER + '/pics/event' + event, '')
        return render_template("pics_events.html", pics=pictures)
    else:
        pictures = get_files(UNPROTECTED_FOLDER + '/pics', '')
        return render_template("pics.html", pics=pictures)

@app.route('/logout', methods=['GET'])
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    msg = f'user id {current_user.id}, {current_user.userid} logged out'
    log(msg)
    userid = current_user.userid  # we need to save the userid BEFORE invoking logout_user()
    logout_user()
    return render_template("logout.html", loggedout_user=userid)

'''
  These are POST request routes
'''
@app.route('/deletefile', methods=['POST'])
def delete_file():
    file_obj = request.get_json()
    filepath = file_obj['request']['filepath']
    filepath = PROTECTED_FOLDER + '/' + filepath if filepath.startswith('docs') else UNPROTECTED_FOLDER + '/' + filepath
    try:
        os.remove(filepath)
        status = 'success'
        log(f"userid {current_user.userid} deleted file {file_obj['request']['filename']}")
    except OSError:
        status = 'failure'
    return_obj = {'status': status}
    return json.dumps(return_obj)

#------------------------------------------------------------
# will send email to a resident
#------------------------------------------------------------
@app.route('/sendsinglemail', methods=['POST'])
def send_single_email():
    mailObj = request.get_json()
    emailto = mailObj['request']['emailto']
    subject = mailObj['request']['subject']
    body = mailObj['request']['body']
    if len(emailto.strip()):
        send_email_relay_host(emailto, subject, body)
    resp_dict = {'status' : 'success'}
    return_obj = {'response' : resp_dict}
    return json.dumps(return_obj)

@app.route('/saveannouncs', methods=["POST"])
def save_announc_list():
    announcsObj = request.get_json()
    announcs = announcsObj['announc']['lines']
    with open(ANNOUNCS_FILE, 'w') as f:
        f.write(announcs)
        f.close()

    return_obj = {'status' : 'success'}
    return json.dumps({'response' : return_obj})

@app.route('/getresident', methods=["POST"])
def get_resident_json():
    userObj = request.get_json()
    type = userObj['request']['type']
    id = userObj['request']['id']

    if type == 'user':
        user = users_repository.get_user_by_userid(id)
    else:
        user = users_repository.get_user_by_unit(id)

    if user == None:
        return_obj = {'status' : 'not_found'}
        return json.dumps({'response' : return_obj})

    if current_user.type == '0':
        passw = user.password
    else:
        passw = '******'

    resident = {
        'unit':user.unit,
        'userid':user.userid,
        'password':passw,
        'name':user.name,
        'email':user.email,
        'startdt':user.startdt,
        'phone':user.phone,
        'type': user.type,
        'ownername': user.ownername,
        'owneremail': user.owneremail,
        'ownerphone': user.ownerphone,
        'occupants': user.occupants
    }

    resp_dict = {'status' : 'success', 'resident':resident}
    return_obj = {'response':resp_dict}
    return json.dumps(return_obj)

@app.route('/saveresident', methods=["POST"])
def save_resident_json():
    json_obj = request.get_json()
    db_user = users_repository.get_user_by_unit(json_obj['resident']['unit'])

    if db_user is None:
        password = generate_password(json_obj['resident']['userid'])
        user = User(
            users_repository.next_index(),
            json_obj['resident']['unit'],
            json_obj['resident']['userid'],
            password,
            json_obj['resident']['name'],
            json_obj['resident']['email'],
            json_obj['resident']['startdt'],
            json_obj['resident']['phone'],
            json_obj['resident']['type'],
            json_obj['resident']['ownername'],
            json_obj['resident']['owneremail'],
            json_obj['resident']['phone'],
            json_obj['resident']['occupants']
        )
    else:
        db_user.name = json_obj['resident']['name']
        db_user.email = json_obj['resident']['email']
        db_user.startdt = json_obj['resident']['startdt']
        db_user.phone = json_obj['resident']['phone']
        db_user.ownername = json_obj['resident']['ownername']
        db_user.owneremail = json_obj['resident']['owneremail']
        db_user.ownerphone = json_obj['resident']['ownerphone']
        db_user.occupants = json_obj['resident']['occupants']
        user = db_user
        #print(f'delete before adding to db')
        #users_repository.delete_user(user)

    # this assign the user object on the hash (dict), where the unit is key, user is value
    users_repository.save_user(user)

    # save to firebase
    fireDB.insert_or_update_resident( user.get_json_data() )

    # save the entire list of users to a file
    users_repository.save_users_to_file(RESIDENTS_DB)

    return_obj = {'status': 'success'}
    return json.dumps({'response': return_obj})

@app.route('/saveresidentpartial', methods=["POST"])
def save_resident_partial():
    json_obj = request.get_json()
    db_user = users_repository.get_user_by_unit(json_obj['resident']['unit'])

    if db_user is None:
        return_obj = {'status': 'failure'}
        return json.dumps({'response': return_obj})
    else:
        db_user.userid = json_obj['resident']['userid']
        db_user.password = json_obj['resident']['password']
        db_user.name = json_obj['resident']['name']
        db_user.email = json_obj['resident']['email']
        db_user.phone = json_obj['resident']['phone']
        db_user.startdt = json_obj['resident']['startdt']
        db_user.type = json_obj['resident']['type']
        db_user.ownername = json_obj['resident']['ownername']
        db_user.owneremail = json_obj['resident']['owneremail']
        db_user.ownerphone = json_obj['resident']['ownerphone']
        db_user.occupants = json_obj['resident']['occupants']
        user = db_user

    # this assign the user object on the hash (dict), where the unit is key, user is value
    users_repository.save_user(user)

    fireDB.insert_or_update_resident( user.get_json_data() )

    # save the entire list of users to a file
    users_repository.save_users_to_file(RESIDENTS_DB)
    return_obj = {'status': 'success'}
    return json.dumps({'response': return_obj})

@app.route('/changepassword', methods=["POST"])
def change_password():
    userObj = request.get_json()
    dbUser = users_repository.get_user_by_unit(userObj['resident']['unit'])
    dbUser.password = userObj['resident']['password']

    # save this user in an internal structure
    users_repository.save_user(dbUser)

    # save to firebase
    fireDB.insert_or_update_resident( user.get_json_data() )

    # save the entire list of users to a file
    users_repository.save_users_to_file(RESIDENTS_DB)

    return_obj = {'status': 'success'}
    return json.dumps({'response': return_obj})

@app.route('/changeuserid', methods=["POST"])
def change_userid():
    userObj = request.get_json()
    dbUser = users_repository.get_user_by_unit(userObj['resident']['unit'])
    dbUser.userid = userObj['resident']['userid']

    # save this user in an internal structure
    users_repository.save_user(dbUser)

    # save to firebase
    fireDB.insert_or_update_resident( user.get_json_data() )

    # save the entire list of users to a file
    users_repository.save_users_to_file(RESIDENTS_DB)

    return_obj = {'status': 'success'}
    return json.dumps({'response': return_obj})


@app.route('/upload', methods=['GET' , 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        uploaded_convname = request.form['convname']
        file_size = request.form['filesize']
        print(f'size {file_size}  file name received {uploaded_file.filename}  special name: {uploaded_convname}')

        filename = secure_filename(uploaded_file.filename)
        filename = filename.replace('_', '-')
        filename = filename.replace(' ', '-')
        fullpath = ''
        if uploaded_convname == 'announc':
            fullpath = UNPROTECTED_FOLDER + '/opendocs/announcs/' + filename
        elif uploaded_convname == 'pubfile':
            fullpath = UNPROTECTED_FOLDER + '/opendocs/files/' + filename
        elif uploaded_convname == 'bylaws':
            fullpath = PROTECTED_FOLDER + '/docs/bylaws/' + filename
        elif uploaded_convname == 'otherdoc':
            fullpath = PROTECTED_FOLDER + '/docs/other/' + filename
        elif uploaded_convname == 'picture':
            fullpath = UNPROTECTED_FOLDER + '/pics/' + filename
        else:
            fullpath = PROTECTED_FOLDER + '/docs/financial/' + "Fin-" + uploaded_convname + ".pdf"

        uploaded_file.stream.seek(0)
        uploaded_file.save(fullpath)
        return render_template("upload.html")
    else:
        docs2020 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2020')
        docs2021 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2021')
        docs2022 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2022')
        docs2023 = get_files(PROTECTED_FOLDER + '/docs/financial', 'Fin-2023')
        bylaws = get_files(PROTECTED_FOLDER + '/docs/bylaws', '')
        otherdocs = get_files(PROTECTED_FOLDER + '/docs/other', '')
        opendocs = get_files(UNPROTECTED_FOLDER + '/opendocs/files', '')
        picts = get_files(UNPROTECTED_FOLDER + '/pics', '')
        return render_template("upload.html", bylaws=bylaws, otherdocs=otherdocs, opendocs=opendocs,
                               findocs2020=docs2020, findocs2021=docs2021,
                               findocs2022=docs2022, findocs2023=docs2023,
                               pics=picts)

@app.route('/login', methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        registered_user = users_repository.get_user_by_userid(userid)

        if registered_user is None:
            flash("Invalid userid or password")
            return render_template("login.html")

        next_page = request.args.get('next')

        if not next_page:
            next_page = url_for('home')

        if registered_user.password == password:
            #print('Login successful: user %s , password %s' % (registered_user.username, registered_user.password))
            msg = f'user {registered_user.userid} logged in'
            log(msg)
            login_user(registered_user)
            return redirect(next_page)
        else:
            #return abort(401)
            flash("Invalid userid or password")
            return render_template("login.html")
    else:
        return render_template("login.html")

@app.route('/register', methods = ['GET' , 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        registered_user = users_repository.get_user_by_userid(userid)

        if registered_user is not None:
            flash("User already exists.")
            return render_template("register.html")

        password = request.form['password']
        new_user = User(userid , password , users_repository.next_index())
        users_repository.save_user(new_user)

        # save to firebase
        fireDB.insert_or_update_resident(user.get_json_data())
        return Response("Registered Successfully")
    else:
        return render_template("register.html")


'''
  These are simply supporting functions (i.e not related to GET or POST)
'''
def log(msg):
    timestamp = get_timestamp()
    with open(LOG_FILE, "a") as f:
        f.write(f'{timestamp} {msg}\n')
        f.close()

def get_timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

def send_email_relay_host(emailto, subject, body):
    TO = emailto
    SUBJECT = subject
    BODY = body
    HOST = "localhost"

    # prepare message
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = WHITEGATE_NAME + ' <' + WHITEGATE_EMAIL + '>'
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY))
    email_list = TO.split(',') # creates a list from a comma-separated string

    # connect to server
    server = smtplib.SMTP(HOST)

    # now send email
    response = server.sendmail(WHITEGATE_EMAIL, email_list, msg.as_string())
    server.quit()
    
    # print email list
    # print(f'Message sent to emails: {email_list}')

def send_email_google(emailto, subject, body):
    FROM = "whitegatecondoinfo@gmail.com"
    TO = emailto
    SUBJECT = subject
    BODY = body

    # prepare message
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = FROM
    msg['To'] = TO
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY))
    email_list = TO.split(',') # creates a list from a comma-separated string

    # google gmail credentials
    email_user = "whitegatecondoinfo"
    email_password = "whitegate@2021"
    server = smtplib.SMTP_SSL('smtp.gmail.com', 587)
    server.starttls()
    server.ehlo()
    server.login(email_user, email_password)

    # now send email
    response = server.sendmail(FROM, email_list, msg.as_string())
    server.quit()

def get_all_emails():
    all_emails = []
    for key in users_repository.get_users():
        user = users_repository.get_user_by_unit(key)
        email = user.email.strip()
        if len(email):
            all_emails.append(email)
    msg = f'all emails {all_emails}'        
    log(msg)
    return all_emails

def sort_criteria(obj):
    return int(obj['unit'])

def generate_password(userid):
    number = randint(1, 9999)
    if number < 10:
        numberStr = "000" + str(number)
    elif number < 100:
        numberStr = "00" + str(number)
    elif number < 1000:
        numberStr = "0" + str(number)
    else:
        numberStr = str(number)
    return userid + '@' + numberStr

# handle login failed
@app.errorhandler(401)
def login_failed(e):
    return Response('<p>Login failed</p>')


# handle page not found
@app.errorhandler(404)
def page_not_found(e):
    return Response('<p>Sorry, page not found</p>')


@app.before_request
def before_request():
    session.permanent = True # doesn't destroy the session when the browser window is closed
    app.permanent_session_lifetime = timedelta(hours=2)
    session.modified = True  # resets the session timeout timer


# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    user = users_repository.get_user_by_id(userid)
    login_user(user)
    msg = f'load_user(): userid {userid}, userid {user.userid}, authenticated {current_user.is_authenticated}, type {current_user.get_type()}'
    log(msg) 
    return user


def get_files(folder, pattern):
    if pattern:
        arr = [x for x in os.listdir(folder) if x.startswith(pattern)]
    else:
        #arr = os.listdir(folder)
        arr = []
        for fname in os.listdir(folder):
            path = os.path.join(folder, fname)
            if not os.path.isdir(path):
                arr.append(fname)

    arr.sort()
    return arr

'''
  host='0.0.0.0' means "accept connections from any client ip address".
  This is only used for testing purposes. In production, server.py is loaded by passenger_wsgi.py,
  which is where we load the users from desk into a dict since main() below will never run.
'''
def main():
    load_users()
    app.run(host='0.0.0.0', port=9999, debug=False)

if __name__ == '__main__':
    main()
