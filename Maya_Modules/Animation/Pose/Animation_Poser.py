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
        self.pose_file_path = None
        self.image_base_path = None

        self.apply_button = None
        self.refresh_button = None
        self.input_pose_name = None
        self.save_path = None
        self.button_scroll = None
        self.thumbnail_buttons = []
        self.connection_layout = None

        self.default_style = "background-color: #34d8ed; color: black"
        self.setStyleSheet('background-color:#262f38;')
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 420)

        file_path = cmds.file(q=True, sn=True)
        file_name = os.path.basename(file_path)
        raw_name, extension = os.path.splitext(file_name)
        self.scene_name = raw_name
        print("Here is the name of the file that is currently open => {0}".format(self.scene_name))

        self.save_base_path = os.path.dirname(__file__)
        self._write_export_dir(self.save_base_path)

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
        self.input_pose_name = QtWidgets.QLineEdit()
        self.input_pose_name.setReadOnly(True)
        self.input_pose_name.setPlaceholderText("Input Pose File Name")
        self.input_pose_name.setText(self.scene_name)
        self.save_path = QtWidgets.QLineEdit()
        self.save_path.setReadOnly(False)
        self.save_path.setPlaceholderText("Save Directory")
        self.save_path.setText(self.pose_file_path)
        horizontal_layout_input_field = QtWidgets.QFormLayout()
        horizontal_layout_input_field.addRow(self.input_pose_name)
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

    def _get_export_file_name(self):
        file_name = self.input_pose_name.text()
        time = int(cmds.currentTime(q=1))
        return file_name + "_{}".format(str(time))

    def _create_ui_connection(self):
        self.apply_button.clicked.connect(partial(self._write_pose_assets, self.image_base_path))
        self.refresh_button.clicked.connect(self._refresh_file_action)
        pass

    # scroll viewを更新する
    def _refresh_file_action(self):
        for button in self.thumbnail_buttons:
            self.connection_layout.removeWidget(button)

        self.thumbnail_buttons = []
        current_pose_file_path = os.listdir(self.pose_file_path)
        for i in range(len(current_pose_file_path)):
            file_name = os.path.basename(current_pose_file_path[i]).split('.', 1)[0]
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
                button.clicked.connect(partial(self._load_pose_assets, i))
                self.thumbnail_buttons.append(button)
                self.connection_layout.addWidget(button)
            else:
                cmds.warning("not exists. => {}".format(icon))

    @staticmethod
    def _get_all_joint():
        joints = cmds.ls(selection=True, dag=True, type="joint")
        return joints

    def _write_export_dir(self, path_name):
        # "/SavePose/PoseData/"
        self.pose_file_path = path_name + "/PoseData/"
        if not os.path.exists(self.pose_file_path):
            os.makedirs(self.pose_file_path)
        self.image_base_path = path_name + "/Image/"
        if not os.path.exists(self.image_base_path):
            os.makedirs(self.image_base_path)

    @staticmethod
    def _get_controllers(*args):
        """
        Return: 全てのコントローラを返します。
        """
        # Finding all the nurbs curves to get the shape node on the anim_curves
        nurbs_curve_list = cmds.ls(type="nurbsCurve")
        nurbs_surface_list = cmds.ls(type="nurbsSurface")
        if nurbs_surface_list:
            for curve in nurbs_surface_list:
                nurbs_curve_list.append(curve)

        print("nurbs_curve_list => {0}, nurbs_surface_list => {1}".format(len(nurbs_curve_list), len(nurbs_surface_list)))

        shape_list = nurbs_curve_list
        ctrl_list = []

        # すべてのshape controllerを反復処理する
        for shape in shape_list:
            parent = cmds.listRelatives(shape, parent=True)[0]
            # 同じ名前のコントローラが複数あるかどうかを確認する
            dub_names = cmds.ls(parent, exactType="transform")
            for ctrl in dub_names:
                #clash_name = ctrl.rsplit("|", 1)[-1]

                if not ctrl in ctrl_list:
                    # コントローラーがキーが使える属性を取得したかどうかを確認する、そうでなければ、コントロールをミラーリングする理由はない
                    if cmds.listAttr(ctrl, keyable=True):
                        ctrl_list.append(ctrl)
        return ctrl_list

    # NOTE
    # Pose Assetを書き出す
    def _write_pose_assets(self, base_icon_path, *args):
        export_file_name = self._get_export_file_name()
        save_path = self.save_path.text()

        joints = cmds.ls(type="joint")

        all_controllers = self._get_controllers()
        # キーを持たないジョイントを除外する
        keyed_joints = [joint for joint in all_controllers if cmds.keyframe(joint, q=True, keyframeCount=True) > 0]

        if export_file_name == "" or save_path == "":
            cmds.warning("export file name or save file is empty")
            return

        if len(keyed_joints) == 0:
            cmds.warning("keyed_joints is empty")
            return

        for joint in keyed_joints:
            print("joint => {}".format(joint))

        file_path = save_path + "/" + export_file_name + ".json"
        if os.path.isfile(file_path):
            cmds.warning("The same pose file already exists.")
            return

        if save_path != self.save_base_path:
            cmds.warning("Re-create the directory because there is a change in the file path. => {}".format(save_path))
            #self._write_export_dir(save_path)

        # Get the selected node and attribute
        name_dict = "{\n"
        for joint in keyed_joints:
            key_attribute_list = cmds.listAttr(joint, s=1, w=1, k=1, v=1, u=1, st=['translate*', 'rotate*', 'scale*'])
            if key_attribute_list is not None:
                for attr in key_attribute_list:
                    value = cmds.getAttr(joint + "." + attr)
                    name_dict = name_dict + "\"" + joint + "." + attr + "\" : " + str(value) + ",\n"
        name_dict = name_dict + "}\n"

        print(file_path)
        s = name_dict
        # ファイル書きだしテスト
        with open(file_path, mode='w') as f:
            f.write(s)

        # take picture for play blast module
        # 現在のフレームを取得
        cmds.select(keyed_joints[0], r=True)

        time = int(cmds.currentTime(q=1))
        # UIを参照してファイル名をとってくる
        paste_name = self._get_export_file_name()
        new_path_file_name = self.image_base_path + paste_name
        # nurbs curveを非表示
        cmds.modelEditor("modelPanel4", e=1, nc=0)
        # ファイル名にパスを含めると、そこに書き出してくれる。
        pose_icon = cmds.playblast(fmt="image", c="jpg", w=80, h=80, st=time, et=time, cf=new_path_file_name, fo=1, v=0, p=100, qlt=100, cc=1, sqt=0, showOrnaments=0)
        os.rename(pose_icon, pose_icon + ".jpg")
        # ナーブスカーブ表示
        cmds.modelEditor("modelPanel4", e=1, nc=1)

    def _load_pose_assets(self, file_index):
        file_path = self.pose_file_path + "*"
        file = glob.glob(file_path)

        print("load file =>{}".format(file))
        f = open(file[file_index])
        inf = f.read()
        # convert to dictionary
        file_dictionary = ast.literal_eval(inf)

        time = int(cmds.currentTime(q=1))
        key = [k for k, v in file_dictionary.items()]
        val = [v for k, v in file_dictionary.items()]
        for file_index in range(len(key)):
            try:
                attr_obj = key[file_index]
                value = val[file_index]
                #print(attr_obj)
                cmds.setAttr(attr_obj, value)
                cmds.setKeyframe(attr_obj, v=value, t=time)
            except:
                pass

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


