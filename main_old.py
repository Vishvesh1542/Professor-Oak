import interactions
import utils
import raids
import name_pokemon


bot = interactions.Client(token="token",
                          intents=interactions.Intents.ALL)


@bot.command(
    name="raid",
    description="All the commands about raids",
    options=[
        # Raid meta
        interactions.Option(
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
        ),

        # Raid help
        interactions.Option(
            name="help",
            description="Get help about how to use the raid calculation feature.",
            type=interactions.OptionType.SUB_COMMAND,
        ),

        # Raid search
        interactions.Option(
            name="search",
            description="Show all the on-going raids!",
            type=interactions.OptionType.SUB_COMMAND,
        ),
        # Raid joins
        interactions.Option(
            name="server_join",
            description="Show all the on-going raids!",
            type=interactions.OptionType.SUB_COMMAND,
            options=[
                interactions.Option(
                    name='raid_id',
                    description='The ID of the raid you want to join.',
                    type=interactions.OptionType.INTEGER,
                    required=True
                )
            ]
        ),
    ],
)
async def cmd(ctx: interactions.CommandContext, sub_command: str, pokemon: str = "", raid_id: int = 0):
    if sub_command == "meta":
        await ctx.send(embeds=await utils.get_raid_pokemon(ctx, pokemon))
    elif sub_command == "help":
        await ctx.send(embeds=utils.raid_help())
    elif sub_command == 'search':
        await ctx.send(embeds=await utils.search_raids(ctx, bot))
    elif sub_command == 'server_join':
        await ctx.send(await utils.get_server_link(bot=bot, id_=raid_id, ctx=ctx), ephemeral=True)
        

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



@bot.event(name='on_message_create')
async def on_message(message: interactions.Message):
    await utils.process_message(bot, message)


@bot.command(
    name='toggle',
    description='If u can see this u are hacking',
    options=[
        interactions.Option(
                name='raidpublic',
                description='Toggles if this server can be viewed by typeing /raid search',
                type=interactions.OptionType.SUB_COMMAND
        )
    ]
)
async def toggle(ctx: interactions.CommandContext, sub_command=str):
    await ctx.send(await utils.toggle_public_server(ctx=ctx, bot=bot))

# just teaching raxton 
@bot.event
async def on_ready():
    utils.init_files()
    raids.init_files()
    name_pokemon.init_files()
    print('ready!')


bot.start()
