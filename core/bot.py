import discord, os, asyncio
from threading import Thread
from functools import wraps

bot = discord.Client()

guild = None
loop = asyncio.get_event_loop()

def task(f):
    #turns an asynchronous coroutine function into a task
    @wraps(f)
    def decorator(*args, **kwargs):
        return loop.create_task(f(*args, **kwargs))
    return decorator

@bot.event
async def on_ready():
    global guild
    guild = bot.get_guild(831515414022455336) # UniversityTWOW
    await bot.change_presence(activity=discord.Game(name='https://universitytwow.cf'))
    print('Headmaster bot is running!')

import bot.secret as _
def run():
    #runs the bot in a separate thread
    thread = Thread(target=lambda: bot.run(os.environ['BOT_TOKEN']))
    thread.run()