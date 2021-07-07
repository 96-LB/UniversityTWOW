import core.data as data
import bot.roles as roles
from core.web import app
from web.application import requires_accepted
from web.classes import class_list
from web.permissions import requires_admin
from flask import request, render_template, redirect, url_for
from replit import db

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

@app.route('/register/update')
@requires_admin
def update():
    classes = {class_id: [] for class_id in class_list}
    students = {}
    for user in db.keys():
        #checks if each user is accepted and has registred for classes
        app = data.get('application', user=user)
        registration = data.get('classes', user=user)
        if app.get('accepted') and registration:
            #adds roles and updates the class list of studnts
            roles.add_roles(*registration, user=user, reason='registered for class')
            for class_id in registration:
                classes[class_id].append(user)
            students[user] = registration
    
    #updates the database with each classes's list
    for class_id, student_list in classes.items():
        data.set('students', student_list, user=class_id)
    
    return {'classes': classes, 'students': students}