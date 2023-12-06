from debug.vlog import log
from debug.debug_utils import log_exec

from debug.debug_flags import *


flags = []
for name in dir():
    if name.startswith("DBG"):
        flags.append(name)


__all__ = ["log"]
__all__ += ["log_exec"]

__all__ += flags


if __name__ == "__main__":
    print(__all__)
