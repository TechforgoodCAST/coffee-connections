from flask import request, current_app, redirect

from functools import wraps

from .templating import render

import logging


def templated(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = f"{request.endpoint.replace('.', '/')}.html"
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                ctx = {'content': ctx}
            ctx['site_title'] = current_app.config['SITE_TITLE']
            if 'userobj' in ctx:
                ctx['userobj'] = kwargs['userobj']
            else:
                ctx['userobj'] = None
            if '/' in template_name:
                section = template_name.split('/')[0]
                ctx['nav'] = section
            return render(template_name, ctx)
        return decorated_function
    return decorator