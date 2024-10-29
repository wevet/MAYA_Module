# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QPushButton, QCheckBox, QSlider, QFrame, QMessageBox
from PySide2.QtCore import Qt
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
import math



def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)



class Edge_Detector:
    def __init__(self):
        self.selected_object = None
        self.curves = []
        self.layer_name = "EdgeLayer"
        self.object_set_name = "EdgeObjectSet"
        self.line_thickness = 0.02
        self.merge_for_uv = False  # MergeしてUV展開するかのフラグ

        self.angle_threshold = 45  # 交差の角度の閾値 (°)
        self.droplet_size = 0.2  # えきだまりのサイズ
        self.voxel_size = 0.1  # ボクセルサイズ

        self.selected_meshes = []
        self.intersections = []


    def select_object(self):
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.error("Please select a mesh object.")
            return
        self.selected_object = selected_objects[0]
        print(f"Selected object: {self.selected_object}")


    def detect_boundary_edges(self):
        if not self.selected_object:
            cmds.error("No object selected.")
            return

        shape_node = cmds.listRelatives(self.selected_object, shapes=True)[0]
        boundary_edges = cmds.polyListComponentConversion(shape_node, toEdge=True, border=True)

        if boundary_edges:
            cmds.select(boundary_edges, add=True)
            print(f"Boundary edges detected and selected: {boundary_edges}")
        else:
            print("No boundary edges found.")


    def edge_to_curve(self):
        selected_edges = cmds.filterExpand(sm=32)
        if not selected_edges:
            cmds.error("Please select edges.")
            return

        self.create_display_layer()

        for edge in selected_edges:
            try:
                cmds.select(edge)
                curve = cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=False)
                self.curves.append(curve[0])
                print(f"Curve created from edge: {curve[0]}")
                cmds.editDisplayLayerMembers(self.layer_name, curve[0])
            except Exception as e:
                print(f"Error converting edge {edge} to curve: {e}")

        self.group_curves()


    def create_display_layer(self):
        if not cmds.objExists(self.layer_name):
            cmds.createDisplayLayer(name=self.layer_name, empty=True)
            print(f"Display layer '{self.layer_name}' created.")
        else:
            print(f"Display layer '{self.layer_name}' already exists.")


    def group_curves(self):
        # Group作成または既存グループへの追加
        if not cmds.objExists(self.object_set_name):
            cmds.group(self.curves, name=self.object_set_name)
            print(f"Curves grouped under '{self.object_set_name}'.")
        else:
            cmds.group(self.curves, self.object_set_name)
            print(f"Curves added to existing group '{self.object_set_name}'.")


    def convert_curve_to_mesh(self):
        if not self.curves:
            cmds.error("No curves available for NURBS surface creation.")
            return

        mesh_group = cmds.group(empty=True, name="MeshGroup")
        generated_meshes = []

        for curve in self.curves:
            # 押し出しのプロファイルとして使用するカーブを作成（円形）
            profile_curve = cmds.circle(radius=self.line_thickness, sections=8, degree=3, name="profileCurve")[0]
            extruded_surface = cmds.extrude(profile_curve, curve, constructionHistory=True, fixedPath=True, useComponentPivot=1, useProfileNormal=False, polygon=0)[0]
            cmds.parent(extruded_surface, mesh_group)
            print(f"Extruded surface created from curve: {extruded_surface}")

            poly_mesh = self.convert_nurbs_to_poly(extruded_surface)
            if poly_mesh:
                self.apply_uv_projection(poly_mesh)
                cmds.parent(poly_mesh, mesh_group)
                generated_meshes.append(poly_mesh)

            # プロファイルカーブと押し出しサーフェスを削除
            cmds.delete(profile_curve)
            cmds.delete(extruded_surface)


        # MergeしてからUV展開するか、個別にUV展開するか
        if self.merge_for_uv and len(generated_meshes) > 1:
            # メッシュをマージしてUV展開
            merged_mesh = cmds.polyUnite(generated_meshes, name="MergedMesh", constructionHistory=False)[0]
            self.apply_clean_uv_layout(merged_mesh)
            cmds.delete(merged_mesh, ch=True)
            cmds.parent(merged_mesh, mesh_group)
            return [merged_mesh]  # 交差検出用に返す
        else:
            # 個別にUV展開
            for mesh in generated_meshes:
                self.apply_clean_uv_layout(mesh)
            return generated_meshes


    @staticmethod
    def apply_clean_uv_layout(poly_mesh):
        """
        綺麗なUVレイアウトを適用するメソッド。
        polyLayoutUVを使用してUVを整理し、均等なスケールと回転を維持
        """
        try:
            cmds.polyLayoutUV(
                poly_mesh,
                layout=2,  # 一般的なレイアウト
                rotateForBestFit=True,
                spacing=0.002,  # UV間の間隔を調整
                worldSpace=True
            )
            print(f"Clean UV layout applied for polygon mesh: {poly_mesh}")
        except Exception as e:
            cmds.warning(f"Failed to apply clean UV layout to {poly_mesh}: {e}")


    @staticmethod
    def convert_nurbs_to_poly(nurbs_surface, poly_type=1, chord_height_ratio=0.9, fit_tolerance=0.01, merge_edge_length=0.001):
        try:
            poly_mesh = cmds.nurbsToPoly(
                nurbs_surface,
                mnd=1,
                f=1,
                pt=poly_type,
                chr=chord_height_ratio,
                ft=fit_tolerance,
                mel=merge_edge_length
            )[0]

            print(f"Polygon mesh created: {poly_mesh}")
            cmds.polyAutoProjection(poly_mesh, layoutMethod=2, insertBeforeDeformers=True, scaleMode=1)
            print(f"UVs projected for {poly_mesh}")
            return poly_mesh
        except Exception as e:
            cmds.warning(f"Failed to convert NURBS surface {nurbs_surface} to polygon: {e}")
            return None


    @staticmethod
    def apply_uv_projection(poly_mesh):
        try:
            cmds.polyAutoProjection(poly_mesh, layoutMethod=2, insertBeforeDeformers=True, scaleMode=1)
            print(f"UVs applied for polygon mesh: {poly_mesh}")
        except Exception as e:
            cmds.warning(f"Failed to apply UV projection to {poly_mesh}: {e}")


    def apply_clean_uv_layout(self, poly_mesh):
        try:
            cmds.polyLayoutUV(poly_mesh, scaleMode=1, layout=2, rotateForBestFit=True, spacing=0.002, worldSpace=True)
            print(f"Clean UV layout applied for polygon mesh: {poly_mesh}")
        except Exception as e:
            cmds.warning(f"Failed to apply clean UV layout to {poly_mesh}: {e}")


    def run_intersection(self):

        self.selected_meshes = cmds.ls(selection=True, type='transform')
        if not self.selected_meshes or len(self.selected_meshes) < 1:
            cmds.error("Please select at least one mesh.")
            return

        for mesh in self.selected_meshes:
            print(f"Detecting intersections for {mesh}...")
            self.detect_self_intersections(mesh)
        pass


    def run_intersections_array(self, selected_meshes):
        self.selected_meshes = selected_meshes
        for mesh in self.selected_meshes:
            print(f"Detecting intersections for {mesh}...")
            self.detect_self_intersections(mesh)
        pass


    def detect_self_intersections(self, mesh):
        # メッシュ内のエッジを取得
        edges = cmds.polyListComponentConversion(mesh, toEdge=True)
        cmds.select(edges)
        edge_list = cmds.ls(selection=True, fl=True)

        # エッジ座標をボクセルにマッピング
        edge_voxels = {}
        for edge in edge_list:
            edge_center = self.get_edge_center(edge)
            voxel_key = self.get_voxel_key(edge_center)

            if voxel_key not in edge_voxels:
                edge_voxels[voxel_key] = []
            edge_voxels[voxel_key].append(edge)

        # 同じボクセル内のエッジ間で交差判定
        for voxel_key, edges_in_voxel in edge_voxels.items():
            if len(edges_in_voxel) > 1:
                for i, edge1 in enumerate(edges_in_voxel):
                    for edge2 in edges_in_voxel[i + 1:]:
                        if self.is_intersecting(edge1, edge2):
                            angle = self.calculate_angle_between(edge1, edge2)
                            droplet_mesh = self.create_droplet_by_intersection_type(angle)
                            if droplet_mesh:
                                intersection_position = self.get_edge_center(edge1)  # 交差位置に配置
                                cmds.move(intersection_position[0], intersection_position[1], intersection_position[2], droplet_mesh)
                                self.intersections.append((edge1, edge2, droplet_mesh))
                                print(f"Intersection detected between {edge1} and {edge2} with angle {angle}° - {droplet_mesh} added.")

        if not self.intersections:
            print(f"No intersections found in {mesh}.")
        else:
            print(f"{len(self.intersections)} intersections found in {mesh}.")


    @staticmethod
    def get_edge_center(edge):
        # エッジの中央座標を計算
        edge_points = cmds.pointPosition(edge, world=True)
        center = [(edge_points[0][i] + edge_points[1][i]) / 2 for i in range(3)]
        return center


    def get_voxel_key(self, position):
        # ボクセルキー（x, y, z のボクセル位置）を計算
        return tuple(int(pos // self.voxel_size) for pos in position)


    def calculate_angle_between(self, edge1, edge2):
        # エッジの方向ベクトルを取得して角度を計算
        edge1_dir = self.get_edge_direction(edge1)
        edge2_dir = self.get_edge_direction(edge2)
        dot_product = sum(a * b for a, b in zip(edge1_dir, edge2_dir))
        magnitude1 = math.sqrt(sum(a ** 2 for a in edge1_dir))
        magnitude2 = math.sqrt(sum(b ** 2 for b in edge2_dir))

        angle_radians = math.acos(dot_product / (magnitude1 * magnitude2))
        return math.degrees(angle_radians)


    @staticmethod
    def get_edge_direction(edge):
        # エッジの方向ベクトルを計算
        edge_points = cmds.pointPosition(edge, world=True)
        direction = [edge_points[1][i] - edge_points[0][i] for i in range(3)]
        magnitude = math.sqrt(sum(d ** 2 for d in direction))
        return [d / magnitude for d in direction]


    def is_intersecting(self, edge1, edge2):
        # エッジの交差判定 (距離で判定)
        pos1 = cmds.pointPosition(edge1, world=True)
        pos2 = cmds.pointPosition(edge2, world=True)
        distance = self.calculate_distance(pos1, pos2)
        return distance < self.voxel_size / 2  # ボクセルサイズに依存する閾値


    def calculate_distance(self, pos1, pos2):
        # 2つのエッジの距離を計算
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))


    def create_droplet_by_intersection_type(self, angle):
        # 角度に基づいて交差の種類を判定し、えきだまりメッシュを作成
        if self.is_cross_intersection(angle):
            return cmds.polySphere(radius=self.droplet_size, name="Droplet_Circle")[0]
        elif self.is_t_intersection(angle):
            return \
            cmds.polyCube(width=self.droplet_size, height=self.droplet_size, depth=self.droplet_size, name="Droplet_T")[
                0]
        elif self.is_diagonal_intersection(angle):
            return cmds.polyCylinder(radius=self.droplet_size, height=0.05, name="Droplet_Ellipse")[0]
        return None


    def is_cross_intersection(self, angle):
        # 十字交差判定
        return abs(angle - 90) < self.angle_threshold


    def is_t_intersection(self, angle):
        # T字交差判定
        return abs(angle - 90) < self.angle_threshold / 2


    def is_diagonal_intersection(self, angle):
        # 斜め交差の判定
        return abs(angle - 45) < self.angle_threshold


    def run_detection(self):
        self.select_object()
        self.detect_boundary_edges()
        self.edge_to_curve()
        self.convert_curve_to_mesh()



