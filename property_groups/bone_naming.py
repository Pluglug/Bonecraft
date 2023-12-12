import re
import bpy
from .. debug import log, DBG_RENAME
from .. operators.test_data import *

class BoneNamingPrefix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)

class BoneNamingMiddleWord(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)

class BoneNamingSuffix(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Name")
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)

# class BoneCounterSettings(bpy.types.PropertyGroup):
#     digits: bpy.props.IntProperty(name="Digits", default=2, min=1, max=5)

# class BoneSidePairSettings(bpy.types.PropertyGroup):
#     side_pair: bpy.props.EnumProperty(
#         name="Side Pair",
#         description="Left/Right side pair format",
#         items=[
#             ('LR', "L / R", "Upper case L/R", 1),
#             ('lr', "l / r", "Lower case l/r", 2),
#             ('LEFT_RIGHT', "LEFT / RIGHT", "Full word LEFT/RIGHT", 3),
#             ('left_right', "left / right", "Full word left/right", 4),
#         ],
#         default='LR'
#     )
#     separator: bpy.props.EnumProperty(
#         name="Separator",
#         description="Separator for left/right",
#         items=[
#             ('_', "Underscore", "_"),
#             ('.', "Dot", "."),
#             ('-', "Dash", "-"),
#             (' ', "Space", " "),
#             ('', "None", ""),
#         ],
#         default='_'
#     )
#     position: bpy.props.EnumProperty(
#         name="Position",
#         description="Position of side pair",
#         items=[
#             ('PREFIX', "Prefix", "Before the name"),
#             ('SUFFIX', "Suffix", "After the name"),
#         ],
#         default='SUFFIX'
#     )

# class BoneSeparatorSettings(bpy.types.PropertyGroup):
#     separator: bpy.props.EnumProperty(
#         name="Separator",
#         items=[
#             ('_', "Underscore", "_"),
#             ('.', "Dot", "."),
#             ('-', "Dash", "-"),
#             (' ', "Space", " "),
#         ],
#         default='_'
#     )

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
            ('LR', "L / R", "Upper case L/R", 1),
            ('lr', "l / r", "Lower case l/r", 2),
            ('LEFT_RIGHT', "LEFT / RIGHT", "Full word LEFT/RIGHT", 3),
            ('left_right', "left / right", "Full word left/right", 4),
        ],
        default='LR'
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


    regex_cache = {}

    def update_cache(self):
        DBG_RENAME and log.info("Updating regex cache")
        self.regex_cache = {
            "prefix": self.generate_regex_pattern(self.prefixes),
            "middle_word": self.generate_regex_pattern(self.middle_words),
            "suffix": self.generate_regex_pattern(self.suffixes),
            "side": self.generate_side_regex(self)
        }
        DBG_RENAME and self.print_cache()

    def generate_regex_pattern(self, items):
        pattern = re.compile(f"({'|'.join(re.escape(item.name) for item in items)})")
        DBG_RENAME and log.info("Generated regex pattern:", pattern)
        return pattern

    def generate_side_regex(self):
        side_pair = self.side_pair
        separator = re.escape(self.side_separator)
        position = self.side_position

        left, right = self.split_side_pair(side_pair)

        if position == 'PREFIX':
            pattern = f"^({left}{separator}|{right}{separator})"
        else:
            pattern = f"({separator}{left}|{separator}{right})$"

        return re.compile(pattern)
    
    def split_side_pair(self, side_pair):
        if side_pair == 'LR':
            return 'L', 'R'
        elif side_pair == 'lr':
            return 'l', 'r'
        elif side_pair == 'LEFT_RIGHT':
            return 'LEFT', 'RIGHT'
        elif side_pair == 'left_right':
            return 'left', 'right'
        else:
            return 'L', 'R'
    
    def print_cache(self):
        log.header("Regex cache")
        for key, value in self.regex_cache.items():
            log.info(f"{key}: {value}")

    def get_regex_cache(self):
        return self.regex_cache


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
