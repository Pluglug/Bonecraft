import bpy

from abc import ABC, abstractmethod
from . naming import NamingElements, PoseBonesNamespace


class EditableObject(ABC):  # RenamableObject
    obj_type = None
    def __init__(self, obj):
        self.obj = obj
    

class EditableBone(EditableObject):
    obj_type = "pose_bone"
    def __init__(self, bone):
        super().__init__(bone)
        self._init_rendering()

        # self.collection = None
        # self.color = None
    
    def _init_rendering(self):
        self.namespace = self.obj.id_data
        self.original_name = self.obj.name
        self.new_name = ""
        self.naming_elements = None

    def search_elements(self, naming_elements: NamingElements):
        naming_elements.search_elements(self)


class RenamePoseBones:
    def __init__(self):
        self.es = NamingElements("pose_bone")
        self.ns = NamespaceManager()

        self.original_names = []
        self.new_names = []

    def execute_rename(self, operator: bpy.types.Operator, context: bpy.types.Context):
        selected_pose_bones = context.selected_pose_bones
        new_elements = operator.new_elements

        for bone in selected_pose_bones:
            b = EditableBone(bone)
            self.es.search_elements(b)
            self.es.update_elements(new_elements)
            new_name = self.es.render_name()
            if self.check_duplicate_names(b, new_name):
                new_name = self.es.counter_operation(b)
                if new_name:
                    self.es.apply_name_change(b, new_name)
            else:
                self.es.apply_name_change(b, new_name)

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
