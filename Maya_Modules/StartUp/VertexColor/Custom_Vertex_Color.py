# -*- coding: utf-8 -*-

import sys
from PySide2.QtWidgets import QVBoxLayout, QGridLayout, QPushButton, QCheckBox, QLabel
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.api.OpenMaya as om
from functools import partial
import pymel.core as pm
from maya import mel


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QMainWindow)


class CustomVertexColorGUI(QtWidgets.QDockWidget):
    WINDOW_TITLE = "Vertex Color Tool"
    MODULE_VERSION = "1.6"

    def __init__(self, parent=maya_main_window()):
        super(CustomVertexColorGUI, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setObjectName("CustomVertexColorGUI")
        self.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)

        self.setStyleSheet('background-color: #262f38; color: white;')

        # color cache
        self.cache_vertex_colors = None


        # メインウィジェットを設定
        main_widget = QtWidgets.QWidget()
        self.setWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_widget.setLayout(main_layout)

        self.is_always_check_zero = True
        self.initialized_vertex_color = False
        self.r_value = 0.0
        self.g_value = 0.0
        self.b_value = 0.0

        # メッシュ名表示ラベル
        self.mesh_label = QLabel("Selected Mesh: None")
        self.mesh_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.mesh_label)

        # 現在の頂点カラーの表示ラベル
        self.current_color_label = QLabel("Current Vertex Color: R=0.0, G=0.0, B=0.0")
        self.current_color_label.setStyleSheet("color: white;")
        main_layout.addWidget(self.current_color_label)

        # 頂点カラー表示切り替えチェックボックス
        self.display_vertex_color_checkbox = QCheckBox("Show Vertex Color")
        self.display_vertex_color_checkbox.stateChanged.connect(self.toggle_vertex_color_display)

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
        self.r_checkbox = QCheckBox("Show R Channel")
        self.g_checkbox = QCheckBox("Show G Channel")
        self.b_checkbox = QCheckBox("Show B Channel")
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

        if self.is_always_check_zero is True:
            # 他のチャンネルは0にリセットし、指定したチャンネルのみにvalueを適用
            if channel == 'R':
                self.r_value, self.g_value, self.b_value = value, 0.0, 0.0
            elif channel == 'G':
                self.r_value, self.g_value, self.b_value = 0.0, value, 0.0
            elif channel == 'B':
                self.r_value, self.g_value, self.b_value = 0.0, 0.0, value
        else:
            # チャンネルごとに一時的にカラーを保存
            setattr(self, f"{channel.lower()}_value", value)

        self.update_current_color_label()
        self.apply_vertex_color(channel, value)


    def toggle_channel(self, channel, state):
        # チャンネルの表示/非表示を切り替え
        #print(f"{channel} チャンネルの表示を切り替えました: {state}")
        self.update_vertex_color_display(channel, state)


    @staticmethod
    def get_vertex_colors_with_poly_color_per_vertex(mesh):
        """各頂点のカラーを取得し、キャッシュする"""
        # メッシュが存在するか確認
        if not cmds.objExists(mesh):
            cmds.warning(f"メッシュ {mesh} が存在しません")
            return {}

        vertex_colors = {}
        num_vertices = cmds.polyEvaluate(mesh, vertex=True)
        for i in range(num_vertices):
            try:
                color = cmds.polyColorPerVertex(f"{mesh}.vtx[{i}]", query=True, rgb=True)
                if color is not None:
                    vertex_colors[i] = color
                else:
                    cmds.warning(f"{mesh}.vtx[{i}] の頂点カラーがありません。")
                    pass

            except RuntimeError:
                cmds.warning(f"{mesh}.vtx[{i}] の頂点カラー情報が取得できませんでした")
        return vertex_colors



    """
    初回のみdictionaryを作成し、頂点カラーをcopyする
    """
    def initialize_vertex_cache(self, mesh):
        """メッシュ全体の頂点カラーをキャッシュ"""
        if self.cache_vertex_colors is None:
            self.cache_vertex_colors = {}

        # キャッシュが既に存在している場合は再生成しない
        if mesh not in self.cache_vertex_colors:
            vertex_colors = self.get_vertex_colors_with_poly_color_per_vertex(mesh)
            # 初期化時には全ての頂点を「面ではなく頂点で塗られた」としてキャッシュに保存
            self.cache_vertex_colors[mesh] = { vtx_id: {"color": color, "is_face": False} for vtx_id, color in vertex_colors.items() }
            print(f"initialized => {self.cache_vertex_colors[mesh]}")
        else:
            print(f"Existing cache is being used.: {mesh}")


    """
    頂点カラーが編集できない場合はできるように変更する
    cached_vertex_colorの更新も行う
    頂点カラーの編集時、channelMask適用時、vertex color表示時のいずれかで呼び出される
    """
    def _apply_paint_vertex_color_frag(self, mesh):
        # 初回チェック: 頂点カラーが設定されていなければ黒で初期化
        try:
            vertex_colors = cmds.polyColorPerVertex(f"{mesh}.vtx[0]", query=True, rgb=True)
            if vertex_colors is not None:
                cmds.polyOptions(mesh, colorShadedDisplay=True)
                cmds.setAttr(mesh + ".displayColors", 1)

                if self.cache_vertex_colors is None or self.initialized_vertex_color is False:
                    self.initialized_vertex_color = True
                    self.initialize_vertex_cache(mesh)
                    print(f"initialize vertex map => {mesh}")
                else:
                    print(f"already have vertex_colors => {mesh}")
            else:
                # ここは呼び出されないはず
                print("not have vertex_colors")

        except RuntimeError:
            # 頂点カラーがない場合、黒で初期化
            cmds.polyColorPerVertex(mesh, rgb=(0, 0, 0), colorDisplayOption=True)
            cmds.setAttr(mesh + ".displayColors", 1)
            print(f"vertex_colorsがNoneの為、{mesh} に初回の頂点カラー（黒）が設定されました。")
            self.initialized_vertex_color = True
            self.cache_vertex_colors = None
            self.initialize_vertex_cache(mesh)
        self.update_mesh_info(mesh)


    """
    指定チャンネルのみを更新し、チェックボックスオフのチャンネルは表示上0にしつつ他のチャンネルは保持
    """
    def apply_vertex_color(self, channel, value):
        print("apply_vertex_color")

        selected_components = cmds.ls(selection=True, flatten=True)
        if not selected_components:
            cmds.warning("頂点を選択してください")
            return

        # メッシュと頂点情報を確認
        mesh = self._get_obtain_object_with_shape()
        if not mesh:
            print(f"{mesh} has no mesh")
            return

        self._apply_paint_vertex_color_frag(mesh)
        self._global_vertex_color_display(2)
        self.display_vertex_color_checkbox.setChecked(True)

        # 頂点選択時の処理
        for component in selected_components:
            if ".vtx[" in component:
                vertices_to_paint = [component]
                for vertex in vertices_to_paint:
                    try:
                        # 既存の頂点カラーを取得（存在しない場合はデフォルトカラーを設定）
                        existing_color = cmds.polyColorPerVertex(vertex, query=True, rgb=True)
                        if existing_color is None:
                            cmds.warning(f"{vertex} の頂点カラーを取得できなかったため、スキップします")
                            continue

                        # 頂点IDの抽出
                        vtx_id = int(vertex.split(".vtx[")[-1][:-1])
                        cache_data = self.cache_vertex_colors[mesh].get(
                            vtx_id, {"color": existing_color, "is_face": False}
                        )
                        vertex_color = cache_data["color"]

                        r_value = value if channel == "R" else vertex_color[0]
                        g_value = value if channel == "G" else vertex_color[1]
                        b_value = value if channel == "B" else vertex_color[2]

                        # チェックボックスの状態に応じて表示上の値をマスク（0に設定）
                        display_r = r_value if self.r_checkbox.isChecked() else 0.0
                        display_g = g_value if self.g_checkbox.isChecked() else 0.0
                        display_b = b_value if self.b_checkbox.isChecked() else 0.0

                        # MELコマンドを生成して実行
                        mel_command = f"polyColorPerVertex -r {display_r} -g {display_g} -b {display_b} {vertex};"
                        mel.eval(mel_command)

                        # 更新した情報をキャッシュに格納
                        self.cache_vertex_colors[mesh][vtx_id] = {
                            "color": [r_value, g_value, b_value],
                            "is_face": False
                        }

                    except (ValueError, IndexError):
                        cmds.warning(f"無効な頂点の選択: {vertex}")

        # 面選択時の処理
        for component in selected_components:
            if ".f[" in component:
                face_id = int(component.split(".f[")[-1][:-1])
                vertices_to_paint = cmds.polyListComponentConversion(component, toVertex=True)
                vertices_to_paint = cmds.ls(vertices_to_paint, flatten=True)
                for vertex in vertices_to_paint:
                    try:
                        # 既存の頂点カラーを取得（存在しない場合はデフォルトカラーを設定）
                        existing_color = cmds.polyColorPerVertex(vertex, query=True, rgb=True)
                        if existing_color is None:
                            cmds.warning(f"{vertex} の頂点カラーを取得できなかったため、スキップします")
                            continue

                        cache_data = self.cache_vertex_colors[mesh].get(
                            face_id, {"color": existing_color, "is_face": True}
                        )
                        vertex_color = cache_data["color"]

                        r_value = value if channel == "R" else vertex_color[0]
                        g_value = value if channel == "G" else vertex_color[1]
                        b_value = value if channel == "B" else vertex_color[2]

                        # チェックボックスの状態に応じて表示上の値をマスク（0に設定）
                        display_r = r_value if self.r_checkbox.isChecked() else 0.0
                        display_g = g_value if self.g_checkbox.isChecked() else 0.0
                        display_b = b_value if self.b_checkbox.isChecked() else 0.0

                        # MELコマンドを生成して実行（面ごとの塗りに対して全体適用）
                        face_name = f"{mesh}.f[{face_id}]"
                        mel_command = f"polyColorPerVertex -r {display_r} -g {display_g} -b {display_b} {face_name};"
                        mel.eval(mel_command)

                        # 更新した情報をキャッシュに格納
                        self.cache_vertex_colors[mesh][face_id] = {
                            "color": [r_value, g_value, b_value],
                            "is_face": True
                        }

                        print(f"write face => {face_id}")

                    except (ValueError, IndexError):
                        cmds.warning(f"無効な頂点の選択: {vertex}")
        cmds.refresh()


    """
    チェックボックスの状態に基づいて、選択中の頂点の頂点カラーの表示のみを切り替える
    """
    def update_vertex_color_display(self, channel, state):
        print("update_vertex_color_display")

        # メッシュと頂点情報を確認
        mesh = self._get_obtain_object_with_shape()
        if not mesh:
            print(f"{mesh} has no mesh")
            return

        self._apply_paint_vertex_color_frag(mesh)
        self._global_vertex_color_display(2)
        self.display_vertex_color_checkbox.setChecked(True)
        vertex_colors = self.cache_vertex_colors[mesh]

        # メッシュの頂点にアクセス
        mesh_selection_list = om.MSelectionList()
        mesh_selection_list.add(mesh)
        dag_path = mesh_selection_list.getDagPath(0)
        mesh_function = om.MFnMesh(dag_path)
        num_vertices = mesh_function.numVertices

        # 全頂点に対してキャッシュのチェックを行い、表示データを準備
        for vtx_id in range(num_vertices):
            if vtx_id in vertex_colors:
                cache_data = vertex_colors[vtx_id]
                current_color = cache_data["color"]
                is_face_painted = cache_data["is_face"]

                if not is_face_painted:
                    r_display = current_color[0] if self.r_checkbox.isChecked() else 0.0
                    g_display = current_color[1] if self.g_checkbox.isChecked() else 0.0
                    b_display = current_color[2] if self.b_checkbox.isChecked() else 0.0
                    # 頂点で塗られた箇所の色表示（グラデーションあり）
                    display_color = om.MColor((r_display, g_display, b_display, 1.0))
                    mesh_function.setVertexColor(display_color, vtx_id)


        # 面に対する処理
        all_faces = cmds.polyEvaluate(mesh, face=True)
        for face_id in range(all_faces):
            if face_id in vertex_colors:
                cache_data = vertex_colors[face_id]
                current_color = cache_data["color"]
                is_face_painted = cache_data["is_face"]

                if is_face_painted:
                    r_display = current_color[0] if self.r_checkbox.isChecked() else 0.0
                    g_display = current_color[1] if self.g_checkbox.isChecked() else 0.0
                    b_display = current_color[2] if self.b_checkbox.isChecked() else 0.0
                    face_name = f"{mesh}.f[{face_id}]"
                    print(f"face id => {face_id}")
                    mel_command = f"polyColorPerVertex -r {r_display} -g {g_display} -b {b_display} {face_name};"
                    mel.eval(mel_command)
        cmds.refresh()


    @staticmethod
    def _global_vertex_color_display(state):
        # シーン全体で頂点カラーの表示を切り替える
        if state == 2:
            mel.eval("polyOptions -global -drc 1 -dgc 1 -dbc 1 -dal 0;")  # RGBをオン、アルファをオフ
        else:
            mel.eval("polyOptions -global -drc 0 -dgc 0 -dbc 0 -dal 0;")  # RGBとアルファをオフ


    def toggle_vertex_color_display(self, state):
        """頂点カラーの表示をシーン全体で切り替える"""
        self._global_vertex_color_display(state)

        # メッシュと頂点情報を確認
        mesh = self._get_obtain_object_with_shape()
        if not mesh:
            print(f"{mesh} has no mesh")
            return

        if state == 2:
            self._apply_paint_vertex_color_frag(mesh)
        else:
            cmds.polyOptions(mesh, colorShadedDisplay=False)
            cmds.setAttr(mesh + ".displayColors", 0)


    @staticmethod
    def _get_obtain_object_with_shape():
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("頂点またはフェースを選択してください")
            return

        # メッシュのトランスフォーム名を取得
        if ".vtx[" in selected_vertices[0]:
            transform = selected_vertices[0].split(".vtx[")[0]
        elif ".f[" in selected_vertices[0]:
            transform = selected_vertices[0].split(".f[")[0]
        else:
            cmds.warning("頂点またはフェースを選択してください")
            return

        # トランスフォームからシェイプを取得
        shape = cmds.listRelatives(transform, shapes=True, fullPath=True)
        if shape:
            mesh_shape = shape[0]
            print(f"Acquired shape name: {mesh_shape}")
            return transform
        else:
            cmds.warning("Selected object has no shape")
            return None


    def update_mesh_info(self, mesh):
        """選択中のメッシュと頂点情報をGUIに表示"""
        # メッシュ名を取得（最初の頂点からメッシュ名を抽出）
        mesh_name = mesh.split(".")[0]
        self.mesh_label.setText(f"Selected Mesh: {mesh_name}")
        self.update_current_color_label()


    def update_current_color_label(self):
        """現在設定している頂点カラーのRGBをラベルに反映"""
        r, g, b = self._get_current_color()
        self.current_color_label.setText(f"Current Vertex Color: R={r}, G={g}, B={b}")


    def _get_current_color(self):
        r = getattr(self, 'r_value', 0.0)
        g = getattr(self, 'g_value', 0.0)
        b = getattr(self, 'b_value', 0.0)
        return r, g, b



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


