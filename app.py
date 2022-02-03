from flask import Flask, redirect, url_for, request, make_response

from functools import wraps
from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode
import jwt
import datetime


import toml
import logging


from common import check_user, requires_privilege, templated, get_hostname

from models import Person, Organization


app = Flask(__name__)
app.secret_key = app.config['SECRET_KEY']
# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)


auth0 = OAuth(app).register(
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
@check_user
@templated('home')
def home_handler(userobj):
    return {'message': 'hello', 'host':get_hostname(request)}


@app.get('/schema')
def schema_handler():
    person = Person({'name':'blank'})
    return person.as_schema()


@app.get('/users/add')
def typeform_webhook_handler():
    # TODO translate data from typeform into a model
    # TODO persist the model somewhere like Stein
    # TODO fire signup action
    # TODO notify Slack of new signup
    # TODO think again if we're not using typeform
    return 'webook from typeform'


@app.get('/users/confirm')
def confirm_user_handler():
    # TODO notify Slack of confirmation
    return 'email confirmation'



@app.get('/login')
def login__handler():
    return auth0.authorize_redirect(redirect_uri='http://localhost:5000/callback')



@app.get('/logout')
def logout_handler():
    params = {'returnTo': 'http://localhost:5000/', 'client_id': app.config['AUTH0_CLIENT_ID']}
    resp = make_response(redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params)))
    resp.delete_cookie('cast_user')
    return resp


@app.route('/callback')
def callback_handler():
    # Handles response from token endpoint
    try:
        auth0.authorize_access_token()
        resp = auth0.get('userinfo')
        userinfo = resp.json()
        if userinfo['email'] in app.config['USERS']:
            token = jwt.encode(payload=userinfo, key=app.config['JWT_SECRET'], algorithm='HS256')
            response = make_response(redirect('/admin'))
            response.set_cookie('cast_user', token, expires = datetime.datetime.now() + datetime.timedelta(days=30))
            return response
        else:
            return redirect('/not-allowed')
    except:
        return redirect('/')


@app.get('/not-allowed')
@check_user
@templated('not-allowed')
def not_allowed_handler(userobj):
    return 'you\'re not allowed to do that' +  ' | ' + userobj['given_name']


@app.get('/admin')
@requires_privilege('admins')
@templated('admin/home')
def admin_home_handler(userobj):
    # TODO think about what this should contain? Stats? Recent actions?
    return 'admin home'

@app.get('/admin/users')
@requires_privilege('admins')
def admin_users_handler(userobj):
    # TODO list of users with sorting
    return 'admin/ list users'+ ' | ' + userobj['given_name']


@app.get('/admin/users/edit/<string:uid>')
@requires_privilege('admins')
def admin_user_edit_handler(userobj, uid):
    # TODO edit of a user of coffee connections
    return 'admin/ edit user' + uid + ' | ' + userobj['given_name']


@app.get('/admin/users/view/<string:uid>')
@requires_privilege('admins')
def admin_user_view_handler(userobj, uid):
    # TODO view of a user of coffee connections
    return 'admin/ view user' + uid + ' | ' + userobj['given_name']


@app.get('/admin/users/approve/<string:uid>')
@requires_privilege('admins')
def admin_user_approve_handler(userobj, uid):
    # TODO approve of a user of coffee connections
    return 'admin/ approve user' + uid + ' | ' + userobj['given_name']


@app.get('/admin/matches/create')
@requires_privilege('admins')
# TODO think about what this does. Does it create a new match table? Does it populate with guessed matches
def admin_create_matches_handler(userobj):
    return 'admin/ create matches '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/view')
@requires_privilege('admins')
def admin_view_matches_handler(userobj):
    # TODO show matches
    return 'admin/ view matches '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/edit')
@requires_privilege('admins')
def admin_edit_matches_handler(userobj):
    # TODO edit matches
    return 'admin/ edit matches '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/test')
@requires_privilege('admins')
def admin_test_matches_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
        return 'admin/ send test matches '+ ' | ' + userobj['given_name']


@app.post('/admin/matches/test')
@requires_privilege('admins')
def admin_test_matches_confirm_handler(userobj):
    return 'admin/ send test matches confirmed '+ ' | ' + userobj['given_name']


# TODO email permission decorator
@app.get('/admin/matches/send')
@requires_privilege('senders')
def admin_send_matches_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
    return 'admin/ send live matches '+ ' | ' + userobj['given_name']


# TODO email permission decorator
@app.post('/admin/matches/send')
@requires_privilege('senders')
def admin_send_matches_confirm_handler(userobj):
    return 'admin/ send live matches confirmed '+ ' | ' + userobj['given_name']


