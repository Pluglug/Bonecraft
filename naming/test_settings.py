# TODO: 設定で一括で大文字にしたり、小文字にしたり、キャメルケースにしたりできるようにする
# pyright: reportInvalidTypeForm=false

try: # Running in Blender
    from ..debug import log, DBG_RENAME
except:  # Running Test in VSCode
    from debug import log, DBG_RENAME

rename_settings = {
    "pose_bone": [
        {
            "order": 1,  # インデックス使用すれば不要
            "name": "prefix",  # キャプチャ用の名前 ユーザーが設定できるが重複不可 gen_sefe_name()が必要
            "type": "text",
            "enabled": True,
            "items": [
                "CTRL", 
                "DEF", 
                "MCH", 
                "ORG", 
                "DRV", 
                "TRG", 
                "PROP",
                ],
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
            "items": ["Finger", "Thumb", "Index", "Middle", "Ring", "Pinky"],
            "separator": "_",
        },
        {
            "order": 4,
            "name": "suffix",
            "type": "text",
            "enabled": True,
            "items": [
                "Base", 
                "Tweak", 
                "Pole", 
                "IK", 
                "FK", 
                "Roll", 
                "Rot", 
                "Loc", 
                "Scale",
                "INT",
                ],
            "separator": "_",
        },
        {
            "order": 5,
            "name": "misc",
            "type": "text",
            "enabled": True,
            "items": [
                "int", 
                "rot",
                "temp", 
                "copy", 
                "delete", 
                "hide", 
                "show", 
                "hide_select", 
                "show_select"
                ],
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


import bpy


def ic_cb(value) -> str:
    """Return icon name for checkbox."""
    return 'CHECKBOX_HLT' if value else 'CHECKBOX_DEHLT'


SEPARATOR_ITEMS = [
    ('_', "Underscore", "_"),
    ('.', "Dot", "."),
    ('-', "Dash", "-"),
    (' ', "Space", " "),
]

NAMING_TYPE_ITEMS = [
    ('text', "Text", ""),
    ('position', "Position", ""),
    ('ez_counter', "EZ Counter", ""),
]

POSITION_ITEMS = [
    "L", "R", "Top", "Bot", "Fr", "Bk"
]

RENAMABLE_OBJECTS = [
    ('POSE_BONE', "Pose Bone", "Rename pose bones"),
    # ('MATERIAL', "Material", "Rename materials"),  # 未実装
    # ('OBJECT', "Object", "Rename objects"),
    # ('SCENE', "Scene", "Rename scenes"),
    # ('TEXTURE', "Texture", "Rename textures"),
    # ('WORLD', "World", "Rename worlds"),
]


class ItemOption(bpy.types.PropertyGroup):
    # このクラスはRenameElementSettings.itemsのために使用される
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    option: bpy.props.StringProperty(name="Option")

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.separator(factor=0.1)

        layout.active = item.enabled
        layout.prop(item, "enabled", text="", emboss=False,
                 icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        r = layout.row()
        r.prop(item, "option", text="", emboss=False)

        r.separator(factor=0.5)

# リネーム設定の各要素を管理するプロパティグループ
class RenameElementSettings(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(name="Enabled", default=True)
    name: bpy.props.StringProperty(name="Name")  # 重複避けるためにはgen_safe_name()が必要
    type: bpy.props.EnumProperty(name="Type", items=NAMING_TYPE_ITEMS)
    separator: bpy.props.EnumProperty(name="Separator", items=SEPARATOR_ITEMS)
    items: bpy.props.CollectionProperty(type=ItemOption)
    digits: bpy.props.IntProperty(name="Digits")  # ez_counter用

    # def draw_item():
    #     pass

    def get_value(self, num):
        if self.type in ["text", "position"]:
            if num < len(self.items):
                return self.items[num]
            else:
                log.error(f"Index out of range: {num}")
                return None
        elif self.type == "ez_counter":
            return num
        else:
            log.error(f"Unknown type: {self.type}")
            return None


# リネーム設定を管理するプロパティグループ
class RenameElementsSettings(bpy.types.PropertyGroup):
    elements: bpy.props.CollectionProperty(type=RenameElementSettings)

    def get_setting(self, setting_name):
        return self.elements.get(setting_name)

class TestPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__
    renamable_object = bpy.props.EnumProperty(
        items=RENAMABLE_OBJECTS,
        name="Renamable Object",
        description="Select the object to rename"
    )
    rename_settings: bpy.props.CollectionProperty(type=RenameElementsSettings)
    elements_active_index: bpy.props.IntProperty()
    items_active_index: bpy.props.IntProperty()  # for Element items


class RENAME_UL_Element(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        layout.separator(factor=0.1)

        layout.active = item.enabled
        layout.prop(item, "enabled", text="", emboss=False,
                 icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        r = layout.row()
        if index == 0:
            r.active = False
        r.prop(item, "separator", text="", emboss=False)

        r = layout.row()
        r.prop(item, "name", text="", emboss=False)

        r.separator(factor=0.5)
    

class RENAME_PT_Panel(bpy.types.Panel):
    bl_label = "Rename Settings"
    bl_idname = "RENAME_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'RenameTool'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "rename_target", text="Target")

        box = layout.box()
        row = box.row()
        col = row.column()
        # col.template_list("RENAME_UL_Settings", "", scene, "rename_settings", scene, "rename_settings_index")
        col.template_list("RENAME_UL_Element", "", scene, "rename_settings", scene, "rename_settings_index")

        col = row.column(align=True)
        ops = col.operator("uilist.entry_add", icon='ADD', text="")
        ops.list_path = "scene.rename_settings"

        # 選択された要素の詳細設定を表示
        if scene.rename_settings_index >= 0 and len(scene.rename_settings) > scene.rename_settings_index:
            setting = scene.rename_settings[scene.rename_settings_index]

            box = layout.box()
            box.prop(setting, "name")
            box.prop(setting, "type")
            box.prop(setting, "enabled")
            box.prop(setting, "separator")

            if setting.type == 'ez_counter':
                box.prop(setting, "digits")

            # itemsの編集UIを追加する

# -------------------------------------------------------------------

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
    