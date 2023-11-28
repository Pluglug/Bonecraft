import json
import os
from datetime import datetime
from addon import ADDON_ID, VERSION

from utils.vlog import log
from utils.debug_flags import DBG_PRESET


# def on_property_update(self, context):
#     preset_manager.unsaved_changes = True


class PresetManager:
    def __init__(self):
        self.unsaved_changes = False

    @staticmethod
    def create_preset_data(rigging_naming_conventions, preset_name):
        return {
            "addon": ADDON_ID,
            "addon_version": '.'.join(map(str, VERSION)),
            "preset_name": preset_name,
            "Last_saved_date": datetime.now().isoformat(),
            "Rigging_naming_conventions": rigging_naming_conventions
        }

    @staticmethod
    def is_valid_format(data):
        required_keys = {'addon', 'addon_version', 'preset_name', 'Last_saved_date', 'Rigging_naming_conventions'}
        return required_keys.issubset(data.keys())

    def load_preset(self, file_path):
        # 現在編集中のファイルとして設定する。
        with open(file_path, 'r') as file:
            data = json.load(file)

        if self.is_valid_format(data):
            self.unsaved_changes = False
            return data['Rigging_naming_conventions']
        else:
            raise ValueError("Invalid preset format")

    def save_preset(self, file_path, rigging_naming_conventions, preset_name):
        # bone_namingsからプロパティーを取得
        preset_data = self.create_preset_data(rigging_naming_conventions, preset_name)

        with open(file_path, 'w') as file:
            json.dump(preset_data, file, indent=4)

        # 未保存フラグを消す
        self.unsaved_changes = False
        # RenameCacheを作る

    # # プリセットデータの取得メソッド
    # def get_prefixes(self):
    #     return self.data["prefixes"]
    #
    # # その他の取得メソッド...

# test_file_path = "C:\\Users\\113412A00AUKD\\Desktop\\ICF_AutoCapsule_Disabled\\_bw2ill\\4.0.0\\4.0\\scripts\\addons\\bonecraft\\user\\Naming presets for rigging\\MyNameingPreset.json"
# naming_pre_data = PresetManager.load_preset(test_file_path)
# print(naming_pre_data)

# class PresetManager:
#     def __init__(self, presets_folder):
#         self.presets_folder = presets_folder
#
#     def save_preset(self, preset_data, preset_name):
#         file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
#         with open(file_path, 'w') as file:
#             json.dump(preset_data, file, indent=4)
#
#     def load_preset(self, preset_name):
#         file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
#         with open(file_path, 'r') as file:
#             return json.load(file)
#
#     def delete_preset(self, preset_name):
#         file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
#         if os.path.exists(file_path):
#             os.remove(file_path)


# 一度編集されれば"未保存"フラグが立つ
# Saveされるまで警告を出す　もしくはAutoSave
# MMのPlugsの管理方法
# Saveでキャッシュも作る

if __name__ == "__main__":
    pass