import re
import bpy
from debug import log, DBG_RENAME
from .naming_test_utils import *


class BoneInfo:
    def __init__(self, pose_bone):
        self.pose_bone = pose_bone
        self.original_name = pose_bone.name
        self.new_name = ""  # 新しい名前を格納するためのフィールド
        # 今後の拡張のための追加フィールド
        self.collection = None  # ボーンが属するコレクション
        self.color = None       # ボーンの色

    def rename(self, new_name):
        self.new_name = new_name
        self.pose_bone.name = new_name

"""
メモ
ボーンの名前を変更する際は、pose modeで行う。
Arm_obj.001
    Armature.001
        Bone.001
        Bone.002
Arm_obj.002
    Armature.002
        Bone.001
        Bone.002


        
bpy.ops.pose.autoside_names(axis='XAXIS')
XAXIS: Left/Right
YAXIS: Front/Back
ZAXIS: Top/Bottom


bpy.ops.pose.flip_names(do_strip_numbers=False)
選択した骨の名前の軸の接尾辞を反転させる
do_strip_numbers: name.Left.001 -> name.Right

親子関係でカウンターを付ける


bpy.context.selected_pose_bones
bpy.context.selected_pose_bones_from_active_object

"""
    

class BoneNamingPrefix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)

class BoneNamingMiddleWord(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)

class BoneNamingSuffix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)


separator_items = [
    ('_', "Underscore", "_"),
    ('.', "Dot", "."),
    ('-', "Dash", "-"),
    (' ', "Space", " "),
]


class BoneNamingPreset(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Preset Name")

    prefixes: bpy.props.CollectionProperty(type=BoneNamingPrefix)
    middle_words: bpy.props.CollectionProperty(type=BoneNamingMiddleWord)
    suffixes: bpy.props.CollectionProperty(type=BoneNamingSuffix)

    counter: bpy.props.IntProperty(
        name="Counter Settings", 
        default=2, 
        min=1, 
        max=5
    )

    common_separator: bpy.props.EnumProperty(
        name="Common Separator",
        items=separator_items,
        default='_'
    )

    side_pair: bpy.props.EnumProperty(
        name="Side Pair",
        description="Left/Right side pair format",
        items=[
            ('L|R', "L / R", "Upper case L/R", 1),
            ('l|r', "l / r", "Lower case l/r", 2),
            ('LEFT|RIGHT', "LEFT / RIGHT", "Full word LEFT/RIGHT", 3),
            ('left|right', "left / right", "Full word left/right", 4),
        ],
        default='L|R'
    )
    side_separator: bpy.props.EnumProperty(
        name="Side Separator",
        description="Separator for left/right",
        items=separator_items,
        default='.'
    )
    side_position: bpy.props.EnumProperty(
        name="Side Position",
        description="Position of side pair",
        items=[
            ('PREFIX', "Prefix", "Before the name"),
            ('SUFFIX', "Suffix", "After the name"),
        ],
        default='SUFFIX'
    )


class BoneNamingPresets(bpy.types.PropertyGroup):
    is_cache_valid = False

    presets: bpy.props.CollectionProperty(type=BoneNamingPreset)
    active_preset_index: bpy.props.IntProperty(name="Active Preset Index")

    def on_preset_selected(self):
        pass

    def create_pie_menu_items(self, context):
        pass

    def export_presets(self, file_path):
        pass

    def import_presets(self, file_path):
        pass

    def on_edit(self, context):
        self.is_cache_valid = False


if __name__ == "__main__":
    pass
