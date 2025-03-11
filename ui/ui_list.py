import bpy


def ic_cb(value):
    return "CHECKBOX_HLT" if value else "CHECKBOX_DEHLT"


class BONENAME_UL_PREFIX(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.separator(factor=0.1)
        layout.active = item.enabled

        layout.prop(item, "enabled", text="", emboss=False, icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        layout.prop(item, "name", text="", emboss=False)

        layout.separator(factor=0.1)


class BONENAME_UL_MIDDLE_WORD(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.separator(factor=0.1)
        layout.active = item.enabled

        layout.prop(item, "enabled", text="", emboss=False, icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        layout.prop(item, "name", text="", emboss=False)

        layout.separator(factor=0.1)


class BONENAME_UL_SUFFIX(bpy.types.UIList):
    def draw_item(
        self, context, layout, data, item, icon, active_data, active_propname
    ):
        layout.separator(factor=0.1)
        layout.active = item.enabled

        layout.prop(item, "enabled", text="", emboss=False, icon=ic_cb(item.enabled))

        layout.separator(factor=0.1)

        layout.prop(item, "name", text="", emboss=False)

        layout.separator(factor=0.1)
