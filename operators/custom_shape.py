import bpy
from ..debug import log as Log

MESH_SHAPE = {
    'Plane': {'primitive_plane_add': {'size': 0.5}},
    'Circle': {'primitive_circle_add': {'radius': 0.5, 'vertices': 8}},
    'Cube': {'primitive_cube_add': {'size': 0.5}},
    'UVSphere': {'primitive_uv_sphere_add': {'radius': 0.5}},
    'ICOSphere': {'primitive_ico_sphere_add': {'radius': 0.5, 'subdivisions': 1}},
}

def create_mesh_shape(shape='Plane', **kwargs):
    if shape in MESH_SHAPE:
        ops_func = getattr(bpy.ops.mesh, list(MESH_SHAPE[shape].keys())[0])
        ops_func(**MESH_SHAPE[shape][list(MESH_SHAPE[shape].keys())[0]], **kwargs)
    else:
        raise ValueError(f"Invalid shape: {shape}")

def edit_custom_shape(): # (self, context):
    context = bpy.context
    armature = context.active_object
    # Operator Poll
    if armature.type != 'ARMATURE' or context.mode != 'POSE' \
            or len(context.selected_pose_bones) != 1:
        return
    
    p_bone = context.active_pose_bone

    # Retrieved from operator properties and add-on preferences
    new_shape_type = 'Circle'  

    create_mesh_shape(new_shape_type, rotation=(1.5708, 0, 0))  # Y-UP

    # Apply Y-UP rotation
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

    mesh_obj = context.active_object
    mesh_obj.name = f"cs_user_{p_bone.name}"

    # TODO: 存在確認を一度に行い、ロジックを簡略化
    if not p_bone.custom_shape:
        # カスタムシェイプが未設定の場合は新規作成
        p_bone.custom_shape = mesh_obj
    else:
        # 既存のカスタムシェイプがある場合
        if p_bone.custom_shape.name == mesh_obj.name:
            # 既にユーザー編集済みのカスタムシェイプがある場合はリンク
            mesh_obj.data = p_bone.custom_shape.data
        else:
            # 新規作成または異なるカスタムシェイプが設定されている場合
            mesh_obj.data = p_bone.custom_shape.data.copy()
            p_bone.custom_shape = mesh_obj

    # custom propにアーマチュアとボーン名を記録
    mesh_obj['linked_armature'] = armature.name
    mesh_obj['linked_bone'] = p_bone.name

    if (t := p_bone.custom_shape_transform) is not None:
        # Override transformが設定されている場合はそれを適用
        base_matrix = armature.matrix_world @ t.matrix
    else:
        # Override transformが設定されていない場合はボーンの姿勢を適用
        base_matrix = armature.matrix_world @ p_bone.matrix

    # トランスフォームオフセット
    from mathutils import Matrix, Euler
    translation_matrix = Matrix.Translation(p_bone.custom_shape_translation)
    rotation_matrix = Euler(p_bone.custom_shape_rotation_euler).to_matrix().to_4x4()
    mesh_obj.matrix_world = armature.matrix_world @ base_matrix @ translation_matrix @ rotation_matrix

    mesh_obj.scale *= p_bone.custom_shape_scale_xyz
    mesh_obj.scale *= p_bone.length if p_bone.use_custom_shape_bone_size else 1.0

    # MeshEditモードへの切り替え
    bpy.ops.object.mode_set(mode='EDIT')
    # フェイス削除
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    
    
    bpy.ops.mesh.select_mode(type='VERT')
    bpy.ops.mesh.select_all(action='SELECT')

    # ハンドラーの登録
    # handler = PostShapeEditActionHandler(mesh_obj)
    # handler.start()

    bpy.app.handlers.depsgraph_update_post.append(gen_post_shape_edit_handler(mesh_obj))
    Log.header("hide_custom_shape_on_mode_change Started.", title="Handler")


# def hide_custom_shape_on_mode_change(scene, depsgraph):
#     active_obj = bpy.context.active_object
#     if active_obj and active_obj.type == 'MESH' and bpy.context.object.mode == 'OBJECT':
#         # オブジェクトを非表示に設定
#         active_obj.hide_viewport = True
#         active_obj.hide_render = True
        
#         # 再選択
#         if active_obj.get('linked_armature', None):
#             armature = bpy.data.objects.get(active_obj['linked_armature'])
#             if armature:
#                 bpy.context.view_layer.objects.active = armature
#                 bpy.ops.object.mode_set(mode='POSE')
#                 bone = armature.pose.bones.get(active_obj['linked_bone'])
#                 if bone:
#                     bone.bone.select = True
#         bpy.app.handlers.depsgraph_update_post.remove(hide_custom_shape_on_mode_change)


def gen_post_shape_edit_handler(target_obj):
    def handler(scene, depsgraph):
        def hide(obj):
            obj.hide_viewport = True
            obj.hide_render = True
        
        def reselect_linked_bone(obj):
            if arm := bpy.data.objects.get(obj['linked_armature'], None):
                bpy.context.view_layer.objects.active = arm
                bpy.ops.object.mode_set(mode='POSE')
                bone = arm.pose.bones.get(obj['linked_bone'])
                if bone:
                    bone.bone.select = True
        # TODO: 早期リターンを追加 条件分岐の見直し
        try:
            current_obj = bpy.context.active_object
            current_mode = bpy.context.mode

            if current_obj != target_obj or current_mode != 'EDIT_MESH':
                if current_obj.type == 'MESH' and current_mode == 'OBJECT':
                    Log.info("Move from Edit to Object mode.")
                    hide(target_obj)
                    reselect_linked_bone(target_obj)
                elif current_obj.type == 'ARMATURE' and current_mode == 'POSE':
                    Log.info("Move from Edit to Pose mode.")
                    hide(target_obj)
                else:
                    print(f"Exceptional state: {current_obj.name} is in {current_mode} mode.")

                if handler in bpy.app.handlers.depsgraph_update_post:
                    bpy.app.handlers.depsgraph_update_post.remove(handler)
                    Log.footer(title="hide_custom_shape_on_mode_change Stopped.")
        except Exception as e:
            print(f"Error occurred: {e}")
            bpy.app.handlers.depsgraph_update_post.remove(handler)
    return handler
