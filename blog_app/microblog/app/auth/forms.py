from flask_wtf import FlaskForm
from flask_babel import _, lazy_gettext as _l
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
import sqlalchemy as sa
from app import db
from app.models import User

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

class ResetPasswordRequestForm(FlaskForm):
    email=StringField(_l('Email'),validators=[DataRequired(),Email()])
    submit=SubmitField(_l('Request Password Reset'))

class ResetPasswordForm(FlaskForm):
    password1=PasswordField(_l('Password'),validators=[DataRequired()])
    password2=PasswordField(_l('Enter Password again'),validators=[DataRequired(),EqualTo('password1')])
    submit=SubmitField(_l('Request Password Reset'))