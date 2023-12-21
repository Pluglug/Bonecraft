import re
import bpy

from debug import log
DBG_PARSE = True

from test import test_data as td

rename_preset = td.rename_preset


class NameParser:
    def __init__(self, preset):
        self.preset = preset
        self.regex = None
        # self.compile_pattern()

    def compile_pattern(self):
        DBG_PARSE and log.header("Compiling NameParser pattern")
        self.regex = re.compile(
            self.build_pattern()
        )
        DBG_PARSE and log.info(self.regex)

    def build_pattern(self):
        sep = re.escape(self.preset["common_separator"]["separator"])
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        side_position = self.preset["side_pair_settings"]["side_position"]
        pattern_parts = [
            self.build_side_pattern(side_position, side_sep) \
                if side_position == 'PREFIX' else None,
            self.optional(self.build_prefix_pattern(sep)),
            self.optional(self.build_middle_pattern(sep)),
            self.optional(self.build_suffix_pattern(sep)),
            self.optional(self.build_counter_pattern(sep)) \
                if self.preset["counter"]["enabled"] else None,
            self.build_side_pattern(side_position, side_sep) \
                if side_position == 'SUFFIX' else None
        ]

        return '^' + ''.join(filter(None, pattern_parts)) + '$'
    
    @staticmethod
    def optional(pattern):
        return f'(?:{pattern})?'

    def build_prefix_pattern(self, sep):
        prefix_pattern = '|'.join(self.preset['prefixes'])
        # return f'(?:(?P<prefix>{prefix_pattern}){sep})?'  # "CTRL_"
        return f'(?P<prefix>{prefix_pattern}){sep}'


    def build_middle_pattern(self, sep):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle_words']))
        # return f'(?:(?:{sep})?(?P<middle>{middle_pattern}))?'  # "_Arm"
        return f'(?:{sep})?(?P<middle>{middle_pattern})'


    def build_suffix_pattern(self, sep):
        suffix_pattern = '|'.join(self.preset['suffixes'])
        # return f'(?:(?:{sep})?(?P<suffix>{suffix_pattern}))?'  # "_Tweak"
        return f'(?:{sep})?(?P<suffix>{suffix_pattern})'


    def build_counter_pattern(self, sep):
        counter_pattern = r'\d{' + str(self.preset['counter']['digits']) + '}'
        # return f'(?:(?:{sep})?(?P<counter>{counter_pattern}))?'  # "_01"
        return f'(?:{sep})?(?P<counter>{counter_pattern})'


    def build_side_pattern(self, side_position, side_sep):
        side_pattern = '[' + self.preset['side_pair_settings']['side_pair'] + ']'
        if side_position == 'PREFIX':
            return f'(?P<side>{side_pattern}){side_sep}'  # "L."
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<side>{side_pattern})'

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

    def parse_elements(self, name):
        elements = {'prefix': None, 'middle': None, 'suffix': None, 'counter': None, 'side': None}
        DBG_PARSE and log.header("Parsing name: " + name)
        # 各要素を検索
        for part in ['prefix', 'middle', 'suffix', 'counter']:  # , 'side']:  # TODO: side_separatorを考慮
            elements[part] = self.search_element(name, part)
            DBG_PARSE and log.info(f"Found {part}: {elements[part]}")

        elements['side'] = self.serch_side_element(name, 'side')
        DBG_PARSE and log.info(f"Found side: {elements['side']}")
        
        return elements

    def search_element(self, name, element_type):
        pattern = getattr(self, f'build_{element_type}_pattern')(self.preset["common_separator"]["separator"])
        regex = re.compile(pattern)
        match = regex.search(name)
        if match:
            # TODO: 後続処理のための情報を得る
            return match.group(element_type)
        else:
            return None
    
    def serch_side_element(self, name, element_type):
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        pattern = self.build_side_pattern(self.preset["side_pair_settings"]["side_position"], side_sep)
        regex = re.compile(pattern)
        match = regex.search(name)
        if match:
            return match.group(element_type)
        else:
            None

    def modify_name(self, name, modifications):
        # 名前の任意の部分を変更する処理（例: 追加、削除、置換など）
        pass

    def test_parse_elements(self, name_list):
        log.header("Testing NameParser")
        for name in name_list:
            parsed_name = self.parse_elements(name)
            # if parsed_name:
            #     log.info(str(parsed_name) + " <- " + name)
            # else:
            #     log.warning(str(parsed_name) + " <- " + name)


def test():
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
        "Spine_01",
        "MCH_Spine_01",
        "Hand.L",
        # "Hand_.L",
        "Hand",
        "_Hand",
        "Leg_Tweak"
    ]
    log.info("side_position: SUFFIX")
    # parser.test_parse(test_names_suf)
    parser.test_parse_elements(test_names_suf)

    rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    # parser.compile_pattern()

    test_names_pre = [
        "L.Arm_01",
        "L.CTRL_Hoge_Hoge_01",
        "R.Leg_Tweak_01",
        "Spine_01",
        "CTRL_Spine_01",
        "L.Hand",
        "L._Hand",
        "Hand",
    ]
    log.info("side_position: PREFIX")
    # parser.test_parse(test_names_pre)
    parser.test_parse_elements(test_names_pre)


    rename_preset["counter"]["enabled"] = False

    # parser.compile_pattern()

    test_names_no_counter = [
        "L.Arm",
        "L.CTRL_Hoge_Hoge.001",
        "R.Leg_Tweak",
        "Spine_01",
        "CTRL_Spine.001",
        "L.Hand",
        "L._Hand.001",
        "Hand",
    ]

    log.info("side_position: SUFFIX, counter: disabled")
    # parser.test_parse(test_names_no_counter)

    parser.test_parse_elements(test_names_no_counter)
