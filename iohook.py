import json
import os


class IOHOOK:
    _dict = None
    _list = None


    def __init__(self, filename: str) -> None:
        with open(filename, 'r') as file:
            json_file = json.load(file)
        self.filename = filename
        if type(json_file) is dict:
            self._dict = json_file
        elif type(json_file) is list:
            self._list = json_file

        file_name=filename.split('/')[-1]
        f_name_dict = file_name.split('.')[:-1]
        string = ''
        for name in f_name_dict:
            string += name
        print(f'Loaded {string}')
    
    def get(self) -> dict | list:
        if self._dict is not None:
            return self._dict
        return self._list
    
    def get_value(self, key: str):
        if self._dict is None:
            raise TypeError('This file is not of type dictionary.')
        
        try:
            return self._dict[key]
        except KeyError:
            raise KeyError(f'Dictionary does not contain key "{key}".')
        
    def get_index(self, index: int):
        if self._list is None:
            raise TypeError('This file is not of type list.')

        if index is not int:
            raise TypeError(f'Only accept integers as indexex. (got {index})')

        try:
            return self._list[index]
        except IndexError:
            raise IndexError(f'The list index "{index}" is out of range.')

    def save(self):
        with open(self.filename, 'w') as file:
            if self._dict is not None:
                json.dump(self._dict, file)
                return
            json.dump(self._list, file)

def init():
    global pokemon, raid_pokemon
    pokemon = IOHOOK(os.getcwd() + '/data/pokemon_dict.json')
    raid_pokemon = IOHOOK(os.getcwd() + '/data/raid_pokemon_dict.json')

def get_pokemon() -> dict:
    return pokemon

def get_raid_pokemon() -> list:
    return raid_pokemon