import os
import core.data as data
from core.web import app, discord
from flask_discord import requires_authorization
from flask import request, render_template, abort

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text', methods=['POST'])
@requires_authorization
def text():
    data.set('dev', request.form.to_dict)
    return "data successfully saved."