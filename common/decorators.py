from flask import request, make_response, current_app, redirect

import jwt

from functools import wraps

from .authentication import get_user_from_cookie



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