import core.data as data
from core.bot import bot, task
from discord.errors import NotFound, Forbidden

@task
async def reveal(channel_ids, role_id):
    try:
        channels = [bot.get_channel(int(channel_id)) for channel_id in channel_ids]
        guild = channels[0].guild
        member = await guild.fetch_member(data.get_id())
        bember = await guild.fetch_member(bot.user.id)
        role = guild.get_role(int(role_id))

        #adds an editing role to self for an instant and modifies the chanenls      
        await bember.add_roles(role, reason='modifying permissions')
        for channel in channels:
            await channel.set_permissions(member, reason='revealed', read_messages=True)
        await bember.remove_roles(role, reason='done modifying permissions')
    except Exception as error:
        if isinstance(error, NotFound):
            print(f'ERROR: User {data.get_id()} not found.\n{error}')
        elif isinstance(error, Forbidden):
            print(f'ERROR: Cannot edit permissions for {channel_ids} or add {role_id}.\n{error}')
        else:
            raise error

### graduation

import asyncio, random, re
from functools import wraps
from time import time

import discord.app_commands as slash
from discord import ChannelType, Guild, Interaction, Member, Message, Object, Role, TextChannel, Webhook


tree = slash.CommandTree(bot)

webhook: Webhook = None

guild: Guild = Object(1121165553311154176) # hideout
utwow: Guild = Object(831515414022455336) # universitytwow
channel: TextChannel = Object(1155231933811404840) # graduation ceremony
cellar: TextChannel = Object(1138498458563641445) # wine cellar

roles: dict[str, Role] = {
    'ice': Object(1124423759147847811),
    'tenure': Object(831949263079604286),
    'undead': Object(1138511580594704385)
}
professors: dict[str, int] = {
    '96': 236257776421175296,
    'h': 450096592582737920,
    'chou': 210285266814894081,
    'biscuit': 212983348325384200,
    'az': 212805953630896128,
    'dark': 184768535107469314,
}
nicks: dict[int, str] = {
    236257776421175296: 'Dr. 69 LB',
    450096592582737920: 'Dr. H',
    210285266814894081: 'Prof. Cho',
    212983348325384200: 'Prof. Biscuit',
    212805953630896128: 'Dr. Ite',
    184768535107469314: 'Dr. Dark, PhD',
}
mre: int = 849279934987894805

commands = []

state = None
brb_points = None
cooldowns = None
async def init_state():
    global state, brb_points, cooldowns
    
    astroid_blacklist = ('admissions', 'staff', 'intro to collaborative efforts', 'alternate reality games')
    # astroid_blacklist += ('the history of twows, and why it\'s all bullshit', 'world language twowing', 'handwriting', 'calculus iii', 'statistics and modeling', 'hosting a good twow', 'the art of art') # TODO: remove this
    
    categories = [i for i in await utwow.fetch_channels() if i.type == ChannelType.category]
    for category in categories:
        if category.name.lower() not in astroid_blacklist:
            await category.set_permissions(utwow.default_role, send_messages=False)
    
    state = {
        'level': 0,
        'brb': 1,
        'brb_points': {},
        'evidence': 0,
        'sans': False,
        'undead': False,
        'blacklist': [],
        'thenamesi': False,
        'snare': [],
        'astroid': list(astroid_blacklist),
        'cooldowns': {},
    }

    brb_points = state['brb_points']
    cooldowns = state['cooldowns']
    
    await cellar.set_permissions(utwow.default_role, read_messages=False)
    await channel.set_permissions(utwow.default_role, send_messages=False) # todo: remove read_messages=False

    async for member in utwow.fetch_members():
        if roles['undead'] in member.roles:
            await member.remove_roles(roles['undead'], reason='Resetting state.')
    
    tree.clear_commands(guild=guild)
    for command in commands[0]:
        tree.add_command(command, guild=guild)
    await tree.sync(guild=guild)

### WEBHOOKS

async def send_sans(message):
    await webhook.send(message, username='sans', avatar_url='https://cdn.discordapp.com/attachments/1065676287798169620/1121187436500885595/sans.png')


async def send_mewtwo(message):
    await webhook.send(message, username='Mewtwo', avatar_url='https://cdn.discordapp.com/attachments/1065676287798169620/1124420513322766336/1ed5c5117cec1f095fb2ccd17bea064b.png')


async def send_thenamesi(message):
    await webhook.send(message, username='thenamesi', avatar_url='https://cdn.discordapp.com/attachments/1065676287798169620/1134130247076429834/thenamesh.png')

### DECORATORS

