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

        self.margin_label = None
        self.margin_input = None

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
        self.margin_label = QLabel('Margin:')

        self.width_input = QLineEdit(self)
        self.height_input = QLineEdit(self)
        self.line_thickness_input = QLineEdit(self)
        self.margin_input = QLineEdit(self)

        self.num_samples = 20

        # default value
        self.width_input.setText('4096')
        self.height_input.setText('4096')
        self.line_thickness_input.setText('10')
        self.margin_input.setText("0")

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
        #self.generate_button.clicked.connect(self.export_curve_to_png_uv)

        self.generate_button.clicked.connect(self._on_click_callback)
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
        layout.addWidget(self.margin_label)
        layout.addWidget(self.margin_input)
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

    def _on_click_callback(self):
        self.project_curves_onto_temporary_surface()

        pass

    def create_uv_mesh_with_curve(self, curve):
        """
        カーブのUV情報を反映させるために、仮のポリゴンプレーンを作成し、
        そのUV情報を編集します。
        """
        points =  self.get_curve_data(curve)

        if not points:
            cmds.warning("カーブの座標が取得できませんでした。")
            return

        min_x = min(point[0] for point in points)
        max_x = max(point[0] for point in points)
        min_z = min(point[2] for point in points)
        max_z = max(point[2] for point in points)

        uv_points = self.convert_to_uv(points, min_x, max_x, min_z, max_z)

        poly_plane = cmds.polyPlane(width=1, height=1, sx=1, sy=1, name="UV_Curve_Mesh")[0]
        uv_set = cmds.polyUVSet(poly_plane, query=True, currentUVSet=True)[0]

        for i, (u, v) in enumerate(uv_points):
            try:
                cmds.polyEditUV(f"{poly_plane}.map[{i}]", u=u, v=v, uvSetName=uv_set)
            except Exception as e:
                cmds.warning(f"UVの設定に失敗しました: {e}")
        print(f"UV情報が反映されたメッシュ: {poly_plane}")
        return poly_plane


    def project_curves_onto_temporary_surface(self):

        print("project_curves_onto_temporary_surface")

        selection = cmds.ls(selection=True, dag=True, type=["nurbsCurve", "mesh"])

        if len(selection) < 2:
            cmds.warning("1つ以上のカーブと1つのメッシュを選択してください。")
            return

        mesh = None
        curves = []
        for obj in selection:
            if cmds.nodeType(obj) == "mesh":
                mesh = obj
            elif cmds.nodeType(obj) == "nurbsCurve":
                curves.append(obj)

        if not mesh or len(curves) == 0:
            cmds.warning("1つのメッシュと1つ以上のカーブを選択してください。")
            return

        print(f"選択されたメッシュ: {mesh}")
        print(f"選択されたカーブ: {curves}")

        bbox = cmds.exactWorldBoundingBox(mesh)
        center_x = (bbox[0] + bbox[3]) / 2
        center_y = (bbox[1] + bbox[4]) / 2
        center_z = (bbox[2] + bbox[5]) / 2
        width = bbox[3] - bbox[0]
        height = bbox[5] - bbox[2]

        nurbs_surface = cmds.nurbsPlane(width=width * 1.2, lengthRatio=1.0, axis=(0, 1, 0), ch=False)[0]
        cmds.move(center_x, center_y, center_z, nurbs_surface)
        print(f"仮のNURBSサーフェスが作成されました: {nurbs_surface}")

        for curve in curves:
            try:
                # カーブの投影
                projected_curve = cmds.projectCurve(curve, nurbs_surface, direction=(0, 1, 0), ch=False)[0]
                print(f"カーブ {curve} がNURBSサーフェス {nurbs_surface} に投影されました: {projected_curve}")
                # 投影されたカーブのシェイプノードを取得
                duplicated_curve = cmds.duplicateCurve(projected_curve, ch=False, rn=False, local=False)[0]
                self.create_uv_mesh_with_curve(duplicated_curve)

                # 投影されたカーブを削除
                cmds.delete(projected_curve)

            except Exception as e:
                cmds.warning(f"カーブ {curve} の投影に失敗しました: {e}")

        cmds.delete(nurbs_surface)
        print("仮のNURBSサーフェスが削除されました。")


    """
    curve 情報をuvに投影する処理
    """
    def convert_curve_to_uv(self):

        print("export_curve_to_uv")
        selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not selected_curves:
            QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
            return

        all_points = []
        control_vertices_list = []

        for curve in selected_curves:
            # 制御点（Control Vertices）を取得
            control_vertices = Texture_Exporter.get_curve_data(curve)
            control_vertice = [(cv[0], cv[2]) for cv in control_vertices]  # XとZ座標を使用
            control_vertices_list.append(control_vertice)
            curve_points = self.get_curve_geometry_data(curve)
            all_points.append(curve_points)

        min_x = min(p[0] for curve in all_points for p in curve)
        max_x = max(p[0] for curve in all_points for p in curve)
        min_y = min(p[1] for curve in all_points for p in curve)
        max_y = max(p[1] for curve in all_points for p in curve)

        curve_width = max_x - min_x
        curve_height = max_y - min_y

        # UV空間にカーブを正しく収めるためにポリゴンプレーンを作成
        plane_width = curve_width * 1.2  # 余裕を持たせるために1.2倍
        plane_height = curve_height * 1.2

        # ポリゴンプレーンをカーブの大きさに基づいて作成
        poly_plane = cmds.polyPlane(width=plane_width, height=plane_height, sx=1, sy=1, name="UV_Plane")[0]

        # UVセットの情報を取得
        uv_set = cmds.polyUVSet(poly_plane, query=True, currentUVSet=True)[0]

        # すべてのカーブに対してUV情報を計算
        uv_points = []
        for curve_points in all_points:
            uv_list = []
            for point in curve_points:
                # XとY座標をUV座標として使用
                u = (point[0] - min_x) / curve_width
                v = (point[1] - min_y) / curve_height
                uv_list.append((u, v))
                print(f"Point: ({point[0]}, {point[1]}) -> UV: ({u}, {v})")
            uv_points.append(uv_list)
            print(f"uv info => {uv_list}")

        # ポリゴンプレーンのUVを調整してカーブに合わせる
        for uv_list in uv_points:
            for j, (u, v) in enumerate(uv_list):
                # ポリゴンプレーンのUVを設定
                cmds.polyEditUV(f"{poly_plane}.map[{j}]", u=u, v=v, uvSetName=uv_set)

        # UVウィンドウを表示
        cmds.TextureViewWindow()


    """
    curve dataのworld座標をuv座標に変換し書き出す
    """
    def export_curve_to_png_uv(self):
        selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not selected_curves:
            QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
            return

        all_uv_points = []
        min_x, max_x, min_y, max_y, min_z, max_z = None, None, None, None, None, None

        # 各カーブの座標を取得し、全体の範囲を計算
        for curve in selected_curves:

            #curve_points_uv = self.get_uv_data(curve)  # UV情報を取得する関数
            curve_points = Texture_Exporter.get_curve_data(curve)

            # カーブの範囲を計算
            cur_min_x, cur_max_x, cur_min_y, cur_max_y, cur_min_z, cur_max_z = Texture_Exporter.calculate_bounds(curve_points)

            # 最小/最大値を全体の範囲に統合
            if min_x is None or cur_min_x < min_x:
                min_x = cur_min_x
            if max_x is None or cur_max_x > max_x:
                max_x = cur_max_x
            if min_y is None or cur_min_y < min_y:
                min_y = cur_min_y
            if max_y is None or cur_max_y > max_y:
                max_y = cur_max_y
            if min_z is None or cur_min_z < min_z:
                min_z = cur_min_z
            if max_z is None or cur_max_z > max_z:
                max_z = cur_max_z

            # UV空間に変換して保存
            uv_points = Texture_Exporter.convert_to_uv(curve_points, min_x, max_x, min_z, max_z)

            for uv_pos in uv_points:
                print("uv pos => {}".format(uv_pos))

            all_uv_points.append(uv_points)

        # 画像サイズと線の太さを設定
        width = int(self.width_input.text())
        height = int(self.height_input.text())
        line_thickness = int(self.line_thickness_input.text())

        # ファイルパスの取得
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;TGA Files (*.tga)", options=QFileDialog.Options())

        if file_path:
            # カーブを画像に描画
            self.draw_curves_to_png(all_uv_points, width, height, line_thickness, file_path)
            QMessageBox.information(self, "Success", "Texture saved successfully.")
        else:
            QMessageBox.warning(self, "Error", "Failed to save texture.")
        pass


    """
    world座標をtextureの中心点から計算し描画
    """
    def export_curve_to_png_world_position(self):

        print("export_curve_to_png")
        selected_curves = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not selected_curves:
            QMessageBox.warning(self, "Error", "No curves selected. Please select at least one curve.")
            return

        width = int(self.width_input.text())
        height = int(self.height_input.text())
        line_thickness = int(self.line_thickness_input.text())
        margin = int(self.margin_input.text())
        mask_enabled = self.mask_check.isChecked()

        print("num_samples => {}".format(self.num_samples))

        all_points = []
        control_vertices_list = []

        for curve in selected_curves:
            # 制御点（Control Vertices）を取得
            """
            control_vertices = Texture_Exporter.get_curve_data(curve)
            control_vertice = [(cv[0], cv[2]) for cv in control_vertices]
            control_vertices_list.append(control_vertice)
            curve_points = self.get_curve_geometry_data(curve)
            """
            curve_points_uv = self.get_uv_data(curve)  # UV情報を取得する関数
            all_points.append(curve_points_uv)

        min_x = min(p[0] for curve in all_points for p in curve)
        max_x = max(p[0] for curve in all_points for p in curve)
        min_y = min(p[1] for curve in all_points for p in curve)
        max_y = max(p[1] for curve in all_points for p in curve)

        curve_width = max_x - min_x
        curve_height = max_y - min_y

        scale_factor = min((width - 2 * margin) / curve_width, (height - 2 * margin) / curve_height)
        offset_x = (width - curve_width * scale_factor) / 2 - min_x * scale_factor
        offset_z = (height - curve_height * scale_factor) / 2 - min_y * scale_factor

        # マスクの設定に基づいてアルファチャンネルを設定
        alpha_value = 0 if mask_enabled else 255

        image = Image.new('RGBA', (width, height), color=(255, 255, 255, alpha_value))
        draw = ImageDraw.Draw(image)

        # export edit points
        for curve in all_points:
            scaled_points = [((p[0] * scale_factor + offset_x), (p[1] * scale_factor + offset_z)) for p in curve]
            for i in range(len(scaled_points) - 1):
                draw.line([scaled_points[i], scaled_points[i + 1]], fill=self.selected_color + (255,), width=line_thickness)

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
    def calculate_bounds(points):
        """
        ポイントリストから最小値と最大値を計算
        """
        min_x = min(p[0] for p in points)
        max_x = max(p[0] for p in points)
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        min_z = min(p[2] for p in points)
        max_z = max(p[2] for p in points)
        return min_x, max_x, min_y, max_y, min_z, max_z


    def draw_curves_to_png(self, uv_points, width, height, line_thickness, file_path):

        mask_enabled = self.mask_check.isChecked()

        # マスクの設定に基づいてアルファチャンネルを設定
        alpha_value = 0 if mask_enabled else 255

        """
        UV座標を基にPNG画像にカーブを描画し、ファイルに保存
        """
        # 画像の作成
        image = Image.new('RGBA', (width, height), color=(255, 255, 255, alpha_value))  # 背景を透明に
        draw = ImageDraw.Draw(image)

        # 各カーブの描画
        for uv_point in uv_points:
            # デバッグ: uv_pointsの内容を確認
            if not all(isinstance(point, tuple) and len(point) == 2 for point in uv_point):
                print("Error: UV points are not in the correct format (expected tuples of (u, v)).")
                print(f"Actual content: {uv_point}")
                continue
            scaled_points = [(u * width, (1 - v) * height) for u, v in uv_point]  # Vを上下反転
            for i in range(len(scaled_points) - 1):
                draw.line([scaled_points[i], scaled_points[i + 1]], fill=(0, 0, 0, 255), width=line_thickness)

        # 画像をファイルに保存
        image.save(file_path)
        print(f"Image saved to {file_path}")



    @staticmethod
    def convert_to_uv(points, min_x, max_x, min_z, max_z):
        """
        3D座標をUV空間に正規化
        """
        uv_points = []
        x_range = max_x - min_x
        z_range = max_z - min_z

        # XまたはZの範囲が0の場合には1に設定してエラーを回避
        if x_range == 0:
            x_range = 1.0
        if z_range == 0:
            z_range = 1.0

        for point in points:
            u = (point[0] - min_x) / x_range  # X座標をUに変換
            v = (point[2] - min_z) / z_range  # Z座標をVに変換
            uv_points.append((u, v))
        return uv_points


    def get_uv_data(self, curve):
        """
        指定されたカーブのUV情報を取得します。
        UV空間は0〜1の範囲に正規化されます。
        """
        num_points = self.num_samples  # UV空間上でサンプリングするポイント数
        uv_points = []
        for i in range(num_points + 1):
            param = float(i) / num_points
            position = cmds.pointOnCurve(curve, pr=param, top=True, p=True)
            u = (position[0] + 5) / 10  # X座標をUに正規化（例として-5〜5の範囲を0〜1に変換）
            v = (position[2] + 5) / 10  # Z座標をVに正規化（例として-5〜5の範囲を0〜1に変換）
            uv_points.append((u, v))
        return uv_points


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


