# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QLabel
from PySide2.QtCore import Qt
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
from functools import partial


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)


class CustomVertexColorGUI(QtWidgets.QDialog):

    def __init__(self, parent=maya_main_window()):
        super(CustomVertexColorGUI, self).__init__(parent)
        self.setWindowTitle("Vertex Color Tool")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet('background-color: #262f38; color: white;')
        self.setFixedSize(400, 150)  # ウィンドウの固定サイズを設定

        layout = QVBoxLayout()
        self.setLayout(layout)

        # RGBのボタンを配置するグリッドレイアウト
        grid_layout = QGridLayout()
        self.buttons = {}
        for i, color in enumerate(['R', 'G', 'B']):
            for j, value in enumerate([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]):
                btn = QPushButton(f"{value:.1f}")
                # partialを使用して引数を固定
                btn.clicked.connect(partial(self.set_vertex_color, color, value))
                btn.setStyleSheet(f"background-color: {self.get_color_style(color, value)}; color: black;")
                self.buttons[(color, value)] = btn

                grid_layout.addWidget(btn, i, j)
        layout.addLayout(grid_layout)

        # R, G, Bの表示切り替えチェックボックス
        self.r_checkbox = QCheckBox("Rを表示")
        self.g_checkbox = QCheckBox("Gを表示")
        self.b_checkbox = QCheckBox("Bを表示")
        self.r_checkbox.setChecked(True)
        self.g_checkbox.setChecked(True)
        self.b_checkbox.setChecked(True)
        self.r_checkbox.stateChanged.connect(partial(self.toggle_channel, 'R'))
        self.g_checkbox.stateChanged.connect(partial(self.toggle_channel, 'G'))
        self.b_checkbox.stateChanged.connect(partial(self.toggle_channel, 'B'))

        layout.addWidget(self.r_checkbox)
        layout.addWidget(self.g_checkbox)
        layout.addWidget(self.b_checkbox)

        self.update_vertex_color_display()


    @staticmethod
    def get_color_style(channel, value):
        """指定されたチャンネルと値に基づいてボタンの色を設定する"""
        if channel == 'R':
            return f"rgb({int(value * 255)}, 0, 0)"
        elif channel == 'G':
            return f"rgb(0, {int(value * 255)}, 0)"
        elif channel == 'B':
            return f"rgb(0, 0, {int(value * 255)})"


    @staticmethod
    def set_vertex_color(channel, value):
        # 選択されたオブジェクトを取得
        selection = cmds.ls(selection=True, dag=True, type='mesh')
        if not selection:
            cmds.warning("メッシュを選択してください")
            return

        mesh = selection[0]
        cmds.setAttr(mesh + ".displayColors", 1)

        # メッシュの頂点を取得
        mesh_selection_list = om.MSelectionList()
        mesh_selection_list.add(mesh)
        dag_path = mesh_selection_list.getDagPath(0)
        mesh_function = om.MFnMesh(dag_path)

        # 頂点ごとのカラー情報を設定
        vertex_count = mesh_function.numVertices
        vertex_ids = list(range(vertex_count))
        try:
            colors = mesh_function.getVertexColors()
            print(f"Retrieved colors: {colors}")
        except RuntimeError:
            # 頂点カラーが設定されていない場合、初期化する
            print("頂点カラーが設定されていないので初期化します。")
            colors = [om.MColor((1.0, 1.0, 1.0, 1.0))] * vertex_count

        for i in range(vertex_count):
            color = colors[i]
            if channel == 'R':
                color.r = value
            elif channel == 'G':
                color.g = value
            elif channel == 'B':
                color.b = value
            colors[i] = color

        # 頂点カラーを設定
        mesh_function.setVertexColors(colors, vertex_ids)
        cmds.refresh()

        print("vertex_color => {}, vertex_ids => {}".format(colors, vertex_ids))


    def toggle_channel(self, channel, state):
        # チャンネルの表示/非表示を切り替え
        print(f"{channel} チャンネルの表示を切り替えました: {state}")
        self.update_vertex_color_display()


    def update_vertex_color_display(self):
        """チェックボックスの状態に基づいて頂点カラーの表示を切り替える"""
        show_r = self.r_checkbox.isChecked()
        show_g = self.g_checkbox.isChecked()
        show_b = self.b_checkbox.isChecked()

        # Mayaの設定で、頂点カラー表示の切り替え
        selection = cmds.ls(selection=True, dag=True, type='mesh')
        if not selection:
            cmds.warning("メッシュを選択してください")
            return

        mesh = selection[0]
        cmds.setAttr(mesh + ".displayColors", 1)

        # 現在の頂点カラーを取得し、表示するチャンネルのみ強調表示
        mesh_selection_list = om.MSelectionList()
        mesh_selection_list.add(mesh)
        dag_path = mesh_selection_list.getDagPath(0)
        mesh_function = om.MFnMesh(dag_path)
        vertex_count = mesh_function.numVertices
        vertex_ids = list(range(vertex_count))

        try:
            colors = mesh_function.getVertexColors()
        except RuntimeError:
            colors = [om.MColor((1.0, 1.0, 1.0, 1.0))] * vertex_count

        for i in range(vertex_count):
            color = colors[i]
            if not show_r:
                color.r = 0.0
            if not show_g:
                color.g = 0.0
            if not show_b:
                color.b = 0.0
            colors[i] = color

        mesh_function.setVertexColors(colors, vertex_ids)
        cmds.refresh()



def show_main_window():
    global custom_vertex_color_gui
    try:
        custom_vertex_color_gui.close()  # type: ignore
        custom_vertex_color_gui.deleteLater()  # type: ignore
    except:
        pass
    custom_vertex_color_gui = CustomVertexColorGUI()
    custom_vertex_color_gui.show()
