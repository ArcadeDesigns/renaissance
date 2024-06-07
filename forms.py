from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField

class PaymentForm(FlaskForm):
    name = StringField(validators=[DataRequired()])
    email = StringField(validators=[DataRequired()])

    #Payment Content
    title = StringField(validators=[DataRequired()])
    location = StringField(validators=[DataRequired()])
    country = StringField(validators=[DataRequired()])
    cost = StringField(validators=[DataRequired()])
    submit = SubmitField()

class DestinationForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    location = StringField(validators=[DataRequired()])
    country = StringField(validators=[DataRequired()])
    cost = StringField(validators=[DataRequired()])
    content = CKEditorField(validators=[DataRequired()])
    file = FileField()
    alt = StringField(validators=[DataRequired()])
    title_tag = StringField(validators=[DataRequired()])
    url_link = StringField(validators=[DataRequired()])
    meta_description = TextAreaField(validators=[DataRequired()])
    keyword = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()

class BlogForm(FlaskForm):
    title = StringField(validators=[DataRequired()])
    content = CKEditorField(validators=[DataRequired()])
    file = FileField()
    alt = StringField(validators=[DataRequired()])
    title_tag = StringField(validators=[DataRequired()])
    url_link = StringField(validators=[DataRequired()])
    meta_description = TextAreaField(validators=[DataRequired()])
    keyword = TextAreaField(validators=[DataRequired()])
    submit = SubmitField()

class LoginForm(FlaskForm):
    email = StringField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()

class UserForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    middle_name = StringField()
    email = StringField(validators=[DataRequired()])
    password_hash = PasswordField(validators=[DataRequired(), EqualTo('password_hash2', message='Passwords Must Match!')])
    password_hash2 = PasswordField(validators=[DataRequired()])
    profile_pic = FileField()
    facebook_account = StringField()
    twitter_account = StringField()
    instagram_account = StringField()
    location = StringField()
    submit = SubmitField()

class PasswordForm(FlaskForm):
    email = StringField("what's your Email", validators=[DataRequired()])
    password_hash = PasswordField(
        "what's your Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class NamerForm(FlaskForm):
    name = StringField("what's your name", validators=[DataRequired()])
    submit = SubmitField("Submit")
