from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, PasswordField, SelectField, BooleanField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional
from BloggerConnect.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', 
                             validators=[DataRequired(), EqualTo('password')])

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    summary = TextAreaField('Summary', validators=[Length(max=500)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(min=50)])
    is_published = BooleanField('Publish immediately', default=True)
    auto_enhance = BooleanField('Auto-enhance content with AI formatting', default=True)
    auto_tags = BooleanField('Generate smart tags automatically', default=True)
    documents = FileField('Upload Related Documents', 
                      validators=[FileAllowed(['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx', 'ppt', 'pptx', 'zip'], 
                                 'Allowed file types: PDF, Word, Excel, PowerPoint, Text, ZIP')],
                      render_kw={'multiple': True, 'accept': '.pdf,.doc,.docx,.txt,.xls,.xlsx,.ppt,.pptx,.zip'})
    
class BlogImageForm(FlaskForm):
    images = FileField('Upload Images', 
                      validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                 'Images only!')],
                      render_kw={'multiple': True, 'accept': 'image/*'})
    
class SingleImageForm(FlaskForm):
    image = FileField('Upload Image', 
                     validators=[FileRequired(), 
                                FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 
                                           'Images only!')],
                     render_kw={'accept': 'image/*'})

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    theme_preference = SelectField('Theme', 
                                 choices=[('light', 'Light Theme'), 
                                         ('dark', 'Dark Theme'), 
                                         ('hacker', 'Hacker Theme')], 
                                 validators=[DataRequired()])

class AdminUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    credits = IntegerField('Credits', validators=[DataRequired()], default=0)
    is_active = BooleanField('Active', default=True)
    theme_preference = SelectField('Theme', 
                                 choices=[('light', 'Light Theme'), 
                                         ('dark', 'Dark Theme'), 
                                         ('hacker', 'Hacker Theme')], 
                                 validators=[DataRequired()])
