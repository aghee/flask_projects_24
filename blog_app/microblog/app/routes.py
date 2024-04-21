from flask import render_template,flash,redirect,request,url_for
from app import app,db,oauth
from app.forms import LoginForm,RegistrationForm,EditProfileForm,EmptyForm,ResetPasswordRequestForm,ResetPasswordForm
from flask_login import current_user,login_user,logout_user,login_required
import sqlalchemy as sa
from app.models import User
from urllib.parse import urlsplit
from datetime import datetime,timezone
from flask import session
from app.forms import PostForm
from app.models import Post
from app.email import send_password_reset_email

@app.route('/google-login')
def login_google():
    return oauth.myapp.authorize_redirect(redirect_uri=url_for('googlecallback',_external=True))

@app.route('/signin')
def googlecallback():
    token=oauth.myapp.authorize_access_token()
    session['user']=token
    # flash('Creating Account Now...')
    return redirect(url_for('index'))

@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
@login_required
def index():
    form=PostForm()
    if form.validate_on_submit():
        post=Post(body=form.post.data,author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Post has been shared!')
        return redirect(url_for('index'))
    # user={'username':'Agy'}
    # posts=[
    #     {'author': {'username': 'Anita'},
    #     'body': 'Oh Happy Day!'},
    #     {
    #     'author': {'username': 'Wangwi'},
    #     'body': 'Don\'t mess with Kansiime by Ugandan comedian was so cool!'
    #     }
    # ]
    page=request.args.get('page',1,type=int)
    posts=db.paginate(current_user.following_posts(),page=page,
                      per_page=app.config['POSTS_PER_PAGE'],error_out=False)
    next_url=url_for('index',page=posts.next_num) if posts.has_next else None
    previous_url=url_for('index',page=posts.prev_num) if posts.has_prev else None
    # posts=db.session.scalars(current_user.following_posts()).all()
    return render_template('index.html',title='Home',form=form,posts=posts.items,
                           next_url=next_url,previous_url=previous_url)

@app.route('/user/<username>',methods=['GET','POST'])
@login_required
def user(username):
    user=db.first_or_404(sa.select(User).where(User.username==username))
    # query_one=db.session.scalars(current_user.following_posts()).first()
    # posts=[
    #     {'author':user,'body':'Testpost@1'},
    #     {'author':user,'body':'Testpost@2'}
    # ]
    page=request.args.get('page',1,type=int)
    query=user.posts.select().order_by(Post.timestamp.desc())
    posts=db.paginate(query,page=page,per_page=app.config['POSTS_PER_PAGE'],error_out=False)
    next_url=url_for('user',username=user.username,page=posts.next_num) if posts.has_next else None
    prev_url=url_for('user',username=user.username,page=posts.prev_num) if posts.has_prev else None
    form=EmptyForm()
    return render_template('user.html',user=user,posts=posts.items,form=form,next_url=next_url,prev_url=prev_url)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=RegistrationForm()
    if form.validate_on_submit():
        user=User(username=form.username.data,email=form.email.data)
        user.set_password(form.passwd.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats!You are registered')
        return redirect(url_for('login'))
    return render_template('register.html',title='Register',form=form)

@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=LoginForm()
    if form.validate_on_submit():
       user=db.session.scalar(
          sa.select(User).where(User.username==form.username.data)
       )
       if user is None or not user.check_password(form.pwad.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
       login_user(user,remember=form.remember_me.data)
       next_page=request.args.get('next')
       if not next_page or urlsplit(next_page).netloc !='':
           next_page=url_for('index')
           return redirect(next_page)
       return redirect(url_for('index'))
    return render_template('login.html',title='Sign In',form=form)

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def edit_profile():
    form=EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.about_me=form.about_me.data
        db.session.commit()
        flash('Changes saved!')
    elif request.method=='GET':
        form.username.data=current_user.username
        form.about_me.data=current_user.about_me
        flash('Here is your requested info!')
    return render_template('edit_profile.html',title='Edit Profile',form=form)

@app.route('/follow/<username>',methods=['POST'])
@login_required
def follow(username):
    form=EmptyForm()
    if form.validate_on_submit():
        user=db.session.scalar(
            sa.select(User).where(User.username==username)
        )
        if user is None:
            flash(f'{username} does not exist!')
            return redirect(url_for('index'))
        if user==current_user:
            flash('You cannot follow yourself!')
            return redirect(url_for('user',username=username))
        current_user.follow(user)
        db.session.commit()
        flash(f'You are now following {username}!')
        return redirect(url_for('user',username=username))
    else:
        return redirect(url_for('index'))

@app.route('/unfollow/<username>',methods=['POST'])
@login_required
def unfollow(username):
    form=EmptyForm()
    if form.validate_on_submit():
        user=db.session.scalar(
            sa.select(User).where(User.username==username)
        )
        if user is None:
            flash(f'{username} not found!')
            return redirect(url_for('index'))
        if user ==current_user:
            flash('You cannot unfollow yourself!')
            return redirect(url_for('user',username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(f'You have stopped following {username}.')
        return redirect(url_for('user',username=username))
    else:
        return redirect(url_for('index'))

@app.route('/explore')
@login_required
def explore():
    page=request.args.get('page',1,type=int)
    query=sa.select(Post).order_by(Post.timestamp.desc())
    # posts=db.session.scalars(query).all()
    posts=db.paginate(query,page=page,
                      per_page=app.config['POSTS_PER_PAGE'],error_out=False)
    next_url=url_for('explore',page=posts.next_num) if posts.has_next else None
    previous_url=url_for('explore',page=posts.prev_num) if posts.has_prev else None
    return render_template('index.html',title='Explore',posts=posts.items,
                           next_url=next_url,previous_url=previous_url)

@app.route('/reset_password_request',methods=['GET','POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form=ResetPasswordRequestForm()
    if form.validate_on_submit():
        user=db.session.scalar(
            sa.select(User).where(User.email==form.email.data)
        )
        if user:
            send_password_reset_email(user)
        flash('Check email provided for password reset instructions')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',title='Reset Password',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user=User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form=ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password1.data)
        db.session.commit()
        flash('You have reset your password!')
        return redirect(url_for('login'))
    return render_template('reset_your_password.html',form=form)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen=datetime.now(timezone.utc)
        db.session.commit()

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


