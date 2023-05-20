import interactions
from interactions.ext.paginator import Paginator, Page
import raids
import iohook
import raid_search
from name_pokemon import name_pokemon, init_files

token = "MTEwNTg2NzQ4NTkwNDkxNjUxMA.GeVGBd.EIqurAJanZJM9pAQGQPIXXZj700O6Lx3kvJxO0"

bot = interactions.Client(token=token, intents=interactions.Intents.ALL)

@bot.event
async def on_ready():
    global raidmeta, raidsearch
    raidmeta = raids.RaidMeta()
    raidsearch = raid_search.RaidSearcher(bot=bot)
    iohook.init()
    init_files()

    print('ready')
command_meta = interactions.Option(
            name="meta",
            description="Using Professor Oak's experience get the best counters to any Pokémon!",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name="pokemon",
                    description="Pokémon whose best raid counters you want to get.",
                    type=interactions.OptionType.STRING,
                    required=True,
                ),  
            ],
        )
command_search = interactions.Option(
    name='search',
    description="Globals time and don't know which server to join? No worry! Everything is one command away!",
    type=interactions.OptionType.SUB_COMMAND,
    options=[
        interactions.Option(
            name='group',
            description="If you have access to private servers, type the _secret code_ to get access to them.",
            type=interactions.OptionType.STRING,
            required=False
        )
    ]
)


subcommands = [
command_meta,
command_search
]
@bot.command(
        name='raid', description='If you see this you are hacking',
        options=subcommands)
async def raid(ctx: interactions.CommandContext, sub_command: str, pokemon: str=' ', group=None):
    if sub_command == 'help':
        await ctx.send(embeds=await raidmeta.get_raid_message())
    elif sub_command == 'meta':
        try:
            embeds, pages = await raidmeta.meta(pokemon=pokemon)
            if embeds:
                await ctx.send(embeds=embeds)
            else:
                await   Paginator(client=bot, ctx=ctx, pages=pages, disable_after_timeout=True, use_select=False).run()

        except:
            await ctx.send('Sorry, something went wrong. Please try again', ephemeral=True)
    elif sub_command == 'search':
        try:
            list_ = raidsearch.get_raids(group)
            number_of_items_in_page = 3
            list_split = [list_[i: i + number_of_items_in_page] for i in range(0, len(list_), number_of_items_in_page)]

            pages = []
            for index, page in enumerate(list_split, start=1):
                embed = interactions.Embed(title=f"Current Raids", color=0x3F704D)
                max_ = max(len(x.raid_boss) for x in page) if page else 0
                
                for i in page:
                    stars = '⭐' * i.raid_stars
                    embed.add_field(name=f'{i.raid_boss.ljust(max_)} | id: `{i.raid_id}`', value=f'```{stars.ljust(5)} | Time left: {i.get_time_left_string()}```')
                
                embed.set_footer(text=f'Showing page {index} of {len(list_split)}')
                pages.append(Page(embeds=embed))

            if len(pages) > 1:
                paginator = Paginator(client=bot, ctx=ctx, pages=pages, disable_after_timeout=True, use_select=False)
                await paginator.run()
            else:
                try:
                    await ctx.send(embeds=embed)
                except UnboundLocalError:
                    await ctx.send(embeds=interactions.Embed(title='Sorry, there are no raids matching your requirements'))
        except:
            await ctx.send('Sorry, something went wrong. Please try again', ephemeral=True)

