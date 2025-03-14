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


# class UnknownElement(NamingElement):
#     element_type = "text"

#     def build_pattern(self):
#         # TODO: プリセットに無い語を検出可能にする
#         return None
#     # 先頭から食べていく
#     # 検出時に、セパレーターで分割しながらorderを割り振る。
#     # Elementのorderは、検出時に一時的に上書きされる。


class TextElement(NamingElement):
    element_type = "text"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get("items", [])

    @maybe_with_separator
    @capture_group
    def build_pattern(self):
        return "|".join(self.items)

    def test_random_output(self):
        return self.separator, random.choice(self.items)


class PositionElement(NamingElement):
    element_type = "position"

    def apply_settings(self, settings):
        super().apply_settings(settings)
        self.items = settings.get("items", [])

    def build_pattern(self):
        sep = re.escape(self.separator)
        pattern = "|".join(self.items)

        if self.order == 1:
            return f"(?P<{self.id}>{pattern}){sep}"
        # elif self.get_order() > 1:
        else:
            return f"{sep}(?P<{self.id}>{pattern})"

    def test_random_output(self):
        return self.separator, random.choice(self.items)
