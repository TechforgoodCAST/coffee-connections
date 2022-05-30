from flask import Flask, redirect, url_for, request, make_response

import asyncio

from functools import wraps
import uuid

import toml
import csv

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
    """
    This function takes data from a signup form and creates a user
    """

    # TODO have this called from whatever we're using for sign up
    fields = get_fields('Person')

    print (fields)    
    new_person = Person({
        'given_name':'Chris',
        'family_name':'Thorpe',
        'email':'chris@wearecast.org.uk',
        'job_title':'Head of Technology',
        'description':'An open data and open standards and reuse nerd',
        'knows_about': 'Open standards, open data, reuse, some technology, digital strategy',
        'work_location':'Remote',
        'seeks': 'Enlightenment, peace and tranquility.',
        'cc__digital_journey': 'It\'s embedded into what we do across all areas and our daily practices',
        'cc__validated_mail': True,
        'cc_created_at': None,
        'cc__consent': True,
        'cc__status': '100',
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


@app.get('/users/import')
def csv_user_loader():
    """
    This function loads historic data and creates individual files for users and a collected file of all users, persisted in S3
    """
    row_count = 0
    import_count = 0
    match_count = 0
    match_error_count = 0
    historic_users = {}
    unique_ids = []
    # first off, we'll import the users into the historic users dictionary
    with open('livedata/cc_users.csv', newline='') as csvfile:
        cc_historic_users = csv.reader(csvfile, delimiter=',')
        for historic_user in cc_historic_users:
            # first row contains the labels
            if row_count == 0:
                # map the labels from the CSV to the new variable names from schema.org
                fields = map_historic_data_fields(historic_user)
                row_count += 1
            else:
                # ignore empty rows
                if len(historic_user) > 0:
                    # joing field names and fields from the CSV
                    userdict = {key:value for (key, value) in list(zip(fields, historic_user))}
                    # append the original id to an array of unique ids
                    id = userdict['cc__historic_id']
                    unique_ids.append(id)
                    # combine the data from two fields to form the organisation
                    if len(userdict['works_for-name']) > 0:
                        userdict['works_for'] = {
                            'identifier':userdict['works_for-identifier'],
                            'name': userdict['works_for-name']
                        }
                    # and then remove those two fields from the user dictionary
                    del userdict['works_for-name']
                    del userdict['works_for-identifier']
                    # we're dealing with historic data, so we'll set the email validation field to True as they're existing users who've been mailed
                    userdict['cc__validated_mail'] = True
                    # then load the Person pydantic model to check for validation errors
                    person = Person(userdict)
                    if person.has_errors():
                        print (person.has_errors())
                    else:
                        # if there are no errors, we'll add them to the historic users dictionary and increment the import counter
                        import_count += 1
                        historic_users[id] = person.as_dict()
                    # increment the row counter so we can compare rows in the dataset to number of successful imports
                    row_count += 1
    # now we'll iterate through the previous matches 
    #TODO check with Coffee Connections team about run 16. Was it sent?
    with open('livedata/cc_matches.csv', newline='') as csvfile:
        previous_matches = csv.reader(csvfile, delimiter=',')
        match_row_count = 0
        for previous_match in previous_matches:
            # ignore the first row as that's labels
            if match_row_count > 0:
                match_1 = previous_match[1]
                match_2 = previous_match[2]
                run = previous_match[3]
                # the data contains some matches where the user is no longer in the dataset
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
                    match_error_count += 1
            # increment the match row count. due to the missing user this will not match the count of the matches
            match_row_count += 1
    # now that we've associated the users with the matches we'll iterate through again to check for errors
    processed_users = {}
    for id in historic_users:
        persondict = historic_users[id]
        person = Person(persondict)
        if person.has_errors():
            print (person.has_errors())
        else:
            processed_user = person.as_dict()
            processed_users[processed_user['identifier']] = processed_user
    # 
    match_row_count -= 1
    row_count -=1
    return {'users':processed_users, 'row_count':row_count, 'import_count':import_count, 'unique_id_count':len(unique_ids), 'match_count':match_count, 'match_row_count':match_row_count, 'match_error_count':match_error_count}


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



