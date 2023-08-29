import json

def load() -> None:
    with open(r'data/users.json', 'r') as file:
        global users
        users = json.load(file)

    print(' [ INFO ]'.ljust(15) + 'Loaded user data.')

def sync():
    with open(r'data/users.json', 'w') as file:
        json.dump(users, file)

def add_user(name: str, user_id: int, type_: str, credits: int):
    if str(user_id) in users.keys():
        return None
    users[str(user_id)] = {'name': name, 'type': type_, 'credits': credits, 'servers': {}}
    sync()
    return True

def get_servers(user = None):
    if user:
        raise NotImplementedError('Lazy implement this')
        return
    
    server_list = [key for user in users for key in user['servers']]
    return server_list

def get_group(guild_id: int) -> str | None:
    return next((data['server'][guild_id]['group'] for user, data
                   in users.items() if guild_id in data['servers']), None)

def get_user(user_id: int):
    if user_id not in users.keys():
        return None
    else:
        return int(users[user_id])

def use_credits(user_id: int, credits: int = 1):
    if user_id not in users.keys():
        return None
    user_id = str(user_id)
    if users[user_id]['credits'] - credits < 0:
        return False
    users[user_id]['credits'] -= credits
    return True