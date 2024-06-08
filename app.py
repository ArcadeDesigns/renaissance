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
import logging
from mailjet_rest import Client

# Cloudinary CDN Service
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url

app = Flask(__name__)
ckeditor = CKEditor(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///renaissance.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://renaissancetoursafrica_db_user:ExFpaEupvNeaBfpfUiFPpnrzQavAm3iB@dpg-cpi4miq1hbls73bc3eh0-a.oregon-postgres.render.com/renaissancetoursafrica_db'
app.config['SECRET_KEY'] = "cairocoders-ednalan"
app.config['FLASK_DEBUG'] = True

cloudinary.config(
    cloud_name="renaissance-images",
    api_key="234972531999559",
    api_secret="e39vygsEK4jFyXcTkUDui7f2NMg",
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

CLIENT_ID = '461094641840-aih2rmv5147gvlut443vtlia7nfga50l.apps.googleusercontent.com'
CLIENT_SECRET = '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'
REDIRECT_URI = 'https://renaissance-nlmh.onrender.com/renaissance/auth/google-callback'

# Google Authentication
GOOGLE_AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
GOOGLE_TOKEN_URL = 'https://accounts.google.com/o/oauth2/token'
GOOGLE_USERINFO_URL = 'https://www.googleapis.com/oauth2/v1/userinfo'

# Paystack configuration
PAYSTACK_SECRET_KEY = 'SK_TEST_49A761Ad2E3efdbcae223606ab466f0a6371db99'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

app.config['MAX_CONTENT_LENGTH'] = 16 * 900 * 900
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


##########################################################################################
##########################################################################################
####### User Authentication Structure using Google Authentication Login Process ##########
### This section includes The Google Authentication, and Custom Email Login Structure ####
##########################################################################################
##########################################################################################

@app.route('/renaissance-administrator/auth/access', methods=['GET', 'POST'])
def administrator():
    destinations = Destinations.query.order_by(Destinations.date_posted)
    historys = Historys.query.order_by(Historys.id)
    our_users = Users.query.order_by(Users.date_added)
    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('pages/administration.html',
        title_tag="",
        meta_description="",
        keywords="",
        terms=terms,
        policys=policys,
        our_users=our_users,
        historys=historys,
        destinations=destinations,
        url_link="https://www.renaissance.com/renaissance-administrator/auth/access",
        revised="20th of May 2024",
    )


@app.route('/renaissance/auth/google-callback')
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
                return redirect(url_for('dashboard'))
                
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
        return redirect(url_for('dashboard'))

    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': 'openid email profile',
    }
    auth_url = f"{GOOGLE_AUTH_URL}?{'&'.join(f'{key}={value}' for key, value in params.items())}"
    return redirect(auth_url)

@app.route('/renaissance/travel-and-tourism/auth/create/account', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user:
            flash("This user already has an account with us. Please try logging in instead.")
            return render_template("authentication/registration.html", form=form)

        hashed_pw = generate_password_hash(form.password_hash.data, method="sha256")
        new_user = Users(email=form.email.data, password_hash=hashed_pw)
        db.session.add(new_user)
        try:
            db.session.commit()
            # Uncomment the following lines if email functionality is set up
            # mail_sender.send_confirmation_email(form.email.data, form.name.data)
            # admin_update_mail.send_admin_mail(form.email.data, form.name.data)
            flash("User added successfully.")
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash("This user already has an account with us. Please try logging in instead.")
            return render_template("authentication/registration.html", form=form)

    return render_template(
        'authentication/registration.html',
        form=form,
        title_tag="User Registration",
        meta_description="Create your account to access Renaissance travel and tourism services.",
        keywords="user registration, travel and tourism, renaissance",
        url_link=request.url,
        revised="20th of May 2024"
    )

@app.route('/renaissance/travel-and-tourism/auth/login/account', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("You have successfully logged in.")
            if current_user.id == 1:
                return redirect(url_for('administrator'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password. Please try again.")
    return render_template('authentication/login.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        url_link="https://www.renaissance.com/renaissance/travel-and-tourism/auth/login/account",
        revised="20th of May 2024",
    )

@app.route('/update-user-information/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)

    if request.method == "POST":
        name_to_update.first_name = request.form['first_name']
        name_to_update.last_name = request.form['last_name']
        name_to_update.middle_name = request.form['middle_name']
        name_to_update.email = request.form['email']
        name_to_update.contact_info = request.form['contact_info']
        name_to_update.facebook_account = request.form['facebook_account']
        name_to_update.twitter_account = request.form['twitter_account']
        name_to_update.instagram_account = request.form['instagram_account']
        name_to_update.location = request.form['location']

        if request.files.get('profile_pic'):
            pic_filename = secure_filename(
                request.files['profile_pic'].filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['profile_pic']

            try:
                upload_result = cloudinary.uploader.upload(
                    saver, folder="renaissance-image-upload")
                name_to_update.profile_pic = upload_result['public_id']
                db.session.commit()
                flash("User Updated Successfully !")
                return redirect(url_for('dashboard'))
            except Exception as e:
                flash(f"Error! looks like there was a problem: {e}. Try Again!")
                return redirect(url_for("update", id=id))
        else:
            db.session.commit()
            flash("User Updated Successfully !")
            return redirect(url_for("update", id=id))
    return render_template("dashboard/account/update.html", form=form,
        name_to_update=name_to_update,
        id=id or 1)

@app .route('/delete/<int:id>')
@login_required
def delete(id):
    if id == current_user.id:
        user_to_delete = Users.query.get_or_404(id)
        name = None
        form = UserForm()
        try:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash("The user has been successfully deleted.")
            our_users = Users.query.order_by(Users.date_added)
            return redirect(url_for('index'))
        except:
            flash("An error occurred while attempting to delete the user. Please try again.")
            return render_template("dashboard/account/update.html",
                                   form=form,
                                   name=name,
                                   our_users=our_users)
    else:
        flash("You do not have permission to delete this user.")
        return redirect(url_for('dashboard'))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Successfully Logged Out! ")
    return redirect(url_for('login'))

##########################################################################################
##########################################################################################
####### User Authentication Structure using Google Authentication Login Process ##########
### This section includes The Google Authentication, and Custom Email Login Structure ####
##########################################################################################
##########################################################################################

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com",
        revised="20th of May 2024",
    )

@app.route('/about-renaissance/travels-and-tourism', methods=['GET', 'POST'])
def about():
    return render_template('pages/about.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/about-renaissance/travels-and-tourism",
        revised="20th of May 2024",
    )

@app.route('/renaissance-destination/secure-travels', methods=['GET', 'POST'])
def destination():
    destinations = Destinations.query.order_by(Destinations.date_posted.desc())
    return render_template('pages/destination.html',
        title_tag="",
        meta_description="",
        keywords="",
        destinations=destinations,
        url_link="https://www.renaissance.com/renaissance-destination/secure-travels",
        revised="20th of May 2024",
    )

@app.route('/renaissance/secure-travels/contact-us', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        sender_email = 'info@quinndaisies.com'
        recipient_email = 'sid2284@gmail.com'
        name = form.name.data
        email = form.email.data
        message = form.message.data

        try:
            api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
            api_secret = '118dec95ed600a827d6400f210f3a524'

            # Renaissance Tours Africa APIs
            #api_key = 'f2ee68f1ee98061359df748b4838a35a'
            #api_secret = '6257f707079382e46bb698f85e4084be'
            
            mailjet = Client(auth=(api_key, api_secret), version='v3.1')

            data = {
                'Messages': [
                    {
                        "From": {
                            "Email": sender_email,
                            "Name": "Renaissance Tours Africa Notification"
                        },
                        "To": [
                            {
                                "Email": recipient_email,
                                "Name": "CEO Renaissance Tours Africa"
                            }
                        ],
                        "Subject": "Message Notification for Renaissance Tours Africa",
                        "TextPart": "",
                        "HTMLPart": f'''<div style="width: 100%; height: 100%; justify-content: center; align-content: center; margin: auto; display: flex; padding: 2%;">
                                            <div style="width: 100%; max-width: 600px; border-radius: 15px; overflow: hidden;  height: 100%; justify-content: center; align-content: center; margin: auto; display: block; position: relative;">
                                                <div style=" width: 100%; height: 100%; justify-content: center; align-content: center; margin: auto; display: block; background-color: rgba(0, 0, 0, .8); position: absolute; top: 0; left: 0; padding: 2%;">
                                                    <h2 style="color: #fff; font-size: 2.5em; font-weight: 700; text-align: center;">Renaissance Tours Africa</h2>
                                                    <h3 style="color: #fff; font-size: 1.5em; font-weight: 700; text-align: center; padding-top: 5%;">New message from {email}</h3>
                                                    <p style="color: #fff; font-size: 1em; font-weight: 500; text-align: center;">{message}</p>
                                                </div>
                                            </div>
                                        </div>''',
                        "CustomID": "AppGettingStartedTest"
                    }
                ]
            }

            result = mailjet.send.create(data=data)
            
            # Check if the request was successful (status code 2xx)
            if result.status_code == 200:
                flash("Thank you for reaching out. Your message has been successfully sent. We will promptly review your inquiry and get in touch with you at our earliest convenience.")
                # Send an automated response
                send_message(form)
            else:
                print(f"Failed to send the email. MailJet API response: {result.json()}")
                flash("Failed to send the email.", 'danger')
        except Exception as e:
            print(f"Error occurred while sending the emails: {e}")
            flash("Failed to send the email.", 'danger')

    return render_template('pages/contact.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        url_link="https://www.renaissance.com/renaissance/secure-travels/contact-us",
        revised="20th of May 2024",
    )

def send_message(contact_form):
    sender_email = 'info@quinndaisies.com'
    subject = "Do not reply"
    recipient_name = contact_form.name.data
    recipient_email = contact_form.email.data

    try:
        api_key = '614f1d5db217f5a35c8ed583bbf4f09c'
        api_secret = '118dec95ed600a827d6400f210f3a524'
        
        # Renaissance Tours Africa APIs
        #api_key = 'f2ee68f1ee98061359df748b4838a35a'
        #api_secret = '6257f707079382e46bb698f85e4084be'
        
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')

        data = {
            'Messages': [
                {
                    "From": {
                        "Email": sender_email,
                        "Name": "Renaissance Tours Africa"
                    },
                    "To": [
                        {
                            "Email": recipient_email,
                            "Name": recipient_name
                        }
                    ],
                    "Subject": subject,
                    "TextPart": "",
                    "HTMLPart": f'''<div style="width: 100%; height: 100%; justify-content: center; align-content: center; margin: auto; display: flex; padding: 2%;">
                                        <div style="width: 100%; max-width: 600px; border-radius: 15px; overflow: hidden;  height: 100%; justify-content: center; align-content: center; margin: auto; display: block; position: relative;">
                                            <div style=" width: 100%; height: 100%; justify-content: center; align-content: center; margin: auto; display: block; background-color: rgba(0, 0, 0, .8); position: absolute; top: 0; left: 0; padding: 2%;">
                                                <h2 style="color: #fff; font-size: 2.5em; font-weight: 700; text-align: center;">Renaissance Tours Africa</h2>
                                                <p style="color: #fff; font-size: 1em; font-weight: 500; text-align: center;">Thank you for contacting us. We have received your message and will respond promptly. We appreciate your patience.</p>
                                            </div>
                                        </div>
                                    </div>''',
                    "CustomID": "AppGettingStartedTest"
                }
            ]
        }

        result = mailjet.send.create(data=data)
        # Check if the request was successful (status code 2xx)
        if result.status_code != 200:
            print(f"Failed to send the automated response. MailJet API response: {result.json()}")
    except Exception as e:
        print(f"Error occurred while sending the automated response: {e}")

@app.route('/renaissance/travel-blog/tourism-articles', methods=['GET', 'POST'])
def posts():
    blogs = Blogs.query.order_by(Blogs.date_posted.desc())
    return render_template('pages/blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        blogs=blogs,
        url_link="https://www.renaissance.com/renaissance/travel-blog/tourism-articles",
        revised="20th of May 2024",
    )

@app.route('/renaissance/travel-blog/tourism-articles/<int:id>', methods=['GET', 'POST'])
def post(id):
    blog = Blogs.query.get(id)
    blogs = Blogs.query.order_by(Blogs.date_posted.desc())

    title_tag = blog.title_tag
    url_link = url_for('post', id=blog.id, _external=True)
    keyword = blog.keyword
    meta_description = blog.meta_description
    revised = blog.formatted_date_with_day()

    blogs = Blogs.query.order_by(Blogs.date_posted.desc())
    return render_template('pages/blog-post.html',
        title_tag=title_tag,
        meta_description=meta_description,
        keywords=keyword,
        blog=blog,
        blogs=blogs,
        url_link=url_link,
        revised=revised,
    )

##########################################################################################
##########################################################################################
####################### Dashboard System and Structure ###################################
##########################################################################################
##########################################################################################

@app.route('/renaissance/dashboard/auth/user/account', methods=['GET', 'POST'])
def dashboard():
    historys = Historys.query.order_by(Historys.id)
    destinations = Destinations.query.order_by(Destinations.date_posted.desc())
    our_users = Users.query.order_by(Users.date_added.desc()).all
    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('dashboard/dashboard.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account",
        revised="20th of May 2024",
        historys=historys,
        destinations=destinations,
        our_users=our_users,
        terms=terms,
        policys=policys
    )

@app.route('/renaissance/dashboard/auth/user/account/destination', methods=['GET', 'POST'])
def dashboard_destination():
    destinations = Destinations.query.order_by(Destinations.date_posted)
    our_users = Users.query.order_by(Users.date_added.desc()).all
    return render_template('dashboard/destination.html',
        title_tag="",
        meta_description="",
        keywords="",
        destinations=destinations,
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account/destination",
        revised="20th of May 2024",
        our_users=our_users,
    )

@app.route('/renaissance/dashboard/auth/user/account/blogs', methods=['GET', 'POST'])
def dashboard_blog():
    blogs = Blogs.query.order_by(Blogs.date_posted)
    our_users = Users.query.order_by(Users.date_added.desc()).all
    return render_template('dashboard/blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        blogs=blogs,
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account/blogs",
        revised="20th of May 2024",
        our_users=our_users,
    )

@app.route('/renaissance/dashboard/auth/user/account/destination/details/<int:id>', methods=['GET', 'POST'])
def destination_details(id):
    form = PaymentForm()
    if form.validate_on_submit():
        client_name = request.form.get('name')
        client_email = request.form.get('email')

        # Payment Information
        destination_name = request.form.get('title')
        destination_location = request.form.get('location')
        destination_country = request.form.get('country')
        destination_cost = float(request.form.get('cost'))
        paying = int(destination_cost * 100)

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "email": client_email,
            "amount": paying,
            "callback_url": url_for('payment_callback', _external=True),
            "metadata": {
                "destination_name": destination_name
            }
        }

        try:
            response = requests.post("https://api.paystack.co/transaction/initialize", headers=headers, json=payload)
            response_data = response.json()
            logging.info(f"Paystack response: {response_data}")

            if response.status_code == 200 and response_data['status']:
                authorization_url = response_data['data']['authorization_url']
                return redirect(authorization_url)
            else:
                error_message = response_data.get('message', 'Unknown error')
                logging.error(f"Failed to initiate payment: {error_message}")
                flash(f"Failed to initiate payment: {error_message}", "danger")
        except Exception as e:
            logging.error(f"Exception during payment processing: {e}")
            flash("An error occurred while processing your payment. Please contact admin.", "danger")
    destination = Destinations.query.get(id)
    destinations = Destinations.query.order_by(Destinations.date_posted.desc())
    our_users = Users.query.order_by(Users.date_added.desc()).all()

    title_tag = destination.title
    url_link = url_for('destination', id=destination.id, _external=True)
    keyword = destination.keyword
    meta_description = destination.meta_description

    return render_template('pages/destination-details.html',
        title_tag=title_tag,
        meta_description=meta_description,
        keywords=keyword,
        destination=destination,
        destinations=destinations,
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account/destination/details",
        revised="20th of May 2024",
        our_users=our_users,
        form=form,
    )

@app.route('/payment_callback')
@login_required
def payment_callback():
    reference = request.args.get('reference')
    
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        logging.info(f"Paystack verification response: {response_data}")
        
        if response_data['data']['status'] == 'success':
            flash("Payment successful!", "success")
            
            metadata = response_data['data'].get('metadata')
            if metadata and isinstance(metadata, dict):
                destination_name = metadata.get('destination_name')
                amount = response_data['data']['amount'] / 100
            else:
                logging.error("Invalid metadata format.")
                flash("Payment verification failed due to invalid metadata format. Please contact admin.", "danger")
                return redirect(url_for('destination'))

            user = Users.query.filter_by(id=current_user.id).first()
            history = Historys(
                destination_name=destination_name,
                payment_status=True,
                amount=amount,
                poster_id=current_user.id
            )
            db.session.add(history)
            db.session.commit()
        else:
            flash("Payment failed. Please try again.", "danger")
    else:
        flash("Payment verification failed. Please try again.", "danger")    
    return redirect(url_for('destination'))

@app.route('/renaissance/dashboard/auth/user/history', methods=['GET', 'POST'])
def history():
    historys = Historys.query.order_by(Historys.id)
    return render_template('pages/history.html',
        title_tag="",
        meta_description="",
        keywords="",
        historys=historys,
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account",
        revised="20th of May 2024",
    )

@app.route('/renaissance/terms-and-conditions', methods=['GET', 'POST'])
def terms_conditions():
    terms = Terms.query.order_by(Terms.id)
    return render_template('pages/terms.html',
        title_tag="",
        meta_description="",
        keywords="",
        terms=terms,
        url_link="https://www.renaissance.com/renaissance/terms-and-conditions",
        revised="20th of May 2024",
    )

@app.route('/renaissance/privacy-policy', methods=['GET', 'POST'])
def privacy_policy():
    policys = Policys.query.order_by(Policys.id)
    return render_template('pages/privacy-policy.html',
        title_tag="",
        meta_description="",
        keywords="",
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/privacy-policy",
        revised="20th of May 2024",
    )

##########################################################################################
##########################################################################################
####################### Dashboard System and Structure ###################################
##########################################################################################
##########################################################################################
#-----------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------#
##########################################################################################
##########################################################################################
############################### Create Website Content ###################################
##########################################################################################
##########################################################################################

@app.route('/renaissance/admin/auth/user/create-blog-post', methods=['GET', 'POST'])
@login_required
def create_post():   
    form = BlogForm() 
    if form.validate_on_submit():
        poster = current_user.id
        blog = Blogs(
            title=form.title.data,
            content=form.content.data,
            file=form.file.data,
            alt=form.alt.data,
            title_tag=form.title_tag.data,
            url_link=form.url_link.data,
            meta_description=form.meta_description.data,
            keyword=form.keyword.data,
            poster_id=poster,
        )

        if form.file.data:
            blog.file = form.file.data
            filename = secure_filename(blog.file.filename)
            file_name = str(uuid.uuid1()) + "_" + filename
            saver = form.file.data
            blog.file = file_name

            try:
                upload_result = cloudinary.uploader.upload(
                    saver, folder="renaissance-image-upload")
                blog.file = upload_result['public_id']
                db.session.add(blog)
                db.session.commit()
                flash("Blog post has been created successfully.")
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error! looks like there was a problem: {e}. Try Again!")
                return redirect(url_for('create_post', form=form))
        else:
            db.session.add(post)
            db.session.commit()
            send_subscription()
            deduct_credits(poster)
            flash("Blog article successfully created !")
            return redirect(url_for("dashboard"))

        form.title.data = ''
        form.content.data = ''
        form.file.data = ''
        form.alt.data = ''
        form.title_tag.data = ''
        form.url_link.data = ''
        form.meta_description.data = ''
        form.keyword.data = ''
    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)

    return render_template('pages/create-blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/renaissance/admin/auth/user/create-blog-post",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/edit-blog-post/<int:id>', methods=['GET', 'POST'])
def edit_post(id): 
    blog = Blogs.query.get_or_404(id)
    form = BlogForm(obj=blog) 

    title_tag = blog.title_tag
    meta_description = blog.meta_description
    keyword = blog.keyword

    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data
        blog.title_tag = form.title_tag.data
        blog.url_link = form.url_link.data
        blog.meta_description = form.meta_description.data
        blog.keyword = form.keyword.data
        db.session.commit()

        flash("Your blog post has been successfully updated!")
        return redirect(url_for("posts"))

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)

    return render_template('pages/edit-blog.html',
        title_tag=title_tag,
        meta_description=meta_description,
        keywords=keyword,
        form=form,
        terms=terms,
        policys=policys,
        revised="20th of May 2024",
    )

@app.route('/blog-posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Blogs.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return message
            flash("Blog post was deleted successfully!")

            # Grab all the post from the DataBase
            blogs = Blogs.query.order_by(Blogs.date_posted)
            return redirect(url_for('posts', blogs=blogs))

        except:
            # return error message
            flash("Whoops!!! there was a Problem deleting post try again...")
            blogs = Blogs.query.order_by(Blogs.date_posted)
            return redirect(url_for('dashboard_blog', blogs=blogs))
    else:
        # return message
        flash("You are not authorized to Delete this Post!")
        # Grab all the post from the DataBase
        blogs = Blogs.query.order_by(Blogs.date_posted)
        return redirect(url_for('posts', blogs=blogs))

@app.route('/renaissance/admin/auth/user/create-a-new-destination', methods=['GET', 'POST'])
@login_required
def create_destination():   
    form = DestinationForm() 
    if form.validate_on_submit():
        poster = current_user.id
        destination = Destinations(
            title=form.title.data,
            location=form.location.data,
            country=form.country.data,
            cost=form.cost.data,
            content=form.content.data,
            file=form.file.data,
            alt=form.alt.data,
            title_tag=form.title_tag.data,
            url_link=form.url_link.data,
            meta_description=form.meta_description.data,
            keyword=form.keyword.data,
            poster_id=poster,
        )

        if form.file.data:
            destination.file = form.file.data
            filename = secure_filename(destination.file.filename)
            file_name = str(uuid.uuid1()) + "_" + filename
            saver = form.file.data
            destination.file = file_name

            try:
                upload_result = cloudinary.uploader.upload(
                    saver, folder="renaissance-image-upload")
                destination.file = upload_result['public_id']
                db.session.add(destination)
                db.session.commit()
                flash("A new destination has been created successfully.")
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Error! looks like there was a problem: {e}. Try Again!")
                return redirect(url_for('create_destination', form=form))
        else:
            db.session.add(destination)
            db.session.commit()
            flash("Post Successfully Added !")
            return redirect(url_for("dashboard"))

        form.title.data = ''
        form.location.data = ''
        form.country.data = ''
        form.cost.data = ''
        form.content.data = ''
        form.file.data = ''
        form.alt.data = ''
        form.title_tag.data = ''
        form.url_link.data = ''
        form.meta_description.data = ''
        form.keyword.data = ''

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)

    return render_template('pages/create-destination.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/create-a-new-destination",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/edit-destination/<int:id>', methods=['GET', 'POST'])
def edit_destination(id): 
    destination = Destinations.query.get_or_404(id)
    form = DestinationForm(obj=destination) 

    title_tag = destination.title_tag
    meta_description = destination.meta_description
    keyword = destination.keyword

    if form.validate_on_submit():
        destination.title = form.title.data
        destination.location = form.location.data
        destination.country = form.country.data
        destination.cost = form.cost.data
        destination.content = form.content.data
        destination.title_tag = form.title_tag.data
        destination.url_link = form.url_link.data
        destination.meta_description = form.meta_description.data
        destination.keyword = form.keyword.data
        db.session.commit()

        flash("Your destination post has been successfully updated!")
        return redirect(url_for("destination"))

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('pages/edit-destination.html',
        title_tag=title_tag,
        meta_description=meta_description,
        keywords=keyword,
        form=form,
        revised="20th of May 2024",
    )

@app.route('/destination-posts/delete/<int:id>')
@login_required
def delete_destination(id):
    post_to_delete = Destinations.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster_id or id == 1:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # return message
            flash("Destination post was deleted successfully!")

            # Grab all the post from the DataBase
            destinations = Destinations.query.order_by(Destinations.date_posted)
            return redirect(url_for('posts', destinations=destinations))

        except:
            # return error message
            flash("Whoops!!! there was a Problem deleting post try again...")
            destinations = Destinations.query.order_by(Destinations.date_posted)
            return redirect(url_for('dashboard_destination', destinations=destinations))
    else:
        # return message
        flash("You are not authorized to Delete this Post!")
        # Grab all the post from the DataBase
        destinations = Destinations.query.order_by(Destinations.date_posted)
        return redirect(url_for('posts', destinations=destinations))

@app.route('/renaissance/admin/auth/user/create-terms-and-conditions', methods=['GET', 'POST'])
@login_required
def create_terms():   
    form = TermsForm() 
    if form.validate_on_submit():
        poster = current_user.id
        term = Terms(
            content=form.content.data,
        )

        db.session.add(term)
        db.session.commit()
        flash("Dear Admin, the terms and conditions have been successfully created.")
        return redirect(url_for("administrator"))

        form.content.data = ''

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('forms/terms-form.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/create-terms-and-conditions",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/edit-terms-and-conditions/<int:id>', methods=['GET', 'POST'])
def edit_terms(id): 
    term = Terms.query.get_or_404(id)
    form = TermsForm(obj=term) 

    if form.validate_on_submit():
        term.content = form.content.data
        db.session.commit()

        flash("Dear Admin, the terms and conditions have been successfully updated.")
        return redirect(url_for("administrator"))
    
    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('forms/terms-form.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/edit-terms-and-conditions/",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/create-privacy-policy', methods=['GET', 'POST'])
@login_required
def create_privacy():   
    form = PrivacyForm() 
    if form.validate_on_submit():
        policy = Policys(
            content=form.content.data,
        )

        db.session.add(policy)
        db.session.commit()
        flash("Dear Admin, the privacy policy contents have been successfully created.")
        return redirect(url_for("administrator"))

        form.content.data = ''

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('forms/privacy-form.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/create-privacy-policy",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/edit-privacy-policy/<int:id>', methods=['GET', 'POST'])
def edit_privacy(id): 
    policy = Policys.query.get_or_404(id)
    form = PrivacyForm(obj=policy) 

    if form.validate_on_submit():
        policy.content = form.content.data
        db.session.commit()

        flash("Dear Admin, the terms and conditions have been successfully upated your privacy policy.")
        return redirect(url_for("administrator"))

    terms = Terms.query.order_by(Terms.id)
    policys = Policys.query.order_by(Policys.id)
    return render_template('forms/privacy-form.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        terms=terms,
        policys=policys,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/edit-privacy-policy",
        revised="20th of May 2024",
    )

##########################################################################################
##########################################################################################
############################### Create Website Content ###################################
##########################################################################################
##########################################################################################

@app.route('/files/<path:filename>')
def uploaded_files(filename):
    app = current_app._get_current_object()
    path = (app.config['UPLOAD_FOLDER'])
    return send_from_directory(path, filename)

@app.route('/upload', methods=['POST'])
def upload():
    app = current_app._get_current_object()
    f = request.files.get('upload')

    # Add more validations here
    extension = f.filename.split('.')[-1].lower()
    if extension not in ['jpg', 'gif', 'png', 'jpeg']:
        return upload_fail(message='Image only!')
    saver.save(os.path.join((app.config['UPLOAD_FOLDER']), f.filename))
    url = url_for('main.uploaded_files', filename=f.filename)
    return upload_success(url, filename=f.filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("components/404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template("components/500.html"), 500

if __name__ == '__main__':
    app.run(debug=True)
