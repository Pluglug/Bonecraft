from abc import ABC, abstractmethod
import re
import functools

from debug import log, DBG_RENAME
from naming_test_utils import (rename_preset, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )


# regex_utils

def capture_group(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        group = self.element_type
        return f'(?P<{group}>{func(self, *args, **kwargs)})'
    return wrapper

def maybe_with_separator(position="prefix"):
    """position: "prefix", "suffix", "both", "none" """
    def _maybe_with_separator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            sep = self.common_separator()
            sep = f"(?:{sep})?"
            result = func(self, *args, **kwargs)
            if result:
                if position == "prefix":
                    return f'{sep}{result}'
                elif position == "suffix":
                    return f'{result}{sep}'
                elif position == "both":
                    return f'{sep}{result}{sep}'
                else:
                    return result
            else:
                return result
        return wrapper
    return _maybe_with_separator


class NamingElement(ABC):
    element_type = None
    use_common_separator = True

    _compiled_patterns = {}
    _cache_invalidated = True

    def __init__(self, settings):
        self.settings = settings  # TODO: 設定が変更されたらパターンを再構築する

    @abstractmethod
    def build_pattern(self):  # FIXME: buildとrebuildの機能が対応していない
        pass

    # @abstractmethod
    # def rebuild_name(self, elements):
    #     pass

    def invalidate_cache(self):
        self._cache_invalidated = True  # TODO: 設定側にフラグを持たせる

    def change_settings(self, new_settings):  # TODO: これも設定側に持たせる?
        self.settings = new_settings
        self.invalidate_cache() 

    # def update_cache(self):
    #     if self._cache_invalidated:
    #         pattern = self.build_pattern()
    #         self._compiled_patterns[self.element_type] = re.compile(pattern)
    #         self._cache_invalidated = False

    def search(self, name):
        if self._cache_invalidated:
            NamingElement.update_all_caches(self.settings)
        regex = self._compiled_patterns.get(self.element_type)
        match = regex.search(name)
        if match:
            return {
                'value': match.group(self.element_type),
                # 'type': element_type,
                # 'start': match.start(element_type),
                # 'end': match.end(element_type),
                # 'remainder': name[:match.start(element_type)] + name[match.end(element_type):]
            }
        else:
            return None

    def common_separator(self):
        return self.settings["common_settings"]["common_separator"]

    @classmethod
    def get_element_types(cls):
        subclasses = cls.__subclasses__()
        return [subclass.element_type for subclass in subclasses if subclass.element_type]

    # @classmethod
    # def update_all_caches(cls, settings):
    #     for element_type in cls.get_element_types():
    #         element = globals()[f"{element_type.capitalize()}Element"](settings)
    #         cls._compiled_patterns[element_type] = re.compile(element.build_pattern())
        
    #     cls._cache_invalidated = False

    @classmethod
    def update_all_caches(cls, settings):
        for subclass in cls.__subclasses__():
            if subclass.element_type:
                element = subclass(settings)
                cls._compiled_patterns[subclass.element_type] = re.compile(element.build_pattern())

        cls._cache_invalidated = False
        DBG_RENAME and log.info("Caches: " + str(cls._compiled_patterns))

class PrefixElement(NamingElement):
    element_type = "prefix"

    @maybe_with_separator(position="suffix")
    @capture_group
    def build_pattern(self):
        return f"({'|'.join(self.settings[self.element_type])})"


class MiddleElement(NamingElement):
    element_type = "middle"

    @maybe_with_separator(position="both")
    @capture_group
    def build_pattern(self):
        return f"({'|'.join(self.settings[self.element_type])})"
    

class SuffixElement(NamingElement):
    element_type = "suffix"

    @maybe_with_separator(position="prefix")
    @capture_group
    def build_pattern(self):
        return f"({'|'.join(self.settings[self.element_type])})"


class CounterElement(NamingElement):
    element_type = "counter"

    @maybe_with_separator(position="prefix")
    @capture_group
    def build_pattern(self):
        digits = self.settings[self.element_type]["digits"]
        return f"\d{{{digits}}}"    
    
    def get_value(self, elements):
        return int(elements[self.element_type]['value']) if elements[self.element_type] else None
    
    def get_string(self, value: int) -> str:
        return f"{value:0{self.settings['counter_settings']['digits']}d}"


class SideElement(NamingElement):
    # TODO: Positionに変更して、左右だけでなく、前後、上下なども扱えるようにする
    element_type = "side"
    # 独自のセパレーターを持つため、rebuild_nameで検知するためのフラグ
    use_common_separator = False

    def build_pattern(self):
        side_sep = re.escape(self.settings["side_pair"]["side_separator"])
        side_pattern = self.settings["side_pair"]["side_pair"]
        side_position = self.settings["side_pair"]["side_position"]
        if side_position == 'PREFIX':
            return f'(?P<{self.element_type}>{side_pattern}){side_sep}'
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<{self.element_type}>{side_pattern})'
        

