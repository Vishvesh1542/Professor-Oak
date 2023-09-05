import discord
from discord import Option
from discord.ext import commands
from discord.ext.pages import Page, Paginator
import random
import time

import user_handler
import raid_searches
import raids
import help

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
        
        if not group:
            if option_1:
                if i_required:
                    @commands.slash_command(name=name, description=description)
                    async def f(ctx, x: Option(input_type=i_type, name=i_name,
                                                    description=i_description,
                                                    required=i_required)):
                        await function(ctx, x)
                    self.bot.add_application_command(f)
                else:
                    @commands.slash_command(name=name, description=description)
                    async def f(ctx, x: Option(input_type=i_type, name=i_name,
                                                    description=i_description,
                                                    required=i_required)):
                        await function(ctx, x)
                    self.bot.add_application_command(f)
            else:
                @commands.slash_command(name=name, description=description)
                async def f(ctx):
                    await function(ctx)
                self.bot.add_application_command(f)
            self.commands[name] = {'description': description,
                                    'options': [], 'function': function}
        else:
            if option_1:
                if i_required:
                    @group.command(name=name, description=description)
                    async def f(ctx, x: Option(input_type=i_type, name=i_name,
                                                    description=i_description,
                                                    required=i_required)):
                        await function(ctx, x)
                else:
                    @group.command(name=name, description=description)
                    async def f(ctx, x: Option(input_type=i_type, name=i_name,
                                                    description=i_description,
                                                    required=i_required)):
                        await function(ctx, x)
            else:
                @group.command(name=name, description=description)
                async def f(ctx):
                    await function(ctx)
            self.commands[group.name + ' ' + name] = {'description': description,
                                    'options': [], 'function': function}

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
        elif paginator:
            if isinstance(ctx, discord.Message):
                await ctx.channel.send(
                    embed = paginator.pages[0].embeds[0])
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

        self.add_command('help', 'Get help on how to use Professor Oak.',
                         self.c_help, True, 'page', 'Page number.', int, False)

        raid = discord.SlashCommandGroup('raid', 'Commands related to the "raids" feature of Pokemon')
        self.add_command('meta', 'Get the best raid counters for any Pokemon!', self.c_raid_pokemon
                        , True, 'pokemon', 'Pokemon whose counters you want to get!',
                        str, True, group=raid)
        self.add_command('search', 'Find out ongoing raids!', self.c_raid_search,
                         True, 'group', 'group whose raids you want to get.',
                         str, False, raid)
        
        server = discord.SlashCommandGroup('server', 'commands related to managing this server')
        self.add_command('make_public', 'Makes this server public for others to join raids.',
                         self.c_make_public, True, 'group',
                           'the group you want to add this server to', str, False, server) # Works
        
        self.add_command('remove_public', 'Hide a server so that it is not shown using `/raid search`'
                         , self.c_remove_public, False, False, False, False, False, server) # Works
        
        self.add_command('change_group', 'Change the group this server is in', self.c_change_group,
                         True, 'group', 'name of the group you want to change to', str, # Works
                         True, server)
        
        self.add_command('get_group', 'get the group this server is in!', self.c_get_group, False,
                         False, False, False, False, server) # Works
        
        self.add_command('join', 'Join a server with its raid_id', self.c_server_join, True,
                         'server_id', 'the server id. (Found below beside the raid boss)',
                         int, True, server)

        group = discord.SlashCommandGroup('group', 'group related commands.')
        self.add_command('new', 'Creates a new group', self.c_group_create,
                         True, 'group_name', 'The name of the group you want to make',
                         str, True, group) # Works

        premium = discord.SlashCommandGroup('premium', 'Premium commands :)')
        self.add_command('give', 'Give premium to a user.', self.c_premium_give,
                         True, 'person', 'The person whom you want to give premium to',
                         discord.SlashCommandOptionType.user, True, premium) # Works

        self.bot.add_application_command(sc_start)
        self.bot.add_application_command(raid)
        self.bot.add_application_command(server)
        self.bot.add_application_command(group)
        self.bot.add_application_command(premium)

    async def c_start_slash(self, ctx: discord.commands.ApplicationContext, _: tuple=None):
        response = user_handler.add_user(name=ctx.user.name, user_id=ctx.user.id,
                            type_='normal', credits=100)
        if response is None:
            await ctx.respond('You are already a user!')
            return 
        await ctx.respond('Successfully added user!')
    
    async def c_start(self, ctx: discord.Message, _: tuple=None):
        response = user_handler.add_user(name=ctx.author.name, user_id=ctx.author.id,
                              type_='normal', credits=100)
        
        if response is None:
            await ctx.channel.send('You are already a user!', reference=ctx)
            return 
        
        await ctx.channel.send('Successfully added user!', reference=ctx)

    async def c_help(self, ctx, command_parts: tuple =  None):  
        page = 0

        if isinstance(ctx, discord.Message):
            command_parts = ' '.join(command_parts)

        if command_parts and command_parts.isdigit():
            int_ = int(command_parts)
            if 0 < int_ < 8:
                page = int_
        embed = help.get_page(page)
        await self.send_message(ctx, embeds=embed)

