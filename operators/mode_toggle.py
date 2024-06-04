import bpy


class ModeToggleUtils:
    @staticmethod
    def get_linked_armature(rigged_object) -> bpy.types.Object:
        for modifier in rigged_object.modifiers:
            if modifier.type == 'ARMATURE':
                return modifier.object
        return None

    @staticmethod
    def get_rigged_mesh(armature) -> bpy.types.Object:
        for child in armature.children:
            if child.type == 'MESH':
                if MTU.get_linked_armature(child) == armature:
                    return child
        return None

    @staticmethod
    def get_active_bone_name(context) -> str:
        bone = context.active_bone or context.active_pose_bone or None
        return bone.name if bone else None

    @staticmethod
    def switch_mode(context, target_object, mode='OBJECT', secondary_object=None):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        target_object.select_set(True)
        secondary_object and secondary_object.select_set(True)
        context.view_layer.objects.active = target_object
        bpy.ops.object.mode_set(mode=mode)


MTU = ModeToggleUtils


class BONECRAFT_OT_mode_toggle(bpy.types.Operator):
    bl_idname = "bonecraft.mode_toggle"
    bl_label = "Toggle Mode (Armature/Mesh)"
    bl_description = "Toggle between Armature and Mesh mode"
    bl_options = {'REGISTER', 'UNDO'}

    armature_mode: bpy.props.EnumProperty(
        name="Armature Mode",
        items=[
            ('EDIT', "Edit", "Edit mode"),
            ('POSE', "Pose", "Pose mode")
        ]
    )
    rigged_mesh_mode: bpy.props.EnumProperty(
        name="Mesh Mode",
        items=[
            ('EDIT', "Edit", "Edit mode"),
            ('WEIGHT_PAINT', "Weight Paint", "Weight Paint mode")
        ]
    )
    add_new_vertex_group: bpy.props.BoolProperty(
        name="Add New Vertex Group",
        description="Add a new vertex group if the active bone does not have one",
        default=True
    )

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type in {'ARMATURE', 'MESH'}

    def execute(self, context):
        ao = context.active_object
        
        if ao.type == 'ARMATURE':
            if (mesh := MTU.get_rigged_mesh(ao)):
                return self.switch_to_mesh_mode(context, ao, mesh)
            self.report({'ERROR'}, "Active armature does not have a rigged mesh")

        elif ao.type == 'MESH':
            if (arm := MTU.get_linked_armature(ao)):
                return self.switch_to_armature_mode(context, arm)
            self.report({'ERROR'}, "Active mesh is not rigged to an armature")
        
        else:
            self.report({'ERROR'}, "Active object is not an Armature or Mesh")        
        return {'CANCELLED'}
    
    def switch_to_armature_mode(self, context, target_armature):
        MTU.switch_mode(context, target_armature, self.armature_mode)
        return {'FINISHED'}
    
    def switch_to_mesh_mode(self, context, reference_armature, target_mesh):
        active_bone_name = MTU.get_active_bone_name(context)

        MTU.switch_mode(context, target_mesh, 
                        self.rigged_mesh_mode, reference_armature)

        if active_bone_name and self.rigged_mesh_mode == 'WEIGHT_PAINT':
            if (vg := target_mesh.vertex_groups.get(active_bone_name, None)):
                bpy.ops.object.vertex_group_set_active(group=active_bone_name)
            else:
                if self.add_new_vertex_group:
                    vg = target_mesh.vertex_groups.new(name=active_bone_name)
                    bpy.ops.object.vertex_group_set_active(group=vg.name)
                    self.report({'INFO'}, f"Created new vertex group: {vg.name}")
                else:
                    self.report({'INFO'}, f"Active bone '{active_bone_name}' does not have a vertex group")
        return {'FINISHED'}


class BONECRAFT_OT_enter_weight_paint_mode(bpy.types.Operator):
    bl_idname = "bonecraft.enter_weight_paint_mode"
    bl_label = "Enter Weight Paint Mode"
    bl_description = "Enter Weight Paint mode with the active bone's vertex group selected"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        ao = context.active_object
        return ao is not None and ao.type == 'MESH'

    def execute(self, context):
        ao = context.active_object

        if (arm := MTU.get_linked_armature(ao)):
            MTU.switch_mode(context, ao, 'WEIGHT_PAINT', arm)
        else:
            bpy.ops.object.mode_set(mode='WEIGHT_PAINT', toggle=True)

        return {'FINISHED'}


operator_classes = [
    BONECRAFT_OT_mode_toggle,
    BONECRAFT_OT_enter_weight_paint_mode
]
