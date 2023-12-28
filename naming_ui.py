import bpy
from . naming_test_utils import rename_preset


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
        self.draw_section(box, rename_preset['prefix'], 'prefix')
        self.draw_delete_button(box, 'prefix')

        row.separator()

        box = row.box()
        box.label(text="Middle")
        self.draw_section(box, rename_preset['middle'], 'middle')
        self.draw_delete_button(box, 'middle')

        row.separator()

        box = row.box()
        box.label(text="Suffix")
        self.draw_section(box, rename_preset['suffix'], 'suffix')
        self.draw_delete_button(box, 'suffix')

    def draw_delete_button(self, box, target_parts):
        del_button = box.operator("bonecraft.rename_bone_test", text="Delete", icon='CANCEL')
        del_button.target_parts = target_parts
        del_button.operation = 'delete'

    def draw_section(self, box, items, target_parts):
        max_items = 5

        num_col = len(items) // max_items
        # num_col = max(1, num_col)
        num_col = max(1, (len(items) + max_items - 1) // max_items)

        # 列幅
        scale_factor = 0.8 * num_col

        col = box.column_flow(columns=num_col, align=False)
        col.scale_x = scale_factor

        for i, item in enumerate(items):
            ops = col.operator("bonecraft.rename_bone_test", text=item)
            ops.operation = 'add/replace'
            ops.preset_index = i
            ops.target_parts = target_parts


panel_classes = [
    BONECRAFT_PT_rename_bone
]
