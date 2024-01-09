from .element_base import NamingElement
from ..regex_utils import capture_group, maybe_with_separator


class EzCounterElement(NamingElement):
    element_type = "ez_counter"
    
    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.digits = settings.get('digits', 2)
        # セパレーターとセットで識別する場合、カウンターが名前の先頭にあるとセパレーターが付与されない。
        # できれば、名前の先頭にあってほしくない。なにか制約を考える必要がある。

    @maybe_with_separator  # self.separator、つまりez_counterのセパレーターを使用
    @capture_group
    def build_pattern(self):
        # sep = re.escape(self.get_separator())
        # return f'{sep}\\d{{{self.digits}}}'  # このようにセパレーターとセットで識別することで、bl_counterとの衝突をある程度避けることができる
        return f'\\d{{{self.digits}}}' # (?=\D|$)'あえて"00"を取らせちゃう なんとかなれー 3桁以上だとダメ  # FIXME: bl_counterを拾ってしまう
    
    def standby(self):
        super().standby()
        self.value_int = None
        self.start = None
        self.end = None
        self.forward = None
        self.backward = None

    def capture(self, match):
        if match:
            self.value_int = int(self.value)
            self.start = match.start(self.name)
            self.end = match.end(self.name) 
            self.forward = match.string[match.end(self.name):]
            self.backward = match.string[:match.start(self.name)]
            return True
        return False
    
    def add(self, num):
        if num and isinstance(num, int):
            self.value_int += num
            self.value = f'{self.value_int:0{self.digits}d}'
        return self.value

    def increment(self):
        return self.add(1)

    def get_separator(self):
        return self.separator  # + "|\\."
    
    def set_value(self, int_value):
        self.value = f'{int_value:0{self.digits}d}'
        self.value_int = int_value

    def find_unused_min_counter(self, name, name_set, max_counter=9999):
        self.search(name)  # forward, backwardを更新 妥当?
        for i in range(1, max_counter + 1):
            proposed_name = f"{self.forward}{i:0{self.digits}d}{self.backward}"
            if proposed_name not in name_set:
                self.set_value(i)
                DBG_RENAME and log.info(f'  find_unused_min_counter: {self.value}')
                return True
        return False

    # CounterElement に "." をセパレータとして設定しようとした場合に、
    # BlCounterElement との衝突が起こりうることを警告するポップアップを表示
    # そもそもCounterとBlCounterを区別しないようにする? 
    # 設定を変えたときに、変換できると便利 (01 -> 00001)
    # "001"、"-01"、".A"などの開始設定 なにかExcelのオートフィルみたいなことができるモジュールはないか?
    #  "Bone-A-01", "Bone-B-02" など  マルチカウンターサポート これはcounterを高度に抽象化すればできるかもしれない

    # def get_string(self):
    #     return f'{self.value:0{self.digits}d}' if self.value else None
    
    # def replace_bl_counter(self, name, value):
    #     if BlCounterElement.search(name):
    #         return name[:BlCounterElement.start] + f'.{value:0{self.digits}d}'


class BlCounterElement(NamingElement):
    """ Buildin Blender counter pattern like ".001" """
    element_type = "bl_counter"

    def apply_settings(self, settings):
        # No settings for this element.
        self.cache_invalidated = True
        self.settings = settings

        self.identifier = 'bl_counter'
        self.order = 100  # ( ´∀｀ )b
        self.name = 'bl_counter'
        self.enabled = False  # デフォルトで名前の再構築時に無視されるようにする?
        self.digits = 3
        self.separator = "."  # The blender counter is always "." .

    @capture_group
    def build_pattern(self):
        # I don't know of any other pattern than this. Please let me know if you do.
        sep = re.escape(self.get_separator())
        return f'{sep}\\d{{{self.digits}}}$'
    
    def standby(self):
        super().standby()
        self.start = None
        self.value_int = None

    def capture(self, match):
        if match:
            self.value = match.group(self.name)
            self.start = match.start(self.name)
            self.value_int = int(self.value[1:])
            return True
        return False

    def get_separator(self):
        return self.separator
    
    def get_value_int(self) -> int:
        return int(self.value[1:]) if self.value else None  # .001 -> 001

    # def except_bl_counter(self, name):
    #     """Return the name without the bl_counter and the bl_counter value."""
    #     if self.search(name):
    #         return name[:self.start], int(self.value[1:])
    #     else:
    #         return name, None
