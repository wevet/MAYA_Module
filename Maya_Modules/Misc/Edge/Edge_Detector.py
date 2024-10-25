# -*- coding: utf-8 -*-

import sys
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QPushButton, QMessageBox
from PySide2.QtCore import Qt
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance



def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)


class Edge_Detector:
    def __init__(self):
        self.selected_object = None
        self.curves = []
        self.layer_name = "CurvesLayer"
        self.group_name = "CurvesGroup"
        self.line_thickness = 0.02

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
        if not self.curves:
            print("No curves to group.")
            return

        if not cmds.objExists(self.group_name):
            cmds.group(self.curves, name=self.group_name)
            print(f"Curves grouped under '{self.group_name}'.")
        else:
            cmds.parent(self.curves, self.group_name)
            print(f"Curves added to existing group '{self.group_name}'.")


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

            # プロファイルカーブを削除
            cmds.delete(profile_curve)
            cmds.delete(extruded_surface)

        return generated_meshes


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


    def detect_intersections(self):
        # 生成されたメッシュを取得
        generated_meshes = self.convert_curve_to_mesh()
        if not generated_meshes:
            cmds.error("No meshes generated for intersection detection.")
            return

        for i, mesh1 in enumerate(generated_meshes):
            for j, mesh2 in enumerate(generated_meshes):
                if i >= j:
                    continue  # 同じメッシュ同士またはすでにチェック済みのペアはスキップ

                # メッシュ同士の交差判定を行う
                intersection = cmds.polyBoolOp(mesh1, mesh2, operation=3, constructionHistory=False, name=f"Intersection_{i}_{j}")
                if cmds.objExists(intersection):
                    print(f"Intersection detected between {mesh1} and {mesh2}: {intersection}")
                    cmds.delete(intersection)  # 交差メッシュは一時的なものなので削除
                else:
                    print(f"No intersection detected between {mesh1} and {mesh2}")

    def run_detection(self):
        self.select_object()
        self.detect_boundary_edges()
        self.edge_to_curve()
        self.detect_intersections()


class EdgeDetectorGUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(EdgeDetectorGUI, self).__init__(maya_main_window())
        self.setWindowTitle("Edge Detector GUI")
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet('background-color: #262f38; color: white;')
        self.resize(300, 150)

        self.edge_detector = Edge_Detector()
        self.line_thickness_input = QLineEdit(self)
        self.line_thickness_input.setText('0.02')

        self.convert_button = QPushButton('Run Edge Detection')
        self.convert_button.clicked.connect(self.run_edge_detection)
        self.convert_button.setStyleSheet("background-color: #34d8ed; color: black;")

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Line Thickness:'))
        layout.addWidget(self.line_thickness_input)
        layout.addWidget(self.convert_button)

        self.setLayout(layout)

    def run_edge_detection(self):
        try:
            line_thickness = float(self.line_thickness_input.text())
            self.edge_detector.line_thickness = line_thickness
            self.edge_detector.run_detection()
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter a valid number for line thickness.")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")



def show_main_window():
    global edge_detector_gui
    try:
        edge_detector_gui.close()  # type: ignore
        edge_detector_gui.deleteLater()  # type: ignore
    except:
        pass
    edge_detector_gui = EdgeDetectorGUI()
    edge_detector_gui.show()
