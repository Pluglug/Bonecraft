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
        group = self.name
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
        DBG_RENAME and log.info(f'init: {self.name}')

    @abstractmethod  # 抽象メソッドとインスタンスメソッドの混在はよろしくない?
    def build_pattern(self):
        """Each subclass should implement its own pattern building method."""
        pass

    def standby(self):
        self.value = None
        # self.start = None
        # self.end = None
        # self.remainder = None

    def search(self, target_string):
        if self.cache_invalidated:
            self.update_cache()
        match = self.compiled_pattern.search(target_string)
        return self.capture(match)
    
    def capture(self, mache):
        if mache:
            self.value = mache.group(self.name)
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


class UnknownElement(NamingElement):
    pass


class TextElement(NamingElement):
    element_type = "text"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get('items', [])

    @maybe_with_separator
    @capture_group
    def build_pattern(self):
        return '|'.join(self.items)
        

class EzCounterElement(NamingElement):
    element_type = "ez_counter"
    
    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.digits = settings.get('digits', 2)
        # セパレーターとセットで識別する場合、カウンターが名前の先頭にあるとセパレーターが付与されない。
        # できれば、名前の先頭にあってほしくない。なにか制約を考える必要がある。

    @maybe_with_separator  # self.separator、つまりez_counterのセパレーターを使用
    @capture_group
    def build_pattern(self):
        # sep = re.escape(self.get_separator())
        # return f'{sep}\\d{{{self.digits}}}'  # このようにセパレーターとセットで識別することで、bl_counterとの衝突をある程度避けることができる
        return f'\\d{{{self.digits}}}' # (?=\D|$)'あえて"00"を取らせちゃう なんとかなれー 3桁以上だとダメ  # FIXME: bl_counterを拾ってしまう
    
    def standby(self):
        super().standby()
        self.value_int = None

    def capture(self, match):
        if match:
            self.value = match.group(self.name)
            self.value_int = int(self.value)
            return True
        return False
    
    # 指定された数と足し算
    def add(self, num):
        self.value_int += num
        self.value = f'{self.value_int:0{self.digits}d}'
        return self.value

    def increment(self):
        return self.add(1)

    def get_separator(self):
        return self.separator  # + "|\\."
    # CounterElement に "." をセパレータとして設定しようとした場合に、
    # BlCounterElement との衝突が起こりうることを警告するポップアップを表示
    # そもそもCounterとBlCounterを区別しないようにする? 
    # しかし2箇所にカウンターが存在する可能性がある("name-05.001") 
    # 足し算すればいいんだ!("name-06")
    # 設定を変えたときに、変換できると便利 (01 -> 00001)
    # "001"、"-01"、".A"などの開始設定 なにかExcelのオートフィルみたいなことができるモジュールはないか?
    #  "Bone-A-01", "Bone-B-02" など  マルチカウンターサポート これはcounterを高度に抽象化すればできるかもしれない

    # def get_string(self):
    #     return f'{self.value:0{self.digits}d}' if self.value else None
    
    # def replace_bl_counter(self, name, value):
    #     if BlCounterElement.search(name):
    #         return name[:BlCounterElement.start] + f'.{value:0{self.digits}d}'

class PositionElement(NamingElement):
    element_type = "position"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get('items', [])
    
    def build_pattern(self):
        sep = re.escape(self.get_separator())
        pattern = '|'.join(self.items)

        if self.get_order() == 1:
            return f'(?P<{self.name}>{pattern}){sep}'
        # elif self.get_order() > 1:
        else:
            return f'{sep}(?P<{self.name}>{pattern})'

    def get_separator(self):
        return self.separator


class BlCounterElement(NamingElement):
    """ Buildin Blender counter pattern like ".001" """
    element_type = "bl_counter"

    def apply_settings(self, settings):
        # No settings for this element.
        self.cache_invalidated = True
        self.settings = settings

        self.identifier = 'bl_counter'
        self.order = 100  # ( ´∀｀ )b
        self.name = 'bl_counter'
        self.enabled = False  # デフォルトで名前の再構築時に無視されるようにする?
        self.digits = 3
        self.separator = "."  # The blender counter is always "." .

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
            self.value = match.group(self.name)
            self.start = match.start(self.name)
            self.value_int = int(self.value[1:])
            return True
        return False

    def get_separator(self):
        return self.separator
    
    def get_value(self):
        return int(self.value[1:]) if self.value else None  # .001 -> 001

    def except_bl_counter(self, name):
        """Return the name without the bl_counter and the bl_counter value."""
        if self.search(name):
            return name[:self.start], int(self.value[1:])
        else:
            return name, None


