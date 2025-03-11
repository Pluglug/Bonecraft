from abc import ABC, abstractmethod
import re
import random


try:
    from .element_base import NamingElement
    from .regex_utils import capture_group, maybe_with_separator
    from ..debug import log, DBG_RENAME
except:
    from element_base import NamingElement
    from regex_utils import capture_group, maybe_with_separator
    from debug import log, DBG_RENAME


from abc import ABC, abstractmethod


class CounterInterface(ABC):
    """Interface for CounterElement."""

    @property
    @abstractmethod
    def value(self) -> str:
        """
        Returns the current value of the counter.
        """
        pass

    @value.setter
    @abstractmethod
    def value(self, value):
        """
        Sets the counter's current value.
        """
        pass

    @property
    @abstractmethod
    def value_int(self) -> int:
        """
        Returns the current integer value of the counter.
        """
        pass

    @value_int.setter
    @abstractmethod
    def value_int(self, value):
        """
        Sets the counter's current value.
        """
        pass

    def _update_counter_values(self, value):
        """Ensuring sync between value and value_int."""
        self._value, self._value_int = self._parse_value(value)

    def _parse_value(self, value: "str|int") -> tuple[str, int]:
        if value is None:
            return None, None

        try:
            value_int = int(value)
            value_str = f"{value_int:0{self.digits}d}"
            return value_str, value_int
        except ValueError:
            log.error(f"Value '{value}' cannot be converted.")
            return None, None

    def add(self, value: "str|int"):
        if isinstance(value, (int, str)):
            _, num_int = self._parse_value(value)
            if num_int is not None:
                new_value_int = self.value_int + num_int
                if new_value_int >= 0:
                    self.value_int = new_value_int
        else:
            raise ValueError(
                f"Cannot add type {type(value).__name__} to {type(self).__name__}."
            )

    # # 将来的に、特殊メソッドを使用してNEのvalueなどをもっと扱いやすくしたい
    # def __add__(self, other):
    #     """
    #     Implements addition (+).
    #     Args:
    #         other (int or str): The value to add to the counter.
    #     """
    #     if isinstance(other, (int, str)):
    #         self.add(other)
    #     else:
    #         raise ValueError(f"Cannot add type {type(other).__name__} to EzCounterElement.")
    #     return self

    # def __iadd__(self, other):
    #     """
    #     Implements in-place addition (+=).
    #     Args:
    #         other (int or str): The value to add to the counter.
    #     """
    #     if isinstance(other, (int, str)):
    #         self.add(other)
    #     else:
    #         raise ValueError(f"Cannot add type {type(other).__name__} to EzCounterElement.")
    #     return self

    def integrate_counter(self, source_counter: NamingElement):
        """
        Integrates the value from a given source counter into this counter.
        Args:
            source_counter (NamingElement): The counter to be integrated.
        """

        if not isinstance(source_counter, CounterInterface):
            raise ValueError(
                f"source_counter must be a CounterInterface, not {type(source_counter).__name__}"
            )

        if source_counter.value is None:
            # Continue to use own value if the source counter has no value.
            return

        # Add or transfer the source counter's value and reset the source counter.
        if self.value is not None:
            # self.add(source_counter.value_int)
            pass
        else:
            self.value = source_counter.value_int
        source_counter.value = None  # Reset the source counter.

    @abstractmethod
    def gen_proposed_name(self, i: int) -> str:
        """
        Generates a proposed name using the current counter value.
        Used to find an available counter value.
        """
        pass


