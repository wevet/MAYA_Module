# -*- coding: utf-8 -*-

import sys
import json
from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QFileDialog, QColorDialog, QMessageBox, QSlider
from PySide2.QtCore import Qt
from PIL import Image, ImageDraw
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from math import factorial
import math


info = cmds.about(version=True)
version = int(info.split(" ")[0])


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QDialog)



class Texture_Exporter(QtWidgets.QDialog):

    WINDOW_TITLE = "Texture Exporter"
    MODULE_VERSION = "1.0"
    MARGIN = 400
    INTERSECTION_TOLERANCE = 10  # 交点の範囲
    PIXEL_SEARCH_RANGE = 10

    def __init__(self, parent=None, *args, **kwargs):
        super(Texture_Exporter, self).__init__(maya_main_window())
        self.width_label = None
        self.width_input = None

        self.height_label = None
        self.height_input = None

        self.line_thickness_label = None
        self.line_thickness_input = None

        self.curve_color_label = None
        self.curve_color_button = None
        self.curve_color_input = None

        self.selected_color = (0, 0, 0)

        self.num_samples_slider = None
        self.num_samples_label = None
        self.num_samples = 20  # デフォルト値

        self.mask_check = None

        self.generate_button = None

        self._create_ui()

    def _create_ui(self):
        self.default_style = "background-color: #34d8ed; color: black"
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet('background-color:#262f38;')
        self.resize(320, 320)

        self.width_label = QLabel('Width:')
        self.height_label = QLabel('Height:')
        self.line_thickness_label = QLabel('Line Thickness:')
        self.curve_color_label = QLabel('Curve Color:')
        self.num_samples_label = QLabel(f'Sample Points: {self.num_samples}')

        self.width_input = QLineEdit(self)
        self.height_input = QLineEdit(self)
        self.line_thickness_input = QLineEdit(self)

        self.num_samples = 20

        # default value
        self.width_input.setText('4096')
        self.height_input.setText('4096')
        self.line_thickness_input.setText('10')

        self.curve_color_input = QLineEdit(self)
        self.curve_color_input.setReadOnly(True)
        self.curve_color_input.setText(str(self.selected_color))

        self.curve_color_button = QtWidgets.QPushButton('Select Curve Color')
        self.curve_color_button.clicked.connect(self._choose_color)
        self.curve_color_button.setStyleSheet(self.default_style)

        self.mask_check = QtWidgets.QCheckBox('Enable Mask (Alpha 0)', self)
        self.mask_check.setChecked(True)

        self.num_samples_slider = QSlider(Qt.Horizontal)
        self.num_samples_slider.setMinimum(5)
        self.num_samples_slider.setMaximum(100)
        self.num_samples_slider.setValue(self.num_samples)
        self.num_samples_slider.setTickInterval(5)
        self.num_samples_slider.setTickPosition(QSlider.TicksBelow)
        self.num_samples_slider.valueChanged.connect(self._update_num_samples_label)

        self.generate_button = QtWidgets.QPushButton('Export')
        self.generate_button.clicked.connect(self.export_curve_to_png)
        self.generate_button.setStyleSheet(self.default_style)

        separator_line_1 = QtWidgets.QFrame(parent=None)
        separator_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)

        # レイアウト設定
        layout = QVBoxLayout()
        layout.addWidget(self.width_label)
        layout.addWidget(self.width_input)
        layout.addWidget(self.height_label)
        layout.addWidget(self.height_input)
        layout.addWidget(self.line_thickness_label)
        layout.addWidget(self.line_thickness_input)
        layout.addWidget(self.curve_color_label)
        layout.addWidget(self.curve_color_input)
        layout.addWidget(self.curve_color_button)
        layout.addWidget(self.num_samples_label)
        layout.addWidget(self.num_samples_slider)
        layout.addWidget(self.mask_check)
        layout.addWidget(separator_line_1)
        layout.addWidget(self.generate_button)
        self.setLayout(layout)


    def _choose_color(self):
        # QColorDialog を使って色を選択
        color = QColorDialog.getColor()

        if color.isValid():
            # 色をRGBタプルに変換
            self.selected_color = color.getRgb()[:3]
            #self.curve_color_button.setStyleSheet(f'background-color: {color.name()}; color: white')
            self.curve_color_input.setText(str(self.selected_color))

    def _update_num_samples_label(self):
        # スライダーの値を取得し、ラベルとサンプル数を更新
        self.num_samples = self.num_samples_slider.value()
        self.num_samples_label.setText(f'Sample Points: {self.num_samples}')

    @staticmethod
    def _draw_grid(draw, width, height, grid_size, grid_divisions=24):
        # 1セルあたりの幅と高さを計算
        cell_width = width / grid_size
        cell_height = height / grid_size

        # 縦線を描画
        for i in range(grid_size + 1):  # +1 で境界を含める
            x = int(i * cell_width)
            draw.line([(x, 0), (x, height)], fill=(200, 200, 200), width=1)

        # 横線を描画
        for i in range(grid_size + 1):
            y = int(i * cell_height)
            draw.line([(0, y), (width, y)], fill=(200, 200, 200), width=1)

        # 中心のX軸とZ軸を太い線で描画
        draw.line([(width // 2, 0), (width // 2, height)], fill=(150, 150, 150), width=2)  # Y軸
        draw.line([(0, height // 2), (width, height // 2)], fill=(150, 150, 150), width=2)  # X軸

    @staticmethod
    def bezier_curve(control_points, num_segments):
        """
        ベジェ曲線を生成する関数。3次のベジェ曲線を使用。
        Args:
            control_points (list of tuples): 制御点のリスト [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
            num_segments (int): 曲線を分割するセグメント数
        Returns:
            list of tuples: 曲線上の点のリスト
        """
        n = len(control_points) - 1
        curve_points = []

        for t in [i / num_segments for i in range(num_segments + 1)]:
            x = sum(factorial(n) / (factorial(i) * factorial(n - i)) * (t ** i) * ((1 - t) ** (n - i)) * control_points[i][ 0] for i in range(n + 1))
            y = sum(factorial(n) / (factorial(i) * factorial(n - i)) * (t ** i) * ((1 - t) ** (n - i)) * control_points[i][1] for i in range(n + 1))
            curve_points.append((x, y))
        return curve_points


    def export_curve_to_png(self):

        print("export_curve_to_png")
        selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not selected_curves:
            QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
            return

        width = int(self.width_input.text())
        height = int(self.height_input.text())
        line_thickness = int(self.line_thickness_input.text())
        margin = self.MARGIN
        mask_enabled = self.mask_check.isChecked()

        print("num_samples => {}".format(self.num_samples))

        all_points = []
        control_vertices_list = []

        for curve in selected_curves:
            # 制御点（Control Vertices）を取得
            control_vertices = Texture_Exporter.get_curve_data(curve)
            control_vertice = [(cv[0], cv[2]) for cv in control_vertices]
            control_vertices_list.append(control_vertice)

            curve_points = self.get_curve_geometry_data(curve)
            all_points.append(curve_points)


        min_x = min(p[0] for curve in all_points for p in curve)
        max_x = max(p[0] for curve in all_points for p in curve)
        min_z = min(p[1] for curve in all_points for p in curve)
        max_z = max(p[1] for curve in all_points for p in curve)

        curve_width = max_x - min_x
        curve_height = max_z - min_z

        scale_factor = min((width - 2 * margin) / curve_width, (height - 2 * margin) / curve_height)
        offset_x = (width - curve_width * scale_factor) / 2 - min_x * scale_factor
        offset_z = (height - curve_height * scale_factor) / 2 - min_z * scale_factor

        # マスクの設定に基づいてアルファチャンネルを設定
        alpha_value = 0 if mask_enabled else 255

        image = Image.new('RGBA', (width, height), color=(255, 255, 255, alpha_value))
        draw = ImageDraw.Draw(image)

        # export edit points
        for curve in all_points:
            scaled_points = [((p[0] * scale_factor + offset_x), (p[1] * scale_factor + offset_z)) for p in curve]
            for i in range(len(scaled_points) - 1):
                draw.line([scaled_points[i], scaled_points[i + 1]], fill=self.selected_color + (255,), width=line_thickness)

        """
        # 制御点を描画（赤色）
        for control_vertices in control_vertices_list:
            scaled_control_points = [((p[0] * scale_factor + offset_x), (p[1] * scale_factor + offset_z)) for p in control_vertices]
            for i in range(len(scaled_control_points) - 1):
                draw.line([scaled_control_points[i], scaled_control_points[i + 1]], fill=(255, 0, 0, 255), width=line_thickness)
        """

        image_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;TGA Files (*.tga)", options=QFileDialog.Options())
        if image_file:
            image.save(image_file)
            QMessageBox.information(self, "Success", "Texture saved successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save texture.")
        pass

    @staticmethod
    def get_curve_data(curve):
        """
        カーブの制御点（CV）を取得
        """
        cv_count = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree") + 1
        control_vertices = [cmds.pointPosition(f"{curve}.cv[{i}]") for i in range(cv_count)]

        return control_vertices

    @staticmethod
    def get_edit_points(curve):
        """
        指定されたNURBSカーブのedit points（編集点）を取得する関数。
        Args:
            curve (str): 曲線の名前。
        Returns:
            list: 編集点の座標リスト。
        """
        try:
            num_edit_points = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree")
            edit_points = []
            for i in range(num_edit_points):
                point = cmds.pointOnCurve(curve, pr=i / (num_edit_points - 1), p=True)  # カーブ上のポイント取得
                edit_points.append(point)
            return edit_points
        except Exception as e:
            print(f"Error while getting edit points: {e}")
            return []


    def get_curve_geometry_data(self, curve):
        # カーブのパラメータ範囲を取得
        param_range = cmds.getAttr(f"{curve}.minMaxValue")[0]
        min_param = param_range[0]
        max_param = param_range[1]

        # 各サンプルのパラメータ値に対応する座標を取得
        geometry_points = []
        for i in range(self.num_samples + 1):
            param = min_param + ((max_param - min_param) * (i / self.num_samples))
            point = cmds.pointOnCurve(curve, pr=param, p=True)
            geometry_points.append((point[0], point[2]))
        return geometry_points


    def _export_curves_selected_to_json(self):
        selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not selected_curves:
            QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
            return None

        curve_data = []
        cloned_curves = []
        intersection_points = []

        grid_size = cmds.grid(q=True, size=True)
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        margin = self.MARGIN

        all_points = []

        # 1. 全ての曲線を処理し、全制御点を取得（min/max計算のため）
        for curve in selected_curves:
            original_cvs = self._get_curve_cvs(curve)
            for p in original_cvs:
                all_points.append(p)

        if not all_points:
            QMessageBox.warning(self, "Error", "No valid points found in curves.")
            return None

        # 2. 最小値と最大値を計算
        min_x = min(p[0] for p in all_points)
        max_x = max(p[0] for p in all_points)
        min_z = min(p[2] for p in all_points)
        max_z = max(p[2] for p in all_points)

        # 3. スケーリングとオフセットの計算
        width_with_margin = width - 2 * margin
        height_with_margin = height - 2 * margin

        scale_factor = min(width_with_margin / (max_x - min_x), height_with_margin / (max_z - min_z))
        offset_x = margin - min_x * scale_factor
        offset_z = margin - min_z * scale_factor

        # 4. 各曲線を処理
        for curve in selected_curves:
            cmds.select(curve)

            # 2. 曲線を複製し、Bezierに変換
            cloned_curve = cmds.duplicate(curve, returnRootsOnly=True)[0]
            cloned_curves.append(cloned_curve)
            cmds.nurbsCurveToBezier()

            # 3. オリジナルの制御点を取得
            original_cvs = self._get_curve_cvs(cloned_curve)

            # 4. グリッドを考慮して絶対座標に変換
            adjusted_cvs = [
                (cv[0] * grid_size, cv[1], cv[2] * grid_size) for cv in original_cvs
            ]

            # 5. 制御点を幅、高さ、マージンを考慮してスケーリング
            scaled_control_vertices = [
                ((x * scale_factor) + offset_x, y, (z * scale_factor) + offset_z) for x, y, z in adjusted_cvs
            ]

            # 6. ノットベクトルを取得
            knot_vector = None
            if cmds.attributeQuery("knots", node=cloned_curve, exists=True):
                knot_vector = cmds.getAttr(cloned_curve + ".knots")

            # 7. 制御点を取得
            cvs = None
            if cmds.attributeQuery("controlPoints", node=cloned_curve, exists=True):
                cvs = cmds.getAttr(cloned_curve + ".controlPoints[*]")

            curve_data.append({
                "curve_name": curve,
                "control_vertices": scaled_control_vertices,
                "knot_vector": knot_vector,
                "control_points": cvs,
            })

            # Bezier曲線の制御点を取得
            bezier_cvs = self._get_curve_cvs(cloned_curve)

            # Bezier制御点をグリッドを考慮して絶対座標に変換
            adjusted_bezier_cvs = [
                (bcv[0] * grid_size, bcv[1], bcv[2] * grid_size) for bcv in bezier_cvs
            ]

            # Bezier制御点を幅、高さ、マージンを考慮してスケーリング
            scaled_bezier_control_vertices = [
                ((x * scale_factor) + offset_x, y, (z * scale_factor) + offset_z) for x, y, z in bezier_cvs
            ]
            curve_data[-1]["bezier_control_vertices"] = scaled_bezier_control_vertices

        # 交差点を検出する
        for i in range(len(curve_data)):
            for j in range(i + 1, len(curve_data)):
                curve1 = curve_data[i]
                curve2 = curve_data[j]

                for k in range(len(curve1["control_vertices"]) - 1):
                    p1_start = curve1["control_vertices"][k]
                    p1_end = curve1["control_vertices"][k + 1]
                    for l in range(len(curve2["control_vertices"]) - 1):
                        p2_start = curve2["control_vertices"][l]
                        p2_end = curve2["control_vertices"][l + 1]
                        if Texture_Exporter._are_segments_intersecting(p1_start, p1_end, p2_start, p2_end):
                            intersection = Texture_Exporter._calculate_intersection(p1_start, p1_end, p2_start, p2_end)
                            if intersection:
                                intersection_points.append(intersection)


        # エクスポートするデータをまとめる
        export_data = {
            "curve_data": curve_data,
            "intersection_points": intersection_points
        }

        for curve in cloned_curves:
            cmds.delete(curve)

        cmds.select(selected_curves)
        return export_data


    def _fill_adjacent_pixels(self, draw, image_data, width, height):
        pixel_colors = []
        for x in range(width):
            for y in range(height):
                if image_data[x, y] == self.selected_color:
                    for dx in range(-self.PIXEL_SEARCH_RANGE, self.PIXEL_SEARCH_RANGE + 1):
                        for dy in range(-self.PIXEL_SEARCH_RANGE, self.PIXEL_SEARCH_RANGE + 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if image_data[nx, ny] == self.selected_color:
                                    pixel_colors.append((nx, ny))
        for px, py in pixel_colors:
            draw.point((px, py), fill=(255, 0, 0))


    def _mark_intersections(self, draw, image, line_coordinates):
        width, height = image.size
        for i in range(len(line_coordinates)):
            for j in range(i + 1, len(line_coordinates)):
                start1, end1 = line_coordinates[i]
                start2, end2 = line_coordinates[j]
                if self._are_segments_intersecting2d(start1, end1, start2, end2):
                    intersection_point = self._get_intersection_point2d(start1, end1, start2, end2)
                    #print("intersection_point => {}".format(intersection_point))
                    if intersection_point:
                        ix, iy = int(intersection_point[0]), int(intersection_point[1])
                        if 0 <= ix < width and 0 <= iy < height:
                            #draw.point((ix, iy), fill=(255, 0, 0))
                            pass
        image_data = image.load()
        self._fill_adjacent_pixels(draw, image_data, width, height)

    """
    write pixel data
    """
    @staticmethod
    def _are_segments_intersecting2d(p1_start, p1_end, p2_start, p2_end):
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        return (ccw(p1_start, p2_start, p2_end) != ccw(p1_end, p2_start, p2_end) and ccw(p1_start, p1_end, p2_start) != ccw(p1_start, p1_end, p2_end))

    """
    write pixel data
    """
    @staticmethod
    def _get_intersection_point2d(p1_start, p1_end, p2_start, p2_end):
        """交点を計算する関数"""
        x1, y1 = p1_start
        x2, y2 = p1_end
        x3, y3 = p2_start
        x4, y4 = p2_end
        denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denominator == 0:
            return None
        intersect_x = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denominator
        intersect_y = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denominator
        return (intersect_x, intersect_y)

    """
    write json data
    """
    @staticmethod
    def _are_segments_intersecting(p1_start, p1_end, p2_start, p2_end):
        def ccw(A, B, C):
            return (C[2] - A[2]) * (B[0] - A[0]) > (B[2] - A[2]) * (C[0] - A[0])
        return (ccw(p1_start, p2_start, p2_end) != ccw(p1_end, p2_start, p2_end)) and (ccw(p1_start, p1_end, p2_start) != ccw(p1_start, p1_end, p2_end))

    """
    write json data
    """
    @staticmethod
    def _calculate_intersection(p1_start, p1_end, p2_start, p2_end):
        x1, z1 = p1_start[0], p1_start[2]
        x2, z2 = p1_end[0], p1_end[2]
        x3, z3 = p2_start[0], p2_start[2]
        x4, z4 = p2_end[0], p2_end[2]

        denominator = (x1 - x2) * (z3 - z4) - (z1 - z2) * (x3 - x4)
        if abs(denominator) < 1e-10:
            return None

        # 交点を計算
        intersect_x = ((x1 * z2 - z1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * z4 - z3 * x4)) / denominator
        intersect_z = ((x1 * z2 - z1 * x2) * (z3 - z4) - (z1 - z2) * (x3 * z4 - z3 * x4)) / denominator

        # 線分の範囲内に交点があるか確認
        if (min(x1, x2) <= intersect_x <= max(x1, x2) and min(z1, z2) <= intersect_z <= max(z1, z2) and
                min(x3, x4) <= intersect_x <= max(x3, x4) and min(z3, z4) <= intersect_z <= max(z3, z4)):
            return (intersect_x, 0, intersect_z)

        return None



def show_main_window():
    global tex_exporter
    try:
        tex_exporter.close()  # type: ignore
        tex_exporter.deleteLater()  # type: ignore
    except:
        pass
    tex_exporter = Texture_Exporter()
    tex_exporter.show()


