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
        self.image_base_path = None

        self.apply_button = None
        self.refresh_button = None
        self.file_name01 = None
        self.save_path = None
        self.button_scroll = None
        self.thumbnail_buttons = []
        self.connection_layout = None

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

        self.image_base_path = self.save_base_path + "/Image/"
        if not os.path.exists(self.image_base_path):
            os.makedirs(self.image_base_path)

        self._create_ui_widget()
        self._create_ui_connection()

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

        # modify thumbnail view
        self._refresh_file_action()

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

    def _create_ui_connection(self):
        self.apply_button.clicked.connect(partial(self._write_pose_assets, self.image_base_path))
        self.refresh_button.clicked.connect(self._refresh_file_action)
        pass

    def _refresh_file_action(self):
        for button in self.thumbnail_buttons:
            self.connection_layout.removeWidget(button)

        self.thumbnail_buttons = []
        file_name_000 = os.listdir(self.file_path_000)
        for i in range(len(file_name_000)):
            file_name = os.path.basename(file_name_000[i]).split('.', 1)[0]
            icon = self.image_base_path + file_name + ".jpg"
            if os.path.exists(icon):
                # ここでポーズデータのファイル名から、アイコンのファイル名を生成する必要がある
                print("icon => {}".format(icon))
                button = QtWidgets.QPushButton()
                button.setFixedSize(80, 80)
                ico = QtGui.QIcon(icon)
                button.setIcon(ico)
                button.setIconSize(button.size())
                button.setFlat(True)
                button.setStyleSheet(self.default_style)
                button.setToolTip("file name : {}".format(file_name))
                button.clicked.connect(partial(self._load_file, i))
                self.thumbnail_buttons.append(button)
                self.connection_layout.addWidget(button)

        pass

    @staticmethod
    def _get_all_joint():
        joints = cmds.ls(selection=True, dag=True, type="joint")
        return joints

    # NOTE
    # Pose Assetを書き出す
    def _write_pose_assets(self, base_icon_path, *args):
        file_name01 = self.file_name01.text()
        save_path = self.save_path.text()
        joints = cmds.ls(selection=True, dag=True, type="joint")

        if len(joints) == 0 or file_name01 == "" or save_path == "":
            cmds.warning("joint empty or file name is empty or save file is empty")
            return

        file_path = save_path + "/" + file_name01 + ".txt"
        if os.path.isfile(file_path):
            cmds.warning("The same pose file already exists.")
            return

        name_dict = "{\n"
        for joint in joints:
            # 選択したノードとアトリビュートをとってくる
            key_attribute_list = cmds.listAttr(joint, s=1, w=1, k=1, v=1, u=1, st=['translate*', 'rotate*', 'scale*'])
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
        cmds.select(joints[0], r=True)

        time = int(cmds.currentTime(q=1))
        # UIを参照してファイル名をとってくる
        paste_name = self.file_name01.text()
        # ボタンにスクショを適用させる
        icon = self.image_base_path + paste_name + ".jpg"
        new_path_file_name = self.image_base_path + paste_name
        # nurbs curveを非表示
        cmds.modelEditor("modelPanel4", e=1, nc=0)
        # ファイル名にパスを含めると、そこに書き出してくれる。
        pose_icon = cmds.playblast(fmt="image", c="jpg", w=70, h=70, st=time, et=time, cf=new_path_file_name, fo=1, v=0, p=100, qlt=100, cc=1, sqt=0, showOrnaments=0)
        os.rename(pose_icon, pose_icon + ".jpg")
        # ナーブスカーブ表示
        cmds.modelEditor("modelPanel4", e=1, nc=1)
        self.file_name01.setText("")

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


