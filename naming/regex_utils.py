import re
import functools


def capture_group(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        group = self.id
        return f'(?P<{group}>{func(self, *args, **kwargs)})'
    return wrapper

def maybe_with_separator(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sep = f"(?:{re.escape(self.separator)})?"
        order = self.order
        result = func(self, *args, **kwargs)
        if result:
            if order == 1:
                return f'{result}{sep}'
            else:  # order > 1:
                return f'{sep}{result}'
        else:
            return result
    return wrapper
