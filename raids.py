import interactions

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
    
    async def meta(self, pokemon: str) -> interactions.Embed:
        embed = interactions.Embed(title="Something went wrong")
        embed.color = 0x3F704D

        pokemon_name, args = await self._get_arguments(pokemon)

        if not await self._valid_pokemon(pokemon_name):
            embed.color = 0X880808
            embed.title = 'Invalid Pokémon  :('
            embed.description = f"**ERROR :** \n Sorry, {pokemon_name} is not a Pokémon."
            return embed
        
        if not await self._valid_arguments(args):
            embed.color = 0X880808
            embed.title = f'Counters for {pokemon_name}:'
            embed.dscription = "**ERROR :** \n Sorry, you gave an invalid argument. \n**allowed arguments :** 'godtier', 'evtrained', 'level {value}'"
            return embed

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
        if pokemon_name.strip().title() not in self.pokemon_list:
            return False
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