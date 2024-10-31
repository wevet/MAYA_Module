# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QPushButton, QCheckBox, QSlider, QFrame, QMessageBox
from PySide2.QtCore import Qt
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance

import Intersection


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)



class Edge_Detector:
    def __init__(self):
        self.selected_object = None
        self.curves = []
        self.object_set_name = "EdgeObjectSet"
        self.mesh_group_name = "MeshGroup"
        self.droplet_group_name = "DropletGroup"
        self.line_thickness = 0.02
        self.merge_for_uv = False  # MergeしてUV展開するかのフラグ

        self.angle_threshold = 45  # 交差の角度の閾値 (°)
        self.droplet_size = 0.05  # えきだまりのサイズ
        self.voxel_size = 0.1  # ボクセルサイズ
        self.tolerance = 0.8  # Default tolerance for intersection in cm

        self.selected_meshes = []


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

        for edge in selected_edges:
            try:
                cmds.select(edge)
                curve = cmds.polyToCurve(form=2, degree=1, conformToSmoothMeshPreview=False)
                self.curves.append(curve[0])
                print(f"Curve created from edge: {curve[0]}")
            except Exception as e:
                print(f"Error converting edge {edge} to curve: {e}")
        self.group_curves()


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

        mesh_group = cmds.group(empty=True, name=self.mesh_group_name)
        generated_meshes = []

        for curve in self.curves:
            # 押し出しのプロファイルとして使用するカーブを作成（円形）
            profile_curve = cmds.circle(radius=self.line_thickness, sections=8, degree=3, name="profileCurve")[0]
            extruded_surface = cmds.extrude(profile_curve, curve, constructionHistory=True, fixedPath=True, useComponentPivot=1, useProfileNormal=False, polygon=0)[0]
            cmds.parent(extruded_surface, mesh_group)
            print(f"Extruded surface created from curve: {extruded_surface}")

            # NURBSからポリゴンへの変換
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
            cmds.polyLayoutUV(poly_mesh, layoutMethod=2)
            print(f"Clean UV layout applied for polygon mesh: {poly_mesh}")
        except Exception as e:
            cmds.warning(f"Failed to apply clean UV layout to {poly_mesh}: {e}")


    @staticmethod
    def convert_nurbs_to_poly(nurbs_surface, poly_type=1, chord_height_ratio=0.8, fit_tolerance=0.005, merge_edge_length=0.05):
        try:
            poly_mesh = cmds.nurbsToPoly(
                nurbs_surface,
                mnd=1,                      # 法線方向
                f=1,                        # サンプルベースのフォーマット
                pt=poly_type,               # ポリゴンタイプ（四角形ポリゴン）
                chr=chord_height_ratio,     # 曲率に基づく高さの許容誤差を増加
                ft=fit_tolerance,           # フィットトレランスを高め、面を簡略化
                mel=merge_edge_length,      # より長いエッジもマージして複雑さを抑える
                ut=1, vt=1                  # UとVの等間隔サンプリングで密度を抑制
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


    """
    edge 検出のメイン処理
    """
    def run_detection(self):
        self.select_object()
        self.detect_boundary_edges()
        self.edge_to_curve()
        self.convert_curve_to_mesh()


    def run_intersections(self, selected_meshes):
        intersection = Intersection.Face_Intersection()
        intersection.tolerance = self.tolerance
        intersection.angle_threshold = self.angle_threshold
        intersection.droplet_size = self.droplet_size
        intersection.voxel_size = self.voxel_size
        intersection.detect_intersections_between_faces(selected_meshes)




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

        # tolerance slider with label
        self.tolerance_label = QLabel(f'Tolerance: {self.edge_detector.tolerance} cm')
        self.tolerance_slider = QSlider(Qt.Horizontal)
        self.tolerance_slider.setRange(1, 200)
        self.tolerance_slider.setValue(int(self.edge_detector.tolerance * 10))  # Scale to match slider range
        self.tolerance_slider.valueChanged.connect(self.update_tolerance)

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

        layout.addWidget(self.tolerance_label)
        layout.addWidget(self.tolerance_slider)
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


    def update_tolerance(self, value):
        self.edge_detector.tolerance = value / 10.0  # Adjust scale if needed
        self.tolerance_label.setText(f'Tolerance: {self.edge_detector.tolerance:.1f} cm')  # Update label


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
                    valid_meshes.append(obj)
                else:
                    cmds.warning(f"{obj} is not a polygon mesh and will be ignored.")

            self.edge_detector.run_intersections(valid_meshes)

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


