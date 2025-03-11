import bpy

# bl_info = {
#     "name": "Simple Name Mod",
#     "author": "Pluglug",
#     "version": (0, 0, 1),
#     "blender": (2, 80, 0),
#     "location": "",
#     "description": "Modify the name of the selected object",
#     "warning": "No Keymap. Please set 'object.name_mod' to your keymap.",
#     "wiki_url": "",
#     "tracker_url": "",
#     "category": "Object"
# }


class RenameOptions(bpy.types.PropertyGroup):
    nm_enum_presuf: bpy.props.EnumProperty(
        name="Prefix/Suffix",
        items=[
            ("PRE", "Prefix", "Prefix"),
            ("SUF", "Suffix", "Suffix"),
        ],
        default="PRE",
    )
    nm_str_presuf: bpy.props.StringProperty(
        name="Prefix/Suffix",
        default="",
    )
    nm_reset_after_use: bpy.props.BoolProperty(
        name="Reset After Use",
        default=True,
    )


class NameMod(bpy.types.Operator):
    bl_idname = "object.name_mod"
    bl_label = "Name Mod"
    bl_description = "Modify the name of the selected object"
    bl_options = {"REGISTER", "UNDO"}

    nm_options: bpy.props.PointerProperty(type=RenameOptions)

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        objects = context.selected_objects
        for obj in objects:
            if self.nm_options.nm_enum_presuf == "PRE":
                obj.name = self.nm_options.nm_str_presuf + "_" + obj.name
            elif self.nm_options.nm_enum_presuf == "SUF":
                obj.name = obj.name + "_" + self.nm_options.nm_str_presuf
        if self.nm_options.nm_reset_after_use:
            self.nm_options.nm_str_presuf = ""
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.prop(self.nm_options, "nm_enum_presuf", expand=True)
        layout.prop(self.nm_options, "nm_str_presuf", text="")
        layout.prop(self.nm_options, "nm_reset_after_use")


# classes = [
#     RenameOptions,
#     NameMod,
# ]


# def register():
#     for cls in classes:
#         bpy.utils.register_class(cls)
#     bpy.types.WindowManager.nm_options = bpy.props.PointerProperty(type=RenameOptions)


# def unregister():
#     for cls in classes:
#         bpy.utils.unregister_class(cls)
#     del bpy.types.WindowManager.nm_options
