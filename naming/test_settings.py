# TODO: 設定で一括で大文字にしたり、小文字にしたり、キャメルケースにしたりできるようにする
# pyright: reportInvalidTypeForm=false

try:  # Running in Blender
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
                "show_select",
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
            "type": "position",
            "enabled": True,
            "items": ["L", "R", "Top", "Bot", "Fr", "Bk"],  # XAXIS, YAXIS, ZAXIS
            "separator": ".",
        },
    ],
}


import bpy


def ic_cb(value) -> str:
    """Return icon name for checkbox."""
    return "CHECKBOX_HLT" if value else "CHECKBOX_DEHLT"


SEPARATOR_ITEMS = [
    ("_", "Underscore", "_"),
    (".", "Dot", "."),
    ("-", "Dash", "-"),
    (" ", "Space", " "),
]

NAMING_TYPE_ITEMS = [
    ("text", "Text", "Normal text"),
    (
        "position",
        "Position",
        "Short words that indicate position, such as left or right",
    ),
    (
        "ez_counter",
        "EZ Counter",
        "Replaces the counter that is automatically added at the end",
    ),
]

POSITION_ITEMS = ["L", "R", "Top", "Bot", "Fr", "Bk"]

RENAMABLE_OBJECTS = [
    ("POSE_BONE", "Pose Bone", "Rename pose bones"),
    ("DEBUG", "Debug", "Debug"),
    # ('MATERIAL', "Material", "Rename materials"),  # 未実装
    # ('OBJECT', "Object", "Rename objects"),
    # ('SCENE', "Scene", "Rename scenes"),
    # ('TEXTURE', "Texture", "Rename textures"),
    # ('WORLD', "World", "Rename worlds"),
]