#         if command_parts is None or command_parts == [] or isinstance(command_parts, Option):
#             embed = discord.Embed(title='Help', color=random.choice(color_list))
#             embed.description = "**Professor Oak can be used for many things**.\n\
# `1. You can get the best pokemon counter for any pokemon. Just use` ``` `/raid meta {pokemon} or .raid meta` ``` \n\
# `2. You can search on-going raids using` ```/raid search or .raid search``` \n \
# `3. And then easily joining those servers using ` ```/server join {id} or .server join {id}```\n\n\
# But there is a lot more to learn about Professor Oak. And you can learn them in the next pages.\n\
# ```Page 1: Setting up your server for showing it in `/raid search or .raid search` ```\
# ```Page 2: How to make servers which only I can access?```\
# ```Page 3: How to hide my serv  er again from `/raid search`?```\
# ```Page 4: More info```\
# "
#             embed.set_footer(text="Search next pages using .help {page} or /help {page}")
#             await self.send_message(ctx=ctx, embeds=embed)
#         else:
#             page = command_parts if command_parts is str else command_parts[0]
#             if isinstance(page, str) and not page.isdigit():
#                 if isinstance(ctx, discord.Message):
#                     await ctx.channel.send('Invalid page!', reference=ctx)
#                 else:
#                     await ctx.respond("Invalid Page!")
#                 return None
#             page = int(page)
#             page_2 = discord.Embed(title='Setting up your server for showing it in `/raid search`')
#             page_2.description = "It is very simple. Just go to the server you want to make public and type `/server make_public`.\
# Keep in mind that you need the ownership of the server."

#             page_3 = discord.Embed(title='How to make servers which only I can access.')
#             page_3.description = "Not every one can do this. This is only given to owners of reasonably \
# big communites who can benifit from the servers. This is \
# **Completely Free**. All you need to do is contact `known_as_agent` and you will be granted premiumship if you intend on helping \
# others. \
# ```How to actually make the server?```\
# You can create server groups, using `/group create {key} or .group create{key}`. remember the key as you will use that to access \
# all the servers in that group.\
# ```What do I do to add my server to that group?```\
# After you have made the group, you can easily add a server to that group with `/group add {key} or .group add {key}`\
# Currently, a server can only be in one group at a time.\
# You need the ownership of the server to add it to the group."

#             page_4 = discord.Embed(title="How to hide my server again from `/raid search`")
#             page_4.description = "It is very easy to hide a public server. Just use `/server remove_public or .server remove_public` \
# You need ownership. This also works if the server is in a private group. It removes the \
# server from that group. You can use this method to change the group of a server."

