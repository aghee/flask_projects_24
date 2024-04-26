from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email
from flask import session
from app import oauth


@bp.route('/google-login')
def login_google():
    return oauth.myapp.authorize_redirect(redirect_uri=url_for('auth.googlecallback',_external=True))

@bp.route('/signin')
def googlecallback():
    token=oauth.myapp.authorize_access_token()
    if session['user']==token:
        current_user.is_authenticated
    return redirect(url_for('main.index'))
    # flash('Creating Account Now...')
    

#fm login.html

@bp.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.passwd.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats!You are registered')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html',title='Register',form=form)

@bp.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=LoginForm()
    if form.validate_on_submit():
       user=db.session.scalar(
          sa.select(User).where(User.username==form.username.data)
       )
       if user is None or not user.check_password(form.pwad.data):
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
       login_user(user,remember=form.remember_me.data)
       next_page=request.args.get('next')
       if not next_page or urlsplit(next_page).netloc !='':
           next_page=url_for('main.index')
           return redirect(next_page)
       return redirect(url_for('main.index'))
    return render_template('auth/login.html',title='Sign In',form=form)

@bp.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form=ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=db.session.scalar(
            sa.select(User).where(User.email==form.email.data)
        )
        if user:
            send_password_reset_email(user)
        flash(_('Check email provided for password reset instructions'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',title='Reset Password',form=form)

@bp.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user=User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password1.data)
        db.session.commit()
        flash(_('You have reset your password!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_your_password.html',form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))
