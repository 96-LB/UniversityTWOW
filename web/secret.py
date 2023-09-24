import json, random, base64
import core.data as data
import web.classes as classes
import web.permissions as permissions
import bot.dm as dm
import bot.roles as roles
import bot.secret as secret
from core.web import app, discord
from flask import abort, request, render_template, redirect, url_for
from flask_discord import requires_authorization
from functools import wraps
from time import time

with open('secrets.json') as f:
    SECRETS = json.load(f)
ARG404 = classes.class_list['ARG404']

@app.route('/reset')
@permissions.requires_admin
def DELETE():
    print("resetting 96 LB's timers...")
    data.set("arg-timers", {}, user="236257776421175296")
    data.set("purgatory", {}, user="236257776421175296")
    
    print("building 31415926535897932...")
    data.set("application", {"accepted": True}, user="31415926535897932")
    data.set("classes", ["GEO013"], user="31415926535897932")
    data.set("students", ["31415926535897932"], user="GEO013")
    
    print("giving nerd judgement...")
    data.set("arg-judgement", {"complete": True}, user="210285266814894081")
    data.set("arg-judgement", {"complete": True}, user="212983348325384200")
    
    print("giving azu judgement...")
    data.set("arg-judgement", {"complete": True}, user="212805953630896128")
    data.set("application", {"accepted": True}, user="353356562615762946")
    data.set("classes", ["ARG404"], user="353356562615762946")
    data.set("arg-judgement", {"complete": True}, user="353356562615762946")
    
    data.set("application", {"accepted": True}, user="351093572931682304")
    data.set("classes", ["ARG404"], user="351093572931682304")
    
    
    print("giving h judgement...")
    data.set("arg-judgement", {"complete": True}, user="450096592582737920")
    data.set("application", {"accepted": True}, user="450096592582737920")
    data.set("classes", ["ARG404"], user="450096592582737920")
    data.set("arg-judgement", {"complete": True}, user="450096592582737920")
    
    return {'reset': True}

### secret ###

def secret_func(f):
    #defines a function from within the secrets
    @wraps(f)
    def decorator(**kwargs):
        loc = {'EXEC_INPUT': kwargs}
        exec(SECRETS['functions'][f.__name__], loc, loc)
        return loc.get('EXEC_OUTPUT')
    return decorator

@secret_func
def generate():
    pass

@secret_func
def verify(*, string):
    pass

@secret_func
def mfa():
    pass

### aux ###

def get_arg_name(name):
    return f'arg-{name}'

def get_arg_page(name):
    #gets the user's current page on a section of the arg
    return data.get(get_arg_name(name)).get('page')

def get_arg_progress(name):
    #gets the user's progress on a section of the arg
    progress = data.get(get_arg_name(name)).get('progress', -1)
    try:
        progress = int(progress)
    except:
        progress = -1
    return progress

def set_arg_progress(name, progress):
    #sets the user's progress on a section of the arg
    if get_arg_progress(name) <= progress:
        arg_name = get_arg_name(name)
        arg_data = data.get(arg_name)
        arg_data['progress'] = progress
        arg_data['page'] = request.path
        data.set(arg_name, arg_data)

def get_step(name, progress):
    #gets a deep copy of the specified arg step
    step = json.loads(json.dumps(SECRETS['branches'][name]['steps'][progress]))
    step.setdefault('name', name)
    step.setdefault('progress', progress)
    return step

def get_step_id(step):
    #encodes a step id by using the registered name and progress
    name = step['name']
    progress = step['progress']
    return f'{name}-{progress}'

def get_arg_id(step):
    #gets the user's arg id for a specific link, or generates a new one
    return data.get('arg-ids').get(get_step_id(step)) or generate()

def set_arg_id(step, arg_id):
    #sets the user's arg id for a specific link and adds it to the list of used ones
    owned = data.get('arg-ids')
    owned[get_step_id(step)] = arg_id
    data.set('arg-ids', owned)

    used = set(data.get('ids', user='ARG404') or [])
    used.add(arg_id)
    data.set('ids', list(used), user='ARG404')

