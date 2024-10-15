# -*- coding: utf-8 -*-

import sys
import json
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QColorDialog, QMessageBox
from PIL import Image, ImageDraw
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya

import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from math import factorial
import math


info = cmds.about(version=True)
version = int(info.split(" ")[0])


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window), QtWidgets.QDialog)
    else:
        return wrapInstance(long(main_window), QtWidgets.QDialog) # type: ignore



class Texture_Exporter(QtWidgets.QDialog):

    WINDOW_TITLE = "Texture Exporter"
    MODULE_VERSION = "1.0"
    MARGIN = 200
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

        self.width_input = QLineEdit(self)
        self.height_input = QLineEdit(self)
        self.line_thickness_input = QLineEdit(self)

        # default value
        self.width_input.setText('2048')
        self.height_input.setText('2048')
        self.line_thickness_input.setText('10')

        self.curve_color_input = QLineEdit(self)
        self.curve_color_input.setReadOnly(True)
        self.curve_color_input.setText(str(self.selected_color))

        self.curve_color_button = QtWidgets.QPushButton('Select Curve Color')
        self.curve_color_button.clicked.connect(self._choose_color)
        self.curve_color_button.setStyleSheet(self.default_style)

        self.generate_button = QtWidgets.QPushButton('Export')
        self.generate_button.clicked.connect(self._generate_image_from_curve)
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
        layout.addWidget(separator_line_1)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)
        #self.setWindowTitle('Curve Image Generator')
        #self.show()

    def _choose_color(self):
        # QColorDialog を使って色を選択
        color = QColorDialog.getColor()

        if color.isValid():
            # 色をRGBタプルに変換
            self.selected_color = color.getRgb()[:3]
            #self.curve_color_button.setStyleSheet(f'background-color: {color.name()}; color: white')
            self.curve_color_input.setText(str(self.selected_color))

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


    def _generate_image_from_curve(self):
        try:
            print("_generate_image_from_curve")

            width = int(self.width_input.text())
            height = int(self.height_input.text())
            line_thickness = int(self.line_thickness_input.text())

            grid_size = int(cmds.grid(q=True, size=True) * 2)
            grid_divisions = cmds.grid(q=True, divisions=True)

            selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

            if not selected_curves:
                QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
                return

            all_points = []
            curve_data = []

            for curve in selected_curves:
                cmds.select(curve)
                spans = cmds.getAttr(f"{curve}.spans")
                degree = cmds.getAttr(f"{curve}.degree")
                # 制御点を取得
                original_cvs = self._get_curve_cvs(curve)

                if not original_cvs:
                    continue

                # スパンと次数を使って各セグメントを細かく分割し描画
                num_points = spans + degree  # 点の数はスパン+次数
                curve_points = []

                for i in range(num_points):
                    param = i / (num_points - 1)
                    point = cmds.pointOnCurve(curve, pr=param, p=True)  # カーブ上の座標取得
                    curve_points.append(point)

                curve_data.append({
                    "curve_name": curve,
                    "control_vertices": curve_points #original_cvs["control_vertices"]
                })

                all_points.extend(curve_points) #original_cvs["control_vertices"]

            if not all_points:
                QMessageBox.warning(self, "Error", "No valid points found in curves.")
                return

            min_x = min(p[0] for p in all_points)
            max_x = max(p[0] for p in all_points)
            min_z = min(p[2] for p in all_points)
            max_z = max(p[2] for p in all_points)

            width_with_margin = width - 2 * self.MARGIN
            height_with_margin = height - 2 * self.MARGIN

            scale_factor_x = width_with_margin / (max_x - min_x) if max_x != min_x else 1
            scale_factor_z = height_with_margin / (max_z - min_z) if max_z != min_z else 1

            offset_x = (width / 2) - ((min_x + max_x) / 2 * scale_factor_x)
            offset_z = (height / 2) - ((min_z + max_z) / 2 * scale_factor_z)

            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)

            self._draw_grid(draw, width, height, grid_size, grid_divisions)

            for curve_info in curve_data:
                points = curve_info["control_vertices"]
                scaled_points = [
                    (
                        (x * scale_factor_x) + offset_x,
                        (z * scale_factor_z) + offset_z
                    ) for x, y, z in points
                ]

                for i in range(len(scaled_points) - 1):
                    start_point = scaled_points[i]
                    end_point = scaled_points[i + 1]
                    draw.line([start_point, end_point], fill=self.selected_color, width=line_thickness)

            image_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;TGA Files (*.tga)", options=QFileDialog.Options())
            if image_file:
                image.save(image_file)
                QMessageBox.information(self, "Success", "Texture saved successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save texture.")

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Value error occurred: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {e}")


    def _generate_image_from_curve_data(self):
        try:
            width = int(self.width_input.text())
            height = int(self.height_input.text())
            line_thickness = int(self.line_thickness_input.text())

            json_data = self._export_curves_selected_to_json()

            if json_data is None:
                QMessageBox.warning(self, "Error", "No curve data available.")
                return

            print("json data => {}".format(json_data))

            all_points = []
            for curve_info in json_data["curve_data"]:
                for p in curve_info["control_vertices"]:
                    all_points.append(p)
                for p in curve_info.get("bezier_control_vertices", []):
                    all_points.append(p)

            if not all_points:
                QMessageBox.warning(self, "Error", "No valid points found in curves.")
                return

            min_x = min(p[0] for p in all_points)
            max_x = max(p[0] for p in all_points)
            min_z = min(p[2] for p in all_points)
            max_z = max(p[2] for p in all_points)

            width_with_margin = width - 2 * self.MARGIN
            height_with_margin = height - 2 * self.MARGIN
            # X方向とZ方向のスケーリングを同じにして、縦横比を保持する
            scale_factor = min(width_with_margin / (max_x - min_x), height_with_margin / (max_z - min_z))

            # オフセットを計算（Mayaの原点をPNGの中央に対応させる）
            offset_x = self.MARGIN - min_x * scale_factor
            offset_z = self.MARGIN - min_z * scale_factor

            # 画像を作成
            image = Image.new('RGB', (width, height), color=(255, 255, 255))
            draw = ImageDraw.Draw(image)

            # Mayaのグリッド設定を取得
            grid_size = int(cmds.grid(q=True, size=True) * 2)
            grid_divisions = cmds.grid(q=True, divisions=True)
            self._draw_grid(draw, width, height, grid_size, grid_divisions)

            line_coordinates = []

            for curve_info in json_data["curve_data"]:
                points = curve_info["control_vertices"]
                scaled_points = [
                    (
                        (x * scale_factor) + offset_x,
                        (z * scale_factor) + offset_z
                    ) for x, y, z in points
                ]
                bezier_points = Texture_Exporter.bezier_curve(scaled_points, num_points=100)
                for i in range(len(bezier_points) - 1):
                    draw.line([bezier_points[i], bezier_points[i + 1]], fill=self.selected_color, width=line_thickness)
                    line_coordinates.append((bezier_points[i], bezier_points[i + 1]))
            # write image
            image_file, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;TGA Files (*.tga)", options=QFileDialog.Options())
            if image_file:
                image.save(image_file)
                QMessageBox.information(self, "Success", "Texture saved successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to save texture.")

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Value error occurred: {e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"An unexpected error occurred: {e}")


    """
    指定されたカーブのControl Verticesを取得
    """
    @staticmethod
    def _get_curve_cvs(curve):
        """
        指定されたNURBSカーブの制御点と曲線の属性を取得する関数。
        Args:
            curve (str): 曲線の名前。
        Returns:
            dict: 制御点、ノットベクトル、スパン、次数などの情報を含む辞書。
        """
        try:
            cv_count = cmds.getAttr(f"{curve}.spans") + cmds.getAttr(f"{curve}.degree")
            control_vertices = [cmds.pointPosition(f"{curve}.cv[{i}]") for i in range(cv_count)]

            knot_vector = None
            if cmds.attributeQuery("knots", node=curve, exists=True):
                knot_vector = cmds.getAttr(f"{curve}.knots")

            spans = None
            if cmds.attributeQuery("spans", node=curve, exists=True):
                spans = cmds.getAttr(f"{curve}.spans")

            degree = None
            if cmds.attributeQuery("degree", node=curve, exists=True):
                degree = cmds.getAttr(f"{curve}.degree")

            param_range = None
            if cmds.attributeQuery("minMaxValue", node=curve, exists=True):
                param_range = cmds.getAttr(f"{curve}.minMaxValue")

            return {
                "control_vertices": control_vertices,
                "knot_vector": knot_vector,
                "spans": spans,
                "degree": degree,
                "param_range": param_range
            }
        except Exception as e:
            print(f"Error while getting curve attributes: {e}")
            return None

    def _get_unified_cvs(self, cvs):
        whd = self._get_width_height(cvs)
        dx, dy = abs(whd[1] - whd[0]), abs(whd[3] - whd[2])

        if dx < dy:
            return self._filter_cvs(cvs, 1, 2)
        return self._filter_cvs(cvs, 0, 2)

    @staticmethod
    def _get_width_height(cvs):
        result = []
        if len(cvs) == 0:
            return result
        xmin = xmax = ymin = ymax = 0
        for i in range(0, len(cvs), 3):
            if i == 0:
                xmin = xmax = cvs[i]
                ymin = ymax = cvs[i + 1]
            else:
                xmin = min(xmin, cvs[i])
                xmax = max(xmax, cvs[i])
                ymin = min(ymin, cvs[i + 1])
                ymax = max(ymax, cvs[i + 1])

        result = [xmin, xmax, ymin, ymax]
        return result


    @staticmethod
    def _get_bspline_cvs(curve):
        result = []
        degree = cmds.getAttr(curve + ".degree")
        if degree < 3:
            return result
        result = cmds.xform(curve + ".cv[*]", query=True, translation=True, worldSpace=True)
        return result

    def _filter_cvs(self, cvs, x, y):
        result = []
        scale = self.SCALE
        for i in range(0, len(cvs), 3):
            result.append(scale * cvs[i + x])
            result.append(scale * cvs[i + y])
        return result

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

    """
    Return a list of points representing a Bézier curve.
    """
    @staticmethod
    def bezier_curve(points, num_points=100):
        def bernstein_poly(n, i, t):
            return (factorial(n) / (factorial(i) * factorial(n - i))) * (t ** i) * ((1 - t) ** (n - i))

        n = len(points) - 1
        if n < 1:
            print("Error: Not enough points to create a Bézier curve.")
            return []

        print("bezier_curve points => {}".format(n))

        curve_points = []
        for t in [i / (num_points - 1) for i in range(num_points)]:
            x = sum(bernstein_poly(n, i, t) * points[i][0] for i in range(n + 1))
            z = sum(bernstein_poly(n, i, t) * points[i][1] for i in range(n + 1))
            curve_points.append((x, z))
        return curve_points

    @staticmethod
    def _get_intersection_points(lines):
        """
        選択した線の交点を計算する。
        """
        points = []
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                if cmds.attributeQuery("controlVertices", node=lines[i], exists=True) and cmds.attributeQuery("controlVertices", node=lines[j], exists=True):
                    # Get control vertices for the two curves
                    cv1 = cmds.getAttr(f"{lines[i]}.controlVertices")[0]
                    cv2 = cmds.getAttr(f"{lines[j]}.controlVertices")[0]

                    # Check for intersections
                    for k in range(len(cv1) - 1):
                        for l in range(len(cv2) - 1):
                            p1 = cv1[k]
                            p2 = cv1[k + 1]
                            q1 = cv2[l]
                            q2 = cv2[l + 1]
                            intersection = Texture_Exporter._line_intersection(p1, p2, q1, q2)
                            if intersection:
                                points.append(intersection)
                else:
                    print(f"Warning: {lines[i]} or {lines[j]} does not have controlVertices attribute.")

        return points

    @staticmethod
    def _line_intersection(p1, p2, q1, q2):
        """
        点p1, p2と点q1, q2で定義される2つの直線の交点を計算する
        """
        # Convert to vector form
        p1 = (p1[0], p1[1])
        p2 = (p2[0], p2[1])
        q1 = (q1[0], q1[1])
        q2 = (q2[0], q2[1])

        # Vector calculations
        a1 = p2[1] - p1[1]
        b1 = p1[0] - p2[0]
        c1 = a1 * p1[0] + b1 * p1[1]

        a2 = q2[1] - q1[1]
        b2 = q1[0] - q2[0]
        c2 = a2 * q1[0] + b2 * q1[1]
        determinant = a1 * b2 - a2 * b1
        if determinant == 0:
            return None  # Parallel lines
        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
        return (x, y)

    def _detect_intersections(self, json_data):
        intersection_points = []
        curves = json_data["curve_data"]

        for i in range(len(curves)):
            for j in range(i + 1, len(curves)):
                points_a = curves[i]["control_vertices"]
                points_b = curves[j]["control_vertices"]

                # 交点を検出
                for point_a in points_a:
                    for point_b in points_b:
                        if math.isclose(point_a[0], point_b[0], abs_tol=self.INTERSECTION_TOLERANCE) and math.isclose(point_a[2], point_b[2], abs_tol=self.INTERSECTION_TOLERANCE):
                            intersection_points.append({
                                "point": point_a,
                                "curves": [curves[i]["curve_name"], curves[j]["curve_name"]]
                            })

        return {
            "intersections": intersection_points
        }


def show_main_window():
    global tex_exporter
    try:
        tex_exporter.close()  # type: ignore
        tex_exporter.deleteLater()  # type: ignore
    except:
        pass
    tex_exporter = Texture_Exporter()
    tex_exporter.show()


