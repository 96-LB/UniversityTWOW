import discord, os, asyncio
from threading import Thread
from functools import wraps

intents = discord.Intents().default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = discord.Client(intents=intents)

guild = None

def task(f):
    #turns an asynchronous coroutine function into a task
    @wraps(f)
    def decorator(*args, **kwargs):
        return asyncio.run_coroutine_threadsafe(f(*args, **kwargs), bot.loop).result()
    return decorator

import bot.secret as secret

@bot.event
async def on_ready():
    global guild
    guild = bot.get_guild(831515414022455336) # UniversityTWOW
    
    await secret.setup(bot)
    await bot.change_presence(activity=discord.Game(name='https://universitytwow.cf'))
    
    print('Headmaster bot is running!')

def run():
    #runs the bot in a separate thread
    thread = Thread(target=lambda: bot.run(os.environ['BOT_TOKEN']))
    thread.run()