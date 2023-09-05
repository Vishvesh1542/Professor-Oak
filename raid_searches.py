import time

def init() -> None:
    global raids
    raids = {}
    print(' [ INFO ]'.ljust(15) + 'Loaded raid_search')

def add_raid(server: int | str, start_time: str, boss: str, stars: str,
             group: None | str = None, raid_id: int = 0):
    raids[str(server)] = {'group': group, 'start_time': start_time + 10,
                          'boss': boss, 'stars': stars, 'raid_id': raid_id}

async def get_raids(group: str = None) -> list:
    current_raids = []
    pop_items = []
    for server_id, info in raids.items():
        if info['start_time'] - time.time() > 0:
            if group == info['group']:
                current_raids.append({'info': info, 'id': server_id})
        else:
            pop_items.append(server_id)
    for i in pop_items:
        raids.pop(i)
    print(' [ INFO ]'.ljust(15) + current_raids)
    return current_raids

async def from_id(group_id: int):
    for server_id, info in raids.items():
        if info['raid_id'] == str(group_id):
            return server_id
    return None