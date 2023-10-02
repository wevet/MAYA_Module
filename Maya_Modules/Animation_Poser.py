# -*- coding: utf-8 -*-

import os.path
import os
import maya.cmds as cmds
import glob
import ast
import sys
from functools import partial


def show_main_window():
    file_path_000 = "/SavePose/PoseDate/"
    icon_path_000 = "/SavePose/Image/"

    file_name_000 = os.listdir(file_path_000)  # ポーズファイルのリスト
    icon_name_000 = os.listdir(icon_path_000)  # アイコンファイルのリスト

    w = 400
    h = 200
    window_title = "Animation Poser"

    if (cmds.window(window_title, ex=1)):
        cmds.deleteUI(window_title)

    win = cmds.window(window_title, t="Animation Poser", wh=(w, h))
    sp_main_form = cmds.formLayout("sp_mainForm")
    sp_frame00 = cmds.frameLayout("sp_frame00", p=sp_main_form, lv=0)

    top_btn_form = cmds.formLayout("top_btn_form", p=sp_frame00)
    file_name01 = cmds.textFieldGrp("file_name01", l='ファイル名', p=top_btn_form)
    save_path = cmds.textFieldGrp("save_path", l="保存場所", text=file_path_000, p=top_btn_form)
    apply_btn = cmds.button("apply_btn", l="セーブポーズ", c=partial(getValue), p=top_btn_form)

    cmds.setParent("..")

    sp_frame01 = cmds.frameLayout("sp_frame01", cll=1, p=sp_main_form, l="POSE")
    btn_form = cmds.formLayout("btn_form", p=sp_frame01)
    btn_scroll = cmds.scrollLayout("btn_scroll", p=btn_form)

    for i in range(len(file_name_000)):
        name_000 = os.path.basename(file_name_000[i]).split('.', 1)[0]
        icon = icon_path_000 + name_000 + ".jpg"
        # ここでポーズデータのファイル名から、アイコンのファイル名を生成する必要がある
        print(icon)

        # ファイル名とマッチしたアイコンのみ表示
        if (os.path.exists(icon)):
            icon_button = cmds.iconTextButton("icon_button" + str(i), st='iconAndTextHorizontal', i1=icon, l=name_000, c=partial(load_file, str(i)), fla=1)
        else:
            nonIcon = icon_path_000 + "non.jpg"
            icon_button = cmds.iconTextButton("icon_button" + str(i), st='iconAndTextHorizontal', i1=nonIcon, l=name_000, c=partial(load_file, str(i)))
            print("無し")

    # cmds.setParent("..")
    cmds.formLayout("topBtnForm", e=1, af=[(save_path, "right", 0), (save_path, "left", 0)], ac=(save_path, "top", 5, file_name01), an=(save_path, "bottom"))
    cmds.formLayout("topBtnForm", e=1, af=[(apply_btn, "right", 0), (apply_btn, "left", 0), (apply_btn, "bottom", 5)], ac=(apply_btn, "top", 5, save_path))
    cmds.formLayout("sp_mainForm", e=1, af=[(sp_frame00, "top", 5), (sp_frame00, "right", 5), (sp_frame00, "left", 5)], an=(sp_frame00, "bottom"))
    cmds.formLayout("sp_mainForm", e=1, af=[(sp_frame01, "bottom", 5), (sp_frame01, "right", 5), (sp_frame01, "left", 5)], ac=(sp_frame01, "top", 5, sp_frame00))
    # ボタンスクロールのレイアウト編集
    cmds.formLayout("btn_form", e=1, af=[(btn_scroll, "top", 5), (btn_scroll, "bottom", 5), (btn_scroll, "right", 5), (btn_scroll, "left", 5)])
    cmds.showWindow(win)


# ----実行ボタンの処理--------/
def getValue():
    file_name01 = cmds.textFieldGrp("file_name01", q=1, tx=1)  # ファイル名と保存場所を取得
    save_path = cmds.textFieldGrp("save_path", q=1, tx=1)

    select_node = cmds.ls(sl=1)
    print(select_node)
    if len(select_node) == 0 and len(file_name01) == 0:
        cmds.warning("オブジェクトを選択してファイル名を付けてください")
        sys.exit()
    elif len(select_node) == 0:
        cmds.warning("オブジェクトを選択してください")
        sys.exit()
    elif len(file_name01) == 0:
        cmds.warning("ファイル名がありません")
        sys.exit()
    elif len(save_path) == 0:
        cmds.warning("保存先を指定してください")
        sys.exit()

    # 選択したノードとアトリビュートをとってくる
    key_attribute_list = cmds.listAttr(select_node, s=1, w=1, k=1, v=1, u=1, st=['translate*', 'rotate*', 'scale*'])
    name_dict = "{"
    for nodeList in select_node:
        # アトリビュートの選別
        key_attribute_list = cmds.listAttr(nodeList, r=True, w=True, k=True, u=True, v=True, m=True, s=True)
        if select_node is None:
            # trueならば繰り返しを抜ける
            continue

        elif len(select_node) == 0:
            continue

        print(key_attribute_list)
        for attr in key_attribute_list:
            value = cmds.getAttr(nodeList + "." + attr)
            name_dict = name_dict + "\"" + nodeList + "." + attr + "\":" + str(value) + ",\n"

    name_dict = name_dict + "}\n"
    file_path = save_path + "\\" + file_name01 + ".txt"

    if os.path.isfile(file_path):
        cmds.warning("同じ名前のファイルがあります")
        sys.exit()

    s = name_dict
    # ファイル書きだしテスト
    with open(file_path, mode='w') as f:
        f.write(s)
    # --------プレイブラストでスクショとる
    # 現在のフレームを取得
    cmds.select(cl=1)
    time = int(cmds.currentTime(q=1))

    icon_path = "/SavePose/Image/"
    paste_name = cmds.textFieldGrp("file_name01", q=1, tx=1)  # UIを参照してファイル名をとってくる
    icon = icon_path + paste_name + ".jpg"  # ボタンにスクショを適用させる

    # ナーブスカーブを非表示
    cmds.modelEditor("modelPanel4", e=1, nc=0)

    # ファイル名にパスを含めると、そこに書き出してくれる。
    pose_icon = cmds.playblast(fmt="image", c="jpg", w=70, h=70, st=time, et=time, cf=icon_path + paste_name, fo=1, v=0, p=100, qlt=100, cc=1, sqt=0, showOrnaments=0)
    os.rename(pose_icon, pose_icon + ".jpg")
    # ナーブスカーブ表示
    cmds.modelEditor("modelPanel4", e=1, nc=1)


def load_file(i):
    file_path = "/SavePose/PoseDate/*"
    File = glob.glob(file_path)

    f = open(File[i])
    inf = f.read()
    # ディクト型に変換
    file_dictionary = ast.literal_eval(inf)

    key = [k for k, v in file_dictionary.items()]
    val = [v for k, v in file_dictionary.items()]

    for i in range(len(key)):
        cmds.setAttr(key[i], val[i])

    f.close()


show_main_window()