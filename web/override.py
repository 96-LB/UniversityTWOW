import core.data as data
from core.web import app, discord
from flask import abort, redirect, url_for
from flask_discord import requires_authorization
from functools import wraps

#discord user @96 LB#5274
admin = 236257776421175296 

def is_admin():
    return discord.authorized and discord.fetch_user().id == admin

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

@app.route('/override')
@requires_admin
def override():
    #resets to administrator user
    return redirect(url_for('override_user', user=admin), 303)

@app.route('/override/<int:user>')
@requires_admin
def override_user(user):
    #overrides the data module's id in order to read other data
    data._id = user
    return redirect(url_for('index'), 303)