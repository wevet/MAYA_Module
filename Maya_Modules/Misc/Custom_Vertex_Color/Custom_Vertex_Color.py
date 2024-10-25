# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QLabel
from PySide2.QtCore import Qt
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)


class CustomVertexColorGUI(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(CustomVertexColorGUI, self).__init__(parent)
        self.setWindowTitle("Vertex Color Tool")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # RGBのボタンを配置するグリッドレイアウト
        grid_layout = QGridLayout()
        self.buttons = {}
        for i, color in enumerate(['R', 'G', 'B']):
            for j, value in enumerate([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]):
                btn = QPushButton(f"{value:.1f}")
                btn.clicked.connect(lambda _, c=color, v=value: self.set_vertex_color(c, v))
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
        self.r_checkbox.stateChanged.connect(lambda: self.toggle_channel('R'))
        self.g_checkbox.stateChanged.connect(lambda: self.toggle_channel('G'))
        self.b_checkbox.stateChanged.connect(lambda: self.toggle_channel('B'))

        layout.addWidget(self.r_checkbox)
        layout.addWidget(self.g_checkbox)
        layout.addWidget(self.b_checkbox)


    def set_vertex_color(self, channel, value):
        # 選択されたオブジェクトを取得
        selection = cmds.ls(selection=True, dag=True, type='mesh')
        if not selection:
            cmds.warning("メッシュを選択してください")
            return

        mesh = selection[0]

        # メッシュの頂点を取得
        msel = om.MSelectionList()
        msel.add(mesh)
        dagPath = msel.getDagPath(0)
        meshFn = om.MFnMesh(dagPath)

        # 現在のカラーを取得し、選択されたチャンネルの値を変更
        vertex_count = meshFn.numVertices
        colors = meshFn.getVertexColors()
        for i in range(vertex_count):
            color = colors[i]
            if channel == 'R':
                color.r = value
            elif channel == 'G':
                color.g = value
            elif channel == 'B':
                color.b = value
            colors[i] = color

        meshFn.setVertexColors(colors, list(range(vertex_count)))
        cmds.refresh()

    def toggle_channel(self, channel):
        # チャンネルの表示/非表示を切り替え
        print(f"{channel} チャンネルの表示を切り替えました")



def show_main_window():
    global custom_vertex_color_gui
    try:
        custom_vertex_color_gui.close()  # type: ignore
        custom_vertex_color_gui.deleteLater()  # type: ignore
    except:
        pass
    custom_vertex_color_gui = CustomVertexColorGUI()
    custom_vertex_color_gui.show()




