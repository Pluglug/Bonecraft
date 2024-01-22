# import os, sys
# own_dir = os.path.dirname(__file__)
# print(f'own_dir: {own_dir}')
# sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import bpy

from abc import ABC, abstractmethod

try:
    # FIXME: circular import
    from . naming import NamingElements, NamespaceManager, PoseBonesNamespace
except:
    from naming import NamingElements, NamespaceManager, PoseBonesNamespace

# 目標: カウンターによる重複名の回避を完成させる　カウンターオブジェクトに委譲
# 目標: リネームの実行を、リネームオブジェクトに委譲する

class EditableObject(ABC):  # RenamableObject
    obj_type = None
    def __init__(self, obj):
        self.obj = obj
    
# 個々のポーズボーンに関連する情報（名前、関連するアーマチュアなど）を管理し、`NamingElements`を使用して新しい名前を生成する
# EditableBoneクラスがNamingElementsを使役し、NamespaceManagerを通じて名前空間を管理する
class EditableBone(EditableObject):
    obj_type = "pose_bone"
    def __init__(self, bone):
        super().__init__(bone)
        self._init_renaming()

        # self.collection = None
        # self.color = None
    
    def _init_renaming(self):
        self.namespace_id = self.obj.id_data
        self.original_name = self.obj.name
        self.new_name = ""
        self.naming_elements = None

    def search_elements(self, naming_elements: NamingElements):
        self.naming_elements = naming_elements
        self.naming_elements.search_elements(self.original_name)

    def update_elements(self, new_elements: dict):  
        self.naming_elements.update_elements(new_elements)

    def render_name(self):
        self.new_name = self.naming_elements.render_name()
        return self.new_name

    
class RenamePoseBones:
    def __init__(self):
        self.es = NamingElements("pose_bone")
        self.nsm = NamespaceManager()

        self.rn_bones = []

    def execute_rename(self, operator: bpy.types.Operator, context: bpy.types.Context):
        selected_pose_bones = context.selected_pose_bones
        new_elements = operator.new_elements

        self.rn_bones = [EditableBone(bone) for bone in selected_pose_bones]

        for b in self.rn_bones:
            self.nsm.get_namespace(b)  # nsmがnsを作成、保持  ここにあるのは違和感
            
            b.search_elements(self.es)
            b.update_elements(new_elements)
            new_name = b.render_name()
            if self.nsm.check_duplicate(b, new_name):
                new_name = b.counter_operation(self.nsm.get_namespace(b))
                if new_name:
                    b.apply_name_change(new_name)

    def counter_operation(self, bone: EditableBone):
        return self.nsm.get_namespace(bone).counter_operation(bone)

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
