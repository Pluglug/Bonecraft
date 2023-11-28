import contextlib
import inspect
import os

# from .addon import ADDON_ID
ADDON_ID = "bonecraft"  # bpy.context.preferences.addons[__name__].bl_info['name']


CONSOLE_COLOR_INFO = '\033[34m'
CONSOLE_COLOR_ERROR = '\033[31m'
CONSOLE_COLOR_HEADER = '\033[1;32m'
CONSOLE_COLOR_WARNING = '\033[33m'


class VisualLog:
    def __init__(self):
        self.indent_level = 0
        self.inspect_enabled = False

    def enable_inspect(self):
        self.inspect_enabled = True

    def disable_inspect(self):
        self.inspect_enabled = False

    def _get_caller_info(self):
        if not self.inspect_enabled:
            return ""

        frame = inspect.currentframe()
        caller_frames = inspect.getouterframes(frame)
        current_script = os.path.basename(__file__)

        for outer_frame in caller_frames:
            module_name = outer_frame.filename
            if current_script not in module_name:
                line_number = outer_frame.lineno
                module_name = module_name if ADDON_ID in module_name else "Unknown module"
                module_name = os.path.relpath(module_name, os.path.dirname(__file__))
                return f"{module_name}:{line_number}: "
        return "Unknown module: "

    def _log(self, color, *args):
        caller_info = self._get_caller_info()
        indent = "    " * self.indent_level
        msg = caller_info + indent + ", ".join(str(arg) for arg in args)
        print(color + msg + '\033[0m')

    def header(self, msg):
        header_title = ADDON_ID
        header_length = max(len(msg), len(header_title))
        header = '-' * (header_length // 2 - len(header_title) // 2) + header_title + '-' * (header_length // 2 - len(header_title) // 2)

        print("")
        self._log(CONSOLE_COLOR_HEADER, header)
        self._log(CONSOLE_COLOR_HEADER, msg)

    def info(self, *args):
        self._log(CONSOLE_COLOR_INFO, *args)

    def error(self, *args):
        self._log(CONSOLE_COLOR_ERROR, *args)

    def warning(self, *args):
        self._log(CONSOLE_COLOR_WARNING, *args)

    @contextlib.contextmanager
    def indented(self):
        self.increase()
        try:
            yield
        finally:
            self.decrease()

    def increase(self):
        self.indent_level += 1

    def decrease(self):
        if self.indent_level > 0:
            self.indent_level -= 1

    def reset_indent(self):
        self.indent_level = 0


log = VisualLog()


# log.header(*args)
# log.info(*args)
# log.error(*args)
# log.warning(*args)


if __name__ == "__main__":
    pass
