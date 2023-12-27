import random
import itertools

from debug import log, DBG_PARSE


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

# TODO: 将来的に、接頭語などではなく、順番で指定できるようにする
# これによって、さらに柔軟な名前の組み合わせを生成できるようになる
rename_preset = {
    "prefix": ["CTRL", "DEF", "MCH"],
    "middle": ["Arm", "Leg", "Spine", "Hand", "Foot", "Head", "Finger", "Toe", "Hoge_Hoge"],
    "suffix": ["Tweak", "Pole"],
    "counter_settings": {
        "enabled": True, 
        "digits": 2
    },
    "side_pair_settings": {
        "side_pair": "L|R",
        "side_separator": ".",
        "side_position": "SUFFIX"
    },
    "common_settings": {"common_separator": "_"}
}


def random_test_names(preset, num_cases=10):
    """ランダムな名前を生成する"""
    test_names = []
    for _ in range(num_cases):
        name_parts = []

        # 接頭語
        if preset['prefixes'] and random.choice([True, False]):
            name_parts.append(random.choice(preset['prefixes']))

        # 中間語
        if preset['middle_words']:
            name_parts.append(random.choice(preset['middle_words']))

        # 接尾語
        if preset['suffixes'] and random.choice([True, False]):
            name_parts.append(random.choice(preset['suffixes']))

        # カウンター
        if preset['counter_settings']['enabled']:
            counter_format = f"{{:0{preset['counter_settings']['digits']}d}}"
            name_parts.append(counter_format.format(random.randint(1, 10)))

        test_names.append(preset['common_settings']['common_separator'].join(name_parts))

        # 左右識別子を追加
        if preset['side_pair_settings']['side_pair'] and random.choice([True, False]):
            if preset['side_pair_settings']['side_position'] == 'PREFIX':
                test_names[-1] = random.choice(preset['side_pair_settings']['side_pair']) + \
                    preset['side_pair_settings']['side_separator'] + test_names[-1]
            else:
                test_names[-1] += preset['side_pair_settings']['side_separator'] + \
                    random.choice(preset['side_pair_settings']['side_pair'])            

    return test_names

# print(random_test_names(rename_preset, 10))


def generate_test_names(preset):
    """全ての組み合わせの名前を生成する"""
    test_cases = []
    sep = preset["common_settings"]["common_separator"]
    side_sep = preset["side_pair_settings"]["side_separator"]
    side_position = preset["side_pair_settings"]["side_position"]

    # 各要素のリストを作成
    prefixes = preset["prefixes"] + [None]
    middle_words = preset["middle_words"]
    suffixes = preset["suffixes"] + [None]
    sides = list(preset["side_pair_settings"]["side_pair"]) + [None]
    
    counters = [f'{random.randint(1, 99):02d}' if preset["counter_settings"]["enabled"] else None for _ in range(10)]

    # 要素の組み合わせを生成
    for elements in itertools.product([True, False], repeat=4):
        parts = []
        if elements[0]:  # 接頭語
            parts.append(random.choice(prefixes))
        parts.append(random.choice(middle_words))  # 中間語は常に存在
        if elements[1]:  # 接尾語
            parts.append(random.choice(suffixes))
        if elements[2]:  # カウンター
            parts.append(random.choice(counters))

        base_name = sep.join(filter(None, parts))

        if elements[3]:  # 左右識別子
            side = random.choice(sides)
            if side:
                if side_position == 'SUFFIX':
                    base_name += f'{side_sep}{side}'
                else:  # 'PREFIX'
                    base_name = f'{side}{side_sep}{base_name}'

        test_cases.append(base_name)

    return test_cases


def generate_test_names_all_cases(preset):
    """プリセット内の全ての組み合わせの名前を生成する"""
    test_cases = []
    sep = preset["common_settings"]["common_separator"]
    side_sep = preset["side_pair_settings"]["side_separator"]
    side_position = preset["side_pair_settings"]["side_position"]

    # 各要素の組み合わせを生成
    prefixes = preset["prefixes"] + [None]
    middle_words = preset["middle_words"] + [None]
    suffixes = preset["suffixes"] + [None]
    sides = list(preset["side_pair_settings"]["side_pair"]) + [None]
    counters = [f'{i:02d}' for i in range(1, 100)] if preset["counter"]["enabled"] else [None]

    # 全ての組み合わせを生成
    for prefix, middle, suffix, counter, side in itertools.product(prefixes, middle_words, suffixes, counters, sides):
        parts = [p for p in [prefix, middle, suffix, counter] if p]
        name = sep.join(parts)

        if side_position == 'SUFFIX' and side:
            name = f"{name}{side_sep}{side}" if name else side
        elif side_position == 'PREFIX' and side:
            name = f"{side}{side_sep}{name}" if name else side

        if name:
            test_cases.append(name)

    return test_cases
