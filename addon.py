import bpy
import os
# import sys
# import traceback


VERSION = None
BL_VERSION = None
ADDON_ID = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
ADDON_PATH = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
# SCRIPT_PATH = os.path.join(ADDON_PATH, "scripts/")
# ICON_ENUM_ITEMS = bpy.types.UILayout.bl_rna.functions[
#     "prop"].parameters["icon"].enum_items


def uprefs(context=None):
    context = context or bpy.context
    return getattr(context, "preferences", None)

def prefs(context=None):
    return uprefs(context).addons[ADDON_ID].preferences
