import bpy
from . Mixin import ArmModeMixin, with_mode

from debug import log, DBG_OPS, log_exec

class BONECRAFT_OT_ParentSet(ArmModeMixin, bpy.types.Operator):
    """
    Attach selected bones with a specific parent type.
    This operator can be used in both Edit Mode and Pose Mode, facilitating various rigging operations.
    """
    bl_idname = "bonecraft.parent_set"
    bl_label = "Set Parent"
    bl_options = {'REGISTER', 'UNDO'}

    parent_type: bpy.props.EnumProperty(
        name="Parent Type",
        description="Type of parenting",
        items=[
            ('OFFSET', "Offset", ""),
            ('CONNECTED', "Connected", "")
        ],
        default='OFFSET'
    )

    @with_mode('EDIT')
    @log_exec
    def execute(self, context):
        DBG_OPS and log.info(f"Parent type: {self.parent_type}")
        bpy.ops.armature.parent_set(type=self.parent_type)
        return {'FINISHED'}


class BONECRAFT_OT_ParentClear(ArmModeMixin, bpy.types.Operator):
    """
    Detach selected bones with a specific clear type.
    This operator can be used in both Edit Mode and Pose Mode, facilitating various rigging operations.
    """
    bl_idname = "bonecraft.parent_clear"
    bl_label = "Clear Parent"
    bl_options = {'REGISTER', 'UNDO'}

    clear_type: bpy.props.EnumProperty(
        name="Clear Type",
        description="Type of clear parenting",
        items=[
            ('CLEAR', "Clear", ""),
            ('DISCONNECT', "Disconnect", "")
        ],
        default='CLEAR'
    )

    @with_mode('EDIT')
    @log_exec
    def execute(self, context):
        DBG_OPS and log.info(f"Parent type: {self.clear_type}")
        bpy.ops.armature.parent_clear(type=self.clear_type)
        return {'FINISHED'}


class BONECRAFT_OT_AddConstraint(ArmModeMixin, bpy.types.Operator):
    """
    Add a constraint to the active bone
    This operator can be used in both Edit Mode and Pose Mode, facilitating various rigging operations.
    """
    bl_idname = "bonecraft.add_constraint"
    bl_label = "Add Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    enum_items = None

    # Not classmethod by anyone's standards.
    # @classmethod
    def get_constraint_items(self, context):
        if not BONECRAFT_OT_AddConstraint.enum_items:
            items = []
            for constraint in bpy.types.Constraint.bl_rna.properties['type'].enum_items:
                items.append((constraint.identifier, constraint.name, constraint.description))  # iconも取れる

            BONECRAFT_OT_AddConstraint.enum_items = items

        return BONECRAFT_OT_AddConstraint.enum_items

    constraint_type: bpy.props.EnumProperty(
        name="Constraint Type",
        description="Type of constraint to add",
        items=get_constraint_items
    )

    with_targets: bpy.props.BoolProperty(
        name="With Targets",
        description="Set target objects/bones for the constraint",
        default=False
    )

    # TODO: 追加したコンストレイントを一時的に表示し簡単な編集ができるようにする
    @with_mode('POSE')
    @log_exec
    def execute(self, context):
        DBG_OPS and log.info(f"Adding constraint: Type = {self.constraint_type}, With Targets = {self.with_targets}")
        if self.with_targets:
            bpy.ops.pose.constraint_add_with_targets(type=self.constraint_type)
        else:
            bpy.ops.pose.constraint_add(type=self.constraint_type)
        return {'FINISHED'}



class BONECRAFT_OT_CopyConstraints(ArmModeMixin, bpy.types.Operator):
    """
    Copy constraints from active to selected bones
    This operator can be used in both Edit Mode and Pose Mode, facilitating various rigging operations.
    """
    bl_idname = "bonecraft.copy_constraints"
    bl_label = "Copy Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @with_mode('POSE')
    @log_exec
    def execute(self, context):
        bpy.ops.pose.constraints_copy()
        return {'FINISHED'}


class BONECRAFT_OT_ClearConstraints(ArmModeMixin, bpy.types.Operator):
    """
    Clear all constraints from selected bones
    This operator can be used in both Edit Mode and Pose Mode, facilitating various rigging operations.
    """
    bl_idname = "bonecraft.clear_constraints"
    bl_label = "Clear Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @with_mode('POSE')
    @log_exec
    def execute(self, context):
        bpy.ops.pose.constraints_clear()
        return {'FINISHED'}



operator_classes = [
    BONECRAFT_OT_ParentSet,
    BONECRAFT_OT_ParentClear,
    BONECRAFT_OT_AddConstraint,
    BONECRAFT_OT_CopyConstraints,
    BONECRAFT_OT_ClearConstraints
]


if __name__ == "__main__":
    pass
