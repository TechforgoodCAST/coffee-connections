from typing import List, Dict, Optional, Callable, Union

from flask import render_template, current_app


"""
This function is used to retrieve the user cookie it does no checking of the privileges of that user

Args:
    template_name (string): name of the template, with or without the file extension if it's an HTML template
    variables (dictionary): dictionary of variables to be shown in the templated response
    code (integer): the http response code
    format (string): the template format (html, json etc)
"""
def render(template_name : str, variables : Dict, code=200, format='html') -> str:
    if format == 'html':
        if 'holding_page' in variables:
            variables['navset'] = current_app.config['NAVSET']['holding']
        else:
            variables['navset'] = current_app.config['NAVSET']['normal']
        variables['navelements'] = [current_app.config['NAVELEMENTS'][navitem] for navitem in variables['navset']]
        if ".html" not in template_name:
            template_name += ".html"
    return render_template(template_name, **variables), code
