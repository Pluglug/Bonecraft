import bpy
from .test_settings import rename_settings, setting_utils

# bone_elements = rename_settings['pose_bone']
bone_settings = setting_utils.get_setting('pose_bone')

class BONECRAFT_PT_rename_bone(bpy.types.Panel):
    bl_label = "Rename Bone"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BoneCraft"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        row = layout.row(align=True)

        box = row.box()
        box.label(text="Prefix")
        # self.draw_section(box, rename_preset['prefix'], 'prefix')
        self.draw_section(box, bone_settings.get_item('prefix').items, 'prefix')
        self.draw_delete_button(box, 'prefix')

        row.separator()

        box = row.box()
        box.label(text="Middle")
        # self.draw_section(box, rename_preset['middle'], 'middle')
        self.draw_section(box, bone_settings.get_item('middle').items, 'middle')
        self.draw_delete_button(box, 'middle')

        row.separator()

        box = row.box()
        box.label(text="Suffix")
        # self.draw_section(box, rename_preset['suffix'], 'suffix')
        self.draw_section(box, bone_settings.get_item('suffix').items, 'suffix')
        self.draw_delete_button(box, 'suffix')

        row.separator()

        box = row.box()
        box.label(text="Finger")
        self.draw_section(box, bone_settings.get_item('finger').items, 'finger')
        self.draw_delete_button(box, 'finger')

        row.separator()

        box = row.box()
        box.label(text="Position")
        self.draw_section(box, bone_settings.get_item('position').items, 'position')
        self.draw_delete_button(box, 'position')

        row.separator()

        box = row.box()
        box.label(text="Misc")
        self.draw_section(box, bone_settings.get_item('misc').items, 'misc')
        self.draw_delete_button(box, 'misc')

        row.separator()

        box = row.box()
        box.label(text="Counter")
        counter_items = [f"{i:02}" for i in range(1, 11)]
        self.draw_section(box, counter_items, 'ez_counter')
        # ops = box.operator("ezrenamer.rename_test", text="start from 1")
        # ops.new_elements = "{'counter': '01'}"
        self.draw_delete_button(box, 'ez_counter')

    def draw_delete_button(self, box, target_parts):
        del_button = box.operator("ezrenamer.rename_pose_bones", text="Delete", icon='CANCEL')
        del_button.target_parts = target_parts
        del_button.operation = 'delete'

    def draw_section(self, box, items, target_part):
        max_items = 7

        num_col = len(items) // max_items
        # num_col = max(1, num_col)
        num_col = max(1, (len(items) + max_items - 1) // max_items)

        scale_factor = 1.2

        col = box.column_flow(columns=num_col, align=False)
        col.scale_x = scale_factor

        for i, item in enumerate(items):
            ops = col.operator("ezrenamer.rename_pose_bones", text=item)
            ops.operation = 'add/replace'
            ops.index = i
            ops.target_parts = target_part

panel_classes = [
    BONECRAFT_PT_rename_bone
]
