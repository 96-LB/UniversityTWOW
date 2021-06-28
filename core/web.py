import os
from base64 import b64encode
from flask import Flask
from flask_discord import DiscordOAuth2Session
from importlib import import_module
from threading import Thread

#sets up a flask application
app = Flask('UniversityTWOW')
app.url_map.strict_slashes = False
app.config['SERVER_NAME'] = 'universitytwow.cf'
app.config['SECRET_KEY'] = b64encode(os.getenv('SECRET_KEY').encode('utf-8'))
app.config['PREFERRED_URL_SCHEME'] = 'https'
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = 'true' #suppresses reverse-proxy http errors - proxy should already force https

#loads in discord environment variables
for key in ['CLIENT_ID', 'CLIENT_SECRET', 'REDIRECT_URI', 'BOT_TOKEN']:
    key = 'DISCORD_' + key
    app.config[key] = os.environ[key]

#start a discord oauth application
discord = DiscordOAuth2Session(app)
app.jinja_env.globals['discord'] = discord

#loads each module in the web folder
for file in os.listdir('web'):
    if file.endswith('.py'):
        import_module('web.' + file[:-3])

def run():
    #runs the webserver in a separate thread
    thread = Thread(target=lambda: app.run('0.0.0.0'))
    thread.start()