import re
import bpy

from debug import log
DBG_PARSE = True


# test preset
rename_preset = {
    "prefixes": ["CTRL", "DEF", "MCH"],
    "middle_words": ["Arm", "Leg", "Spine", "Hand", "Foot", "Head", "Finger", "Toe", "Hoge_Hoge"],
    "suffixes": ["Tweak", "Pole"],
    "counter": {"digits": 2},
    "side_pair_settings": {
        "side_pair": "LR",
        "side_separator": ".",
        "side_position": "SUFFIX" # PREFIX or SUFFIX
    },
    "common_separator": {"separator": "_"}
}


class NameParser:
    def __init__(self, preset):
        self.preset = preset
        self.regex = None
        DBG_PARSE and log.header("Initializing NameParser")        
        self.compile_pattern()

    def compile_pattern(self):
        self.regex = re.compile(
            self.build_pattern()
        )
        DBG_PARSE and log.info("Generated regex pattern:", self.regex)

    def build_pattern(self):
        sep = re.escape(self.preset["common_separator"]["separator"])
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        side_position = self.preset["side_pair_settings"]["side_position"]
        # FIXME: ここでside_positionを判定しているのはよくない
        # どうにかしてbuild_side_patternを一つにまとめたい
        # FIXME: カウンターがない場合、"Hand.L"は認識せず、かわりに"Hand_.L"が認識されるようになってしまう

        pattern_parts = [
            self.build_side_pattern(side_position, side_sep) if side_position == 'PREFIX' else None,
            self.build_prefix_pattern(sep),
            self.build_middle_pattern(sep),
            self.build_suffix_pattern(sep),
            self.build_counter_pattern(),
            self.build_side_pattern(side_position, side_sep) if side_position == 'SUFFIX' else None
        ]

        return '^' + ''.join(filter(None, pattern_parts)) + '$'

    def build_prefix_pattern(self, sep):
        prefix_pattern = '|'.join(self.preset['prefixes'])
        return f'(?:(?P<prefix>{prefix_pattern}){sep})?'

    def build_middle_pattern(self, sep):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle_words']))
        return f'(?:(?P<middle>{middle_pattern}){sep})?'

    def build_suffix_pattern(self, sep):
        suffix_pattern = '|'.join(self.preset['suffixes'])
        return f'(?:(?P<suffix>{suffix_pattern}){sep})?'

    def build_counter_pattern(self):
        counter_pattern = r'\d{' + str(self.preset['counter']['digits']) + '}'
        return f'(?:(?P<counter>{counter_pattern}))?'

    def build_side_pattern(self, side_position, side_sep):
        side_pattern = '[' + self.preset['side_pair_settings']['side_pair'] + ']'
        if side_position == 'PREFIX':
            return f'(?:(?P<side>{side_pattern}){side_sep})?'
        elif side_position == 'SUFFIX':
            return f'(?:{side_sep}(?P<side>{side_pattern}))?'

    def parse(self, name):
        match = self.regex.match(name)
        if match:
            return match.groupdict()
        else:
            return None

    def test_parse(self, name_list):
        log.header("Testing NameParser")
        for name in name_list:
            parsed_name = self.parse(name)
            log.info(name + ": " + str(parsed_name))


# testings

# rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

parser = NameParser(rename_preset)

test_names_suf = [
    "CTRL_Arm_01.L",
    "DEF_Hoge_Hoge_01.L",
    "DEF_Leg_Tweak_01.R",
    "MCH_Spine_01",
    "Hand.L",
    "Hand_.L",
]

# test_names_pre = [
#     "L.Arm_01",
#     "L.CTRL_Hoge_Hoge_01",
#     "R.Leg_Tweak_01",
#     "Spine_01",
#     "L.Hand"
# ]

parser.test_parse(test_names_suf)
