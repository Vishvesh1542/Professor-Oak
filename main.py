import interactions
import raids

token = "MTEwNTg2NzQ4NTkwNDkxNjUxMA.GeVGBd.EIqurAJanZJM9pAQGQPIXXZj700O6Lx3kvJxO0"

bot = interactions.Client(token=token, intents=interactions.Intents.ALL)

@bot.event
async def on_ready():
    global raidmeta
    raidmeta = raids.RaidMeta()

    print('ready')


# Test command
command_help = interactions.Option(
    name='help',
    description='Get help about how to use my raid commands!',
    type=interactions.OptionType.SUB_COMMAND
)
command_meta = interactions.Option(
    name='meta',
    description="Use Professor Oak's experience get the best counters to any Pokémon!",
    type=interactions.OptionType.SUB_COMMAND,
    options=[
        interactions.Option(
            name='pokemon',
            description='The Pokémon whose raid counters you want to get.'
            type=interactions.OptionType.STRING
                )
    ]
)
subcommands = [
command_help,
command_meta
]
@bot.command(
        name='raid', description='If you see this you are hacking', scope=1084731374344359966,
        options=subcommands)
async def raid(ctx: interactions.CommandContext, sub_command: str, pokemon: str):
    if sub_command == 'help':
        await ctx.send(embeds=await raidmeta.get_raid_message())
    elif sub_command == 'meta':
        await ctx.send(embeds=await raidmeta.meta(pokemon))



bot.start()