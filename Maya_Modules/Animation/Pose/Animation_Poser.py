# -*- coding: utf-8 -*-

import os.path
import os
import maya.cmds as cmds
import glob
import ast
import sys
import time
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
        self.MODULE_VERSION = "1.1.0"

        self.apply_button = None
        self.refresh_button = None
        self.input_pose_name = None
        self.export_save_path = None
        self.button_scroll = None
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

        # 初期値はscriptがあるパスに設定
        initial_path = os.path.dirname(__file__)
        self.export_save_base_path = initial_path
        self._write_directories(self.export_save_base_path)

        self.import_save_base_path = initial_path
        self._write_directories(self.import_save_base_path)

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

        self.export_name_label = QtWidgets.QLabel("Export Path")
        self.export_name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.export_name_label.setStyleSheet("color: darkgray")
        self.export_save_path = QtWidgets.QLineEdit()
        self.export_save_path.setReadOnly(False)
        self.export_save_path.setPlaceholderText("Export Directory")
        self.export_save_path.setText(self.export_save_base_path)

        self.import_name_label = QtWidgets.QLabel("Import Path")
        self.import_name_label.setAlignment(QtCore.Qt.AlignLeft)
        self.import_name_label.setStyleSheet("color: darkgray")
        self.import_save_path = QtWidgets.QLineEdit()
        self.import_save_path.setReadOnly(False)
        self.import_save_path.setPlaceholderText("Export Directory")
        self.import_save_path.setText(self.import_save_base_path)

        horizontal_layout_input_field = QtWidgets.QFormLayout()
        horizontal_layout_input_field.addRow(self.input_pose_name)
        horizontal_layout_input_field.addRow(self.export_name_label)
        horizontal_layout_input_field.addRow(self.export_save_path)
        horizontal_layout_input_field.addRow(self.import_name_label)
        horizontal_layout_input_field.addRow(self.import_save_path)

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
        self.refresh_button = QtWidgets.QPushButton("Refresh Import")
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
        self.apply_button.clicked.connect(self.export_pose_asset)
        self.refresh_button.clicked.connect(self._refresh_file_action)
        pass

    def _clear_list_item_widget(self):
        while self.connection_layout.count() > 0:
            connection_ui_item = self.connection_layout.takeAt(0)
            if connection_ui_item.widget():
                connection_ui_item.widget().deleteLater()

    # scroll viewを更新する
    def _refresh_file_action(self):
        self._clear_list_item_widget()

        import_json_path = self._get_imported_pose_file()
        import_image_path = self._get_imported_image_file()
        current_pose_file_path = os.listdir(import_json_path)
        for i in range(len(current_pose_file_path)):
            file_name = os.path.basename(current_pose_file_path[i]).split('.', 1)[0]
            icon = import_image_path + file_name + ".jpg"
            if os.path.exists(icon):
                # ここでポーズデータのファイル名から、アイコンのファイル名を生成する必要がある
                print("icon => {}".format(icon))
                list_item_widget = PoseListItemWidget(parent_instance=self, icon=icon, index=i, file_name=file_name)
                self.connection_layout.addWidget(list_item_widget)

            else:
                cmds.warning("not exists. => {}".format(icon))

    @staticmethod
    def _get_all_joint():
        joints = cmds.ls(selection=True, dag=True, type="joint")
        return joints

    @staticmethod
    def _write_directories(path_name):
        # "/SavePose/PoseData/"
        export_pose_dir = path_name + "/PoseData/"
        if not os.path.exists(export_pose_dir):
            os.makedirs(export_pose_dir)
        export_image_dir = path_name + "/Image/"
        if not os.path.exists(export_image_dir):
            os.makedirs(export_image_dir)

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

    def _find_json_file_recursive(self, prefix):
        for root, dirs, files in os.walk(top="{}".format(self.export_save_base_path)):
            for file in files:
                if not file.lower().endswith(('{}'.format(prefix))):
                    continue
                local_file_path = os.path.join(root, file)
                print('local_file_path = {}'.format(local_file_path))

    # NOTE
    # Pose Assetを書き出す
    def export_pose_asset(self, *args):
        export_file_name = self._get_export_file_name()
        save_path = self.export_save_path.text()

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

        if save_path != self.export_save_base_path:
            cmds.warning("Re-create the directory because there is a change in the file path. => {}".format(save_path))
            self._write_directories(save_path)

        file_path = save_path + "/PoseData/" + export_file_name + ".json"
        if os.path.isfile(file_path):
            cmds.warning("The same pose file already exists.")
            return

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
        new_path_file_name = save_path + "/Image/" + paste_name
        # nurbs curveを非表示
        cmds.modelEditor("modelPanel4", e=1, nc=0)
        # ファイル名にパスを含めると、そこに書き出してくれる。
        pose_icon = cmds.playblast(fmt="image", c="jpg", w=80, h=80, st=time, et=time, cf=new_path_file_name, fo=1, v=0, p=100, qlt=100, cc=1, sqt=0, showOrnaments=0)
        os.rename(pose_icon, pose_icon + ".jpg")
        # ナーブスカーブ表示
        cmds.modelEditor("modelPanel4", e=1, nc=1)
        #time.sleep(1)
        self._refresh_file_action()

    # load json file
    def load_pose_assets(self, file_index):
        file_path = self._get_imported_pose_file() + "*"
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

    def _get_imported_pose_file(self):
        return self.import_save_path.text() + "/PoseData/"

    def _get_imported_image_file(self):
        return self.import_save_path.text() + "/Image/"

    def _get_exported_pose_file(self):
        return self.export_save_path.text() + "/PoseData/"

    def _get_exported_image_file(self):
        return self.export_save_path.text() + "/Image/"

    # delete json file
    # import済みのjson dataを削除
    def delete_pose_asset(self, file_index):
        file_path = self._get_imported_pose_file() + "*"
        file = glob.glob(file_path)

        print("delete json file =>{}".format(file[file_index]))
        os.remove(file[file_index])

        image_file_path = self._get_imported_image_file() + "*"
        image_file = glob.glob(image_file_path)

        print("delete image file =>{}".format(image_file[file_index]))
        os.remove(image_file[file_index])
        time.sleep(1)
        self._refresh_file_action()


