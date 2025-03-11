import bpy


def update_preset_selection(self, context):
    preset_name = self.presets_enum
    self.current_preset_name = preset_name
    # プリセットをロードする処理をここに追加


class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # 利用可能なプリセットの一覧
    presets_enum: bpy.props.EnumProperty(
        name="Presets",
        description="Available presets",
        items=[("PRESET_NAME", "Preset Name", "Description", "FILE_PATH", 0)],
        update=update_preset_selection,
    )

    # 現在選択されているプリセットの名前
    current_preset_name: bpy.props.StringProperty()


def register():
    bpy.utils.register_class(MyAddonPreferences)


def unregister():
    bpy.utils.unregister_class(MyAddonPreferences)
