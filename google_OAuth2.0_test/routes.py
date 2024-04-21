from flask import url_for,session,redirect,render_template
from server import app,oauth
import json
import requests

@app.route('/google-login')
def login():
    return oauth.myapp.authorize_redirect(redirect_uri=url_for('googlecallback',_external=True))

@app.route('/signin')
def googlecallback():
    token=oauth.myapp.authorize_access_token()
    persondataurl=' https://people.googleapis.com/v1/people/me?personFields=genders,birthdays'
    persondata=requests.get(
        persondataurl,
        headers={
            "Authorization":f"Bearer {token['access_token']}"
        }
    ).json()
    token['persondata']=persondata
    session['user']=token
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html',session=session.get('user'),pretty=json.dumps(session.get('user'),indent=4))

@app.route('/here')
def hereitis():
    return render_template('here.html')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect(url_for('home'))