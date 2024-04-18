import bpy
from bpy.types import Operator, Panel, UIList, PropertyGroup
from bpy.props import PointerProperty, CollectionProperty

# class TEST_OT_Foo(bpy.types.Operator):
#     bl_idname = "test.foo"
#     bl_label = "Foo"
#     bl_description = "Foo"
#     bl_options = {'INTERNAL'}

#     # メモリ上にのみ存在し、Blenderが閉じられると消去される
#     my_set = set()

#     input_str: bpy.props.StringProperty()

#     def execute(self, context):
#         # self.my_setと同じであるが、self.__class__.my_setの方が明示的である。
#         if self.input_str in self.__class__.my_set:
#             self.__class__.my_set.remove(self.input_str)
#         else:
#             self.__class__.my_set.add(self.input_str)
#         return {'FINISHED'}

def redraw_screen(context=bpy.context):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()
    # view = context.preferences.view
    # temp = view.ui_scale
    # view.ui_scale = temp + 0.1
    # view.ui_scale = temp

from bl_ui.space_userpref import USERPREF_PT_theme_bone_color_sets

# org_draw = USERPREF_PT_theme_bone_color_sets.draw

# drawをオーバーライドすることで、ボタンを追加することができる
def draw(self, context):
    layout = self.layout
    layout.use_property_split = True
    layout.use_property_decorate = False
    
    layout.label(text="Override2")
    layout.separator()

EXTENDED_PANELS = dict()
EXTENDED_PANELS['TEST_OVERRIDE'] = draw


    # org_draw(self, context)
# オーバーライドしたdrawを設定する
# USERPREF_PT_theme_bone_color_sets.draw = draw  # だめ

# 関数オブジェクトをap/prependする
USERPREF_PT_theme_bone_color_sets.prepend(EXTENDED_PANELS['TEST_OVERRIDE'])  
redraw_screen()

# 消し方
# USERPREF_PT_theme_bone_color_sets.remove(EXTENDED_PANELS['TEST_OVERRIDE'])
# redraw_screen()

# Reference: ed_base.py