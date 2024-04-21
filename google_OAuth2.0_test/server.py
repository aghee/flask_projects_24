from flask import Flask,url_for,session,redirect,render_template
import json
import requests
from authlib.integrations.flask_client import OAuth
from dotenv import dotenv_values


app=Flask(__name__)
appconf = dotenv_values(".env")
app.secret_key=appconf.get('FLASK_SECRET')
oauth=OAuth(app)
#web app client that follows OAuth2.0 authorization code flow
oauth.register(
    'myapp',
    client_id=appconf.get('OAUTH2_CLIENT_ID'),
    client_secret=appconf.get('OAUTH2_CLIENT_SECRET'),
    server_metadata_url=appconf.get('OAUTH2_META_URL'),
    client_kwargs={
        'scope':'openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read'
    }
)

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
if __name__=='__main__':
    app.run(host='0.0.0.0',port=appconf.get('FLASK_PORT'),debug=True)
