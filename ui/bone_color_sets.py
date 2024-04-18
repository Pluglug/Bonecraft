import bpy

bl_info = {
    "name": "Bone Color Presets",
    "description": "Addon to save and load custom bone color presets.",
    "author": "Pluglug",
    "version": (0, 0, 2),
    "blender": (2, 9, 0),
    "location": "Preferences > Themes > Bone Color Sets",
    "warning": "This addon is still in development.",
    "wiki_url": "",
    "category": "Preferences",
}


from bpy.types import PropertyGroup, UIList, Operator
from bpy.props import (
    FloatVectorProperty,
    BoolProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
)

from bl_ui.space_userpref import USERPREF_PT_theme_bone_color_sets


# from ..addon import get_user_preferences, get_addon_preferences
ADDON_ID = __name__
DBG_INIT = True

def get_user_preferences(context=bpy.context):
    preferences = getattr(context, "preferences", None)
    if preferences is not None:
        return preferences
    else:
        raise AttributeError("Unable to access preferences")

def get_addon_preferences(context=bpy.context):
    user_prefs = get_user_preferences(context)
    addon_prefs = user_prefs.addons.get(ADDON_ID)
    if addon_prefs is not None:
        return addon_prefs.preferences
    else:
        raise KeyError(f"Addon '{ADDON_ID}' not found. Ensure it is installed and enabled.")


def _log(color, *args):
    msg = ""
    for arg in args:
        if msg:
            msg += ", "
        msg += str(arg)
    print(color + msg + '\033[0m')

def logi(*args):
    _log('\033[34m', *args)

def loge(*args):
    _log('\033[31m', *args)

def logh(msg):
    _log('\033[1;32m', "")
    _log('\033[1;32m', msg)

def logw(*args):
    _log('\033[33m', *args)


# Bone Color Setsだけのプリセットを作成、保存、読み込みするアドオンを作成する

class CustomBoneColorSet(PropertyGroup):
    normal: FloatVectorProperty(
        name="Normal",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for normal state"
    )
    select: FloatVectorProperty(
        name="Select",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for selected state"
    )
    active: FloatVectorProperty(
        name="Active",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for active state"
    )
    show_colored_constraints: BoolProperty(
        name="Show Colored Constraints",
        description="Whether to show constraints with color",
        default=False
    )

    def copy_from(self, other):
        """Copy color settings from another CustomBoneColorSet."""
        self.normal = other.normal[:]
        self.select = other.select[:]
        self.active = other.active[:]
        self.show_colored_constraints = other.show_colored_constraints

    def as_dict(self):
        return {
            "normal": self.normal[:],
            "select": self.select[:],
            "active": self.active[:],
            "show_colored_constraints": self.show_colored_constraints
        }
    
    def from_dict(self, data):
        self.normal = data["normal"]
        self.select = data["select"]
        self.active = data["active"]
        self.show_colored_constraints = data["show_colored_constraints"]


class CustomBoneColorSets(PropertyGroup):
    color_sets: CollectionProperty(type=CustomBoneColorSet)
    name: StringProperty(default="Custom Bone Color Sets")

    def add_color_sets(self, theme):
        """Add a new color set preset and initialize it from the given theme."""
        self.name = f"Preset {len(self.color_sets)}"
        for theme_set in theme.bone_color_sets:
            preset_set = self.color_sets.add()
            preset_set.copy_from(theme_set)
        return self

    def restore_color_sets(self, theme):
        """Restore the given preset to the theme."""
        for theme_set, preset_set in zip(theme.bone_color_sets, self.color_sets):
            theme_set.copy_from(preset_set)

    def save_to_file(self, filepath):
        """Save presets to a file."""
        import json
        data = [cs.as_dict() for cs in self.color_sets]
        with open(filepath, 'w') as f:
            json.dump(data, f)

    def load_from_file(self, filepath):
        """Load presets from a file."""
        import json
        with open(filepath, 'r') as f:
            data = json.load(f)
        for cs_data in data:
            cs = self.color_sets.add()
            cs.from_dict(cs_data)


class BONECOLOR_UL_presets_bone_color_sets(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        # item: CustomBoneColorSets
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="")


