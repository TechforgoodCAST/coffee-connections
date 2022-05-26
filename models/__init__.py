from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from pydantic import ValidationError
from datetime import datetime
from uuid import UUID, uuid4

import humps
import json

import importlib

import logging


def uuid_convert(field: UUID) -> str:
    """
    Converts a UUID to the hex string equivalent

    Args:
        field (UUID) : the UUID contained in the string
    
    Returns:
        str : the hex string equivalent
    """
    if isinstance(field, UUID):
        return field.hex

def to_camel(string: str) -> str:
    return ''.join(word.capitalize() for word in string.split('_'))


def to_snake_case(string: str) -> str:
    return ''.join(['_' + i.lower() if i.isupper() else i for i in string]).lstrip('_')

def now():
    return datetime.now().isoformat()

class ConfigModel(BaseModel):
    pass
    #class Config:
    #    alias_generator = humps.camelize


class OrganizationModel(ConfigModel):
        identifier : Optional[str] = Field(
            default=None, title="The identifier for the organisation which is the domain name of the email address"
        )
        name : Optional[str] = Field(
            default=None, title="The name of the organisation"
        )


class PersonModel(ConfigModel):
        _form_field_types = {
            'given_name':'text',
            'family_name':'text',
            'email':'email',
            'job_title':'text',
            'seeks':'textarea',
            'knows_about':'textarea',
            'work_location':'text',
            'description':'textarea',
            'works_for-name':'text',
            'cc__digital_journey':'textarea',
            'cc__consent':'checkbox'
        }
        """
        This model is derived from https://schema.org/Person

        Fields starting with "cc__" are namespaced extensions of the model specific to Coffee Connections
        """
        identifier : UUID = Field(default_factory=uuid4)
        given_name : str = Field(
            default=None, title="The given name of the person"
        )
        family_name : str = Field(
            default=None, title="The family name of the person"
        )
        email : str = Field(
            default=None, title="The email address of the person"
        )
        job_title : str = Field(
            default=None, title="The job title of the person"
        )
        seeks : Optional[str] = Field(
            default=None, title="What the person is seeking from Coffee Connections"
        )
        knows_about : Optional[str] = Field(
            default=None, title="What the person knows about and are willing to share with their connections"
        )
        work_location : str = Field(
            default=None, title="Where the person is based"
        )
        description : Optional[str] = Field(
            default=None, title="A short biography (bio field from previous data)"
        )
        works_for : Optional[OrganizationModel] = Field(
            default=None, title="Who the person works for"
        )
        alumni_of : Optional[List[OrganizationModel]] = Field(
            default=None, title="Organisation the person has worked for previously"
        )
        cc__digital_journey : Optional[str] = Field(
            default=None, title="The digital journey of the person"
        )
        cc__validated_mail : bool = Field(
            default=False, title="Whether the person has validated their email address"
        )
        cc__approve_secret : UUID = Field(
            default_factory=uuid4, title="The secret for the email address validation"
        )
        cc__region : Optional[str] = Field(
            default=None, title="The region in which the person works"
        )
        cc__created_at : str = Field(
            default_factory=now, title="The creation timestamp for the person record as an isoformat datetimestring"
        )
        cc__updated_at : Optional[str] = Field(
            default=None, title="The creation timestamp for the person record as an isoformat datetimestring"
        )
        cc__status : Optional[str] = Field(
            default=None, title="The status code for the person"
        )
        cc__consent : bool = Field(
            default=False, title="Whether or not they have given consent to be part of Coffee Connections"
        )
        cc__consent_text : str = Field(
            default=None, title="The text of the consent form"
        )

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
            return json.dumps({'errors': json.loads(self._errors)})
        else:
            model = self.as_dict()
            return json.dumps(model, default=uuid_convert)


    def as_dict(self):
        if self._errors:
            return {'errors': json.loads(self._errors)}
        else:
            model = self._Model.dict(by_alias=True)
            for key in model:
                if key[0] == '_':
                    del model[key]
            return model


    def as_schema(self, format='json'):
        _Model = self.select_model()
        return _Model.schema()


    def form_field_types(self):
        return self._Model._form_field_types





class Person(Model):
    pass


class Organization(Model):
    pass
