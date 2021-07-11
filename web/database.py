import json
from core.web import app
from web.permissions import requires_admin
from web.logs import PREFIX
from replit import db

@app.route('/database/<string:filter_type>')
@requires_admin
def database(filter_type):
    #selects a filter to use
    try:
        filter_func = {
            'all': lambda x: True,
            'students': lambda x: x.isdigit(),
            'classes': lambda x: 6 <= len(x) <= 7 and x[-3:].isdigit(),
            'logs': lambda x: x.startswith(PREFIX)
        }[filter_type]
    except:
        return {'ERROR': 'Invalid filter type.'}

    #outputs the database as a json object
    obj = {}
    for key in db:
        if filter_func(key):
            obj[key] = json.loads(db[key])
    return obj