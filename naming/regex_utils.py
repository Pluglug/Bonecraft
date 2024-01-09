import functools


def capture_group(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        group = self.name
        return f'(?P<{group}>{func(self, *args, **kwargs)})'
    return wrapper

def maybe_with_separator(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        # エスケープした方が良いかも
        sep = f"(?:{self.get_separator()})?"
        order = self.get_order()
        result = func(self, *args, **kwargs)
        if result:
            if order == 1:
                return f'{result}{sep}'
            # elif order > 1:
            else:
                return f'{sep}{result}'
        else:
            return result
    return wrapper
