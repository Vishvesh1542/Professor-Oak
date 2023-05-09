import interactions
import raids
import json
import raids_data 
import name_pokemon
import time
import os


raid_class = raids_data.Raid()

class Scope:
    RESTRICTED = 1
    DETAILED = 2
    SPAWNPOKEMON = 3
    RAIDPOKEMON = 4


class AsyncList:
    def __init__(self, lst=list()):
        self.lst = lst
        self.i = 0

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.i >= len(self.lst):
            raise StopAsyncIteration
        item = self.lst[self.i]
        self.i += 1
        return item


def init_files() -> None:
    global raid_pokemon, pokemon_list
    with open(os.getcwd() + '/data/pokemon_list') as file:
        pokemon_list = json.load(file)

    with open(os.getcwd() + '/data/raid_pokemon') as file:
        raid_pokemon = eval(file.read())

    print('(re)loaded common files ')


def send_guilds(ctx, bot) -> interactions.Embed:
    embed = interactions.Embed(title='Error')
    guilds = bot.guilds
    embed.title = f'Professor Oak is currently in {len(guilds)} servers!'

    if int(ctx.user.id) == 886873187965616158:
        for guild in guilds:
            embed.add_field(name=str(guild.name), value='')

    return embed


def raid_help() -> interactions.Embed:
    embed = interactions.Embed(title='How to use the raid commands?')
    embed.color = 0xC8A2C8

    embed.description = '\
    Professor Oak has a lot of experience with doing raids so he can \n\
    instantly tell which Pokémon is a counter for any given Pokémon. \n\
    He also conveniently gives score to Pokémon to better select pokemon\n\n\
    Here are a few commands to get started: \n\n\n'

    embed.add_field(name='/raid meta {pokemon}',
                    value='Professor Oak compares some of \
                          the best pokemon and tells which is most effective.')

    embed.add_field(name='/raid search {args}',
                    value="Globals and don't have any raids? No problem! search for raids across servers and join them if u like!")
    
    embed.add_field(name='/raid server_join {id}',
                    value="Found a raid but are not in the server? Just type the id of the raid and join the server!")
    
    embed.add_field(name='/toggle raidpublic',
                    value="Want other people to look at what raids your server has to offer? Just toggle it on!")

    embed.set_footer(
        "Note that the {pokemon}, {args} & {id} are variables.")
    return embed


async def get_arguments(_input: str) -> dict:
    pokemon_name = ''
    arguments = {}
    seperator = ' --'

    # On pc
    if '--' in _input:
        seperator = ' --'

    split_input = _input.strip().split(seperator)
    pokemon_name = split_input[0].title()

    if len(split_input) > 1:
        async for argument in AsyncList(split_input[1:]):
            argument_split = argument.strip().split(' ')

            # Has a value
            if len(argument_split) > 1:
                arguments[argument_split[0].lower()] = argument_split[1].lower()
            else:
                arguments[argument_split[0].lower()] = None

    return pokemon_name, arguments


def valid_pokemon(pokemon_name: str, scope: int = Scope.SPAWNPOKEMON) -> bool:
    if scope == Scope.SPAWNPOKEMON:
        if pokemon_name.strip().title() not in pokemon_list:
            return False
        return True
    elif scope == Scope.RAIDPOKEMON:
        if pokemon_name.strip().title not in [x['name'].title() for x in raid_pokemon]:
            return False
        return True


async def valid_arguments(arguments: dict, scope: int) -> bool:
    ALLOWED_ARGUMENTS_RESTRICTED = ['level', 'evtrained', 'godtier']
    ALLOWED_ARGUMENTS_DETAILED = ['level', 'evtrained', 'godtier', 'hpiv', 'hpev', 'atkiv', 'etkev', 'defiv', 'defev', 'spatkiv', 'spatkev'
                                  , 'spdefiv', 'spdefev', 'speediv', 'speedev', 'nature']

    if scope == Scope.RESTRICTED:
        for argument in AsyncList(list(arguments.keys())):
            if argument.strip().lower() not in ALLOWED_ARGUMENTS_RESTRICTED:
                return False

            if argument.lower() == 'level':
                if not arguments[argument].isdigit():
                    return False

        return True


async def get_wrong_argument(arguments: dict, scope: int) -> str:
    ALLOWED_ARGUMENTS_RESTRICTED = ['level', 'evtrained', 'godtier']

    if scope == Scope.RESTRICTED:
        for argument in AsyncList(list(arguments.keys())):
            if argument.strip() not in ALLOWED_ARGUMENTS_RESTRICTED:
                return argument
        return True


async def get_raid_pokemon(ctx, _input: str) -> interactions.Embed:
    embed = interactions.Embed(title="Something went wrong")
    embed.color = 0x3F704D

    pokemon_name, args = await get_arguments(_input)

    embed.title = f'Counters for {pokemon_name}:'

    if not await valid_pokemon(pokemon_name):
        embed.color = 0X880808
        embed.title = f'Counters for {pokemon_name} ( Invalid Pokemon ):'
        embed.add_field(
            name='Error', value=f'{pokemon_name} is not a valid pokemon!')
        return embed

    if not await valid_arguments(arguments=args, scope=Scope.RESTRICTED):
        embed.color = 0X880808
        embed.title = f'Counters for {pokemon_name}:'
        embed.add_field(name='Arguments: ( invalid )', value=f'{get_wrong_argument(args, scope=Scope.RESTRICTED)} \
                         is not a valid argument or has an incorrect value!')
        return embed

    best_pokemon_list = await raids.get_general_raid_pokemon(pokemon_list[pokemon_name], arguments=args)

    max_length = max(len(item[1]) for item in best_pokemon_list)

    for pokemon_name, move_name, score in best_pokemon_list:
        embed.add_field(name=pokemon_name, value=f'```{move_name.ljust(max_length)}|{score}```')


    string = ""
    for argument in args:
        if args[argument] is None:
            string += argument.title() + ', '
        
        else:
            string += argument.title() + ': ' + str(args[argument]) + ', '
    embed.set_footer(string)
    return embed


