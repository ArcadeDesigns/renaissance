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

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///renaissance.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://renaissance_db_user:FFxRe3eeEDNNB2vQZ1s6X74MR8Pi6Ssy@dpg-cpdhdg5ds78s73eii6r0-a.oregon-postgres.render.com/renaissance_db'
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
    return render_template('pages/destination.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance-destination/secure-travels",
        revised="20th of May 2024",
    )

@app.route('/renaissance/secure-travels/contact-us', methods=['GET', 'POST'])
def contact():
    return render_template('pages/contact.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance/secure-travels/contact-us",
        revised="20th of May 2024",
    )

@app.route('/renaissance/travel-blog/tourism-articles', methods=['GET', 'POST'])
def posts():
    return render_template('pages/blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance/travel-blog/tourism-articles",
        revised="20th of May 2024",
    )

##########################################################################################
##########################################################################################
####################### Dashboard System and Structure ###################################
##########################################################################################
##########################################################################################

@app.route('/renaissance/dashboard/auth/user/account', methods=['GET', 'POST'])
def dashboard():
    our_users = Users.query.order_by(Users.date_added.desc()).all
    return render_template('dashboard/dashboard.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account",
        revised="20th of May 2024",
        our_users=our_users,
    )

@app.route('/renaissance/dashboard/auth/user/account/destination', methods=['GET', 'POST'])
def dashboard_destination():
    destinations = Destinations.query.order_by(Destinations.date_posted.desc())
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

@app.route('/renaissance/dashboard/auth/user/account/destination/details', methods=['GET', 'POST'])
def destination_details():
    destinations = Destinations.query.order_by(Destinations.date_posted.desc())
    our_users = Users.query.order_by(Users.date_added.desc()).all
    return render_template('pages/destination-details.html',
        title_tag="",
        meta_description="",
        keywords="",
        destinations=destinations,
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account/destination/details",
        revised="20th of May 2024",
        our_users=our_users,
    )

@app.route('/renaissance/dashboard/auth/user/history', methods=['GET', 'POST'])
def history():
    return render_template('pages/history.html',
        title_tag="",
        meta_description="",
        keywords="",
        url_link="https://www.renaissance.com/renaissance/dashboard/auth/user/account",
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

    return render_template('pages/create-blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        url_link="https://www.renaissance.com/renaissance/renaissance/admin/auth/user/create-blog-post",
        revised="20th of May 2024",
    )

@app.route('/renaissance/admin/auth/user/create-blog-post', methods=['GET', 'POST'])
def edit_post():   
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
                saver.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], file_name))
                flash("Blog post has been created successfully.")
                return redirect(url_for("posts"))
            except:
                flash("An error occurred. Please try again.")
                return render_template("publish.html", form=form)
        else:
            db.session.add(post)
            db.session.commit()
            send_subscription()
            deduct_credits(poster)
            flash("Post Successfully Added !")
            return redirect(url_for("posts"))

        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        form.file.data = ''
        form.alt.data = ''
        form.keyword.data = ''
        form.title_tag.data = ''
        form.url_link.data = ''
        form.youtube_url.data = ''
        form.meta_description.data = ''
        form.category.data = ''
        form.other_category.data = ''
        total_score = ''
        grade_reason = ''
        grade_description = ''
        improvement_suggestions = ''

    return render_template('pages/create-blog.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        url_link="https://www.renaissance.com/renaissance/renaissance/admin/auth/user/create-blog-post",
        revised="20th of May 2024",
    )


@app.route('/renaissance/admin/auth/user/create-a-new-destination', methods=['GET', 'POST'])
@login_required
def create_destination():   
    form = DestinationForm() 
    if form.validate_on_submit():
        poster = current_user.id
        destination = Destinations(
            title=form.title.data,
            location=form.location.data,
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
        form.cost.data = ''
        form.content.data = ''
        form.file.data = ''
        form.alt.data = ''
        form.title_tag.data = ''
        form.url_link.data = ''
        form.meta_description.data = ''
        form.keyword.data = ''

    return render_template('pages/create-destination.html',
        title_tag="",
        meta_description="",
        keywords="",
        form=form,
        url_link="https://www.renaissance.com/renaissance/admin/auth/user/create-a-new-destination",
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
