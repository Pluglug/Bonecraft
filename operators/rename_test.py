import re
import bpy

from utils.vlog import log
from utils.debug import DBG_RENAME


test_bone_names = [
    "Arm.L", "Leg.R", "Spine_01", "Hand.l", "Foot.r", "Head", "Finger01.L", "Toe01.R"
]

test_selected_pose_bones = [
     bpy.data.objects['SubArmature'].pose.bones["Bone"],
     bpy.data.objects['MyArmature'].pose.bones["Root"],
     bpy.data.objects['MyArmature'].pose.bones["Hand.l"],
     bpy.data.objects['MyArmature'].pose.bones["Spine_01"],
     bpy.data.objects['MyArmature'].pose.bones["Leg.R"],
     bpy.data.objects['MyArmature'].pose.bones["Arm.L"],
     bpy.data.objects['MyArmature'].pose.bones["Tail"],
     bpy.data.objects['MyArmature'].pose.bones["Hand.l.001"],
     bpy.data.objects['MyArmature'].pose.bones["Hand.l.002"],
     bpy.data.objects['MyArmature'].pose.bones["Finger01.L"],
     bpy.data.objects['MyArmature'].pose.bones["Finger02.L"]
]

rename_preset = {
    "prefixes": ["CTRL", "DEF", "MCH"],
    "middle_words": ["Arm", "Leg", "Spine", "Hand", "Foot", "Head", "Finger", "Toe"],
    "suffixes": ["Tweak", "Pole"],
    "counter_settings": {"digits": 2},
    "side_pair_settings": {
        "side_pair": "LR",
        "separator": "_",
        "position": "SUFFIX"
    },
    "separator_settings": {"separator": "_"}
}


import re


class RenameCache:
    def __init__(self, preset):
        self.preset = preset
        self.regex_cache = {}
        DBG_RENAME and log.header("Initializing RenameCache")
        self.update_cache()

    def update_cache(self):
        DBG_RENAME and log.info("Updating regex cache")
        self.regex_cache = {
            "prefix": self.generate_regex_pattern(self.preset["prefixes"]),
            "middle_word": self.generate_regex_pattern(self.preset["middle_words"]),
            "suffix": self.generate_regex_pattern(self.preset["suffixes"]),
            "side": self.generate_side_regex(self.preset["side_pair_settings"])
        }
        self.print_cache()

    def generate_regex_pattern(self, items):
        pattern = re.compile(f"({'|'.join(re.escape(item) for item in items)})")
        DBG_RENAME and log.info("Generated regex pattern:", pattern)
        return pattern

    def generate_side_regex(self, side_pair_settings):
        side_pair = side_pair_settings["side_pair"]
        separator = re.escape(side_pair_settings["separator"])
        position = side_pair_settings["position"]

        # 左右ペアの値を分割
        left, right = self.split_side_pair(side_pair)

        # ポジションに基づいてパターンを生成
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
        # その他の条件に対応する必要があればここに追加
        else:
            return '', ''  # デフォルトの値

    def print_cache(self):
        DBG_RENAME and log.header("Current Regex Cache")
        for key, value in self.regex_cache.items():
            DBG_RENAME and log.info(f"{key}: {value}")


# 初期化とキャッシュの更新
rename_cache = RenameCache(rename_preset)


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

    # 必要に応じて他のメソッドやプロパティを追加


selected_bones_info = [BoneInfo(pose_bone) for pose_bone in bpy.context.selected_pose_bones]

# リネーム例
for bone_info in selected_bones_info:
    bone_info.rename("新しい名前")


# if __name__ == "__main__":
#     pass
