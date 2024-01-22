from abc import ABC, abstractmethod
import re

try: # Running in Blender
    from ..debug import log, DBG_RENAME
    from . naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    from . regex_utils import capture_group, maybe_with_separator
except:  # Running Test in VSCode
    from debug import log, DBG_RENAME
    from naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    from regex_utils import capture_group, maybe_with_separator


class NamingElement(ABC):
    element_type = None
    _group_counter = 0  # TODO: 削除

    def __init__(self, settings):
        self.apply_settings(settings)
        self.standby()
        DBG_RENAME and log.info(f'init: {self.id}')

    @abstractmethod
    def build_pattern(self):
        """Each subclass should implement its own pattern building method."""
        pass

    def standby(self):
        self._value: str = None

    def search(self, target_string):
        if self.cache_invalidated:
            self.update_cache()
        match = self.compiled_pattern.search(target_string)
        return self.capture(match)
    
    def capture(self, match):
        if match:
            self.value = match.group(self.id)
            # 将来必要になるかもしれないので残しておく
            # self.start = match.start(self.id)
            # self.end = match.end(self.id)
            # self.forward = match.string[:self.start]
            # self.backward = match.string[self.end:]
            # self.remainder = self.forward + self.backward
            return True
        return False

    def update(self, new_string):
        self.search(new_string)
    
    def render(self):
        if self.enabled and self.value:
            return self.separator, self.value

    @property
    def value(self) -> str:
        return self._value
    
    @value.setter
    def value(self, new_value):
        if new_value is not None:
            try:
                self._value = str(new_value)
            except ValueError:
                log.error(f"Value '{new_value}' cannot be converted to string.")
        else:
            self._value = None

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        log.warning("name has been deprecated. Use id instead.")
        return self.id

    @property
    def order(self):
        return self._order

    @property
    def enabled(self):
        return self._enabled

    @property
    def separator(self):
        return self._separator

    def apply_settings(self, settings):
        self.cache_invalidated = True
        
        self._id = settings.get('name', self.generate_identifier())
        self._order = settings.get('order', 0)
        self._enabled = settings.get('enabled', True)
        self._separator = settings.get('separator', "_")

    def invalidate_cache(self):
        self.cache_invalidated = True

    def update_cache(self):
        if self.cache_invalidated:
            self.compiled_pattern = re.compile(self.build_pattern())
            DBG_RENAME and log.info(f'  update_cache: {self.id}: {self.compiled_pattern}')
            self.cache_invalidated = False

    @classmethod
    def generate_identifier(cls):
        # safe_name = re.sub(r'\W|^(?=\d)', '_', self.id).lower()  # さらに重複があった場合には、_1, _2, ... というようにする
        cls._group_counter += 1
        return f"{cls.element_type}_{cls._group_counter}"
    
    @abstractmethod
    def test_random_output(self):
        pass
    
    # new_elementsを作るための便利メソッドが欲しい
