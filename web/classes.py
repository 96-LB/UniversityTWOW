import core.data as data
from core.web import app, discord, jinja_env
from web.permissions import requires_admin
from web.application import accepted
from flask import render_template, abort
from flask_discord import requires_authorization
from functools import wraps

department_list = {
    'TWOW Design': {
        'name': 'TWOW Design'
    },
    'Sociology': {
        'name': 'Sociology'
    },
    'Cultural Studies': {
        'name': 'Cultural Studies'
    },
    'Visual Arts': {
        'name': 'Visual Arts'
    },
    'Mathematics': {
        'name': 'Mathematics'
    }
}

professor_list = {
    '212983348325384200': {
        'id': '212983348325384200',
        'name': 'Prof. Biscuit'
    },
    '212805953630896128': {
        'id': '212805953630896128',
        'name': 'Dr. Azurite'
    },
    '184768535107469314': {
        'id': '184768535107469314',
        'name': 'Dr. Dark'
    },
    '450096592582737920': {
        'id': '450096592582737920',
        'name': 'Dr. H'
    },
    '236257776421175296': {
        'id': '236257776421175296',
        'name': 'Dr. LB'
    },
    '849279934987894805': {
        'id': '849279934987894805',
        'name': 'Mr. E'
    }
}

class_list = {
    'BS003': {
        'id': 'BS003',
        'title': 'The Bachelor\'s of Art of Bachelor\'s of Science',
        'department': department_list['TWOW Design']['name'],
        'professor': professor_list['212983348325384200']['id'],
        'professor_name': professor_list['212983348325384200']['name'],
        'ta': None,
        'description': 'NOTE TO SELF: Replace this with some pretentious, academic-sounding explantion of just fucking winging it on the fly. I\'d say I couldn\'t believe that the dean\'s letting me get away with this, but I guess that\'s what a tenure\'s for.'
    },
    'COLL101': {
        'id': 'COLL101',
        'title': 'Intro to Collaborative Efforts',
        'department': department_list['Sociology']['name'],
        'professor': professor_list['212805953630896128']['id'],
        'professor_name': professor_list['212805953630896128']['name'],
        'ta': professor_list['236257776421175296']['id'],
        'description': 'Let\'s all hold hands (or bump elbows, haha) and get along! This class helps us have epic gamer friendships and develop bonds in a place befuddled by those dang computers.'
    },
    'WLAN101': {
        'id': 'WLAN101',
        'title': 'World Language TWOWing',
        'department': department_list['Cultural Studies']['name'],
        'professor': professor_list['184768535107469314']['id'],
        'professor_name': professor_list['184768535107469314']['name'],
        'ta': professor_list['450096592582737920']['id'],
        'description': 'A practical and culture-oriented class on TWOWing in another language - useful for whenever the English speaking world gets inevitably and brutally taken over by a non-specific Romance-language-speaking foreign power!'
    },
    'ART110': {
        'id': 'ART110',
        'title': 'Handwriting',
        'department': department_list['Visual Arts']['name'],
        'professor': professor_list['184768535107469314']['id'],
        'ta': None,
        'description': 'A practical and culture-oriented class on TWOWing in manual handwriting - useful for whenever all computers get strategically destroyed by a non-specific despotic anti-information authoritarian regime led by a Romance-language-speaking foreign power!'
    },
    'MATH210': {
        'id': 'MATH210',
        'title': 'Calculus III',
        'department': department_list['Mathematics']['name'],
        'professor': professor_list['450096592582737920']['id'],
        'professor_name': professor_list['450096592582737920']['name'],
        'ta': None,
        'description': 'Here you\'ll learn about differentiation and integration in multiple dimensions!'
    },
    'HIST314': {
        'id': 'HIST314',
        'title': 'TWOW History',
        'department': department_list['Cultural Studies']['name'],
        'professor': professor_list['212983348325384200']['id'],
        'professor_name': professor_list['212983348325384200']['name'],
        'ta': None,
        'description': '"An interdisciplinary overview of the greater historical trends over the past five years. Examination of important figures and innovations through cultural, mathematical, and interpersonal lenses."<br><br>"...did you get all that? Yeah, alright. I don\'t get why I\'m teaching this course if I\'m around for half of the curriculum. This is fucking stupid."'
    },
    'MATH141': {
        'id': 'MATH141',
        'title': 'Statistics and Modeling',
        'department': department_list['Mathematics']['name'],
        'professor': professor_list['236257776421175296']['id'],
        'professor_name': professor_list['236257776421175296']['name'],
        'ta': None,
        'description': 'Basic survey of statistics modeling techniques such as Gaussian distributions and inter-TWOW ranking systems and their applications. Qualitative analysis of strengths and weaknesses of various models.'
    },
    'TWOW101-1': {
        'id': 'TWOW101-1',
        'title': 'Hosting a Good TWOW',
        'department': department_list['TWOW Design']['name'],
        'professor': professor_list['450096592582737920']['id'],
        'professor_name': professor_list['450096592582737920']['name'],
        'ta': None,
        'description': 'A project-oriented class that covers all aspects of creating a TWOW; this includes good prompts, good aesthetics, good presentation and even good twists. Also covers how to avoid bad prompts, bad aesthetics, bad presentation and bad twists.'
    },
    'TWOW101-2': {
        'id': 'TWOW101-2',
        'title': 'Hosting a Good TWOW',
        'department': department_list['TWOW Design']['name'],
        'professor': professor_list['236257776421175296']['id'],
        'professor_name': professor_list['236257776421175296']['name'],
        'ta': None,
        'description': '<i>[NOTE: Due to popular demand, two sections have been opened for this course. You may not sign up for both TWOW101-1 and TWOW101-2.]</i>'
    },
    'ARG404': {
        'id': 'ARG404',
        'title': 'Alternate Reality Games',
        'department': department_list['Sociology']['name'],
        'professor': professor_list['849279934987894805']['id'],
        'professor_name': professor_list['849279934987894805']['name'],
        'ta': professor_list['236257776421175296']['id'],
        'description': '&nbsp;'
    },
    'ART121': {
        'id': 'ART121',
        'title': 'The Art of Art',
        'department': department_list['Visual Arts']['name'],
        'professor': professor_list['212805953630896128']['id'],
        'professor_name': professor_list['212805953630896128']['name'],
        'ta': None,
        'description': 'DRAW. CREATE. LIBERATE.'
    }
}

