
import json


def request2json(request):
    if type(request.body)!=dict:
        req = json.loads(request.body)
    else:
        req = request.body
    return req


def keys1_in_keys2(keys1,keys2):
    for k in keys1:
        if k not in keys2:
            return False
    return True

def file_to_name_type(file_name):
    x=file_name.split('.')
    return ''.join(x[:-1]),x[-1]
