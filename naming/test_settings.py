
rename_settings = {
    "pose_bone": [
        {
            "order": 1,
            "name": "prefix",  # キャプチャ用の名前 ユーザーが設定できるが重複は許されない
            "type": "text",
            "enabled": True,
            "items": ["CTRL", "DEF", "MCH"],
            "separator": "_",
        },
        {
            "order": 2,
            "name": "middle",
            "type": "text",
            "enabled": True,
            "items": ["Bone", "Root", "Arm", "Leg", "Spine", "Hand", "Foot", "Head", "Finger", "Toe", "Tail"],
            "separator": "_",
        },
        {
            "order": 3,
            "name": "suffix",
            "type": "text",
            "enabled": True,
            "items": ["Tweak", "Pole"],
            "separator": "_",
        },
        {
            "order": 4,
            "name": "ez_counter",
            "type": "ez_counter",
            "enabled": True,
            "digits": 2,
            "separator": "-",
        },
        {
            "order": 5,
            "name": "position",
            "type": "position",  # positionである必要がなくなった  
            # "type": "text",　# 否定 セパレーター込みで一つの要素として扱う必要がある 正規表現を見直す必要がある searchロジックでのセパレーターの扱いを見直す
            "enabled": True,
            "items": ["L", "R", "Top", "Bot", "Fr", "Bk"],  # XAXIS, YAXIS, ZAXIS
            "separator": ".",
        },
    ],
}


# setting utils

class Item:
    def __init__(self, item_data):
        self.name = item_data.get("name")
        self.type = item_data.get("type")
        self.enabled = item_data.get("enabled")
        self.items = item_data.get("items", [])
        self.digits = item_data.get("digits", 0)
        self.separator = item_data.get("separator", "")

    def get_value(self, num):
        if self.type in ["text", "position"]:
            if num < len(self.items):
                return self.items[num]
            else:
                raise ValueError(f"Index out of range: {num}")
        elif self.type == "ez_counter":
            return f"{num:0{self.digits}d}"
        else:
            raise ValueError(f"Unknown type: {self.type}")


class Setting:
    def __init__(self, setting_data):
        self.items = {item["name"]: Item(item) for item in setting_data}

    def get_item(self, item_name):
        return self.items.get(item_name)


class SettingUtils:
    def __init__(self, settings_data):
        self.settings = {name: Setting(setting) for name, setting in settings_data.items()}

    def get_setting(self, setting_name):
        return self.settings.get(setting_name)


setting_utils = SettingUtils(rename_settings)


if __name__ == "__main__":
    # testing
    pose_bone_setting = setting_utils.get_setting("pose_bone")

    tgt_name = "prefix"
    tgt_num = 1

    r = pose_bone_setting.get_item(tgt_name).get_value(tgt_num)
    print(r)
    