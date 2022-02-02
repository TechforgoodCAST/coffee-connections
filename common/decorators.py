from flask import request, current_app, redirect

from functools import wraps

from .authentication import get_user_from_cookie
from .templating import render

import logging

def check_user(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        userobj = get_user_from_cookie(request, current_app.config)
        kwargs['userobj'] = userobj
        return f(*args, **kwargs)
    return decorated


def requires_privilege(privilege=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            userobj = get_user_from_cookie(request, current_app.config, privilege=privilege)
            kwargs['userobj'] = userobj
            if userobj:
                if privilege in userobj['privileges']:
                    return f(*args, **kwargs)
                else:
                    return redirect('/not-allowed')
            else: 
                return redirect('/login')
        return decorated
    return decorator



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
                return ctx
            else:
                ctx['userobj'] = kwargs['userobj']
                if '/' in template_name:
                    section = template_name.split('/')[0]
                    ctx['nav'] = section
            return render(template_name, ctx)
        return decorated_function
    return decorator