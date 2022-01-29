from flask import Flask, redirect, url_for

from functools import wraps
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode



import toml
import logging

from models import Person, Organization


app = Flask(__name__)
app.secret_key = 'testingthisout'
# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)



oauth = OAuth(app)



auth0 = oauth.register(
    'auth0',
    client_id = app.config['AUTH0_CLIENT_ID'],
    client_secret = app.config['AUTH0_CLIENT_SECRET'],
    api_base_url = app.config['AUTH0_API_BASE_URL'],
    access_token_url = app.config['AUTH0_ACCESS_TOKEN_URL'],
    authorize_url = app.config['AUTH0_AUTHORIZE_URL'],
    client_kwargs={
        'scope': 'openid profile email',
    },
)









@app.get('/')
def home_handler():
    # TODO what should this page be. Is it a signup page?
    person = Person({'name':'Chris'})
    return person.as_schema()


@app.get('/users/add')
def typeform_webhook_handler():
    # TODO translate data from typeform into a model
    # TODO persist the model somewhere like Stein
    # TODO fire signup action
    # TODO notify Slack of new signup
    return 'webook from typeform'




@app.get('/login')
def login__form_handler():
    # TODO login using Auth0
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')



@app.get('/logout')
def logout_handler():
    params = {'returnTo': url_for('home_handler', _external=True), 'client_id': app.config['AUTH0_CLIENT_ID']}
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))




@app.route('/callback')
def callback_handler():
    # Handles response from token endpoint
    auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    # Store the user information in flask session.
    payload = userinfo
    userinfo = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    logging.warn(payload)
    logging.warn(userinfo)
    return redirect('/admin')




# TODO auth decorator
@app.get('/admin')
def admin_home_handler():
    # TODO think about what this should contain? Stats? Recent actions?
    return 'admin home'


@app.get('/admin/users')
def admin_users_handler():
    # TODO think about what this should contain? Stats? Recent actions?
    return 'admin home'



# TODO auth decorator
@app.get('/admin/matches/create')
# TODO think about what this does. Does it create a new match table? Does it populate with guessed matches
def admin_create_matches_handler():
    return 'match creation'


# TODO auth decorator
@app.get('/admin/matches/view')
def admin_view_matches_handler():
    # TODO show matches
    return 'match view'


# TODO auth decorator
@app.get('/admin/matches/edit')
def admin_edit_matches_handler():
    # TODO edit matches
    return 'match edit'


# TODO auth decorator
@app.get('/admin/matches/test')
def admin_test_matches_handler():
    # TODO show form which will approve the sending, make it have some friction
    return 'match send'


# TODO auth decorator
@app.post('/admin/matches/test')
def admin_test_matches_confirm_handler():
    return 'match send confirmation step'


# TODO auth decorator
@app.get('/admin/matches/send')
def admin_send_matches_handler():
    # TODO show form which will approve the sending, make it have some friction
    return 'match send'

# TODO auth decorator
@app.post('/admin/matches/send')
def admin_send_matches_confirm_handler():
    return 'match send confirmation step'
