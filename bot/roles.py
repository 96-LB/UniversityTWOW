from discord.errors import NotFound
import core.bot as bot

ROLE_APPLIED = 857972729093685248

@bot.task
async def applied(user):
    try:
        member = await bot.guild.fetch_member(user)
        role = bot.guild.get_role(ROLE_APPLIED)
        await member.add_roles(role, reason="submitted application")
    except NotFound as e:
        print(f'ERROR: User {user} not found.\n{e}')