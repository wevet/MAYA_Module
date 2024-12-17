# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
import numpy as np
from PIL import Image, ImageDraw
from shiboken2 import wrapInstance
import math
from itertools import combinations


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)



class UVEdgeExporter(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UVEdgeExporter, self).__init__(maya_main_window())

        self.setWindowTitle("UV Edge Exporter")
        self.setFixedSize(300, 300)
        self.setObjectName("UVEdgeExporterTool")


        self.image_size = 4096
        self.line_thickness = 1
        self.threshold = 0.01

        # gui
        self.width_label = None
        self.width_input = None

        self.height_label = None
        self.height_input = None

        self.thickness_slider = None
        self.thickness_label = None

        self.threshold_slider = None
        self.threshold_label = None

        self.mode_label = None
        self.edge_radio = None
        self.vertex_radio = None

        self.window = None
        self.export_image_button = None
        self.export_svg_button = None
        self.export_ai_button = None

        # GUI作成
        self.create_widgets()
        self.create_layouts()
        self.create_connections()


    def create_widgets(self):
        self.width_label = QtWidgets.QLabel("Width:")
        self.width_input = QtWidgets.QSpinBox()
        self.width_input.setRange(1, 8192)  # 最大8192ピクセル
        self.width_input.setValue(self.image_size)

        self.height_label = QtWidgets.QLabel("Height:")
        self.height_input = QtWidgets.QSpinBox()
        self.height_input.setRange(1, 8192)  # 最大8192ピクセル
        self.height_input.setValue(self.image_size)

        self.thickness_label = QtWidgets.QLabel(f"Line Thickness: {self.line_thickness}")
        self.thickness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.thickness_slider.setMinimum(1)
        self.thickness_slider.setMaximum(50)
        self.thickness_slider.setValue(self.line_thickness)

        self.threshold_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.threshold_slider.setMinimum(1)
        self.threshold_slider.setMaximum(1000)
        self.threshold_slider.setTickInterval(1)
        self.threshold_label = QtWidgets.QLabel(f"Threshold: {self.threshold_slider.value() / 1000.0}")

        self.threshold_slider.valueChanged.connect(
            lambda: self.threshold_label.setText(f"Threshold: {self.threshold_slider.value() / 1000.0}")
        )

        self.mode_label = QtWidgets.QLabel("Select Mode:")
        self.edge_radio = QtWidgets.QRadioButton("Edge")
        self.vertex_radio = QtWidgets.QRadioButton("Vertex")
        self.edge_radio.setChecked(True)  # デフォルトはエッジ
        self.export_image_button = QtWidgets.QPushButton("Export as IMAGE")
        self.export_svg_button = QtWidgets.QPushButton("Export as SVG")
        self.export_ai_button = QtWidgets.QPushButton("Export as AI")


    def create_layouts(self):
        """レイアウト設定"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.width_label)
        main_layout.addWidget(self.width_input)
        main_layout.addWidget(self.height_label)
        main_layout.addWidget(self.height_input)
        main_layout.addWidget(self.thickness_label)
        main_layout.addWidget(self.thickness_slider)
        main_layout.addWidget(self.mode_label)
        mode_layout = QtWidgets.QHBoxLayout()
        mode_layout.addWidget(self.edge_radio)
        mode_layout.addWidget(self.vertex_radio)
        main_layout.addLayout(mode_layout)
        main_layout.addWidget(self.export_image_button)
        main_layout.addWidget(self.export_svg_button)
        main_layout.addWidget(self.export_ai_button)


    def create_connections(self):
        self.thickness_slider.valueChanged.connect(self.update_line_thickness)
        self.export_image_button.clicked.connect(self.export_as_image)
        self.export_svg_button.clicked.connect(self.export_as_svg)
        self.export_ai_button.clicked.connect(self.export_as_ai)


    def update_line_thickness(self, value):
        """線の太さの更新"""
        self.line_thickness = value
        self.thickness_label.setText(f"Line Thickness: {self.line_thickness}")


    def show_message(self, title, message):
        """メッセージボックスを表示"""
        msg_box = QtWidgets.QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(QtWidgets.QMessageBox.Information)
        msg_box.exec_()


    @staticmethod
    def draw_line(image, p1, p2, thickness, color=(0, 0, 0)):
        """
        線を描画し、線の太さを考慮。

        Args:
            image (numpy.ndarray): 画像データ。
            p1 (tuple): 線の開始点 (x, y)。
            p2 (tuple): 線の終了点 (x, y)。
            thickness (int): 線の太さ。
            color (tuple): 線の色 (R, G, B)。
        """
        x0, y0 = p1
        x1, y1 = p2
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            for tx in range(-thickness // 2, thickness // 2 + 1):
                for ty in range(-thickness // 2, thickness // 2 + 1):
                    nx, ny = x0 + tx, y0 + ty
                    if 0 <= nx < image.shape[1] and 0 <= ny < image.shape[0]:
                        image[ny, nx] = color

            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy


    @staticmethod
    def draw_line_with_aa(image, p1, p2, thickness, color=(0, 0, 0)):
        """
        アンチエイリアス処理を適用して線を描画

        Args:
            image (numpy.ndarray): 画像データ。
            p1 (tuple): 線の開始点 (x, y)。
            p2 (tuple): 線の終了点 (x, y)。
            thickness (int): 線の太さ。
            color (tuple): 線の色 (R, G, B)。
        """
        x0, y0 = p1
        x1, y1 = p2

        # 線分を描画するためのDDAアルゴリズム
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))
        x_inc = dx / steps
        y_inc = dy / steps

        x, y = x0, y0
        for _ in range(int(steps) + 1):
            ix, iy = int(x), int(y)
            alpha_x = 1 - abs(x - ix)
            alpha_y = 1 - abs(y - iy)

            # 各ピクセルに色を加算
            for tx in range(-thickness // 2, thickness // 2 + 1):
                for ty in range(-thickness // 2, thickness // 2 + 1):
                    nx, ny = ix + tx, iy + ty
                    if 0 <= nx < image.shape[1] and 0 <= ny < image.shape[0]:
                        current_color = image[ny, nx]
                        blend_alpha = alpha_x * alpha_y
                        blended_color = [
                            int(current_color[i] * (1 - blend_alpha) + color[i] * blend_alpha)
                            for i in range(3)
                        ]
                        image[ny, nx] = np.clip(blended_color, 0, 255)
            x += x_inc
            y += y_inc


    # @TODO
    # tgaファイルに書き出す
    def export_as_image(self):
        """
        エッジまたは頂点を選択して画像としてエクスポート
        """
        image_width = self.width_input.value()
        image_height = self.height_input.value()
        line_thickness = self.thickness_slider.value()

        # 画像サイズが有効か確認
        if image_width <= 0 or image_height <= 0:
            cmds.warning("Invalid image size. Width and height must be greater than 0.")
            return

        image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255

        if self.edge_radio.isChecked():
            self._export_edges(image, image_width, image_height, line_thickness)
        elif self.vertex_radio.isChecked():
            self._export_vertices(image, image_width, image_height, line_thickness)

        file_path = cmds.fileDialog2(fileMode=0, caption="Save Image", fileFilter="TGA Files (*.tga)")
        if not file_path:
            return
        output_path = file_path[0]
        if not output_path.lower().endswith(".tga"):
            output_path += ".tga"
        Image.fromarray(image).save(output_path, format="TGA")
        self.show_message("Export Complete", f"Image exported to {output_path}")


    def _export_edges(self, image, image_width, image_height, line_thickness):
        """
        選択されたエッジを描画
        """
        selected_edges = cmds.ls(selection=True, flatten=True)
        if not selected_edges:
            cmds.warning("No edges selected.")
            return

        for edge in selected_edges:
            print(f"Processing Edge: {edge}")
            uv_coordinates = cmds.polyListComponentConversion(edge, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)

            # UV座標が不十分な場合はスキップ
            if not uv_list or len(uv_list) < 2:
                print(f"Edge Not Valid UV_list : {edge}")
                continue

            # UV座標を取得してユニークな座標だけを残す
            uv_positions = [cmds.polyEditUV(uv, query=True) for uv in uv_list]
            unique_uv_positions = list(dict.fromkeys([tuple(uv) for uv in uv_positions]))

            # 有効なUV座標が2つ未満の場合はスキップ
            if len(unique_uv_positions) < 2:
                print(f"Edge Not Valid unique_uv_positions : {edge}")
                continue

            # エッジに接続するフェース情報を取得
            edge_index = int(edge.split("[")[-1].split("]")[0])
            mesh_name = edge.split(".")[0]
            selection_list = om.MSelectionList()
            selection_list.add(mesh_name)

            dag_path = om.MDagPath()
            selection_list.getDagPath(0, dag_path)
            edge_itr = om.MItMeshEdge(dag_path)
            index_ptr = om.MScriptUtil().asIntPtr()
            edge_itr.setIndex(edge_index, index_ptr)

            connected_faces = om.MIntArray()
            edge_itr.getConnectedFaces(connected_faces)

            # フェースごとのUV座標を収集
            face_uv_groups = {}
            for i in range(connected_faces.length()):
                face_index = connected_faces[i]
                # フェース名を作成 (例: pCube1.f[0])
                face_name = f"{mesh_name}.f[{face_index}]"
                face_uvs = cmds.polyListComponentConversion(face_name, toUV=True)
                face_uvs = cmds.ls(face_uvs, flatten=True)
                face_uv_positions = [cmds.polyEditUV(uv, query=True) for uv in face_uvs]
                face_uv_groups[face_index] = list(dict.fromkeys([tuple(uv) for uv in face_uv_positions]))
                print(f"Add face index => {face_uv_groups[face_index]}")

            # 隣接フェースを考慮したUVペアの描画
            for i, start_uv in enumerate(unique_uv_positions):
                for j, end_uv in enumerate(unique_uv_positions):
                    # 同じ点または順序が逆の点ペアを除外
                    if i >= j:
                        continue

                    # 2つのUVが同じフェースに属するかを判定
                    shared_face = False
                    for face_index, uv_group in face_uv_groups.items():
                        if start_uv in uv_group and end_uv in uv_group:
                            shared_face = True
                            break

                    # 同じフェース内に属しているUVペアだけを描画
                    if shared_face:
                        start_pixel = (int(round(start_uv[0] * (image_width - 1))), int(round((1 - start_uv[1]) * (image_height - 1))))
                        end_pixel = (int(round(end_uv[0] * (image_width - 1))), int(round((1 - end_uv[1]) * (image_height - 1))))
                        print(f"Drawling. start_pixel: {start_pixel}, end_pixel: {end_pixel}")
                        self.draw_line_with_aa(image, start_pixel, end_pixel, thickness=line_thickness, color=(0, 0, 0))


    def _export_vertices(self, image, image_width, image_height, line_thickness):
        """
        選択された頂点を描画
        """
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("No vertices selected.")
            return

        for vertex in selected_vertices:
            uv_coordinates = cmds.polyListComponentConversion(vertex, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)
            for uv in uv_list:
                uv_pos = cmds.polyEditUV(uv, query=True)
                pixel = (int(uv_pos[0] * (image_width - 1)), int((1 - uv_pos[1]) * (image_height - 1)))
                self.draw_line(image, pixel, pixel, thickness=line_thickness, color=(0, 0, 0))


    # @TODO
    # svgファイルに書き出す
    def export_as_svg(self):
        image_width = self.width_input.value()
        image_height = self.height_input.value()
        line_thickness = self.thickness_slider.value()

        # SVG保存ダイアログを表示
        file_path = cmds.fileDialog2(fileMode=0, caption="Save SVG", fileFilter="SVG Files (*.svg)")
        if not file_path:
            return
        output_path = file_path[0]
        if not output_path.lower().endswith(".svg"):
            output_path += ".svg"

        svg_lines = []
        svg_lines.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" '
            f'width="{image_width}" height="{image_height}" '
            f'viewBox="0 0 {image_width} {image_height}">\n'
        )

        if self.edge_radio.isChecked():
            self._generate_svg_edges(svg_lines, image_width, image_height)
        elif self.vertex_radio.isChecked():
            self._generate_svg_vertices(svg_lines, image_width, image_height)
        svg_lines.append("</svg>\n")

        with open(output_path, "w") as svg_file:
            svg_file.writelines(svg_lines)

        self.show_message("Export Complete", f"SVG file exported to {output_path}")


    def _generate_svg_edges(self, svg_lines, image_width, image_height):
        """
        エッジデータをSVG形式の直線として追加
        """
        line_thickness = self.thickness_slider.value()
        selected_edges = cmds.ls(selection=True, flatten=True)
        if not selected_edges:
            cmds.warning("No edges selected.")
            return

        for edge in selected_edges:
            print(f"Processing Edge: {edge}")
            uv_coordinates = cmds.polyListComponentConversion(edge, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)

            if not uv_list or len(uv_list) < 2:
                print(f"Edge Not Valid UV_list : {edge}")
                continue

            uv_positions = [cmds.polyEditUV(uv, query=True) for uv in uv_list]
            unique_uv_positions = list(dict.fromkeys([tuple(uv) for uv in uv_positions]))

            if len(unique_uv_positions) < 2:
                print(f"Edge Not Valid unique_uv_positions : {edge}")
                continue

            # エッジに接続するフェース情報を取得
            edge_index = int(edge.split("[")[-1].split("]")[0])
            mesh_name = edge.split(".")[0]
            selection_list = om.MSelectionList()
            selection_list.add(mesh_name)
            dag_path = om.MDagPath()
            selection_list.getDagPath(0, dag_path)
            edge_itr = om.MItMeshEdge(dag_path)
            index_ptr = om.MScriptUtil().asIntPtr()
            edge_itr.setIndex(edge_index, index_ptr)
            connected_faces = om.MIntArray()
            edge_itr.getConnectedFaces(connected_faces)

            # フェースごとのUV座標を収集
            face_uv_groups = {}
            for i in range(connected_faces.length()):
                face_index = connected_faces[i]
                face_name = f"{mesh_name}.f[{face_index}]"
                face_uvs = cmds.polyListComponentConversion(face_name, toUV=True)
                face_uvs = cmds.ls(face_uvs, flatten=True)
                face_uv_positions = [cmds.polyEditUV(uv, query=True) for uv in face_uvs]
                face_uv_groups[face_index] = list(dict.fromkeys([tuple(uv) for uv in face_uv_positions]))
                print(f"Add face index => {face_uv_groups[face_index]}")

            # 隣接フェースを考慮したUVペアの描画
            for i, start_uv in enumerate(unique_uv_positions):
                for j, end_uv in enumerate(unique_uv_positions):
                    if i >= j:
                        continue

                    # 2つのUVが同じフェースに属するかを判定
                    shared_face = any(
                        start_uv in uv_group and end_uv in uv_group
                        for uv_group in face_uv_groups.values()
                    )

                    # 同じフェース内に属しているUVペアだけをSVGに追加
                    if shared_face:
                        start_pixel = (start_uv[0] * (image_width - 1), (1 - start_uv[1]) * (image_height - 1))
                        end_pixel = (end_uv[0] * (image_width - 1), (1 - end_uv[1]) * (image_height - 1))
                        print(f"Adding line to SVG. start_pixel: {start_pixel}, end_pixel: {end_pixel}")
                        line_tag = (f'<line x1="{start_pixel[0]}" y1="{start_pixel[1]}" ' f'x2="{end_pixel[0]}" y2="{end_pixel[1]}" ' f'style="stroke:black;stroke-width:{line_thickness}" />\n')
                        svg_lines.append(line_tag)


    def _generate_svg_vertices(self, svg_lines, image_width, image_height):
        """
        頂点データをSVG形式の円として追加
        """
        line_thickness = self.thickness_slider.value()
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("No vertices selected.")
            return

        for vertex in selected_vertices:
            uv_coordinates = cmds.polyListComponentConversion(vertex, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)

            for uv in uv_list:
                uv_pos = cmds.polyEditUV(uv, query=True)
                pixel_x = int(round(uv_pos[0] * (image_width - 1)))
                pixel_y = int(round((1 - uv_pos[1]) * (image_height - 1)))
                svg_lines.append(f'<circle cx="{pixel_x}" cy="{pixel_y}" r="{line_thickness / 2}" ' 'style="fill:black;" />\n')


    # @TODO
    # aiファイルに書き出す
    def export_as_ai(self):
        image_width = self.width_input.value()
        image_height = self.height_input.value()
        line_thickness = self.thickness_slider.value()

        # AI保存ダイアログを表示
        file_path = cmds.fileDialog2(fileMode=0, caption="Save AI", fileFilter="AI Files (*.ai)")
        if not file_path:
            return
        output_path = file_path[0]
        if not output_path.lower().endswith(".ai"):
            output_path += ".ai"

        ai_lines = []
        # AIファイルのヘッダー
        ai_lines.append("%!PS-Adobe-3.0 EPSF-3.0\n")
        ai_lines.append(f"%%BoundingBox: 0 0 {image_width} {image_height}\n")
        ai_lines.append(f"/w {{ setlinewidth }} def\n")  # 線の太さを設定する関数
        ai_lines.append(f"/m {{ moveto }} def\n")  # 移動コマンド
        ai_lines.append(f"/l {{ lineto }} def\n")  # 線を引くコマンド
        ai_lines.append(f"/S {{ stroke }} def\n")  # 線を描画するコマンド

        if self.edge_radio.isChecked():
            self._generate_ai_edges(ai_lines, image_width, image_height)
        elif self.vertex_radio.isChecked():
            self._generate_ai_vertices(ai_lines, image_width, image_height)

        ai_lines.append("showpage\n")

        with open(output_path, "w") as ai_file:
            ai_file.writelines(ai_lines)
        self.show_message("Export Complete", f"AI file exported to {output_path}")


    # エッジ用AI書き出し
    def _generate_ai_edges(self, ai_lines, image_width, image_height):
        """
        エッジデータをAI形式のパスとして追加
        """
        line_thickness = self.thickness_slider.value()
        selected_edges = cmds.ls(selection=True, flatten=True)
        if not selected_edges:
            cmds.warning("No edges selected.")
            return

        ai_lines.append(f'1 w\n')  # 初期線の太さを設定
        ai_lines.append(f'{line_thickness} w\n')  # 線の太さを設定

        for edge in selected_edges:
            print(f"Processing Edge: {edge}")
            uv_coordinates = cmds.polyListComponentConversion(edge, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)

            if not uv_list or len(uv_list) < 2:
                print(f"Edge Not Valid UV_list : {edge}")
                continue

            uv_positions = [cmds.polyEditUV(uv, query=True) for uv in uv_list]
            unique_uv_positions = list(dict.fromkeys([tuple(uv) for uv in uv_positions]))

            if len(unique_uv_positions) < 2:
                print(f"Edge Not Valid unique_uv_positions : {edge}")
                continue

            # エッジに接続するフェース情報を取得
            edge_index = int(edge.split("[")[-1].split("]")[0])
            mesh_name = edge.split(".")[0]
            selection_list = om.MSelectionList()
            selection_list.add(mesh_name)
            dag_path = om.MDagPath()
            selection_list.getDagPath(0, dag_path)
            edge_itr = om.MItMeshEdge(dag_path)
            index_ptr = om.MScriptUtil().asIntPtr()
            edge_itr.setIndex(edge_index, index_ptr)
            connected_faces = om.MIntArray()
            edge_itr.getConnectedFaces(connected_faces)

            # フェースごとのUV座標を収集
            face_uv_groups = {}
            for i in range(connected_faces.length()):
                face_index = connected_faces[i]
                face_name = f"{mesh_name}.f[{face_index}]"
                face_uvs = cmds.polyListComponentConversion(face_name, toUV=True)
                face_uvs = cmds.ls(face_uvs, flatten=True)
                face_uv_positions = [cmds.polyEditUV(uv, query=True) for uv in face_uvs]
                face_uv_groups[face_index] = list(dict.fromkeys([tuple(uv) for uv in face_uv_positions]))
                print(f"Add face index => {face_uv_groups[face_index]}")

            # 隣接フェースを考慮したUVペアの描画
            for i, start_uv in enumerate(unique_uv_positions):
                for j, end_uv in enumerate(unique_uv_positions):
                    if i >= j:
                        continue

                    # 2つのUVが同じフェースに属するかを判定
                    shared_face = any(
                        start_uv in uv_group and end_uv in uv_group
                        for uv_group in face_uv_groups.values()
                    )

                    # 同じフェース内に属しているUVペアだけをAIに追加
                    if shared_face:
                        start_pixel = (start_uv[0] * image_width, start_uv[1] * image_height)
                        end_pixel = (end_uv[0] * image_width, end_uv[1] * image_height)
                        print(f"Adding line to AI. start_pixel: {start_pixel}, end_pixel: {end_pixel}")
                        ai_lines.append(f'{start_pixel[0]} {start_pixel[1]} m {end_pixel[0]} {end_pixel[1]} l S\n')


    # 頂点用AI書き出し
    def _generate_ai_vertices(self, ai_lines, image_width, image_height):
        """
        頂点データをAI形式の円として追加
        """
        line_thickness = self.thickness_slider.value()
        selected_vertices = cmds.ls(selection=True, flatten=True)
        if not selected_vertices:
            cmds.warning("No vertices selected.")
            return

        radius = line_thickness / 2
        for vertex in selected_vertices:
            uv_coordinates = cmds.polyListComponentConversion(vertex, toUV=True)
            uv_list = cmds.ls(uv_coordinates, flatten=True)
            for uv in uv_list:
                uv_pos = cmds.polyEditUV(uv, query=True)
                pixel_x = uv_pos[0] * (image_width - 1)
                pixel_y = uv_pos[1] * (image_height - 1)
                ai_lines.append(f"newpath {pixel_x} {pixel_y} {radius} 0 360 arc fill\n")


def show_main_window():
    global uv_edge_exporter
    try:
        uv_edge_exporter.close()  # type: ignore
        uv_edge_exporter.deleteLater()  # type: ignore
    except:
        pass
    # Instantiate and show the tool
    uv_edge_exporter = UVEdgeExporter()
    uv_edge_exporter.show()


