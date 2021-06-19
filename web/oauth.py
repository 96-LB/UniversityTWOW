from core.web import app, discord
from flask import redirect, url_for
from flask_discord import Unauthorized

@app.errorhandler(Unauthorized)
def error_unauthorized(error):
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return discord.create_session(['identify'], prompt=False)

@app.route('/logout')
def logout():
    discord.revoke()
    return redirect(url_for('index'), 303)

@app.route('/callback')
def callback():
    discord.callback()
    return redirect(url_for('application'), 303)