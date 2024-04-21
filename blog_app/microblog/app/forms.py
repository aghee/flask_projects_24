from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from app import db
import sqlalchemy as sa
from app.models import User
from flask_babel import _,lazy_gettext as _l

class LoginForm(FlaskForm):
    username=StringField(_l('Username'),validators=[DataRequired()])
    pwad=PasswordField(_l('Password'),validators=[DataRequired()])
    remember_me=BooleanField(_l('Remember me'))
    submit=SubmitField(_l('Sign In'))

class RegistrationForm(FlaskForm):
    username=StringField(_l('Username'),validators=[DataRequired()])
    email=StringField(_l('Email'),validators=[DataRequired(),Email()])
    passwd=PasswordField(_l('Password'),validators=[DataRequired()])
    pass1=PasswordField(_l('Repeat Password'),validators=[DataRequired(),EqualTo('passwd')])
    submit=SubmitField(_l('Register'))

    def validate_username(self,username):
        user=db.session.scalar(sa.select(User).where(User.username==username.data))
        if user is not None:
            raise ValidationError('Username exists!Enter a different one.')
    
    def validate_email(self,email):
        user=db.session.scalar(sa.select(User).where(User.email==email.data))
        if user is not None:
            raise ValidationError('Email exists!Enter a different one')
        
class EditProfileForm(FlaskForm):
    username=StringField(_l('Username'),validators=[DataRequired()])
    about_me=TextAreaField(_l('About me'),validators=[Length(min=10,max=150)])
    submit=SubmitField(_l('Submit'))

    def __init__(self,orig_username,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.orig_username=orig_username
    
    def validate_username(self,username):
        if username.data !=self.orig_username:
            user=db.session.scalar(sa.select(User).where(User.username==username.data))
            if user is not None:
                raise ValidationError('You can only update about me details relating to yourself,not for another user! ')
            elif user is None:
                raise ValidationError('User does not exist! Confirm that the username is that of currently logged in user')
        
class EmptyForm(FlaskForm):
    submit=SubmitField('Submit')

class PostForm(FlaskForm):
    post=TextAreaField(_l('Write something here'),validators=[DataRequired(),Length(min=5,max=150)])
    submit=SubmitField(_l('Share post'))

class ResetPasswordRequestForm(FlaskForm):
    email=StringField(_l('Email'),validators=[DataRequired(),Email()])
    submit=SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password1=PasswordField(_l('Password'),validators=[DataRequired()])
    password2=PasswordField(_l('Enter Password again'),validators=[DataRequired(),EqualTo('password1')])
    submit=SubmitField(_l('Request Password Reset'))