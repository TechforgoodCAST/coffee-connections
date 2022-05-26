from flask import Flask, redirect, url_for, request, make_response

import asyncio

from functools import wraps
import datetime
import uuid

import toml
import logging

import importlib


from common.providers import sendGridProvider, send_email
from common.utilities import request_variables

from models import Person, Organization

_models = __import__("models")

app = Flask(__name__)

# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)


@app.get('/schema')
def schema_handler():
    """
    This function outputs the schema used for the application
    """
    person = Person({'name':'blank'})
    return person.as_schema()


@app.get('/test')
def test_handler():
    asyncio.run(send_email('signup', ['chris@wearecast.org.uk'], 'Welcome to Coffee Connections', {'first_name':'Chris', 'hostname':'http://localhost:5000', 'uid': uuid.uuid4().hex}))
    return 'hello'


def get_fields(modelname):
    _model = getattr(_models,modelname)
    model = _model({}).as_schema()
    print (model)
    fields = []
    for field in model['properties']:
        if '$ref' in model['properties'][field]:
            unpackmodelname = model['properties'][field]['$ref'].replace('#/definitions/','').replace('Model','')
            unpackfields = get_fields(unpackmodelname)
            for unpackfield in unpackfields:
                fields.append(f'{field}-{unpackfield}')
        else:
            fields.append(field)
    return fields


@app.get('/users/add')
def signup_handler():
    # TODO have this called from whatever we're using for sign up
    fields = get_fields('Person')
    print (fields)
    
    new_person = Person({
        'given_name':'Chris',
        'family_name':'Thorpe',
        'email':'chris@wearecast.org.uk',
        'job_title':'Head of Technology',
        'work_location':'Remote',
        'cc__validated_mail': True,
        'cc_created_at': None,
        'cc__consent': True,
        'cc__consent_text': 'consent text',
        'works_for': {
            'identifier':'wearecast.org.uk',
            'name': 'CAST'
        }
    })
    print (new_person.form_field_types())
    # TODO persist the model in InnoDB or similar
    # TODO fire signup email
    # TODO notify Slack of new signup
    return new_person.as_json()


@app.get('/users/confirm-email/<string:uuid>')
def confirm_user_handler(uuid):
    # TODO show as a web page, style to be defined
    # TODO notify Slack of confirmation
    return 'email confirmation'


@app.get('/admin/users/approve/<string:identifier>')
def admin_user_approve_handler(identifier):
    # TODO approve of a user of coffee connections - as a button in Slack
    return 'admin/ approve user' + identifier


@app.get('/admin/matches/create')
# TODO think about what this does. Does it create a new match table? Does it populate with guessed matches
def admin_create_matches_handler():
    return 'admin/ create matches'


@app.get('/admin/matches/view')
def admin_view_matches_handler():
    # TODO show matches
    return 'admin/ view matches'


@app.get('/admin/matches/test')
def admin_test_matches_handler():
    # TODO show form which will approve the sending, make it have some friction
    return 'admin/ send test matches'


@app.get('/admin/matches/test/confirmed')
def admin_test_matches_confirm_handler():
    return 'admin/ send test matches confirmed'


@app.get('/admin/matches/send')
def admin_send_matches_handler():
    # TODO show form which will approve the sending, make it have some friction
    return 'admin/ send live matches'


@app.get('/admin/matches/send/confirmed')
def admin_send_matches_confirm_handler():
    return 'admin/ send live matches confirmed'


@app.get('/admin/followups/test')
def admin_test_followups_handler():
    # TODO show form in Slack which will approve the sending, make it have some friction
    return 'admin/ send test matches'


@app.get('/admin/followups/test/confirmed')
def admin_test_followups_confirm_handler():
    return 'admin/ send test matches confirmed'


# TODO email permission decorator
@app.get('/admin/followups/send')
def admin_send_followups_handler():
    # TODO show form in Slack which will approve the sending, make it have some friction
    return 'admin/ send live matches'


# TODO email permission decorator
@app.get('/admin/followups/send/confirmed')
def admin_send_followups_confirm_handler():
    return 'admin/ send live matches confirmed'



