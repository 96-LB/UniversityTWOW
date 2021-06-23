import core.data as data
from core.web import app, discord
from time import time
from flask import request

@app.before_request
def log():
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