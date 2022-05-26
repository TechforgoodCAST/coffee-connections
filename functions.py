
_models = __import__("models")

def get_fields(modelname):
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
