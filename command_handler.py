import discord
from discord import Option
from discord.ext import commands
from discord.ext.pages import Page, Paginator
import random
import time

import user_handler
import raid_searches
import raids
global color_list 
color_list = [0x3F704D,0x4D6D70,0x704D67,0x6D704D,0x50704D,0x704D4D,0x5B704D,0x704D56,0x4D7070,0x704E3D]

class CommandHandler:
    def __init__(self, bot: discord.Bot) -> None:
        self.bot = bot
        self.commands = {}

        self.add_commands_cog()

    def add_command(self, name, description, function, 
                    option_1=None, i_name=None, i_description=None,
                    i_type=None, i_required=True, group=None):
        
        options = []
        
        if option_1:
            options.append(Option(input_type=i_type, name=i_name,
                                description=i_description,
                                required=i_required))
            
        @commands.slash_command(name=name, description=description)
        async def f(ctx, **kwargs):
            function_kwargs = {'ctx': ctx}
            for option in options:
                function_kwargs[option.name] = kwargs.get(option.name)
            function(**function_kwargs)
            
        self.commands[name] = {'description': description,
                                'options': options, 'function': function}

    async def send_message(self, ctx, message=None, embeds=None, paginator=None):
        if message:
            if isinstance(ctx, discord.Message):
                await ctx.channel.send(message, reference=ctx)
            else:
                await ctx.respond(message)
            return None
        elif embeds:
            if not paginator:
                if isinstance(ctx, discord.Message):
                    await ctx.channel.send(embed=embeds, reference=ctx)
                else:
                    await ctx.respond(embed=embeds)
                return None
            else:
                if isinstance(ctx, discord.Message):
                    await Paginator.send(ctx)
                else:
                    await paginator.respond(interaction=ctx.interaction)
                return None

    def add_commands_cog(self):
        @commands.slash_command(name='start', description='Start making your life easier by being a part of Professor Oak.')
        async def sc_start(ctx: discord.commands.ApplicationContext):
            await self.c_start_slash(ctx=ctx)
        self.commands['start'] = {'description': 
        'Start making your life easier by being a part of Professor Oak.',
                                 'options': [], 'function': self.c_start}
        
        @commands.slash_command(name='help', description='Get help on how to use Professor Oak.')
        async def sc_help(ctx: discord.commands.ApplicationContext,
                          page=Option(input_type=int, description='Page number.',
                                      required=False)):
            await self.c_help(ctx=ctx, command_parts=page)
                    
        self.commands['help'] = {'description': 
        'get help on how to use Professor Oak.',
                                 'options': [], 'function': self.c_help}


        raid = discord.SlashCommandGroup('raid', 'Commands related to the "raids" feature of Pokemon')

        @raid.command(name='meta', description='Get the best raid counters for any Pokemon!',)
        async def sc_raid_meta(ctx, pokemon: Option(str,
                description='The Pokemon whose counters you want to get!', required=True)):
            await self.c_raid_pokemon(ctx, pokemon) 
                
        self.commands['raid meta'] = {'description': 
        'Get the best raid counters for any Pokemon!',
                                 'options': [], 'function': self.c_raid_pokemon}


        self.bot.add_application_command(sc_start)
        self.bot.add_application_command(sc_help)
        self.bot.add_application_command(raid)

    async def c_start_slash(self, ctx: discord.commands.ApplicationContext, command_parts: tuple=None):
        response = user_handler.add_user(name=ctx.user.name, user_id=ctx.user.id,
                            type_='normal', credits=100)
        if response is None:
            await ctx.respond('You are already a user!')
            return 
        await ctx.respond('Successfully added user!')
    
    async def c_start(self, ctx: discord.Message, command_parts: tuple):
        response = user_handler.add_user(name=ctx.author.name, user_id=ctx.author.id,
                              type_='normal', credits=100)
        
        if response is None:
            await ctx.channel.send('You are already a user!', reference=ctx)
            return 
        
        await ctx.channel.send('Successfully added user!', reference=ctx)

    async def c_help(self, ctx, command_parts: tuple =  None):  
        print(command_parts)
        if command_parts is None or command_parts == [] or isinstance(command_parts, Option):
            embed = discord.Embed(title='Help', color=random.choice(color_list))
            embed.description = "**Professor Oak can be used for many things**.\n\
`1. You can get the best pokemon counter for any pokemon. Just use` ``` `/raid meta {pokemon} or .raid meta` ``` \n\
`2. You can search on-going raids using` ```/raid search or .raid search``` \n \
`3. And then easily joining those servers using ` ```/server join {id} or .server join {id}```\n\n\
But there is a lot more to learn about Professor Oak. And you can learn them in the next pages.\n\
```Page 1: Setting up your server for showing it in `/raid search or .raid search` ```\
```Page 2: How to make servers which only I can access?```\
```Page 3: How to hide my serv  er again from `/raid search`?```\
```Page 4: More info```\
"
            embed.set_footer(text="Search next pages using .help {page} or /help {page}")
            if isinstance(ctx, discord.Message):
                await ctx.channel.send(embed=embed, reference=ctx)
            else:
                await ctx.respond(embed=embed)
            return None
        else:
            page = command_parts if command_parts is str else command_parts[0]
            if isinstance(page, str) and not page.isdigit():
                if isinstance(ctx, discord.Message):
                    await ctx.channel.send('Invalid page!', reference=ctx)
                else:
                    await ctx.respond("Invalid Page!")
                return None
            page = int(page)
            page_2 = discord.Embed(title='Setting up your server for showing it in `/raid search`')
            page_2.description = "It is very simple. Just go to the server you want to make public and type `/server make_public`.\
        Keep in mind that you need the ownership of the server."

            page_3 = discord.Embed(title='How to make servers which only I can access.')
            page_3.description = "Not every one can do this. This is only given to owners of reasonably \
    big communites who can benifit from the servers. This is \
    **Completely Free**. All you need to do is contact `known_as_agent` and you will be granted premiumship if you intend on helping \
    others. \
    ```How to actually make the server?```\
    You can create server groups, using `/group create {key} or .group create{key}`. remember the key as you will use that to access \
    all the servers in that group.\
    ```What do I do to add my server to that group?```\
    After you have made the group, you can easily add a server to that group with `/group add {key} or .group add {key}`\
    Currently, a server can only be in one group at a time.\
    You need the ownership of the server to add it to the group."

            page_4 = discord.Embed(title="How to hide my server again from `/raid search`")
            page_4.description = "It is very easy to hide a public server. Just use `/server remove_public or .server remove_public` \
    You need ownership. This also works if the server is in a private group. It removes the \
    server from that group. You can use this method to change the group of a server."

            page_5 = discord.Embed(title='It all sounded like greek and latin')
            page_5.description = "Sorry to hear that, I am not a professional you see. \
        Any doubts you have or any suggestions can be asked in the (Un)official server.\
        Alternatively, you can DM me `known_as_agent`. I will be more than happy to clarify \
        doubts"
            
            pages = [page_2, page_3, page_4, page_5]
            correct_page = page-1
            try:
                if isinstance(ctx, discord.Message):
                    await ctx.channel.send(embed=pages[correct_page], reference=ctx)
                else:
                    await ctx.respond(embed=pages[correct_page])
            except IndexError:
                if isinstance(ctx, discord.Message):
                    await ctx.channel.send('Invalid Page!', reference=ctx)
                else:
                    await ctx.respond('Invalid Page!')
                return None

    async def c_raid_search(self, ctx, group: str = None):
        raids_ = raid_searches.get_raids(group)
        if not raids_:
            if isinstance(ctx, discord.Message):
                await ctx.channel.send('Sorry, no raids found!', reference=ctx)
            else:
                await ctx.respond('Sorry, no raids found!')
            return None
        raids_into_pages = [raids_[i: i:10] for i in range(0, len(raids_), 10)]

        pages = []
        title = 'Ongoing raids:' if not group  else f'Ongoing raids for group {group}'
        for page_data in raids_into_pages:
            embed = discord.Embed(title=title,
                                  color=random.choice(color_list))
            for raid in page_data:
                string = ''
                string += '⭐' * int(raid['info']['stars']) 
                string.ljust(5)
                string += raid['info']['boss']

                time_left_seconds = raid['info']['start_time'] - time.time()
                minutes = time_left_seconds // 60
                seconds %= 60
                hours = minutes // 60
                minutes %= 60

                embed.add_field(name=string, value=f'time left: {hours} : {minutes} : {seconds}'.ljust(15) 
                                + str(raid['info']['raid_id']))
            pg = Page(embeds=[embed,])
            pages.append(pg)
        pgnator = Paginator(pages)

        if isinstance(ctx, discord.Message):
            await ctx.channel.send(embed=pages[0].embeds[0], reference=ctx)
        else:
            await pgnator.respond(interaction=ctx.interaction)
        return None

    async def func_process_raid(self, message) -> None:
        # if message.guild.id in user_handler.get_servers():
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

            group = None # user_handler.get_group(message.guild.id)

            raid_searches.add_raid(server=message.guild.id, start_time=time.time() + time_left,
                                   boss= raid_boss, stars = stars, group=group, raid_id=raid_id)
                                   
    async def c_raid_pokemon(self, ctx, command_parts: tuple):
        print(command_parts)
        if command_parts is None or command_parts == []:
            await ctx.channel.send('No Pokemon given!', reference=ctx)
            return 

        if command_parts is str:
            c = command_parts
        else:
            c = ''.join(command_parts)
        embed = await raids.get_meta(c)

        if isinstance(ctx, discord.Message):
            await ctx.channel.send(embed=embed.pages[0].embeds[0], reference=ctx)
        else:
            if isinstance(embed, Paginator):
                await embed.respond(interaction=ctx.interaction)
            else:
                await ctx.respond(embeds=[embed,])
        return None

    async def process_message(self, message: discord.message.Message):
                                   # Professor Oak's
        if message.author.id == 1105867485904916510:
            if message.embeds:
                if message.embeds[0].title == "⚔️ Raid Announcement ⚔️":
                    await self.func_process_raid(message)

        elif not message.content.startswith('.'):
            return None

        command_parts = message.content[1:].split(' ')
        command_name = command_parts[0]
        if command_name not in self.commands:
            try:
                command_name = command_name + ' ' + command_parts[1]
                if command_name not in self.commands:
                    return 404
                await self.commands[command_name]['function'](message, command_parts[2:])
                return
            except IndexError:
                return 
                
        await self.commands[command_name]['function'](message, command_parts[1:])
