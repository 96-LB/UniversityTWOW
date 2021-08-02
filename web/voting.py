import os, json
import core.data as data
from core.web import app, discord
from web.permissions import requires_admin
from datetime import datetime
from flask import render_template, request, redirect, url_for
from flask_discord import requires_authorization
from replit import db
from time import time

#builds the voting data
response_list = '''
you write N responses (1 <= N <= 5), your score is the sum of all scores minus 50*(N-1)
You gain 5% in score but 96 LB will run a bot that pings you every 5 minutes and gives a random fake deadline.
Gain 0.1% boost for every e in your response.
10% boost but if you don't supervote you get banned from the server
See the prompt before everyone else. You are able to censor a word from it from the other contestants.
Gives you a ballpeen hammer (free) from Roguelike TWOW.
allows you to see 3 example responses for a given prompt
Stack a +2.37% boost for every pair of consecutive double letters you have in your response.  Now you can just spam piss piss piss piss piss piss p
For every Z you use, you gain +1% strength; 5% maximum strength. In addition, voting your response last will grant you +7.5% luck.
Multiply your other boosts’ values, then add to your score.
it replaces a chosen twist with amogus TWOW (everything becomes among us reference)
Reap the effects of every item that any contestant holds (excluding this item), but instantly die if you don't win the round by 10%.
Add a "CANCELLED" banner atop the booksona of all submitters that couldn't place above you.
Gives you a custom role on the 69TWOW server.
Gain a 20% score boost by not repeating the same letter in 2 consecutive words.
Gives you three other items at random.
During voting, choose a response that doesn't belong to you. You earn a boost equal to that response's boost, minus 10%.
Accumulate a stacking 2.5% boost for every round you and your target place within 20% of the leaderboard of each other. Receive a 20% penalty when you don't.
Choose a contestant during responding. Their response will be encoded by cipher (Vigenère with key "UIRQEXCBHUSFOXWML").
Maybe an item which added random words to the end of your response and gave 10% boost
It alerts you if your response is currently sandblasted!
'''.split('\n')[1:-1]

response_list = {chr(ord('A') + i): response_list[i] for i in range(len(response_list))}

character_counts = json.loads(os.environ['VOTING_CHARACTERS'])

@app.route('/voting', methods=['GET', 'POST'])
@requires_authorization
def voting():
    return {
        'GET': voting_get,
        'POST': voting_post
    }[request.method]()

def voting_get():
    #reads prior vote data to fill in the voting screen
    vote_data = data.get('vote')
    vote = vote_data.get('vote', [])
    vote_letters = [response['letter'] for response in vote]
    responses = vote + [{
        'letter': letter,
        'response': response,
        'name': ''
    } for letter, response in response_list.items() if letter not in vote_letters]
    characters = character_counts.get(data.get_id(), 100)

    return render_template('voting.html', responses=responses, characters=characters)

def voting_post():
    #initializes and grabs the submitted vote
    fields = request.form.to_dict(False)
    characters = character_counts.get(data.get_id(), 100)
    vote = []

    #iterates over the list of response orderings and names
    letters = fields.get('letter', [])
    names = fields.get('name', [])
    for i in range(min(len(letters), len(names))):
        #the name is truncated if they run out of characters
        letter = letters[i]
        name = names[i][:characters]

        #builds a response object and subtracts the characters
        if letter in response_list:
            vote.append({
                'letter': letter,
                'response': response_list[letter],
                'name': name
            })
            characters -= len(name)

    #updates the database
    data.set('vote', {
        'characters': characters,
        'vote': vote
    })
    
    return redirect(url_for('voting'), 303)

###

@app.route('/voting/logs', methods=['GET', 'POST'])
@requires_authorization
def voting_log():
    return {
        'GET': voting_log_get,
        'POST': voting_log_post
    }[request.method]()

@requires_admin
def voting_log_get():
    #gets the log entries from the database
    obj = {}
    logs = db.get('~zzz~logs-voting')

    #iterates over all the ids to build a json object
    for key in logs:
        value = []

        #formats each log entry
        for log in logs[key]:
            timestamp = datetime.utcfromtimestamp(log[0]).strftime("%Y-%m-%d %H:%M:%S")
            user, action, response, info = log[1:]
            value.append(f'{timestamp} :: {user} performed {action} on {response} ({info})')
        
        obj[key] = value

    return obj

def voting_log_post():
    #updates the database
    json = request.get_json()
    logs = data.get(data.get_id(), user='~zzz~logs-voting') or []
    logs.append([int(time()), discord.fetch_user().username, json.get('action'), json.get('response'), json.get('info')])
    data.set(data.get_id(), logs, user='~zzz~logs-voting')
    return {'logs': logs}