class NamingElements:  #(ABC)
    # elements_type = None
    def __init__(self, obj_type, settings):
        # 将来、typeで何をビルドするか指示される。mesh, material, bone, etc...
        self.elements = self.build_elements(obj_type, settings)  # TODO: obj_typeの扱いを考える

    def build_elements(self, obj_type, settings):
        elements = []
        elements_type = f"{obj_type}_elements"
        for element_settings in settings[elements_type]:
            element_type = element_settings["type"]
            element = self.create_element(element_type, element_settings)
            elements.append(element)
            
        elements.append(BlCounterElement({}))  # これはハードコードで良い
        elements.sort(key=lambda e: e.get_order())
        DBG_RENAME and log.info( \
            f'build_elements: {elements_type}:\n' + '\n'.join([f'  {e.identifier}: {e.name}' for e in elements]))
        return elements
    
    def get_element_classes(self):
        element_classes = {}  # 再利用する場合はキャッシュ
        subclasses = NamingElement.__subclasses__()  # TODO: obj_typeに適したサブクラスを取得する必要がある
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
        DBG_RENAME and log.header(f'search_elements: {name}', False)
        for element in self.elements:
            element.standby()
            element.search(name)
    
    def update_elements(self, new_elements=None):
        if not new_elements and not isinstance(new_elements, dict):
            return

        for element in self.elements:
            if element.name in new_elements:
                element.value = new_elements[element.name] or None

    def render_name(self):
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

    def counter_operation(self, bone):
        bl_counter = next((e for e in self.elements if isinstance(e, BlCounterElement)), None)
        ez_counter = next((e for e in self.elements if isinstance(e, EzCounterElement)), None)

        if bl_counter and ez_counter:
            ez_counter.add(bl_counter.get_value())
        elif ez_counter:
            ez_counter.increment()
        else:
            raise ValueError("EzCounterElement is missing in elements")

        proposed_name = self.render_name()
        while self.check_duplicate_names(bone, proposed_name):
            ez_counter.increment()
            proposed_name = self.render_name()
        return proposed_name

    def check_duplicate_names(self, bone, name):
        # ここでハッシュセットを使用して名前の重複をチェック
        return name in (b.name for b in bone.id_data.pose.bones)

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
    

# class Namespace(ABC):
#     pass


# class PoseBones(Namespace):
#     def __init__(self):
#         self.namespaces = []

#     def register_object(self, bone):
#         # オブジェクトを登録し、名前空間を初期化または更新
#         armature = bone.id_data
#         for pose_bone in armature.pose.bones:
#             self.namespaces.append(pose_bone.name)

#     def check_duplicate(self, proposed_name):
#         # 提案された名前が既に存在するかチェック
#         return proposed_name in self.namespaces

#     def increment_counter(self, elements):
#         # 必要に応じてカウンターをインクリメントし、新しい名前を生成
#         counter_element = [e for e in elements if isinstance(e, EzCounterElement)]
#         while self.check_duplicate(proposed_name):
#             counter_element.increment()
#             proposed_name = self.render_name()
#         return elements


import bpy
class EZRENAMER_OT_RenameTest(bpy.types.Operator):
    bl_idname = "ezrenamer.rename_test"
    bl_label = "Rename Test"
    bl_options = {'REGISTER', 'UNDO'}

    new_elements: bpy.props.StringProperty(name="New Elements", default="")

    def execute(self, context):
        # new_elements = {"prefix": "CTRL", "suffix": "", "position": None}
        _new_elements = eval(self.new_elements)
        selected_pose_bones = context.selected_pose_bones
        es = NamingElements("bone", rename_settings)
        for bone in selected_pose_bones:
            es.search_elements(bone.name)
            es.update_elements(_new_elements)
            new_name = es.counter_operation(bone)
            bone.name = new_name
        return {'FINISHED'}


operator_classes = [
    EZRENAMER_OT_RenameTest,
]


if __name__ == "__main__":
    DBG_RENAME = True
    log.header("Naming Base Test", False)
    es = NamingElements("bone", rename_settings)
    # es.print_elements("CTRL_Root-05.L.001")
    # es.search_elements("CTRL_Root-05.L.001")
    # name = es.render_name()
    # log.info(name)
    from naming_test_utils import rename_preset
    test_names = random_test_names(rename_preset, 2)  # TODO: test_utilsを作り直す
    new_elements = {"prefix": "CTRL", "suffix": "", "position": None}

    test_names += ["CTRL_Root-05.L.001"]

    for name in test_names:
        es.search_elements(name)
        es.update_elements(new_elements)
        _ = es.render_name()