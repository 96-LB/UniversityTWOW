from core.web import app, discord
from flask import redirect, url_for, request
from flask_discord import Unauthorized, AccessDenied

@app.errorhandler(Unauthorized)
def error_unauthorized(error):
    return redirect(url_for('login'), 303)

@app.route('/login')
def login():
    next_page = request.args.get('next', 'index')
    return discord.create_session(['identify'], prompt=False)

@app.route('/logout')
def logout():
    discord.revoke()
    return redirect(url_for('index'), 303)

@app.route('/callback')
def callback():
    try:
        print(discord.callback())
    except AccessDenied:
        return redirect(url_for('index'), 303)
    return redirect(url_for('application'), 303)