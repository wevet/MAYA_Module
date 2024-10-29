# -*- coding: utf-8 -*-

"""
supported version MAYA 2023
"""
from os.path import exists

import maya.cmds as cmds
import maya.OpenMayaUI as omui
import sys

info = cmds.about(version=True)
version = int(info.split(" ")[0])

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from shiboken2 import wrapInstance


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)


class LightManager(QtWidgets.QDialog):
    WINDOW_TITLE = "Maya & Substance Painter Light Manager"
    MODULE_VERSION = "1.2"

    def __init__(self, parent=None, *args, **kwargs):
        super(LightManager, self).__init__(maya_main_window())

        self.default_style = "background-color: #34d8ed; color: black"
        self.setStyleSheet('background-color:#262f38;')
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 240)

        # レイアウト
        self.layout = QtWidgets.QVBoxLayout()

        self.search_button = None

        self.light_direction_label = None
        self.light_direction_edit = None

        self.sp_light_label = None
        self.sp_light_direction_edit = None

        self.selected_light_label = None
        self.selected_light_edit = None

        self._create_ui()

    # create GUI
    def _create_ui(self):
        # 手動でライト名を入力するテキストフィールド
        self.selected_light_label = QtWidgets.QLabel("Selected Light:")
        self.selected_light_edit = QtWidgets.QLineEdit()
        self.selected_light_edit.setReadOnly(True)
        self.search_button = QtWidgets.QPushButton("Search Light")
        self.search_button.setStyleSheet(self.default_style)

        self.light_direction_label = QtWidgets.QLabel("Maya Light Direction:")
        self.light_direction_edit = QtWidgets.QLineEdit()

        # Substance Painterのライト情報表示
        self.sp_light_label = QtWidgets.QLabel("Substance Light Direction:")
        self.sp_light_direction_edit = QtWidgets.QLineEdit()

        # レイアウトに追加
        self.layout.addWidget(self.selected_light_label)
        self.layout.addWidget(self.selected_light_edit)

        self.layout.addWidget(self.search_button)
        self.layout.addWidget(self.light_direction_label)
        self.layout.addWidget(self.light_direction_edit)
        self.layout.addWidget(self.sp_light_label)
        self.layout.addWidget(self.sp_light_direction_edit)
        self.setLayout(self.layout)
        self.search_button.clicked.connect(self._search_light)

    """
    テキストフィールドに入力されたライト名を検索
    """

    def _search_light(self):
        # 現在選択されているライトを取得
        selected_lights = cmds.ls(selection=True, dag=True, type="transform")
        #selected_lights = cmds.ls(selection=True, dag=True, type="light")

        if selected_lights:
            light_name = selected_lights[0]
            self.selected_light_edit.setText(light_name)
            self._update_light_direction(light_name)
        else:
            QMessageBox.warning(self, "Search Light", "No light selected.")

    """
    選択したtransform objectはlightであるかの判定
    """

    @staticmethod
    def get_light_transform_attributes(light_name):
        # シェイプノードを取得
        light_shape = cmds.listRelatives(light_name, shapes=True)
        if not light_shape:
            raise ValueError(f"No shape found for {light_name}.")

        light_shape = light_shape[0]
        # ライトシェイプかどうかを判定
        if cmds.objectType(light_shape, isAType='light'):
            # トランスフォームノードを取得
            transform_node = cmds.listRelatives(light_shape, parent=True)[0]
            # トランスフォームアトリビュートを取得
            position = cmds.xform(transform_node, query=True, translation=True, worldSpace=True)
            rotation = cmds.xform(transform_node, query=True, rotation=True, worldSpace=True)
            # 不動小数点下三桁までの表示に変換
            formatted_position = [round(coord, 3) for coord in position]
            formatted_rotation = [round(angle, 3) for angle in rotation]
            return formatted_position, formatted_rotation
        else:
            # ライトシェイプではない場合は (0, 0, 0) を返す
            return [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]

    """
    選択されたMayaのライトの向きを更新
    """

    def _update_light_direction(self, select_light):
        if select_light:
            position, rotation = LightManager.get_light_transform_attributes(select_light)

            if len(rotation) >= 3 and len(position) >= 3:
                self.light_direction_edit.setText(f"X: {rotation[0]}, Y: {rotation[1]}, Z: {rotation[2]}")
                self._update_sp_light_direction(rotation, position)

    """
    MayaのベクトルをSubstance用に変換
    """
    @staticmethod
    def _convert_to_substance_vector(position, direction):
        # Maya (Y-Up) から Substance Painter (Z-Up) への変換
        # Horizontal RotationにY軸の回転を、Vertical RotationにX軸の回転を適用
        horizontal_rotation = LightManager.convert_rotation_to_substance(direction[1])
        vertical_rotation = LightManager.convert_rotation_to_substance(-direction[0])
        return horizontal_rotation, vertical_rotation


    """
    Substance Painterのデフォルトライトの向きを表示
    """
    def _update_sp_light_direction(self, rotation, position):
        #sp_position, sp_rotation = LightManager._convert_to_substance_vector(position, rotation)

        # 変換されたSubstance用のHorizontal/Vertical Rotationの値を取得
        horizontal_rotation, vertical_rotation = LightManager._convert_to_substance_vector(position, rotation)

        # Substance Painter用のパラメータとしてGUIに表示
        self.sp_light_direction_edit.setText(f"Horizontal: {horizontal_rotation}°, Vertical: {vertical_rotation}°")


    @staticmethod
    def convert_rotation_to_substance(angle):
        # -180〜180の値を0〜360に変換
        if angle < 0:
            converted_angle = angle + 360
        else:
            converted_angle = angle
        return converted_angle


def show_main_window():
    global light_manager_ui
    try:
        light_manager_ui.close()
        light_manager_ui.deleteLater()
    except:
        pass
    light_manager_ui = LightManager()
    light_manager_ui.show()
    return light_manager_ui
