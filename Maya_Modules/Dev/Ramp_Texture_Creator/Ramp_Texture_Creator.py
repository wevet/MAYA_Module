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

        self.ramp_nodes = []
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

        self.create_ramp_button = QPushButton("Create Ramp")
        self.create_ramp_button.setFixedHeight(30)
        self.create_ramp_button.setStyleSheet(self.default_style)
        self.create_ramp_button.clicked.connect(self.create_ramp)

        self.export_button = QPushButton("Export Texture")
        self.export_button.setFixedHeight(30)
        self.export_button.setStyleSheet(self.default_style)
        self.export_button.clicked.connect(self.export_texture)

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

            # ボタンのインデックスからランプノードとエントリのインデックスを計算
            button_index = self.buttons.index(button)
            ramp_node_index = 4 - (button_index // 5)  # 4から減少させることで縦の逆転を修正
            color_entry_index = button_index % 5  # 各ランプノード内のエントリインデックス

            # インデックスが範囲内かチェックしてから設定
            if ramp_node_index < len(self.ramp_nodes) and color_entry_index < 5:
                cmds.setAttr(f"{self.ramp_nodes[ramp_node_index]}.colorEntryList[{color_entry_index}].color", rgb[0], rgb[1], rgb[2], type="double3")
            else:
                print(f"Error: Invalid index - ramp_node_index: {ramp_node_index}, color_entry_index: {color_entry_index}")


    def create_ramp(self):
        # Hyper shadeウィンドウを開く
        cmds.HypershadeWindow()

        # 既存のノードを削除してから新しく作成
        if hasattr(self, 'ramp_nodes') and self.ramp_nodes:
            for node in self.ramp_nodes:
                if cmds.objExists(node):
                    cmds.delete(node)
            self.ramp_nodes.clear()

        if hasattr(self, 'main_ramp_node') and self.main_ramp_node:
            if cmds.objExists(self.main_ramp_node):
                cmds.delete(self.main_ramp_node)
            self.main_ramp_node = None

        # GUI順で5つの横行ランプノードを作成
        self.ramp_nodes = []  # 初期化後に新しい配列を準備

        for i in range(4, -1, -1):
            ramp_node = cmds.shadingNode('ramp', asTexture=True, name=f"horizontalRamp{i + 1}")
            self.ramp_nodes.append(ramp_node)

            # ランプの補間方法を「ノーサー」に設定してブレンドを防ぐ
            cmds.setAttr(f"{ramp_node}.interpolation", 0)  # 0: None (ノーサー)
            cmds.setAttr(f"{ramp_node}.type", 1)  # 1: Vランプに設定

            # 各横行ランプに5つの色を設定（5x5の一行分）
            for j in range(5):
                button_index = i * 5 + j  # 各行のインデックスに対応
                button = self.buttons[button_index]

                # ボタンの背景色を取得し、ランプノードに設定
                color = button.palette().button().color()
                rgb = (color.redF(), color.greenF(), color.blueF())

                # 横行ランプのエントリに色を設定
                position = j * 0.2  # 0.2刻みで均等に配置（0.0, 0.2, 0.4, 0.6, 0.8）
                cmds.setAttr(f"{ramp_node}.colorEntryList[{j}].position", position)
                cmds.setAttr(f"{ramp_node}.colorEntryList[{j}].color", rgb[0], rgb[1], rgb[2], type="double3")

        # 縦方向のメインランプノードを作成し、横行ランプを接続
        self.main_ramp_node = cmds.shadingNode('ramp', asTexture=True, name="gridColorRampMain")
        cmds.setAttr(f"{self.main_ramp_node}.interpolation", 0)  # メインランプも補間方法を「ノーサー」に設定

        # 横行ランプをメインランプの colorEntryList に正しい順番で接続
        for i, ramp_node in enumerate(self.ramp_nodes):
            # メインランプのエントリに横行ランプの出力を接続
            cmds.connectAttr(f"{ramp_node}.outColor", f"{self.main_ramp_node}.colorEntryList[{i}].color", force=True)
            cmds.setAttr(f"{self.main_ramp_node}.colorEntryList[{i}].position", i * 0.2)  # 縦方向のポジション設定

        # 出力シェーダーに接続（必要な場合のみ）
        if not cmds.objExists("final_output"):
            final_output = cmds.shadingNode('lambert', asShader=True, name="final_output")
        else:
            final_output = "final_output"
            existing_connections = cmds.listConnections(f"{final_output}.color", source=True, destination=False, plugs=True)
            if existing_connections:
                cmds.disconnectAttr(existing_connections[0], f"{final_output}.color")

        cmds.connectAttr(f"{self.main_ramp_node}.outColor", f"{final_output}.color")


    def export_texture(self):
        # エクスポート用のテクスチャが生成されているか確認
        if not self.main_ramp_node or not cmds.objExists(self.main_ramp_node):
            QMessageBox.warning(self, "Error", "Ramp has not been created or is invalid.")
            return

        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid width or height value.")
            return

        print(f"Main Ramp Node: {self.main_ramp_node}")
        print(cmds.nodeType(self.main_ramp_node))  # これでノードのタイプを確認

        # 保存先ファイルパスの取得
        file_path = cmds.fileDialog2(fileFilter="Image Files (*.png *.jpg *.tif)", dialogStyle=2, fileMode=0)
        if not file_path:
            QMessageBox.warning(self, "Error", "No file path selected.")
            return

        # パスを正しく処理
        output_path = file_path[0].replace("\\", "/")
        print(f"Exporting to: {output_path}")

        # 仮のジオメトリ（例えば平面）を作成または選択してベイクを行う
        bake_geometry = "pPlane1"

        if not cmds.objExists(bake_geometry):
            bake_geometry = cmds.polyPlane(name="pPlane1", width=1, height=1, subdivisionsX=1, subdivisionsY=1)[0]

        # ベイク処理
        try:
            cmds.convertSolidTx(f"{self.main_ramp_node}.outColor", bake_geometry,
                                backgroundColor=[0, 0, 0],
                                fileFormat="tif", fileImageName=output_path,
                                resolutionX=width, resolutionY=height)
            QMessageBox.information(self, "Success", f"Texture exported to {output_path}")

            cmds.delete(bake_geometry)
        except Exception as e:
            print(f"Failed to export texture: {e}")




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

