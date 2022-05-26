from typing import Callable
from typing import List, Dict, Optional, Callable, Union
from flask import current_app, request


"""
This function is used retrieve the hostname so that URLs can be built dynamically and the live/development context switches can be made. 

Args:
    request (flask request object)
"""
def get_hostname(request : Callable) -> str:
    return request.url_root



def request_variables(form, params=None):
    if not params:
        params = [element for element in form['elements']]
    variables = {}
    default_value = None
    for param in params:
        variables[param] = None
        if request.method == "GET":
            variables[param] = request.args.get(param)
        else:
            if 'multi' in form['elements'][param]:
                variables[param] = request.values.getlist(param)
            else:
                try:
                    variables[param] = request.form[param]
                    if form:
                        if form['elements'][param]['display'] == 'textarea':
                            variables[param] = '\n'.join(request.form[param].splitlines())
                        elif form['elements'][param]['display'] == 'text':
                            variables[param] = ' '.join(request.form[param].splitlines())
                except:
                    try:
                        variables[param] = request.get_json()[param]
                    except:
                        variables[param] = None
        if form:
            if 'null_text' in form['elements'][param]:
                if variables[param] == form['elements'][param]['null_text']:
                    variables[param] = None
        if variables[param] is not None and len(variables[param]) == 0:
            variables[param] = None
        if variables[param] == 'None':
            variables[param] = None
    return variables