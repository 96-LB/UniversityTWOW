import os
import core.data as data
from flask import render_template, abort, request, redirect, url_for
from flask_discord import requires_authorization
from core.web import app
from functools import wraps

def is_page(page):
    try:
        page = int(page)
        return os.path.isfile(f'templates/application/{page}.html')
    except:
        return False

def application_in_progress(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        application = data.get('application')
        if not application.get('next_page') or application.get('submitted'):
            return redirect(url_for('application'), 303)
        else:
            return f(*args, **kwargs)
    return decorator
    

@app.route('/application', methods=['GET', 'POST'])
@requires_authorization
def application():
    return {
        'GET': application_get,
        'POST': application_post
    }[request.method]()

def application_get():
    return render_template('application.html', **data.get('application'))

def application_post():
    application = data.get('application')
    
    if application.get('next_page'):
        data.set('application', {
            'submitted': True
        })
        return redirect(url_for('application'), 303)
    else:
        data.set('application', {
            'next_page': 1
        })
        return redirect(url_for('application_page', page=1), 303)

@app.route('/application/<int:page>', methods=['GET', 'POST'])
@requires_authorization
@application_in_progress
def application_page(page):
    if not is_page(page):
        abort(404)

    return {
        'GET': application_page_get,
        'POST': application_page_post
    }[request.method](page)

def application_page_get(page):
    return render_template(f'application/{page}.html', data=data.get(f'page{page}'))

def application_page_post(page):
    fields = request.form.to_dict(False)
    if 'next' in fields:
        next_ = fields.pop('next')[0]
    data.set(f'page{page}', fields)

    if next_:
        next_page = page
        if next_ == 'next':
            next_page += 1
        if next_ == 'back':
            next_page -= 1
        if is_page(next_page):
            page = next_page

    data.set('application', {
        'next_page': page,
        'finished': next_page > page
    })
    
    if page == next_page:
        return redirect(url_for('application_page', page=page), 303)
    else:
        return redirect(url_for('application'), 303)