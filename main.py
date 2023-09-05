import discord
from command_handler import CommandHandler
from discord.ext import commands
import user_handler
import raids
import raid_searches
import help

intents = discord.Intents.default()
intents.message_content = True

class ProfessorOak(discord.Bot):
    def __init__(self, description=None, *args, **options):
        super().__init__(description, *args, **options)
        self.commands_manager = CommandHandler(self)
        self.add_application_command(self.test)

    async def on_ready(self):
        print(' [ INFO ]'.ljust(15) + f'Logged in as {self.user}')

    async def on_message(self, message):
        # if message.author == self.user:
        #     return

        await self.commands_manager.process_message(message)

    @commands.slash_command(
        name='test',
        description='If u can see this u are hacking'
    )
    async def test(ctx):
        embed = discord.Embed(title='⚔️ Raid Announcement ⚔️')
        embed.description = 'Hello trainers ! A new raid will start in 1 hour. Here are the details about the raid.\n\
    **Raid Boss :** ?\n \
    **Raid Stars :** ⭐⭐\n\
    **Start Time :** <t:1683041467:f> UTC'
        embed.set_image(url='https://images.pokemonbot.com/assets/raid_eggs/2.png')
        await ctx.send(embeds=[embed,])
    

with open('token') as f:
    token = f.read()
print(' [ INFO ] '.ljust(15) + token)
user_handler.load()
raids.load()
help.load()
raid_searches.init()


ProfessorOak(intents=intents).run(token)
