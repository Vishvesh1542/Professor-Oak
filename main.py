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

    async def on_ready(self):
        user_handler.load()
        raids.load()
        help.load()
        raid_searches.init()
        print(' [ INFO ]'.ljust(15) + f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        await self.commands_manager.process_message(message)

with open('token') as f:
    token = f.read()
print(' [ INFO ] '.ljust(15) + token)
ProfessorOak(intents=intents).run(token)
