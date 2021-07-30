import os, json
import core.data as data
import web.classes as classes
from flask import render_template, abort, request, redirect, url_for
from flask_discord import requires_authorization
from core.web import app
from functools import wraps
from web.permissions import is_admin
from time import time

### data ###

def get_page_data(test, page):
    #gets the submitted data for a specific page
    return (data.get('tests')
        .get(test['class']['id'], {})
        .get(test['id'], {})
        .get(f'page{page}', {}))

def set_page_data(test, page, page_data):
    #sets the submitted data for a specific page
    tests = data.get('tests')
    test_data = tests.setdefault(test['class']['id'], {}).setdefault(test['id'], {})
    test_data[f'page{page}'] = page_data
    return data.set('tests', tests)

def get_test_data(test):
    return get_page_data(test, '-test')

def set_test_data(test, test_data):
    return set_page_data(test, '-test', test_data)

###

def get_test(class_, test_id):
    #checks whether a setup file exists for the specified test and returns it if so
    try:
        class_id = class_['id']
        with open(f'templates/testing/{class_id}/{test_id}/test.json') as test_data:
            test = json.loads(test_data.read())
        test['class'] = class_
        test['id'] = test_id
        return test
    except:
        return None

def get_time_limit(test):
    #gets the time limit deadline for completing a test
    try:
        return int(test['time_limit'] + time())
    except Exception as e:
        print(e)
        return None

def time_remaining(test):
    #the time remaining on the user's test
    try:
        return int(get_test_data(test)['time'] - time())
    except Exception as e:
        print(e)
        return None

### checks ###

def is_page(test, page):
    #checks whether a file exists for the specified test page
    try:
        class_id = test['class']['id']
        test_id = test['id']
        page = int(page)
        return os.path.isfile(f'templates/testing/{class_id}/{test_id}/{page}.html')
    except:
        return False

def started_test(test):
    #whether the user has started the given test
    return bool(get_test_data(test).get('started'))

def submitted_test(test):
    #whether the user has submitted the given test
    return bool(get_test_data(test).get('submitted'))

def next_page(test):
    #the user's next page
    return get_test_data(test).get('next_page', 0)

### aux ###

def count_pages(test):
    page = 0
    while is_page(test, page + 1):
        page += 1
    return page

def start_test(test):
    #sets the user's deadline to the earliest of the hard deadline and the time limit
    deadline = test.get('deadline')
    time_limit = get_time_limit(test)
    print(deadline)
    print(time_limit)
    if deadline is None:
        deadline = time_limit
    elif time_limit is not None:
        deadline = min(deadline, time_limit)
    
    print({
        'started': True,
        'next_page': 1,
        'time': deadline
    })
    #starts the user's test
    return set_test_data(test, {
        'started': True,
        'next_page': 1,
        'time': deadline
    })

def set_next_page(test, page):
    test_data = get_test_data(test)
    test_data['next_page'] = page
    return set_test_data(test, test_data)

def submit_test(test):
    #submits the user's test
    return set_test_data(test, {
        'submitted': True
    })

### decorators ###

def requires_valid_test(f):
    #requires that the specified test id is valid and active
    @wraps(f)
    def decorator(*args, class_, test_id, **kwargs):
        test = get_test(class_, test_id)
        if not test or test.get('start', 0) > time():
            abort(404)
        return f(*args, test=test, **kwargs)
    return decorator

def requires_valid_page(f):
    #redirects to the main test page if the specified page is not valid
    @wraps(f)
    def decorator(*args, test, page, **kwargs):
        if not is_page(test, page):
            return redirect(url_for('test_main', class_id=test['class']['id'], test_id=test['id']), 303)
        return f(*args, test=test, page=page, **kwargs)
    return decorator

def requires_test_in_progress(f):
    #redirects to the main test page unless either of the conditions are met:
    #1. the user has started but not submitted an application
    #2. the user is an administrator
    @wraps(f)
    @requires_authorization
    def decorator(*args, test, **kwargs):
        if (not started_test(test) or submitted_test(test)): # TODO: and not is_admin():
            return redirect(url_for('test_main', class_id=test['class']['id'], test_id=test['id']), 303)
        else:
            #if there is no time left, submit the test before proceeding
            if time_remaining(test) < 0:
                submit_test(test)
            return f(*args, test=test, **kwargs)
    return decorator

def must_be_next_page(f):
    #redirects to the main test page unless either of the conditions are met:
    #1. this is the user's next page
    #2. the user is an administrator
    @wraps(f)
    @requires_authorization
    def decorator(*args, test, page, **kwargs):
        if get_test_data(test).get('next_page') != page: # TODO: and not is_admin():
            return redirect(url_for('test_main', class_id=test['class']['id'], test_id=test['id']), 303)
        else:
            return f(*args, test=test, page=page, **kwargs)
    return decorator

### routes ###

@app.route('/testing/<string:class_id>/<string:test_id>', methods=['GET', 'POST'])
@classes.requires_valid_class
@classes.requires_class_member
@requires_valid_test
def test_main(*, test):
    return {
        'GET': test_main_get,
        'POST': test_main_post
    }[request.method](test=test)

def test_main_get(*, test):
    return render_template('testing.html', test=test, test_data=get_test_data(test), time=time())

def test_main_post(*, test):
    #begins the test if not yet started
    if not started_test(test) or submitted_test(test):
        start_test(test)
    return redirect(url_for('test_page', class_id=test['class']['id'], test_id=test['id'], page=1), 303)

###

@app.route('/testing/<string:class_id>/<string:test_id>/<int:page>', methods=['GET', 'POST'])
@classes.requires_valid_class
@classes.requires_class_member
@requires_valid_test
@requires_test_in_progress
@requires_valid_page
@must_be_next_page
def test_page(*, test, page):
    return {
        'GET': test_page_get,
        'POST': test_page_post
    }[request.method](test=test, page=page)

def test_page_get(*, test, page):
    class_id = test['class']['id']
    test_id = test['id']
    return render_template(f'testing/{class_id}/{test_id}/{page}.html', data=get_page_data(test, page), test_data=get_test_data(test), count=count_pages(test), remaining=time_remaining(test))

def test_page_post(*, test, page):
    #stores the user's responses to the form, excluding the next field
    fields = request.form.to_dict(False)
    next_ = None
    if 'next' in fields:
        next_ = fields.pop('next')[0]
    set_page_data(test, page, fields)

    #adjusts the next page based on the value of the next field
    next_page = page
    if next_ == '►':
        next_page += 1
        #students can only go forwards -- if there are no more pages, submit the test
        if is_page(test, next_page):
            set_next_page(test, next_page)
        else:
            submit_test(test)
    if next_ == '◄':
        next_page -= 1

    return redirect(url_for('test_page', class_id=test['class']['id'], test_id=test['id'], page=next_page), 303)