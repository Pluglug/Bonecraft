from abc import ABC, abstractmethod
import functools
import re


try:
    from .debug import log, DBG_RENAME
    from .operators.mixin_utils import ArmModeMixin
    from .naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
except:
    from debug import log, DBG_RENAME
    from operators.mixin_utils import ArmModeMixin
    from naming_test_utils import (rename_settings, # test_selected_pose_bones, 
                               random_test_names, generate_test_names, 
                               )
    




# class ObjectInfo:  # BlenderObjectInfo NamingObject など
#     def __init__(self, obj):
#         self.obj = obj
#         self.original_name = obj.name
#         self.naming_space = obj.id_data
#         self.new_name = ""

# data_type (enum in [
#     'OBJECT', 
#     'COLLECTION', 
#     'MATERIAL', 
#     'MESH', ?
#     'CURVE', ?
#     'META', ?
#     'VOLUME', 
#     'GPENCIL', ?
#     'ARMATURE', ?
#     'LATTICE', ?
#     'LIGHT', ?
#     'LIGHT_PROBE', ?
#     'CAMERA', ?
#     'SPEAKER', ?
#     'BONE', 
#     'NODE', ?
#     'SEQUENCE_STRIP', 
#     'ACTION_CLIP'
#     ], (optional)) – Type, Type of data to rename

# SimpleRenamesItem = [
            # Object,
            # Data,
            # Material,
            # Bone,
            # Image Textures,
            # Collection,
            # Actions,
            # Shape Keys,
            # Vertex Groups,
            # Particle Systems,
            # UV Maps,
            # Facemaps,
            # Color Attributes,
            # Attributes,
            # ]


class BoneInfo:
    def __init__(self, pose_bone):
        self.pose_bone = pose_bone
        self.naming_space = pose_bone.id_data
        self.original_name = pose_bone.name
        self.new_name = ""

        self.naming_elements = None
        
        # 今後の拡張
        self.collection = None
        self.color = None
    


class RenameTest:
    def __init__(self, obj_type):
        self.obj_type = obj_type
        self.pr = rename_settings
        self.naming_elements = NamingElements(obj_type, self.pr)
        self.ns = PoseBonesNamespaces()
    
    def test(self, selected_pose_bones):
        for bone in selected_pose_bones:
            b = BoneInfo(bone)
            self.naming_elements.search_elements(b)
            # ...

    def rename_bone(self, bone, new_elements=None):
        self.naming_elements.search_elements(bone)
        self.naming_elements.update_elements(new_elements)
        new_name = self.naming_elements.render_name()
        if self.check_duplicate_names(bone, new_name):
            new_name = self.naming_elements.counter_operation(bone)
            if new_name:
                self.naming_elements.apply_name_change(bone, new_name)
                return True
            else:
                return False
        else:
            self.naming_elements.apply_name_change(bone, new_name)
            return True

    def check_duplicate_names(self, bone, proposed_name):
        return self.ns.check_duplicate(bone, proposed_name)


import bpy
class EZRENAMER_OT_RenameTest(bpy.types.Operator, ArmModeMixin):
    bl_idname = "ezrenamer.rename_test"
    bl_label = "Rename Test"
    bl_options = {'REGISTER', 'UNDO'}

    new_elements: bpy.props.StringProperty(name="New Elements", default="")

    def execute(self, context):
        with self.mode_context(context, 'POSE'):
            new_elements = {"prefix": "CTRL", "suffix": "", "position": None}
            _new_elements = eval(self.new_elements) if self.new_elements else new_elements
            selected_pose_bones = context.selected_pose_bones
            es = NamingElements("bone", rename_settings)
            for bone in selected_pose_bones:
                DBG_RENAME and log.header(f'Original name: {bone.name}')
                es.search_elements(bone.name)
                DBG_RENAME and log.info(f'Elements: {[(e.name, e.value) for e in es.elements]}')
                es.update_elements(_new_elements)
                DBG_RENAME and log.info(f'Update elements: {[(e.name, e.value) for e in es.elements]}')
                new_name = es.counter_operation(bone)
                bone.name = new_name
                DBG_RENAME and log.warning(f'New name: {bone.name}')
        return {'FINISHED'}


operator_classes = [
    EZRENAMER_OT_RenameTest,
]


if __name__ == "__main__":
    DBG_RENAME = True
    log.header("Naming Base Test", False)
    es = NamingElements("bone", rename_settings)
    # es.print_elements("CTRL_Root-05.L.001")
    # es.search_elements("CTRL_Root-05.L.001")
    # name = es.render_name()
    # log.info(name)
    from naming_test_utils import rename_preset
    test_names = random_test_names(rename_preset, 2)  # TODO: test_utilsを作り直す
    new_elements = {"prefix": "CTRL", "suffix": "", "position": None}

    test_names += ["CTRL_Root-05.L.001"]

    for name in test_names:
        es.search_elements(name)
        es.update_elements(new_elements)
        _ = es.render_name()