import re
import bpy

from .operators.mixin_utils import ArmModeMixin

from .debug import log, DBG_PARSE, DBG_RENAME
from .naming_test_utils import (rename_preset, # test_selected_pose_bones, 
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
        return f'(?P<prefix>{prefix_pattern})(?:{self.sep})?'  

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
        elif elements['side']:
            side = elements['side']['value']
        else:
            side = None

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
    operation: bpy.props.EnumProperty(
        name="Operation",
        description="Operation to perform",
        items=[
            ('add/replace', "Add/Replace", "Add or replace", 1),
            ('delete', "Delete", "Delete", 2),
        ],
        default='add/replace'
    )
    preset_index: bpy.props.IntProperty(
        name="Preset Index",
        description="Preset index to use",
        default=0,
        min=0,
        max=100
    )

    def execute(self, context):
        DBG_RENAME and log.info(f"Target parts: {self.target_parts}", f"Operation: {self.operation}", f"Preset index: {self.preset_index}")
        with self.mode_context(context, 'POSE'):
            self.rename_selected_pose_bones(context)
        return {'FINISHED'}
    
    def rename_selected_pose_bones(self, context):
        for bone in context.selected_pose_bones:
            self.rename_bone(bone)

    def rename_bone(self, bone):
        elements = self.nm.search_elements(bone.name, ['prefix', 'middle', 'suffix', 'counter', 'side'])

        if self.operation == 'add/replace':
            new_elements = {self.target_parts: rename_preset[self.target_parts][self.preset_index]} 
        elif self.operation == 'delete':
            new_elements = {self.target_parts: ""}

        new_name = self.nm.rebuild_name(elements, new_elements)
        bone.name = new_name


class BONECRAFT_PT_rename_bone(bpy.types.Panel):
    bl_label = "Rename Bone"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BoneCraft"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)

        box = row.box()
        box.label(text="Prefix")
        self.draw_section(box, rename_preset['prefix'], 'prefix')
        del_prefix = box.operator("bonecraft.rename_bone_test", text="Delete")
        del_prefix.target_parts = 'prefix'
        del_prefix.operation = 'delete'

        row.separator()

        box = row.box()
        box.label(text="Middle")
        self.draw_section(box, rename_preset['middle'], 'middle')
        del_middle = box.operator("bonecraft.rename_bone_test", text="Delete")
        del_middle.target_parts = 'middle'
        del_middle.operation = 'delete'

        row.separator()

        box = row.box()
        box.label(text="Suffix")
        self.draw_section(box, rename_preset['suffix'], 'suffix')
        del_suffix = box.operator("bonecraft.rename_bone_test", text="Delete")
        del_suffix.target_parts = 'suffix'
        del_suffix.operation = 'delete'

    def draw_section(self, box, items, target_parts):
        max_items = 5

        # 計算された列数
        num_col = len(items) // max_items
        num_col = max(1, num_col)  # 少なくとも1列は確保

        # 列のスケールを設定するための基準値
        scale_factor = 0.8 * num_col

        if num_col > 1:
            col = box.column_flow(columns=num_col, align=False)
            # 各列のscale_xを設定
            col.scale_x = scale_factor
        else:
            col = box.column(align=False)

        for i, item in enumerate(items):
            ops = col.operator("bonecraft.rename_bone_test", text=item)
            ops.operation = 'add/replace'
            ops.preset_index = i
            ops.target_parts = target_parts




operator_classes = [
    BONECRAFT_OT_rename_bone,
    BONECRAFT_PT_rename_bone,
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

    # rebuild test
    new_elements = {'suffix': 'Tweak', 'counter': '12', 'side': 'R'}
    rename_bone_test(new_elements)
