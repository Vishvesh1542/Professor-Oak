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
        # self.add_application_command(self.test)

    async def on_ready(self):
        print(' [ INFO ]'.ljust(15) + f'Logged in as {self.user}')

    async def on_guild_join(self, guild):
        print(guild.owner_id)
        owner = await self.fetch_user(guild.owner_id)
        await owner.send("\
Privacy Policy for Professor Oak\n\
\n\
1. Data Collection\n\
\n\
We want to assure you that Professor Oak does not collect or store any sensitive or personal information from users. We respect your privacy and prioritize the protection of your data.\n\
\n\
2. Server Data\n\
\n\
Our bot may collect and store server-specific data to provide its intended services, such as server id. However, this data is not linked to any individual user and is solely used for the bot's functionality within the server.\n\
\n\
3. Sensitive Information\
\n\
We do not request, access, or store sensitive information, including but not limited to personal identification data, passwords, or payment information. We have no access to private messages or conversations.\n\
\n\
4. Data Security\
\n\
The security of your data is essential to us. We have implemented measures to safeguard any server data stored by our bot. However, please be aware that no online service can guarantee absolute security.\n\
\n\
5. Contact Information\n\
\n\
If you have any questions or concerns regarding our bot's privacy policy, please don't hesitate to contact me at known_as_agent.\n\
\n\
By using our Discord bot, you agree to the terms outlined in this privacy policy.\n\
")

    async def on_message(self, message):
        if message.author == self.user:
            return

        await self.commands_manager.process_message(message)

    # @commands.slash_command(
    #     name='test',
    #     description='If u can see this u are hacking'
    # )
    # async def test(ctx):
    #     embed = discord.Embed(title='⚔️ Raid Announcement ⚔️')
    #     embed.description = 'Hello trainers ! A new raid will start in 1 hour. Here are the details about the raid.\n\
    # **Raid Boss :** ?\n \
    # **Raid Stars :** ⭐⭐\n\
    # **Start Time :** <t:1683041467:f> UTC'
    #     embed.set_image(url='https://images.pokemonbot.com/assets/raid_eggs/2.png')
    #     await ctx.send(embeds=[embed,])
    

with open('token') as f:
    token = f.read()
print(' [ INFO ] '.ljust(15) + token)
user_handler.load()
raids.load()
help.load()
raid_searches.init()


ProfessorOak(intents=intents).run(token)
