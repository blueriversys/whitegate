"""
https://towardsdatascience.com/virtual-environments-104c62d48c54

How to set the virtual env:
. python3 -m venv <virtual-env-folder>  (ex. python3 -m venv myvenv)
. source myvenv/bin/activate (to activate)
. pip install -r requirements.txt

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
RESIDENTS_DB = SERVER_FOLDER + "/" + "residents.json"
ANNOUNCS_FILE = SERVER_FOLDER + "/" + "announcs.dat"
LOG_FILE = SERVER_FOLDER + "/" + "whitegate.log"

cgitb.enable()


# read residents json file and create dictionaries
with open(RESIDENTS_DB, 'r') as f:
    strContent = f.read()
    jsonObj = json.loads(strContent)
    residents = jsonObj['residents']
    for resident in residents:
        user = User(
            resident['unit'],
            resident['userid'],
            resident['password'],
            resident['lastname'],
            resident['name'],
            resident['email'],
            resident['startdt'],
            resident['phone'],
            users_repository.next_index(),
            resident['type']
        )
        users_repository.add_user_to_dict(user)


def log(msg):
    timestamp = get_timestamp()
    with open(LOG_FILE, "a") as f:
        f.write(f'{timestamp} {msg}\n')
        f.close()


def get_timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

@app.route('/docs/<path:filename>')
@login_required
def protected(filename):
    return send_from_directory(app.static_folder + '/docs', filename)

@app.route('/opendocs/<path:filename>')
def unprotected(filename):
    return send_from_directory(app.static_folder + '/opendocs', filename)

@app.route('/')
def index():
    return redirect(url_for('home'))

@app.route('/deletefile', methods=['POST'])
def delete_file():
    file_obj = request.get_json()
    filepath = file_obj['request']['filepath']
    print(f'file to be deleted {filepath}')
    try:
        os.remove('static/'+filepath)
        status = 'success'
        log(f"username {current_user.username} deleted file {file_obj['request']['filename']}")
    except OSError:
        status = 'failure'
    return_obj = {'status': status}
    return json.dumps(return_obj)

#------------------------------------------------------------
# will send email to all residents, one by one
#------------------------------------------------------------
@app.route('/sendmail', methods=['POST'])
def send_bulk_email():
    emailto = get_all_emails()
#    subject = request.form.get('emailtitlefield')
#    body = request.form.get('emailbodyfield')

    mailObj = request.get_json()
    subject = mailObj['request']['subject']
    body = mailObj['request']['body']

#    send_email_google(emailto, subject, body)

    for single_email_to in emailto:
        send_email_relay_host(single_email_to, subject, body)

#   FOR TESTING PURPOSES ONLY
#    for single_email_to in emailto:
#        print(f'sending email to {single_email_to}')
#        subj = mailObj['request']['subject']
#        subject = subj + ",   " + single_email_to
#        single_email_to = GMAIL_WHITEGATE_EMAIL 
#        send_email_relay_host(single_email_to, subject, body)

    resp_dict = {'status' : 'success'}
    return_obj = {'response' : resp_dict}
    return json.dumps(return_obj)

@app.route('/sendsinglemail', methods=['POST'])
def send_single_email():
    mailObj = request.get_json()
    emailto = mailObj['request']['emailto']
    subject = mailObj['request']['subject']
    body = mailObj['request']['body']
    #print(f'emailto {emailto}  subject {subject}  body {body}')
    #user = users_repository.get_user(username)
    #passw = user.password
    #body = 'Your credential to access whitegatecondo.com:\n\nusername: ' + username + "\npassword: " + passw 
    if len(emailto.strip()):
        send_email_relay_host(emailto, subject, body)
    resp_dict = {'status' : 'success'}
    return_obj = {'response' : resp_dict}
    return json.dumps(return_obj)

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

    pictures = get_files(app.static_folder + '/pics', '')
    return render_template("home.html", pics=pictures)

@app.route('/about')
def about():
    return render_template("about.html")

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

@app.route('/saveannouncs', methods=["POST"])
def save_announc_list():
    announcsObj = request.get_json()
    announcs = announcsObj['announc']['lines']
    with open(ANNOUNCS_FILE, 'w') as f:
        f.write(announcs)
        f.close()

    return_obj = {'status' : 'success'}
    return json.dumps({'response' : return_obj})

@app.route('/announcs')
def announcs():
    return render_template("announcs.html")

@app.route('/docs')
@login_required
def get_docs():
    docs2020 = get_files(app.static_folder + '/docs/financial', 'Fin-2020')
    docs2021 = get_files(app.static_folder + '/docs/financial', 'Fin-2021')
    docs2022 = get_files(app.static_folder + '/docs/financial', 'Fin-2022')
    bylaws = get_files(app.static_folder + '/docs/bylaws', '')
    otherdocs = get_files(app.static_folder + '/docs/other', '')
    return render_template("docs.html", bylaws=bylaws, otherdocs=otherdocs, findocs2020=docs2020, findocs2021=docs2021, findocs2022=docs2022)

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

def sort_criteria(obj):
    return int(obj['unit'])

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
                               'userid':user.username, 
                               'password':passw,
                               'lastname':user.lastname,
                               'name':user.name,
                               'email':user.email,
                               'startdt':user.startdt,
                               'phone':user.phone,
                               'type':user.type
                          } )
        i += 1

    resident_list.sort(key=sort_criteria)
    json_obj = {'residents':resident_list}
    return json.dumps(json_obj)

@app.route('/getresident', methods=["POST"])
def get_resident_json():
    userObj = request.get_json()
    type = userObj['request']['type']
    id = userObj['request']['id']
#    print(f'request type {type} id {id}' )

    if type == 'user':
        user = users_repository.get_user(id)
    else:
        user = users_repository.get_user_by_unit(id)

    if user == None:
        return_obj = {'status' : 'not_found'}
        return json.dumps({'response' : return_obj})

    resident = {'unit':user.unit, 
                'userid':user.username, 
                'password':user.password,
                'lastname':user.lastname,
                'name':user.name,
                'email':user.email,
                'startdt':user.startdt,
                'phone':user.phone,
                'type':user.type
            }

    resp_dict = {'status' : 'success', 'resident':resident}
    return_obj = {'response':resp_dict}
    return json.dumps(return_obj)


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


@app.route('/saveresident', methods=["POST"])
def save_resident_json():
    userObj = request.get_json()
    dbUser = users_repository.get_user_by_unit(userObj['resident']['unit'])

    if dbUser == None:
        password = generate_password(userObj['resident']['userid'])
        user = User(
            userObj['resident']['unit'],
            userObj['resident']['userid'],
            password,
            userObj['resident']['lastname'],
            userObj['resident']['name'],
            userObj['resident']['email'],
            userObj['resident']['startdt'],
            userObj['resident']['phone'],
            users_repository.next_index(),
            userObj['resident']['type']
        )
    else:
        user = User(
            dbUser.unit,
            userObj['resident']['userid'],
            dbUser.password,
            userObj['resident']['lastname'],
            userObj['resident']['name'],
            userObj['resident']['email'],
            userObj['resident']['startdt'],
            userObj['resident']['phone'],
            users_repository.next_index(),
            userObj['resident']['type']
        )
#        print(f'delete before adding to db')
        users_repository.delete_user(user)

    # save this user in an internal structure
    users_repository.save_user(user)

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
        #print(f'size {uploaded_file.content_length}  file name received {uploaded_file.filename}  special name: {uploaded_convname}')

        filename = secure_filename(uploaded_file.filename)
        filename = filename.replace('_', '-')
        filename = filename.replace(' ', '-')
        fullpath = '' 
        if uploaded_convname == 'announc':
            fullpath = app.static_folder + '/opendocs/announcs/' + filename 
        elif uploaded_convname == 'bylaws':
            fullpath = app.static_folder + '/docs/bylaws/' + filename 
        elif uploaded_convname == 'otherdoc':
            fullpath = app.static_folder + '/docs/other/' + filename   
        elif uploaded_convname == 'picture':
            fullpath = app.static_folder + '/pics/' + filename   
        else:
            fullpath = app.static_folder + '/docs/financial/' + "Fin-" + uploaded_convname + ".pdf"  

        uploaded_file.stream.seek(0)
        uploaded_file.save(fullpath) 
        return render_template("upload.html")     
    else:
        docs2020 = get_files(app.static_folder + '/docs/financial', 'Fin-2020')
        docs2021 = get_files(app.static_folder + '/docs/financial', 'Fin-2021')
        docs2022 = get_files(app.static_folder + '/docs/financial', 'Fin-2022')
        bylaws = get_files(app.static_folder + '/docs/bylaws', '')
        otherdocs = get_files(app.static_folder + '/docs/other', '')
        pics = get_files(app.static_folder + '/pics', '')
        return render_template("upload.html", bylaws=bylaws, otherdocs=otherdocs, findocs2020=docs2020,
                               findocs2021=docs2021, findocs2022=docs2022, pics=pics)


@app.route('/pics')
def pics():
    pictures = get_files(app.static_folder + '/pics', '')
    return render_template("pics.html", pics=pictures)

@app.route('/team')
def team():
    return render_template("team.html")

@app.route('/login', methods=['GET' , 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        registeredUser = users_repository.get_user(username)

        if registeredUser == None:
            flash("Invalid username or password")
            return render_template("login.html")

        next_page = request.args.get('next')

        if not next_page:
            next_page = url_for('home')

        if registeredUser.password == password:
            #print('Login successful: user %s , password %s' % (registeredUser.username, registeredUser.password))
            msg = f'user {registeredUser.username} logged in'
            log(msg)
            login_user(registeredUser)
            return redirect(next_page)
        else:
            #return abort(401)
            flash("Invalid username or password")
            return render_template("login.html") 
    else:
        return render_template("login.html")

@app.route('/register', methods = ['GET' , 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        registeredUser = users_repository.get_user(username)

        if registeredUser != None:
            flash("User already exists.")
            return render_template("register.html")

        password = request.form['password']
        new_user = User(username , password , users_repository.next_index())
        users_repository.save_user(new_user)
        return Response("Registered Successfully")
    else:
        return render_template("register.html")


@app.route('/logout', methods=['GET'])
def logout():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))

    msg = f'user id {current_user.id}, {current_user.username} logged out'
    log(msg)
    username = current_user.username  # we need to save the username BEFORE invoking logout_user()
    logout_user()
    return render_template("logout.html", loggedout_user=username)


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
    msg = f'load_user(): userid {userid}, username {user.username}, authenticated {current_user.is_authenticated}, type {current_user.get_type()}'
    log(msg) 
    return user


def get_files(folder, pattern):
    if pattern:
       arr = [x for x in os.listdir(folder) if x.startswith(pattern)]    
    else:
       arr = os.listdir(folder)
    #arr = glob.glob(pattern)
    arr.sort()
    return arr


# host='0.0.0.0' means "accept connections from any client ip address"
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999, debug=False)