class PP_ElementItem(bpy.types.PropertyGroup):
    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="If enabled, this word can be used in renaming",
        default=True,
        # update=_emi_compile_regex,  # TODO: make this work
    )
    item: bpy.props.StringProperty(
        name="Item",
        description="Word to be used in renaming",
        default="",
        maxlen=64,
        # update=_emi_compile_regex,
    )

    # 定義する場所はここではない?
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        layout.separator(factor=0.1)

        layout.active = item.enabled
        layout.prop(item, "enabled", text="", emboss=False, icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        r = layout.row()
        r.prop(item, "item", text="", emboss=False)

        r.separator(factor=0.5)


# リネーム設定の各要素を管理するプロパティグループ
class PP_NamingElement(bpy.types.PropertyGroup):
    """Element (prefixes, suffixes, etc.) in the naming convention."""

    def _update_name(self, context) -> None:
        pass
        # pr = prefs(context).rename_settings  # 仮
        # for i, elem in enumerate(pr.elements):
        #     if i != self.index and elem.name == self.name:
        #         self.name = self.gen_safe_name()
        #         log.error(f"Name is duplicated: {self.name}")
        #         break

    enabled: bpy.props.BoolProperty(
        name="Enabled",
        description="If enabled, this element can be used in renaming",
        default=True,
    )
    name: bpy.props.StringProperty(
        name="Name",
        description="The name of this element (no duplicates allowed)",
        default="New Element",
        # update=_update_name,　 TODO: make this work
    )  # 重複避けるためにはgen_safe_name()などが必要
    type: bpy.props.EnumProperty(
        name="Type",
        description="Type of element (text, counter, etc.)",
        items=NAMING_TYPE_ITEMS,
    )
    separator: bpy.props.EnumProperty(
        name="Separator",
        description='Separator to connect to the "forward" word (element)',
        items=SEPARATOR_ITEMS,
    )
    digits: bpy.props.IntProperty(
        name="Digits",
        description="Number of digits to be filled with zeros(only if type is Counter)",
    )  # ez_counter用

    items: bpy.props.CollectionProperty(
        type=PP_ElementItem,
        name="Items",
        description="List of items to be used in renaming",
    )
    # active_item_index: bpy.props.IntProperty(
    #     name="Active Item Index",
    #     description="Index of the active item in the list",
    #     options={'SKIP_SAVE'},
    # )

    def add_item(self, item: str) -> bool:
        if item not in self.items:
            # 追加と入力は分ける?
            self.items.add().item = item
            return True
        return False

    def remove_item(self, index: int) -> bool:
        if index < len(self.items):
            self.items.remove(index)
            # インデックス操作必要?
            return True
        return False

    def move_item(self, index: int, direction: int) -> bool:
        if index < len(self.items):
            if 0 <= index + direction < len(self.items):
                self.items.move(index, index + direction)
                return True
        return False

    def get_item(self, num: int) -> str:
        if self.type in ["text", "position"]:
            if num < len(self.items):
                return self.items[num]
            else:
                log.error(f"Index out of range: {num}")
                return None
        elif self.type == "ez_counter":
            return f"{num:0{self.digits}d}"
        else:
            log.error(f"Unknown type: {self.type}")
            return None

    def get_value(self, num):
        """Deprecated. Use get_item() instead."""
        caller = log.get_caller_info()
        log.warn(
            "get_value() is deprecated. Use get_item() instead. "
            + f"Called from {caller.filename}:{caller.lineno}"
        )


class PP_NamingElements(bpy.types.PropertyGroup):
    """A naming convention based on the combination of each element.
    It exists for each object type (or namespace)."""

    object_type: bpy.props.EnumProperty(
        items=RENAMABLE_OBJECTS,
        name="Object Type",
        description="Select the object type to rename",
    )
    elements: bpy.props.CollectionProperty(type=PP_NamingElement)
    active_element_index: bpy.props.IntProperty()  # for Element

    def get_setting(self, setting_name):
        return self.elements.get(setting_name)


class TestPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    rename_settings: bpy.props.CollectionProperty(
        type=PP_NamingElements,
        name="Rename Settings",
        description="Settings for renaming objects",
    )
    idx_emi: bpy.props.IntProperty(  # for Element items
        name="Active Item Index",
        description="Index of the active item in the list",
        options={"SKIP_SAVE"},
    )
    idx_em: bpy.props.IntProperty(  # for NamingElement
        name="Active Element Index",
        description="Index of the active element in the list",
        options={"SKIP_SAVE"},
    )
    idx_ed_elements: bpy.props.IntProperty(  # for NamingElements
        name="Active Element Index",
        description="Index of the elements being edited",
        options={"SKIP_SAVE"},
    )


def property_register():
    bpy.utils.register_class(PP_ElementItem)
    bpy.utils.register_class(PP_NamingElement)
    bpy.utils.register_class(PP_NamingElements)
    bpy.utils.register_class(TestPreferences)


class RENAME_UL_Element(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname, index
    ):
        layout.separator(factor=0.1)

        layout.active = item.enabled
        layout.prop(item, "enabled", text="", emboss=False, icon=ic_cb(item.enabled))

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
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "RenameTool"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "rename_target", text="Target")

        box = layout.box()
        row = box.row()
        col = row.column()
        # col.template_list("RENAME_UL_Settings", "", scene, "rename_settings", scene, "rename_settings_index")
        col.template_list(
            "RENAME_UL_Element",
            "",
            scene,
            "rename_settings",
            scene,
            "rename_settings_index",
        )

        col = row.column(align=True)
        ops = col.operator("uilist.entry_add", icon="ADD", text="")
        ops.list_path = "scene.rename_settings"

        # 選択された要素の詳細設定を表示
        if (
            scene.rename_settings_index >= 0
            and len(scene.rename_settings) > scene.rename_settings_index
        ):
            setting = scene.rename_settings[scene.rename_settings_index]

            box = layout.box()
            box.prop(setting, "name")
            box.prop(setting, "type")
            box.prop(setting, "enabled")
            box.prop(setting, "separator")

            if setting.type == "ez_counter":
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
        self.settings = {
            name: Setting(setting) for name, setting in settings_data.items()
        }

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
