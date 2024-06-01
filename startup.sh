#!/bin/bash

# To run file "./startup.sh"

# Create folders
mkdir templates static

# Create files
touch app.py models.py forms.py create_database.py database.py 

# Create subfolders in the templates folder
mkdir templates/components templates/authentication templates/forms templates/dashboard

# Create files in the templates folder
touch templates/index.html templates/base.html

# Create files in subfolders in the templates folder
touch templates/components/navbar.html templates/components/footer.html templates/components/notification.html

# Create files in subfolders in the templates folder
touch templates/authentication/login.html templates/authentication/registration.html

# Create subfolders in the static folder
mkdir static/js static/css 

# Create files subfolders in the static folder
touch static/js/app.js static/js/main.js static/js/index.js

# Create files subfolders in the static folder
touch static/css/app.css static/css/main.css static/css/index.css 

cat <<EOF > app.py
from flask import *
from forms import *
from models import *
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
from flask_ckeditor import upload_success, upload_fail
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from flask_wtf.csrf import CSRFProtect
from flask_ckeditor import CKEditor
import urllib.request
from database import db
import uuid as uuid
import os
import requests

# Cloudinary CDN Service
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
ckeditor = CKEditor(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///adeyproperties.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://adey_properties_db_vqev_user:DTswNlQJ3PphV7aWtxG8Kn9adSKuZFdE@dpg-coh69iev3ddc73fi9it0-a.oregon-postgres.render.com/adey_properties_db_vqev'
app.config['SECRET_KEY'] = "cairocoders-ednalan"
app.config['FLASK_DEBUG'] = True

cloudinary.config(
    cloud_name="adeyproderties",
    api_key="468776535587538",
    api_secret="rrkPZWsBZLR2pOUKolZI2vjKqoA",
)

upload("https://upload.wikimedia.org/wikipedia/commons/a/ae/Olympic_flag.jpg",
       public_id="olympic_flag")
url, options = cloudinary_url(
    "olympic_flag", width=100, height=150, crop="fill")

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = [
    'jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG']
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

CLIENT_ID = '257070779507-uv04il08l9c5i1rf1jqqlabokkh9hbsg.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'https://adey-properties-ocge.onrender.com/adey-properties/auth/google-callback'

# Google Authentication
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

app.config['MAX_CONTENT_LENGTH'] = 16 * 900 * 900
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/adey-properties/auth/google-callback')
def google_callback():
    code = request.args.get('code')
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
    }
    response = requests.post(GOOGLE_TOKEN_URL, data=data)
    access_token = response.json().get('access_token')
    if access_token:
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(GOOGLE_USERINFO_URL, headers=headers)
        if response.status_code == 200:
            profile_data = response.json()
            user = Users.query.filter_by(email=profile_data['email']).first()
            if user:
                login_user(user)
                flash("Login Successful!", 'success')
                if user.id == 1:
                    return redirect(url_for('admin'))
                else:
                    return redirect(url_for('properties'))
            else:
                hashed_pw = generate_password_hash('your_random_password', "sha256")
                user = Users(name=profile_data['name'], username=profile_data['email'], email=profile_data['email'], password_hash=hashed_pw)
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash("User Created and logged In Successfully", "success")
                return redirect(url_for('properties'))
    return redirect(url_for('google_login'))

@app.route('/continue/with/google')
def google_login():
    if current_user.is_authenticated:
        if current_user.id == 1:
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('properties'))

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    return redirect(auth_url)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.adeyproperties.com",
        revised="20th of April 2024",
    )

EOF

cat <<EOF > models.py
from database import db
from datetime import date, datetime
from flask_login import UserMixin
EOF

cat <<EOF > create_database.py
from app import app, db
with app.app_context():
    db.create_all()
EOF

cat <<EOF > database.py
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
EOF
