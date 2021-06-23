import json
from core.web import app, discord
from replit import db
from copy import deepcopy


#stores any loaded users
_cache = {}

#overridden id
_id = None

def get_id():
    return str(_id if _id is not None else discord.fetch_user().id)

app.jinja_env.globals['get_id'] = get_id

def _load():
    user = get_id()
    
    #loads the user data first from the cache, then from the database
    if user in _cache:
        obj = _cache[user]
    elif user in db.keys():
        obj = json.loads(db[user])
    else:
        obj = {}
    
    #caches the loaded object
    _cache[user] = obj
    
    return obj

def get(key):
    #deepcopies to prevent editing
    return deepcopy(_load().get(key, {}))

def set(key, value):
    user = get_id()
    obj = _load()

    #updates both the cache and the database
    obj[key] = value
    db[user] = json.dumps(obj)