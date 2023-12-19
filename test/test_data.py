import bpy

test_bone_names = [
    "Arm.L", "Leg.R", "Spine_01", "Hand.l", "Foot.r", "Head", "Finger01.L", "Toe01.R"
]

# test_selected_pose_bones = [
#      bpy.data.objects['SubArmature'].pose.bones["Bone"],
#      bpy.data.objects['MyArmature'].pose.bones["Root"],
#      bpy.data.objects['MyArmature'].pose.bones["Hand.l"],
#      bpy.data.objects['MyArmature'].pose.bones["Spine_01"],
#      bpy.data.objects['MyArmature'].pose.bones["Leg.R"],
#      bpy.data.objects['MyArmature'].pose.bones["Arm.L"],
#      bpy.data.objects['MyArmature'].pose.bones["Tail"],
#      bpy.data.objects['MyArmature'].pose.bones["Hand.l.001"],
#      bpy.data.objects['MyArmature'].pose.bones["Hand.l.002"],
#      bpy.data.objects['MyArmature'].pose.bones["Finger01.L"],
#      bpy.data.objects['MyArmature'].pose.bones["Finger02.L"]
# ]

rename_preset = {
    "prefixes": ["CTRL", "DEF", "MCH"],
    "middle_words": ["Arm", "Leg", "Spine", "Hand", "Foot", "Head", "Finger", "Toe"],
    "suffixes": ["Tweak", "Pole"],
    "counter": {"digits": 2},
    "side_pair_settings": {
        "side_pair": "LR",
        "side_separator": ".",
        "side_position": "SUFFIX"
    },
    "common_separator": {"separator": "_"}
}
