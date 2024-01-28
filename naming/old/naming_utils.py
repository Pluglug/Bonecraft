import re

from naming import NameParser
from naming.old.naming_test_utils import rename_preset, random_test_names, generate_test_names

from debug import log, DBG_PARSE


class StricterNameParser(NameParser):
    def __init__(self, preset):
        self.preset = preset
        self.regex = None
        self.compile_full_pattern()

    @staticmethod
    def optional(pattern):
        return f'(?:{pattern})?'

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
        counter_pattern = r'\d{' + str(self.preset['counter_settings']['digits']) + '}'
        return f'(?:{sep})?(?P<counter>{counter_pattern})'

    def build_side_pattern(self, side_position, side_sep):
        side_pattern = self.preset['side_pair_settings']['side_pair']
        if side_position == 'PREFIX':
            return f'(?P<side>{side_pattern}){side_sep}'
        elif side_position == 'SUFFIX':
            return f'{side_sep}(?P<side>{side_pattern})'

    def compile_full_pattern(self):
        DBG_PARSE and log.header("Compiling NameParser full pattern")
        self.regex = re.compile(
            self.build_full_pattern()
        )
        DBG_PARSE and log.info(self.regex)

    def build_full_pattern(self):
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

    def parse_full_pattern(self, name):
        match = self.regex.match(name)
        if match:
            return match.groupdict()
        else:
            return None

    def test_parse(self, name_list):
        log.header("Testing NameParser")
        for name in name_list:
            parsed_name = self.parse_full_pattern(name)
            if parsed_name:
                log.info(str(parsed_name) + " <- " + name)
            else:
                log.warning(str(parsed_name) + " <- " + name)
