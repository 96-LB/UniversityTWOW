from core.web import app
from flask import session, redirect, url_for
from web.permissions import requires_admin

@app.route('/override')
@requires_admin
def override():
    #resets to administrator user
    session['override'] = None
    return redirect(url_for('index'), 303)

@app.route('/override/<int:user>')
@requires_admin
def override_user(*, user):
    #overrides the data module's id in order to read other data
    session['override'] = user
    return redirect(url_for('index'), 303)