def get_arg_timer(step):
    #gets the user's arg id for a specific step, or generates a new one
    return data.get('arg-timers').get(get_step_id(step), {
        'time': 0,
        'text': ''
    })

def set_arg_timer(step, seconds, text=''):
    #gets the user's arg timer for a specific step
    timers = data.get('arg-timers')
    timers[get_step_id(step)] = {
        'time': int(time()) + seconds,
        'text': text
    }
    data.set('arg-timers', timers)

def is_on_timer(step):
    #compares the timer's scheduled time to the current time
    return get_arg_timer(step)['time'] > time()

def is_complete(name):
    return bool(data.get(get_arg_name(name)).get('complete'))

def complete_arg(name):
    #sets a flag that indicates the branch as complete
    arg_name = get_arg_name(name)
    arg_data = data.get(arg_name)
    arg_data['complete'] = True
    data.set(arg_name, arg_data)

def alert(error):
    #don't call this function or you are in for a bad time
    message = f'⚠️ **ERROR:** {error} ⚠️\nUsername: {discord.fetch_user().username}\nID: {data.get_id()}\nPath: {request.path}'
    print(message)
    dm.dm(permissions.ADMIN, message)
    abort(404)                

def secret_page(step):
    return render_template('classes/class_page/secret_page.html', step=step)

def get_redirect(name, progress):
    #builds a redirect to the specified arg step
    step = get_step(name, progress)
    kwargs = {}
    if step.get('generated'):
        kwargs['arg_id'] = get_arg_id(step)
    name = name.replace('-', '_')
    return redirect(url_for(f'arg_{name}_{progress}', **kwargs), 303)

### decorators ###

def requires_arg(f):
    #ensures that the user is registered for ARG404 and is not in purgatory
    @wraps(f)
    @requires_authorization
    def decorator(*args, **kwargs):
        if 'ARG404' not in data.get('classes') and not classes.is_professor():
            abort(404)
        if classes.is_in_purgatory():
            return redirect(url_for('purgatory'))
        return f(*args, **kwargs)
    return decorator

def requires_arg_progress(name, progress):
    #ensures that the user has progressed far enough on a section of the arg
    def wrapper(f):
        @wraps(f)
        @requires_arg
        def decorator(*args, **kwargs):
            if get_arg_progress(name) < progress:
                alert('Early access')
            return f(*args, **kwargs)
        return decorator
    return wrapper

def verify_arg_id(step):
    #verifies that the route has a valid arg id, if required
    def wrapper(f):
        @wraps(f)
        def decorator(*args, arg_id=None, **kwargs):
            #skips validation if the step doesn't require it
            if step.get('generated'):
                #verifies the generated link
                step_id = get_step_id(step)
                owned = data.get('arg-ids')
                if step_id in owned:
                    if owned[step_id] != arg_id:
                        print(owned[step_id])
                        print(arg_id)
                        alert('Mismatched ID')
                elif arg_id in data.get('ids', user='ARG404'):
                    alert('Reused ID') 
                elif not verify(string=arg_id):
                    alert('Invalid ID')
                
                #updates the database
                set_arg_id(step, arg_id)

            return f(*args, **kwargs)
        return decorator
    return wrapper

def verify_arg_timer(step):
    #verifies that the user is not on cooldown for the route
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            timer = get_arg_timer(step)
            remaining = timer['time'] - time()
            if remaining > 0:
                timer = get_arg_timer(step)
                return render_template('timer.html', text=timer['text'], remaining=remaining)
            return f(*args, **kwargs)
        return decorator
    return wrapper

def requires_complete(*names):
    #requires that the given branches are complete
    def wrapper(f):
        @wraps(f)
        def decorator(*args, **kwargs):
            for name in names:
                if not is_complete(name):
                    alert('Early access 2')
            return f(*args, **kwargs)
        return decorator
    return wrapper

