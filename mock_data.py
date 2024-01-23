import os, sys
sys.path.append(os.path.dirname(__file__))

from editable_object import EditableBone
from naming import PoseBonesNamespace


class MockPoseBone:
    """BlenderのPoseBoneを模倣するモッククラス"""
    def __init__(self, name, id_data):
        self.name = name
        self.id_data = id_data

class MockPose:
    """BlenderのPoseを模倣するモッククラス"""
    def __init__(self, armature, bone_names):
        # 辞書を使用してボーン名とMockPoseBoneオブジェクトをマッピング
        self.id_data = armature
        self.bones = {name: MockPoseBone(name, self.id_data) for name in bone_names}

    def __iter__(self):
        return iter(self.bones.values())

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

# import bpy

# bone = bpy.context.selected_pose_bones[0]
# armature = bone.id_data
# for pose_bone in armature.pose.bones:  # .values():も有効
#     print(pose_bone.name)

# >>> Bone
# >>> Bone.001
# >>> Bone.002
# >>> Bone.003
# >>> Bone.004
# >>> Bone.005