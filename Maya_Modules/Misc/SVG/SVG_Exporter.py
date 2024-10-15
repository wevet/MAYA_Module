# -*- coding: utf-8 -*-

"""
supported version MAYA 2023, 2025
"""


import maya.cmds as cmds
import maya.OpenMayaUI as omui
import os
import sys

info = cmds.about(version=True)
version = int(info.split(" ")[0])

if version >= 2025:
    from PySide6 import QtCore, QtWidgets
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
else:
    from PySide2 import QtCore, QtWidgets
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *


#from shiboken2 import wrapInstance

"""
def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window), QtWidgets.QDialog)
    else:
        return wrapInstance(long(main_window), QtWidgets.QDialog) # type: ignore
"""

class SVGExporterUI(QtWidgets.QDialog):

    WINDOW_TITLE = "SVG Exporter"
    MODULE_VERSION = "1.0"
    SCALE = 100

    def __init__(self, parent=None, *args, **kwargs):
        #super(SVGExporterUI, self).__init__(maya_main_window())
        super(SVGExporterUI, self).__init__()

        self.margin = 50
        self.line_thickness = 2

        self.check_intersection = False

        #self.ui = None
        self.texture_size_label = None
        self.texture_size_input = None

        self.line_thickness_label = None
        self.line_thickness_input = None

        self.calculate_bounding_box_check = None
        self.bounding_box_margin_label = None
        self.bounding_box_margin_input = None

        self.check_intersection = None
        self.default_style = None
        self._create_ui()


    def _create_ui(self):
        self.default_style = "background-color: #34d8ed; color: black"
        self.setStyleSheet('background-color:#262f38;')
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(300, 240)

        self.texture_size_label = QtWidgets.QLabel("Texture Size (Width, Height):")
        self.texture_size_label.setStyleSheet("color: darkgray")
        self.texture_size_input = QtWidgets.QLineEdit("2000, 2000")

        self.line_thickness_label = QtWidgets.QLabel("Line Thickness:")
        self.line_thickness_label.setStyleSheet("color: darkgray")
        self.line_thickness_input = QtWidgets.QLineEdit("2")

        self.calculate_bounding_box_check = QtWidgets.QCheckBox("Calculate BoundingBox:")
        self.calculate_bounding_box_check.setStyleSheet("color: darkgray")

        self.bounding_box_margin_label = QtWidgets.QLabel("Margin:")
        self.bounding_box_margin_label.setStyleSheet("color: darkgray")
        self.bounding_box_margin_input = QtWidgets.QLineEdit("50")

        #self.check_intersection = QtWidgets.QCheckBox("Check for Curve Intersections")
        #self.check_intersection.setStyleSheet("color: darkgray")

        self.export_button = QtWidgets.QPushButton("Export to SVG")
        self.export_button.setStyleSheet(self.default_style)
        self.export_button.clicked.connect(self._on_click_export_svg)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.texture_size_label)
        layout.addWidget(self.texture_size_input)
        layout.addWidget(self.line_thickness_label)
        layout.addWidget(self.line_thickness_input)

        layout.addWidget(self.calculate_bounding_box_check)

        layout.addWidget(self.bounding_box_margin_label)
        layout.addWidget(self.bounding_box_margin_input)

        #layout.addWidget(self.check_intersection)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

    # ui event callback
    def _on_click_export_svg(self):
        texture_size_input = self.texture_size_input.text().strip()
        line_thickness_input = self.line_thickness_input.text().strip()
        margin_input = self.bounding_box_margin_input.text().strip()

        try:
            # テクスチャサイズを取得
            width, height = map(int, texture_size_input.split(','))

            # ラインの太さを取得
            self.line_thickness = float(line_thickness_input)

            # 余白
            self.margin = float(margin_input)

            # 交点チェック?
            self.check_intersection = False #self.check_intersection.isChecked()

            # エクスポートするファイル名を指定
            file_name = cmds.fileDialog2(fileFilter='SVG Files (*.svg)', dialogStyle=2, caption='Save SVG')[0]
            if file_name:
                self._export_curves_selected_to_svg(file_name, (width, height))
                QtWidgets.QMessageBox.information(self, "Success", "SVG exported successfully!")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    """
    SVG exportの実処理
    """
    def _export_curves_selected_to_svg(self, file_name, texture_size):

        lines = cmds.ls(selection=True, dag=True, type="nurbsCurve")

        if not lines:
            raise ValueError("No curves selected for export.")

        paths = ""

        intersection_points = []  # 交点を格納するリスト

        # x_min, x_max, y_min, y_max
        bounding_box = [0.0, 0.0, 0.0, 0.0]

        for line in lines:
            cmds.select(line)
            cvs = self._get_curve_cvs(line)
            cvs = self._get_unified_cvs(cvs)
            SVGExporterUI._update_bounding_box(cvs, bounding_box)

            if len(cvs) > 0:
                paths += self._get_path_from_cvs(cvs) + "\n"

            # cleanup
            cmds.delete()

        width = texture_size[0] #bounding_box[1] - bounding_box[0] + 2 * self.margin
        height = texture_size[1] #bounding_box[3] - bounding_box[2] + 2 * self.margin

        if self.calculate_bounding_box_check.isChecked():
            width = bounding_box[1] - bounding_box[0] + 2 * self.margin
            height = bounding_box[3] - bounding_box[2] + 2 * self.margin

        if self.check_intersection:
            pass

        intersection_points += self._get_intersection_points(lines)

        # 交点をSVGパスに追加
        for point in intersection_points:
            print("found intersection points => {}".format(len(intersection_points)))
            radius = 5
            paths += f'<circle cx="{point[0]}" cy="{point[1]}" r="{radius}" fill="red" />\n'

        print("texture_size w => {}, h => {}".format(width, height))

        template = self._svg_template(width, height)
        output = template.replace("%paths%", paths)

        #output = output.replace("%width%", str(width))
        #output = output.replace("%height%", str(height))

        if self.check_intersection:
            pass

        trans_x = -1.0 * int(bounding_box[0]) + self.margin
        trans_y = int(bounding_box[3]) + self.margin
        output = output.replace("%trans_x%", str(trans_x))
        output = output.replace("%trans_y%", str(trans_y))

        with open(file_name, 'w') as file:
            file.write(output)
        print("SVG file saved to: {}".format(file_name))
        cmds.select(lines)


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
                            intersection = SVGExporterUI._line_intersection(p1, p2, q1, q2)
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

    def _get_curve_cvs(self, curve):
        cvs = []
        degree = cmds.getAttr(curve + ".degree")
        if degree < 3:
            print(f"Sorry, curve '{curve}' needs to be of degree 3!")
            return cvs

        duplicate = cmds.duplicate(curve, returnRootsOnly=True)
        cmds.nurbsCurveToBezier()
        cvs = self._get_bspline_cvs(duplicate[0])
        return cvs

    def _svg_template(self, width, height):
        return f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?><svg id="main" width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><g id="frame" transform="translate(%trans_x%, %trans_y%) scale(1, -1)">%paths%</g></svg>"""

    def _path_template(self, stroke_width):
        return f"""<path d="M %mx% ,%my% C %points% " id="line16832" style="fill:none;stroke:#000000;stroke-width:{stroke_width};stroke-miterlimit:4;stroke-dasharray:none;stroke-opacity:1" />"""


    def _filter_cvs(self, cvs, x, y):
        result = []
        scale = self.SCALE
        for i in range(0, len(cvs), 3):
            result.append(scale * cvs[i + x])
            result.append(scale * cvs[i + y])
        return result


    """
    カーブの各軸の最小・最大差分を計算
    """
    def _get_unified_cvs(self, cvs):
        whd = self._get_width_height(cvs)
        dx, dy = abs(whd[1] - whd[0]), abs(whd[3] - whd[2])

        if dx < dy:
            return self._filter_cvs(cvs, 1, 2)
        return self._filter_cvs(cvs, 0, 2)


    """
    SVG形式でカーブを描画するためのパスを構築
    """
    def _get_path_from_cvs(self, cvs):
        output = self._path_template(self.line_thickness)
        points = ""

        for i in range(0, len(cvs), 2):
            if i == 0:
                output = output.replace("%mx%", str(cvs[i]))
                output = output.replace("%my%", str(cvs[i + 1]))
            else:
                points += f"{cvs[i]},{cvs[i + 1]} "

        output = output.replace("%points%", points.strip())
        return output


    """
    制御点の座標からバウンディングボックス（最小の外接矩形）を計算
    """
    @staticmethod
    def _update_bounding_box(cvs, bounding_box):
        # 初期化されていない場合、最初の制御点でバウンディングボックスを設定
        for i in range(0, len(cvs), 2):
            if i == 0 and all(b == 0 for b in bounding_box):
                bounding_box[0] = bounding_box[1] = cvs[i] # min max
                bounding_box[2] = bounding_box[3] = cvs[i + 1] # min max
            bounding_box[0] = min(bounding_box[0], cvs[i])
            bounding_box[1] = max(bounding_box[1], cvs[i])
            bounding_box[2] = min(bounding_box[2], cvs[i + 1])
            bounding_box[3] = max(bounding_box[3], cvs[i + 1])



def show_main_window():
    global svg_expoter_ui
    try:
        svg_expoter_ui.close()
        svg_expoter_ui.deleteLater()
    except:
        pass
    svg_expoter_ui = SVGExporterUI()
    svg_expoter_ui.show()
    return svg_expoter_ui


