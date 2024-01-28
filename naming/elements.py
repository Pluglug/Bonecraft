# import os, sys
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from abc import ABC, abstractmethod
import random
import itertools

try:
    from . element_base import NamingElement
    from . element_text import TextElement, PositionElement
    from . element_counter import BlCounterElement

    from .. debug import log, DBG_RENAME
    from . test_settings import rename_settings
except:
    from element_base import NamingElement
    from element_text import TextElement, PositionElement
    from element_counter import BlCounterElement

    from debug import log, DBG_RENAME
    from test_settings import rename_settings

# import bpy

# def uprefs():
#     return bpy.context.preferences

def prefs():
    return rename_settings
    # return uprefs().addons[ADDON_ID].preferences

# TODO: メインカウンター、サブカウンター属性を持たせる

# EditableObjectをここまで連れてくる?
class NamingElements: # (ABC):
    """名前生成のルールとロジック"""
    object_type = None
    def __init__(self, obj_type):
        self.elements = self._create_elements(obj_type)

    def _create_elements(self, obj_type):
        DBG_RENAME and log.header(f'build_elements: {obj_type}').increase()
        pr = prefs()
        if obj_type not in pr:
            raise ValueError(f"Unknown object type: {obj_type}")
        settings: list = pr[obj_type]  # TODO: prefsを作成後作り直す
        
        elements = []
        for elem_settings in settings:
            elem_type = elem_settings["type"]
            element = self._create_element(elem_type, elem_settings)
            elements.append(element)
        
        elements.append(BlCounterElement({}))
        elements.sort(key=lambda e: e.order)
        DBG_RENAME and log.decrease().info(
            f'{obj_type}: {len(elements)} elements\n' + '\n' \
                .join([f'  {e.id}: {e.element_type}' for e in elements]))
        return elements
    
    _element_classes = None
    @classmethod
    def _get_element_classes(cls):
        if cls._element_classes:
            return cls._element_classes
        element_classes = {}
        subclasses = NamingElement.__subclasses__()
        for subclass in subclasses:
            element_type = getattr(subclass, 'element_type', None)
            if element_type:
                element_classes[element_type] = subclass
        cls._element_classes = element_classes
        return element_classes

    def _create_element(self, element_type, settings):
        element_classes = self._get_element_classes()
        element_class = element_classes.get(element_type, None)
        if element_class:
            return element_class(settings)
        else:
            raise ValueError(f"Unknown element type: {element_type}")

    def get_element(self, element_type: str) -> NamingElement:
        for element in self.elements:
            if element.id == element_type:  # TODO: idもしくはelement_type
                return element
        raise ValueError(f"Unknown element type: {element_type}")

    def search_elements(self, name: str):
        DBG_RENAME and log.header(f'search_elements: {name}')
        for element in self.elements:
            element.standby()
            element.search(name)  # TODO: ETに前後の状態を渡せば、さらに正確に検索できる かもしれない

    def update_elements(self, new_elements: dict=None):
        if not new_elements and not isinstance(new_elements, dict):
            return

        for element in self.elements:
            if element.id in new_elements:
                # new_elementsの値がNoneの場合は、その要素を無効化する
                element.value = new_elements[element.id] or None
                # element.set_value(new_elements[element.name] or None)
        
        new_name = self.render_name()
        for element in self.elements:
            # elementのキャプチャ要素を更新する
            element.update(new_name)
        # return new_name  # 再考
        return self

    def render_name(self) -> str:
        elements_parts = [element.render() for element in self.elements \
                          if element.enabled and element.value]
        name_parts = []
        for sep, value in elements_parts:
            if name_parts:
                name_parts.append(sep)
            name_parts.append(value)
        name = ''.join(name_parts)
        DBG_RENAME and log.info(f'render_name: {name}')
        return name

    def chenge_all_settings(self, new_settings):
        for element in self.elements:
            element.change_settings(new_settings)

    def update_caches(self):
        for element in self.elements:
            if element.cache_invalidated:
                element.update_cache()
    
    def pring_elements(self):
        for element in self.elements:
            log.info(f"{element.id}: {element.value}")
    
    def gen_random_test_names(self, num_cases=10) -> list:
        """Generate random names for test cases"""
        test_names = []
        for _ in range(num_cases):
            elem_parts = [elem.test_random_output() for elem in self.elements \
                          if random.choice([True, False])]
            name_parts = []
            for sep, value in elem_parts:
                if name_parts:
                    name_parts.append(sep)
                name_parts.append(value)
            test_names.append(''.join(name_parts))
        return test_names

    def gen_test_names(self) -> list:
        """Generate all combinations of test case names"""

        # Generate combinations where each element is present or absent
        element_combinations = itertools.product([True, False], repeat=len(self.elements))

        test_cases = []
        for combination in element_combinations:
            name_parts = []
            for elem, include in zip(self.elements, combination):
                if include:  #  and elem.enabled:
                    sep, value = elem.test_random_output()
                    if name_parts:
                        name_parts.append(sep)
                    name_parts.append(value)
            test_cases.append(''.join(name_parts))

        return test_cases


if '__main__' == __name__:
    # testing
    ne = NamingElements('pose_bone')
    log.header("Generate test names", 'TEST').increase()
    names = ne.gen_random_test_names(5)
    # names = ne.gen_test_names()
    # log.info('\n'.join(names))
    for name in names:
        log.info(name)
