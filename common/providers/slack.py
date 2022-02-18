from flask import current_app

import json
import logging

from .http import httpProvider
from common.templating import render



class slackProvider():

    webhook = None

    def __init__(self):
        self.webhook = current_app.config['SLACK_WEBHOOK']


    def put(self, message):
        response = httpProvider().post(self.webhook, message, 'txt')
        return response


    def send_templated_message(self, template, variables):
        message, code = render('messages/{template}.jnj'.format(template=template), variables, format='json')
        resp = self.put(message)
        if resp is not None:
            return True
        else: 
            return False


async def send_slack_message(template, variables):
    return slackProvider().send_templated_message(template, variables)
    
