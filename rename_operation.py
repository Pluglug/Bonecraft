# import os, sys
# own_dir = os.path.dirname(__file__)
# print(f'own_dir: {own_dir}')
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import bpy

try:
    from . naming import NamingElements, NamespaceManager
    from . editable_object import EditableBone
    from . operators.mixin_utils import ArmModeMixin
    from . debug import log
except:
    from naming import NamingElements, NamespaceManager
    from editable_object import EditableBone
    from operators.mixin_utils import ArmModeMixin
    from debug import log

# 目標: カウンターによる重複名の回避を完成させる　カウンターオブジェクトに委譲
# 目標: リネームの実行を、リネームオブジェクトに委譲する

# テスト環境を整える
class EZRENAMER_OT_CreateTestArmature(bpy.types.Operator):
    bl_idname = "ezrenamer.create_test_armature"
    bl_label = "Create Test Armature"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.armature_add()
        arm = context.object
        arm.name = "TestArmature"
        arm.show_name = True
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.armature.select_all(action='SELECT')
        # ボーンを10本追加
        for i in range(10):
            bpy.ops.armature.duplicate_move(
                TRANSFORM_OT_translate={"value":(0, 0, 1)}
            )

        # ランダムな名前を付与
        es = NamingElements("pose_bone")
        test_names = es.gen_random_test_names(10)
        for i, bone in enumerate(arm.data.edit_bones):
            bone.name = test_names[i]

        return {'FINISHED'}


class EZRENAMER_OT_NSTest(bpy.types.Operator, ArmModeMixin):
    bl_idname = "ezrenamer.ns_test"
    bl_label = "Namespace Test"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        with self.mode_context(context, 'POSE'):
            log.header("RenameOperation", "TEST")
            es = NamingElements("pose_bone")
            ns = NamespaceManager()

            selected_pose_bones = context.selected_pose_bones
            rn_bones = [EditableBone(bone) for bone in selected_pose_bones]

            for i, rnb in enumerate(rn_bones):
                log.header(rnb.original_name)
                log.info(f'arm: {rnb.namespace_id.name}')

                rnb.get_namespace(ns)
                # new_name = f'NewName.{i+1:02d}'
                rnb.search_elements(es)
                rnb.update_elements({"prefix": "CTRL"})
                rnb.counter_operation()
                new_name = rnb.render_name()

            
            log.header("Result")
            # ns.namespacesの内容を表示
            ns.print_namespaces()

            return {'FINISHED'}

operator_classes = [
    EZRENAMER_OT_CreateTestArmature,
    EZRENAMER_OT_NSTest,
]

    
# class RenamePoseBones:
#     def __init__(self):
#         self.es = NamingElements("pose_bone")
#         self.nsm = NamespaceManager()

#         self.rn_bones = []

#     def execute_rename(self, operator: bpy.types.Operator, context: bpy.types.Context):
#         selected_pose_bones = context.selected_pose_bones
#         new_elements = operator.new_elements

#         # self.rn_bones = [EditableBone(bone) for bone in selected_pose_bones]

#         for b in self.rn_bones:
#             self.nsm.get_namespace(b)  # nsmがnsを作成、保持  ここにあるのは違和感
            
#             b.search_elements(self.es)
#             b.update_elements(new_elements)
#             new_name = b.render_name()
#             if self.nsm.check_duplicate(b, new_name):
#                 new_name = b.counter_operation(self.nsm.get_namespace(b))
#                 if new_name:
#                     b.apply_name_change(new_name)

    # def counter_operation(self, bone: EditableBone):
    #     return self.nsm.get_namespace(bone).counter_operation(bone)

        # self.nsm.get_namespace(b)  # nsmがnsを作成、保持

        # self.es.search_elements(b)
        # self.es.update_elements(new_elements)
        # new_name = self.es.render_name()
        # if self.check_duplicate_names(b, new_name):
        #     new_name = self.es.counter_operation(b)
        #     if new_name:
        #         self.es.apply_name_change(b, new_name)
        # else:
        #     self.es.apply_name_change(b, new_name)

    # def execute_rename(self, operator: bpy.types.Operator, context: bpy.types.Context):
    #     selected_pose_bones = context.selected_pose_bones
    #     for bone in selected_pose_bones:
    #         b = BoneInfo(bone)
    #         # ...

    # def confirm_rename(self):
    #     # 確認パネルに、rn_bone.original_name, rn_bone.new_nameを表示する
    #     # ユーザは、rn_bone.allow_rename(bool)を変更し、個別にリネームを取り消すことができる
    #     # ユーザがリネームの実行を承認した場合のみ、リネームを実行する
    #     pass

    # def apply_name_change(self):
    #     # メソッドを持たせたrn_boneのスケッチ        
    #     for rn_bone in self.rn_bones:
    #         if rn_bone.new_name and rn_bone.allow_rename:
    #             rn_bone.apply_name_change()