def wrap(level: int, cooldown: int, auth: bool = False, *, brb: bool = False):
    def decorator(f):
        
        @wraps(f)
        async def wrapper(interaction: Interaction, *args, **kwargs):
            if auth and interaction.user.id != 849279934987894805:
                await interaction.response.send_message('Only Mr. E is powerful enough to run this command.')
                return
            
            now = time()
            remaining = max(cooldowns.get(f.__name__, 0) - now, 0)
            if remaining:
                left = int(remaining) + 1
                message = (
                    f'The new button is currently being prepared! {left}s remain!'
                    if brb else
                    f'You must wait **{left}** second{"" if left == 1 else "s"} before using this command again.'
                )
                await interaction.response.send_message(message)
                return
            
            cooldowns[f.__name__] = now + cooldown
            
            return await f(interaction, *args, **kwargs)
        
        if auth:
            wrapper.__doc__ = '🔒 ' + (f.__doc__ or '')
        
        return wrapper
    return decorator


def command(level: int, cooldown: int, auth: bool = False):
    def decorator(f):
        for i in range(len(commands), level + 1):
            commands.append([])
        commands[level].append(slash.command()(wrap(level, cooldown, auth)(f)))
        return f
    return decorator


async def random_professor():
    members = [member async for member in utwow.fetch_members() if member.id in professors.values()]
    return random.choice(members)

### LEVEL 0 - MR. E

@command(0, 0, True)
async def reset(interaction: Interaction):
    '''Start everything over again'''

    await interaction.response.defer(thinking=True)
    await init_state()
    await interaction.followup.send('Reset state.')


@command(0, 0, True)
async def hack(interaction: Interaction, levels: int = 1):
    '''Hack into the UniversityTWOW mainframe'''

    for i in range(levels):
        state['level'] += 1
        new_commands = commands[state['level']] if state['level'] < len(commands) else []
        for command in new_commands:
            tree.add_command(command, guild=guild)
    
    await tree.sync(guild=guild)
    await interaction.response.send_message('Hacking successful. New commands are now available!')

### LEVEL 1 - BRB

brb_group = slash.Group(name='bigredbutton', description='Command for the Big Red Button game')

@brb_group.command()
async def press(interaction: Interaction):
    '''Press the Big Red Button'''

    if state['brb'] == -1:
        await interaction.response.send_message('The new button is being reconstructed. Infinitymin Infinitys remain!')
    elif state['level'] < 6:
        await press_normal(interaction)
    else:
        await press_kaboom(interaction)

@wrap(1, 18, brb=True)
async def press_normal(interaction: Interaction):
    brb = state['brb']
    user = interaction.user
    id = user.id
    
    points = 10 + round((0.75 + 0.5 * random.random()) * brb**1.25)
    brb_points.setdefault(id, 0)
    brb_points[id] += points
    state['brb'] += 1
    
    await interaction.response.send_message(f'**{user.name}** presses the button, and...')
    await asyncio.sleep(3)
    await interaction.channel.send(
        f'<:brb:1121198255615782973> The #{brb} Big Red Button did nothing.\n\n' +
        f'{user.mention} gained {points} points. Another button arrives in **15 seconds**.'
    )

async def press_kaboom(interaction: Interaction):
    message = (
        f'<:brb:1121198255615782973> ***The #{state["brb"]} Big Red Button blew up!***\n\n' +
        f'{interaction.user.mention} has been incapacitated. Their point total is now **{brb_points[interaction.user.id]}**.\n' +
        'They cannot press any more buttons for 6 hours.\n' +
        'The button is broken. It\'ll take forever to rebuild it.'
    )
    state['brb'] = -1
    await interaction.response.send_message(f'**{interaction.user.name}** presses the button, and...')
    await asyncio.sleep(3)
    
    await channel.send(message)
    await channel.set_permissions(utwow.default_role, send_messages=True) # todo: remove read_messages=False
    await interaction.channel.send(message)


@brb_group.command()
async def top(interaction: Interaction):
    '''See the Big Red Button leaderboard'''
    
    message = (
        '```diff\n' +
        '---⭐ Big Red Button Points Leaderboard Page 1 ⭐---\n' +
        '\n' +
        ' Rank |  Name                  |  Points\n'
    )
    
    points = sorted(brb_points.items(), key=lambda x: x[1], reverse=True)
    for i, person in enumerate(points):
        if i == 0: # + if the person is first
            line = f'+ {i + 1}{" " * (4 - len(str(i)))}|  '
        else: # - otherwise
            line = f'- {i + 1}{" " * (4 - len(str(i)))}|  '
        
        try: # Try to gather a username from the ID
            member = (await bot.fetch_user(int(person[0]))).display_name
        except Exception as e: # If you can't, just display the ID
            print(e)
            member = str(person[0])

        line += f'{member[:20]}{" " * (22 - len(member[:20]))}|  ' # Trim usernames to 20 characters long
        line += str(person[1]) + '\n' # Add points value and newline
    
        message += line # Add this line to the final message
    
    points.append((interaction.user.id, 0))
    
    for i in range(len(points) + 1):
        if points[i][0] == interaction.user.id:
            break
    
    message += f'\nYour rank is {i+1}, with {points[i][1]} points.```'
    
    await interaction.response.send_message(message)

