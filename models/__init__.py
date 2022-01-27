from typing import List, Dict, Optional
from pydantic import BaseModel
from pydantic import ValidationError
import humps

import importlib

import logging



def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


def to_snake_case(string: str) -> str:
    return ''.join(['_' + i.lower() if i.isupper() else i for i in string]).lstrip('_')



class ConfigModel(BaseModel):

    class Config:
        alias_generator = humps.camelize


class OrganizationModel(ConfigModel):
        identifier : str
        name : str


class PersonModel(ConfigModel):
        identifier : str
        given_name : str
        family_name : str
        email : str
        job_title : str
        seeks : Optional[str]
        knows_about : Optional[str]
        work_location : str
        description : Optional[str]
        works_for : OrganizationModel
        alumni_of : Optional[List[OrganizationModel]]


class Model():

    def __init__(self, variables):
        self._errors = None
        self._schema = None

        _Model = self.select_model()
        self.schema = _Model.schema()
        try:
            self._Model = _Model(**variables)

        except ValidationError as e:
            self._errors = e.json()


    def select_model(self):
        _model_name = self.__class__.__name__ + 'Model'
        _module = importlib.import_module('models')
        _Model = getattr(_module,_model_name)
        return _Model


    def has_errors(self):
        if self._errors:
            return self._errors
        else:
            return False


    def as_json(self):
        if self._errors:
            return None
        else:
            return json.dumps(self._Model.dict())


    def as_dict(self):
        if self._errors:
            return None
        else:
            return self._Model.dict(by_alias=True)


    def as_schema(self, format='json'):
        _Model = self.select_model()
        self.schema = _Model.schema()
        self.schema['title'] = self.schema['title'].replace('Model', '')
        return _Model.schema()


class Person(Model):
    pass


class Organization(Model):
    pass
