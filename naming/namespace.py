from abc import ABC, abstractmethod
import re


class Namespace:
    def __init__(self):
        self.names = set()  # ポーズボーンの名前を保持するハッシュセット

    def update_name(self, old_name, new_name):
        if old_name in self.names:
            self.names.remove(old_name)
        self.names.add(new_name)

    def add_name(self, name):
        self.names.add(name)

    def remove_name(self, name):
        self.names.remove(name)


class Namespaces(ABC):
    ns_type = None  # なんとなくつけた

    def __init__(self):
        self.namespaces = {}
        # TODO: armature以外のobjの調査
    
    @abstractmethod
    def get_namespace(self, obj):
        """If the namespace does not exist, create it."""
        raise NotImplementedError

    def update_name(self, obj, old_name, new_name):
        namespace = self.get_namespace(obj)
        namespace.update_name(old_name, new_name)

    def check_duplicate(self, obj, proposed_name):
        # if obj.name == proposed_name:
        #     return False  # 名前が変更されていない場合は、重複チェックを行わない
        namespace = self.get_namespace(obj)
        return proposed_name in namespace.names


class PoseBonesNamespaces(Namespaces):
    ns_type = "pose_bone"  # armature?

    def get_namespace(self, bone):
        armature = bone.id_data
        if armature.name not in self.namespaces:
            self.namespaces[armature.name] = Namespace()
            for pose_bone in armature.pose.bones:
                self.namespaces[armature.name].add_name(pose_bone.name)
        return self.namespaces[armature.name]
