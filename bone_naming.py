import re
import bpy
from debug import log, DBG_RENAME
from .naming_test_utils import *


class NamingElement:
    def __init__(self, key):
        self.key = key
        self.regex = None
        self.enabled = True
    
    def generate_regex(self, preset_data):
        if self.key in preset_data:
            self.regex = re.compile(f"({'|'.join(re.escape(item) for item in preset_data[self.key])})")



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
    
    # def build_new_name(self, prefix, middle_word, suffix):
    #     """新しい名前を生成して返す"""
    #     new_name = ""
    #     if prefix:
    #         new_name += prefix
    #     if middle_word:
    #         new_name += middle_word
    #     if suffix:
    #         new_name += suffix
    #     return new_name

    # 必要に応じて他のメソッドやプロパティを追加


class RenameCache:
    def __init__(self, preset):
        self.preset = preset
        self.regex_cache = {}
        DBG_RENAME and log.header("Initializing RenameCache")
        self.update_cache()

    def update_cache(self):
        """各種正規表現パターンを生成してキャッシュに格納する"""
        DBG_RENAME and log.info("Updating regex cache")
        self.regex_cache = {
            "prefix": self.generate_regex_pattern(self.preset["prefixes"]),
            "middle_word": self.generate_regex_pattern(self.preset["middle_words"]),
            "suffix": self.generate_regex_pattern(self.preset["suffixes"]),
            "side": self.generate_side_regex(self.preset["side_pair_settings"])
        }
        self.print_cache()

    def generate_regex_pattern(self, items):
        """正規表現パターンを生成して返す"""
        pattern = re.compile(f"({'|'.join(re.escape(item) for item in items)})")
        DBG_RENAME and log.info("Generated regex pattern:", pattern)
        return pattern

    def generate_side_regex(self, side_pair_settings):
        """左右ペアの正規表現を生成して返す"""
        side_pair = side_pair_settings["side_pair"]
        separator = re.escape(side_pair_settings["separator"])
        position = side_pair_settings["position"]

        left, right = self.split_side_pair(side_pair)

        if position == 'PREFIX':
            pattern = f"^({left}{separator}|{right}{separator})"
        else:
            pattern = f"({separator}{left}|{separator}{right})$"

        return re.compile(pattern)

    def split_side_pair(self, side_pair):
        """左右ペアを分割して返す"""
        if side_pair == 'LR':
            return 'L', 'R'
        elif side_pair == 'lr':
            return 'l', 'r'
        elif side_pair == 'LEFT_RIGHT':
            return 'LEFT', 'RIGHT'
        elif side_pair == 'left_right':
            return 'left', 'right'
        else:
            return 'L', 'R'  # デフォルト値

    def print_cache(self):
        log.header("Current Regex Cache")
        for key, value in self.regex_cache.items():
            log.info(f"{key}: {value}")

    def get_regex_cache(self):
        return self.regex_cache


# # 初期化とキャッシュの更新
# rename_cache = RenameCache(rename_preset)
    

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