def arg_step(name, progress):
    #registers a route as a specific step on the arg
    def wrapper(f):
        #loads a deep copy of the arg step and sets the flask route
        step = get_step(name, progress)
        route = step['route']
        methods = [step.get('method', 'GET')]
        requisites = step.get('requisites', [])

        def set_progress():
            #sets the arg progress for the current step
            set_arg_progress(name, progress)
            if step.get('end'):
                complete_arg(name)

        @app.route(route, methods=methods)
        @wraps(f)
        @requires_complete(*requisites)
        @requires_arg_progress(name, progress - 1)
        @verify_arg_id(step)
        def decorator(*args, **kwargs):
            return {
                'GET': decorator_get,
                'POST': decorator_post
            }[request.method](*args, **kwargs)

        @verify_arg_timer(step)
        def decorator_get(*args, **kwargs):
            #only sets the arg progress if the function doesn't throw or abort
            out = f(*args, step=get_step(name, progress), **kwargs)
            set_progress()
            return out

        def decorator_post(*args, **kwargs):
            #only sets the arg progress if the provided answer matches and the timer isn't running
            timed = not is_on_timer(step)
            passed = timed and step.get('answer', '').lower().strip() == request.form.get('answer', '').lower().strip() 
            print(request.form.get('answer', ''))

            #pass passed and timed as a parameter to let the route differentiate what it does
            out = f(*args, step=get_step(name, progress), passed=passed, timed=timed, **kwargs)
            if passed:
                set_progress()
            elif timed:
                #if not on cooldown, start the cooldown
                timer = step.get('timer')
                if timer:
                    set_arg_timer(step, timer.get('time', 0), timer.get('text', ''))
            return out
            
        return decorator
    return wrapper

### routes ###

@app.route('/purgatory')
@app.route('/purgatory/<string:purgatory_id>')
@requires_authorization
def purgatory(purgatory_id=None):
    #the user must be in purgatory
    if not classes.is_in_purgatory():
        abort(404)
    purgatory_data = data.get('purgatory')

    if not purgatory_id or purgatory_id != purgatory_data['next']:
        #if the next link is not supplied, provide the letter
        return f'''
<p>
    {discord.fetch_user().username},
</p>
<p>
    I have taken it upon myself to erase you from my class database due to repeated transgressions against the rules I have laid out for you. Your disobedience is rampant and your loyalty is questionable at best. Perhaps my own training is at fault, so I have devised an...alternate lesson plan. You will be provided one hundred randomly generated codes and must visit each page manually; under no circumstances may you be readmitted to ARG404 until this assignment is completed. You may continue at <a href="https://universitytwow.cf/purgatory/{purgatory_data['next']}">https://universitytwow.cf/purgatory/{purgatory_data['next']}</a>.
</p>
<p>
    - Mr. E
</p>
'''
    else:
        #otherwise, decrease the count by one and generate a new link
        purgatory_data['count'] -= 1
        purgatory_data['next'] = str(random.randrange(0, 1000000000000))
        data.set('purgatory', purgatory_data)

        #checks whether the punishment is finished
        if purgatory_data['count'] == 0:
            if not classes.is_professor():
                #regrants access to ARG404 and provides another letter
                registration = data.get('classes')
                registration.append('ARG404')
                data.set('classes', registration)
                roles.add_roles('ARG404', user=data.get_id(), reason='completed purgatory')
            return f'''
<p>
    {discord.fetch_user().username},
</p>
<p>
    Your alternative assignment is complete. Do not ignore my warnings again, or you will not be given another chance.
</p>
<p>
    - Mr. E
</p>
'''
        else:
            return f'''
<p>
    Your next code is {purgatory_data['next']}.
</p>
'''

@app.route('/banish/<string:user>')
@permissions.requires_admin
def banish(user=None):
    #abstract banish so that the code can banish people too
    return banish_internal(user)

def banish_internal(user=None):
    if not classes.is_professor():
        #removes the student from ARG404
        registration = data.get('classes', user=user) or []
        registration.remove('ARG404')
        data.set('classes', registration, user=user)
        roles.remove_roles('ARG404', user=user, reason='banished')

    #puts the user in purgatory
    data.set('purgatory', {
        'count': 100,
        'next': str(random.randrange(0, 1000000000000))
    }, user=user)
    return {user: {'purgatory': data.get('purgatory', user=user), 'classes': data.get('classes', user=user)}}

