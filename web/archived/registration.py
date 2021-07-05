import core.data as data
from core.web import app
from web.application import requires_accepted
from web.classes import class_list
from flask import request, render_template, redirect, url_for

@app.route('/register', methods=['GET', 'POST'])
@requires_accepted
def register():
    return {
        'GET': register_get,
        'POST': register_post
    }[request.method]()

def register_get():
    return render_template('register.html', class_list=class_list, classes=data.get('classes'))

def register_post():
    #stores a list of unique classes and removes TWOW101 double sections
    classes = list(set(request.form.getlist('classes')))
    if 'TWOW101-1' in classes and 'TWOW101-2' in classes:
        classes.remove('TWOW101-2')
    data.set('classes', classes)
    return redirect(url_for('register'), 303)