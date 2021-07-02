import core.data as data
import core.bot as bot
from discord.errors import NotFound

ROLES = {
    'APPLICANT': 857972729093685248,
    'ENROLLED': 860135224184668161,
    'TWOW DESIGN': 860178085232115732,
    'SOCIOLOGY': 860178260411285524,
    'CULTURAL STUDIES': 860178332657123348,
    'VISUAL ARTS': 860178433962803241,
    'MATHEMATICS': 860178734131576862,
    'UNDECIDED': 860178980153983017,
    'BS003': 860179125078589471,
    'COLL101': 860179172176166952,
    'WLAN101': 860179394201780235,
    'MATH210': 860179449571835956,
    'HIST314': 860179602575982593,
    'MATH141': 860179680286736434,
    'TWOW101-1': 860179741913645096,
    'TWOW101-2': 860179794263277618,
    'ART110': 860180153232785450,
    'ARG404': 860180361022275616,
    'ART121': 860180564412989460
}

@bot.task
async def add_role(role, reason=None):
    try:
        member = await bot.guild.fetch_member(data.get_id())
        role = bot.guild.get_role(ROLES[role.upper()])
        await member.add_roles(role, reason=reason)
    except NotFound as error:
        print(f'ERROR: User {data.get_id()} not found.\n{error}')

@bot.task
async def remove_role(role, reason=None):
    try:
        member = await bot.guild.fetch_member(data.get_id())
        role = bot.guild.get_role(ROLES[role.upper()])
        await member.remove_roles(role, reason=reason)
    except NotFound as error:
        print(f'ERROR: User {data.get_id()} not found.\n{error}')