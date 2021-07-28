from core.web import app
from flask import session, redirect, url_for
from web.permissions import requires_admin

def requires_overrider(f):
    #requires admin permissions, unless the user is disabling an override
    def decorator(*args, user=None, **kwargs):
        func = f if session.get('override') and user is None else requires_admin(f)
        return func(*args, user=user, **kwargs)
    return decorator

def override_internal(user=None):
    #abstraction so that the code can modify override without admin permissions
    session['override'] = user
    return redirect(url_for('index'), 303)

@app.route('/override')
@app.route('/override/<int:user>')
@requires_overrider
def override(*, user=None):
    #visiting /override/<id> overrides the data module's id, tricking the website
    #visiting /override resets your id back to normal
    #the @requires_overrider decorator ensures that no unauthorized users can visit this page!
    return override_internal(user)

test = '31415926535897932'
@app.route(f'/override/{test}')
def override_test():
    #just some testing code -- this is guaranteed safe
    return override_internal(test)