### LEVEL 2 - AZURITE

@command(2, 99999)
async def wine(interaction: Interaction):
    '''Break into the fraudulent wine cellar'''
    
    await cellar.set_permissions(cellar.guild.default_role, read_messages=True)
    await interaction.response.send_message('Unlocked the cellar.')

@command(2, 120)
async def objection(interaction: Interaction):
    '''Become a true lawyer'''

    await channel.send('https://tenor.com/buTxo.gif')
    await interaction.response.send_message('Shouted "OBJECTION!" at the top of your lungs.')

@command(2, 180)
async def present(interaction: Interaction):
    '''Present a piece of devastating evidence'''
    
    evidences = (
        'https://cdn.discordapp.com/attachments/1065676287798169620/1138883031474655292/00044400154604_A1C1-1-2048x2048.png', # fish sticks
        'https://cdn.discordapp.com/attachments/1065676287798169620/1138889990470914068/note.png', # note
        'https://cdn.discordapp.com/attachments/1065676287798169620/1155235166386663564/convenient_tape_recorder.mp4', # recording
        'https://cdn.discordapp.com/attachments/1065676287798169620/1150524967033774122/gun.png' # gun
    )
    default = 'https://cdn.discordapp.com/attachments/1065676287798169620/1138886021946290306/latest.png' # badge
    
    await channel.send(evidences[state['evidence']] if state['evidence'] < len(evidences) else default)
    state['evidence'] += 1
    await interaction.response.send_message('Showed your evidence to the court.')

### LEVEL 3 - 96 LB

@command(3, 60)
async def lb(interaction: Interaction):
    '''Reveal the Dean's secret identity'''

    dean = await utwow.fetch_member(professors['96'])
    await dean.edit(nick='Dr. 96 LB')
    await interaction.response.send_message('Exposed the dean.')


@command(3, 120)
async def sans(interaction: Interaction):
    '''Summon the secret agent'''

    if not state['sans']:
        await interaction.response.send_message('Summoned sans.')
        await send_sans('hey guys')
        await asyncio.sleep(3)
        await send_sans('the air feels a bit dead in here')
        await asyncio.sleep(5)
        await send_sans('mind if i help lift the spirits?')
        state['sans'] = True
    else:
        messages = [
            'i hope youre finding my jokes humerus',
            r'\*drinks ketchup\*',
            'gettttttt dunked on!!!'
            '<https://www.youtube.com/watch?v=H01BwSD9eyQ>'
        ]
        await send_sans(random.choice(messages))
        await interaction.response.send_message('Asked sans to tell a joke.')

@command(3, 99999)
async def undead(interaction: Interaction):
    'Introduce a virus from another universe'
    
    state['undead'] = True
    await interaction.response.send_message('The end is nigh.')

### LEVEL 4 - BISCUITMISTRESS

@command(4, 99999)
async def ooc(interaction: Interaction):
    '''Break character'''
    
    await channel.send(r'\*SHATTER\*')
    await interaction.response.send_message('Shattered the fourth wall.')


@command(4, 240)
async def censor(interaction: Interaction, word: str):
    '''Enlist the CIA to censor any mention of a specific word'''

    word = ''.join(i.lower() for i in word if i.isalnum())
    state['blacklist'].append(word)
    await interaction.response.send_message(f'Added `{word}` to the blacklist.')


@command(4, 600)
async def reality(interaction: Interaction):
    '''Bend reality'''
    
    biscuit = await utwow.fetch_member(professors['biscuit'])
    await biscuit.kick(reason='Reality has been bent.')
    await interaction.response.send_message('Something changed...')

### LEVEL 5 - THENAMESH

@command(5, 120)
async def mewtwo(interaction: Interaction):
    '''Release the lab experiment'''
    
    professor = await random_professor()
    message = f'*Mewtwo used **Brain Blast** on {professor.mention}!*'
    if professor.id == professors['dark']:
        message += '\n\nIt\'s not very effective...'
    
    await send_mewtwo(message)
    await interaction.response.send_message('Unleashed Mewtwo.')


@command(5, 99999)
async def thenamesi(interaction: Interaction):
    '''Release the other lab experiment'''

    state['thenamesi'] = True
    await interaction.response.send_message('Unleashed thenamesi.')


@command(5, 180)
async def cryo(interaction: Interaction):
    '''Hijack the cryogenic rays'''
    
    professor = await random_professor()
    message = '`INCORRECT CODE. INTRUDER DETECTED. CRYOGENIC RAYS ACTIVATED.`'

    await professor.add_roles(roles['ice'], reason=message)
    await professor.remove_roles(roles['tenure'], reason=message)
    await channel.send(message)
    await interaction.response.send_message('Activated cryogenic rays.')

    await asyncio.sleep(60)
    
    melted = 'Melted.'
    await professor.add_roles(roles['tenure'], reason=melted)
    await professor.remove_roles(roles['ice'], reason=melted)

