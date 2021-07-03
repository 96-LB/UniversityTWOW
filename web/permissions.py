from core.web import discord, jinja_env
from flask import abort
from flask_discord import requires_authorization
from functools import wraps

#discord user @96 LB#5274
ADMIN = 236257776421175296 

@jinja_env
def is_admin():
    return discord.authorized and discord.fetch_user().id == ADMIN

def requires_admin(f):
    #returns 403 unauthorized if the user is not an administrator
    @wraps(f)
    @requires_authorization
    def decorator(*args, **kwargs):
        if not is_admin():
            abort(403)
        else:
            return f(*args, **kwargs)
    return decorator