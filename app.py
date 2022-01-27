from flask import Flask
import toml
import logging

from models import Person, Organization


app = Flask(__name__)
# load the config file from the TOML formatted file (not checked into repository)
app.config.from_file('config.toml', toml.load)



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
    return 'login'

@app.post('/login')
def login_handler():
    # TODO login using Auth0
    return 'login'





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
