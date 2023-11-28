import json
import os


class PresetManager:
    def __init__(self, presets_folder):
        self.presets_folder = presets_folder

    def save_preset(self, preset_data, preset_name):
        file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
        with open(file_path, 'w') as file:
            json.dump(preset_data, file, indent=4)

    def load_preset(self, preset_name):
        file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
        with open(file_path, 'r') as file:
            return json.load(file)

    def delete_preset(self, preset_name):
        file_path = os.path.join(self.presets_folder, f"{preset_name}.json")
        if os.path.exists(file_path):
            os.remove(file_path)


# 一度編集されれば"未保存"フラグが立つ
# Saveされるまで警告を出す　もしくはAutoSave
# MMのPlugsの管理方法
