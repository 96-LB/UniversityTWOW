import os
from base64 import b64encode
from flask import Flask
from flask_discord import DiscordOAuth2Session
from importlib import import_module
from threading import Thread

app = Flask('UniversityTWOW')
app.url_map.strict_slashes = False
app.config['SERVER_NAME'] = 'universitytwow.cf'
app.config['SECRET_KEY'] = b64encode(os.getenv('SECRET_KEY').encode('utf-8'))
app.config['PREFERRED_URL_SCHEME'] = 'https'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "true" #suppresses reverse-proxy http errors - proxy should already force https

for key in ['CLIENT_ID', 'CLIENT_SECRET', 'BOT_TOKEN', 'REDIRECT_URI']:
    key = 'DISCORD_' + key
    app.config[key] = os.environ[key]

discord = DiscordOAuth2Session(app)
app.jinja_env.globals['discord'] = discord

for file in os.listdir('web'):
    if file.endswith('.py'):
        import_module('web.' + file[:-3])

def run():
    thread = Thread(target=lambda: app.run('0.0.0.0'))
    thread.start()