# -*- coding: utf-8 -*-

import sys
import maya.cmds as cmds
import math
import numpy as np


class Face_Intersection:

    def __init__(self):
        self.droplet_group_name = "DropletGroup"
        self.angle_threshold = 45  # 交差の角度の閾値 (°)
        self.droplet_size = 0.05  # えきだまりのサイズ
        self.voxel_size = 0.1  # ボクセルサイズ
        self.tolerance = 0.8  # Default tolerance for intersection in cm

        self.intersections = []


    """
    face での交点検出
    """
    def detect_intersections_between_faces(self, mesh_list):
        """
        異なるメッシュ間でのface交差を検出し、交差点にドロップレットを配置します
        """

        intersection_positions = set()  # 交差点の座標を保持するセット

        for i, mesh1 in enumerate(mesh_list):
            faces1 = cmds.polyListComponentConversion(mesh1, toFace=True)
            face_list1 = cmds.ls(faces1, fl=True)

            for j, mesh2 in enumerate(mesh_list):
                if i >= j:
                    continue

                faces2 = cmds.polyListComponentConversion(mesh2, toFace=True)
                face_list2 = cmds.ls(faces2, fl=True)

                # `numpy`を使ってfaceの中心座標を取得
                centers1 = np.array([self.get_face_center(face) for face in face_list1 if self.get_face_center(face) is not None])
                centers2 = np.array([self.get_face_center(face) for face in face_list2 if self.get_face_center(face) is not None])

                if centers1.size == 0 or centers2.size == 0:
                    continue

                # 距離計算（ベクトル化）
                distances = np.linalg.norm(centers1[:, None] - centers2, axis=2)

                # 距離が閾値未満のペアのみをチェック
                intersecting_pairs = np.where(distances < self.voxel_size)

                for idx1, idx2 in zip(*intersecting_pairs):
                    face1, face2 = face_list1[idx1], face_list2[idx2]
                    normal1 = self.get_face_normal(face1)
                    normal2 = self.get_face_normal(face2)

                    if normal1 is None or normal2 is None:
                        continue

                    angle = self.calculate_angle_between_vectors(normal1, normal2)
                    intersection_type = self._determine_intersection_type(angle)

                    if intersection_type == "none":
                        continue

                    # 交差位置を計算
                    intersection_position = ((centers1[idx1] + centers2[idx2]) / 2).tolist()

                    if intersection_position and not self._is_near_existing_intersection(intersection_position, intersection_positions):
                        intersection_positions.add(tuple(intersection_position))

                        self.intersections.append({
                            "position": intersection_position,
                            "angle": angle,
                            "type": intersection_type
                        })
                        print(f"Intersection detected between {face1} and {face2} with angle {angle}° at {intersection_position}.")

        if not self.intersections:
            print("No intersections found between selected faces.")
        else:
            print(f"{len(self.intersections)} intersections found between selected faces.")
            self._create_droplets_for_intersections()


    def _is_near_existing_intersection(self, position, intersection_positions):
        """
        既存の交差位置に対して、指定された位置が近似的に一致するかを確認します。
        """
        for existing_position in intersection_positions:
            distance = np.linalg.norm(np.array(existing_position) - np.array(position))
            if distance < self.tolerance:
                return True
        return False


    def _create_droplets_for_intersections(self):
        """
        保存された交差情報に基づいて、ドロップレットメッシュを生成
        """
        droplet_group = cmds.group(empty=True, name=self.droplet_group_name)

        for intersection in self.intersections:
            position = intersection["position"]
            intersection_type = intersection["type"]
            droplet_mesh = self._create_droplet_by_intersection_type(intersection_type, position)
            if droplet_mesh:
                cmds.move(position[0], position[1], position[2], droplet_mesh, worldSpace=True)
                print(f"Droplet created at {position} for intersection type {intersection_type}")
                cmds.parent(droplet_mesh, droplet_group)


    def _is_intersecting_faces(self, face1, face2):
        # faceの中心座標を取得して、交差をチェック
        center1 = self.get_face_center(face1)
        center2 = self.get_face_center(face2)

        if center1 and center2:
            distance = self.calculate_distance(center1, center2)
            return distance < self.voxel_size  # ボクセルサイズに依存する閾値で判定
        return False


    def _get_face_intersection_position(self, face1, face2):
        """
        2つの異なるfaceの交差位置を計算します。
        ここではfaceの中心点の平均を近似的な交差位置としています。
        """
        center1 = self.get_face_center(face1)
        center2 = self.get_face_center(face2)

        if center1 and center2:
            # 2つの中心点の平均を交差位置とする
            intersection_x = (center1[0] + center2[0]) / 2
            intersection_y = (center1[1] + center2[1]) / 2
            intersection_z = (center1[2] + center2[2]) / 2
            return [intersection_x, intersection_y, intersection_z]
        else:
            print(f"Unable to determine intersection position for {face1} and {face2}")
            return None


    @staticmethod
    def get_face_normal(face):
        """
        指定されたfaceの法線ベクトルを取得します。
        """
        try:
            # polyInfoコマンドでfaceの法線情報を取得
            normal_info = cmds.polyInfo(face, faceNormals=True)
            if normal_info:
                normal_values = list(map(float, normal_info[0].split()[-3:]))
                return np.array(normal_values)
            else:
                print(f"No normal info found for {face}")
                return None

        except Exception as e:
            print(f"Failed to get face normal for {face}: {e}")
            return None


    @staticmethod
    def get_face_center(face):
        """
        指定されたfaceの中心座標を取得します。
        """
        try:
            # faceの頂点リストを取得
            vertices = cmds.polyListComponentConversion(face, toVertex=True)
            vertex_list = cmds.ls(vertices, fl=True)

            # 各頂点の位置を取得して、中心を計算
            if not vertex_list:
                raise ValueError(f"No vertices found for face {face}")

            positions = np.array([cmds.pointPosition(vtx, world=True) for vtx in vertex_list])
            return np.mean(positions, axis=0)

        except Exception as e:
            print(f"Failed to get face center for {face}: {e}")
            return None


    @staticmethod
    def calculate_angle_between_vectors(vector1, vector2):
        """
        2つのベクトル間の角度を計算して返します（度数法）。
        """
        # 内積とベクトルの大きさを計算
        dot_product = np.dot(vector1, vector2)
        magnitude1 = np.linalg.norm(vector1)
        magnitude2 = np.linalg.norm(vector2)

        # コサインの値を -1から1の範囲に制限して角度を計算
        cos_theta = np.clip(dot_product / (magnitude1 * magnitude2), -1.0, 1.0)
        angle_radians = np.arccos(cos_theta)
        return np.degrees(angle_radians)


    def _get_voxel_key(self, position):
        # ボクセルキー（x, y, z のボクセル位置）を計算
        return tuple(int(pos // self.voxel_size) for pos in position)


    @staticmethod
    def calculate_distance(pos1, pos2):
        # 2つのエッジの距離を計算
        return math.sqrt(sum((p1 - p2) ** 2 for p1, p2 in zip(pos1, pos2)))


    def _create_droplet_by_intersection_type(self, intersection_type, position):
        """
        交差の種類に基づいて適切なメッシュ（ドロップレット）を生成し、指定された位置に配置します。
        """
        if intersection_type == "cross":
            droplet_mesh = cmds.polySphere(radius=self.droplet_size, name="Droplet_Circle")[0]
        elif intersection_type == "T":
            droplet_mesh = cmds.polyCube(width=self.droplet_size, height=self.droplet_size, depth=self.droplet_size, name="Droplet_T")[0]
        elif intersection_type == "diagonal":
            droplet_mesh = cmds.polyCylinder(radius=self.droplet_size, height=0.05, name="Droplet_Ellipse")[0]
        else:
            return None
        return droplet_mesh


    def _determine_intersection_type(self, angle):
        """
        交差の角度に基づき交差の種類を判定します。
        """
        if self._is_cross_intersection(angle):
            return "cross"
        elif self._is_t_intersection(angle):
            return "T"
        elif self._is_diagonal_intersection(angle):
            return "diagonal"
        return "none"


    def _is_cross_intersection(self, angle):
        # 十字交差判定
        return abs(angle - 90) < self.angle_threshold


    def _is_t_intersection(self, angle):
        # T字交差判定
        return abs(angle - 90) < self.angle_threshold / 2


    def _is_diagonal_intersection(self, angle):
        # 斜め交差の判定
        return abs(angle - 45) < self.angle_threshold


