# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QLabel
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
from functools import partial


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QMainWindow)


class CustomVertexColorGUI(QtWidgets.QDockWidget):

    WINDOW_TITLE = "Vertex Color Tool"
    MODULE_VERSION = "1.1"

    def __init__(self, parent=maya_main_window()):
        super(CustomVertexColorGUI, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setObjectName("CustomVertexColorGUI")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.setStyleSheet('background-color: #262f38; color: white;')

        # color cache
        self.cache_vertex_colors = {}

        # メインウィジェットを設定
        main_widget = QtWidgets.QWidget()
        self.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)

        # メッシュ名表示ラベル
        self.mesh_label = QLabel("選択中のメッシュ: なし")
        self.mesh_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.mesh_label)

        # 現在の頂点カラーの表示ラベル
        self.current_color_label = QLabel("現在の頂点カラー: R=0.0, G=0.0, B=0.0")
        self.current_color_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.current_color_label)

        # 頂点カラー表示切り替えチェックボックス
        self.display_vertex_color_checkbox = QCheckBox("頂点カラーを表示")
        self.display_vertex_color_checkbox.stateChanged.connect(self.toggle_vertex_color_display)

        # RGBのボタンを配置するグリッドレイアウト
        grid_layout = QGridLayout()
        self.buttons = {}
        for i, color in enumerate(['R', 'G', 'B']):
            for j, value in enumerate([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]):
                btn = QPushButton(f"{value:.1f}")
                btn.clicked.connect(partial(self.set_and_apply_vertex_color, color, value))
                btn.setStyleSheet(f"background-color: {self.get_color_style(color, value)}; color: black;")
                self.buttons[(color, value)] = btn

                grid_layout.addWidget(btn, i, j)
        main_layout.addLayout(grid_layout)

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


        main_layout.addWidget(self.display_vertex_color_checkbox)
        main_layout.addWidget(self.r_checkbox)
        main_layout.addWidget(self.g_checkbox)
        main_layout.addWidget(self.b_checkbox)

        # 初期状態でチャンネルの表示を制御
        #self.update_vertex_color_display()
        self.update_mesh_info()


    def set_temp_vertex_color(self, channel, value):
        """一時的に頂点カラーを設定し、GUI上に表示"""
        setattr(self, f"{channel.lower()}_value", value)
        self.update_current_color_label()


    @staticmethod
    def get_color_style(channel, value):
        """指定されたチャンネルと値に基づいてボタンの色を設定する"""
        if channel == 'R':
            return f"rgb({int(value * 255)}, 0, 0)"
        elif channel == 'G':
            return f"rgb(0, {int(value * 255)}, 0)"
        elif channel == 'B':
            return f"rgb(0, 0, {int(value * 255)})"


    def set_and_apply_vertex_color(self, channel, value):
        """一時的に頂点カラーを設定し、即座に選択頂点に適用"""
        # チャンネルごとに一時的にカラーを保存
        setattr(self, f"{channel.lower()}_value", value)
        self.update_current_color_label()

        # 頂点カラーを即座に適用
        self.apply_vertex_color()
        pass


    def toggle_channel(self, channel, state):
        # チャンネルの表示/非表示を切り替え
        print(f"{channel} チャンネルの表示を切り替えました: {state}")
        self.update_vertex_color_display(channel, state)


    @staticmethod
    def clamp(value, min_value=0.0, max_value=1.0):
        """valueをmin_valueとmax_valueの間に制限"""
        return max(min(value, max_value), min_value)


    @staticmethod
    def get_vertex_colors_with_poly_color_per_vertex(mesh):
        vertex_colors = {}
        num_vertices = cmds.polyEvaluate(mesh, vertex=True)

        for i in range(num_vertices):
            color = cmds.polyColorPerVertex(f"{mesh}.vtx[{i}]", query=True, rgb=True)
            if color:
                vertex_colors[i] = color
            else:
                vertex_colors[i] = [1.0, 1.0, 1.0]  # デフォルトカラー
        return vertex_colors


    def apply_vertex_color(self):
        """選択した頂点の指定チャンネルのみを更新し、表示切り替えも同時に行う"""
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("頂点を選択してください")
            return

        self.update_mesh_info()

        # メッシュと頂点情報を確認
        mesh = selected_vertices[0].split(".")[0]
        cmds.setAttr(mesh + ".displayColors", 1)

        # メッシュの頂点にカラーを設定
        mesh_selection_list = om.MSelectionList()
        mesh_selection_list.add(mesh)
        dag_path = mesh_selection_list.getDagPath(0)
        mesh_function = om.MFnMesh(dag_path)

        r = getattr(self, 'r_value', 1.0)
        g = getattr(self, 'g_value', 1.0)
        b = getattr(self, 'b_value', 1.0)

        if not hasattr(self, 'cache_vertex_colors'):
            self.cache_vertex_colors = self.get_vertex_colors_with_poly_color_per_vertex(mesh)


        # チェックボックスの状態を確認して、非表示チャンネルは見た目のみ0
        for vertex in selected_vertices:
            vtx_id = int(vertex.split(".vtx[")[-1][:-1])
            current_color = self.cache_vertex_colors.get(vtx_id, [1.0, 1.0, 1.0])

            # 表示上のRGB値を決定
            new_r = r if r is not None else current_color[0]
            new_g = g if g is not None else current_color[1]
            new_b = b if b is not None else current_color[2]

            # 表示制御（見た目だけ0にする）
            display_r = new_r if self.r_checkbox.isChecked() else 0.0
            display_g = new_g if self.g_checkbox.isChecked() else 0.0
            display_b = new_b if self.b_checkbox.isChecked() else 0.0

            # 数値設定は常に行うが、表示はチェックボックスによって制御
            display_color = om.MColor((display_r, display_g, display_b, 1.0))

            # 新しいカラーを頂点に設定し、キャッシュも更新
            mesh_function.setVertexColor(display_color, vtx_id)
            self.cache_vertex_colors[vtx_id] = [new_r, new_g, new_b]

        #self.cache_vertex_colors = self.get_vertex_colors_with_poly_color_per_vertex(mesh)

        cmds.refresh()


    def update_vertex_color_display(self, channel, state):
        """チェックボックスの状態に基づいて、選択中の頂点の頂点カラーの表示のみを切り替える"""

        # 選択中の頂点リストを取得
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("頂点が選択されていません")
            return

        # メッシュと頂点情報を取得
        mesh = selected_vertices[0].split(".")[0]
        if not cmds.objExists(mesh):
            cmds.warning(f"メッシュ {mesh} が存在しません")
            return

        if not hasattr(self, 'cache_vertex_colors'):
            self.cache_vertex_colors = self.get_vertex_colors_with_poly_color_per_vertex(mesh)

        vertex_colors = self.cache_vertex_colors
        display_colors = []

        # 選択中の頂点に対してのみ、指定チャンネルの表示/非表示を反映
        for vertex in selected_vertices:
            try:
                vtx_id = int(vertex.split(".vtx[")[-1][:-1])  # 頂点インデックスを抽出

                # キャッシュしたカラーから現在のRGB値を取得
                current_color = vertex_colors.get(vtx_id, [1.0, 1.0, 1.0])
                r, g, b = current_color
                # チェックボックスの状態に応じて、各チャンネルを可視化のみ制御
                r_display = r if self.r_checkbox.isChecked() else 0.0
                g_display = g if self.g_checkbox.isChecked() else 0.0
                b_display = b if self.b_checkbox.isChecked() else 0.0
                a = 1.0  # アルファ値は固定
                # 最終的な表示カラーを作成
                display_color = om.MColor((r_display, g_display, b_display, a))

                display_colors.append((vtx_id, display_color))

            except (ValueError, IndexError):
                cmds.warning(f"無効な頂点の選択: {vertex}")

        # メッシュの頂点にアクセス
        mesh_selection_list = om.MSelectionList()
        mesh_selection_list.add(mesh)
        dag_path = mesh_selection_list.getDagPath(0)
        mesh_function = om.MFnMesh(dag_path)

        for vtx_id, color in display_colors:
            mesh_function.setVertexColor(color, vtx_id)

        cmds.refresh()


    def toggle_vertex_color_display(self, state):
        """頂点カラーの表示切り替え"""
        selected_vertices = cmds.ls(selection=True, dag=True, type='mesh')
        if not selected_vertices:
            cmds.warning("メッシュを選択してください")
            return

        mesh = selected_vertices[0]
        if state == 2:  # チェックされている場合
            cmds.setAttr(mesh + ".displayColors", 1)
        else:
            cmds.setAttr(mesh + ".displayColors", 0)
        print(f"{mesh} のdisplayColorsの表示を切り替えました: {state}")


    def update_mesh_info(self):
        """選択中のメッシュと頂点情報をGUIに表示"""
        # 選択中の頂点リストを取得
        selected_vertices = cmds.ls(selection=True, flatten=True)

        if selected_vertices:
            # メッシュ名を取得（最初の頂点からメッシュ名を抽出）
            mesh_name = selected_vertices[0].split(".")[0]
            self.mesh_label.setText(f"選択中のメッシュ: {mesh_name}")
        else:
            # 選択がない場合
            self.mesh_label.setText("選択中のメッシュ: なし")
        # 現在のカラー情報を更新
        self.update_current_color_label()


    def update_current_color_label(self):
        """現在設定している頂点カラーのRGBをラベルに反映"""
        r = getattr(self, 'r_value', 0.0)
        g = getattr(self, 'g_value', 0.0)
        b = getattr(self, 'b_value', 0.0)
        self.current_color_label.setText(f"現在の頂点カラー: R={r}, G={g}, B={b}")



"""
ドッキング可能なguiを生成
"""
def show_main_window():
    global custom_vertex_color_gui
    try:
        custom_vertex_color_gui.close()  # type: ignore
        custom_vertex_color_gui.deleteLater()  # type: ignore
    except:
        pass
    custom_vertex_color_gui = CustomVertexColorGUI()

    # ドッキング設定をカスタマイズ
    if cmds.workspaceControl("CustomVertexColorGUIWorkspaceControl", query=True, exists=True):
        cmds.deleteUI("CustomVertexColorGUIWorkspaceControl", control=True)

    # ドッキング位置を右側に設定、または浮動ウィンドウとして表示
    control_name = cmds.workspaceControl(
        "CustomVertexColorGUIWorkspaceControl",
        label="Vertex Color Tool",
        tabToControl=("AttributeEditor", -1),  # 右側にドッキング
        floating=True  # 浮動ウィンドウとして開始
    )

    # ウィジェットをMayaのworkspaceControlに接続
    workspace_control_ptr = omui.MQtUtil.findControl(control_name)
    if workspace_control_ptr:
        qt_control = wrapInstance(int(workspace_control_ptr), QtWidgets.QWidget)
        layout = qt_control.layout()
        layout.addWidget(custom_vertex_color_gui)


