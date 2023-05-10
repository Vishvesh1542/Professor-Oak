import json

class IOHOOK:
    _dict = None
    _list = None


    def __init__(self, filename: str) -> None:
        with open(filename, 'r') as file:
            json_file = json.load(file)
        
        if json_file is dict:
            self._dict = json_file
        elif json_file is list:
            self._list = json_file
    
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
