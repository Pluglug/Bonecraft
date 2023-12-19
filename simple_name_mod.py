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
        self.compile_pattern()

    def compile_pattern(self):
        DBG_PARSE and log.header("Compiling NameParser pattern")
        self.regex = re.compile(
            self.build_pattern()
        )
        DBG_PARSE and log.info("Generated regex pattern:", self.regex)

    def build_pattern(self):
        sep = re.escape(self.preset["common_separator"]["separator"])
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        side_position = self.preset["side_pair_settings"]["side_position"]
        # TODO: build_side_pattern()内でside_positionを判定するようにする
        pattern_parts = [
            self.build_side_pattern(side_position, side_sep) if side_position == 'PREFIX' else None,
            self.build_prefix_pattern(sep),
            self.build_middle_pattern(sep),
            self.build_suffix_pattern(sep),
            self.build_counter_pattern(sep),
            self.build_side_pattern(side_position, side_sep) if side_position == 'SUFFIX' else None
        ]

        return '^' + ''.join(filter(None, pattern_parts)) + '$'

    def build_prefix_pattern(self, sep):
        prefix_pattern = '|'.join(self.preset['prefixes'])
        return f'(?:(?P<prefix>{prefix_pattern}){sep})?'  # "CTRL_"

    def build_middle_pattern(self, sep):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle_words']))
        # return f'(?:(?:{sep})?(?P<middle>{middle_pattern})(?:{sep})?)?'  # "_Arm_"
        return f'(?:(?P<middle>{middle_pattern}))?'  # "Arm"

    def build_suffix_pattern(self, sep):
        suffix_pattern = '|'.join(self.preset['suffixes'])
        return f'(?:(?:{sep})?(?P<suffix>{suffix_pattern}))?'  # "_Tweak"

    def build_counter_pattern(self, sep):
        counter_pattern = r'\d{' + str(self.preset['counter']['digits']) + '}'
        return f'(?:(?:{sep})?(?P<counter>{counter_pattern}))?'  # "_01"

    def build_side_pattern(self, side_position, side_sep):
        side_pattern = '[' + self.preset['side_pair_settings']['side_pair'] + ']'
        if side_position == 'PREFIX':
            return f'(?:(?P<side>{side_pattern})){side_sep}?'  # "L."
        elif side_position == 'SUFFIX':
            return f'(?:(?:{side_sep})?(?P<side>{side_pattern}))?'  # ".L"

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
            if parsed_name:
                log.info(str(parsed_name) + " <- " + name)
            else:
                log.warning(str(parsed_name) + " <- " + name)


# testings

# 開始時に時刻を表示
import time
log.header("Start testing NameParser")
log.info("Start time:", time.strftime("%Y/%m/%d %H:%M:%S"))


parser = NameParser(rename_preset)

test_names_suf = [
    "CTRL_Arm_01.L",
    "DEF_Hoge_Hoge_01.L",
    "DEF_Leg_Tweak_01.R",
    "MCH_Spine_01",
    "Hand.L",
    "Hand_.L",
    "Hand",
    "_Hand",
]

parser.test_parse(test_names_suf)

rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

parser.compile_pattern()

test_names_pre = [
    "L.Arm_01",
    "L.CTRL_Hoge_Hoge_01",
    "R.Leg_Tweak_01",
    "Spine_01",
    "L.Hand",
    "L._Hand",
    "Hand",
]

parser.test_parse(test_names_pre)
