import core.data as data
from core.web import app, discord
from time import time
from flask import request

@app.before_request
def log():
    if not (request.method == 'HEAD' or request.path.startswith('/static') or request.path.startswith('/favicon')):
        user = discord.fetch_user().username if discord.authorized else '*'
        print(f'{user} visited {request.path} ({request.method})')
    if discord.authorized and request.url_rule:
        endpoint = request.url_rule.endpoint
        if endpoint not in ['static', 'favicon', 'callback']:
            #logs visits to each page
            logs = data.get('logs') or []
            logs.append({
                'time': time(),
                'page': endpoint
            })
            data.set('logs', logs)