import utils
import os


def init_files():
    global weakness_chart, raid_pokemon
    with open(os.getcwd() + '/data/weakness_chart') as file:
        weakness_chart = eval(file.read())

    with open(os.getcwd() + '/data/raid_pokemon') as file:
        raid_pokemon = eval(file.read())

    print('(Re)loaded Raid files')


def get_weakness(type_1, type_2, type_3=''):
    table = {'bug': 1, 'dark': 1, 'electric': 1, 'fairy': 1, 'fighting': 1, 'fire': 1, 'flying': 1, 'ghost': 1, 'grass': 1, 'ground': 1, 'ice': 1, 'normal': 1, 'poison': 1,
             'psychic': 1, 'rock': 1, 'steel': 1, 'water': 1, 'dragon': 1, 'shadow': 1}

    if type_1.lower() == 'shadow':
        type_1 = type_2
        type_2 = type_3

    for effectiveness, _types in list(weakness_chart[type_1.lower()].items()):
        if effectiveness == 'weak':
            for _type in _types:
                table[_type] *= 2
        elif effectiveness == 'resist':
            for _type in _types:
                table[_type] *= .5
        elif effectiveness == 'immune':
            for _type in _types:
                table[_type] *= 0

    if type_2 == '':
        return table

    for effectiveness, _types in list(weakness_chart[type_2.lower()].items()):
        if effectiveness == 'weak':
            for _type in _types:
                table[_type] *= 2
        elif effectiveness == 'resist':
            for _type in _types:
                table[_type] *= .5
        elif effectiveness == 'immune':
            for _type in _types:
                table[_type] *= 0

    for key, value in list(table.items()):
        if value == 0:
            table[key] = 0.25
    return table


def get_damage(attacking_pokemon: dict, defending_pokemon: dict, move: list, random_number: int = 0.925) -> int:
    atk_by_def = 0
    defending_pokemon_weakness = get_weakness(*defending_pokemon['type'])

    if move[2] == 'p':
        atk_by_def = attacking_pokemon['atk'] / defending_pokemon['def']

    elif move[2] == 's':
        atk_by_def = attacking_pokemon['spatk'] / defending_pokemon['spdef']

    damage = int(((2 * attacking_pokemon['level'] * .2 + 2) * move[1][0] * atk_by_def *
                  (0.02 * move[1][1] * .01) + 2) * defending_pokemon_weakness[move[0].lower()] * random_number)

    return damage


def get_stats(pokemon: dict, level: int, arguments: dict) -> dict:
    iv = {'hp': 20, 'atk': 20, 'def': 20,
          'spatk': 20, 'spdef': 20, 'speed': 20}
    ev = {'hp': 0, 'atk': 0, 'def': 0,
          'spatk': 0, 'spdef': 0, 'speed': 0}

    for argument in list(arguments.keys()):
        argument = argument.lower()
        if argument == 'hpiv':
            iv['hp'] = int(arguments['hpiv'])
        elif argument == 'atkiv':
            iv['atk'] = int(arguments['atkiv'])
        elif argument == 'defiv':
            iv['def'] = int(arguments['defiv'])
        elif argument == 'spatkiv':
            iv['spatk'] = int(arguments['spatkiv'])
        elif argument == 'spdefiv':
            iv['spdef'] = int(arguments['spdefiv'])
        elif argument == 'speediv':
            iv['speed'] = int(arguments['speediv'])

        elif argument == 'hpev':
            ev['hp'] = int(arguments['hpev'])
        elif argument == 'atkev':
            ev['atk'] = int(arguments['atkev'])
        elif argument == 'defev':
            ev['def'] = int(arguments['defev'])
        elif argument == 'spatkev':
            ev['spatk'] = int(arguments['spatkev'])
        elif argument == 'spdefev':
            ev['spdef'] = int(arguments['spdefev'])
        elif argument == 'speedev':
            ev['speed'] = int(arguments['speedev'])

        if argument == 'evtrained':
            ev['hp'] = 252
            ev['atk'] = 252
            ev['spatk'] = 252
        elif argument == 'godtier':
            iv['hp'] = 31
            iv['atk'] = 31
            iv['spatk'] = 31
            iv['def'] = 26
            iv['spdef'] = 26
            iv['speed'] = 20

    stats = pokemon.copy()
    stats['hp'] = int(((iv['hp'] + (2 * int(pokemon['hp'])) +
                        (ev['hp'] / 4) + 100) * level) / 100 + 10)
    stats['atk'] = int(((iv['atk'] + (2 * int(pokemon['atk'])) +
                         (ev['atk'] / 4)) * level) / 100 + 5)
    stats['def'] = int(((iv['def'] + (2 * int(pokemon['def'])) +
                         (ev['def'] / 4)) * level) / 100 + 5)
    stats['spatk'] = int(((iv['spatk'] + (2 * int(pokemon['spatk'])) +
                           (ev['spatk'] / 4)) * level) / 100 + 5)
    stats['spdef'] = int(((iv['spdef'] + (2 * int(pokemon['spdef'])) +
                           (ev['spdef'] / 4)) * level) / 100 + 5)
    stats['speed'] = int(((iv['speed'] + (2 * int(pokemon['speed'])) +
                           (ev['speed'] / 4)) * level) / 100 + 5)
    stats['level'] = level

    stats['type'] = [x.lower() for x in stats['type']]

    return stats


def get_score(attacking_pokemon: dict, defending_pokemon: dict) -> int:
    score = 0

    avg_damage_done = get_damage(attacking_pokemon=attacking_pokemon,
                                 defending_pokemon=defending_pokemon, move=attacking_pokemon['move'])
    avg_damage_taken = []

    score += avg_damage_done
    avg_damage_taken.append(get_damage(
        defending_pokemon, attacking_pokemon, ['normal', [40, 100], 'p']))
    for move in defending_pokemon['moves']:
        avg_damage_taken.append(get_damage(
            defending_pokemon, attacking_pokemon, move))
    score -= sum(avg_damage_taken)/len(avg_damage_taken) * 4

    return int(score)


async def get_general_raid_pokemon(pokemon: dict, arguments: dict) -> list:
    score_list = []

    level = 100
    if 'level' in arguments:
        level = int(arguments['level'])

    spawn_pokemon = get_stats(pokemon, level=level, arguments={})

    async for rpokemon in utils.AsyncList(raid_pokemon):
        pokemon = get_stats(rpokemon, level=100, arguments=arguments)
        score = get_score(attacking_pokemon=pokemon,
                          defending_pokemon=spawn_pokemon)
        score_list.append([rpokemon['name'], rpokemon['move'][3], score])

    return sorted(score_list, key=lambda x: x[2], reverse=True)[:10]

