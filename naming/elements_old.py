# class NamingElements:  #(ABC)
#     # elements_type = None
#     def __init__(self, obj_type, settings):
#         # 将来、typeで何をビルドするか指示される。mesh, material, bone, etc...
#         self.elements = self.build_elements(obj_type, settings)  # TODO: obj_typeの扱いを考える
#         self.ns = PoseBonesNamespaces()
#         self.namespace = None

#     def build_elements(self, obj_type, settings):
#         elements = []
#         elements_type = f"{obj_type}_elements"
#         for element_settings in settings[elements_type]:
#             element_type = element_settings["type"]
#             element = self.create_element(element_type, element_settings)
#             elements.append(element)

#         elements.append(BlCounterElement({}))  # これはハードコードで良い
#         elements.sort(key=lambda e: e.get_order())
#         DBG_RENAME and log.info( \
#             f'build_elements: {elements_type}:\n' + '\n'.join([f'  {e.identifier}: {e.name}' for e in elements]))
#         return elements

#     def get_element_classes(self):
#         element_classes = {}  # 再利用する場合はキャッシュ
#         subclasses = NamingElement.__subclasses__()  # TODO: obj_typeに適したサブクラスを取得する必要がある
#         for subclass in subclasses:
#             element_type = getattr(subclass, 'element_type', None)
#             if element_type:
#                 element_classes[element_type] = subclass
#         return element_classes

#     def create_element(self, element_type, settings):
#         element_classes = self.get_element_classes()
#         element_class = element_classes.get(element_type, None)
#         if element_class:
#             return element_class(settings)
#         else:
#             raise ValueError(f"Unknown element type: {element_type}")

#     # def search_elements(self, name):
#     #     DBG_RENAME and log.header(f'search_elements: {name}', False)
#     #     for element in self.elements:
#     #         element.standby()
#     #         element.search(name)

#     def search_elements(self, bone):
#         self.namespace = self.ns.get_namespace(bone)
#         name = bone.name
#         DBG_RENAME and log.header(f'search_elements: {name}', False)
#         for element in self.elements:
#             element.standby()
#             element.search(name)
#         # return ??? 何かしら返すと使いやすいかも

#     def update_elements(self, new_elements: dict=None):
#         if not new_elements and not isinstance(new_elements, dict):
#             return

#         for element in self.elements:
#             if element.name in new_elements:
#                 element.value = new_elements[element.name] or None

#     def render_name(self):
#         elements_parts = [element.render() for element in self.elements \
#                           if element.is_enabled() and element.value]
#         name_parts = []
#         for sep, value in elements_parts:
#             if name_parts:
#                 name_parts.append(sep)
#             name_parts.append(value)
#         name = ''.join(name_parts)
#         DBG_RENAME and log.info(f'render_name: {name}')
#         return name

#     def apply_name_change(self, obj, new_name):
#         old_name = obj.name
#         obj.name = new_name
#         self.namespace.update_name(obj, old_name, new_name)

#     def check_duplicate_and_update_counter(self, proposed_name, namespace):
#         pass # TODO: ここから作業

#     def counter_operation(self, bone):
#         bl_counter = next((e for e in self.elements if isinstance(e, BlCounterElement)), None)
#         ez_counter = next((e for e in self.elements if isinstance(e, EzCounterElement)), None)

#         if bl_counter.value:
#             if ez_counter.value:  # bl_counterとez_counterの両方が存在する場合
#                 DBG_RENAME and log.info(f'  existing bl_counter and ez_counter: {bl_counter.value}, {ez_counter.value}')
#                 ez_counter.add(bl_counter.get_value_int())  # ez_counter + bl_counter  # もしかしたら不要 1からカウンターを探すプロセスに統一する?どちらが効率的か?
#                 bl_counter.value = None
#             else:  # bl_counterのみ存在
#                 DBG_RENAME and log.info(f'  existing bl_counter: {bl_counter.value}')
#                 ez_counter.set_value(bl_counter.get_value())
#                 bl_counter.value = None
#             proposed_name = self.render_name()  # この時点で、名前は完成しているはず
#             if self.check_duplicate_names(proposed_name):  # 重複チェック
#                 if ez_counter.find_unused_min_counter(proposed_name, self.ns.get_namespace(bone)):
#                     return self.render_name()
#                 else:
#                     log.error(f'  counter operation failed: {bl_counter.value}')
#                     return None

#         elif ez_counter.value:  # ez_counterのみの存在
#             DBG_RENAME and log.info(f'  existing ez_counter: {ez_counter.value}')
#             proposed_name = self.render_name()  # この時点で、名前は完成しているはず
#             if self.check_duplicate_names(proposed_name):
#                 if ez_counter.find_unused_min_counter(proposed_name, self.namespace.names):
#                     return self.render_name()
#                 else:
#                     log.error(f'  counter operation failed: {ez_counter.value}')
#                     return None

#         else:  # カウンターの不在
#             DBG_RENAME and log.info(f'  no existing counter')
#             proposed_name = self.render_name()  # カウンターの不在の場合は、名前は完成しているはず
#             if self.check_duplicate_names(proposed_name):
#                 if ez_counter.find_unused_min_counter(proposed_name, self.namespace.names):
#                     return self.render_name()
#                 else:
#                     log.error(f'  counter operation failed: {ez_counter.value}')
#                     return None

#     def check_duplicate_names(self, name):
#         return name in self.namespace.names

#     def chenge_all_settings(self, new_settings):
#         for element in self.elements:
#             element.change_settings(new_settings)

#     def update_caches(self):
#         for element in self.elements:
#             if element.cache_invalidated:
#                 element.update_cache()

#     def print_elements(self, name):
#         self.search_elements(name)
#         for element in self.elements:
#             log.info(f"{element.identifier}: {element.value}")

#     # # -----counter operations-----
#     # @staticmethod
#     # def check_duplicate_names(bone):
#     #     return bone.name in (b.name for b in bone.id_data.pose.bones)

#     # def replace_bl_counter(self, elements):
#     #     if 'bl_counter' in elements:
#     #         num = self.get_bl_counter_value(elements)
#     #         elements['counter'] = {'value': self.get_counter_string(num)}
#     #         del elements['bl_counter']
#     #     return elements

#     # # 名前の重複を確認しながら、カウンターをインクリメントしていく
#     # def increment_counter(self, bone, elements):  # boneもしくはarmature 明示的なのは...
#     #     # ここでboneが絶対に必要になる interfaceでboneもelementsも扱えるようにしたい
#     #     counter_value = self.get_counter_value(elements)
#     #     while self.check_duplicate_names(bone):
#     #         counter_value += 1
#     #         elements['counter']['value'] = self.get_counter_string(counter_value)
#     #     return elements
