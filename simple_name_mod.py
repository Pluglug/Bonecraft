import re
import bpy

from . operators.mixin_utils import *


"""演習: 簡易構造でリネーム機能を動作させる"""

prefix_items = [
    "Def",
    "Ctl",
    "Mch"
]

mid_items = [
    "Root",
    "Spine",
    "Arm",
    "Leg",
    "Hand",
    "Foot",
    "Finger",
    "Toe",
    "Head",
    "Eye"
]

side_pair_patterns = re.compile(r"\.L|\.R")
number_pattern = re.compile(r"\d{2}")

SEPALATOR = "_"


class SimpleNameMod:
    # セパレーター
    pass


class SIMPLENAMEMOD_OT_add_prefix(ArmModeMixin, bpy.types.Operator):
    bl_idname = "simple_name_mod.add_prefix"
    bl_label = "Add Prefix"
    bl_description = "Add prefix to bone name"
    bl_options = {'REGISTER', 'UNDO'}

    prefix: bpy.props.EnumProperty(
        name="Prefix",
        items=[(item, item, "") for item in prefix_items]
    )