@bot.command(
        name='server',
        description='If u can see this u are hacking',
        options=[
            interactions.Option(
                name='join',
                description='Found the perfect raid? Need to join the server? Just type the raid id!',
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                    name='server_id',
                    description='The id of the server you want to join.',
                    type=interactions.OptionType.INTEGER,
                    required=True
                    )
                ]
            ),
            interactions.Option(
                name='make_public',
                description='Make this server public and accessable by anyone using /raid search',
                type=interactions.OptionType.SUB_COMMAND
            ),
            interactions.Option(
                name='remove_public',
                description='Makes this server private. No one can see this using /raid search',
                type=interactions.OptionType.SUB_COMMAND
            )
        ]
)
async def server(ctx: interactions.CommandContext, sub_command: str, server_id: int=-1):
    if sub_command == 'join':
        try:
            server_ = await raidsearch.get_invite_link(raid_id=server_id)
            await ctx.send(server_, ephemeral=True)
        except Exception as e:
            print(e)

    elif sub_command == 'make_public':
        if ctx.user.id != ctx.guild.owner_id:
            await ctx.send('Sorry, only owners can edit this.')
            return 
        iohook.get_public_servers().get()[str(ctx.guild_id)] = None
        iohook.get_public_servers().save()
        await ctx.send('Successfully made this server public to everyone')
    elif sub_command == 'remove_public':
        if ctx.user.id != ctx.guild.owner_id:
            ctx.send('Sorry, only owners can ed it this.')
            return 
        iohook.get_public_servers().get().pop(str(ctx.guild_id))
        await ctx.send('Successfully hid this server.')


@bot.command(
    name='group',
    description='If u can see this u are hacking',
    options=[
        interactions.Option(
            name='create',
            description='Create a new private group for servers',
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name='name',
                    description='Name of the new private server.',
                    type=interactions.OptionType.STRING,
                    required=True
                )
            ]
        ),
        interactions.Option(
            name='add',
            description='Made a private group? Add your servers with this command.',
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name='name',
                    description='Name of the private server.',
                    type=interactions.OptionType.STRING,
                    required=True
                )
            ]
        ),
        interactions.Option(
            name='remove',
            description='Removes this server from all groups.',
            type=interactions.OptionType.SUB_COMMAND,
            )
    ]
)
async def group(ctx: interactions.CommandContext, sub_command: str, name: str='String'):
    try:
        if sub_command == 'create':
            if ctx.user.id not in iohook.get_premium_users().get():
                await ctx.send('Sorry, only premium users can create private groups. :(  ||Contact @TheAgent#1542||')
                return
            if name in iohook.get_public_servers().get()['groups']:
                await ctx.send(f'Sorry, a private group with name {name} already exists. :( ') 
                return 
            iohook.get_public_servers().get()['groups'].append(name)
            iohook.get_public_servers().save()
            await ctx.send(f'Successfully created private group with name {name}')
        elif sub_command == 'add':
            if ctx.user.id not in iohook.get_premium_users().get():
                await ctx.send('Sorry, only premium users can add servers to groups :(. ||Contant @TheAgent#1542||')
                return
            if name not in iohook.get_public_servers().get()['groups']:
                await ctx.send(f'Sorry, the group with name {name} does not exist. ||Create it with /group create||')
                return 
            if ctx.guild_id in iohook.get_public_servers().get():
                if iohook.get_public_servers().get()[str(ctx.guild_id)] == name:
                    await ctx.send(f'This server is already in the group {name}')
                else:
                    await ctx.send('This server is already in another group.')       

                return 
            if ctx.guild.owner_id != ctx.user.id:
                await ctx.send('Sorry, only owners can edit this')
                return
            iohook.get_public_servers().get()[str(ctx.guild_id)] = name
            iohook.get_public_servers().save()
            await ctx.send(f'Successfully added this group to private group {name}')
        elif sub_command == 'remove':
            if ctx.user.id not in iohook.get_premium_users().get():
                await ctx.send('Sorry, only premium users can remove servers from groups :(. ||Contant @TheAgent#1542||')
                return
            if ctx.guild_id not in iohook.get_public_servers().get():
                await ctx.send('This server is not in any groups.')       
                return 
            if ctx.guild.owner_id != ctx.user.id:
                await ctx.send('Sorry, only owners can edit this')
                return
            iohook.get_public_servers().get().pop(str(ctx.guild_id))
            iohook.get_public_servers().save()
            await ctx.send(f'Successfully removed this server from groups')
    except Exception as e:
        await ctx.send('Sorry, something went wrong. Please try again', ephemeral=True)
        print(e)

    