### LEVEL 6 - DARK

@command(6, 240)
async def snare(interaction: Interaction):
    '''Steal the evil mastermind's technology'''
    
    state['snare'] = list(professors.values())
    
    await channel.send('You notice a small lever hidden behind the podium. Type `!pull` to pull it.')
    await interaction.response.send_message('Planted snare trap.')
    await asyncio.sleep(15)

    members = [i async for i in utwow.fetch_members()]
    for professor in state['snare']:
        for member in members:
            if member.id == professor:
                await channel.send(f'A snare trap triggers and flings {member.mention} into the stratosphere!')
                await member.kick('Flung into stratosphere.')

@command(6, 120)
async def astroidinator(interaction: Interaction):
    '''Use a souvenir from the evil lair'''
    
    await channel.send('*The earth begins shaking...*')
    await interaction.response.send_message('Activated doomsday machine.')
    
    await asyncio.sleep(5)
    categories = [i for i in await utwow.fetch_channels() if i.type == ChannelType.category]
    categories = [i for i in categories if i.name.lower() not in state['astroid']]
    if categories:
        category = random.choice(categories)
        state['astroid'].append(category.name.lower())
        await channel.send(f'A giant asteroid crashes into **{category.name}** and obliterates it!')
        await category.set_permissions(utwow.default_role, read_messages=False)
    else:
        await channel.send('The earth stops shaking.')
    

### SETUP

async def verify_membership(member: Member):
    ban = member.id != mre and any(not data.get('arg-'+ name, user=str(member.id)).get('complete') for name in ('lb', 'h', 'nerd', 'azu', 'dark'))
    if ban:
        await member.kick(reason='Unauthorized access.')
    return ban    


commands[1].append(brb_group)

async def setup(bot):
    print('Syncing commands...')
    
    global cellar, channel, guild, roles, utwow, webhook
    guild = await bot.fetch_guild(guild.id) # hideout
    utwow = await bot.fetch_guild(utwow.id) # universitytwow
    channel = await bot.fetch_channel(channel.id) # graduation ceremony
    cellar = await bot.fetch_channel(cellar.id) # wine cellar
    webhook = (await channel.webhooks())[0] # webhook
    roles = {name: utwow.get_role(obj.id) for name, obj in roles.items()}
    
    await init_state()

    @bot.event
    async def on_member_join(member: Member):
        if member.guild == guild:
            await verify_membership(member)
        elif member.guild == utwow:
            if member.id in professors.values(): 
                await member.edit(nick=nicks[member.id], roles=[roles['tenure']], reason='They have tenure, unfortunately.')
            elif data.get('application', user=str(member.id)).get('accepted'):
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

                major = data.get('page5', user=str(member.id)).get('major', ['Undecided'])[0]
                
                new_roles = data.get('classes', user=str(member.id)) or []
                new_roles += ['ENROLLED', major]
                new_roles = [utwow.get_role(ROLES[role.upper()]) for role in new_roles]
                
                await member.add_roles(*new_roles, reason='student')
    
    @bot.event
    async def on_message(message: Message):
        if message.channel != channel:
            if message.guild == guild and message.author.id != bot.user.id:
                await verify_membership(message.author)
            return

        if message.author.id in [854858671010611210, 1121184332615266406]:
            return
        
        if state['sans']:
            if re.search(r'\bton\b', message.content, re.IGNORECASE):
                await send_sans('a skele-ton')
            if re.search(r'\btrombone\b', message.content, re.IGNORECASE):
                await send_sans('trom-bone')
            if re.search(r'\bfunny\b', message.content, re.IGNORECASE):
                await send_sans('funny? more like humerus')
            if re.search(r'\bhumorous\b', message.content, re.IGNORECASE):
                await send_sans('humerous? more like humerus')
        
        if state['thenamesi']:
            if message.author.id == professors['h']:
                await send_thenamesi(message.content)

        if message.author.id in state['snare'] and '!pull' in message.content:
            state['snare'].remove(message.author.id)
        
        words = message.content.lower().split()
        words = [''.join(i for i in word if i.isalnum()) for word in words]
        words = [word for word in words if word]
        for word in state['blacklist']:
            if word in words:
                await message.delete()
        
        if state['undead']:
            if random.random() < .05:
                if roles['undead'] not in message.author.roles:
                    member = message.author
                else:
                    member = random.choice([i async for i in utwow.fetch_members()])
                await member.add_roles(roles['undead'], reason=f'Infected by {message.author.name}.')