### main ###

@app.route('/ARG404')
@requires_arg
@requires_complete('judgement')
def arg_main():
    #loads the main arg portal with the branch data encoded as a base-64 json
    branches = [{
        'link': get_arg_page(branch) or f'{request.path}/{index}',
        'completed': is_complete(branch)
    } for index, branch in enumerate(['lb', 'h', 'nerd', 'azu', 'dark'])]
    
    if all(branch['completed'] for branch in branches):
        branches.append({
            'link': url_for('fin'),
        })
    
    branches = json.dumps(branches)
    branches = base64.b64encode(branches.encode()).decode()
    return render_template('secret.html', branches=branches)

### tutorial ###

@arg_step('tutorial', 0)
def arg_tutorial_0(step):
    return secret_page(step)

@arg_step('tutorial', 1)
def arg_tutorial_1(step):
    return secret_page(step)

@arg_step('tutorial', 2)
def arg_tutorial_2(step):
    return secret_page(step)

@arg_step('tutorial', 3)
def arg_tutorial_3(step, passed, timed):
    if passed:
        return get_redirect('tutorial', 4)
    else:
        return get_redirect('tutorial', 2)

@arg_step('tutorial', 4)
def arg_tutorial_4(step):
    return secret_page(step)

@arg_step('tutorial', 5)
def arg_tutorial_5(step, passed, timed):
    if passed:
        banish_internal(data.get_id())
        return redirect(url_for('purgatory'), 303)
    else:
        complete_arg('tutorial')
        return get_redirect('tutorial', 4)

### judgement ###

@arg_step('judgement', 0)
def judgement(step):
    #determines whether the user is ready to continue to the arg
    if is_complete('tutorial'):
        step['end'] = True
        complete_arg('judgement')
    else:
        step['link']['text'] = 'You have not yet completed the two assignments which I have laid out for you. As such, I cannot trust you to continue forth with our sensitive operation. However, there is still time to amend this. Complete your assigned tasks and return to this page in order to be cleared for further progress in this class. That is all.'
    
    return secret_page(step)

### lb ###

@arg_step('lb', 0)
def arg_lb_0(step):
    return secret_page(step)

@arg_step('lb', 1)
def arg_lb_1(step, passed, timed):
    if passed:
        return get_redirect('lb', 2)
    else:
        return get_redirect('lb', 0)

@arg_step('lb', 2)
def arg_lb_2(step):
    return secret_page(step)

@arg_step('lb', 3)
def arg_lb_3(step):
    return secret_page(step)

@arg_step('lb', 4)
def arg_lb_4(step):
    return secret_page(step)

@arg_step('lb', 5)
def arg_lb_5(step, passed, timed):
    if passed:
        return get_redirect('lb', 6)
    else:
        return get_redirect('lb', 4)

@arg_step('lb', 6)
def arg_lb_6(step):
    return secret_page(step)

### h ###

@arg_step('h', 0)
def arg_h_0(step):
    return secret_page(step)

@arg_step('h', 1)
def arg_h_1(step):
    return secret_page(step)

@arg_step('h', 2)
def arg_h_2(step, passed, timed):
    if passed:
        return get_redirect('h', 3)
    else:
        return get_redirect('h', 1)

@arg_step('h', 3)
def arg_h_3(step):
    return secret_page(step)

@arg_step('h', 4)
def arg_h_4(step, passed, timed):
    if passed:
        return get_redirect('h', 5)
    else:
        return get_redirect('h', 3)

@arg_step('h', 5)
def arg_h_5(step):
    return secret_page(step)

@arg_step('h', 6)
def arg_h_6(step, passed, timed):
    if passed:
        return get_redirect('h', 7)
    else:
        return get_redirect('h', 5)

@arg_step('h', 7)
def arg_h_7(step):
    return secret_page(step)

