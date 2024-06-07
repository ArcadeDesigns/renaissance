from database import db
from datetime import date, datetime
from flask_login import UserMixin

class Historys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_name = db.Column(db.String(), nullable=False)
    payment_status = db.Column(db.Boolean, default=False)
    amount = db.Column(db.Text, nullable=False)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class Destinations(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    location = db.Column(db.String(), nullable=False)
    country = db.Column(db.String(), nullable=True)
    cost = db.Column(db.String(), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(), nullable=False)
    alt = db.Column(db.String(), nullable=False)
    title_tag = db.Column(db.String(), nullable=False)
    url_link = db.Column(db.String(), nullable=False)
    meta_description = db.Column(db.Text, nullable=False)
    keyword = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Returns only the month and year: March 2023
    def formatted_date(self):
        return self.date_posted.strftime("%B %Y")

    # Returns day, month, and year: 15 March 2023
    def formatted_date_with_day(self):
        return self.date_posted.strftime("%d %B %Y")

    # Returns time: 9:30 am
    def formatted_time(self):
        return self.date_posted.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_posted
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"

class Blogs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    content = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(), nullable=False)
    alt = db.Column(db.String(), nullable=False)
    title_tag = db.Column(db.String(), nullable=False)
    url_link = db.Column(db.String(), nullable=False)
    meta_description = db.Column(db.Text, nullable=False)
    keyword = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Returns only the month and year: March 2023
    def formatted_date(self):
        return self.date_posted.strftime("%B %Y")

    # Returns day, month, and year: 15 March 2023
    def formatted_date_with_day(self):
        return self.date_posted.strftime("%d %B %Y")

    # Returns time: 9:30 am
    def formatted_time(self):
        return self.date_posted.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_posted
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(), nullable=True)
    last_name = db.Column(db.String(), nullable=True)
    middle_name = db.Column(db.String(), nullable=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    contact_info = db.Column(db.String(), nullable=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    profile_pic = db.Column(db.String(), nullable=True)
    facebook_account = db.Column(db.Text(), nullable=True)
    twitter_account = db.Column(db.Text(), nullable=True)
    instagram_account = db.Column(db.Text(), nullable=True)
    location = db.Column(db.String(), nullable=True)

    # Foreignkey Integration
    historys = db.relationship('Historys', backref='poster', lazy=True, cascade='all, delete-orphan')
    blogs = db.relationship('Blogs', backref='poster', lazy=True, cascade='all, delete-orphan')
    destinations = db.relationship('Destinations', backref='poster', lazy=True, cascade='all, delete-orphan')

    # Do Some Password Stuff
    password_hash = db.Column(db.String())

    def formatted_date(self):
        return self.date_added.strftime("%B %Y")

    def formatted_date_with_day(self):
        return self.date_added.strftime("%d %B %Y")

    def formatted_time(self):
        return self.date_added.strftime("%I:%M %p").lstrip('0')

    def time_since_posted(self):
        time_diff = datetime.now() - self.date_added
        hours, remainder = divmod(time_diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if time_diff.days > 0:
            return f"{time_diff.days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    @property
    def password(self):
        raise AttributeError(' Password Not A Readable Attribute !!! ')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return '<Name %r>' % self.name
