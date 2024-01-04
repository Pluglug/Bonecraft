from abc import ABC, abstractmethod
import functools
import re


try:
    from .debug import log, DBG_RENAME
    from .naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
except:
    from debug import log, DBG_RENAME
    from naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    

# regex_utils

def capture_group(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        group = self.get_identifier()
        return f'(?P<{group}>{func(self, *args, **kwargs)})'
    return wrapper

def maybe_with_separator(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # エスケープした方が良いかも
        sep = f"(?:{self.get_separator()})?"
        order = self.get_order()
        result = func(self, *args, **kwargs)
        if result:
            if order == 1:
                return f'{result}{sep}'
            # elif order > 1:
            else:
                return f'{sep}{result}'
        else:
            return result
    return wrapper


class NamingElement(ABC):
    element_type = None
    _group_counter = 0

    def __init__(self, settings):
        self.apply_settings(settings)
        self.standby()

    @abstractmethod
    def build_pattern(self):
        """Each subclass should implement its own pattern building method."""
        pass

    def standby(self):
        self.value = None
        # self.start = None
        # self.end = None
        # self.remainder = None

    def search(self, name):
        if self.cache_invalidated:
            self.update_cache()
        match = self.compiled_pattern.search(name)
        return self.capture(match)
    
    def capture(self, mache):
        if mache:
            self.value = mache.group(self.identifier)
            # 将来必要になるかもしれないので残しておく
            # self.start = match.start(self.identifier)
            # self.end = match.end(self.identifier)
            # self.remainder = name[:match.start(self.identifier)] + name[match.end(self.identifier):]
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
        # return self.settings["separator_setttings"]["text_separator"]  # TODO: 各要素ごとに設定する
        return "_"

    def apply_settings(self, settings):
        self.cache_invalidated = True

        # identifierがまだない場合は生成する
        if not hasattr(self, 'identifier'):
            self.identifier = self.generate_identifier()  # TODO: 上位から与える nameが一意であることを保証する
        
        self.settings = settings
        self.order = settings.get('order', 0)
        self.name = settings.get('name', 'Element')
        self.enabled = settings.get('enabled', True)

    def invalidate_cache(self):
        self.cache_invalidated = True

    def update_cache(self):
        if self.cache_invalidated:
            self.compiled_pattern = re.compile(self.build_pattern())
            DBG_RENAME and log.info(f'update_cache: {self.identifier}: {self.compiled_pattern}')
            self.cache_invalidated = False

    @classmethod
    def generate_identifier(cls):  # TODO: initのたびに呼ばれるので、もっと良い方法を考える 上位から与える? new_elementの渡し方が難しくなるからnameを使う。設定で一意制を保証する
        # safe_name = re.sub(r'\W|^(?=\d)', '_', self.name).lower()  # さらに重複があった場合には、_1, _2, ... というようにする
        cls._group_counter += 1
        return f"{cls.element_type}_{cls._group_counter}"
    

class TextElement(NamingElement):
    element_type = "text"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get('items', [])

    @maybe_with_separator
    @capture_group
    def build_pattern(self):
        return '|'.join(self.items)
        

class CounterElement(NamingElement):
    element_type = "counter"
    
    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.digits = settings.get('digits', 2)

    @maybe_with_separator
    @capture_group
    def build_pattern(self):
        sep = re.escape(self.get_separator())
        return f'\\d{{{self.digits}}}(?=\D|$)'  # FIXME: bl_counterを拾ってしまう

    def get_separator(self):
        # return self.settings["separator_setttings"]["counter_separator"]
        return "-"
    # CounterElement に "." をセパレータとして設定しようとした場合に、
    # BlCounterElement との衝突が起こりうることを警告するポップアップを表示
    
    def get_value(self):
        return int(self.value) if self.value else None
    
    def get_string(self):
        return f'{self.value:0{self.digits}d}' if self.value else None
    

class PositionElement(NamingElement):
    element_type = "position"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get('items', [])
    
    def build_pattern(self):
        sep = re.escape(self.get_separator())
        pattern = '|'.join(self.items)

        if self.get_order() == 1:
            return f'(?P<{self.identifier}>{pattern}){sep}'
        # elif self.get_order() > 1:
        else:
            return f'{sep}(?P<{self.identifier}>{pattern})'

    def get_separator(self):
        # return self.settings["separator_setttings"]["position_separator"]
        return "."


class BlCounterElement(NamingElement):
    """ Buildin Blender counter pattern like ".001" """
    element_type = "bl_counter"

    def apply_settings(self, settings):
        # No settings for this element.
        self.cache_invalidated = True
        self.settings = settings

        self.identifier = 'bl_counter'
        self.order = -1
        self.name = 'bl_counter'
        self.enabled = False  # 名前の再構築時に無視されるようにする?
        self.digits = 3

    @capture_group
    def build_pattern(self):
        # I don't know of any other pattern than this. Please let me know if you do.
        sep = re.escape(self.get_separator())
        return f'{sep}\\d{{{self.digits}}}$'
    
    def standby(self):
        super().standby()
        self.start = None
        self.value_int = None

    def capture(self, match):
        if match:
            self.value = match.group(self.identifier)
            self.start = match.start(self.identifier)
            self.value_int = int(self.value[1:])
            return True
        return False

    def get_separator(self):
        return "."  # The blender counter is always "." .
    
    def get_value(self):
        return int(self.value[1:]) if self.value else None  # .001 -> 001

    def except_bl_counter(self, name):
        """Return the name without the bl_counter and the bl_counter value."""
        if self.search(name):
            return name[:self.start], int(self.value[1:])
        else:
            return name, None


class NamingElements:
    def __init__(self, obj_type, settings):
        # 将来、typeで何をビルドするか指示される。mesh, material, bone, etc...
        self.elements = self.build_elements(settings)

    def build_elements(self, settings):
        elements = []
        for element_settings in settings["elements"]:
            element_type = element_settings["type"]
            element = self.create_element(element_type, element_settings)
            elements.append(element)
            
        elements.append(BlCounterElement({}))  # これはハードコードで良い
        elements.sort(key=lambda e: e.get_order())
        return elements
    
    def get_element_classes(self):
        element_classes = {}  # 再利用する場合はキャッシュ
        subclasses = NamingElement.__subclasses__()
        for subclass in subclasses:
            element_type = getattr(subclass, 'element_type', None)
            if element_type:
                element_classes[element_type] = subclass
        return element_classes

    def create_element(self, element_type, settings):
        element_classes = self.get_element_classes()
        element_class = element_classes.get(element_type, None)
        if element_class:
            return element_class(settings)
        else:
            raise ValueError(f"Unknown element type: {element_type}")
    
    def search_elements(self, name):
        for element in self.elements:
            element.standby()
            element.search(name)
    
    def update_elements(self, new_elements=None):  # TODO: new_elementsの指定方法を再考する
        e = {}
        for element in self.elements:
            # 新しい要素を受け取った場合
            if new_elements and element.identifier in new_elements:
                if new_elements[element.identifier] != "":
                    e[element.identifier] = new_elements[element.identifier]
                else:
                    # 新しい要素が空の場合
                    e[element.identifier] = None
            # 新しい要素がない場合
            elif self.elements[element]:
                e[element.identifier] = self.elements[element]
            # 新しい要素がなく、既存の要素もない場合
            else:
                e[element.identifier] = None
        
        for element in self.elements:
            self.elements[element] = e[element.identifier]
    
    def render_name(self):
        elements_parts = [element.render() for element in self.elements \
                          if element.is_enabled() and element.value]
        name_parts = []
        for sep, value in elements_parts:
            if name_parts:
                name_parts.append(sep)
            name_parts.append(value)
        return ''.join(name_parts)

    def chenge_all_settings(self, new_settings):
        for element in self.elements:
            element.change_settings(new_settings)

    def update_caches(self):
        for element in self.elements:
            if element.cache_invalidated:
                element.update_cache()
    
    def print_elements(self, name):
        self.search_elements(name)
        for element in self.elements:
            log.info(f"{element.identifier}: {element.value}")


if __name__ == "__main__":
    log.header("Test")
    es = NamingElements("オブジェクトタイプなど", rename_settings)
    # es.print_elements("CTRL_Root-05.L.001")
    # es.search_elements("CTRL_Root-05.L.001")
    # name = es.render_name()
    # log.info(name)
    from naming_test_utils import rename_preset
    test_names = random_test_names(rename_preset, 5)  # TODO: test_utilsを作り直す

    for name in test_names:
        es.search_elements(name)
        log.info(f"{name} -> {es.render_name()}")
    