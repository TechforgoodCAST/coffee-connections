from flask import current_app
from typing import List, Tuple

import markdown

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from common.templating import render



class sendGridProvider():

    api_key = None

    def __init__(self):
        self.api_key = current_app.config['SENDGRID_API_KEY']
        self.from_email = current_app.config['SENDER_EMAIL']
 

    def send(self, to_emails:List[str], subject:str, content:str) -> Tuple:
        message = Mail(
            from_email=self.from_email,
            to_emails=to_emails,
            subject=subject,
            html_content=content)
        try:
            sg = SendGridAPIClient(self.api_key)
            response = sg.send(message)
            if response.status_code == 202:
                return {'body':response.body}, True, []
            else:
                return {'body':response.body}, False, ['unknown_error']
        except Exception as e:
            return {}, False, e.message


    def send_templated_message(self, template, to_emails, subject, variables):
        message, code = render('emails/{template}.jnj'.format(template=template), variables, format='email')
        message = markdown.markdown(message)
        resp, success, errors = self.send(to_emails, subject, message)
        if resp is not None:
            return True
        else: 
            return False


async def send_email(template, to_emails, subject, variables):
    return sendGridProvider().send_templated_message(template, to_emails, subject, variables)
