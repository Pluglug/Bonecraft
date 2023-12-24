import re
import bpy

from debug import log, DBG_PARSE

from naming_test_utils import rename_preset, random_test_names, generate_test_names


class BoneData:
    def __init__(self, **kwargs):
        self.attributes = kwargs

    # def get(self, key, default=None):
    #     return self.attributes.get(key, default)

    # def set(self, key, value):
    #     self.attributes[key] = value

    def __getitem__(self, key):
        return self.attributes[key]

    def __setitem__(self, key, value):
        self.attributes[key] = value
    
    def __delitem__(self, key):
        del self.attributes[key]

    def __contains__(self, key):
        return key in self.attributes

    def keys(self):
        return self.attributes.keys()
    
    def values(self):
        return self.attributes.values()
    
    def items(self):
        return self.attributes.items()
    
    def __getattr__(self, name):
        try:
            return self.attributes[name]
        except KeyError:
            raise AttributeError(f'{name} is not defined')

    def __setattr__(self, name, value):
        if name == 'attributes':
            super().__setattr__(name, value)
        else:
            self.attributes[name] = value
    
    def __repr__(self):
        attrs = ', '.join(f'{k}={v!r}' for k, v in self.attributes.items())
        return f'{self.__class__.__name__}({attrs})'


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
            return {
                'value': match.group(element_type),
                'type': element_type,
                'start': match.start(element_type),
                'end': match.end(element_type),
                'remainder': name[:match.start(element_type)] + name[match.end(element_type):]
            }
            # return NamingElement(
            #     value=match.group(element_type),
            #     type=element_type,
            #     start=match.start(element_type),
            #     end=match.end(element_type),
            #     remainder=name[:match.start(element_type)] + name[match.end(element_type):]
            # )
        else:
            return None

    def test_parse_elements(self, name_list):
        import time
        log.header("Testing NameParser")
        log.info("Start time:", time.strftime("%Y/%m/%d %H:%M:%S"))  # TODO: vlogで実装

        element_types = ['prefix', 'middle', 'suffix', 'counter', 'side']
        for name in name_list:
            log.header("Parsing: " + name)
            parsed_name = self.search_elements(name, element_types)
            log.info(f"Parsed name: {parsed_name}")


class PoseBones:
    def __init__(self, armature):
        self.armature = armature
        self.bones = self.armature.pose.bones




if __name__ == "__main__":
    # -----test parse-----
    log.enable_inspect()
    parser = NameParser(rename_preset)

    # rename_preset["side_pair_settings"]["side_position"] = "PREFIX"

    test_names = generate_test_names(rename_preset)
    parser.test_parse_elements(test_names)



    # # -----test NamingElement-----
    # DBG_PARSE = False
    # parser = NameParser(rename_preset)
    # test_name = "MCH_Toe_Tweak_12.R"
    # elements = parser.search_elements(test_name, ['prefix', 'middle', 'suffix', 'counter', 'side'])
    # # log.info(elements)

    # # 抽出した要素に対する操作の例
    # for key, element in elements.items():
    #     if element:
    #         # 名前の要素に関する情報をログに記録
    #         log.info(f"{key}: {element}")

    #         # 特定の要素に対する操作
    #         if key == 'counter':
    #             # カウンター値を変更
    #             new_counter_value = int(element.value) + 1
    #             # element.set('value', str(new_counter_value))  # set method
    #             # element.value = str(new_counter_value)  # __setattr__ method
    #             element['value'] = str(new_counter_value)  # __setitem__ method
    #             # setattr(element, 'value', str(new_counter_value))  # __setattr__ method
    #             log.info(f"Updated counter: {element}")
    #             break
