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


if __name__ == "__main__":
    # 使用可能なUIエリアタイプを表示
    for ui_type in get_ui_types_from_error():
        print(ui_type)
