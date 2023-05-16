import interactions
from interactions.ext.paginator import Paginator
import raids
import iohook
import raid_search

token = "MTEwNTg2NzQ4NTkwNDkxNjUxMA.GeVGBd.EIqurAJanZJM9pAQGQPIXXZj700O6Lx3kvJxO0"

bot = interactions.Client(token=token, intents=interactions.Intents.ALL)

@bot.event
async def on_ready():
    global raidmeta, raidsearch
    raidmeta = raids.RaidMeta()
    raidsearch = raid_search.RaidSearcher(bot=bot)
    iohook.init()

    print('ready')
# very important changes
# Test command
command_help = interactions.Option(
    name='help',
    description='Get help about how to use my raid commands!',
    type=interactions.OptionType.SUB_COMMAND
)
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
command_help,
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
        embeds, pages = await raidmeta.meta(pokemon=pokemon)
        if embeds:
            await ctx.send(embeds=embeds)
        else:
            await   Paginator(client=bot, ctx=ctx, pages=pages, disable_after_timeout=True, use_select=False).run()
    elif sub_command == 'search':
        list_ = raidsearch.get_raids(group)
        embeds = interactions.Embed(title='Current Raids')
        try:
            max_ = max([len(x.raid_boss) for x in list_])
        except ValueError:
            max_ = 0
        for item in list_:
            stars = ''.join(['⭐' for _ in range(item.raid_stars)])
            embeds.add_field(name=f'{item.raid_boss.ljust(max_)} | id: `{item.raid_id}`', value=f'```{stars.ljust(5)} | Time left: {item.get_time_left_string()}```')
        
        await ctx.send(embeds=embeds)

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
        server_ = await raidsearch.get_invite_link(raid_id=server_id)
        await ctx.send(server_, ephemeral=True)

@bot.command(
    name='group',
    description='If u can see this u are hacking',
    scope=1084731374344359966,
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
        iohook.get_public_servers().get().pop(str(ctx.guild_id))
        iohook.get_public_servers().save()
        await ctx.send(f'Successfully removed this server from groups')
    
@bot.event(name='on_message_create')
async def on_message(message: interactions.Message):
    # if message.author != "Pokémon":
    #     return
    if message.embeds == []:
        return
    
    if message.embeds[0].title == '⚔️ Raid Announcement ⚔️':
        raidsearch.add_raid(message=message)

@bot.command(
    name='test',
    description='If u can see this u are hacking',
    scope=1084731374344359966,
)
async def test(ctx: interactions.CommandContext):
    embed = interactions.Embed(title='⚔️ Raid Announcement ⚔️')
    embed.description = 'Hello trainers ! A new raid will start in 1 hour. Here are the details about the raid.\n\
**Raid Boss :** Professor Oak\n \
**Raid Stars :** ⭐⭐\n\
**Start Time :** <t:1683041467:f> UTC'
    embed.set_image(url='https://static.fandomspot.com/images/12/10751/06-professor-oak-pokemon-anime.jpg')
    await ctx.send(embeds=embed)


bot.start()