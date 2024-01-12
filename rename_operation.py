import bpy

from . naming import NamingElements, PoseBonesNamespaces


class BoneInfo:
    def __init__(self, pose_bone):
        self.pose_bone = pose_bone
        self.namespace = pose_bone.id_data
        self.original_name = pose_bone.name
        self.new_name = ""

        self.naming_elements = None
        
        # 今後の拡張
        self.collection = None
        self.color = None

        # boneがapplyするべき?


class BoneToRename:
    def __init__(self, pose_bone):
        self.pose_bone = pose_bone
        self.namespace = pose_bone.id_data
        self.original_name = pose_bone.name
        self.new_name = ""

        self.naming_elements = None
    
    def search_elements(self, naming_elements: NamingElements):
        self.naming_elements = naming_elements
        self.naming_elements.search_elements(self)

    def apply_name_change(self):
        self.pose_bone.name = self.new_name
        # self.namespace.update_name(self.original_name, self.new_name)
        # Elementと同じように、Boneも自身のorg_name, new_nameを保持
        # control側で、apply_name_changeを呼び出す namespace更新はどうする?

class RenamePoseBones:
    def __init__(self):
        self.es = NamingElements("pose_bone")
        self.ns = PoseBonesNamespaces()

        self.original_names = []
        self.new_names = []

    def execute_rename(self, operator: bpy.types.Operator, context: bpy.types.Context):
        selected_pose_bones = context.selected_pose_bones
        new_elements = operator.new_elements

        for bone in selected_pose_bones:
            b = BoneInfo(bone)
            self.es.search_elements(b)
            self.es.update_elements(new_elements)
            new_name = self.es.render_name()
            if self.check_duplicate_names(b, new_name):
                new_name = self.es.counter_operation(b)
                if new_name:
                    self.es.apply_name_change(b, new_name)
            else:
                self.es.apply_name_change(b, new_name)