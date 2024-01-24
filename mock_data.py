import os, sys
sys.path.append(os.path.dirname(__file__))

from collections.abc import MutableMapping
from typing import List, Dict, Union, Any, Optional, Tuple, Iterable, Iterator, Callable

from editable_object import EditableBone
from naming import PoseBonesNamespace


class MockPoseBone:
    """BlenderのPoseBoneを模倣するモッククラス"""
    def __init__(self, name, armature):
        self.name = name
        self.id_data = armature

class MockPose(MutableMapping):
    """BlenderのPoseを模倣するモッククラス"""
    def __init__(self, armature, bone_names):
        self._bones = {name: MockPoseBone(name, armature) for name in bone_names}
        self._keys = list(self._bones.keys())

    @property
    def bones(self):
        return self._bones

    def __getitem__(self, key):
        if isinstance(key, int):
            # インデックスでのアクセス
            key = self._keys[key]
        return self._bones[key]

    def __setitem__(self, key, value):
        self._bones[key] = value
        self._keys = list(self._bones.keys())

    def __delitem__(self, key):
        del self._bones[key]
        self._keys = list(self._bones.keys())

    def __iter__(self):
        return iter(self._bones.values())

    def __len__(self):
        return len(self._bones)

    def keys(self):
        return self._bones.keys()

    def values(self):
        return self._bones.values()

    def items(self):
        return self._bones.items()

class MockArmature:
    """BlenderのArmatureを模倣するモッククラス"""
    def __init__(self, name, bone_names):
        self.name = name
        self.pose = MockPose(self, bone_names)


# テスト用のMockArmatureオブジェクトを作成
my_armature = MockArmature('MyArmature', ["Root", "Hand.l", "Spine_01", "Leg.R", "Arm.L", "Tail"])
sub_armature = MockArmature('SubArmature', ["Bone", "Bone.001", "Bone.002", "Bone.003"])


test_selected_pose_bones = [
    my_armature.pose.bones["Root"],
    my_armature.pose.bones["Hand.l"],
    my_armature.pose.bones["Spine_01"],
    # my_armature.pose.bones["Leg.R"],
    # my_armature.pose.bones["Arm.L"],
    # my_armature.pose.bones["Tail"],
    # my_armature.pose.bones["Hand.l.001"],
    # my_armature.pose.bones["Hand.l.002"],
    # my_armature.pose.bones["Finger01.L"],
    # my_armature.pose.bones["Finger02.L"],
    # sub_armature.pose.bones["Bone"],
    # sub_armature.pose.bones["Bone.001"],
    # sub_armature.pose.bones["Bone.002"],
    # sub_armature.pose.bones["Bone.003"],
]

from debug import log

bone = test_selected_pose_bones[0]
armature = bone.id_data
for pose_bone in armature.pose.bones:
    log.info(pose_bone.name)

# # import bpy

# # bone = bpy.context.selected_pose_bones[0]
# # armature = bone.id_data
# # for pose_bone in armature.pose.bones:  # .values():も有効
# #     print(pose_bone.name)

# # >>> Bone
# # >>> Bone.001
# # >>> Bone.002
# # >>> Bone.003
# # >>> Bone.004
# # >>> Bone.005
    


class CustomPropCollection:
    def __init__(self):
        self._items = {}
        self._keys = []

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._items[self._keys[key]]
        elif isinstance(key, str):
            return self._items[key]
        else:
            raise TypeError("Invalid key type.")

    def __iter__(self):
        for key in self._keys:
            yield self._items[key]

    def __len__(self):
        return len(self._items)

    def add(self, key, value):
        if key not in self._items:
            self._keys.append(key)
        self._items[key] = value

    def keys(self):
        return self._keys

    def values(self):
        return [self._items[key] for key in self._keys]

    def items(self):
        return [(key, self._items[key]) for key in self._keys]

# 使用例
collection = CustomPropCollection()
collection.add("Root", MockPoseBone("Root", None))
collection.add("Hand.l", MockPoseBone("Hand.l", None))

# インデックスでアクセス
print(collection[0].name)  # => "Root"

# キーでアクセス
print(collection["Hand.l"].name)  # => "Hand.l"

# イテレート
for bone in collection:
    print(bone.name)

# keys, values, items
print(collection.keys())
print(collection.values())
print(collection.items())