class PoseListItemWidget(QtWidgets.QWidget):

    def __init__(self, parent_instance, icon, index, file_name):
        super(PoseListItemWidget, self).__init__()
        self.main = parent_instance
        self.icon = icon
        self.index = index
        self.file_name = file_name
        self.sel_button = None
        self.del_button = None
        self.file_name_label = None
        self.setFixedHeight(80)
        self.create_ui_widgets()
        self.create_ui_layout()
        self.create_ui_connections()

    def create_ui_widgets(self):
        self.sel_button = QtWidgets.QPushButton()
        self.sel_button.setStyleSheet("background-color: #707070")
        #self.sel_button.setText("ImportPose")
        self.sel_button.setToolTip("file name : {}".format(self.file_name))
        self.sel_button.setFixedSize(80, 60)

        ico = QtGui.QIcon(self.icon)
        self.sel_button.setIcon(ico)
        self.sel_button.setIconSize(self.sel_button.size())
        self.sel_button.setFlat(True)

        self.del_button = QtWidgets.QPushButton()
        self.del_button.setStyleSheet("background-color: #ed4a34; color: white")
        self.del_button.setText("Delete Pose")
        self.del_button.setFixedSize(80, 40)

        self.file_name_label = QtWidgets.QLabel(self.file_name)
        self.file_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.file_name_label.setStyleSheet("color: darkgray")

    def create_ui_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 10, 5)
        main_layout.addWidget(self.sel_button)
        main_layout.addWidget(self.file_name_label)
        main_layout.addWidget(self.del_button)

    def create_ui_connections(self):
        self.sel_button.clicked.connect(partial(self.main.load_pose_assets, self.index))
        self.del_button.clicked.connect(partial(self.main.delete_pose_asset, self.index))
        pass


def show_main_window():
    global animation_poser
    try:
        animation_poser.close()  # type: ignore
        animation_poser.deleteLater()  # type: ignore
    except:
        pass
    animation_poser = Animation_Pose()
    animation_poser.show()


