import json
from core.web import discord, jinja_env
from replit import db
from flask import session
from replit import database

#we override the default json encoder to allow ourselves to serialize replit's mutable objects
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, database.database.ObservedDict):
            return dict(obj.items())
        if isinstance(obj, database.database.ObservedList):
            return list(obj)
        return json.JSONEncoder.default(self, obj)
json.JSONEncoder.default = CustomJSONEncoder.default

#stores any loaded users
_cache = {}

@jinja_env
def get_id(user=None):
    override = session.get('override')
    return str(
        user if user is not None else 
        override if override is not None else
        discord.fetch_user().id)

def _load(user=None):
    user = get_id(user)

    #loads the user data first from the cache, then from the database
    if user in _cache:
        obj = _cache[user]
    elif user in db.keys():
        obj = db.get(user)
    else:
        obj = {}
    
    #caches the loaded object
    _cache[user] = obj
    
    return obj

def get(key, *, user=None):
    #deepcopies to prevent editing
    return json.loads(json.dumps((_load(user).get(key, {}))))

def set(key, value, *, user=None):
    obj = _load(user)

    #updates both the cache and the database
    obj[key] = value
    db.set(get_id(user), obj)

def keys():
    return db.keys()

def delete(*, user):
    if user in db:
        del db[user]
    if user in _cache:
        del _cache[user]