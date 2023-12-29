import re
import bpy

try:
    from .operators.mixin_utils import ArmModeMixin  # vscodeではエラーになる Blenderでは問題ない
    from .debug import log, DBG_PARSE, DBG_RENAME
    from .naming_test_utils import (rename_preset, # test_selected_pose_bones, 
                                    random_test_names, generate_test_names, 
                                    )
except :
    from operators.mixin_utils import ArmModeMixin
    from debug import log, DBG_PARSE, DBG_RENAME
    from naming_test_utils import (rename_preset, # test_selected_pose_bones,
                                    random_test_names, generate_test_names, 
                                    )
    

# FIXME: このモジュールの構成を見直す
# Builder, Interface, Parser, Element, Rebuilder etc...
class NamingManager:
    def __init__(self, preset):
        self.preset = preset
        self.sep = re.escape(self.preset["common_settings"]["common_separator"])
    
    # -----builders-----
    def build_element_pattern(self, element_type):
        try:
            build_func = getattr(self, f'build_{element_type}_pattern')
        except AttributeError:
            raise AttributeError(f'build_{element_type}_pattern is not defined')
        
        return build_func()
    
    # TODO: パターンをキャッシュする
    # TODO: パターンだけ作ればいいようにしたい -> (?P<{element_type}>{pattern})

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
    
    def build_bl_counter_pattern(self):
        # Buildin Blender counter pattern like ".001"
        pattern = r'\.\d{3}'
        return f'(?P<bl_counter>{pattern})'

    # -----interface-----    
    def get_counter_value(self, elements):
        return int(elements['counter']['value']) if elements['counter'] else None

    def get_bl_counter_value(self, elements):
        if 'bl_counter' in elements:
            return int(elements['bl_counter']['value'][1:])  # .001 -> 001
        else:
            return None
    
    def get_counter_string(self, value: int) -> str:
        return f"{value:0{self.preset['counter_settings']['digits']}d}"

    # -----counter operations-----
    @staticmethod
    def check_duplicate_names(bone):
        return bone.name in (b.name for b in bone.id_data.pose.bones)

    def replace_bl_counter(self, elements):
        if 'bl_counter' in elements:
            num = self.get_bl_counter_value(elements)
            elements['counter'] = {'value': self.get_counter_string(num)}
            del elements['bl_counter']
        return elements

    # 名前の重複を確認しながら、カウンターをインクリメントしていく
    def increment_counter(self, bone, elements):  # boneもしくはarmature 明示的なのは...
        # ここでboneが絶対に必要になる interfaceでboneもelementsも扱えるようにしたい
        counter_value = self.get_counter_value(elements)
        while self.check_duplicate_names(bone):
            counter_value += 1
            elements['counter']['value'] = self.get_counter_string(counter_value)
        return elements
    

    # -----parser-----
    def search_elements(self, name, element_types=None):
        element_types = element_types or ['prefix', 'middle', 'suffix', 'counter', 'side', 'bl_counter']
        elements = {element: None for element in element_types}
        for part in element_types:
            DBG_PARSE and log.info(f"Searching {part}...")
            elements[part] = self.search_element(name, part)
            DBG_PARSE and log.info(f"{part}: {elements[part]}")
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

    # def replace_bl_counter_sketch(self, bone, elements):
    #     # # Blenderのカウンターを特定する正規表現パターン
    #     # bl_counter_pattern = self.build_bl_counter_pattern()
    #     # bl_counter_regex = re.compile(bl_counter_pattern)
    #     # bl_counter_match = bl_counter_regex.search(elements['remainder'])

    #     # if bl_counter_match:
    #     #     # Blenderのカウンター値（例：.001）を取得し、整数に変換
    #     #     bl_counter_value = int(bl_counter_match.group()[1:])

    #         # 元のカウンター値がある場合は置き換え、なければ新しく設定
    #         if 'counter' in elements and elements['counter']:
    #             elements['counter']['value'] = f"{bl_counter_value:03d}"  # 3桁でフォーマット
    #         else:
    #             elements['counter'] = {'value': f"{bl_counter_value:03d}"}

    #         # 元のBlenderカウンターを削除
    #         elements['remainder'] = bl_counter_regex.sub('', elements['remainder'])

    #     # 名前を再構築
    #     new_name = self.rebuild_name(elements)
        
    #     # 名前が重複している場合は、カウンターをインクリメントして再度検証
    #     while self.check_duplicate_names(bone):
    #         bl_counter_value += 1  # カウンターをインクリメント
    #         elements['counter']['value'] = f"{bl_counter_value:03d}"  # 更新
    #         new_name = self.rebuild_name(elements)  # 名前を再構築

    #     # 重複がなくなった新しい名前を返す
    #     return new_name




    # -----rebuilder-----
    def rebuild_name(self, elements, new_elements=None):
        # if elements['bl_counter']:
        #     elements = self.replace_bl_counter(elements)  # これは外で済ませるべき
        
        n = []
        for element_type in ['prefix', 'middle', 'suffix', 'counter']:
            if new_elements and element_type in new_elements:
                if new_elements[element_type] != "":
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
    
    def rename_bone(self, bone, elements, new_elements=None):       
        pass