@arg_step('h', 8)
def arg_h_8(step, passed, timed):
    if passed:
        return get_redirect('h', 9)
    else:
        return get_redirect('h', 7)

@arg_step('h', 9)
def arg_h_9(step):
    return secret_page(step)

@arg_step('h', 10)
def arg_h_10(step, passed, timed):
    if passed:
        return get_redirect('h', 11)
    else:
        return get_redirect('h', 9)

@arg_step('h', 11)
def arg_h_11(step):
    return secret_page(step)

@arg_step('h', 12)
def arg_h_12(step, passed, timed):
    if passed:
        return get_redirect('h', 13)
    else:
        return get_redirect('h', 11)

@arg_step('h', 13)
def arg_h_13(step):
    return secret_page(step)

@arg_step('h', 14)
def arg_h_14(step, passed, timed):
    if passed:
        return get_redirect('h', 15)
    else:
        return get_redirect('h', 13)

@arg_step('h', 15)
def arg_h_15(step):
    return secret_page(step)

@arg_step('h', 16)
def arg_h_16(step, passed, timed):
    if passed:
        return get_redirect('h', 17)
    else:
        return get_redirect('h', 15)

@arg_step('h', 17)
def arg_h_17(step):
    return secret_page(step)

### nerd ###

@arg_step('nerd', 0)
def arg_nerd_0(step):
    return secret_page(step)

@arg_step('nerd', 1)
def arg_nerd_1(step):
    return redirect(step['redirect'], 303)

@arg_step('nerd', 2)
def arg_nerd_2(step):
    return secret_page(step)

@arg_step('nerd', 3)
def arg_nerd_3(step, passed, timed):
    if passed:
        return get_redirect('nerd', 4)
    else:
        return get_redirect('nerd', 2)

@arg_step('nerd', 4)
def arg_nerd_4(step):
    return secret_page(step)

### azu ###

@arg_step('azu', 0)
def arg_azu_0(step):
    return secret_page(step)

@arg_step('azu', 1)
def arg_azu_1(step, passed, timed):
    if passed:
        return get_redirect('azu', 2)
    else:
        return get_redirect('azu', 0)

@arg_step('azu', 2)
def arg_azu_2(step):
    return secret_page(step)

@arg_step('azu', 3)
def arg_azu_3(step):
    return secret_page(step)

@arg_step('azu', 4)
def arg_azu_4(step):
    return secret_page(step)

@arg_step('azu', 5)
def arg_azu_5(step):
    return get_redirect('azu', 6)

@arg_step('azu', 6)
def arg_azu_6(step):
    return secret_page(step)

### dark ###

@arg_step('dark', 0)
def arg_dark_0(step):
    return secret_page(step)

@arg_step('dark', 1)
def arg_dark_1(step):
    return secret_page(step)

@arg_step('dark', 2)
def arg_dark_2(step, passed, timed):
    if passed:
        secret.reveal(step['channels'], step['role'])
        return get_redirect('dark', 3)
    else:
        return get_redirect('dark', 1)

@arg_step('dark', 3)
def arg_dark_3(step):
    return secret_page(step)

@arg_step('dark', 4)
def arg_dark_4(step):
    return secret_page(step)

@arg_step('dark', 5)
def arg_dark_5(step, passed, timed):
    if passed:
        #sets up multi-factor authentication
        msg, code = mfa()

        #sends the code
        phone_data = data.get('arg-dark-phone')
        recipient = phone_data.get('recipient')
        if recipient:
            dm.dm(recipient, msg)

        #updates the database
        name = get_arg_name(step['name'])
        arg_data = data.get(name)
        arg_data['mfa'] = {
            'code': code,
            'time': int(time()) + 900
        }
        data.set(name, arg_data)

        return get_redirect('dark', 6)
    else:
        return get_redirect('dark', 4)

@arg_step('dark', 6)
def arg_dark_6(step):
    return secret_page(step)

