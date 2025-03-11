import bpy


def get_ui_types_from_error():
    try:
        # 無効な値を設定してエラーを発生させる
        bpy.context.area.ui_type = "invalid_ui_type"
    except TypeError as e:
        # エラーメッセージから利用可能なUIエリアタイプを取得
        message = str(e)
        start = message.find("(") + 1
        end = message.find(")")
        ui_types = message[start:end].replace("'", "").split(", ")

    return ui_types


def set_constraints(
    armature_name, source_prefix, target_prefix, constraint_type="COPY_TRANSFORMS"
):
    # アーマチュアオブジェクトを取得
    armature = bpy.data.objects.get(armature_name)
    if not armature or armature.type != "ARMATURE":
        print(f"Error: {armature_name} is not an armature object.")
        return

    # アーマチュアのポーズボーンを繰り返し処理
    for bone in armature.pose.bones:
        # 接頭語が一致するかチェック
        if bone.name.startswith(source_prefix):
            target_bone_name = bone.name.replace(source_prefix, target_prefix, 1)
            target_bone = armature.pose.bones.get(target_bone_name)

            # ターゲットボーンが存在する場合、コンストレイントを追加
            if target_bone:
                constraint = bone.constraints.new(type=constraint_type)
                constraint.target = armature
                constraint.subtarget = target_bone_name
            else:
                print(f"Target bone {target_bone_name} not found.")


# スクリプトの実行
# 例: アーマチュア名'Armature', 接頭語'Def-', 'Tgt-', コンストレイントタイプ'COPY_TRANSFORMS'
# set_constraints('Armature', 'DEF', 'TRG')


if __name__ == "__main__":
    # 使用可能なUIエリアタイプを表示
    for ui_type in get_ui_types_from_error():
        print(ui_type)
