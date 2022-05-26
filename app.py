from flask import Flask, redirect, url_for, request, make_response

import asyncio

from functools import wraps
import datetime
import uuid

import toml
import logging
import csv

import importlib


from common.providers import sendGridProvider, send_email
from common.utilities import request_variables

from models import Person, Organization
from functions import get_fields, map_historic_data_fields

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


@app.get('/users/load')
def csv_user_loader():
    i = 0
    j = 0
    historic_users = {}
    matches = {}
    unique_ids = []
    match_count = 0
    with open('livedata/cc_users.csv', newline='') as csvfile:
        cc_historic_users = csv.reader(csvfile, delimiter=',')
        for historic_user in cc_historic_users:
            if i == 0:
                fields = map_historic_data_fields(historic_user)
                print (fields)
                i += 1
            else:
                if len(historic_user) > 0:
                    userdict = {key:value for (key, value) in list(zip(fields, historic_user))}
                    id = userdict['cc__id']
                    unique_ids.append(id)
                    if len(userdict['works_for-name']) > 0:
                        userdict['works_for'] = {
                            'identifier':userdict['works_for-identifier'],
                            'name': userdict['works_for-name']
                        }
                    del userdict['works_for-name']
                    del userdict['works_for-identifier']
                    userdict['cc__validated_mail'] = True
                    person = Person(userdict)
                    if person.has_errors():
                        print (person.has_errors())
                    else:
                        j += 1
                        historic_users[id] = person.as_dict()
                    i += 1
    with open('livedata/cc_matches.csv', newline='') as csvfile:
        previous_matches = csv.reader(csvfile, delimiter=',')
        print(matches)
        a = 0
        for previous_match in previous_matches:
            if a > 0:
                match_1 = previous_match[1]
                match_2 = previous_match[2]
                run = previous_match[3]
                try:
                    historic_users[match_1]['cc__matches'].append(historic_users[match_2]['identifier'])
                    if run not in historic_users[match_1]['cc__runs']:
                        historic_users[match_1]['cc__runs'].append(run)
                    historic_users[match_2]['cc__matches'].append(historic_users[match_1]['identifier'])
                    if run not in historic_users[match_2]['cc__runs']:
                        historic_users[match_2]['cc__runs'].append(run)
                    match_count += 1
                except:
                    print ((match_1, match_2, run))

            a += 1
    processed_users = {}
    for id in historic_users:
        persondict = historic_users[id]
        person = Person(persondict)
        if person.has_errors():
            print (person.has_errors())
        else:
            processed_user = person.as_dict()
            processed_users[processed_user['identifier']] = processed_user
    return {'users':processed_users, 'count':i-1, 'success':j, 'unique_id_count':len(unique_ids), 'match_count':match_count}


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