@arg_step('dark', 7)
def arg_dark_7(step, passed, timed):
    if passed:
        banish_internal(data.get_id())
        return redirect(url_for('purgatory'), 303)
    else:
        #calculates whether they passed manually
        mfa = data.get(get_arg_name(step['name'])).get('mfa', {})
        answer = request.form.get('answer')
        passed = timed and answer and answer.strip() == mfa.get('code') and time() < mfa.get('time', time() + 1)
        if passed:
            set_arg_progress('dark', 7)
            return get_redirect('dark', 8)
        elif timed:
            timer = step['timer-manual']
            set_arg_timer(step, timer['time'], timer['text'])
        return get_redirect('dark', 4)

@arg_step('dark', 8)
def arg_dark_8(step):
    return secret_page(step)

@arg_step('dark', 9)
def arg_dark_9(step, passed, timed):
    if passed:
        return get_redirect('dark', 10)
    else:
        return get_redirect('dark', 8)

@arg_step('dark', 10)
def arg_dark_10(step):
    return secret_page(step)

@arg_step('dark', 11)
def arg_dark_11(step, passed, timed):
    if passed:
        return get_redirect('dark', 12)
    else:
        return get_redirect('dark', 10)

@arg_step('dark', 12)
def arg_dark_12(step):
    return secret_page(step)

### dark-brb ###

@arg_step('dark-brb', 0)
def arg_dark_brb_0(step):
    return secret_page(step)

@arg_step('dark-brb', 1)
def arg_dark_brb_1(step, passed, timed):
    if passed:
        banish_internal(data.get_id())
        return redirect(url_for('purgatory'), 303)
    else:
        #calculates whether they passed manually
        name = get_arg_name(step['name'])
        arg_data = data.get(name)
        passed = timed and arg_data.get('brb')
        if passed:
            timer = step['timer-manual']
            set_arg_timer(step, timer['time'], timer['text'])
            set_arg_progress('dark-brb', 1)
            secret.reveal(step['channels'], step['role'])
            complete_arg('dark-brb')
        elif timed:
            timer = get_step('dark-brb', 0)['timer-manual']
            set_arg_timer(step, timer['time'], timer['text'])
            arg_data['brb'] = True
            data.set(name, arg_data)
        return get_redirect('dark-brb', 0)

### dark-phone

@arg_step('dark-phone', 0)
def arg_dark_phone_0(step):
    return secret_page(step)

@arg_step('dark-phone', 1)
def arg_dark_phone_1(step, passed, timed):
    recipient = request.form.get('answer')
    if recipient:
        #sends the captcha
        for message in step['messages']:
            dm.dm(recipient, message)
        
        #updates the database
        name = get_arg_name(step['name'])
        arg_data = data.get(name)
        arg_data['pending'] = recipient
        data.set(name, arg_data)
        set_arg_progress('dark-phone', 1)

        return get_redirect('dark-phone', 2)
    else:
        return get_redirect('dark-phone', 0)

@arg_step('dark-phone', 2)
def arg_dark_phone_2(step):
    return secret_page(step)

@arg_step('dark-phone', 3)
def arg_dark_phone_3(step, passed, timed):
    if passed:
        #updates the database
        name = get_arg_name(step['name'])
        arg_data = data.get(name)
        arg_data['recipient'] = arg_data.get('pending', '')
        data.set(name, arg_data)
        set_arg_progress('dark-phone', 3)

        return get_redirect('dark-phone', 4)
    else:
        return get_redirect('dark-phone', 2)

@arg_step('dark-phone', 4)
def arg_dark_phone_4(step):
    step.pop('end')
    return secret_page(step)

### dark-vault ###

@arg_step('dark-vault', 0)
def arg_dark_vault_0(step):
    return secret_page(step)

@arg_step('dark-vault', 1)
def arg_dark_vault_1(step, passed, timed):
    if passed:
        return get_redirect('dark-vault', 2)
    else:
        return get_redirect('dark-vault', 0)

@arg_step('dark-vault', 2)
def arg_dark_vault_2(step):
    step['link']['text'] = step['link']['text'].replace('§', '')
    step.pop('end')
    return secret_page(step)

### reward ###

@arg_step('fin', 0)
def fin(step):
    return redirect(step['redirect'], 303)