class EdgeDetectorGUI(QtWidgets.QDialog):

    WINDOW_TITLE = "Edge Detector Tool"
    MODULE_VERSION = "1.0"

    def __init__(self, parent=None):
        super(EdgeDetectorGUI, self).__init__(maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet('background-color: #262f38; color: white;')
        self.resize(300, 260)

        self.edge_detector = Edge_Detector()
        self.line_thickness_input = QLineEdit(self)
        self.line_thickness_input.setText('0.02')

        # Edge function
        self.convert_button = QPushButton('Create Edge')
        self.convert_button.clicked.connect(self.run_edge_detection)
        self.convert_button.setStyleSheet("background-color: #34d8ed; color: black;")

        # Angle Threshold slider and label
        self.angle_threshold_label = QLabel(
            f'Angle Threshold for Intersection (°): {self.edge_detector.angle_threshold}')
        self.angle_threshold_slider = QSlider(Qt.Horizontal)
        self.angle_threshold_slider.setRange(0, 90)
        self.angle_threshold_slider.setValue(self.edge_detector.angle_threshold)
        self.angle_threshold_slider.valueChanged.connect(self.update_angle_threshold)

        # Droplet Size slider and label
        self.droplet_size_label = QLabel(f'Droplet Size: {self.edge_detector.droplet_size}')
        self.droplet_size_slider = QSlider(Qt.Horizontal)
        self.droplet_size_slider.setRange(1, 100)
        self.droplet_size_slider.setValue(int(self.edge_detector.droplet_size * 100))
        self.droplet_size_slider.valueChanged.connect(self.update_droplet_size)

        # Intersection detection button
        self.intersection_button = QPushButton('Check Intersection')
        self.intersection_button.clicked.connect(self.check_intersection)
        self.intersection_button.setStyleSheet("background-color: #ff8080; color: black;")

        # Merge UV checkbox
        self.merge_uv_checkbox = QCheckBox("Merge before UV Layout")
        self.merge_uv_checkbox.setChecked(False)
        self.merge_uv_checkbox.stateChanged.connect(self.toggle_merge_uv)

        # Separators
        separator_line_1 = QFrame(parent=None)
        separator_line_1.setFrameShape(QFrame.HLine)
        separator_line_1.setFrameShadow(QFrame.Sunken)
        separator_line_2 = QFrame(parent=None)
        separator_line_2.setFrameShape(QFrame.HLine)
        separator_line_2.setFrameShadow(QFrame.Sunken)

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Line Thickness:'))
        layout.addWidget(self.line_thickness_input)
        layout.addWidget(self.convert_button)
        layout.addWidget(separator_line_1)

        layout.addWidget(self.angle_threshold_label)
        layout.addWidget(self.angle_threshold_slider)
        layout.addWidget(self.droplet_size_label)
        layout.addWidget(self.droplet_size_slider)
        layout.addWidget(self.intersection_button)
        layout.addWidget(separator_line_2)
        layout.addWidget(self.merge_uv_checkbox)

        self.setLayout(layout)


    def update_angle_threshold(self, value):
        self.edge_detector.angle_threshold = value
        self.angle_threshold_label.setText(f'Angle Threshold for Intersection (°): {value}')  # 現在の値を更新


    def update_droplet_size(self, value):
        droplet_size = value / 100.0
        self.edge_detector.droplet_size = droplet_size
        self.droplet_size_label.setText(f'Droplet Size: {droplet_size}')  # 現在の値を更新


    def toggle_merge_uv(self, state):
        self.edge_detector.merge_for_uv = bool(state)


    def run_edge_detection(self):
        try:
            line_thickness = float(self.line_thickness_input.text() or "0.02")
            self.edge_detector.line_thickness = line_thickness
            self.edge_detector.run_detection()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for line thickness.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")


    def check_intersection(self):
        try:
            # 選択内容がポリゴンメッシュかを確認
            selected_objects = cmds.ls(selection=True, type='transform')
            valid_meshes = []

            for obj in selected_objects:
                shapes = cmds.listRelatives(obj, shapes=True)
                if shapes and cmds.nodeType(shapes[0]) == "mesh":  # ポリゴンメッシュのみをリストに追加
                    # 確実にポリゴンメッシュとして処理されるように、ヒストリーを削除
                    poly_mesh = cmds.polyUnite(obj, constructionHistory=False, mergeUVSets=True)[0]
                    cmds.delete(poly_mesh, ch=True)  # ヒストリー削除で確定
                    valid_meshes.append(obj)
                else:
                    cmds.warning(f"{obj} is not a polygon mesh and will be ignored.")

            self.edge_detector.run_intersections_array(valid_meshes)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred during intersection check: {str(e)}")



def show_main_window():
    global edge_detector_gui
    try:
        edge_detector_gui.close()  # type: ignore
        edge_detector_gui.deleteLater()  # type: ignore
    except:
        pass
    edge_detector_gui = EdgeDetectorGUI()
    edge_detector_gui.show()


