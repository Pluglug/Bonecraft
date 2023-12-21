import re
import bpy

from debug import log, DBG_PARSE

from naming_test_utils import rename_preset, random_test_names, generate_test_names


class NameParser:
    def __init__(self, preset):
        self.preset = preset
        self.regex = None

    def build_prefix_pattern(self, sep):
        prefix_pattern = '|'.join(self.preset['prefixes'])
        return f'(?P<prefix>{prefix_pattern}){sep}'  

    def build_middle_pattern(self, sep):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle_words']))
        return f'(?:{sep})?(?P<middle>{middle_pattern})'

    def build_suffix_pattern(self, sep):
        suffix_pattern = '|'.join(self.preset['suffixes'])
        return f'(?:{sep})?(?P<suffix>{suffix_pattern})'

    def build_counter_pattern(self, sep):
        counter_pattern = r'\d{' + str(self.preset['counter']['digits']) + '}'
        return f'(?:{sep})?(?P<counter>{counter_pattern})'

    def build_side_pattern(self, side_position, side_sep):
        side_pattern = '[' + self.preset['side_pair_settings']['side_pair'] + ']'
        if side_position == 'PREFIX':
            return f'(?P<side>{side_pattern}){side_sep}'
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<side>{side_pattern})'

    def parse_elements(self, name):
        elements = {'prefix': None, 'middle': None, 'suffix': None, 'counter': None, 'side': None}
        DBG_PARSE and log.header("Parsing name: " + name)
        # 各要素を検索
        for part in ['prefix', 'middle', 'suffix', 'counter']:
            elements[part] = self.search_element(name, part)
            DBG_PARSE and log.warning(f"Found {part}: {elements[part]}") if elements[part] else log.info(f"Found {part}: {elements[part]}")

        elements['side'] = self.serch_side_element(name, 'side')
        DBG_PARSE and log.warning(f"Found side: {elements['side']}") if elements['side'] else log.info(f"Found side: {elements['side']}")
        
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

    def test_parse_elements(self, name_list):
        log.header("Testing NameParser")
        for name in name_list:
            parsed_name = self.parse_elements(name)


if __name__ == "__main__":
    # testings

    # 開始時に時刻を表示
    import time
    log.header("Start testing NameParser")
    log.info("Start time:", time.strftime("%Y/%m/%d %H:%M:%S"))

    parser = NameParser(rename_preset)

    rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    test_names = generate_test_names(rename_preset)
    parser.test_parse_elements(test_names)