@jinja_env
def is_professor():
    return discord.authorized and data.get_id() in professor_list

def teaches_class(class_id):
    return is_professor() and class_id in class_list and data.get_id() in (class_list[class_id]['professor'], class_list[class_id]['ta'])

def enrolled_in(class_id):
    return discord.authorized and class_id in class_list and class_id in data.get('classes')

def student_or_professor(f):
    #checks whether the user is an accepted student or a professor
    @wraps(f)
    @requires_authorization
    def decorator(*args, **kwargs):
        return f(*args, **kwargs) if is_professor() else accepted(f)(*args, **kwargs)
    return decorator

def is_class_member(f):
    #checks whether a student is enrolled in or a professor is teaching a class
    @wraps(f)
    @student_or_professor
    def decorator(*args, class_id, **kwargs):
        if class_id not in class_list:
            abort(404)
        if not enrolled_in(class_id) and not teaches_class(class_id):
            abort(403)
        return f(*args, class_id=class_id, **kwargs)
    return decorator

def find_link(link_id, links):
    for link in links:
        if 'id' not in links:
            continue
        if link['id'] == link_id:
            return link
        if isinstance(links['id'], list):
            link = find_link(link_id, link)
            if link:
                return link
    return None

@app.route('/classes')
@student_or_professor
@requires_admin
def classes():
    classes = [class_id for class_id in class_list if teaches_class(class_id)] if is_professor() else data.get('classes')
    return render_template('classes.html', class_list=class_list, classes=classes)

@app.route('/classes/<string:class_id>')
@is_class_member
@requires_admin
def class_page(*, class_id):
    links = data.get('links', user=class_id)
    return render_template('class_page.html', links=links, **class_list[class_id])

@app.route('/classes/<string:class_id>/<int:link_id>')
@is_class_member
@requires_admin
def link_page(*, class_id, link_id):
    links = data.get('links', user=class_id)
    link = find_link(link_id, links)
    if not link:
        abort(404)
    return render_template('link_page.html', class_id=class_id, **link)