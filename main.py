import interactions
import utils
import raids
import name_pokemon


with open('token') as token:
    token = str(token.read())

intents = interactions.Intents.ALL

bot = interactions.Client(token="OTcxMzQyNzEwNzI2MzQ4ODEw.G3Fg_k.h8XCYekp1JGZt-moiJ4VWwaYMF0Hlko2GNJKb4",
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

        # # Raid search
        # interactions.Option(
        #     name="search",
        #     description="Show all the on-going raids!",
        #     type=interactions.OptionType.SUB_COMMAND,
        # ),
        # # Raid joins
        # interactions.Option(
        #     name="server_join",
        #     description="Show all the on-going raids!",
        #     type=interactions.OptionType.SUB_COMMAND,
        #     options=[
        #         interactions.Option(
        #             name='raid_id',
        #             description='The ID of the raid you want to join.',
        #             type=interactions.OptionType.INTEGER,
        #             required=True
        #         )
        #     ]
        # ),
    ],
)
async def cmd(ctx: interactions.CommandContext, sub_command: str, pokemon: str = "", raid_id: int = 0):
    if sub_command == "meta":
        await ctx.send(embeds=await utils.get_raid_pokemon(ctx, pokemon))
    elif sub_command == "help":
        await ctx.send(embeds=utils.raid_help())
    # elif sub_command == 'search':
    #     await ctx.send(embeds=await utils.search_raids(ctx, bot))
    # elif sub_command == 'server_join':
    #     await ctx.send(await utils.get_server_link(bot=bot, id_=raid_id, ctx=ctx), ephemeral=True)


@bot.event(name='on_message_create')
async def on_message(message: interactions.message.Message):
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


@bot.event
async def on_ready():
    utils.init_files()
    raids.init_files()
    name_pokemon.init_files()
    print('ready!')


bot.start()