# -*- coding: utf-8 -*-

import sys
from functools import partial
from PySide2.QtWidgets import QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QLabel, QHBoxLayout, QLineEdit, QMessageBox
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import Qt
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QMainWindow)


class RampTextureToolGUI(QtWidgets.QDockWidget):
    WINDOW_TITLE = "Ramp Texture Creator"
    MODULE_VERSION = "1.0"

    def __init__(self, parent=None):
        super(RampTextureToolGUI, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setObjectName("RampTextureToolGUI")
        self.setStyleSheet('background-color: #262f38; color: white;')
        self.default_style = "background-color: #34d8ed; color: black"

        # メインウィジェットの設定
        main_widget = QtWidgets.QWidget()
        self.setWidget(main_widget)  # QDockWidgetにmain_widgetをセット

        # レイアウトを作成し、main_widgetに設定
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)  # メインの余白を少しだけ追加
        grid_layout = QGridLayout()
        grid_layout.setSpacing(2)  # グリッド内のボタン間のスペースを縮小
        self.buttons = []

        self.ramp_nodes= []
        self.main_ramp_node = None

        # グリッドボタンの作成
        for i in range(5):
            for j in range(5):
                button = QPushButton(f"{i * 5 + j + 1}")
                button.setFixedSize(50, 50)  # ボタンのサイズを固定
                button.setStyleSheet("background-color: black;")
                button.clicked.connect(partial(self.set_color, button))
                grid_layout.addWidget(button, i, j)
                self.buttons.append(button)

        # サイズ入力フィールドの作成
        size_layout = QHBoxLayout()
        size_layout.setSpacing(5)  # 入力フィールド間のスペースを調整
        self.width_input = QLineEdit()
        self.width_input.setFixedSize(60, 25)
        self.width_input.setPlaceholderText("Width (default: 1024)")
        self.width_input.setText("1024")
        self.height_input = QLineEdit()
        self.height_input.setFixedSize(60, 25)
        self.height_input.setPlaceholderText("Height (default: 1024)")
        self.height_input.setText("1024")

        size_layout.addWidget(QLabel("Width:"))
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("Height:"))
        size_layout.addWidget(self.height_input)

        # ボタンの作成
        self.create_ramp_button = QPushButton("Create Ramp")
        self.create_ramp_button.setFixedHeight(30)
        self.create_ramp_button.setStyleSheet(self.default_style)
        self.create_ramp_button.clicked.connect(self.create_ramp)

        self.export_button = QPushButton("Export Texture")
        self.export_button.setFixedHeight(30)
        self.export_button.setStyleSheet(self.default_style)
        self.export_button.clicked.connect(self.export_texture)

        # レイアウトへの追加
        main_layout.addLayout(grid_layout)
        main_layout.addLayout(size_layout)
        main_layout.addWidget(self.create_ramp_button)
        main_layout.addWidget(self.export_button)


    def set_color(self, button):
        # カラーピッカーの起動
        color = QtWidgets.QColorDialog.getColor()
        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")

            rgb = (color.redF(), color.greenF(), color.blueF())
            # 選択された色を対応するランプノードに反映
            index = self.buttons.index(button)  # ボタンのインデックスを取得
            ramp_node_index = index // 5  # 横行のランプノードのインデックス
            color_entry_index = index % 5  # 縦行のエントリの位置
            # 色をランプノードの colorEntryList に設定
            cmds.setAttr(f"{self.ramp_nodes[ramp_node_index]}.colorEntryList[{color_entry_index}].color", rgb[0], rgb[1], rgb[2], type="double3")


    def create_ramp(self):
        # Hyper shadeウィンドウを開く
        cmds.HypershadeWindow()

        # 5つの横行ランプノードを作成
        ramp_nodes = []
        for i in range(5):
            ramp_node = cmds.shadingNode('ramp', asTexture=True, name=f"horizontalRamp{i + 1}")
            ramp_nodes.append(ramp_node)

            # 各横行のランプに5つの色を設定（5x5の一行分）
            for j in range(5):
                button_index = i * 5 + j
                button = self.buttons[button_index]

                # ボタンの色を取得
                color = button.palette().button().color()
                rgb = (color.redF(), color.greenF(), color.blueF())

                # 横行ランプのエントリに色を設定
                cmds.setAttr(f"{ramp_node}.colorEntryList[{j}].position", j * 0.2)  # 0.2刻み
                cmds.setAttr(f"{ramp_node}.colorEntryList[{j}].color", rgb[0], rgb[1], rgb[2], type="double3")

        # メインの縦方向ランプノードを作成し、横行ランプを接続
        main_ramp_node = cmds.shadingNode('ramp', asTexture=True, name="gridColorRampMain")

        for i, ramp_node in enumerate(ramp_nodes):
            # 縦方向の colorEntryList に横行ランプノードを接続
            cmds.connectAttr(f"{ramp_node}.outColor", f"{main_ramp_node}.colorEntryList[{i}].color")
            cmds.setAttr(f"{main_ramp_node}.colorEntryList[{i}].position", i * 0.2)  # 縦方向に配置

        # 出力シェーダーに接続（必要な場合のみ）
        if not cmds.objExists("final_output"):
            final_output = cmds.shadingNode('lambert', asShader=True, name="final_output")
        else:
            final_output = "final_output"
            existing_connections = cmds.listConnections(f"{final_output}.color", source=True, destination=False, plugs=True)
            if existing_connections:
                cmds.disconnectAttr(existing_connections[0], f"{final_output}.color")

        cmds.connectAttr(f"{main_ramp_node}.outColor", f"{final_output}.color")

        # ノードリストを保持してUIでアクセスできるようにする
        self.ramp_nodes = ramp_nodes
        self.main_ramp_node = main_ramp_node


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

    # ドッキング設定をカスタマイズ
    if cmds.workspaceControl("RampTextureToolGUIWorkspaceControl", query=True, exists=True):
        cmds.deleteUI("RampTextureToolGUIWorkspaceControl", control=True)

    # ドッキング位置を右側に設定、または浮動ウィンドウとして表示
    control_name = cmds.workspaceControl(
        "RampTextureToolGUIWorkspaceControl",
        label="Ramp Texture Tool",
        tabToControl=("AttributeEditor", -1),  # 右側にドッキング
        floating=True  # 浮動ウィンドウとして開始
    )

    # ウィジェットをMayaのworkspaceControlに接続
    workspace_control_ptr = omui.MQtUtil.findControl(control_name)
    if workspace_control_ptr:
        qt_control = wrapInstance(int(workspace_control_ptr), QtWidgets.QWidget)
        layout = qt_control.layout()
        layout.addWidget(ramp_texture_ui)

