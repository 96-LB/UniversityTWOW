from core.web import app, discord
from flask import abort
from flask_discord import requires_authorization
from functools import wraps

#discord user @96 LB#5274
ADMIN = 236257776421175296 

def is_admin():
    return discord.authorized and discord.fetch_user().id == ADMIN

app.jinja_env.globals['is_admin'] = is_admin

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