@bot.command(
        name='premium',
        description='If u can see this you are hacking',
        scope=1066670325993046046,
        options=[
            interactions.Option(
                name='give',
                description='Give premium to a specific user',
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name='user',
                        description='The user whom you want to give premium to.',
                        type=interactions.OptionType.USER,
                        required=True
                    )
                ]
            ),
            interactions.Option(
                name='remove',
                description='Removes premium from a specific user',
                type=interactions.OptionType.SUB_COMMAND,
                options=[
                    interactions.Option(
                        name='user',
                        description='The user whom you want to remove premium from.',
                        type=interactions.OptionType.USER,
                        required=True
                    )
                ]
            )
        ]

)
async def premium(ctx: interactions.CommandContext, sub_command: str, user: interactions.Member):
    if ctx.user.id != 886873187965616158:
        await ctx.send('Sorry, you do not have the permissions to run this command.')
    if sub_command == 'give':
        if int(user.user.id) not in iohook.get_premium_users().get():
            iohook.get_premium_users().get().append(int(user.user.id))
            iohook.get_premium_users().save()
        await ctx.send(f'Successfully gave premium to {user.user.username}')
    if sub_command == 'remove':
        if int(user.user.id) in iohook.get_premium_users().get():
            iohook.get_premium_users().get().remove(int(user.user.id))
            iohook.get_premium_users().save()
        await ctx.send(f'Successfully removed premium from {user.user.username}')


@bot.command(
    name='help',
    description="Get help about how to use my commands."
)
async def help(ctx: interactions.CommandContext):
    page_1 = interactions.Embed(title='Help')
    page_1.description = '**You can use this bot for two main thing:**\n\
1. You can get the best pokemon coutner for any pokemon. Just use ```/raid meta {pokemon}``` \n\
2. You can search for on-going raids using `/raid search`. If you know of any private server keys, \
you can type that and view all the private servers also. The command is:```/raid search ```\n\
There are a lot of commands to set up your server. Shown in upcoming pages.\
'
    page_2 = interactions.Embed(title='Setting up your server for showing it in `/raid search`')
    page_2.description = "It is very simple. Just go to the server you want to make public and type `/server make_public`.\
Keep in mind that you need the ownership of the server.\
```What if I want to make it a private server only visible using a key?```\
Currently, only a selected few `Known as Premium members` Can create private server groups \
and add servers to those groups. \n\
This is to ensure that groups that are being made are accessible to at least 10 people.\
"
    page_3 = interactions.Embed(title='How to get premium and what can I do with it?')
    page_3.description = "Even though the name might sound like you need to pay for it. Premiumship of the bot is \
**Completely Free**. All you need to do is contact `@TheAgent#1542` and you will be granted premiumship if you intend on helping \
others. \
```What can I do with premium?```\
With premium you can create server groups, using `/group create {key}`. remember the key as you will use that to access \
all the servers in that group.\
```What do I do to add my server to that group?```\
After you have made the group, you can easily add a server to that group with `/group add {key}`\
Currently, a server can only be in one group at a time.\
You again need the ownership of the server to add it to the group."

    page_4 = interactions.Embed(title="How to hide my server again from `/raid search`")
    page_4.description = "It is very easy to hide a public server. Just use `/server remove_public` \
Again, you need ownership. This also works if the server is in a private group. It removes the \
server from that group. You can use this method to change the group of a server."

    page_5 = interactions.Embed(title='It all sounded like greek and latin')
    page_5.description = "Sorry to hear that, I am not a professional you see. \
Any doubts you have or any suggestions can be asked in the (Un)official server.\
Alternatively, you can DM me `@TheAgent#1542`. I will be more than happy to clarify \
doubts"

    await Paginator(client=bot, ctx=ctx, pages=[Page(embeds=page_1), Page(embeds=page_2), Page(embeds=page_3), Page(embeds=page_4), Page(embeds=page_5)]).run()

@bot.event(name='on_message_create')
async def on_message(message: interactions.Message):
    if message.author != "Pokémon":
        return
    if message.embeds == []:
        return
    
    if message.embeds[0].title == '⚔️ Raid Announcement ⚔️':
        try:
            raidsearch.add_raid(message=message)
        except Exception as e:
            print(e)
    elif message.embeds[0].title == "A wild pokémon has аppeаred!":
        try:
            embeds_ = await name_pokemon(image_url=message.embeds[0].url)
            channel = await message.get_channel()
            await channel.send(embeds=embeds_)
        except Exception as e:
            print(e)

bot.start()