import re
import bpy

from .operators.mixin_utils import ArmModeMixin

from debug import log, DBG_PARSE
from naming_test_utils import (rename_preset, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )


class NamingManager:
    def __init__(self, preset):
        self.preset = preset
        self.sep = re.escape(self.preset["common_settings"]["common_separator"])
    
    def build_element_pattern(self, element_type):
        try:
            build_func = getattr(self, f'build_{element_type}_pattern')
        except AttributeError:
            raise AttributeError(f'build_{element_type}_pattern is not defined')
        
        return build_func()

    def build_prefix_pattern(self):
        prefix_pattern = '|'.join(self.preset['prefix'])
        return f'(?P<prefix>{prefix_pattern}){self.sep}'  

    def build_middle_pattern(self):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle']))
        return f'(?:{self.sep})?(?P<middle>{middle_pattern})'

    def build_suffix_pattern(self):
        suffix_pattern = '|'.join(self.preset['suffix'])
        return f'(?:{self.sep})?(?P<suffix>{suffix_pattern})'

    def build_counter_pattern(self):
        counter_pattern = r'\d{' + str(self.preset['counter_settings']['digits']) + '}'
        return f'(?:{self.sep})?(?P<counter>{counter_pattern})'

    def build_side_pattern(self):
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        side_position = self.preset["side_pair_settings"]["side_position"]
        side_pattern = self.preset['side_pair_settings']['side_pair']
        
        if side_position == 'PREFIX':
            return f'(?P<side>{side_pattern}){side_sep}'
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<side>{side_pattern})'
    
    def search_elements(self, name, element_types):
        elements = {element: None for element in element_types}
        for part in element_types:
            elements[part] = self.search_element(name, part)
        return elements

    def search_element(self, name, element_type):
        pattern = self.build_element_pattern(element_type)
        regex = re.compile(pattern)
        match = regex.search(name)
        if match:
            return {
                'value': match.group(element_type),
                # 'type': element_type,
                # 'start': match.start(element_type),
                # 'end': match.end(element_type),
                # 'remainder': name[:match.start(element_type)] + name[match.end(element_type):]
            }
        else:
            return None
    
    def rebuild_name(self, elements, new_elements=None):
        n = []
        for element_type in ['prefix', 'middle', 'suffix', 'counter']:
            if new_elements and element_type in new_elements:
                n.append(new_elements[element_type])
            elif elements[element_type]:
                n.append(elements[element_type]['value'])
            
        name = self.preset["common_settings"]["common_separator"].join(n)

        side_sep = self.preset["side_pair_settings"]["side_separator"]
        side_position = self.preset["side_pair_settings"]["side_position"]
        if new_elements and 'side' in new_elements:
            side = new_elements['side']
        else:
            side = elements['side']['value']

        if side:
            if side_position == 'PREFIX':
                name = f'{side}{side_sep}{name}'
            else:
                name = f'{name}{side_sep}{side}'
        
        return name
    
    def get_element_preset(self, element_type):
        if element_type in ['prefix', 'middle', 'suffix']:
            return self.preset[element_type]
        elif element_type == 'counter':
            return None
        elif element_type == 'side':
            return None


class PoseBoneEditor:
    pass


def rename_bone_test(new_elements=None):
    selected_bones_names = random_test_names(rename_preset, 5)
    # DBG_PARSE and log.info(f"Selected bones: {selected_bones_names}")
    nm = NamingManager(rename_preset)

    for bone_name in selected_bones_names:
        DBG_PARSE and log.info(f"Parse: {bone_name}")
        elements = nm.search_elements(bone_name, ['prefix', 'middle', 'suffix', 'counter', 'side'])
        # DBG_PARSE and log.info(f"Elements: {elements}")
        new_name = nm.rebuild_name(elements, new_elements)
        DBG_PARSE and log.info(f"New name: {new_name}")


class BONECRAFT_OT_rename_bone(bpy.types.Operator, ArmModeMixin):
    bl_idname = "bonecraft.rename_bone_test"
    bl_label = "Rename Bone Test"
    bl_description = "Testing renaming bones"

    nm = NamingManager(rename_preset)
        
    """操作対象となるNameElement"""
    target_parts: bpy.props.EnumProperty(
        name="Target Parts",
        description="Target parts to rename",
        items=[
            ('prefix', "Prefix", "Prefix", 1),
            ('middle', "Middle", "Middle", 2),
            ('suffix', "Suffix", "Suffix", 3),
            # ('counter', "Counter", "Counter", 4),
            ('side', "Side", "Side", 5),
        ],
        default='middle'
    )
    """追加/入替もしくは削除"""
    operation: bpy.props.EnumProperty(
        name="Operation",
        description="Operation to perform",
        items=[
            ('add/replace', "Add/Replace", "Add or replace", 1),
            ('delete', "Delete", "Delete", 2),
        ],
        default='add/replace'
    )

    preset_enum_items = []

    def get_preset_enum(self):
        if not BONECRAFT_OT_rename_bone.preset_enum_items:
            enum_items = []
            for i, preset in enumerate(rename_preset[self.target_parts]):
                enum_items.append((str(i), preset, preset, i))
            BONECRAFT_OT_rename_bone.preset_enum_items = enum_items
        return BONECRAFT_OT_rename_bone.preset_enum_items

    preset_index: bpy.props.EnumProperty(
        name="Preset",
        description="Preset to use",
        items=get_preset_enum,
        default='0'
    )

    def execute(self, context):
        with self.mode_context(self, context, 'POSE'):
            self.rename_selected_pose_bones()
        return {'FINISHED'}
    
    def rename_selected_pose_bones(self, context):
        for bone in context.selected_pose_bones:
            self.rename_bone(bone)

    def rename_bone(self, bone):
        elements = self.nm.search_elements(bone.name, ['prefix', 'middle', 'suffix', 'counter', 'side'])

        if self.operation == 'add/replace':
            new_elements = self.nm.get_element_preset(self.target_parts)[self.preset_index]
        elif self.operation == 'delete':
            new_elements = {self.target_parts: None}

        new_name = self.nm.rebuild_name(elements, new_elements)
        bone.name = new_name


operator_classes = [
    BONECRAFT_OT_rename_bone,
]


if __name__ == "__main__":
    pass
    # -----test parse-----
    # log.enable_inspect()
    # parser = NameParser(rename_preset)

    # # rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    # test_names = generate_test_names(rename_preset)
    # parser.test_parse_elements(test_names)



    # # -----test NamingElement-----
    # DBG_PARSE = False
    # parser = NameParser(rename_preset)
    # test_name = "MCH_Toe_Tweak_12.R"
    # elements = parser.search_elements(test_name, ['prefix', 'middle', 'suffix', 'counter', 'side'])
    # # log.info(elements)

    # # 抽出した要素に対する操作の例
    # for key, element in elements.items():
    #     if element:
    #         # 名前の要素に関する情報をログに記録
    #         log.info(f"{key}: {element}")

    #         # 特定の要素に対する操作
    #         if key == 'counter':
    #             # カウンター値を変更
    #             new_counter_value = int(element.value) + 1
    #             # element.set('value', str(new_counter_value))  # set method
    #             # element.value = str(new_counter_value)  # __setattr__ method
    #             element['value'] = str(new_counter_value)  # __setitem__ method
    #             # setattr(element, 'value', str(new_counter_value))  # __setattr__ method
    #             log.info(f"Updated counter: {element}")
    #             break

    # # rebuild test
    # new_elements = {'suffix': 'Tweak', 'counter': '12', 'side': 'R'}
    # rename_bone_test(new_elements)
