from abc import ABC, abstractmethod
try:
    from . element_base import NamingElement
    from . element_counter import BlCounterElement, EzCounterElement
    from . element_text import TextElement, PositionElement
    from . namespace import Namespace, NamespaceManager, PoseBonesNamespace

    from .. debug import log, DBG_RENAME
    from . naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names)
    from .. rename_operation import EditableObject
except:
    from element_base import NamingElement
    from element_counter import BlCounterElement, EzCounterElement
    from element_text import TextElement, PositionElement

    from debug import log, DBG_RENAME
    from naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names)
    from rename_operation import EditableObject

import bpy

def uprefs():
    return bpy.context.preferences

def prefs():
    return rename_settings
    # return uprefs().addons[ADDON_ID].preferences

# EditableObjectをここまで連れてくる?
class NamingElements(ABC):
    """名前生成のルールとロジック"""
    object_type = None
    def __init__(self, obj_type):
        self.elements = self._create_elements(obj_type)


    def _create_elements(self, obj_type):
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
        elements.sort(key=lambda e: e.get_order())  # しなくてもいいかも
        DBG_RENAME and log.info( \
            f'build_elements: {obj_type}:\n' + '\n' \
                .join([f'  {e.identifier}: {e.name}' for e in elements]))
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
            if element.element_type == element_type:
                return element
        raise ValueError(f"Unknown element type: {element_type}")

    def search_elements(self, name: str):
        DBG_RENAME and log.header(f'search_elements: {name}', False)
        for element in self.elements:
            element.standby()
            element.search(name)

    def update_elements(self, new_elements: dict=None):
        if not new_elements and not isinstance(new_elements, dict):
            return

        for element in self.elements:
            if element.name in new_elements:
                # new_elementsの値がNoneの場合は、その要素を無効化する
                # element.value = new_elements[element.name] or None
                element.set_value(new_elements[element.name] or None)
        
        new_name = self.render_name()
        for element in self.elements:
            # elementのキャプチャ要素を更新する
            element.update(new_name)

    def render_name(self) -> str:
        elements_parts = [element.render() for element in self.elements \
                          if element.is_enabled() and element.value]
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
    
    def print_elements(self, name):
        self.search_elements(name)
        for element in self.elements:
            log.info(f"{element.identifier}: {element.value}")

    # # -----counter operations-----
    # @staticmethod
    # def check_duplicate_names(bone):
    #     return bone.name in (b.name for b in bone.id_data.pose.bones)

    # def replace_bl_counter(self, elements):
    #     if 'bl_counter' in elements:
    #         num = self.get_bl_counter_value(elements)
    #         elements['counter'] = {'value': self.get_counter_string(num)}
    #         del elements['bl_counter']
    #     return elements

    # # 名前の重複を確認しながら、カウンターをインクリメントしていく
    # def increment_counter(self, bone, elements):  # boneもしくはarmature 明示的なのは...
    #     # ここでboneが絶対に必要になる interfaceでboneもelementsも扱えるようにしたい
    #     counter_value = self.get_counter_value(elements)
    #     while self.check_duplicate_names(bone):
    #         counter_value += 1
    #         elements['counter']['value'] = self.get_counter_string(counter_value)
    #     return elements