# -*- coding: utf-8 -*-

"""
Description:
    A tool for mirroring the anim_curves from one side to the other
    or to flip the pose

Usage:
1. Select what the mirror axis direction is in the "mirror axis" dropdown menu.

2. Select what direction you wish to mirror in the "direction" dropdown menu.

By default, it works with
-upper case L and R
-lower case l and r
-Lf and Rt

If your naming convention is one of the default then skip to step 4
3. Write your naming convention for the left side
   in the "left naming convention" textbox, and your
   right naming convention in the "right naming convention" textbox.

4. Click the "Mirror" button

"""

import os
import sys

import maya.standalone
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QApplication, QLabel
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds
import maya.OpenMaya as om
import maya.mel as mel
import subprocess
import pymel.core as pm
from time import sleep


class OperationType(object):
    left_to_right = "Left to Right"
    right_to_left = "Right to Left"
    flip_to_frame = "Flip to Frame"
    selected = "Selected"
    mirror_middle = "Mirror Middle"
    not_selected = "Not Selected"


def maya_main_menu():
    main_window = omui.MQtUtil.mainWindow()

    if main_window is not None:
        if sys.version_info.major >= 3:
            return wrapInstance(int(main_window), QtWidgets.QDialog)
        else:
            return wrapInstance(long(main_window), QtWidgets.QDialog)  # type: ignore
    else:
        pass

def preserve_selection(func):
    def wrapper(*args, **kwargs):
        print("-------------open chunk-------------")
        cmds.undoInfo(openChunk=True)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise
        finally:
            cmds.undoInfo(closeChunk=True)
            print("-------------close chunk-------------")
    return wrapper


