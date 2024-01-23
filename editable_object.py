from abc import ABC, abstractmethod


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

    def search_elements(self, naming_elements):
        self.naming_elements = naming_elements
        self.naming_elements.search_elements(self.original_name)

    def update_elements(self, new_elements: dict):  
        self.naming_elements.update_elements(new_elements)

    def render_name(self):
        self.new_name = self.naming_elements.render_name()
        return self.new_name
    