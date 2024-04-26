from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l
from app import db
from app.models import User


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