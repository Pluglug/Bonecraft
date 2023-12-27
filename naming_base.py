from abc import ABC, abstractmethod
import re

from debug import log
from naming_test_utils import (rename_preset, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )


class NamingElement(ABC):
    def __init__(self, settings):
        self.settings = settings
    
    @abstractmethod
    def build_pattern(self):
        pass

    @abstractmethod
    def search(self, name):
        pass

    @abstractmethod
    def rebuild(self, elements, new_value=None):
        pass


class PrefixElement(NamingElement):
    def __init__(self, settings):
        super().__init__(settings)
        self.pattern = self.build_pattern()

    def build_pattern(self):
        prefix_pattern = '|'.join(self.settings['prefixes'])
        return f'(?P<prefix>{prefix_pattern}){self.settings["common_separator"]}'  

    def search(self, name):
        regex = re.compile(self.pattern)
        match = regex.search(name)
        if match:
            return {
                'value': match.group('prefix'),
            }
        else:
            return None
    
    def rebuild(self, elements, new_value=None):
        if new_value:
            return new_value
        elif elements['prefix']:
            return elements['prefix']['value']
        else:
            return None


class BoneData:
    def __init__(self, **kwargs):
        self.attributes = kwargs

    # def get(self, key, default=None):
    #     return self.attributes.get(key, default)

    # def set(self, key, value):
    #     self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value
    
    def __delitem__(self, key):
        del self.attributes[key]

    def __contains__(self, key):
        return key in self.attributes

    def keys(self):
        return self.attributes.keys()
    
    def values(self):
        return self.attributes.values()
    
    def items(self):
        return self.attributes.items()
    
    def __getattr__(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            raise AttributeError(f'{name} is not defined')

    def __setattr__(self, name, value):
        if name == 'attributes':
            super().__setattr__(name, value)
        else:
            self.attributes[name] = value
    
    def __repr__(self):
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.attributes.items())
        return f'{self.__class__.__name__}({attrs})'
    