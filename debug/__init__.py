"""Debugging utilities for the project."""
from .vlog import log
from .debug_utils import log_exec

from .debug_flags import *


__all__ = ["log"]
__all__ += ["log_exec"]

# Collect all DBG_* flags
__all__ += [name for name in globals() if name.startswith("DBG")]


# Usage:
# from debug import log, DBG_HOGE
# DBG_HOGE and log.header("Start processing...").increase()
# for item in data_list:
#     DBG_HOGE and log.info("Processing item:", item, "Status:", process_status)