class BlCounterElement(NamingElement):
    # Buildin Blender counter pattern like ".001"
    element_type = "bl_counter"

    @capture_group
    def build_pattern(self):
        return r"\.\d{3}"
    
    def get_value(self, name):
        match = self.search(name)
        if match:
            return int(match.group(self.element_type)[1:])  # .001 -> 001


class NamingManager:
    # TODO: 包括的な入力検証とエラー処理を実装する
    # settings, name, elementsの型をチェックする
    def __init__(self, settings):
        DBG_RENAME and log.header("NamingManager init", header=False)
        self.settings = settings
        self.elements = self.initialize_elements()
        DBG_RENAME and self.print_elements()
    
    def initialize_elements(self):
        elements = {}
        subclasses = NamingElement.__subclasses__()
        # TODO: 初期化インターフェイスを作って、それを実装したクラスだけを初期化するようにする
        for subclass in subclasses:
            if subclass.element_type:
                elements[subclass.element_type] = subclass(self.settings)
        return elements

    def search_elements(self, name):
        elements = {}
        # TODO: element.search()の戻り値に対してロバストであることを確認する
        for element_type, element in self.elements.items():
            elements[element_type] = element.search(name)
        return elements
    
    def update_elements(self, elements, new_elements=None):
        e = {}
        elements_types = NamingElement.get_element_types()
        for element_type in elements_types:
            # 新しい要素を受け取った場合
            if new_elements and element_type in new_elements:
                if new_elements[element_type] != "":
                    e[element_type] = new_elements[element_type]
                else:
                    # 新しい要素が空の場合
                    e[element_type] = None
            # 新しい要素がない場合
            elif elements[element_type]:
                e[element_type] = elements[element_type]
        return e
    
    def rebuild_name(self, elements):
        # 各要素のrebuild_nameにインデックスを渡す
        # ちがう、elementが順番をもつべき

        n = []
        name = ""

        # use_common_separator=Trueの要素を先に処理する
        for element_type, element in self.elements.items():
            if element.use_common_separator:
                n.append(element.get_string(elements))
        
        c_sep = NamingElement.common_separator()
        name = c_sep.join(n)

        side_sep = self.settings["side_pair"]["side_separator"]
        side_position = self.settings["side_pair"]["side_position"]
        if elements["side"]:
            if side_position == 'PREFIX':
                name = f"{elements['side']}{side_sep}{name}"
            elif side_position == 'SUFFIX':
                name = f"{name}{side_sep}{elements['side']}"
        
        return name

    # TODO: デバックモジュールに移動する
    def print_elements(self):
        for element_type, element in self.elements.items():
            log.info(f"{element_type}: {element}")
        log.info("")
    
    def parse_test(self):
        test_names = random_test_names(self.settings, 10)
        for name in test_names:
            log.info(f"Name: {name}")
            for element_type, element in self.elements.items():
                log.info(f"  {element_type}: {element.search(name)}")
            log.info("")


if __name__ == "__main__":
    nm = NamingManager(rename_preset)
    nm.parse_test()