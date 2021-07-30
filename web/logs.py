import core.data as data
from core.web import app, discord
from web.permissions import requires_admin
from datetime import date, datetime
from flask import request
from time import time

PREFIX = '~zzz~logs-'

@app.before_request
def log_request():
    if not (request.method == 'HEAD' or request.path.startswith('/static') or request.path.startswith('/favicon')):
        #logs visits to each page
        user = discord.fetch_user().username if discord.authorized else '*'
        print(f'{user} visited {request.path} ({request.method})')
        
        #updates the database
        logs = data.get('logs', user=f'{PREFIX}{date.today()}') or []
        logs.append([int(time()), user, request.path, request.method])
        data.set('logs', logs, user=f'{PREFIX}{date.today()}')

@app.route('/logs')
@requires_admin
def get_logs():
    #gets the log entries from the database
    obj = {}
    keys = [key for key in data.keys() if key.startswith(PREFIX)]
    keys.sort()

    #iterates over all the dates to build a json object
    for key in keys:
        value = []
        logs = data.get('logs', user=key) or []
        
        #formats each log entry
        for log in logs:
            timestamp = datetime.utcfromtimestamp(log[0]).strftime("%Y-%m-%d %H:%M:%S")
            user, path, method = log[1:]
            value.append(f'{timestamp} :: {user} visited {path} ({method})')
        
        obj[key[len(PREFIX):]] = value

    return obj