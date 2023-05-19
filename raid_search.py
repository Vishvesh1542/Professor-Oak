import interactions
import time
from datetime import datetime
import iohook

class Raid:
    bot = None

    server_id = None
    raid_boss = None
    raid_stars = None
    # The time the message was sent on ( time.time())
    message_time = None
    # The time mentioned on the message ( 5 mins left...)
    time_left = None
    group = None
    raid_id = None
    
    def __init__(self, server_id: int, raid_boss: str, raid_stars: int, message_time: int, time_left: int,
                  group: str | None, raid_id: int | str) -> None:
        self.server_id = server_id
        self.raid_boss = raid_boss
        self.raid_stars = raid_stars
        self.message_time = message_time
        self.time_left = time_left
        self.group = group
        self.raid_id = str(raid_id)

    def get_time_left(self) -> int:
        time_left = self.message_time + self.time_left - time.time() 
        return time_left
    
    def get_time_left_string(self) -> str:
        time_left = self.get_time_left()
        m, s = divmod(time_left, 60)
        h, m = divmod(m, 60)

        return f'{int(h)}:{int(m)}:{int(s)}'


class RaidSearcher:
    current_raids = []
    def __init__(self, bot: interactions.Client) -> None:
        self.bot = bot

    def add_raid(self, message: interactions.Message):
        public_servers = iohook.get_public_servers().get()
        if message.guild_id in public_servers:
            embed = message.embeds
            description = embed[0].description
            
            raid_boss = description.split('**Raid Boss :**')[1].split('\n')[0].strip()
            stars = description.split('**Raid Stars :**')[1].split('\n')[0].strip()
            time_until_raid = description.split('A new raid will start in')[1].split('.')[0].strip()
            raid_id = '-'

            if 'Raid ID' in description:
                raid_id = description.split('**Raid ID :**')[1].split('\n')[0].strip()

            time_left = 0

            if time_until_raid == '1 hour':
                time_left = 4500
            elif time_until_raid == '15 minutes':
                time_left = 900
            elif time_until_raid == '10 minutes':
                time_left = 600
            elif time_until_raid == '5 minutes':
                time_left = 300
            time_ = datetime.fromisoformat(str(message.timestamp)).timestamp()
            self.current_raids.append(Raid(raid_boss=raid_boss, raid_id=raid_id, server_id=message.guild_id, raid_stars=len(stars),\
                                           time_left=time_left, message_time=time_, group=public_servers[message.guild_id]))
            
    def get_raids(self, group) -> list:
        _list = [x for x in self.current_raids if x.get_time_left() >= 0 and x.group == group]        
        return _list
    
       
    async def get_invite_link(self, raid_id) -> str:
        for i in list(self.current_raids):
            if i.raid_id != '-':
                if int(i.raid_id) == int(raid_id):
                    server_id = i.server_id
                    break
        else:
            return f'Sorry, the raid with id {raid_id} does not exist'

        guild = await self.bot._http.get_guild(server_id)
        invite_arguments = {
            'max_age': 120,
            'max_uses': 1,
            'temporary': True,
        }

        first_channel_id = guild['system_channel_id']
        try:
            invite_link = await self.bot._http.create_channel_invite(first_channel_id, payload=invite_arguments)
            return f"https://discord.com/invite/{invite_link['code']}"

        except:
            owner_id = guild['owner_id']
            owner = await self.bot._http.get_user(int(owner_id))
            return f"Sorry, I do not have the required permissions in that server to create an invite link :( \n\
This server is owned by `@{owner['username']}#{owner['discriminator']}`. Please contact him/her. \n\
Also while you are at it, ask him to give me permission to invite so that others don't have to do this again. Thanks!".strip()