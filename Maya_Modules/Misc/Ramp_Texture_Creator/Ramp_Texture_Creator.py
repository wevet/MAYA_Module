# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox, QHBoxLayout
from PySide2.QtCore import Qt
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)


class RampTextureToolGUI(QtWidgets.QWidget):
    def __init__(self, parent=maya_main_window()):
        super(RampTextureToolGUI, self).__init__(parent)

        self.setWindowTitle("Ramp Texture Creator")
        self.setGeometry(300, 300, 400, 400)

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.grid_layout = QtWidgets.QGridLayout()
        self.buttons = []

        self.ramp_node = None  # ランプノードを格納するための変数

        # グリッドボタンの作成
        for i in range(5):
            for j in range(5):
                button = QtWidgets.QPushButton(f"{i * 5 + j + 1}")
                button.clicked.connect(lambda _, b=button: self.set_color(b))
                self.grid_layout.addWidget(button, i, j)
                self.buttons.append(button)

        # サイズ入力フィールドの作成
        size_layout = QHBoxLayout()
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Width (default: 1024)")
        self.width_input.setText("1024")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Height (default: 1024)")
        self.height_input.setText("1024")

        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_input)

        # ボタンの作成
        self.create_ramp_button = QtWidgets.QPushButton("Create Ramp")
        self.create_ramp_button.clicked.connect(self.create_ramp)

        self.export_button = QtWidgets.QPushButton("Export Texture")
        self.export_button.clicked.connect(self.export_texture)

        # レイアウトへの追加
        self.main_layout.addLayout(self.grid_layout)
        self.main_layout.addLayout(size_layout)
        self.main_layout.addWidget(self.create_ramp_button)
        self.main_layout.addWidget(self.export_button)

    def set_color(self, button):
        # カラーピッカーの起動
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")
            rgb = (color.redF(), color.greenF(), color.blueF())
            # 選択された色をランプノードに反映
            if self.ramp_node:
                index = self.buttons.index(button)  # ボタンのインデックスを取得
                cmds.setAttr(f"{self.ramp_node}.colorEntryList[{index}].color", rgb[0], rgb[1], rgb[2], type="double3")

    def create_ramp(self):
        # ランプテクスチャの作成処理
        print("Create Ramp")
        if self.ramp_node:
            cmds.delete(self.ramp_node)  # 既存のランプがある場合は削除

        self.ramp_node = cmds.shadingNode('ramp', asTexture=True, name="tempRamp")
        for i in range(25):
            cmds.setAttr(f"{self.ramp_node}.colorEntryList[{i}].position", i * (1.0 / 24.0))
            cmds.setAttr(f"{self.ramp_node}.colorEntryList[{i}].color", 0, 0, 0, type="double3")  # デフォルトで黒に設定

    def export_texture(self):
        # テクスチャのエクスポート処理
        if not self.ramp_node:
            QMessageBox.warning(self, "Error", "Ramp has not been created yet.")
            return

        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid width or height value.")
            return

        # ランプテクスチャをベイクするための処理
        file_path = cmds.fileDialog2(fileFilter="Image Files (*.png *.jpg *.tif)", dialogStyle=2, fileMode=0)
        if file_path:
            cmds.convertSolidTx(self.ramp_node, file_path[0], fileImageName=file_path[0], resolutionX=width, resolutionY=height)
            QMessageBox.information(self, "Success", f"Texture exported to {file_path[0]}")


def show_main_window():
    global ramp_texture_ui
    try:
        ramp_texture_ui.close()  # type: ignore
        ramp_texture_ui.deleteLater()  # type: ignore
    except:
        pass
    ramp_texture_ui = RampTextureToolGUI()
    ramp_texture_ui.show()
