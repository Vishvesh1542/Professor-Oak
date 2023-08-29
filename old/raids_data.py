from datetime import datetime
import time

class Raid:
    current_raids = {}
    def __init__(self):
        self.current_raids = {}
        print('(Re)loaded raid data files')


    def add_raid(self, raid_boss: str, guild: int, timestamp: int, time_left: int, stars: str, id_: str):
        if str(guild) not in self.current_raids:
            self.current_raids[str(guild)] = {}
        time_ = datetime.fromisoformat(timestamp).timestamp()
        self.current_raids[str(guild)] = {'boss': raid_boss, 'start_time': time_, 'time_left': time_left, 'stars': stars, 'id': id_}


    def update(self):
        new_dict = {}
        for server, lst in list(self.current_raids.items()):
            if time.time() - lst[1] <= lst[2]:
                new_dict[server] = lst
        self.current_raids = new_dict.copy()

    def get(self):
        return self.current_raids