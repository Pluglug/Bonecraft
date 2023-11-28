# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . operators.edit_ops import operator_classes
from . property_groups.bone_naming import *
from . utils.vlog import log
from . utils.debug import *
import addon

bl_info = {
    "name": "BoneCraft",
    "author": "pluglug",
    "version": (0, 4, 1),
    "blender": (4, 0, 0),
    "location": "",
    "description": "Enhances the rigging workflow in Blender by streamlining operations across Edit and Pose modes.",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Rigging"
}


addon.VERSION = bl_info["version"]
addon.BL_VERSION = bl_info["blender"]


def register():
    DBG_INIT and log.header("Registering BoneCraft operators...")
    for cls in operator_classes:
        bpy.utils.register_class(cls)
        DBG_INIT and log.info(f"Registered: {cls.__name__}")


def unregister():
    DBG_INIT and log.header("Unregistering BoneCraft operators...")
    for cls in operator_classes:
        bpy.utils.unregister_class(cls)
        DBG_INIT and log.info(f"Unregistered: {cls.__name__}")


if __name__ == "__main__":
    pass


# "D"pie
# 接尾語として無視されるリスト 正規表現を使用できる。
# ペアレント(編集モードへ) altで解除
# コントレインスト(ポーズモードへ)
# 名前プリセット
# コレクション移動(ctrl D)
# 変形
# ワイヤ 名前 軸

# PME POP MOVE 入れ替えじゃなくしてほしい

# shift w ボーンオプション
#     ワイヤー表示?
#     変形
#     エンベロープを頂点グループに乗算
#     回転を継承×
#      ロック
# 親の選択この選択 Aドラッグ
# ポーズモードでのペアレントは何に使う?Pieでは編集モードのみにする
# IK
# Blenderでは、ボーン（アーマチュア）の追加・単体のプロパティ編集は編集モード、コンストレイントなどリギングに必要なものを乗せるにはポーズモードと作業に応じてモードを切り替えなければならない。その不便を解消するため、ポーズモード中でもある程度編集モードと同じ挙動を行えるように開発されたのがこのボーンツールだ。


# 3ds Maxの標準機能「選択セット」を踏襲したツールで、オブジェクトもしくはアーマチュア内の骨の登録が可能。追加機能として選択時のマニピュレータモードの指定とセットの外部保存を組み込んでいる。

# 選択中のボーンに応じて、ペアレント設定、削除を切り替えるか、迷った
# ちょっと複雑

# ひとつだけなら親子解除でいいか
