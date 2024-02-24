
rename_settings = {
    "pose_bone": [
        {
            "order": 1,
            "name": "prefix",  # キャプチャ用の名前 ユーザーが設定できるが重複は許されない
            "type": "text",
            "enabled": True,
            "items": ["CTRL", "DEF", "MCH", "ORG", "DRV", "TRG", "PROP"],
            "separator": "_",
        },
        {
            "order": 2,
            "name": "middle",
            "type": "text",
            "enabled": True,
            "items": [
                "Bone", 
                "Root", 
                "Spine", 
                "Chest",
                "Torso", 
                "Hips",
                "Tail",
                "Neck",
                "Head", 
                "Shoulder",
                "Arm", 
                "Elbow",
                "ForeArm",
                "Hand", 
                "InHand", 
                "Finger", 
                "UpLeg",
                "Leg", 
                "Shin",
                "Foot", 
                "Knee",
                "Toe", 
            ],
            "separator": "_",
        },
        {
            "order": 3,
            "name": "finger",
            "type": "text",
            "enabled": True,
            "items": ["Thumb", "Index", "Middle", "Ring", "Pinky"],
            "separator": "_",
        },
        {
            "order": 4,
            "name": "suffix",
            "type": "text",
            "enabled": True,
            "items": ["Base", "Tweak", "Pole", "IK", "FK", "Roll", "Rot", "Loc", "Scale"],
            "separator": "_",
        },
        {
            "order": 5,
            "name": "misc",
            "type": "text",
            "enabled": True,
            "items": ["INT", "temp", "copy", "delete", "hide", "show", "hide_select", "show_select"],
            "separator": "_",
        },
        {
            "order": 6,
            "name": "ez_counter",
            "type": "ez_counter",
            "enabled": True,
            "digits": 2,
            "separator": "-",
        },
        {
            "order": 7,
            "name": "position",
            "type": "position",  # positionである必要がなくなった  
            # "type": "text",　# 否定 セパレーター込みで一つの要素として扱う必要がある 正規表現を見直す必要がある searchロジックでのセパレーターの扱いを見直す
            "enabled": True,
            "items": ["L", "R", "Top", "Bot", "Fr", "Bk"],  # XAXIS, YAXIS, ZAXIS
            "separator": ".",
        },
    ],
}
# TODO: 設定で一括で大文字にしたり、小文字にしたり、キャメルケースにしたりできるようにする

# setting utils
try: # Running in Blender
    from ..debug import log, DBG_RENAME
except:  # Running Test in VSCode
    from debug import log, DBG_RENAME
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
                log.error(f"Index out of range: {num}")
                return None
        elif self.type == "ez_counter":
            # return f"{num:0{self.digits}d}"
            return num
        else:
            log.error(f"Unknown type: {self.type}")
            return None
    
    def len_items(self):
        return len(self.items)


class Setting:
    def __init__(self, setting_data):
        self.items = {item["name"]: Item(item) for item in setting_data}

    def get_item(self, item_name):  # FIXME: Setting.items.itemsになっちゃう
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

    r = pose_bone_setting.get_item(tgt_name)  # .get_value(tgt_num)
    print(type(r.items))
    