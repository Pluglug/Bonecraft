import bpy
from abc import ABC, abstractmethod
import re

try:
    from .. editable_object import EditableObject, EditableBone
    from . element_counter import CounterInterface, BlCounterElement, EzCounterElement
    from ..debug import log, DBG_RENAME
except:
    from editable_object import EditableObject, EditableBone
    from element_counter import CounterInterface, BlCounterElement, EzCounterElement
    from debug import log, DBG_RENAME


class Namespace(ABC):
    ns_type = None
    def __init__(self, obj):
        self.names = set()  # ハッシュセット
        self.register_namespace(obj)

    @abstractmethod
    def register_namespace(self, obj: EditableObject):
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
    
    def print_names(self):
        log.info(f'{self.__class__.__name__}: {self.names}')
    

class PoseBonesNamespace(Namespace):
    ns_type = "pose_bone"  # armature?
    def register_namespace(self, obj: EditableBone):
        if not isinstance(obj, EditableBone):
            raise ValueError(f"PoseBonesNamespace can only register EditableBone: {obj}")
        DBG_RENAME and log.header(f'Register namespace (arm: {obj.namespace_id.name})')  # DBG
        armature = obj.namespace_id
        for pose_bone in armature.pose.bones:
            self.add_name(pose_bone.name)
        DBG_RENAME and log.info(f'  Namespace registed: {self.names}')  # DBG

    def update_name(self, old_name, new_name):  # DBG
        super().update_name(old_name, new_name)  # DBG
        DBG_RENAME and log.info(f'Namespace updated: {self.names}')  # DBG


class NamespaceManager:
    # EditableObjectのnamespaceに基づいて、適切なNamespaceを割り当てる
    # 名前空間の管理と名前の重複チェック
    def __init__(self):
        self.namespaces = {}

    def get_namespace(self, obj: EditableObject):
        ns_key = self._get_namespace_key(obj)
        if ns_key not in self.namespaces:
            self.namespaces[ns_key] = self._create_namespace(obj)
        # return self.namespaces[ns_key] # self?
        r = self.namespaces[ns_key]  # DBG
        # DBG_RENAME and log.info(f'NamespaceManager.get_namespace: {r.__class__.__name__} at {id(r)}')  # DBG
        return r  # DBG
    
    # def has_namespace(self, obj: EditableObject):
    #     ns_key = self._get_namespace_key(obj)
    #     return ns_key in self.namespaces
    
    # def register_namespace(self, obj: EditableObject):
    #     ns_key = self._get_namespace_key(obj)
    #     if ns_key not in self.namespaces:
    #         self.namespaces[ns_key] = self._create_namespace(obj)
    #     self.namespaces[ns_key].register_namespace(obj)

    def _get_namespace_key(self, obj: EditableObject):
        return obj.namespace_id

    def _create_namespace(self, obj: EditableObject):
        for subclass in Namespace.__subclasses__():
            if subclass.ns_type == obj.obj_type:
                return subclass(obj)
        raise ValueError(f"Unknown namespace type: {obj.obj_type}")

    def update_name(self, obj: EditableObject, old_name, new_name):  # TODO: update_namespace
        namespace = self.get_namespace(obj)  # 未作成でも通る
        namespace.update_name(old_name, new_name)

    def check_duplicate(self, obj: EditableObject, proposed_name):
        # if obj.name == proposed_name:  # obj.nameはない。
        #     return False  # 名前が変更されていない場合は、重複チェックを行わない
        namespace = self.get_namespace(obj)
        return proposed_name in namespace.names

    def find_unused_min_counter(self, obj: EditableObject, max_counter=999):
        ez_counter = obj.naming_elements.get_element("ez_counter")
        for i in range(1, max_counter + 1):
            proposed_name = ez_counter.gen_proposed_name(i)
            if not self.check_duplicate(obj, proposed_name):
                DBG_RENAME and log.info(f'find_unused_min_counter: {i}')
                return i
        return None
    
    def counter_operation(self, obj: EditableObject):
        es = obj.naming_elements
        # こういう書き方してよいの?
        es.get_element("ez_counter").integrate_counter(es.get_element("bl_counter"))

        # bl_counter = obj.naming_elements.get_element("bl_counter")
        # ez_counter = obj.naming_elements.get_element("ez_counter")
        
        # ez_counter.integrate_counter(bl_counter)

        proposed_name = obj.render_name()  # esのrender_nameを使っていたのでnew_nameが更新されていなかった
        if self.check_duplicate(obj, proposed_name):
            available_counter = self.find_unused_min_counter(obj)
            if available_counter:
                # obj.naming_elements.update_elements({"ez_counter": available_counter})  # return new_elements: dict ?
                obj.update_elements({"ez_counter": available_counter})
                DBG_RENAME and log.info(f'counter_operation: available_counter: {available_counter} {obj.name} -> {obj.new_name}')
            else:
                raise ValueError(f"Cannot find available counter for {proposed_name}")
        # return obj.naming_elements.render_name()

    def resolve_name_conflicts(self, obj: EditableObject):
        proposed_name = obj.naming_elements.render_name()
        if self.check_duplicate(obj, proposed_name):
            available_counter = self.find_unused_min_counter(obj)
            if available_counter:
                # obj.naming_elements.update_elements({"ez_counter": available_counter})
                obj.update_elements({"ez_counter": available_counter})
            else:
                raise ValueError(f"Cannot find available counter for {proposed_name}")
    
    def print_namespaces(self):
        for ns_id, ns in self.namespaces.items():
            log.info(f'Namespace: {ns_id}')
            ns.print_names()
