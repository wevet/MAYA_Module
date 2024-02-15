# -*- coding: utf-8 -*-

import os.path
import os
import maya.cmds as cmds
import glob
import ast
import sys
from functools import partial
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *

def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window), QtWidgets.QDialog)
    else:
        return wrapInstance(long(main_window), QtWidgets.QDialog) # type: ignore


class Animation_Pose(QtWidgets.QDialog):

    def __init__(self, parent=None, *args, **kwargs):
        super(Animation_Pose, self).__init__(maya_main_window())
        self.WINDOW_TITLE = "Animation Poser"
        self.MODULE_VERSION = "1.0.0"
        self.file_path_000 = None
        self.icon_path_000 = None

        self.window = None
        self.apply_button = None
        self.refresh_button = None
        self.file_name01 = None
        self.save_path = None
        self.sp_frame01 = None
        self.sp_frame00 = None
        self.sp_main_form = None
        self.button_form = None
        self.button_scroll = None
        self.pose_cache_file_names = []

        self.default_style = "background-color: #34d8ed; color: black"
        self.setStyleSheet('background-color:#262f38;')
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 420)

        self.save_base_path = os.path.dirname(__file__)

        # "/SavePose/PoseData/"
        self.file_path_000 = self.save_base_path + "/PoseData/"
        if not os.path.exists(self.file_path_000):
            os.makedirs(self.file_path_000)

        self.icon_path_000 = self.save_base_path + "/Image/"
        if not os.path.exists(self.icon_path_000):
            os.makedirs(self.icon_path_000)

        self._cell_size = QtCore.QSize(60, 60)
        self.connection_layout = None

        self._create_ui_widget()
        self._create_ui_connection()
        #self.show_main_window()

    def showEvent(self, event):
        print("show event")
        pass

    def closeEvent(self, event):
        print("close event")
        pass

    def _create_ui_widget(self):
        separator_line_1 = QtWidgets.QFrame(parent=None)
        separator_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_2 = QtWidgets.QFrame(parent=None)
        separator_line_2.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_2.setFrameShadow(QtWidgets.QFrame.Sunken)

        # input field
        self.file_name01 = QtWidgets.QLineEdit()
        self.file_name01.setReadOnly(False)
        self.file_name01.setPlaceholderText("Input Pose File Name")
        self.save_path = QtWidgets.QLineEdit()
        self.save_path.setReadOnly(False)
        self.save_path.setPlaceholderText("保存場所")
        self.save_path.setText(self.file_path_000)
        horizontal_layout_input_field = QtWidgets.QFormLayout()
        horizontal_layout_input_field.addRow(self.file_name01)
        horizontal_layout_input_field.addRow(self.save_path)

        # grid layout
        connection_list_widget = QtWidgets.QWidget()
        self.connection_layout = QtWidgets.QVBoxLayout(connection_list_widget)
        self.connection_layout.setContentsMargins(2, 2, 2, 2)
        self.connection_layout.setSpacing(3)
        self.connection_layout.setAlignment(QtCore.Qt.AlignTop)
        list_scroll_area = QtWidgets.QScrollArea()
        list_scroll_area.setWidgetResizable(True)
        list_scroll_area.setWidget(connection_list_widget)

        # button field
        self.apply_button = QtWidgets.QPushButton("SavePose")
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.apply_button.setStyleSheet(self.default_style)
        self.refresh_button.setStyleSheet(self.default_style)
        horizontal_layout_button = QtWidgets.QHBoxLayout()
        horizontal_layout_button.addWidget(self.apply_button)
        horizontal_layout_button.addWidget(self.refresh_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.addLayout(horizontal_layout_input_field)
        main_layout.addWidget(separator_line_1)
        main_layout.addWidget(list_scroll_area)
        main_layout.addWidget(separator_line_2)
        main_layout.addLayout(horizontal_layout_button)

        pass

    def _create_ui_connection(self):
        self.apply_button.clicked.connect(partial(self._get_value, self.icon_path_000))
        self.refresh_button.clicked.connect(self._refresh_file_action)
        pass

    def show_main_window(self):

        w = 400
        h = 200

        if not cmds.window(self.WINDOW_TITLE, ex=1):
            pass
        else:
            cmds.deleteUI(self.WINDOW_TITLE)

        self.window = cmds.window(self.WINDOW_TITLE, t="Animation Poser", wh=(w, h))
        self.sp_main_form = cmds.formLayout("sp_mainForm")
        self.sp_frame00 = cmds.frameLayout("sp_frame00", p=self.sp_main_form, lv=0)

        top_layout = cmds.formLayout("top_button_form", p=self.sp_frame00)
        self.file_name01 = cmds.textFieldGrp("file_name01", l='ファイル名', p=top_layout)
        self.save_path = cmds.textFieldGrp("save_path", l="保存場所", text=self.file_path_000, p=top_layout)

        middle_layout = cmds.formLayout("middle_button_form", p=self.sp_frame00)
        self.apply_button = cmds.button("apply_button", label="SavePose", command=partial(self._get_value, self.icon_path_000), p=top_layout, bgc=[0.3, 0.3, 0.3])
        #self.refresh_button = cmds.button("refresh_button", label="Refresh", command=partial(self._refresh_file_action, self.icon_path_000), p=top_layout, bgc=[0.3, 0.3, 0.3])

        cmds.formLayout("top_button_form", e=1, af=[(self.save_path, "right", 0), (self.save_path, "left", 0)], ac=(self.save_path, "top", 5, self.file_name01), an=(self.save_path, "bottom"))
        cmds.formLayout("top_button_form", e=1, af=[(self.apply_button, "right", 0), (self.apply_button, "left", 0), (self.apply_button, "bottom", 5)], ac=(self.apply_button, "top", 5, self.save_path))
        #cmds.formLayout("top_button_form", e=1, af=[(self.refresh_button, "right", 0), (self.refresh_button, "left", 0), (self.refresh_button, "bottom", 5)], ac=(self.refresh_button, "top", 5, self.save_path))

        cmds.setParent("..")

        # collapse ui
        self.sp_frame01 = cmds.frameLayout("sp_frame01", cll=1, p=self.sp_main_form, l="POSE")
        self.button_form = cmds.formLayout("button_form", p=self.sp_frame01)
        self.button_scroll = cmds.scrollLayout("button_scroll", p=self.button_form)

        cmds.formLayout("sp_mainForm", e=1, af=[(self.sp_frame00, "top", 5), (self.sp_frame00, "right", 5), (self.sp_frame00, "left", 5)], an=(self.sp_frame00, "bottom"))
        cmds.formLayout("sp_mainForm", e=1, af=[(self.sp_frame01, "bottom", 5), (self.sp_frame01, "right", 5), (self.sp_frame01, "left", 5)], ac=(self.sp_frame01, "top", 5, self.sp_frame00))

        file_name_000 = os.listdir(self.file_path_000)
        for i in range(len(file_name_000)):
            name_000 = os.path.basename(file_name_000[i]).split('.', 1)[0]
            icon = self.icon_path_000 + name_000 + ".jpg"
            # ここでポーズデータのファイル名から、アイコンのファイル名を生成する必要がある
            print("icon => {}".format(icon))
            self.pose_cache_file_names.append(name_000)
            if os.path.exists(icon):
                cmds.iconTextButton("icon_button" + str(i), st='iconAndTextHorizontal', i1=icon, l=name_000, c=partial(self._load_file, i), fla=1)

        cmds.formLayout("button_form", e=1, af=[(self.button_scroll, "top", 5), (self.button_scroll, "bottom", 5), (self.button_scroll, "right", 5), (self.button_scroll, "left", 5)])
        cmds.showWindow(self.window)

    def _refresh_file_action(self):
        pass


    @staticmethod
    def _get_all_joint():
        joints = cmds.ls(selection=True, dag=True, type="joint")
        return joints

    def _get_value(self, base_icon_path, *args):
        file_name01 = self.file_name01.text()
        save_path = self.save_path.text()
        joints = self._get_all_joint()

        if len(joints) == 0 or file_name01 == "":
            cmds.warning("Select an object or name the file")
            return
        elif save_path == "":
            cmds.warning("Please specify where to save the file")
            return

        file_path = save_path + "/" + file_name01 + ".txt"
        if os.path.isfile(file_path):
            cmds.warning("同じ名前のファイルがあります")
            return

        name_dict = "{"
        for joint in joints:
            # 選択したノードとアトリビュートをとってくる
            key_attribute_list = cmds.listAttr(joint, s=1, w=1, k=1, v=1, u=1, st=['translate*', 'rotate*', 'scale*'])
            #print(key_attribute_list)
            for attr in key_attribute_list:
                value = cmds.getAttr(joint + "." + attr)
                name_dict = name_dict + "\"" + joint + "." + attr + "\":" + str(value) + ",\n"
            name_dict = name_dict + "}\n"

        print(file_path)
        s = name_dict
        # ファイル書きだしテスト
        with open(file_path, mode='w') as f:
            f.write(s)

        # --------プレイブラストでスクショとる
        # 現在のフレームを取得
        cmds.select(cl=1)
        time = int(cmds.currentTime(q=1))
        # UIを参照してファイル名をとってくる
        #paste_name = cmds.textFieldGrp("file_name01", q=1, tx=1)
        paste_name = self.file_name01.text()
        # ボタンにスクショを適用させる
        icon = self.icon_path_000 + paste_name + ".jpg"
        new_path_file_name = self.icon_path_000 + paste_name
        # nurbs curveを非表示
        cmds.modelEditor("modelPanel4", e=1, nc=0)
        # ファイル名にパスを含めると、そこに書き出してくれる。
        pose_icon = cmds.playblast(fmt="image", c="jpg", w=70, h=70, st=time, et=time, cf=new_path_file_name, fo=1, v=0, p=100, qlt=100, cc=1, sqt=0, showOrnaments=0)
        os.rename(pose_icon, pose_icon + ".jpg")
        # ナーブスカーブ表示
        cmds.modelEditor("modelPanel4", e=1, nc=1)

    def _load_file(self, file_index):
        file_path = self.file_path_000 + "*"
        file = glob.glob(file_path)

        print("load file =>{}".format(file))
        f = open(file[file_index])
        inf = f.read()
        # convert to dictionary
        file_dictionary = ast.literal_eval(inf)

        key = [k for k, v in file_dictionary.items()]
        val = [v for k, v in file_dictionary.items()]
        for file_index in range(len(key)):
            cmds.setAttr(key[file_index], val[file_index])
        f.close()


def show_main_window():
    global animation_poser
    try:
        animation_poser.close()  # type: ignore
        animation_poser.deleteLater()  # type: ignore
    except:
        pass
    animation_poser = Animation_Pose()
    animation_poser.show()


