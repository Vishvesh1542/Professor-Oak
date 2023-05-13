import interactions
from interactions.ext.paginator import Paginator
import raids
import iohook
import raid_search

token = "_secret_   "

bot = interactions.Client(token=token, intents=interactions.Intents.ALL)

@bot.event
async def on_ready():
    global raidmeta, raidsearch
    raidmeta = raids.RaidMeta()
    raidsearch = raid_search.RaidSearcher(bot=bot)
    iohook.init()

    print('ready')


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
        name='raid', description='If you see this you are hacking', scope=1084731374344359966,
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
        embeds = interactions.Embed(title='Something went wrong.')

        for item in list_:
            embeds.add_field(name=item.raid_boss, value=str(item.get_time_left()))
        
        await ctx.send(embeds=embeds)


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
**Raid Boss :** ?\n \
**Raid Stars :** ⭐⭐\n\
**Start Time :** <t:1683041467:f> UTC'
    embed.set_image(url='https://images.pokemonbot.com/assets/raid_eggs/2.png')
    await ctx.send(embeds=embed)


bot.start()