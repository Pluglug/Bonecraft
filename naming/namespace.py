import bpy
from abc import ABC, abstractmethod
import re

from .. rename_operation import EditableObject, EditableBone


class Namespace(ABC):
    ns_type = None
    # EOサブクラスを指定する案  `issubclass(obj_class, subclass.tgt_class)`
    # tgt_class = EditableObject  
    def __init__(self, obj):
        self.names = set()  # ハッシュセット

    @abstractmethod
    def register_namespace(self, obj):
        """Implement a way to get a names from an object."""
        raise NotImplementedError

    def update_name(self, old_name, new_name):
        if old_name in self.names:
            self.names.remove(old_name)
        self.names.add(new_name)

    def add_name(self, name):
        self.names.add(name)

    def remove_name(self, name):
        self.names.remove(name)

    def check_duplicate(self, proposed_name):
        return proposed_name in self.names
    

class PoseBonesNamespace(Namespace):
    ns_type = "pose_bone"  # armature?
    def register_namespace(self, obj: EditableBone):
        if isinstance(obj, EditableBone):
            armature = obj.id_data
            for pose_bone in armature.pose.bones:
                self.add_name(pose_bone.name)


class NamespaceManager:
    def __init__(self):
        self.namespaces = {}

    def get_namespace(self, obj: EditableObject):
        ns_key = self._get_namespace_key(obj)
        if ns_key not in self.namespaces:
            self.namespaces[ns_key] = self._create_namespace(obj)
        return self.namespaces[ns_key]

    def _get_namespace_key(self, obj):
        return obj.namespace

    def _create_namespace(self, obj):
        for subclass in Namespace.__subclasses__():
            if subclass.ns_type == obj.obj_type:
                return subclass(obj)
        raise ValueError(f"Unknown namespace type: {obj.obj_type}")

    # def update_name(self, obj, old_name, new_name):
    #     namespace = self.get_namespace(obj)
    #     namespace.update_name(old_name, new_name)

    def check_duplicate(self, obj, proposed_name):
        # if obj.name == proposed_name:
        #     return False  # 名前が変更されていない場合は、重複チェックを行わない
        namespace = self.get_namespace(obj)
        return proposed_name in namespace.names
