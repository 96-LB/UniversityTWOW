from core.bot import bot, task
from discord.errors import NotFound, Forbidden

@task
async def dm(user, message):
    try:
        print(f"trying to dm {user}")
        recipient = await bot.fetch_user(user)
        print(f"identified recipient {recipient} ({user})")
        channel = recipient.dm_channel or await recipient.create_dm()
        print(f"got channel {channel} ({user})")
        await channel.send(message)
        print(f"successfully notified {user}")
    except Exception as error:
        if isinstance(error, NotFound):
            print(f'ERROR: User {user} not found.\n{error}')
        elif isinstance(error, Forbidden):
            print(f'ERROR: Cannot send direct message to user {user}.\n{error}')
        else:
            raise error