from typing import Callable
from typing import List, Dict, Optional, Callable, Union
from flask import current_app


"""
This function is used retrieve the hostname so that URLs can be built dynamically and the live/development context switches can be made. 

Args:
    request (flask request object)
"""
def get_hostname(request : Callable) -> str:
    return request.url_root

