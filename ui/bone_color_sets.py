import bpy
from bpy.types import (
    Context,
    PropertyGroup, 
    Panel, 
    UIList,
    Operator, 
    WindowManager,
)
from bpy.props import (
    FloatVectorProperty,
    BoolProperty,
    IntProperty,
    StringProperty,
    CollectionProperty,
    PointerProperty,
)

from bl_ui.space_userpref import USERPREF_PT_theme_bone_color_sets


# Bone Color Setsだけのプリセットを作成、保存、読み込みするアドオンを作成する

class CustomBoneColorSet(PropertyGroup):
    normal = FloatVectorProperty(
        name="Normal",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for normal state"
    )
    select = FloatVectorProperty(
        name="Select",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for selected state"
    )
    active = FloatVectorProperty(
        name="Active",
        subtype='COLOR',
        size=3,
        min=0.0, max=1.0,
        description="Color for active state"
    )
    show_colored_constraints = BoolProperty(
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
    color_sets = CollectionProperty(type=CustomBoneColorSet)
    name = StringProperty(default="Custom Bone Color Sets")
    active_bone_color_set_index = IntProperty(default=0)

    def add_preset(self, theme):
        """Add a new color set preset and initialize it from the given theme."""
        new_preset = self.color_sets.add()
        new_preset.name = f"Preset {len(self.color_sets)}"
        for theme_set in theme.bone_color_sets:
            preset_set = new_preset.color_sets.add()
            preset_set.copy_from(theme_set)
        return new_preset

    def restore_preset(self, context, index):
        """Restore the given preset to the theme."""
        theme = context.preferences.themes[0]
        preset = self.color_sets[index]
        for theme_set, preset_set in zip(theme.bone_color_sets, preset.color_sets):
            theme_set.copy_from(preset_set)

    def remove_preset(self, index):
        self.color_sets.remove(index)

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
        theme = context.preferences.themes[0]
        return hasattr(theme, "bone_color_sets")

    def execute(self, context):
        try:
            return self.save_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to save new bone color preset: {e}")
            return {'CANCELLED'}

    def save_preset(self, context):
        theme = context.preferences.themes[0]
        wm = context.window_manager

        new_preset = wm.bone_color_sets.add_preset(theme)
        # wm.active_bone_color_set_index = len(wm.bone_color_sets) - 1

        self.report({'INFO'}, f"New bone color preset saved: {new_preset.name}")
        return {'FINISHED'}


class BONECOLOR_OT_load_preset(Operator):
    """Load the selected bone color preset"""
    bl_idname = "bonecolor.load_preset"
    bl_label = "Load Bone Color Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        return wm.active_bone_color_set_index >= 0

    def execute(self, context):
        try:
            return self.load_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load bone color preset: {e}")
            return {'CANCELLED'}

    def load_preset(self, context):
        wm = context.window_manager
        wm.bone_color_sets.restore_preset(context, wm.active_bone_color_set_index)

        self.report({'INFO'}, f"Loaded bone color preset: {wm.bone_color_sets[wm.active_bone_color_set_index].name}")
        return {'FINISHED'}



class BONECOLOR_OT_remove_preset(Operator):
    """Remove the selected bone color preset"""
    bl_idname = "bonecolor.remove_preset"
    bl_label = "Remove Bone Color Preset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        wm = context.window_manager
        return wm.active_bone_color_set_index >= 0

    def execute(self, context):
        try:
            return self.remove_preset(context)
        except Exception as e:
            self.report({'ERROR'}, f"Failed to remove bone color preset: {e}")
            return {'CANCELLED'}

    def remove_preset(self, context):
        wm = context.window_manager
        target_index = wm.active_bone_color_set_index
        target_name = wm.bone_color_sets[target_index].name

        wm.bone_color_sets.remove_preset(target_index)
        wm.active_bone_color_set_index = max(0, wm.active_bone_color_set_index - 1)

        self.report({'INFO'}, f"Removed bone color preset: {target_name}")
        return {'FINISHED'}


class USERPREF_PT_custom_bone_color_sets(Panel):
    bl_label = "Custom Bone Color Sets"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PREFERENCES'  # 'USER_PREFERENCES'は古い
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        if not wm.bone_color_sets:
            wm.bone_color_sets = bpy.data.window_managers[0].bone_color_sets

        layout.template_list("BONECOLOR_UL_presets_bone_color_sets", "BONECOLOR_UL_presets_bone_color_sets", 
                            wm.bone_color_sets, "color_sets", 
                            wm.bone_color_sets, "active_bone_color_set_index")

        row = layout.row()
        row.operator("bonecolor.save_preset", icon='EXPORT', text="Save Preset")

        if wm.active_bone_color_set_index >= 0:
            row.operator("bonecolor.remove_preset", icon='TRASH', text="Remove Preset")
            row.operator("bonecolor.load_preset", icon='IMPORT', text="Load Preset")

        layout.separator()



classes = (
    CustomBoneColorSet,
    CustomBoneColorSets,
    # BoneColorSetPreset,
    BONECOLOR_UL_presets_bone_color_sets,
    BONECOLOR_OT_save_preset,
    BONECOLOR_OT_load_preset,
    BONECOLOR_OT_remove_preset,
    USERPREF_PT_custom_bone_color_sets,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
    
    WindowManager.bone_color_sets = PointerProperty(type=CustomBoneColorSets)
    WindowManager.active_bone_color_set_index = IntProperty(default=0)
    USERPREF_PT_theme_bone_color_sets.prepend(USERPREF_PT_custom_bone_color_sets.draw)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    USERPREF_PT_theme_bone_color_sets.remove(USERPREF_PT_custom_bone_color_sets.draw)
    del WindowManager.active_bone_color_set_index
    del WindowManager.bone_color_sets

register()








# # Reference
# class USERPREF_PT_theme_bone_color_sets(ThemePanel, CenterAlignMixIn, Panel):
#     bl_label = "Bone Color Sets"
#     bl_options = {'DEFAULT_CLOSED'}

#     def draw_header(self, _context):
#         layout = self.layout

#         layout.label(icon='COLOR')

#     def draw_centered(self, context, layout):
#         theme = context.preferences.themes[0]

#         layout.use_property_split = True

#         for i, ui in enumerate(theme.bone_color_sets, 1):
#             layout.label(text=iface_("Color Set %d") % i, translate=False)

#             flow = layout.grid_flow(row_major=False, columns=0, even_columns=True, even_rows=False, align=True)

#             flow.prop(ui, "normal")
#             flow.prop(ui, "select", text="Selected")
#             flow.prop(ui, "active")
#             flow.prop(ui, "show_colored_constraints")