# --------------------------------------------------
# class BONECRAFT_OT_RenameBone(bpy.types.Operator, ArmModeMixin):
#     bl_idname = "bonecraft.rename_bone_test"
#     bl_label = "Rename Bone Test"
#     bl_description = "Testing renaming bones"

#     nm = NamingManager(rename_preset)
    
#     target_parts: bpy.props.EnumProperty(
#         name="Target Parts",
#         description="Target parts to rename",
#         items=[
#             ('prefix', "Prefix", "Prefix", 1),
#             ('middle', "Middle", "Middle", 2),
#             ('suffix', "Suffix", "Suffix", 3),
#             # ('counter', "Counter", "Counter", 4),
#             # ('side', "Side", "Side", 5),
#         ],
#         default='middle'
#     )
#     operation: bpy.props.EnumProperty(
#         name="Operation",
#         description="Operation to perform",
#         items=[
#             ('add/replace', "Add/Replace", "Add or replace", 1),
#             ('delete', "Delete", "Delete", 2),
#         ],
#         default='add/replace'
#     )
#     preset_index: bpy.props.IntProperty(
#         name="Preset Index",
#         description="Preset index to use",
#         default=0,
#         min=0,
#         max=100
#     )

#     def execute(self, context):
#         DBG_RENAME and log.info(f"Target parts: {self.target_parts}", f"Operation: {self.operation}", f"Preset index: {self.preset_index}")
#         with self.mode_context(context, 'POSE'):
#             self.rename_selected_pose_bones(context)
#         return {'FINISHED'}
    
#     def rename_selected_pose_bones(self, context):
#         for bone in context.selected_pose_bones:
#             self.rename_bone(bone)

#     def rename_bone(self, bone):
#         DBG_RENAME and log.info(f"Rename bone: {bone.name}")
#         armature = bone.id_data
#         elements = self.nm.search_elements(bone.name)  # ここでbl_counterが判明する

#         if self.operation == 'add/replace':
#             new_elements = {self.target_parts: rename_preset[self.target_parts][self.preset_index]} 
#         elif self.operation == 'delete':
#             new_elements = {self.target_parts: ""}

#         new_name = self.nm.rebuild_name(elements, new_elements)
#         bone.name = new_name
#         DBG_RENAME and log.info(f"New name: {bone.name}")


# class BONECRAFT_OT_ToggleSide(bpy.types.Operator, ArmModeMixin):
#     bl_idname = "bonecraft.toggle_side"
#     bl_label = "Toggle Side"
#     bl_description = "Toggle side"

#     nm = NamingManager(rename_preset)

#     side_pair_index: bpy.props.IntProperty(
#         name="Side Pair Index",
#         description="Side pair index to use",
#         default=0,
#         min=0,
#         max=1
#     )

#     def execute(self, context):
#         DBG_RENAME and log.header("Toggle Side")
#         with self.mode_context(context, 'POSE'):
#             self.toggle_side_selected_pose_bones(context)
#         return {'FINISHED'}
    
#     def toggle_side_selected_pose_bones(self, context):
#         for bone in context.selected_pose_bones:
#             self.toggle_side(bone)
    
#     def toggle_side(self, bone):
#         DBG_RENAME and log.info(f"Toggle side: {bone.name}")
#         elements = self.nm.search_elements(bone.name)
#         side_pair = self.nm.get_side_pair()
#         if elements['side']:
#             if elements['side']['value'] == side_pair[self.side_pair_index]:
#                 new_elements = {'side': ""}
#             else:
#                 new_elements = {'side': side_pair[self.side_pair_index]}
#         else:
#             new_elements = {'side': side_pair[self.side_pair_index]}  # TODO: Refactor
        
#         new_name = self.nm.rebuild_name(elements, new_elements)
#         bone.name = new_name
#         DBG_RENAME and log.info(f"New name: {bone.name}")


# operator_classes = [
#     BONECRAFT_OT_RenameBone,
#     BONECRAFT_OT_ToggleSide,
# ]
# ----------------------------

if __name__ == "__main__":
    # pass
    # -----test parse-----
    # log.enable_inspect()
    # parser = NameParser(rename_preset)

    # # rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    # test_names = generate_test_names(rename_preset)
    # parser.test_parse_elements(test_names)



    # # -----test NamingElement-----
    # DBG_PARSE = False
    parser = NamingManager(rename_preset)
    # test_name = "MCH_Toe_Tweak_12.R"
    test_name = "MCH_Toe_Tweak_12.R.001"
    elements = parser.search_elements(test_name)
    log.info(elements)

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
