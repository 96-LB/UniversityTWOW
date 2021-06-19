import os
import core.data as data
from flask import render_template, abort, request, redirect, url_for
from flask_discord import requires_authorization
from core.web import app

@app.route('/application')
@requires_authorization
def application():
    return ''

@app.route('/application/<page>', methods=['GET', 'POST'])
@requires_authorization
def application_page(page):
    return {
        'GET': application_page_get,
        'POST': application_page_post
    }[request.method](page)

def application_page_get(page):
    file = f'application/{page}.html'
    if not os.path.isfile('templates/' + file):
        abort(404)
    else:
        return render_template(file, data=data.get(f'page{page}'))

def application_page_post(page):
    fields = request.form.to_dict(False)
    if 'next' in fields:
        next_ = fields.pop('next')[0]
    data.set(f'page{page}', fields)

    if next_:
        try:
            page = int(page)
            if next_ == 'next':
                page += 1
            if next_ == 'back':
                page -= 1
        except:
            pass
    
    return redirect(url_for('application_page', page=page), 303)