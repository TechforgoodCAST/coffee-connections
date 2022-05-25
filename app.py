from flask import Flask, redirect, url_for, request, make_response

import asyncio

from functools import wraps
import datetime
import uuid

import toml
import logging


from common.providers import sendGridProvider, send_email


from models import Person, Organization


app = Flask(__name__)

# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)


@app.get('/schema')
def schema_handler():
    person = Person({'name':'blank'})
    return person.as_schema()


@app.get('/test')
def test_handler():
    asyncio.run(send_email('signup', ['chris@wearecast.org.uk'], 'Welcome to Coffee Connections', {'first_name':'Chris', 'hostname':'http://localhost:5000', 'uid': uuid.uuid4().hex}))
    return 'hello'


@app.get('/users/add')
def signup_handler():
    # TODO persist the model in InnoDB
    # TODO fire signup email
    # TODO notify Slack of new signup
    return 'from user signup form'


@app.get('/users/add/thank-you')
def signup_thankyou_handler():
    return 'thanking user for signup'


@app.get('/users/confirm-email/<string:uuid>')
def confirm_user_handler(uuid):
    # TODO notify Slack of confirmation
    return 'email confirmation'



@app.get('/admin/users/approve/<string:uid>')
def admin_user_approve_handler(userobj, uid):
    # TODO approve of a user of coffee connections
    return 'admin/ approve user' + uid + ' | ' + userobj['given_name']


@app.get('/admin/matches/create')
# TODO think about what this does. Does it create a new match table? Does it populate with guessed matches
def admin_create_matches_handler(userobj):
    return 'admin/ create matches '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/view')
def admin_view_matches_handler(userobj):
    # TODO show matches
    return 'admin/ view matches '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/test')
def admin_test_matches_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
        return 'admin/ send test matches '+ ' | ' + userobj['given_name']


@app.post('/admin/matches/test')
def admin_test_matches_confirm_handler(userobj):
    return 'admin/ send test matches confirmed '+ ' | ' + userobj['given_name']


@app.get('/admin/matches/send')
def admin_send_matches_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
    return 'admin/ send live matches '+ ' | ' + userobj['given_name']


# TODO email permission decorator
@app.post('/admin/matches/send')
def admin_send_matches_confirm_handler(userobj):
    return 'admin/ send live matches confirmed '+ ' | ' + userobj['given_name']


@app.get('/admin/followups/test')
def admin_test_followups_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
        return 'admin/ send test matches '+ ' | ' + userobj['given_name']


@app.post('/admin/followups/test')
def admin_test_followups_confirm_handler(userobj):
    return 'admin/ send test matches confirmed '+ ' | ' + userobj['given_name']


# TODO email permission decorator
@app.get('/admin/followups/send')
def admin_send_followups_handler(userobj):
    # TODO show form which will approve the sending, make it have some friction
    return 'admin/ send live matches '+ ' | ' + userobj['given_name']


# TODO email permission decorator
@app.post('/admin/followups/send')
def admin_send_followups_confirm_handler(userobj):
    return 'admin/ send live matches confirmed '+ ' | ' + userobj['given_name']



