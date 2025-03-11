from abc import ABC, abstractmethod
import random

from .debug import log, DBG_RENAME


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
        self.name = self.obj.name
        self.new_name = ""
        self.namespace_manager = None
        self.naming_elements = None
        self.updated = False

    def standby(self, naming_elements, namespace_manager):
        self.naming_elements = naming_elements
        self.namespace_manager = namespace_manager
        return self

    def get_namespace(self):
        self.namespace_manager.get_namespace(self)
        return self

    def search_elements(self):
        self.naming_elements.search_elements(self.name)
        return self

    def update_elements(self, new_elements: dict):
        self.new_name = self.naming_elements.update_elements(new_elements).render_name()
        DBG_RENAME and log.info(f"update_elements: {self.name} -> {self.new_name}")
        self.updated = True
        return self

    def update_namespace(self):
        if self.updated:
            self.namespace_manager.update_name(self, self.name, self.new_name)
            DBG_RENAME and log.info(f"update_namespace: {self.name} -> {self.new_name}")
            self.updated = False
        return self

    def render_name(self) -> str:
        self.new_name = self.naming_elements.render_name()
        return self.new_name

    def counter_operation(self):
        self.namespace_manager.counter_operation(self)
        return self

    def confirm_rename(self):
        return self.name, self.new_name

    def convert_to_random(self):
        if self.name and self.new_name:
            self.obj.name = str(random.randint(0, 1000000))
        return self

    def apply_name_change(self):
        self.obj.name = self.new_name
        # self.update_namespace()  # タイミング注意

    def dbg_ns_id(self):  # DBG
        return id(self.namespace_id)  # DBG

    def dbg_es_id(self):  # DBG
        return id(self.naming_elements)  # DBG