class BONECOLOR_OT_save_preset(Operator):
    """Save the current bone color settings as a new preset"""
    bl_idname = "bonecolor.save_preset"
    bl_label = "Save Bone Color Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        theme = get_user_preferences(context).themes[0]
        return hasattr(theme, "bone_color_sets")

    def execute(self, context):
        try:
            return self.save_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save new bone color preset: {e}")
            print(">>>", e)
            return {'CANCELLED'}

    def save_preset(self, context):
        theme = get_user_preferences(context).themes[0]
        prefs = get_addon_preferences(context)
        
        new_preset = prefs.add_bcs_preset(theme)

        self.report({'INFO'}, f"New bone color preset saved: {new_preset.name}")
        return {'FINISHED'}


class BONECOLOR_OT_load_preset(Operator):
    """Load the selected bone color preset"""
    bl_idname = "bonecolor.load_preset"
    bl_label = "Load Bone Color Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        prefs = get_addon_preferences(context)
        return prefs.active_bcs_preset_index >= 0

    def execute(self, context):
        try:
            return self.load_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load bone color preset: {e}")
            return {'CANCELLED'}

    def load_preset(self, context):
        theme = get_user_preferences(context).themes[0]
        prefs = get_addon_preferences(context)
        if prefs.restore_bcs_preset(theme):
            self.report({'INFO'}, f"Loaded bone color preset: {prefs.bcs_presets[prefs.active_bcs_preset_index].name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Failed to load bone color preset")
            return {'CANCELLED'}  # ハンドリング過多?


class BONECOLOR_OT_remove_preset(Operator):
    """Remove the selected bone color preset"""
    bl_idname = "bonecolor.remove_preset"
    bl_label = "Remove Bone Color Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        prefs = get_addon_preferences(context)
        return prefs.active_bcs_preset_index >= 0

    def execute(self, context):
        try:
            return self.remove_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove bone color preset: {e}")
            return {'CANCELLED'}

    def remove_preset(self, context):
        prefs = get_addon_preferences(context)
        prefs.remove_bcs_preset()


def _draw_presets(self, context):
    prefs = get_addon_preferences(context)

    layout = self.layout
    box = layout.box()

    box.label(text="Bone Color Presets", icon='PRESET_NEW')

    box.template_list("BONECOLOR_UL_presets_bone_color_sets", "", 
                         prefs, "bcs_presets", prefs, "active_bcs_preset_index")

    row = box.row()
    row.operator("bonecolor.save_preset", icon='EXPORT', text="Save Preset")

    if prefs.active_bcs_preset_index >= 0:
        row.operator("bonecolor.remove_preset", icon='TRASH', text="Remove Preset")
        row.operator("bonecolor.load_preset", icon='IMPORT', text="Load Preset")

    layout.separator()

# EXTENDED_PANELS

class BCSPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    bcs_presets: CollectionProperty(type=CustomBoneColorSet)
    active_bcs_preset_index: IntProperty(default=0)

    def add_bcs_preset(self, theme: bpy.types.Theme) -> CustomBoneColorSets:
        preset = self.bcs_presets.add()
        preset.add_color_sets(theme)
        self.active_bcs_preset_index = len(self.bcs_presets) - 1
        return preset

    def restore_bcs_preset(self, theme: bpy.types.Theme) -> bool:
        try:
            self.bcs_presets[self.active_bcs_preset_index].restore_color_sets(theme)
            return True
        except IndexError as e:
            print(">>>", e)
            return False
        
    def remove_bcs_preset(self):
        self.bcs_presets.remove(self.active_bcs_preset_index)


classes = (
    CustomBoneColorSet,
    CustomBoneColorSets,
    BONECOLOR_UL_presets_bone_color_sets,
    BONECOLOR_OT_save_preset,
    BONECOLOR_OT_load_preset,
    BONECOLOR_OT_remove_preset,
    BCSPreferences,
)


def register():
    logh("Registering bone_color_sets.py")
    from bpy.utils import register_class
    for cls in classes:
        logi(f"  Registering {cls.__name__}")
        register_class(cls)

    USERPREF_PT_theme_bone_color_sets.prepend(_draw_presets)


def unregister():
    logh("Unregistering bone_color_sets.py")
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        logi(f"  Unregistering {cls.__name__}")
        unregister_class(cls)
    
    USERPREF_PT_theme_bone_color_sets.remove(_draw_presets)
