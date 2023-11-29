import bpy


class MY_PT_Panel(bpy.types.Panel):
    # パネルの定義 ...

    def draw(self, context):
        layout = self.layout
        rigging_settings = context.scene.bone_naming_presets

        # 現在選択されているプリセットの表示と編集
        if rigging_settings.presets:
            preset = rigging_settings.presets[rigging_settings.active_preset_index]

            layout.prop(preset, "name")

            # 接頭語、中間語、接尾語のリストの表示と編集
            for prefix in preset.prefixes:
                layout.prop(prefix, "name")
            # 中間語と接尾語も同様に表示

            # その他の設定の表示
            layout.prop(preset.counter_settings, "digits")
            # 他の設定も同様に表示
