
from typing import Dict, List
_models = __import__("models")

def get_fields(modelname:str) -> List:
    """
    This function takes the name of a model and returns a list of all the fields (so that form input can be captured for example)
    
    Args:
        modelname (str): the name of the model
    
    Returns:
        List: an array of the field names
    """
    _model = getattr(_models,modelname)
    model = _model({}).as_schema()
    print (model)
    fields = []
    for field in model['properties']:
        if '$ref' in model['properties'][field]:
            unpackmodelname = model['properties'][field]['$ref'].replace('#/definitions/','').replace('Model','')
            unpackfields = get_fields(unpackmodelname)
            for unpackfield in unpackfields:
                fields.append(f'{field}-{unpackfield}')
        else:
            fields.append(field)
    return fields




def map_historic_data_fields(fields:List) -> List:
    """
    This function takes a list of historic field names from the Coffee Connections database and returns a list of the schema.org derived field names
    
    Args:
        fields (List): the fields to be convered

    Returns:
        List : mapped fields, a list of the schema.org derived field names
    """
    mapping = {
        'id': 'cc__id',
        'first_name': 'given_name',
        'last_name': 'family_name',
        'org': 'works_for-name',
        'email':'email',
        'domain': 'works_for-identifier',
        'job_title': 'job_title',
        'bio': 'description',
        'region': 'work_location',
        'consent_text': 'cc__consent_text',
        'digital_journey': 'cc__digital_journey',
        'created_at': 'cc__created_at',
        'updated_at': 'cc__updated_at',
        'status': 'cc__status',
        'consent': 'cc__consent'
    }
    mapped_fields = [mapping[field] for field in fields]
    return mapped_fields
