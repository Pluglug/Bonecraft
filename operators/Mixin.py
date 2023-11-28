import bpy
import traceback
from ..utils.vlog import log
from ..utils.debug_flags import *
import functools


def with_mode(mode):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, context, *args, **kwargs):
            if DBG_MIXIN:
                log.header(f"Entering with_mode: Target mode = {mode}")
                log.increase()

            original_mode = context.object.mode if context.object else None
            DBG_MIXIN and log.info(f"Original mode: {original_mode}")

            try:
                if original_mode and original_mode != mode:
                    DBG_MIXIN and log.info(f"Switching mode to: {mode}")
                    bpy.ops.object.mode_set(mode=mode)

                result = func(self, context, *args, **kwargs)

            except Exception as e:
                log.error(f"Error in with_mode: {e}, Operator: {self.bl_idname}, Traceback: {traceback.format_exc()}")
                result = {'CANCELLED'}

            finally:
                DBG_MIXIN and log.decrease()
                if original_mode and context.object and context.object.mode != original_mode:
                    DBG_MIXIN and log.info(f"Restoring original mode: {original_mode}")
                    bpy.ops.object.mode_set(mode=original_mode)

            return result
        return wrapper
    return decorator


class ArmModeMixin:
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'ARMATURE' and obj.mode in {'POSE', 'EDIT'}
