import json
from core.web import discord, jinja_env
from replit import db
from copy import deepcopy
from flask import session

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
        obj = json.loads(db[user])
    else:
        obj = {}
    
    #caches the loaded object
    _cache[user] = obj
    
    return obj

def get(key, *, user=None):
    #deepcopies to prevent editing
    return deepcopy(_load(user).get(key, {}))

def set(key, value, *, user=None):
    obj = _load(user)

    #updates both the cache and the database
    obj[key] = value
    db[get_id(user)] = json.dumps(obj)