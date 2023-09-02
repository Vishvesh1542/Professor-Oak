import discord
from discord.ext.pages import Paginator, Page, PaginatorButton
import json
import os

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

def load() -> None:
    global weakness_chart, raid_pokemon, pokemon_list
    with open(os.getcwd() + '/data/weakness_chart') as file:
        weakness_chart = eval(file.read())

    with open(os.getcwd() + '/data/raid_pokemon') as file:
        raid_pokemon = eval(file.read())

    with open(os.getcwd() + '/data/pokemon_list') as file:
        pokemon_list = json.load(file)

    print(' [ INFO ]'.ljust(15) + 'Loaded raid files.')


async def get_weakness(type_1, type_2='', type_3=''):
    table = {type_name: 1 for type_name in weakness_chart}
    
    if type_1.lower() == 'shadow':
        type_1, type_2 = type_2, type_3

    def apply_effectiveness(effectiveness, _types, multiplier):
        for _type in _types:
            table[_type] *= multiplier
    
    def process_types(_type):
        for effectiveness, _types in weakness_chart[_type.lower()].items():
            if effectiveness == 'weak':
                apply_effectiveness(effectiveness, _types, 2)
            elif effectiveness == 'resist':
                apply_effectiveness(effectiveness, _types, 0.5)
            elif effectiveness == 'immune':
                apply_effectiveness(effectiveness, _types, 0)
    
    process_types(type_1)
    if type_2:
        process_types(type_2)

    for key in table:
        if table[key] == 0:
            table[key] = 0.25
    
    return table

async def get_damage(attacking_pokemon: dict, defending_pokemon: dict, move: list, random_number: int = 0.925) -> int:
    atk_by_def = 0
    defending_pokemon_weakness = await get_weakness(*defending_pokemon['type'])

    if move[2] == 'p':
        atk_by_def = attacking_pokemon['atk'] / defending_pokemon['def']

    elif move[2] == 's':
        atk_by_def = attacking_pokemon['spatk'] / defending_pokemon['spdef']

    damage = int(((2 * attacking_pokemon['level'] * .2 + 2) * move[1][0] * atk_by_def *
                  (0.02 * move[1][1] * .01) + 2) * defending_pokemon_weakness[move[0].lower()] * random_number)

    return damage


async def get_stats(pokemon: dict, level: int, arguments: dict) -> dict:
    iv = {stat: 20 for stat in ['hp', 'atk', 'def', 'spatk', 'spdef', 'speed']}
    ev = {stat: 0 for stat in ['hp', 'atk', 'def', 'spatk', 'spdef', 'speed']}

    for argument, value in arguments.items():
        argument = argument.lower()
        if argument == 'evtrained':
            ev = {stat: 252 for stat in ev}
        elif argument == 'godtier':
            iv.update({'hp': 31, 'atk': 31, 'spatk': 31, 'def': 26, 'spdef': 26, 'speed': 20})

        elif 'iv' == argument:
            stat = argument.replace('iv', '')
            iv[stat] = int(value)
        elif 'ev' == argument:
            stat = argument.replace('ev', '')
            ev[stat] = int(value)
       
    stats = pokemon.copy()
    for stat in ['hp', 'atk', 'def', 'spatk', 'spdef', 'speed']:
        stats[stat] = int(((iv[stat] + (2 * int(pokemon[stat])) + (ev[stat] / 4) + 100) * level) / 100 + 10)
    
    stats['level'] = level
    stats['type'] = [t.lower() for t in stats['type']]
    
    return stats


async def get_score(attacking_pokemon: dict, defending_pokemon: dict) -> int:
    score = 0

    avg_damage_done = await get_damage(attacking_pokemon=attacking_pokemon,
                                 defending_pokemon=defending_pokemon, move=attacking_pokemon['move'])
    avg_damage_taken = []

    score += avg_damage_done
    avg_damage_taken.append(await get_damage(
        defending_pokemon, attacking_pokemon, ['normal', [40, 100], 'p']))
    for move in defending_pokemon['moves']:
        avg_damage_taken.append(await get_damage(
            defending_pokemon, attacking_pokemon, move))
    score -= sum(avg_damage_taken)/len(avg_damage_taken) * 4

    return int(score)


async def get_general_raid_pokemon(pokemon: dict, arguments: dict) -> list:
    score_list = []

    level = 100
    if 'level' in arguments:
        level = int(arguments['level'])

    spawn_pokemon = await get_stats(pokemon, level=level, arguments={})

    async for rpokemon in AsyncList(raid_pokemon):
        pokemon = await get_stats(rpokemon, level=100, arguments=arguments)
        score = await get_score(attacking_pokemon=pokemon,
                          defending_pokemon=spawn_pokemon)
        score_list.append([rpokemon['name'], rpokemon['move'][3], score])

    return sorted(score_list, key=lambda x: x[2], reverse=True)


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


async def valid_pokemon(pokemon_name: str) -> bool:
    if pokemon_name.strip().title() not in pokemon_list and \
        pokemon_name.strip().title() not in [x['name'].title() for x in raid_pokemon]:
        return False
    return True



async def valid_arguments(arguments: dict) -> bool:
    ALLOWED_ARGUMENTS_RESTRICTED = ['level', 'evtrained', 'godtier']
    async for argument in AsyncList(list(arguments.keys())):
        if argument.strip().lower() not in ALLOWED_ARGUMENTS_RESTRICTED:
            return False

        if argument.lower() == 'level':
            if not arguments[argument].isdigit():
                return False

    return True


async def get_wrong_argument(arguments: dict) -> str:
    ALLOWED_ARGUMENTS_RESTRICTED = ['level', 'evtrained', 'godtier']

    async for argument in AsyncList(list(arguments.keys())):
        if argument.strip() not in ALLOWED_ARGUMENTS_RESTRICTED:
            return argument
    return True

async def get_meta(pokemon: str):
    pokemon_name, args = await get_arguments(pokemon)

    if not await valid_pokemon(pokemon_name):
        return discord.Embed(title='Invalid Pokémon  :(', color=0X880808, 
                                description=f"**ERROR :** \n Sorry, {pokemon_name} is not a Pokémon.")
        
    if not await valid_arguments(args):
        return discord.Embed(title=f'Counters for {pokemon_name}:', color=0X880808, 
                                description="**ERROR :** \n Sorry, you gave an invalid argument. \n**allowed arguments :** 'godtier', 'evtrained', 'level {value}'")
        
    pokemon = pokemon_list[pokemon_name]
    best_pokemon_list = await  get_general_raid_pokemon(pokemon, arguments=args)
    number_of_items_in_page = 7
    split_lists = [best_pokemon_list[i:i+number_of_items_in_page] for i in range(0, len(best_pokemon_list), number_of_items_in_page)]
    pages = []
    for _, page in enumerate(split_lists, start=1):
        embed = discord.Embed(title=f"Counters for {pokemon_name}", color=0x3F704D)
        max_size = max(len(i[1]) for i in page)
        
        for i in page:
            embed.add_field(name=i[0], value=f'```{i[1].ljust(max_size)} | {i[2]}```', inline=False)
        
        embed.set_footer(text='The higher the number, the better the Pokemon!')
        pages.append(Page(embeds=[embed,]))

    paginator = Paginator(pages, show_indicator=False)
    return paginator