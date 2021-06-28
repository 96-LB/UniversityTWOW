import os
import core.data as data
import bot.roles as roles
from flask import render_template, abort, request, redirect, url_for
from flask_discord import requires_authorization
from core.web import app
from functools import wraps
from web.override import is_admin

def is_page(page):
    try:
        page = int(page)
        return os.path.isfile(f'templates/application/{page}.html')
    except:
        return False

def application_in_progress(f):
    #redirects to the application page unless either of the conditions are met:
    #1. the user has started but not submitted an application
    #2. the user is an administrator
    @wraps(f)
    @requires_authorization
    def decorator(*args, **kwargs):
        app = data.get('application')
        if (not app.get('next_page') or app.get('submitted')) and not is_admin():
            return redirect(url_for('application'), 303)
        else:
            return f(*args, **kwargs)
    return decorator
    
###

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
        #submits the application
        data.set('application', {
            'submitted': True
        })
        roles.applied(data.get_id())
        return redirect(url_for('application'), 303)
    else:
        #starts the application
        data.set('application', {
            'next_page': 1
        })
        return redirect(url_for('application_page', page=1), 303)

###

@app.route('/application/<int:page>', methods=['GET', 'POST'])
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
    #stores the user's responses to the form, excluding the next field
    fields = request.form.to_dict(False)
    if 'next' in fields:
        next_ = fields.pop('next')[0]
    data.set(f'page{page}', fields)

    #adjusts the next page based on the value of the next field
    if next_:
        next_page = page
        if next_ == '►':
            next_page += 1
        if next_ == '◄':
            next_page -= 1
        if is_page(next_page):
            page = next_page

    #sets the application metadata - it is finished if there is no next page
    data.set('application', {
        'next_page': page,
        'finished': next_page > page
    })
    
    if page == next_page:
        return redirect(url_for('application_page', page=page), 303)
    else:
        return redirect(url_for('application'), 303)