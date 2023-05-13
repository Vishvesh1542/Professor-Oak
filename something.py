import json
import os

with open(os.getcwd() + '/data/raid_pokemon') as file:
    list_ = eval(file.read())



with open(os.getcwd() + '/data/raid_pokemon_dict.json', 'w') as file:
    json.dump(list_, file, indent=1)