#             page_5 = discord.Embed(title='It all sounded like greek and latin')
#             page_5.description = "Sorry to hear that, I am not a professional you see. \
# Any doubts you have or any suggestions can be asked in the (Un)official server.\
# Alternatively, you can DM me `known_as_agent`. I will be more than happy to clarify \
# doubts"
    
            # pages = [page_2, page_3, page_4, page_5]
            # correct_page = page-1
            # try:
            #     await self.send_message(ctx, embeds=pages[correct_page])
            # except IndexError:
            #     await self.send_message(ctx, 'Invalid page!')

    async def c_raid_search(self, ctx, group: str = None):
        if not group:
            group=None
        raids_ = await raid_searches.get_raids(group)
        if not raids_:
            await self.send_message(ctx, 'Sorry, no raids found.')
            return None
        raids_into_pages = [raids_[i: i+10] for i in range(0, len(raids_), 10)]

        pages = []
        title = 'Ongoing raids:' if not group  else f'Ongoing raids for group {group}'
        for page_data in raids_into_pages:
            embed = discord.Embed(title=title,
                                  color=random.choice(color_list))
            for raid in page_data:
                string = raid['info']['stars']
                string = string.ljust(10, "\u00a0")

                seconds = raid['info']['start_time'] - time.time()
                minutes = int(seconds // 60)
                seconds %= 60
                hours = int(minutes // 60)
                minutes %= 60
                seconds = int(seconds)
                string += f'{hours}:{minutes}:{seconds}'
                embed.add_field(name=string, value=f'{raid["info"]["raid_id"]}'.ljust(15, '\u00a0') + f" | {raid['info']['boss']}")
            pg = Page(embeds=[embed,])
            pages.append(pg)
        pgnator = Paginator(pages)

        if isinstance(ctx, discord.Message):
            await ctx.channel.send(embed=pages[0].embeds[0], reference=ctx)
        else:
            await pgnator.respond(interaction=ctx.interaction)
        return None

    async def c_server_join(self, ctx, raid_id: int):
        message = False
        if isinstance(ctx, discord.Message):
            message = True
            string = ' '.join(raid_id)
            if not string.isdigit():
                await self.send_message(ctx, 'Invalid server_id!')
                return
            raid_id = int(string)
        
        server_id = await raid_searches.from_id(raid_id)
        if not server_id:
            await self.send_message(ctx, 'Sorry, a raid with that id does not exist.')
            return
        server = self.bot.get_guild(int(server_id))
        try:
            invite = await server.text_channels[0].create_invite(max_age=60, max_uses=1, temporary=True)

            await self.send_message(ctx, invite)

        except:
            await self.send_message(ctx, 'Sorry, I do not have permission to create links for this server.')
            return
        
    async def c_make_public(self, ctx: discord.context.ApplicationContext, group: str=None):
        user_id = None
        if isinstance(ctx, discord.Message):
            user_id = ctx.author.id
            group = ' '.join(group)
            group = group.strip()
            if group == '' or group == ' ':
                group = None
            if ctx.author.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
        else:
            user_id = ctx.user.id
            if group:
                group = group.strip()
                if group == '' or group == ' ':
                    group = None
            if ctx.user.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
            
        added = user_handler.add_server(user_id, ctx.guild.id)
        if not added:
            await self.send_message(ctx, 'Sorry, you must be a member of Professor Oak community. start using `/start` !')
            return
        
        if group:
            made = user_handler.set_group(ctx.guild.id, group)
            if not made and made != 404:
                await self.send_message(ctx, 'Sorry, that group does not exist. make it first using `/group new` !')
                return
            elif made == 404:
                await self.send_message(ctx, 'Sorry, this server is not public.')
        await self.send_message(ctx, 'Successfully added this server to group: ' + f"`{group}`")

    async def c_remove_public(self, ctx, _=None):
        user_id = None
        if isinstance(ctx, discord.Message):
            if ctx.author.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
            user_id = ctx.author.id
            
        else:
            if ctx.user.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
            user_id = ctx.user.id
            
        removed = user_handler.remove_server(user_id, ctx.guild.id)
        if not removed:
            await self.send_message(ctx, 'Sorry, you must be a member of Professor Oak community. start using `/start` !')
            return
        if removed == 404:
            await self.send_message(ctx, 'This server is not public.')
            return
        
        await self.send_message(ctx, 'Successfully hid this server!')
    
    async def c_change_group(self, ctx, group: str):
        if isinstance(ctx, discord.Message):
            group = ' '.join(group)
            group = group.strip()
            if group == '' or group == ' ':
                group = None
            if ctx.author.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
            
        else:
            group = group.strip()
            if group == '' or group == ' ':
                group = None
            if ctx.user.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can edit this.')
                return
        
        result = user_handler.set_group(ctx.guild.id, group)
        if not result:
            await self.send_message(ctx, 'Sorry, that group does not exist. make it first using `/group new` !')
        
        elif result == 404:
            await self.send_message(ctx, 'This server is not public. Make it public first by using `/server make_public` !')
        
        else:
            await self.send_message(ctx, f'Successfully added this server to group `{group}`')

    async def c_get_group(self, ctx, _=None):
        if isinstance(ctx, discord.Message):
            if ctx.author.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can view this.')
                return
            
        else:
            if ctx.user.id != ctx.guild.owner_id:
                await self.send_message(ctx, 'Sorry, only owners can view this.')
                return

        group = user_handler.get_group(ctx.guild.id)
        print(group)

        if group == 404:
            await self.send_message(ctx, 'This server is not public.')
            return
        elif not group:
            await self.send_message(ctx, 'This server is not in any group.')
            return
        await self.send_message(ctx, 'This server is in group: `' + str(group) + '`')

    async def c_group_create(self, ctx, group=str):

        author_id = None
        if isinstance(ctx, discord.Message):
            group = ' '.join(group)
            author_id = ctx.author.id
        else:
            author_id = ctx.user.id
        group = group.strip()
        if group == '' or group == ' ':
            group = None
            await self.send_message(ctx, 'group_name is a required value!')
        user = user_handler.get_user(author_id)
        if not user:
            await self.send_message(ctx, 'Sorry, you must be a member of Professor Oak community. start using `/start` !')
        elif user['type'] != 'premium':
            await self.send_message(ctx, 'Sorry, only premium users can edit this. |||Contact known_as_agent|||')
        else:
            added = user_handler.add_group(group, ctx.guild.owner_id)
            if not added:
                await self.send_message(ctx, 'Sorry,a group with that name already exists.')
                return
            await self.send_message(ctx, f'Successfully added group {group}. Add servers to it by using `/server make_public` !')

    async def c_premium_give(self, ctx, user):
        user = user.strip()
        if isinstance(ctx, discord.Message):
            user = user[0][2:-1]
            if ctx.author.id != 886873187965616158:
                await self.send_message(ctx, 'Only admins can change this.')
                return
        else:
            user = user[2:-1]
            if ctx.user.id != 886873187965616158:
                await self.send_message(ctx, 'Only admins can change this.')
                return 
        
        set_ = user_handler.set_type(user, 'premium')
        if not set_:
            await self.send_message(ctx, 'Sorry, that user is not a part of Professor Oak.')
        else:
            await self.send_message(ctx, f'Successfully gave premium to user @{user}')

    async def func_process_raid(self, message) -> None:
        # if message.guild.id in user_handler.get_servers():
            embed = message.embeds
            description = embed[0].description
            
            raid_boss = description.split('**Raid Boss :**')[1].split('\n')[0].strip()
            stars = description.split('**Raid Stars :**')[1].split('\n')[0].strip()
            time_until_raid = description.split('A new raid will start in')[1].split('.')[0].strip()
            raid_id = '0'

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

            group = user_handler.get_group(message.guild.id)

            raid_searches.add_raid(server=message.guild.id, start_time=time.time() + time_left,
                                   boss= raid_boss, stars = stars, group=group, raid_id=raid_id)
                                   
    async def c_raid_pokemon(self, ctx, command_parts: tuple):
        if command_parts is None or command_parts == []:
            await ctx.channel.send('No Pokemon given!', reference=ctx)
            return 

        if command_parts is str:
            c = command_parts
        else:
            c = ''.join(command_parts)
        embed = await raids.get_meta(c)

        if isinstance(embed, Paginator):
            await self.send_message(ctx,paginator=embed)
        else:
            await self.send_message(ctx, embeds=embed)

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
