import jwt
import logging


def check_user_privileges(userobj, config, privilege):
    userobj['privileges'] = []
    if privilege.upper() in config:
        if userobj['email'] in config[privilege.upper()]:
            userobj['privileges'].append(privilege)
    return userobj



def get_user_from_cookie(request, config, privilege=None):
    token = request.cookies.get('cast_user')
    if token:
        try:
            userobj = jwt.decode(token, key=config['JWT_SECRET'], algorithms=["HS256"])
        except:
            userobj = None
    else:
        userobj = None
    if userobj:
        if privilege:
            userobj = check_user_privileges(userobj, config, privilege)
    if userobj:
        return userobj
    else:
        return None


