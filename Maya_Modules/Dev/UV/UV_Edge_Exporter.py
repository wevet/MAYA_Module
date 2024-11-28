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
        self.setFixedSize(300, 250)
        self.setObjectName("UVEdgeExporterTool")


        self.image_size = 2048
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

        self.window = None
        self.export_image_button = None
        self.export_svg_button = None
        self.export_json_button = None

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

        self.export_image_button = QtWidgets.QPushButton("Export as PNG")
        self.export_svg_button = QtWidgets.QPushButton("Export as SVG")
        self.export_json_button = QtWidgets.QPushButton("Export as JSON")


    def create_layouts(self):
        """レイアウト設定"""
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.width_label)
        main_layout.addWidget(self.width_input)
        main_layout.addWidget(self.height_label)
        main_layout.addWidget(self.height_input)
        main_layout.addWidget(self.thickness_label)
        main_layout.addWidget(self.thickness_slider)
        main_layout.addWidget(self.threshold_label)
        main_layout.addWidget(self.threshold_slider)
        main_layout.addWidget(self.export_image_button)
        #main_layout.addWidget(self.export_svg_button)
        #main_layout.addWidget(self.export_json_button)


    def create_connections(self):
        self.thickness_slider.valueChanged.connect(self.update_line_thickness)
        self.export_image_button.clicked.connect(self.export_as_edge_image)
        #self.export_svg_button.clicked.connect(self.export_as_svg)
        #self.export_json_button.clicked.connect(self.export_as_json)


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
    def calculate_distance(uv1, uv2):
        """UV座標間の距離を計算"""
        return math.sqrt((uv1[0] - uv2[0]) ** 2 + (uv1[1] - uv2[1]) ** 2)


    # @TODO
    # wip
    def export_as_edge_image(self):
        # 画像の幅と高さを取得
        image_width = self.width_input.value()
        image_height = self.height_input.value()
        line_thickness = self.thickness_slider.value()

        # 入力された画像サイズが有効かチェック
        if image_width <= 0 or image_height <= 0:
            cmds.warning("Invalid image size. Width and height must be greater than 0.")
            return

        # 選択されたエッジを取得
        selected_edges = cmds.ls(selection=True, flatten=True)
        if not selected_edges:
            cmds.warning("No edges selected.")
            return

        # 白い背景画像を作成
        image = np.ones((image_height, image_width, 3), dtype=np.uint8) * 255

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

            # エッジ情報からメッシュ名とエッジインデックスを抽出
            # エッジインデックスを取得
            edge_index = int(edge.split("[")[-1].split("]")[0])
            mesh_name = edge.split(".")[0]
            selection_list = om.MSelectionList()
            selection_list.add(mesh_name)

            # Maya APIを使用してエッジの情報を取得
            dag_path = om.MDagPath()
            selection_list.getDagPath(0, dag_path)
            edge_itr = om.MItMeshEdge(dag_path)
            index_ptr = om.MScriptUtil().asIntPtr()
            edge_itr.setIndex(edge_index, index_ptr)

            # エッジに接続するフェースを取得
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
                        start_pixel = (
                            int(round(start_uv[0] * (image_width - 1))),
                            int(round((1 - start_uv[1]) * (image_height - 1)))
                        )
                        end_pixel = (
                            int(round(end_uv[0] * (image_width - 1))),
                            int(round((1 - end_uv[1]) * (image_height - 1)))
                        )
                        self.draw_line(image, start_pixel, end_pixel, thickness=line_thickness, color=(0, 0, 0))

        # 画像を保存するためのダイアログを表示
        file_path = cmds.fileDialog2(fileMode=0, caption="Save UV Image", fileFilter="PNG Files (*.png)")
        if not file_path:
            return

        # 保存先パスを取得し、PNG形式で保存
        output_path = file_path[0]
        if not output_path.lower().endswith(".png"):
            output_path += ".png"
        Image.fromarray(image).save(output_path)

        # 完了メッセージを表示
        self.show_message("Export Complete", f"UV edges exported to {output_path}")


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
    def get_uv_set_name(mesh_fn):
        uv_set_names = []
        mesh_fn.getUVSetNames(uv_set_names)
        if uv_set_names:
            return uv_set_names[0]
        return None


    @staticmethod
    def get_uv_data_with_open_maya():
        """OpenMayaを使って選択したエッジのUVデータを取得"""
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)

        uv_data = []

        print(f"selection length => {selection.length()}")

        for i in range(selection.length()):
            dag_path = om.MDagPath()
            component = om.MObject()
            selection.getDagPath(i, dag_path, component)

            if component.apiType() == om.MFn.kMeshEdgeComponent:
                mesh_fn = om.MFnMesh(dag_path)
                uv_set_name = UVEdgeExporter.get_uv_set_name(mesh_fn)
                if not uv_set_name:
                    print("No UV set found on the mesh.")
                    continue

                print(f"found uv set name => {uv_set_name}")
                edge_itr = om.MItMeshEdge(dag_path, component)

                while not edge_itr.isDone():
                    edge_uvs = []
                    vertex1 = edge_itr.index(0)
                    vertex2 = edge_itr.index(1)

                    u1_ptr = om.MScriptUtil()
                    u1_ptr.createFromDouble(0.0)
                    u1 = u1_ptr.asFloatPtr()

                    v1_ptr = om.MScriptUtil()
                    v1_ptr.createFromDouble(0.0)
                    v1 = v1_ptr.asFloatPtr()

                    u2_ptr = om.MScriptUtil()
                    u2_ptr.createFromDouble(0.0)
                    u2 = u2_ptr.asFloatPtr()

                    v2_ptr = om.MScriptUtil()
                    v2_ptr.createFromDouble(0.0)
                    v2 = v2_ptr.asFloatPtr()

                    try:
                        # 頂点に関連付けられたUVを取得
                        mesh_fn.getUV(vertex1, u1, v1, uv_set_name)
                        mesh_fn.getUV(vertex2, u2, v2, uv_set_name)

                        edge_uvs.append((om.MScriptUtil.getFloat(u1), om.MScriptUtil.getFloat(v1)))
                        edge_uvs.append((om.MScriptUtil.getFloat(u2), om.MScriptUtil.getFloat(v2)))
                        print(
                            f"Edge {edge_itr.index()}: UV1 ({om.MScriptUtil.getFloat(u1)}, {om.MScriptUtil.getFloat(v1)}), "
                            f"UV2 ({om.MScriptUtil.getFloat(u2)}, {om.MScriptUtil.getFloat(v2)})")

                    except RuntimeError as e:
                        print(f"Error retrieving UVs for edge {edge_itr.index()}: {e}")

                    if edge_uvs:
                        uv_data.append(edge_uvs)
                    else:
                        print(f"No UVs found for edge {edge_itr.index()}")
                    edge_itr.next()

        return uv_data


    def export_as_svg(self):
        uv_data = self.get_uv_data()
        if not uv_data:
            return

        image_width = self.width_input.value()
        image_height = self.height_input.value()
        line_thickness = self.thickness_slider.value()

        file_path = cmds.fileDialog2(fileMode=0, caption="Save SVG", fileFilter="SVG Files (*.svg)")
        if not file_path:
            return

        output_path = file_path[0]
        if not output_path.lower().endswith(".svg"):
            output_path += ".svg"

        with open(output_path, "w") as f:
            f.write('<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n')
            for edge in uv_data:
                for i in range(len(edge) - 1):
                    start = (edge[i][0] * image_width, (1 - edge[i][1]) * image_height)
                    end = (edge[i + 1][0] * image_width, (1 - edge[i + 1][1]) * image_height)
                    f.write(f'<line x1="{start[0]}" y1="{start[1]}" x2="{end[0]}" y2="{end[1]}" '
                            f'style="stroke:black;stroke-width:{line_thickness}" />\n')
            f.write("</svg>")

        self.show_message("Export Complete", f"UV edges exported to {output_path}")


    def export_as_json(self):
        uv_data = self.get_uv_data()
        if not uv_data:
            return

        file_path = cmds.fileDialog2(fileMode=0, caption="Save JSON", fileFilter="JSON Files (*.json)")
        if not file_path:
            return

        output_path = file_path[0]
        if not output_path.lower().endswith(".json"):
            output_path += ".json"

        line_thickness = self.thickness_slider.value()
        image_width = self.width_input.value()
        image_height = self.height_input.value()

        json_data = {
            "image_width": image_width,
            "image_height": image_height,
            "line_thickness": line_thickness,
            "uv_edges": [
                {
                    "start": {"u": edge[i][0], "v": edge[i][1]},
                    "end": {"u": edge[i + 1][0], "v": edge[i + 1][1]}
                }
                for edge in uv_data
                for i in range(len(edge) - 1)
            ]
        }

        import json
        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=4)

        self.show_message("Export Complete", f"UV edges exported to {output_path}")


    @staticmethod
    def get_uv_data():
        selected_edges = cmds.ls(selection=True, flatten=True)
        if not selected_edges:
            cmds.warning("No edges selected.")
            return []

        uv_data = []
        for edge in selected_edges:
            uv_coords = cmds.polyListComponentConversion(edge, toUV=True)
            uv_list = cmds.ls(uv_coords, flatten=True)
            if not uv_list or len(uv_list) < 2:
                continue

            uv_positions = [cmds.polyEditUV(uv, query=True) for uv in uv_list]
            unique_uv_positions = list(dict.fromkeys([tuple(uv) for uv in uv_positions]))
            uv_data.append(unique_uv_positions)

        return uv_data


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


