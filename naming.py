import re
import bpy

from debug import log, DBG_PARSE

from naming_test_utils import rename_preset, random_test_names, generate_test_names


class NameParser:
    def __init__(self, preset):
        self.preset = preset
        self.sep = re.escape(self.preset["common_settings"]["common_separator"])
    
    def build_element_pattern(self, element_type):
        try:
            build_func = getattr(self, f'build_{element_type}_pattern')
        except AttributeError:
            raise AttributeError(f'build_{element_type}_pattern is not defined')
        
        return build_func()

    def build_prefix_pattern(self):
        prefix_pattern = '|'.join(self.preset['prefixes'])
        return f'(?P<prefix>{prefix_pattern}){self.sep}'  

    def build_middle_pattern(self):
        middle_pattern = '|'.join(map(re.escape, self.preset['middle_words']))
        return f'(?:{self.sep})?(?P<middle>{middle_pattern})'

    def build_suffix_pattern(self):
        suffix_pattern = '|'.join(self.preset['suffixes'])
        return f'(?:{self.sep})?(?P<suffix>{suffix_pattern})'

    def build_counter_pattern(self):
        counter_pattern = r'\d{' + str(self.preset['counter_settings']['digits']) + '}'
        return f'(?:{self.sep})?(?P<counter>{counter_pattern})'

    def build_side_pattern(self):
        side_sep = re.escape(self.preset["side_pair_settings"]["side_separator"])
        side_position = self.preset["side_pair_settings"]["side_position"]
        side_pattern = self.preset['side_pair_settings']['side_pair']
        
        if side_position == 'PREFIX':
            return f'(?P<side>{side_pattern}){side_sep}'
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<side>{side_pattern})'
    
    def search_elements(self, name, element_types):
        elements = {element: None for element in element_types}
        for part in element_types:
            elements[part] = self.search_element(name, part)
        return elements

    def search_element(self, name, element_type):
        pattern = self.build_element_pattern(element_type)
        regex = re.compile(pattern)
        match = regex.search(name)
        if match:
            # TODO: 後続処理のための情報を得る
            return match.group(element_type)
        else:
            return None

    def test_parse_elements(self, name_list):
        import time
        log.header("Testing NameParser")
        log.info("Start time:", time.strftime("%Y/%m/%d %H:%M:%S"))  # TODO: vlogで実装

        element_types = ['prefix', 'middle', 'suffix', 'counter', 'side']
        for name in name_list:
            parsed_name = self.search_elements(name, element_types)
            log.header("Parsed name: " + name)
            log.info(f"Parsed name: {parsed_name}")


if __name__ == "__main__":
    # testings
    parser = NameParser(rename_preset)

    # rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    test_names = generate_test_names(rename_preset)
    parser.test_parse_elements(test_names)
