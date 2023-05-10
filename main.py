import interactions

token = "MTEwNTg2NzQ4NTkwNDkxNjUxMA.GeVGBd.EIqurAJanZJM9pAQGQPIXXZj700O6Lx3kvJxO0"

bot = interactions.Client(token=token, intents=interactions.Intents.ALL)

# Test command
@bot.command(name='test', description='None', scope=1084731374344359966)
async def test(ctx: interactions.CommandContext):
    print('test')



bot.start(token=token)