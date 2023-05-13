import interactions
from interactions.ext.paginator import Page
import iohook

class RaidMeta:
    help_embed = interactions.Embed(title='Something went wrong')

    def __init__(self) -> None:
        self.init_raid_message()
        
    def init_raid_message(self) -> None:
        self.help_embed.title = 'How to use the raid commands?'
        self.help_embed.color = 0xC8A2C8

        self.help_embed.description = '\
"Professor Oak is experienced in raids\n\
and can quickly identify counter Pokémon.\n\
He scores Pokémon to aid in selection.\n\
He also can watch after servers for raids!\n\
Try these commands:'

        self.help_embed.add_field(name='/raid meta {pokemon}',
                        value='Professor Oak compares some of \
                            the best pokemon and tells which is most effective.')

        self.help_embed.add_field(name='/raid search {args}',
                        value="Globals and don't have any raids? No problem! search for raids across servers and join them if u like!")
        
        self.help_embed.add_field(name='/raid server_join {id}',
                        value="Found a raid but are not in the server? Just type the id of the raid and join the server!")
        
        self.help_embed.add_field(name='/toggle server',
                        value="Want other people to look at what raids your server has to offer? Just toggle it on!")

        self.help_embed.set_footer(
            "Note that the {pokemon}, {args} & {id} are variables.")

    async def get_raid_message(self) -> interactions.Embed:
        return self.help_embed
    
    async def _valid_arguments(self, args) -> bool:
        allowed_arguments = ['level', 'evtrained', 'godtier']

        for argument in list(args.keys()):
            if argument.strip().lower() not in allowed_arguments:
                return False

            if argument.lower() == 'level':
                if not args[argument].isdigit():
                    return False

        return True

    async def _get_arguments(self, _input: str) -> str | dict:
        pokemon_name = ''
        arguments = {}
        seperator = ' --'

        # On pc
        if '--' in _input:
            seperator = ' --'

        split_input = _input.strip().split(seperator)
        pokemon_name = split_input[0].title()

        if len(split_input) > 1:
            for argument in split_input[1:]:
                argument_split = argument.strip().split(' ')

                # Has a value
                if len(argument_split) > 1:
                    arguments[argument_split[0].lower()] = argument_split[1].lower()
                else:
                    arguments[argument_split[0].lower()] = None

        return pokemon_name, arguments

    async def _valid_pokemon(self, pokemon_name: str) -> bool:
        if pokemon_name.strip().title() not in iohook.get_pokemon().get():
            return False
        return True
  
    async def _get_weakness(self, type_1, type_2, type_3=''):
        table = {'bug': 1, 'dark': 1, 'electric': 1, 'fairy': 1, 'fighting': 1, 'fire': 1, 'flying': 1, 'ghost': 1, 'grass': 1, 'ground': 1, 'ice': 1, 'normal': 1, 'poison': 1,
                'psychic': 1, 'rock': 1, 'steel': 1, 'water': 1, 'dragon': 1, 'shadow': 1}
        
        weakness_chart = {'bug': {'weak': ('rock', 'fire', 'flying',), 'resist': ('ground', 'grass', 'fighting',), 'immune': ()}
, 'dark': {'weak': ('fairy', 'bug', 'fighting',), 'resist': ('ghost', 'dark',), 'immune': ('psychic',)}
, 'dragon': {'weak': ('fairy', 'dragon', 'ice',), 'resist': ('electric', 'water', 'fire', 'grass',), 'immune': ()}
, 'electric': {'weak': ('ground',), 'resist': ('steel', 'electric', 'flying',), 'immune': ()}
, 'fairy': {'weak': ('poison', 'steel',), 'resist': ('bug', 'fighting', 'dark',), 'immune': ('dragon',)}
, 'fighting': {'weak': ('fairy','psychic', 'flying',), 'resist': ('bug', 'rock', 'dark',), 'immune': ()}
, 'fire': {'weak': ('ground', 'water', 'rock',), 'resist': ('bug', 'ice', 'fire', 'grass', 'steel', 'fairy',), 'immune': ()}
, 'flying': {'weak': ('rock', 'electric', 'ice',), 'resist': ('grass', 'bug','fighting',), 'immune': ('ground',)}
, 'ghost': {'weak': ('ghost', 'dark',), 'resist': ('poison', 'bug',), 'immune': ('fighting', 'normal',)}
, 'grass': {'weak': ('bug', 'ice', 'flying', 'fire', 'poison',), 'resist': ('ground', 'water', 'grass', 'electric',), 'immune': ()}
, 'ground': {'weak': ('water', 'grass', 'ice',), 'resist': ('poison', 'rock',), 'immune': ('electric',)}
, 'ice': {'weak': ('rock', 'fighting', 'fire', 'steel',), 'resist': ('ice',), 'immune': ()}
, 'normal': {'weak': ('fighting',), 'resist': ('ghost',), 'immune': ()}
, 'poison': {'weak': ('ground', 'psychic',), 'resist': ('fighting', 'bug', 'grass', 'poison', 'fairy',), 'immune': ()}
, 'psychic': {'weak': ('bug', 'ghost', 'dark',), 'resist': ('psychic', 'fighting',), 'immune': ()}
, 'rock': {'weak': ('ground', 'fighting', 'water', 'grass', 'steel',), 'resist': ('poison', 'fire', 'normal', 'flying',), 'immune': ()}
, 'steel': {'weak': ('ground', 'fire', 'fighting',), 'resist': ('psychic', 'normal', 'dragon', 'bug', 'flying', 'ice', 'grass', 'steel', 'fairy', 'rock',), 'immune': ('poison',)}
, 'water': {'weak': ('electric', 'grass',), 'resist': ('ice', 'water', 'fire', 'steel',), 'immune': ()}
, 'shadow': {'weak': (), 'resis': (), 'immune': ()}
}


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

    async def _get_damage(self, attacking_pokemon: dict, defending_pokemon: dict, move: list, random_number: int = 0.925) -> int:
        atk_by_def = 0
        defending_pokemon_weakness = await self._get_weakness(*defending_pokemon['type'])

        if move[2] == 'p':
            atk_by_def = attacking_pokemon['atk'] / defending_pokemon['def']

        elif move[2] == 's':
            atk_by_def = attacking_pokemon['spatk'] / defending_pokemon['spdef']

        damage = int(((2 * attacking_pokemon['level'] * .2 + 2) * move[1][0] * atk_by_def *
                    (0.02 * move[1][1] * .01) + 2) * defending_pokemon_weakness[move[0].lower()] * random_number)

        return damage

    async def _get_stats(self, pokemon: dict, level: int, arguments: dict) -> dict:
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

    async def _get_score(self, attacking_pokemon: dict, defending_pokemon: dict) -> int:
        score = 0

        avg_damage_done = await self._get_damage(attacking_pokemon=attacking_pokemon,
                                    defending_pokemon=defending_pokemon, move=attacking_pokemon['move'])
        avg_damage_taken = []

        score += avg_damage_done
        avg_damage_taken.append(await self._get_damage(
            defending_pokemon, attacking_pokemon, ['normal', [40, 100], 'p']))
        for move in defending_pokemon['moves']:
            avg_damage_taken.append(await self._get_damage(
                defending_pokemon, attacking_pokemon, move))
        score -= sum(avg_damage_taken)/len(avg_damage_taken) * 4

        return int(score)

    async def _get_raid_pokemon(self, pokemon: dict, arguments: dict) -> list:
        score_list = []

        level = 100
        if 'level' in arguments:
            level = int(arguments['level'])

        spawn_pokemon = await self._get_stats(pokemon, level=level, arguments={})

        for rpokemon in iohook.get_raid_pokemon().get():
            pokemon = await self._get_stats(rpokemon, level=100, arguments=arguments)
            score = await self._get_score(attacking_pokemon=pokemon,
                            defending_pokemon=spawn_pokemon)
            score_list.append([rpokemon['name'], rpokemon['move'][3], score])

        return sorted(score_list, key=lambda x: x[2], reverse=True)

    async def meta(self, pokemon: str) -> interactions.Embed | list:
        pokemon_name, args = await self._get_arguments(pokemon)

        if not await self._valid_pokemon(pokemon_name):
            return interactions.Embed(title='Invalid Pokémon  :(', color=0X880808, 
                                    description=f"**ERROR :** \n Sorry, {pokemon_name} is not a Pokémon."), None
            
        if not await self._valid_arguments(args):
            return interactions.Embed(title=f'Counters for {pokemon_name}:', color=0X880808, 
                                    description="**ERROR :** \n Sorry, you gave an invalid argument. \n**allowed arguments :** 'godtier', 'evtrained', 'level {value}'"), None
            
        pokemon = iohook.get_pokemon().get_value(pokemon_name)
        best_pokemon_list = await self._get_raid_pokemon(pokemon, arguments=args)

        number_of_items_in_page = 5
        split_lists = [best_pokemon_list[i:i+number_of_items_in_page] for i in range(0, len(best_pokemon_list), number_of_items_in_page)]
        
        pages = []
        string = ''
        for key, value in list(args.items()):
            if value is None:
                string += key.title() + ', '
                continue
            string += key.title() + ": " + value + ', '

        for index, page in enumerate(split_lists, start=1):
            embed = interactions.Embed(title=f"Counters for {pokemon_name}", color=0x3F704D)
            max_size = max(len(i[1]) for i in page)
            embed.set_author(string)
            
            for i in page:
                embed.add_field(name=i[0], value=f'```{i[1].ljust(max_size)} | {i[2]}```')
            
            embed.set_footer(text=f'Showing page {index} of {len(split_lists)}')
            pages.append(Page(embeds=embed))
        
        return None, pages

        # return embed
            # pages.append(Page("Page 1", embeds=embed))
