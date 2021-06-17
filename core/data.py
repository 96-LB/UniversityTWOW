import json, core.web as web
from replit import db
from copy import deepcopy

#stores any loaded users
_cache = {}

def _load():
    user = web.discord.fetch_user()
    
    #loads the user data first from the cache, then from the database
    if user.id in _cache:
        obj = _cache[user.id]
    elif user.id in db.keys():
        obj = json.loads(db[user.id])
    else:
        obj = {}
    
    #caches the loaded object
    _cache[user.id] = obj
    
    return obj

def get(key):
    return deepcopy(_load().get(key))

def set(key, value):
    user = web.discord.fetch_user()
    obj = _load()

    #updates both the cache and the database
    obj[key] = value
    db[user.id] = json.dumps(obj)