async def process_raid_message(bot, message) -> None:
    with open(os.getcwd() + '/data/public_servers') as f:
        public_servers = eval(f.read())

    if message.guild_ids in public_servers:
        embed = message.embeds
        description = embed[0].description
        
        raid_boss = description.split('**Raid Boss :**')[1].split('\n')[0].strip()
        stars = description.split('**Raid Stars :**')[1].split('\n')[0].strip()
        time_until_raid = description.split('A new raid will start in')[1].split('.')[0].strip()
        raid_id = '-'

        if 'Raid ID' in description:
            raid_id = description.split('**Raid ID :**')[1].split('\n')[0].strip()

        time_left = 0

        if time_until_raid == '1 hour':
            time_left = 3600
        elif time_until_raid == '15 minutes':
            time_left = 900
        elif time_until_raid == '10 minutes':
            time_left = 600
        elif time_until_raid == '5 minutes':
            time_left = 300

        raid_class.add_raid(raid_boss=raid_boss,
                                guild=int(message.guild_id),
                                timestamp=str(message.timestamp), time_left = time_left, stars=stars, id_=raid_id)
    
    
async def process_message(bot: interactions.Client, message: interactions.message.Message) -> None:
    embeds = message.embeds

    if embeds != [] and embeds != None:
        if message.author.username == 'Pokémon':
            if embeds[0].title == '⚔️ Raid Announcement ⚔️':
                await process_raid_message(bot, message)
            elif  embeds[0].title == "A wild pokémon has аppeаred!":
                channel = await message.get_channel()
                await channel.send(embeds=await name_pokemon.name_pokemon(embeds[0].image.url))


async def search_raids(ctx, bot: interactions.Client) -> interactions.Embed:
    raid_class.update()
    embed = interactions.Embed(title='Current Raids: ')
    embed.color = 0x3F704D

    list_of_raid_pokemon = raid_class.get()

    string = "```"
    try:
        max_length = max([len(x[0]) for x in list(list_of_raid_pokemon.values())])
    except Exception:
        max_length = 1

    list_ = list(list_of_raid_pokemon.items())
    list_ = sorted(list_, key=lambda x: x[1][2] + x[1][1])
    for guild, lst in list_[:15]:
        try:
            guild_name = await bot._http.get_guild(int(guild))
            guild_name = guild_name['name']
            raid_boss = lst[0]
            if raid_boss == '?':
                raid_boss = 'Yet to hatch'

            seconds = lst[2] - time.time() + lst[1] - 30 # (For some reason this is needed)
            m, s = divmod(seconds, 60)
            h, m = divmod(m, 60)

            embed.add_field(name=f"{guild_name} , id: {lst[4]}, star: {lst[3]} ", value=f'```{raid_boss.ljust(max_length)} | Hr: {int(h)} Min: {int(m)} Sec: {int(s)}```')
        except Exception:
            pass
    embed.set_footer('Showing only the first 15 raids')
    return embed


async def toggle_public_server(ctx, bot: interactions.Client) -> str:

    public_servers = []
    with open(os.getcwd() + '/data/public_servers') as file:
        public_servers = eval(file.read())

    sender_id = ctx.user.id
    guild_id = int(ctx.guild_id)

    guild = await bot._http.get_guild(guild_id)
    guild_owner_id = guild['owner_id']

    if sender_id != guild_owner_id:
        return "Sorry, only owners can edit this"
    
    if guild_id not in public_servers:
        public_servers.append(guild_id)
        with open(os.getcwd() + '/data/public_servers', 'w') as file:
            file.write(str(public_servers))
        return 'Successfully made this server public. \n (changes will take place from next raid)'#'Successfully hid this server. \n (changes will take place from next raid)'

    else:
        public_servers.remove(guild_id)
        with open(os.getcwd() + '/data/public_servers', 'w') as file:
            file.write(str(public_servers))
        return 'Successfully hid this server. \n (changes will take place from next raid)'


def get_server_id(raid_id):
    raids = raid_class.get()
    for key, list_ in list(raids.items()):
        if list_[4] != '-':
            if int(list_[4]) == int(raid_id):
                return key
        
    print('x')        
    return False


async def get_server_link(ctx, bot: interactions.Client, id_: int) -> str:
    server_id = get_server_id(raid_id=id_)
    if server_id == False:
        return f'Sorry the raid with id {id_} does not exist'
    guild = await bot._http.get_guild(server_id) 
    invite_arguments = {
        'max_age': 120,
        'max_uses': 1,
        'temporary': True,

    }
    owner_id = guild['owner_id']
    first_channel_id = guild['system_channel_id']
    invite_link = await bot._http.create_channel_invite(first_channel_id, payload=invite_arguments)
    owner = await bot._http.get_user(int(owner_id))
    if invite_link == {'message': 'Missing Permissions', 'code': 50013}:
        return f"Sorry, I do not have the required permissions in that server to create an invite link :( \n\
This server is owned by {owner['username']}#{owner['discriminator']}. Please contact him/her. \n\
Also while you are at it, ask him to give me permission to invite so that others don't have to do this again. Thanks!".strip()
    return f"https://discord.com/invite/{invite_link['code']}"
