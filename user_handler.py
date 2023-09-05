import json

def load() -> None:
    with open(r'data/users.json', 'r') as file:
        global users
        users = json.load(file)

    print(' [ INFO ]'.ljust(15) + 'Loaded user data.')

    with open(r'data/groups.json', 'r') as file:
        global groups
        groups = json.load(file)
    print(' [ INFO ]'.ljust(15) + 'Loaded groups data.')

def sync():
    with open(r'data/users.json', 'w') as file:
        json.dump(users, file)

    with open(r'data/groups.json', 'w') as file:
        json.dump(groups, file)

def add_user(name: str, user_id: int, type_: str, credits: int):
    if str(user_id) in users.keys():
        return None
    users[str(user_id)] = {'name': name, 'type': type_, 'credits': credits, 'servers': {}}
    sync()
    return True

def set_type(user_id, type_: str):
    if str(user_id) not in users:
        return False
    users[str(user_id)]['type'] = type_
    sync()
    return True

def get_servers(user = None):
    if user:
        raise NotImplementedError('Lazy implement this')
    
    server_list = [key for user in users for key in user['servers']]
    return server_list

def add_server(user_id: int, server_id):
    if str(user_id) not in users:
        return False
    users[str(user_id)]['servers'][str(server_id)] = {'group': None}
    print(users[str(user_id)]['servers'])
    sync()
    return True

def remove_server(user_id: int, server_id: int):
    if str(user_id) not in users:
        return False
    try:
        users[str(user_id)]['servers'].pop(str(server_id))
    except KeyError:
        return 404
    print(users[str(user_id)]['servers'])
    sync()
    return True

def set_group(guild_id: int, group: str):
    if group not in [x[0] for x in groups]:
        return False
    for user, u in users.items():
        if str(guild_id) not in u['servers']:
            continue
        else:
            users[user]['servers'][str(guild_id)]['group'] = group
            sync()
            return True
    return 404

def add_group(group_name: str, creator_id: int):
    if group_name in [x[0] for x in groups]:
        return False

    groups.append((group_name, creator_id))
    sync()
    return True

def get_group(guild_id: int) -> str | None:
    servers = [x['servers'] for x in users.values()]

    if all(item == {} for item in servers):
        return 404

    print(servers)
    for server in servers:
        if not server:
            continue

        elif list(server.keys())[0] == str(guild_id):
            pass
            return server[str(guild_id)]['group']
    print(404)
    return 404

def get_user(user_id: int):
    if str(user_id) not in users.keys():
        return None
    else:
        return users[str(user_id)]

def use_credits(user_id: int, credits: int = 1):
    if str(user_id) not in users.keys():
        return None
    user_id = str(user_id)
    if users[user_id]['credits'] - credits < 0:
        return False
    users[user_id]['credits'] -= credits
    return True