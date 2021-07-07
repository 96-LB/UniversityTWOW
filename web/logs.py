import core.data as data
from core.web import app, discord
from datetime import date
from time import time
from flask import request

@app.before_request
def log():
    if not (request.method == 'HEAD' or request.path.startswith('/static') or request.path.startswith('/favicon')):
        #logs visits to each page
        user = discord.fetch_user().username if discord.authorized else '*'
        print(f'{user} visited {request.path} ({request.method})')
        
        #updates the database
        logs = data.get('logs', user=f'~zzz~logs-{date.today()}') or []
        logs.append([time(), user, request.path, request.method])
        data.set('logs', logs, user=f'~zzz~logs-{date.today()}')