# TODO: EzとBlのカウンターを統合する  Indexerとかにする?
class EzCounterElement(NamingElement, CounterInterface):
    element_type = "ez_counter"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.digits = settings.get("digits", 2)
        # セパレーターとセットで識別する場合、カウンターが名前の先頭にあるとセパレーターが付与されない。
        # bl_counterとの区別ができないため、名前の先頭にあってほしくない。なにか制約を考える必要がある。

    @maybe_with_separator
    @capture_group
    def build_pattern(self):
        return (
            f"\\d{{{self.digits}}}"  # FIXME: bl_counterを拾ってしまう foo.001 -> foo-00
        )

    def standby(self):
        super().standby()
        self._value_int = None
        self.start = None
        self.end = None
        self.forward = None
        self.backward = None

    def capture(self, match):
        if match:
            self._value = match.group(self.id)
            self._value_int = int(self.value)
            self.start = match.start(self.id)
            self.end = match.end(self.id)
            self.forward = match.string[: self.start]
            self.backward = match.string[self.end :]
            return True
        return False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._update_counter_values(value)

    @property
    def value_int(self):
        # CounterElement holds both the string and integer representation of the counter.
        return self._value_int

    @value_int.setter
    def value_int(self, value):
        self._update_counter_values(value)

    def gen_proposed_name(self, i: int) -> str:
        """Generates a proposed name using the given index."""
        return f"{self.forward}{i:0{self.digits}d}{self.backward}"

    def test_random_output(self):
        # return self.separator, f'{random.randint(0, 10 ** self.digits - 1):0{self.digits}d}'
        return self.separator, f"{random.randint(1, 15):0{self.digits}d}"


class BlCounterElement(NamingElement, CounterInterface):  # sys_counterとかにする?
    """Buildin Blender counter pattern like ".001" """

    # right-most dot-number
    element_type = "bl_counter"

    def apply_settings(self, settings):
        # No settings for this element.
        self.cache_invalidated = True

        self._id = "bl_counter"
        self._order = 100  # とにかく最後にあってほしい
        self._enabled = False  # デフォルトで名前の再構築時に無視されるようにする?
        self._separator = "."  # The blender counter is always "." .
        self.digits = 3

    @capture_group
    def build_pattern(self):
        # I don't know of any other pattern than this. Please let me know if you do.
        sep = re.escape(self.separator)
        return f"{sep}\\d{{{self.digits}}}$"

    def standby(self):
        super().standby()
        self._value_int = None
        self.start = None
        self.forward = None

    def capture(self, match):
        if match:
            self._value = match.group(self.id)[1:]  # drop the dot
            self._value_int = int(self.value[1:])
            self.start = match.start(self.id)
            self.forward = match.string[: self.start] + self.separator  # need separator
            return True
        return False

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._update_counter_values(value)

    @property
    def value_int(self):
        # CounterElement holds both the string and integer representation of the counter.
        return self._value_int

    @value_int.setter
    def value_int(self, value):
        self._update_counter_values(value)

    def gen_proposed_name(self, i):
        return f"{self.forward}{i:0{self.digits}d}"

    def test_random_output(self):
        # return self.separator, f'{random.randint(0, 10 ** self.digits - 1):0{self.digits}d}'
        return self.separator, f"{random.randint(1, 15):0{self.digits}d}"

    # 末尾のデフォルトカウンター 順序入れ替え可能なカスタムカウンター
    # CounterElement に "." をセパレータとして設定しようとした場合に、
    # BlCounterElement との衝突が起こりうることを警告するポップアップを表示
    # そもそもCounterとBlCounterを区別しないようにする?
    # 設定を変えたときに、変換できると便利 (01 -> 00001)
    # "001"、"-01"、".A"などの開始設定 なにかExcelのオートフィルみたいなことができるモジュールはないか?
    #  "Bone-A-01", "Bone-B-02" など  マルチカウンターサポート これはcounterを高度に抽象化すればできるかもしれない


if __name__ == "__main__":
    # testings
    def alphabet_sequence_generator(start="a"):
        current = start
        while True:
            yield current
            next_char = chr(ord(current[-1]) + 1)
            current = current[:-1] + next_char if next_char <= "z" else current + "a"

    gen = alphabet_sequence_generator("a")
    for _ in range(5):
        print(next(gen))  # a, b, c, d, e
