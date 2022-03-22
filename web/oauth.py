from core.web import app, discord
from flask import redirect, url_for, request
from flask_discord import Unauthorized, AccessDenied
from oauthlib import oauth2

ERRORS = oauth2.rfc6749.errors

@app.errorhandler(Unauthorized)
@app.errorhandler(ERRORS.TokenExpiredError)
@app.errorhandler(ERRORS.InvalidGrantError)
def error_unauthorized(error):
    discord.revoke()
    return redirect(url_for('login', next=request.path), 303)

@app.route('/login')
def login():
    next_page = request.args.get('next', 'index')
    return discord.create_session(['identify'], prompt=False, data={'next': next_page})

@app.route('/logout')
def logout():
    discord.revoke()
    return redirect(url_for('index'), 303)

@app.route('/callback')
def callback():
    next_page = url_for('index')
    try:
        next_page = discord.callback()['next']
    except (AccessDenied, KeyError, ERRORS.MismatchingStateError, ERRORS.InvalidClientIdError):
        pass
    return redirect(next_page, 303)