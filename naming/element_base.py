from abc import ABC, abstractmethod
import re

try:
    from .debug import log, DBG_RENAME
    from .operators.mixin_utils import ArmModeMixin
    from .naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    from .regex_utils import capture_group, maybe_with_separator
except:  # Running Test in VSCode
    from debug import log, DBG_RENAME
    from operators.mixin_utils import ArmModeMixin
    from naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    from regex_utils import capture_group, maybe_with_separator


class NamingElement(ABC):
    element_type = None
    _group_counter = 0

    def __init__(self, settings):
        self.apply_settings(settings)
        self.standby()
        DBG_RENAME and log.info(f'init: {self.name}')

    @abstractmethod  # 抽象メソッドとインスタンスメソッドの混在はよろしくない?
    def build_pattern(self):
        """Each subclass should implement its own pattern building method."""
        pass

    def standby(self):
        self.value: str = None # TODO: name_elementとかにする
        # self.start = None
        # self.end = None
        # self.remainder = None

    def search(self, target_string):
        if self.cache_invalidated:
            self.update_cache()
        match = self.compiled_pattern.search(target_string)
        return self.capture(match)
    
    def capture(self, match):
        if match:
            self.value = match.group(self.name)
            # 将来必要になるかもしれないので残しておく
            # self.start = match.start(self.identifier)
            # self.end = match.end(self.identifier)
            # self.remainder = name[:match.start(self.identifier)] + name[match.end(self.identifier):]
            # self.forward = name[match.end(self.identifier):]
            # self.backward = name[:match.start(self.identifier)]
            return True
        return False
    
    def render(self):
        return self.get_separator(), self.value

    def get_identifier(self):
        return self.identifier

    def get_order(self):
        return self.order

    def is_enabled(self):
        return self.enabled

    def get_separator(self):
        return self.separator

    def apply_settings(self, settings):
        self.cache_invalidated = True

        if not hasattr(self, 'identifier'):
            self.identifier = self.generate_identifier()  # TODO: 削除
        
        self.settings = settings
        self.order = settings.get('order', 0)
        self.name = settings.get('name', self.identifier)
        self.enabled = settings.get('enabled', True)
        self.separator = settings.get('separator', "_")

    def invalidate_cache(self):
        self.cache_invalidated = True

    def update_cache(self):
        if self.cache_invalidated:
            self.compiled_pattern = re.compile(self.build_pattern())
            DBG_RENAME and log.info(f'  update_cache: {self.identifier}: {self.compiled_pattern}')
            self.cache_invalidated = False

    @classmethod
    def generate_identifier(cls):  # TODO: initのたびに呼ばれるので、もっと良い方法を考える 上位から与える? new_elementの渡し方が難しくなるからnameを使う。設定で一意制を保証する
        # safe_name = re.sub(r'\W|^(?=\d)', '_', self.name).lower()  # さらに重複があった場合には、_1, _2, ... というようにする
        cls._group_counter += 1
        return f"{cls.element_type}_{cls._group_counter}"
    
    # new_elementsを作るための便利メソッドが欲しい