class Animation_Mirror_Window(QtWidgets.QDialog):

    dlg_instance = None

    WINDOW_TITLE = "Mirror Animation Window"
    SOURCE_TRANSFORM_ATTRIBUTE = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]
    MODULE_VERSION = "1.0.5"

    @classmethod
    def show_dialog(cls):
        if not cls.dlg_instance:
            cls.dlg_instance = Animation_Mirror_Window()
        if cls.dlg_instance.isHidden():
            cls.dlg_instance.show()
        else:
            cls.dlg_instance.raise_()
            cls.dlg_instance.activateWindow()

    def __init__(self, parent=maya_main_menu()):
        super(Animation_Mirror_Window, self).__init__(parent)

        self.prefix = ["_L", "_R", "L", "R", "Left", "Right"]
        self.geometry = None

        # combo box
        self.mirror_axis_combo_box = None
        self.operation_combo_box = None

        # spin box
        self.min_mirror_frame_spin_box = None
        self.max_mirror_frame_spin_box = None

        # write key frame check box
        self.is_write_keyframe = False
        self.write_keyframe_checkbox = None

        # bake
        self.is_bake_animation = False
        self.bake_animation_checkbox = None

        # button
        self.left_to_right_radio_button = None
        self.right_to_left_radio_button = None
        self.flip_radio_button = None
        self.mirror_button = None
        self.undo_button = None

        # seperator
        self.mirror_axis_seperator = None
        self.top_seperator = None
        self.middle_seperator = None
        self.bottom_seperator = None

        # edit text
        self.left_ctrl_name_line_edit = None
        self.right_ctrl_name_line_edit = None

        # undo data
        self.undo_data = {}

        # misc
        self.setStyleSheet('background-color:#262f38;')

        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(360)
        self.setMinimumHeight(260)
        self.resize(620, 420)
        self._create_widgets()
        self._create_layout()
        self._create_connections()
        self._operation_change()

    def _create_widgets(self):
        self.mirror_axis_combo_box = QtWidgets.QComboBox()
        self.mirror_axis_combo_box.addItems(["X", "Y", "Z"])
        self.mirror_axis_combo_box.setToolTip("Mirror axis direction")
        self.operation_combo_box = QtWidgets.QComboBox()

        self.operation_combo_box.addItems([
                OperationType.flip_to_frame,
                OperationType.left_to_right,
                OperationType.right_to_left,
                OperationType.selected,
                #OperationType.mirror_middle,
                #OperationType.not_selected,
            ])

        styles = "background-color: #262f38; color: white"

        self.operation_combo_box.setToolTip("Mirror operation:\n\n"
            "Flip to Frame: ポーズ全体を反転させる\n"
            "Left to Right: 右のコントローラーを左と同じ値に設定する\n"
            "Right to Left: 左のコントローラーを右と同じ値に設定する\n"
            "Selected: 選択したコントローラーを反対側にミラーリングする\n"
            #"Mirror Middle: 真ん中のコントローラーを裏返す\n"
            #"Not Selected: 選択されていないすべてのコントローラを反転させる\n"
        )
        self.operation_combo_box.setStyleSheet(styles)

        self.min_mirror_frame_spin_box = QtWidgets.QDoubleSpinBox()
        self.min_mirror_frame_spin_box.setRange(-1000000, 1000000)
        self.min_mirror_frame_spin_box.setDecimals(1)
        self.min_mirror_frame_spin_box.setValue(Animation_Mirror_Window.get_min_time())
        self.min_mirror_frame_spin_box.setSingleStep(1)
        self.min_mirror_frame_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.min_mirror_frame_spin_box.setVisible(True)

        self.max_mirror_frame_spin_box = QtWidgets.QDoubleSpinBox()
        self.max_mirror_frame_spin_box.setRange(-1000000, 1000000)
        self.max_mirror_frame_spin_box.setDecimals(1)
        self.max_mirror_frame_spin_box.setValue(Animation_Mirror_Window.get_max_time())
        self.max_mirror_frame_spin_box.setSingleStep(1)
        self.max_mirror_frame_spin_box.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.max_mirror_frame_spin_box.setVisible(True)

        self.left_to_right_radio_button = QtWidgets.QRadioButton("Left To Right")
        self.left_to_right_radio_button.setChecked(True)
        self.right_to_left_radio_button = QtWidgets.QRadioButton("Right To Left")
        self.flip_radio_button = QtWidgets.QRadioButton("Flip")
        self.left_to_right_radio_button.setVisible(False)
        self.right_to_left_radio_button.setVisible(False)
        self.flip_radio_button.setVisible(False)

        self.write_keyframe_checkbox = QtWidgets.QCheckBox("SetKeyFrame")
        self.write_keyframe_checkbox.setChecked(True)
        self.bake_animation_checkbox = QtWidgets.QCheckBox("WithBake?")
        self.bake_animation_checkbox.setChecked(True)

        self.mirror_axis_seperator = QtWidgets.QFrame()
        self.mirror_axis_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.mirror_axis_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.top_seperator = QtWidgets.QFrame()
        self.top_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.top_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.middle_seperator = QtWidgets.QFrame()
        self.middle_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.middle_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.bottom_seperator = QtWidgets.QFrame()
        self.bottom_seperator.setFrameShape(QtWidgets.QFrame.HLine)
        self.bottom_seperator.setFrameShadow(QtWidgets.QFrame.Sunken)

        self.left_ctrl_name_line_edit = QtWidgets.QLineEdit()
        self.left_ctrl_name_line_edit.setPlaceholderText("Default: _L, L, Left")
        self.left_ctrl_name_line_edit.setToolTip("左コントローラーのカスタム命名規則を入力する.\n" "By default works with '_L', 'L' and 'Left'")
        self.left_ctrl_name_line_edit.setStyleSheet(styles)
        self.left_ctrl_name_line_edit.setText("_L")
        self.right_ctrl_name_line_edit = QtWidgets.QLineEdit()
        self.right_ctrl_name_line_edit.setPlaceholderText("Default: _R, R, Right")
        self.right_ctrl_name_line_edit.setToolTip("右コントローラーのカスタム命名規則を入力する.\n" "By default works with '_R', 'R' and 'Right'")
        self.right_ctrl_name_line_edit.setStyleSheet(styles)
        self.right_ctrl_name_line_edit.setText("_R")

        self.mirror_button = QtWidgets.QPushButton("Mirror")
        self.mirror_button.setToolTip("Running Animation Mirror")
        self.mirror_button.setStyleSheet("background-color: #34d8ed; color: black")
        self.undo_button = QtWidgets.QPushButton("Reset")
        self.undo_button.setToolTip("Cancel the previous Mirror")
        self.undo_button.setStyleSheet("background-color: #34d8ed; color: black")

    def _create_layout(self):
        side_to_opp_rb_layout_1 = QtWidgets.QHBoxLayout()
        side_to_opp_rb_layout_1.addWidget(self.left_to_right_radio_button)
        side_to_opp_rb_layout_1.addWidget(self.right_to_left_radio_button)
        side_to_opp_rb_layout_1.addWidget(self.flip_radio_button)

        side_to_opp_rb_layout_2 = QtWidgets.QHBoxLayout()
        side_to_opp_rb_layout_2.addWidget(self.write_keyframe_checkbox)
        side_to_opp_rb_layout_2.addWidget(self.bake_animation_checkbox)

        mirror_options_layout = QtWidgets.QFormLayout()
        mirror_options_layout.addRow("Mirror Axis:", self.mirror_axis_combo_box)
        mirror_options_layout.addRow("Operation Type:", self.operation_combo_box)
        mirror_options_layout.addRow("", self.min_mirror_frame_spin_box)
        mirror_options_layout.addRow("", self.max_mirror_frame_spin_box)
        mirror_options_layout.addRow("", side_to_opp_rb_layout_1)
        mirror_options_layout.addRow("", side_to_opp_rb_layout_2)

        naming_convention_layout = QtWidgets.QFormLayout()
        naming_convention_layout.addRow("Left Naming Scheme:", self.left_ctrl_name_line_edit)
        naming_convention_layout.addRow("Right Naming Scheme:", self.right_ctrl_name_line_edit)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.mirror_button)
        button_layout.addWidget(self.undo_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.addLayout(mirror_options_layout)
        main_layout.addWidget(self.top_seperator)
        main_layout.addLayout(naming_convention_layout)
        main_layout.addWidget(self.middle_seperator)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.bottom_seperator)
        main_layout.addStretch()

    def _create_connections(self):
        self.operation_combo_box.currentTextChanged.connect(self._operation_change)
        self.mirror_button.clicked.connect(self._apply_mirror_control)
        self.undo_button.clicked.connect(self._undo_control)

    def _operation_change(self):
        text = self._get_operation()

        if text == "Not Selected":
            self.left_to_right_radio_button.setVisible(True)
            self.right_to_left_radio_button.setVisible(True)
            self.flip_radio_button.setVisible(True)
        else:
            self.left_to_right_radio_button.setVisible(False)
            self.right_to_left_radio_button.setVisible(False)
            self.flip_radio_button.setVisible(False)

    def _get_mirror_axis(self):
        return self.mirror_axis_combo_box.currentText()

    def _get_operation(self):
        return self.operation_combo_box.currentText()

    def _get_left_name(self):
        return self.left_ctrl_name_line_edit.text()

    def _get_right_name(self):
        return self.right_ctrl_name_line_edit.text()

    def _get_min_flip_frame(self):
        return self.min_mirror_frame_spin_box.value()

    def _get_max_flip_frame(self):
        return self.max_mirror_frame_spin_box.value()

    @staticmethod
    def get_current_time():
        return cmds.currentTime(q=True)

    @staticmethod
    def _is_even(number):
        return (number % 2) == 0

    @staticmethod
    def _get_vectors_dominating_axis(vector):
        """
        Description: ベクトルがどの軸を最も向いているかを取得する
        Args: vector: is a xyz list of 3 float values
        Returns: A string containing an axis. The axis can also be negative
        """
        # Making positive numbers
        denominator = 0
        for value in vector:
            # Making values positive,
            # so the denominator will be all values added together
            value = abs(value)
            denominator += value
        percentage_strength = []
        for value in vector:
            # Making value positive
            # in order to get a strength relative to the other axis
            value = abs(value)
            strength = value / denominator
            percentage_strength.append(strength)
        # Finding the axis with the highest percentage.
        # Since the percentage_strength is a xyz list.
        # We can use the index to find xyz.
        index = percentage_strength.index(max(percentage_strength))
        if index == 0:
            dominating_axis = "-X" if vector[0] < 0 else "X"
        elif index == 1:
            dominating_axis = "-Y" if vector[1] < 0 else "Y"
        elif index == 2:
            dominating_axis = "-Z" if vector[2] < 0 else "Z"
        else:
            dominating_axis = "-X" if vector[0] < 0 else "X"
        return dominating_axis

    @staticmethod
    def get_min_time():
        return cmds.playbackOptions(minTime=True, query=True)

    @staticmethod
    def get_max_time():
        return cmds.playbackOptions(maxTime=True, query=True)

    @staticmethod
    def get_vector_data(ctrl_list):
        """
        Description: 全コントローラのベクトルを求め、dictionaryに格納する。
        Args: ctrl_list: A list of all anim_curves
        Returns: コントローラをキーとし、その異なる軸ベクトルを値とするdictionaryを返します。軸ベクトルを値とする辞書
        """
        vector_dict = {}
        cur_pos = {}
        # Storing the current position of the ctrl,
        # to get vector data in neutral position
        for ctrl in ctrl_list:
            cur_pos[ctrl] = Animation_Mirror_Window.get_attribute_data([ctrl])
            Animation_Mirror_Window._rotate_ctrl_to_zero(ctrl)
        for ctrl in ctrl_list:
            # getting controller vector in neutral position
            vector_dict[ctrl] = {}
            world_mat = cmds.xform(ctrl, matrix=True, worldSpace=True, query=True)
            # Rounding the values in the world matrix
            for i, value in enumerate(world_mat):
                rounded_value = round(value, 3)
                world_mat[i] = rounded_value
            vector_dict[ctrl]["x_axis"] = world_mat[0:3]
            vector_dict[ctrl]["y_axis"] = world_mat[4:7]
            vector_dict[ctrl]["z_axis"] = world_mat[8:11]
        # Setting ctrl back to its position
        for ctrl in ctrl_list:
            Animation_Mirror_Window._rotate_ctrl_to_data(ctrl, cur_pos[ctrl])
        return vector_dict

    @staticmethod
    def get_attribute_data(ctrl_list):
        """
        Description: すべてのコントローラのチャンネルボックスに表示されるキーテーブル属性のデータを取得する
        Args: ctrl_list: A list of anim_curves
        Returns: コントローラをキーとするdictionaryとそのキーテーブルを返します。チャンネルボックスで表示される属性を値として返す。
        """
        data = {}
        for ctrl in ctrl_list:
            # コントローラーからデータを取得し、dictionaryに格納する。
            data[ctrl] = {}
            # Checking if there exist attributes
            attributes = cmds.listAttr(ctrl, keyable=True, unlocked=True)
            for attr in attributes:
                attr_obj = "{}.{}".format(ctrl, attr)
                lock_check = cmds.getAttr(attr_obj, lock=True)
                if lock_check is True:
                    cmds.setAttr(attr_obj, lock=0)

                # 属性に接続があるかどうかを確認する
                source_controller = cmds.listConnections(attr_obj, source=True, destination=False)
                # Checking if source connection is a key
                anim_curve_keys = cmds.listConnections(attr_obj, source=True, type="animCurve")
                if not source_controller:
                    # Getting the value on the controller and storing it in data dict
                    value = cmds.getAttr(attr_obj)
                    # Only store data if int or float type
                    if type(value) in [int, float]:
                        data[ctrl][attr] = value
                elif anim_curve_keys:
                    # Getting the value on the controller and storing it in data dict
                    value = cmds.getAttr(attr_obj)
                    # Only store data if int or float type
                    if type(value) in [int, float]:
                        data[ctrl][attr] = value

        return data

    @staticmethod
    def _get_selected_controls(ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list):
        """
        Description: ビューポートで選択されているコントローラを取得する
        Args:
            ctrl_list: A list of all anim_curves
            left_ctrl_list: A list of all left anim_curves
            right_ctrl_list: A list of all right anim_curves
            middle_ctrl_list: A list of all middle anim_curves
        Returns: 選択されたコントローラを含むネストされたリストを返す
        """
        sel_controls = cmds.ls(selection=True)
        left_sel_controls = []
        right_sel_controls = []
        middle_sel_controls = []
        for sel_ctrl in sel_controls:
            if sel_ctrl in ctrl_list:
                if sel_ctrl in middle_ctrl_list:
                    middle_sel_controls.append(sel_ctrl)
                elif sel_ctrl in left_ctrl_list:
                    left_sel_controls.append(sel_ctrl)
                elif sel_ctrl in right_ctrl_list:
                    right_sel_controls.append(sel_ctrl)
        return [left_sel_controls, right_sel_controls, middle_sel_controls]

    @staticmethod
    def _get_mirror_axis_dominant_vector(mirror_axis, x_dominating, y_dominating, z_dominating):
        """
        Args:
            mirror_axis: ミラー軸を表す文字列
            x_dominating: x軸がどのワールド軸を指しているかを示す文字列
            y_dominating: y軸がどのワールド軸を指しているかを示す文字列
            z_dominating: z軸がどのワールド軸を指しているかを示す文字列
        Returns:  どのxyz軸がミラー軸を指しているかを返す
        """
        # どの軸がミラー軸に最も近いかを見つける
        if mirror_axis == x_dominating or "-{}".format(mirror_axis) == x_dominating:
            mirror_attr = "X"
        elif mirror_axis == y_dominating or "-{}".format(mirror_axis) == y_dominating:
            mirror_attr = "Y"
        elif mirror_axis == z_dominating or "-{}".format(mirror_axis) == z_dominating:
            mirror_attr = "Z"
        # else文は必要ない、しかし2つの軸が等間隔に配置されている場合、次のような問題が発生
        else:
            mirror_attr = mirror_axis
        return mirror_attr

    @staticmethod
    def _remove_items_from_list(ctrl_list, items):
        """
        Args:
            ctrl_list: A list of anim_curves
            items: A list of anim_curves
        Returns: ctrl_listからitems listの項目を削除したリストを返す
        """
        for item in items:
            ctrl_list.remove(item)
        return ctrl_list

    @staticmethod
    def _rotate_ctrl_to_zero(ctrl):
        """
        Description: コントローラーの回転をゼロに設定
        Args:
            ctrl: controller
            auto key: オートキーを無効にするか
        """
        for attr in ["X", "Y", "Z"]:
            if cmds.listAttr("{}.rotate{}".format(ctrl, attr), keyable=True, unlocked=True):
                auto_key = cmds.autoKeyframe(state=True, query=True)
                if auto_key:
                    cmds.autoKeyframe(state=False)
                cmds.setAttr("{}.rotate{}".format(ctrl, attr), 0)
                if auto_key:
                    cmds.autoKeyframe(state=True)

    @staticmethod
    def _rotate_ctrl_to_data(ctrl, data):
        """
        Description: コントローラの回転をデータで指定されたものに設定
        Args:
            ctrl controller
            data： 回転を値とするコントローラを含むdictionary
            auto_key： オートキーを無効にするか
        """
        for attr in ["X", "Y", "Z"]:
            if "rotate{}".format(attr) in data[ctrl].keys():
                auto_key = cmds.autoKeyframe(state=True, query=True)
                if auto_key:
                    cmds.autoKeyframe(state=False)
                cmds.setAttr("{}.rotate{}".format(ctrl, attr), data[ctrl]["rotate{}".format(attr)])
                if auto_key:
                    cmds.autoKeyframe(state=True)

    @staticmethod
    def _split_string(name, split):
        """
        Description:
            定義した場所でコントローラ名を分割
        Args:
            name: コントローラの名前を表す文字列
            split： 名前を分割する場所を表す文字列
        """
        split_list = name.split(split)

        # Getting the length of the split name
        length = len(split_list) - 1
        # Making a list of the different combinations of names
        return_dict = {}
        return_dict["index"] = []
        return_dict["string"] = []

        # Iterating over the length to get the correct amount of item in the list
        for i in range(length):
            string = ""
            index = None
            # Iterating over the split name to reassemble the name
            for x, item in enumerate(split_list):
                string += item
                # Skip adding the side_str
                # if the two for loops are on same iteration
                # also don't add the side_str at the end
                if i == x:
                    index = len(string)
                    return_dict["index"].append(index)
                if not i == x and x != length:
                    string += split
            # In case the same letter is next to each-other
            # like the word 'belly' would split 'bel' 'y' and 'be' 'ly'
            # and when reassembled it would give belly on both
            if not string in return_dict["string"]:
                return_dict["string"].append(string)
        return return_dict

    @staticmethod
    def _is_mirror_same_as_dominants(mirror_axis, dominent, opp_dominent):
        """
        Args:
            mirror_axis: The predefined mirror axis
            dominant: The dominant axis of the controller
            opp dominant: The dominant axis of the opposite controller

        Return:
            Returns a True if the dominant and opposite dominant axis
            is the same. And also the same as the mirror axis, no matter
            if the dominant axis is positive or negative.
        """
        return (
            mirror_axis == dominent
            and mirror_axis == opp_dominent
            or "-{}".format(mirror_axis) == dominent
            and "-{}".format(mirror_axis) == opp_dominent)

    @staticmethod
    def _is_dominants_same_and_not_mirror(mirror_axis, dominent, opp_dominent):
        """
        Args:
            mirror_axis: 定義済みのミラー軸
            dominant: コントローラーの軸
            opp dominant: 反対側のコントローラーの軸
        Return:
            Returns a True if the dominant and opposite dominant axis is the same.
            And they are not the same as the mirror axis, no matter if the dominant axis is positive or negative.
        """
        pos_mirror = dominent == opp_dominent and not dominent == mirror_axis
        neg_mirror = dominent == opp_dominent and not dominent == "-{}".format(mirror_axis)
        # Returning False if any of the two statement is False
        if not pos_mirror or not neg_mirror:
            return False
        else:
            return True

    @staticmethod
    def _reassemble_ctrl_name(name, side, index):
        """
        Args:
            name: サイドを除いたコントローラ名
            side: サイドの命名規則
            index: 名前にサイドを入れる場所を指定する。
        Return:
            側を含むコントローラの名前を返します。
        """
        # Creating the name of the ctrl
        ctrl_name = ""
        for i, letter in enumerate(name):
            # If the index and I is the same
            # then that is where the side should be
            if i == index:
                ctrl_name += side
            ctrl_name += letter
            # If the index and len of name is the same
            # then the side is at the end of the name
            if len(name) == index and i + 1 == index:
                ctrl_name += side
        return ctrl_name


    def _calc_side_controller(self):
        left_naming = self._get_left_name()
        right_naming = self._get_right_name()
        if not left_naming and not right_naming:
            side_con = self.prefix
        elif not left_naming and right_naming:
            om.MGlobal.displayError("There is inputted {} in right naming convention. " "Therefore left naming convention " "also needs an input".format(right_naming))
            return
        elif left_naming and not right_naming:
            om.MGlobal.displayError("There is inputted {} in left naming convention. " "Therefore right naming convention " "also needs an input".format(left_naming))
            return
        else:
            side_con = [left_naming, right_naming]
        return side_con

    @staticmethod
    def get_controllers(side_con):
        """
        Args:
            side_con: サイドの命名規約のリストです。
                このリストは、同じ命名規則が隣り合っている必要があります。
                を隣り合わせにし、右の名前が高いインデックスである必要があります。
                例えば、アッパー（"L"）が使用される場合、左はインデックス0であり
                で、右（"R"）は一つ上のインデックス1である。
                下段のネーミングを使用した場合、左がインデックス2で、右が1つ上のインデックス3です。
                右は1つ上のインデックス3です。つまり、左は常に偶数でなければならず
                は偶数、右は1つ上の奇数でなければならない。

        Return: 左、右、真ん中、すべてのコントローラのキーを持つdictionaryを返します。
            コントローラを返します。また、どのようなコントローラがペアなのかを含むpairも返します。そして、そのペアには番号が割り振られます。
        """
        # Finding all the nurb curves to get the shape node on the anim_curves
        nurbs_curve_list = cmds.ls(type="nurbsCurve")
        nurbs_surface_list = cmds.ls(type="nurbsSurface")
        if nurbs_surface_list:
            for curve in nurbs_surface_list:
                nurbs_curve_list.append(curve)

        print("nurbs_curve_list => {0}, nurbs_surface_list => {1}".format(len(nurbs_curve_list), len(nurbs_surface_list)))

        shape_list = nurbs_curve_list
        ctrl_list = []
        left_ctrl_list = []
        right_ctrl_list = []
        middle_ctrl_list = []
        str_combinations = []
        return_dict = {}
        pair_dict = {}
        pair_dict["controls"] = {}
        pair_dict["pairNumber"] = {}
        pair_number = 0

        # すべてのshape controllerを反復処理する
        for shape in shape_list:
            parent = cmds.listRelatives(shape, parent=True)[0]
            # 同じ名前のコントローラが複数あるかどうかを確認する
            dub_names = cmds.ls(parent, exactType="transform")
            for ctrl in dub_names:
                clash_name = ctrl.rsplit("|", 1)[-1]

                if not ctrl in ctrl_list:
                    # コントローラーがキーが使える属性を取得したかどうかを確認する、そうでなければ、コントロールをミラーリングする理由はない
                    if cmds.listAttr(ctrl, keyable=True):
                        ctrl_list.append(ctrl)
                        # Making the assumption that every rigger is using either "L", "l", "R" or "r" to define side
                        # this list can also be expanded with Lf and Rt if wished
                        for i, side in enumerate(side_con):
                            # if the ctrl == clash name, then there
                            # is not a classing name
                            if ctrl == clash_name:
                                names = Animation_Mirror_Window._split_string(ctrl, side)
                            else:
                                names = Animation_Mirror_Window._split_string(clash_name, side)
                            if names:
                                for name in names["string"]:
                                    # もしその名前がスティングの組み合わせの中にあれば
                                    # スティングの組み合わせに名前がある場合
                                    # 左右に分割したときに
                                    # 結果的に同じ文字列になる
                                    # したがって現在のCtrl
                                    # は右コントローラである
                                    if name in str_combinations:
                                        # Finding what index the split string
                                        # name that is both left and right side is.
                                        index_dict = names["string"].index(name)
                                        # Using that to get where
                                        # in the string the left right name is
                                        index = names["index"][index_dict]

                                        # Creating the name of the anim_curves
                                        even = Animation_Mirror_Window._is_even(i)
                                        if even:
                                            right_side = side_con[i + 1]
                                            left_side = side_con[i]
                                        else:
                                            right_side = side_con[i]
                                            left_side = side_con[i - 1]
                                        right_ctrl = Animation_Mirror_Window._reassemble_ctrl_name(name, right_side, index)
                                        left_ctrl = Animation_Mirror_Window._reassemble_ctrl_name(name, left_side, index)
                                        if ctrl == clash_name:
                                            if not right_ctrl in right_ctrl_list:
                                                right_ctrl_list.append(right_ctrl)
                                            if not left_ctrl in left_ctrl_list:
                                                left_ctrl_list.append(left_ctrl)
                                            pair_dict["controls"][right_ctrl] = pair_number
                                            pair_dict["controls"][left_ctrl] = pair_number
                                            pair_dict["pairNumber"][pair_number] = [left_ctrl, right_ctrl]
                                            pair_number += 1
                                        else:
                                            left_dubs = cmds.ls(left_ctrl, exactType="transform")
                                            right_dubs = cmds.ls(right_ctrl, exactType="transform")
                                            for left_dub, right_dub in zip(left_dubs, right_dubs):
                                                pair_dict["controls"][left_dub] = pair_number
                                                pair_dict["controls"][right_dub] = pair_number
                                                pair_dict["pairNumber"][pair_number] = [left_dub, right_dub]
                                                pair_number += 1
                                                if not left_dub in left_ctrl_list:
                                                    left_ctrl_list.append(left_dub)
                                                if not right_dub in right_ctrl_list:
                                                    right_ctrl_list.append(right_dub)
                                    else:
                                        # Adding the name to a list,
                                        # to check if right side matches
                                        str_combinations.append(name)

        for ctrl in ctrl_list:
            if not ctrl in right_ctrl_list and not ctrl in left_ctrl_list:
                middle_ctrl_list.append(ctrl)
        return_dict["left"] = left_ctrl_list
        return_dict["right"] = right_ctrl_list
        return_dict["middle"] = middle_ctrl_list
        return_dict["all"] = ctrl_list
        return_dict["pair"] = pair_dict
        return return_dict


    # side controller mirror
    # arm l or r
    # leg l or r
    @staticmethod
    def mirror_side_ctrl(ctrl_list, data, mirror_axis, pair_dict, vector_data, is_write_key_frame):
        """
        Description: ミラーコントローラーは片側から反対側へ（反対側）
        Args:
            ctrl_list： array controller
            data ： コントローラを含むdictionary 属性を持つコントローラを含むdictionary
            mirror_axis： ミラー軸を表す文字列
            pair_dict： コントローラとその反対側のコントローラを対にしたdictionary
            vector_data: 軸のベクトルを含むdictionaryすべてのコントローラ
            is_write_key_frame: keyframeを書き込むかどうか
        """
        # controller bake keyframe
        current_time = Animation_Mirror_Window.get_current_time()
        opp_ctrl = None
        for ctrl in ctrl_list:
            # Getting pair number
            pair_number = pair_dict["controls"][ctrl]
            for pair_ctrl in pair_dict["pairNumber"][pair_number]:
                if not pair_ctrl == ctrl:
                    opp_ctrl = pair_ctrl
            # Getting the direction of the axis on controller
            x_axis = vector_data[ctrl]["x_axis"]
            y_axis = vector_data[ctrl]["y_axis"]
            z_axis = vector_data[ctrl]["z_axis"]
            # Getting the direction of the axis on opposite controller
            opp_x_axis = vector_data[opp_ctrl]["x_axis"]
            opp_y_axis = vector_data[opp_ctrl]["y_axis"]
            opp_z_axis = vector_data[opp_ctrl]["z_axis"]

            for attr in data[ctrl].keys():
                if attr not in Animation_Mirror_Window.SOURCE_TRANSFORM_ATTRIBUTE:
                    continue

                value = data[ctrl][attr]
                x_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(x_axis)
                y_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(y_axis)
                z_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(z_axis)
                opp_x_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(opp_x_axis)
                opp_y_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(opp_y_axis)
                opp_z_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(opp_z_axis)

                # 軸がmirrorの軸に最も近いかを探す
                mirror_attr = Animation_Mirror_Window._get_mirror_axis_dominant_vector(mirror_axis, x_dominating, y_dominating, z_dominating)
                attr_obj = "{}.{}".format(opp_ctrl, attr)

                if attr.__contains__("scale"):
                    cmds.setAttr(attr_obj, value)
                    if is_write_key_frame is True:
                        cmds.setKeyframe(attr_obj, v=value, t=current_time)
                elif x_dominating == opp_x_dominating and y_dominating == opp_y_dominating and z_dominating == opp_z_dominating:
                    if attr.__contains__("rotate{}".format(mirror_attr)):
                        cmds.setAttr(attr_obj, value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=value, t=current_time)
                    elif attr.__contains__("rotate"):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif attr.__contains__("translate{}".format(mirror_attr)):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    else:
                        cmds.setAttr(attr_obj, value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=value, t=current_time)
                elif attr.__contains__("translate"):
                    if Animation_Mirror_Window._is_mirror_same_as_dominants(mirror_axis, x_dominating, opp_x_dominating):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif Animation_Mirror_Window._is_mirror_same_as_dominants(mirror_axis, y_dominating, opp_y_dominating):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif Animation_Mirror_Window._is_mirror_same_as_dominants(mirror_axis, z_dominating, opp_z_dominating):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif x_dominating == opp_x_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        elif attr.__contains__("X"):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif y_dominating == opp_y_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        elif attr.__contains__("Y"):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    elif z_dominating == opp_z_dominating:
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        elif attr.__contains__("Z"):
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    else:
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                elif attr.__contains__("rotate"):
                    if Animation_Mirror_Window._is_dominants_same_and_not_mirror(mirror_axis, x_dominating, opp_x_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        elif attr.__contains__("X"):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                    elif Animation_Mirror_Window._is_dominants_same_and_not_mirror(mirror_axis, y_dominating, opp_y_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        elif attr.__contains__("Y"):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                    elif Animation_Mirror_Window._is_dominants_same_and_not_mirror(mirror_axis, z_dominating, opp_z_dominating):
                        if attr.__contains__(mirror_attr):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        elif attr.__contains__("Z"):
                            cmds.setAttr(attr_obj, -value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                        else:
                            cmds.setAttr(attr_obj, value)
                            if is_write_key_frame is True:
                                cmds.setKeyframe(attr_obj, v=value, t=current_time)
                    else:
                        cmds.setAttr(attr_obj, value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=value, t=current_time)
                else:
                    cmds.setAttr(attr_obj, value)
                    if is_write_key_frame is True:
                        cmds.setKeyframe(attr_obj, v=value, t=current_time)

    # center controller mirror
    # spine joint etc...
    @staticmethod
    def mirror_center_ctrl(ctrl_list, data, mirror_axis, vector_data, is_write_key_frame):
        """
        Description: 真ん中のコントローラーを反転させる
        Args:
            ctrl_list： array middle controller
            data： コントローラdictionary 属性を持つコントローラを含む dictionary
            mirror_axis： ミラー軸を表す文字列
            vector_data: 軸のベクトルを含む dictionary すべてのコントローラ
        """
        # controller bake keyframe
        current_time = Animation_Mirror_Window.get_current_time()

        for ctrl in ctrl_list:
            # Getting the direction of the axis on middle controller
            # Getting the direction of the axis on controller
            x_axis = vector_data[ctrl]["x_axis"]
            y_axis = vector_data[ctrl]["y_axis"]
            z_axis = vector_data[ctrl]["z_axis"]
            for attr in data[ctrl].keys():

                if attr not in Animation_Mirror_Window.SOURCE_TRANSFORM_ATTRIBUTE:
                    continue

                value = data[ctrl][attr]
                x_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(x_axis)
                y_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(y_axis)
                z_dominating = Animation_Mirror_Window._get_vectors_dominating_axis(z_axis)
                # Finding what axis is pointing the most to the mirror axis
                mirror_attr = Animation_Mirror_Window._get_mirror_axis_dominant_vector(mirror_axis, x_dominating, y_dominating, z_dominating)
                attr_obj = "{}.{}".format(ctrl, attr)

                if attr.__contains__("scale"):
                    cmds.setAttr(attr_obj, value)
                    if is_write_key_frame is True:
                        cmds.setKeyframe(attr_obj, v=value, t=current_time)
                elif attr.__contains__("translate"):
                    if attr.__contains__(mirror_attr):
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)
                    else:
                        pass
                elif attr.__contains__("rotate"):
                    if attr.__contains__(mirror_attr):
                        cmds.setAttr(attr_obj, value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=value, t=current_time)
                    else:
                        cmds.setAttr(attr_obj, -value)
                        if is_write_key_frame is True:
                            cmds.setKeyframe(attr_obj, v=-value, t=current_time)

    # @TODO
    # flipping controller
    # refactoring
    def _flip_frame(self, left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data):
        Animation_Mirror_Window.flip_frame_outer(left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data, self.is_write_keyframe)

    @staticmethod
    def flip_frame_outer(left_ctrl_list, right_ctrl_list, middle_ctrl_list, data, pair_dict, mirror_axis, vector_data, is_write_key_frame):
        Animation_Mirror_Window.mirror_side_ctrl(ctrl_list=left_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=is_write_key_frame)
        Animation_Mirror_Window.mirror_side_ctrl(ctrl_list=right_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=is_write_key_frame)
        Animation_Mirror_Window.mirror_center_ctrl(ctrl_list=middle_ctrl_list, data=data, mirror_axis=mirror_axis, vector_data=vector_data, is_write_key_frame=is_write_key_frame)

    @preserve_selection
    def _apply_mirror_control(self):
        self._mirror_control()
        pass

    # Cancels the processing of the previous mirror.
    def _undo_control(self):
        #cmds.undo()

        side_con = self._calc_side_controller()
        self.is_write_keyframe = self.write_keyframe_checkbox.isChecked()
        controls = self.get_controllers(side_con)
        ctrl_list = controls["all"]

        if not ctrl_list:
            om.MGlobal.displayError("Couldn't find nurbsCurve or nurbsSurface in scene.")
            return

        operation = self.undo_data['operation']
        if operation is None:
            return

        local_start_frame = int(self.undo_data['start_frame'])
        local_end_frame = int(self.undo_data['end_frame'])

        for frame in range(local_start_frame, local_end_frame):
            current_frame = float(frame)
            print("undo calc keyframe parameters => {0}".format(current_frame))
            cmds.currentTime(current_frame)

            # dict
            for animation in self.undo_data['animation']:
                value = animation[0]
                if value == frame:
                    print('match frame index => {}'.format(value))
                    instance = animation[1]
                    instance.undo_pose_transform(current_frame)

        # finish
        cmds.currentTime(local_start_frame)
        pass

    # Processing itself is heavy, so lightweight is necessary.
    def _mirror_control(self):
        side_con = self._calc_side_controller()
        self.is_write_keyframe = self.write_keyframe_checkbox.isChecked()
        self.is_bake_animation = self.bake_animation_checkbox.isChecked()
        print("side_con => {0}".format(side_con))

        controls = self.get_controllers(side_con)
        left_ctrl_list = controls["left"]
        right_ctrl_list = controls["right"]
        middle_ctrl_list = controls["middle"]
        ctrl_list = controls["all"]
        pair_dict = controls["pair"]

        if not ctrl_list:
            om.MGlobal.displayError("Couldn't find nurbsCurve or nurbsSurface in scene.")
            return

        if not left_ctrl_list and not right_ctrl_list:
            om.MGlobal.displayWarning("Couldn't find side anim_curves. ")
            return

        operation = self._get_operation()
        mirror_axis = self._get_mirror_axis()
        # create start-end range
        local_start_frame = int(self._get_min_flip_frame())
        local_end_frame = int(self._get_max_flip_frame())
        local_end_frame += 1

        print("start frame => {}, end frame => {}".format(local_start_frame, local_end_frame))

        self.undo_data['start_frame'] = local_start_frame
        self.undo_data['end_frame'] = local_end_frame
        self.undo_data['operation'] = operation
        animation = {}

        for frame in range(local_start_frame, local_end_frame):
            current_frame = float(frame)
            print("calc keyframe parameters => {0}".format(current_frame))
            cmds.currentTime(current_frame)
            vector_data = Animation_Mirror_Window.get_vector_data(ctrl_list)
            data = Animation_Mirror_Window.get_attribute_data(ctrl_list)

            instance = Undo_Animation_Data()
            instance.cache_pose_transform(controller=ctrl_list, data=data)
            animation[frame] = instance

            if operation == OperationType.left_to_right:
                self.mirror_side_ctrl(ctrl_list=left_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
            elif operation == OperationType.right_to_left:
                self.mirror_side_ctrl(ctrl_list=right_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
            elif operation == OperationType.flip_to_frame:
                self._flip_frame(left_ctrl_list=left_ctrl_list, right_ctrl_list=right_ctrl_list, middle_ctrl_list=middle_ctrl_list, data=data, pair_dict=pair_dict, mirror_axis=mirror_axis, vector_data=vector_data)
            elif operation == OperationType.mirror_middle:
                self.mirror_center_ctrl(ctrl_list=middle_ctrl_list, data=data, mirror_axis=mirror_axis, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)

            elif operation == OperationType.selected:
                (
                    left_sel_controls,
                    right_sel_controls,
                    middle_sel_controls,
                ) = self._get_selected_controls(ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list)
                if not left_sel_controls and not right_sel_controls and not middle_sel_controls:
                    om.MGlobal.displayError("No controller is selected")
                    return

                if left_sel_controls:
                    self.mirror_side_ctrl(ctrl_list=left_sel_controls, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                if right_sel_controls:
                    self.mirror_side_ctrl(ctrl_list=right_sel_controls, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                if middle_sel_controls:
                    self.mirror_center_ctrl(ctrl_list=middle_sel_controls, data=data, mirror_axis=mirror_axis, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)

            elif operation == OperationType.not_selected:
                (
                    left_sel_controls,
                    right_sel_controls,
                    middle_sel_controls,
                ) = self._get_selected_controls(ctrl_list, left_ctrl_list, right_ctrl_list, middle_ctrl_list)
                if not left_sel_controls and not right_sel_controls and not middle_sel_controls:
                    om.MGlobal.displayWarning("No controller is selected")
                    return

                removed_left_ctrl_list = self._remove_items_from_list(left_ctrl_list, left_sel_controls)
                removed_right_ctrl_list = self._remove_items_from_list(right_ctrl_list, right_sel_controls)
                removed_middle_ctrl_list = self._remove_items_from_list(middle_ctrl_list, middle_sel_controls)
                if self.left_to_right_radio_button.isChecked():
                    if removed_left_ctrl_list:
                        self.mirror_side_ctrl(ctrl_list=removed_left_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                    if removed_middle_ctrl_list:
                        self.mirror_center_ctrl(ctrl_list=removed_middle_ctrl_list, data=data, mirror_axis=mirror_axis, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                elif self.right_to_left_radio_button.isChecked():
                    if removed_right_ctrl_list:
                        self.mirror_side_ctrl(ctrl_list=removed_right_ctrl_list, data=data, mirror_axis=mirror_axis, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                    if removed_middle_ctrl_list:
                        self.mirror_center_ctrl(ctrl_list=removed_middle_ctrl_list, data=data, mirror_axis=mirror_axis, vector_data=vector_data, is_write_key_frame=self.is_write_keyframe)
                elif self.flip_radio_button.isChecked():
                    self._flip_frame(left_ctrl_list=removed_left_ctrl_list, right_ctrl_list=removed_right_ctrl_list, middle_ctrl_list=removed_middle_ctrl_list, data=data, pair_dict=pair_dict, mirror_axis=mirror_axis, vector_data=vector_data)

        # finish
        cmds.currentTime(local_start_frame)
        dic2 = sorted(animation.items(), key=lambda x:x[0])
        self.undo_data['animation'] = dic2

        if self.is_bake_animation is True:
            cmds.refresh(suspend=True)
            cmds.bakeResults(ctrl_list, t=(local_start_frame, local_end_frame), sb=1, at=self.SOURCE_TRANSFORM_ATTRIBUTE, hi="none")
            cmds.refresh(suspend=False)

    def showEvent(self, event):
        super(Animation_Mirror_Window, self).showEvent(event)
        if self.geometry:
            self.restoreGeometry(self.geometry)

    def closeEvent(self, event):
        if isinstance(self, Animation_Mirror_Window):
            super(Animation_Mirror_Window, self).closeEvent(event)
            self.geometry = self.saveGeometry()


def show_main_window():
    global mirror_control
    try:
        mirror_control.close()  # type: ignore
        mirror_control.deleteLater()  # type: ignore
    except:
        pass

    app = QtWidgets.QApplication.instance()
    mirror_control = Animation_Mirror_Window()
    mirror_control.show()

    app.exec_()
    return mirror_control



class Undo_Animation_Data:
    def __init__(self):
        self.controller_dict = {}

    # caches one frame all controller transforms
    def cache_pose_transform(self, controller, data):
        for control in controller:
            for local_attr in data[control].keys():
                attr_obj = "{0}.{1}".format(control, local_attr)
                value = cmds.getAttr(attr_obj)
                self.controller_dict["{}".format(attr_obj)] = value
        pass

    def undo_pose_transform(self, time):
        for pair in self.controller_dict.items():
            attr_obj = pair[0]
            value = pair[1]
            cmds.setAttr(attr_obj, value)
            cmds.setKeyframe(attr_obj, v=value, t=time)
            #print("undo_pose_transform => {}".format(attr_obj))
        pass

# @TODO
class Animation_Mirror_Model:

    def __init__(self):
        self.controller = {}
        self.batch_running_text = None
        self.mirror_axis_text = None
        self.prefix = "_Mirror"

        # @TODO
        # need a bat setting
        self.side_con = ["_L", "_R", "left", "right"]

    @staticmethod
    def _handle_remove_plugins():
        cmds.loadPlugin("fbxmaya.mll")
        plugins = cmds.unknownPlugin(query=True, list=True) or []
        if plugins:
            for plugin in plugins:
                cmds.unknownPlugin(plugin, remove=True)
                print("unload plugin => {}".format(plugin))

    def start_run(self, *args):
        """
        Args: file path, mirror mode, mirror axis
        """
        file_path = args[0]
        index = args[1]
        mirror_axis = args[2]

        if file_path is None:
            print("not valid file path => {}".format(file_path))
            return

        if index is 1:
            self.batch_running_text = OperationType.left_to_right
        elif index is 2:
            self.batch_running_text = OperationType.right_to_left
        elif index is 3:
            self.batch_running_text = OperationType.flip_to_frame
        else:
            print("not valid mirror mode => {}".format(index))
            return

        if mirror_axis is 1:
            self.mirror_axis_text = "X"
        elif mirror_axis is 2:
            self.mirror_axis_text = "Y"
        elif mirror_axis is 3:
            self.mirror_axis_text = "Z"
        else:
            print("not valid mirror axis => {}".format(mirror_axis))
            return

        self._handle_remove_plugins()

        # file open
        cmds.file(file_path, o=True, type='mayaAscii', force=True)
        asset_file_path = cmds.file(q=True, sn=True)
        new_file_name = os.path.basename(asset_file_path)
        scene_name = os.path.splitext(os.path.basename(cmds.file(q=True, sn=True)))[0]
        base_directory = asset_file_path.split(new_file_name)[-2]
        new_scene_name = scene_name + self.prefix
        print("asset_file_path => {}".format(asset_file_path))
        print("filename => {}".format(new_file_name))
        print("scene_name => {}".format(scene_name))
        print("new_scene_name => {}".format(new_scene_name))
        print("base_directory => {}".format(base_directory))

        cmds.currentUnit(time='60fps')
        time_string = mel.eval('currentTimeUnitToFPS')
        print("fps => {}".format(time_string))
        print("choose mirror mode => {}".format(self.batch_running_text))
        print("choose mirror axis => {}".format(self.mirror_axis_text))

        self.controller = Animation_Mirror_Window.get_controllers(self.side_con)
        left_ctrl_list = self.controller["left"]
        right_ctrl_list = self.controller["right"]
        middle_ctrl_list = self.controller["middle"]
        ctrl_list = self.controller["all"]
        pair_dict = self.controller["pair"]

        if not ctrl_list:
            print("Couldn't find nurbsCurve or nurbsSurface in scene.")
            return

        if not left_ctrl_list and not right_ctrl_list:
            print("Couldn't find side anim_curves. ")
            return

        operation = self.batch_running_text
        local_start_frame = int(Animation_Mirror_Window.get_min_time())
        local_end_frame = int(Animation_Mirror_Window.get_max_time())
        local_end_frame += 1
        print("start frame => {}, end frame => {}".format(local_start_frame, local_end_frame))

        print("BEGIN MIRROR ANIMATION => {}".format(asset_file_path))
        for frame in range(local_start_frame, local_end_frame):
            current_frame = float(frame)
            print("calc keyframe parameters => {0}".format(current_frame))
            cmds.currentTime(current_frame)
            vector_data = Animation_Mirror_Window.get_vector_data(ctrl_list)
            data = Animation_Mirror_Window.get_attribute_data(ctrl_list)

            if operation == OperationType.left_to_right:
                Animation_Mirror_Window.mirror_side_ctrl(ctrl_list=left_ctrl_list, data=data, mirror_axis=self.mirror_axis_text, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=True)
            elif operation == OperationType.right_to_left:
                Animation_Mirror_Window.mirror_side_ctrl(ctrl_list=right_ctrl_list, data=data, mirror_axis=self.mirror_axis_text, pair_dict=pair_dict, vector_data=vector_data, is_write_key_frame=True)
            elif operation == OperationType.flip_to_frame:
                Animation_Mirror_Window.flip_frame_outer(left_ctrl_list=left_ctrl_list, right_ctrl_list=right_ctrl_list, middle_ctrl_list=middle_ctrl_list, data=data, pair_dict=pair_dict, mirror_axis=self.mirror_axis_text, vector_data=vector_data, is_write_key_frame=True)

        # finish
        print("BEGIN BAKE ANIMATION => {}".format(asset_file_path))
        cmds.currentTime(local_start_frame)
        cmds.refresh(suspend=True)
        cmds.bakeResults(ctrl_list, t=(local_start_frame, local_end_frame), sb=1, at=Animation_Mirror_Window.SOURCE_TRANSFORM_ATTRIBUTE, hi="none")
        cmds.refresh(suspend=False)

        # rename ma file
        cmds.file(rename=base_directory + new_scene_name + ".ma")
        cmds.file(save=True, type='mayaAscii', force=True)


