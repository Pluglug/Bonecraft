import bpy
import traceback
import functools
import contextlib

try:
    from ..debug import log, DBG_MIXIN
except:
    from debug import log, DBG_MIXIN


def with_mode(mode):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, context, *args, **kwargs):
            original_mode = context.object.mode if context.object else None
            try:
                if original_mode and original_mode != mode:
                    bpy.ops.object.mode_set(mode=mode)

                result = func(self, context, *args, **kwargs)

            except Exception as e:
                log.error(f"Error in with_mode: {e}, Operator: {self.bl_idname}, Traceback: {traceback.format_exc()}")
                result = {'CANCELLED'}

            finally:
                if original_mode and context.object and context.object.mode != original_mode:
                    bpy.ops.object.mode_set(mode=original_mode)

            return result
        return wrapper
    return decorator


class ArmModeMixin:
    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj is not None and obj.type == 'ARMATURE' and obj.mode in {'POSE', 'EDIT'}

    @contextlib.contextmanager
    def mode_context(self, context, mode):
        original_mode = context.object.mode
        bpy.ops.object.mode_set(mode=mode)
        try:
            yield
        finally:
            bpy.ops.object.mode_set(mode=original_mode)
