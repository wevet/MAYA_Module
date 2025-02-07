# -*- coding: utf-8 -*-

import os
import re
from typing import Optional, List
import numpy as np
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance
import maya.mel as mel
from maya.api import OpenMaya
import maya.OpenMayaUI as omui


def get_maya_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)




class TinyDAG(object):
    """
    Tiny DAG class for storing the hierarchy of the BVH file.
    """
    def __init__(self, obj: str, parent: Optional["TinyDAG"] = None):
        self.obj = obj
        self.__parent = parent

    @property
    def parent(self):
        return self.__parent

    def __str__(self) -> str:
        return str(self.obj)

    def full_path(self) -> str:
        if self.parent is not None:
            return "%s|%s" % (self.parent.full_path(), str(self))
        return str(self.obj)



class AnimationTransfer:
    def __init__(self, locator_prefix="loc_"):
        self.locator_prefix = locator_prefix

        # ジョイントのラベルリスト
        self.JOINT_LABELS = [
            "Hips",
            "LeftLeg", "RightLeg", "Spine1", "LeftKnee", "RightKnee", "Spine2",
            "LeftFoot", "RightFoot", "Spine3", "LeftToe", "RightToe", "Neck", "LeftShoulder",
            "RightShoulder", "Head", "LeftArm", "RightArm", "LeftElbow", "RightElbow",
            "LeftHand", "RightHand",
        ]

        # キネマティックチェーンの名前、インデックス、カラーを定義
        self.KINE_CHAIN = [
            ("Spine", [0, 3, 6, 9, 12, 15], 1),
            ("LeftLeg", [0, 1, 4, 7, 10], 6),
            ("RightLeg", [0, 2, 5, 8, 11], 13),
            ("LeftArm", [9, 13, 16, 18, 20], 6),
            ("RightArm", [9, 14, 17, 19, 21], 13)
        ]

        self.K_NAME_SPACE = "GenerativeAI"
        self.K_SOURCE_CHARACTER = "SourceCharacter"
        self.K_TARGET_CHARACTER = "LTCharacter"


        # ロケータ → ジョイントのマッピング
        self.locator_to_joint_map = {
            "loc_Hips": "Hips",
            "loc_Spine1": "Spine",
            "loc_Spine2": "Spine1",
            "loc_Neck": "Neck",
            "loc_Head": "Head",

            "loc_LeftShoulder": "LeftShoulder",
            "loc_LeftArm": "LeftArm",
            "loc_LeftElbow": "LeftForeArm",
            "loc_LeftHand": "LeftHand",
            "loc_RightShoulder": "RightShoulder",
            "loc_RightArm": "RightArm",
            "loc_RightElbow": "RightForeArm",
            "loc_RightHand": "RightHand",

            "loc_LeftLeg": "LeftUpLeg",
            "loc_LeftKnee": "LeftLeg",
            "loc_LeftFoot": "LeftFoot",
            "loc_LeftToe": "LeftToeBase",
            "loc_RightLeg": "RightUpLeg",
            "loc_RightKnee": "RightLeg",
            "loc_RightFoot": "RightFoot",
            "loc_RightToe": "RightToeBase",
        }

        # 親子関係の定義
        self.joint_hierarchy = {
            "Hips": None,
            "Spine": "Hips",
            "Spine1": "Spine",
            "Spine2": "Spine1",
            "Neck": "Spine2",
            "Head": "Neck",
            "LeftShoulder": "Spine2",
            "LeftArm": "LeftShoulder",
            "LeftForeArm": "LeftArm",
            "LeftHand": "LeftForeArm",
            "RightShoulder": "Spine2",
            "RightArm": "RightShoulder",
            "RightForeArm": "RightArm",
            "RightHand": "RightForeArm",
            "LeftUpLeg": "Hips",
            "LeftLeg": "LeftUpLeg",
            "LeftFoot": "LeftLeg",
            "LeftToeBase": "LeftFoot",
            "RightUpLeg": "Hips",
            "RightLeg": "RightUpLeg",
            "RightFoot": "RightLeg",
            "RightToeBase": "RightFoot",
        }

        self.LT_JOINT_MAPPING = {
            "c_c_1_0": 1,
            "c_c_1_1": 8,
            "c_c_1_2": 23,
            "c_n_1_0": 20,
            "c_head_1_0": 15,
            "l_s_1_0": 18,
            "l_a_1_0": 9,
            "l_a_1_1": 10,
            "l_w_1_0": 11,
            "r_s_1_0": 19,
            "r_a_1_0": 12,
            "r_a_1_1": 13,
            "r_w_1_0": 14,
            "l_l_1_0": 2,
            "l_l_1_1": 3,
            "l_foot_1_0": 4,
            "r_l_1_0": 5,
            "r_l_1_1": 6,
            "r_foot_1_0": 7
        }


    def get_locators(self):
        """
        既存の `locator` はそのまま利用し、ない場合のみ新規作成。
        `loc_grp` のみ `GenerativeAI` ネームスペースに配置し、子要素には適用しない。

        Returns:
            tuple: locatorのリストとcurveのリスト
        """

        # namespace が既に適用されているかチェック
        if not cmds.namespace(exists=self.K_NAME_SPACE):
            cmds.namespace(add=self.K_NAME_SPACE)

        # namespaceの適用を `loc_grp` のみにする
        grp_name = f"{self.K_NAME_SPACE}:loc_grp"

        # ルートの `loc_grp` をチェックし、なければ作成
        if not cmds.objExists(grp_name):
            grp = cmds.createNode("transform", n="loc_grp")
            cmds.rename(grp, grp_name)
        else:
            print("already grp_name : {}".format(grp_name))

        locators = []
        chains = []

        # 各ジョイントラベルに対して `locator` を作成または取得
        for lbl in self.JOINT_LABELS:
            loc_name = f"loc_{lbl}"
            if not cmds.objExists(loc_name):
                loc = cmds.spaceLocator(n=loc_name)[0]
                cmds.parent(loc, grp_name, r=False)
            else:
                pass
            locators.append(loc_name)

        # キネマティックチェーンに基づいて `curve` を作成または取得
        for name, indices, color in self.KINE_CHAIN:
            crv_name = f"chain_{name}"

            # `curve` が存在しない場合のみ作成
            if not cmds.objExists(crv_name):
                p = [(0, 0, 0) for _ in indices]
                k = list(range(len(indices)))
                crv = cmds.curve(d=1, p=p, k=k, n=crv_name)
                cmds.parent(crv, grp_name, r=False)
                crv_shape = cmds.listRelatives(crv, s=True, f=True)[0]
                cmds.setAttr(f"{crv_shape}.overrideEnabled", True)
                cmds.setAttr(f"{crv_shape}.overrideColor", color)
                for j, idx in enumerate(indices):
                    loc_shape = cmds.listRelatives(locators[idx], s=True, f=True)[0]
                    cmds.connectAttr(f"{loc_shape}.worldPosition[0]", f"{crv_shape}.controlPoints[{j}]", f=True)
            chains.append(crv_name)

        # namespace の適用を解除（ルートに戻す）
        cmds.namespace(set=":")
        cmds.select(cl=True)
        return locators, chains


    @staticmethod
    def get_translation_anim_curve(node: str):
        """
        指定されたノードの `translateX`, `translateY`, `translateZ` の `animCurve` を取得または作成する。

        Args:
            node (str): ノード名

        Returns:
            list: animCurve のリスト
        """
        anim_curves = []
        for attr in ['translateX', 'translateY', 'translateZ']:
            attr_name = f'{node}.{attr}'
            anim_curve = cmds.ls(cmds.listConnections(attr_name, s=True, d=False), type="animCurveTL")
            if anim_curve:
                anim_curves.extend(anim_curve)
            else:
                anim_curve = cmds.createNode('animCurveTL')
                cmds.connectAttr(f'{anim_curve}.output', attr_name, f=True)
                anim_curves.append(anim_curve)
        cmds.select(cl=True)
        return anim_curves



    def apply_aim_constraints(self, joints):
        """
        Aim Constraint を使ってジョイントの向きを調整する。
        """
        aim_vector = (1, 0, 0)  # X方向に向ける
        up_vector = (0, 1, 0)  # Y方向を上にする

        for parent, child in self.joint_hierarchy.items():
            if not parent or not child or parent not in joints or child not in joints:
                continue
            cmds.aimConstraint(joints[child], joints[parent], aimVector=aim_vector, upVector=up_vector, worldUpType="vector", worldUpVector=up_vector)
        print("✅ Aim Constraints Applied!")


    @staticmethod
    def remove_constraints(joints):
        """
        すべてのジョイントのコンストレインを削除する
        """
        for joint in joints:
            constraints = cmds.listRelatives(joint, type=["pointConstraint", "orientConstraint", "aimConstraint"]) or []
            for constraint in constraints:
                cmds.delete(constraint)
        print("✅ 全コンストレイン削除完了")


    @staticmethod
    def setup_ik_controllers():
        """
        IK Handle をセットアップし、適切な Locator にアタッチする
        既にある場合は再作成しない
        """

        # **スケルトンのルート取得**
        skeleton_root = "RetargetSkeleton_grp"
        if not cmds.objExists(skeleton_root):
            cmds.warning("⚠ Not valid skeleton: `RetargetSkeleton_grp` が見つかりません！")
            return

        # **IK Handle のターゲットリスト**
        ik_targets = {
            "ik_LeftLeg": ("LeftUpLeg", "LeftFoot", "loc_LeftFoot"),
            "ik_RightLeg": ("RightUpLeg", "RightFoot", "loc_RightFoot"),
            "ik_LeftArm": ("LeftArm", "LeftHand", "loc_LeftHand"),
            "ik_RightArm": ("RightArm", "RightHand", "loc_RightHand")
        }

        # **既存の IK Handle がある場合はスキップ**
        for ik_handle, (start_joint, end_joint, _) in ik_targets.items():
            if cmds.objExists(ik_handle):
                print(f"⚠ `{ik_handle}` は既に存在します。スキップします。")
                continue

            # **IK Handle を作成**
            ik = cmds.ikHandle(n=ik_handle, sj=start_joint, ee=end_joint, sol="ikRPsolver")[0]
            print(f"✅ IK Handle `{ik_handle}` を作成しました！")
        print("🎉 All IK Handles have been set up successfully!")


    def apply_constraints_to_ik_controllers(self):
        """
        IK Handle を Joint ではなく Locator にコンストレイントし、
        さらに、腰や胸などの向きを aimConstraint で補正する。
        すべての Locator に Primitive を適用し、視覚的にわかりやすくする。
        IK Handle を `loc_grp` の下に移動し、Shape ノードのロックを解除。
        """

        # **Locator グループのルート取得**
        loc_root = "GenerativeAI:loc_grp"
        if not cmds.objExists(loc_root):
            cmds.warning("⚠ Locator グループが見つかりません！")
            return

        self.setup_ik_controllers()

        # **IK Handle の取得**
        ik_handles = {
            "ik_LeftLeg": "loc_LeftFoot",
            "ik_RightLeg": "loc_RightFoot",
            "ik_LeftArm": "loc_LeftHand",
            "ik_RightArm": "loc_RightHand"
        }

        constraints = []

        for ik_handle, loc_name in ik_handles.items():
            loc_path = f"{loc_root}|{loc_name}"

            if not cmds.objExists(loc_path):
                cmds.warning(f"⚠ `{loc_path}` が見つかりません！")
                continue

            if not cmds.objExists(ik_handle):
                cmds.warning(f"⚠ `{ik_handle}` が見つかりません！")
                continue

            # **IK Handle を `loc_grp` の下に移動（既に子オブジェクトでない場合のみ）**
            current_parent = cmds.listRelatives(ik_handle, parent=True)
            if not current_parent or current_parent[0] != loc_root:
                try:
                    cmds.parent(ik_handle, loc_root)
                    print(f"✅ Moved `{ik_handle}` under `{loc_root}`")
                except RuntimeError:
                    cmds.warning(f"⚠ `{ik_handle}` の親子関係の変更に失敗しました！")

            # **IK Handle を Locator にコンストレイント**
            if not cmds.listRelatives(ik_handle, type="pointConstraint"):
                pc = cmds.pointConstraint(loc_path, ik_handle, mo=True)[0]
                constraints.append(pc)
                print(f"✅ Applied PointConstraint: {loc_path} → {ik_handle}")

        # **上半身の Aim Constraint 設定**
        aim_constraints = {
            "Spine": ["loc_Hips", "loc_Spine1", "loc_Spine2"],
            "Neck": ["loc_Spine3", "loc_Neck", "loc_Head"]
        }

        for joint, locators in aim_constraints.items():
            if len(locators) < 3:
                cmds.warning(f"⚠ `{joint}` の Aim Constraint に必要な Locator が不足しています")
                continue

            loc_aim, loc_up, loc_world_up = [f"{loc_root}|{loc}" for loc in locators]

            if not cmds.objExists(loc_aim) or not cmds.objExists(loc_up) or not cmds.objExists(loc_world_up):
                cmds.warning(f"⚠ `{joint}` に必要な Locator が不足しています")
                continue

            if not cmds.listRelatives(joint, type="aimConstraint"):
                aim_constraint = cmds.aimConstraint(
                    loc_aim, joint, mo=True,
                    aimVector=(1, 0, 0), upVector=(0, 1, 0),
                    worldUpType="object", worldUpObject=loc_world_up
                )[0]
                constraints.append(aim_constraint)
                print(f"✅ Applied AimConstraint: {joint} → {loc_aim}")

            list_constraints = cmds.listRelatives(joint, type="aimConstraint")
            print(f"list => {list_constraints}")

        print("🎉 IK Handle, AimConstraint, Primitive の適用が完了しました！")


    @staticmethod
    def get_existing_hik_characters():
        """
        シーン内の HumanIK キャラクターを取得する
        """
        hik_chars = cmds.ls(type="HIKCharacterNode")
        return hik_chars if hik_chars else []


    """
    retarget元のhumanik定義を行う
    """
    def setup_humanik_source(self):

        # root joint
        # f"{self.K_NAMESPACE}:XXXX_grp

        mel.eval('HIKCharacterControlsTool ;')
        mel.eval('hikCreateDefinition();')

        existing_characters = self.get_existing_hik_characters()

        if self.K_SOURCE_CHARACTER in existing_characters:
            print(f"⚠ 既存のキャラクター `{self.K_SOURCE_CHARACTER}` を削除します")
            mel.eval(f'hikDeleteCharacter("{self.K_SOURCE_CHARACTER}")')

        # **新しいキャラクターを作成**
        mel.eval(f'hikCreateCharacter("{self.K_SOURCE_CHARACTER}")')

        # **Namespace 配下の `_grp` を検索**
        root_candidates = cmds.ls(f"{self.K_NAME_SPACE}:*_grp", long=True)
        if not root_candidates:
            cmds.warning(f"Namespace `{self.K_NAME_SPACE}` 内に適切なグループ (`*_grp`) が見つかりません！")
            return

        # **最初に見つかった `_grp` をルートジョイントとする**
        root_joint_path = root_candidates[0]
        print(f"✅ ルートジョイントを `{root_joint_path}` に設定")

        # **ルート配下のジョイントを取得**
        joints = cmds.listRelatives(root_joint_path, allDescendents=True, type="joint", fullPath=True)
        if not joints:
            cmds.warning(f"⚠ `{root_joint_path}` 配下にジョイントが見つかりません！")
            return

        # **HumanIK にジョイントをマッピング**
        mapping = {
            "Hips": 1,
            "LowerBack": 8,
            "Spine1": 23,
            "Spine2": 24,
            "Neck": 20,
            "Neck1": 15,
            "LeftShoulder": 18,
            "LeftArm": 9,
            "LeftForeArm": 10,
            "LeftHand": 11,
            "RightShoulder": 19,
            "RightArm": 12,
            "RightForeArm": 13,
            "RightHand": 14,
            "LHipJoint": 2,
            "LeftLeg": 3,
            "LeftFoot": 4,
            "RHipJoint": 5,
            "RightLeg": 6,
            "RightFoot": 7
        }

        for joint_name, hik_id in mapping.items():
            # **ジョイントのフルパスを取得**
            joint_path = [j for j in joints if j.endswith(f"|{joint_name}")]
            if not joint_path:
                cmds.warning(f"⚠ ジョイント `{joint_name}` がシーンに存在しません！")
                continue  # 見つからない場合はスキップ

            # **HumanIK にジョイントを登録**
            print(f"✅ `{joint_name}` のパス: {joint_path[0]}")
            mel.eval(f'setCharacterObject("{joint_path[0]}", "{self.K_SOURCE_CHARACTER}", {hik_id}, 0);')

        # **キャラクターをアクティブにする**
        mel.eval(f'hikSetCurrentCharacter("{self.K_SOURCE_CHARACTER}")')

        # **コントロールリグを作成**
        mel.eval('hikCreateControlRig;')
        mel.eval('modelEditor -e -joints true modelPanel4;')

        print(f"🎉 HumanIK Definition '{self.K_SOURCE_CHARACTER}' が設定されました！")


    """
    LT jointのhumanik定義を行う
    """
    def setup_humanik_target(self):
        """
        既存のジョイント構造 (LT_JOINT_MAPPING) に基づいて
        ターゲットキャラクターの HumanIK セットアップを行う。
        """

        # **HumanIK ウィンドウを開く**
        mel.eval('HIKCharacterControlsTool ;')
        mel.eval('hikCreateDefinition();')

        existing_characters = self.get_existing_hik_characters()

        # **既存の `LTCharacter` がある場合は更新、それ以外は作成**
        if self.K_TARGET_CHARACTER in existing_characters:
            print(f"✅ 既存の HumanIK キャラクター `{self.K_TARGET_CHARACTER}` が見つかりました。更新を行います。")

            # **コントロールリグがある場合は削除**
            try:
                mel.eval(f'hikDeleteControlRig("{self.K_TARGET_CHARACTER}")')
                print(f"⚠ `{self.K_TARGET_CHARACTER}` のコントロールリグを削除しました。")
            except RuntimeError as e:
                print(f"⚠ コントロールリグの削除に失敗: {e}")

            # **既存キャラクターをアクティブにする**
            mel.eval(f'hikSetCurrentCharacter("{self.K_TARGET_CHARACTER}")')

        else:
            print(f"⚠ `{self.K_TARGET_CHARACTER}` が存在しないため、新規作成します。")
            mel.eval(f'hikCreateCharacter("{self.K_TARGET_CHARACTER}")')

        # **ターゲットジョイントを HumanIK に登録**
        for joint_name, hik_id in self.LT_JOINT_MAPPING.items():
            joint_path = cmds.ls(joint_name, long=True)
            if not joint_path:
                cmds.warning(f"⚠ ジョイント `{joint_name}` がシーンに存在しません！")
                continue
            print(f"✅ `{joint_name}` のパス: {joint_path[0]}")

            try:
                mel.eval(f'setCharacterObject("{joint_path[0]}", "{self.K_TARGET_CHARACTER}", {hik_id}, 0);')
            except RuntimeError as e:
                print(f"❌ `setCharacterObject` エラー: {e}")
                continue

        # **コントロールリグの再作成**
        mel.eval('hikCreateControlRig;')
        mel.eval('modelEditor -e -joints true modelPanel4;')
        print(f"🎉 HumanIK Target Character `{self.K_TARGET_CHARACTER}` のセットアップが完了しました！")


    def plot(self, data: List[List[List[float]]], scale: float = 1.0, fps: int = 30):
        """
        既存の `locator` にアニメーションを適用（新規作成せずに上書き）。
        `KINE_CHAIN` の情報も維持。

        Args:
            data (List[List[List[float]]]): アニメーションデータ
            scale (float, optional): スケール値。デフォルトは1.0。
            fps (int, optional): フレームレート。デフォルトは30。

        Returns:
            list: 更新された `locator` のリスト
        """
        locators, _ = self.get_locators()

        frames = len(data)
        print("frames: {} / points: {} / params: {}".format(frames, len(data[0]), len(data[0][0])))

        # FPS に基づいた Maya の時間単位を設定
        fps_map = {
            24: "film",
            25: "pal",
            30: "ntsc",
            48: "show",
            50: "palf",
            60: "ntscf"
        }

        cmds.currentUnit(t=fps_map.get(fps, "ntsc"))

        cmds.currentUnit(t="ntsc")
        cmds.playbackOptions(min=1, max=int(frames * 1.5), ast=1, aet=int(frames * 1.5))
        cmds.currentTime(1)

        # **Locator にキーを適用**
        for i, obj in enumerate(locators):
            ms_list = OpenMaya.MSelectionList()
            for anim_curve in self.get_translation_anim_curve(obj):
                ms_list.add(anim_curve)

            mfn_curves: List[OpenMayaAnim.MFnAnimCurve] = []
            for j in range(3):
                mfn_curve = OpenMayaAnim.MFnAnimCurve(ms_list.getDependNode(j))
                # 既存のキーフレームを削除
                for k in range(mfn_curve.numKeys):
                    mfn_curve.remove(0)
                mfn_curves.append(mfn_curve)

            for frame in range(frames):
                k_time = OpenMaya.MTime(frame + 1, OpenMaya.MTime.kSeconds)  # 時間単位を秒に設定
                k_time.value = frame / fps  # FPS に基づいた時間設定
                for m, k_value in enumerate(data[frame][i]):
                    mfn_curves[m].addKey(k_time, k_value * scale)

        return locators



# GUIクラス
class MotionToolKit(QtWidgets.QDialog):

    WINDOW_TITLE = "T2M Motion ToolKit"
    MODULE_VERSION = "1.0"

    def __init__(self, parent=get_maya_window()):
        super(MotionToolKit, self).__init__(parent)
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(360, 360)

        self.animation_transfer = AnimationTransfer()
        self.default_style = "background-color: #34d8ed; color: black"
        self.model_style = "background-color: #ff8080; color: black;"

        self.setStyleSheet('background-color:#262f38;')

        self.K_SPACE_RE = re.compile(r"\s+")

        # This maps the BVH naming convention to Maya
        self.K_TRANSLATION_DICT = {
            "Xposition": "translateX",
            "Yposition": "translateY",
            "Zposition": "translateZ",
            "Xrotation": "rotateX",
            "Yrotation": "rotateY",
            "Zrotation": "rotateZ"
        }

        self.file_path = ""
        self.scale = 100.0
        self.fps = 30
        self.filename = ""
        self.channels = []
        self.imported_joints = []
        self.root_node = None
        self.text_field = ""

        self.layout = QtWidgets.QVBoxLayout(self)

        self.scale_input = QtWidgets.QDoubleSpinBox()
        self.scale_input.setRange(0.01, 1000.0)
        self.scale_input.setValue(self.scale)
        self.layout.addWidget(QtWidgets.QLabel("Rig scale"))
        self.layout.addWidget(self.scale_input)

        self.frame_input = QtWidgets.QSpinBox()
        self.frame_input.setRange(0, 1000)
        self.frame_input.setValue(0)
        #self.layout.addWidget(QtWidgets.QLabel("Frame offset"))
        #self.layout.addWidget(self.frame_input)

        self.rotation_order = QtWidgets.QComboBox()
        self.rotation_order.addItems(["XYZ", "YZX", "ZXY", "XZY", "YXZ", "ZYX"])
        self.layout.addWidget(QtWidgets.QLabel("Rotation Order"))
        self.layout.addWidget(self.rotation_order)

        # **Joint Radius 設定**
        self.joint_radius_input = QtWidgets.QDoubleSpinBox()
        self.joint_radius_input.setRange(0.01, 10.0)
        self.joint_radius_input.setValue(0.1)  # デフォルト値
        self.joint_radius_input.setSingleStep(0.01)
        #self.joint_radius_input.valueChanged.connect(self._update_joint_radius_callback)
        #self.layout.addWidget(QtWidgets.QLabel("Joint Radius"))
        #self.layout.addWidget(self.joint_radius_input)

        self.layout.addWidget(QtWidgets.QLabel("Skeleton Targeting (Select the hips)"))
        self.textfield = QtWidgets.QLineEdit()

        input_button_layout = QtWidgets.QHBoxLayout()

        self.select_button = QtWidgets.QPushButton("Select/Clear")
        self.select_button.clicked.connect(self._toggle_select_root_joint_callback)
        #self.select_button.setStyleSheet(self.model_style)
        input_button_layout.addWidget(self.textfield)
        input_button_layout.addWidget(self.select_button)

        self.layout.addLayout(input_button_layout)

        self.skeleton_button = QtWidgets.QPushButton("Import SKeleton")
        self.skeleton_button.clicked.connect(self._import_template_with_name_space)
        self.skeleton_button.setStyleSheet(self.default_style)
        self.layout.addWidget(self.skeleton_button)

        self.import_button = QtWidgets.QPushButton("Import Motion")
        self.import_button.clicked.connect(self._on_select_file_callback)
        self.import_button.setStyleSheet(self.model_style)
        self.layout.addWidget(self.import_button)

        # ファイル選択ボタン
        # self.file_btn = QtWidgets.QPushButton("Select Motion File")
        # self.file_btn.clicked.connect(self.load_file)
        # self.layout.addWidget(self.file_btn)

        # スケール入力
        # self.scale_input = QtWidgets.QDoubleSpinBox()
        # self.scale_input.setRange(0.1, 1000.0)
        # self.scale_input.setValue(100.0)
        # self.layout.addWidget(self.scale_input)

        # FPS設定
        # self.fps_input = QtWidgets.QSpinBox()
        # self.fps_input.setRange(1, 120)
        # self.fps_input.setValue(30)
        # self.layout.addWidget(self.fps_input)

        buttom_button_layout = QtWidgets.QHBoxLayout()

        # motion fileのhik setup
        self.humanik_source_button = QtWidgets.QPushButton("IK Definition Source")
        self.humanik_source_button.clicked.connect(self.animation_transfer.setup_humanik_source)
        self.humanik_source_button.setStyleSheet(self.default_style)
        buttom_button_layout.addWidget(self.humanik_source_button)

        # target jointのsetup
        self.humanik_target_button = QtWidgets.QPushButton("IK Definition Target")
        self.humanik_target_button.clicked.connect(self.animation_transfer.setup_humanik_target)
        self.humanik_target_button.setStyleSheet(self.default_style)
        buttom_button_layout.addWidget(self.humanik_target_button)
        self.layout.addLayout(buttom_button_layout)


    def _update_joint_radius_callback(self):
        """
        GUIからの変更に応じてインポートされたジョイントの半径を更新
        """
        #radius = self.joint_radius_input.value()
        radius = 0.1
        for joint in self.imported_joints:
            if cmds.objExists(joint):
                cmds.setAttr(f"{joint}.radius", radius)
        print(f"BVHインポートジョイントの半径を {radius} に設定")


    def _import_template_with_name_space(self):
        """
        preset/template.bvh を Maya にインポートし、ネームスペースを付与した上で `_read_bvh_callback` に渡す。
        """
        # スクリプトの実行ディレクトリを取得し、相対パスを解決
        script_dir = os.path.dirname(os.path.abspath(__file__))
        #template_path = os.path.join(script_dir, "preset", "template.bvh")
        template_path = os.path.join(script_dir, "preset", "template_new.bvh")

        # ファイルが存在するか確認
        if not os.path.exists(template_path):
            cmds.warning(f"BVHテンプレートファイルが見つかりません: {template_path}")
            return

        self._filename = template_path

        ns = self.animation_transfer.K_NAME_SPACE
        if not cmds.namespace(exists=ns):
            cmds.namespace(add=ns)

        self._read_bvh_callback()
        self._clear_animation()
        self._reset_pose_callback()
        #self._update_joint_radius_callback()


    def _on_select_file_callback(self):
        """
        import bvh file
        """
        file_filter = "Motion Capture (*.bvh)"
        result = cmds.fileDialog2(fileFilter=file_filter, dialogStyle=1, fm=1)

        if not result:
            return

        self._filename = result[0]
        self._read_bvh_callback()


    def _read_bvh_callback(self):
        """
        BVHファイルを読み込み、ジョイントの作成と半径設定、アニメーションキーの更新、および終了フレームの更新。
        """
        safe_close = False  # End Site 処理用のフラグ
        motion = False  # アニメーションパート開始フラグ
        self._channels = []
        self.imported_joints = []

        rig_scale = self.scale_input.value()
        #frame = self.frame_input.value()
        frame = 0
        rot_order = self.rotation_order.currentIndex()
        final_frame = frame

        ns = self.animation_transfer.K_NAME_SPACE
        base_group_name = f"{ns}:template_grp"

        with open(self._filename) as f:
            # BVHファイルが有効かチェック
            if not f.readline().startswith("HIERARCHY"):
                cmds.error("No valid .bvh file selected.")
                return False

            if not cmds.objExists(base_group_name):
                grp = cmds.group(em=True, name=base_group_name)
                cmds.setAttr("%s.scale" % grp, rig_scale, rig_scale, rig_scale)
                my_parent = TinyDAG(grp, None)
            else:
                my_parent = TinyDAG(cmds.select(base_group_name), None)

            existing_joints = cmds.listRelatives(base_group_name, allDescendents=True, type="joint", fullPath=True) or []

            min_time = cmds.playbackOptions(q=True, minTime=True)
            max_time = cmds.playbackOptions(q=True, maxTime=True)

            for joint in existing_joints:
                for attr in ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]:
                    cmds.cutKey(joint, attribute=attr, time=(min_time, max_time))
            print(f"🗑 既存のアニメーションキーを削除しました ({min_time} - {max_time})")

            for line in f:
                # タブをスペースに変換
                line = line.replace("\t", " ")

                if not motion:
                    if line.startswith("ROOT"):
                        root_name = line[5:].strip()

                        if self.root_node:
                            my_parent = TinyDAG(str(self.root_node), None)
                        else:
                            my_parent = TinyDAG(root_name, my_parent)
                            self.root_node = my_parent
                            self.textfield.setText(my_parent.full_path())

                    elif "JOINT" in line:
                        jnt = self.K_SPACE_RE.split(line.strip())
                        if my_parent:
                            joint_name = jnt[1]
                            my_parent = TinyDAG(joint_name, my_parent)

                            # **Maya上にジョイントを作成**
                            if cmds.objExists(my_parent.full_path()):
                                print(f"DEBUG: Existing Joint found - {my_parent.full_path()}")
                            else:
                                # **親が存在すれば新規作成**
                                if my_parent.parent and cmds.objExists(my_parent.parent.full_path()):
                                    # 親ノードを選択
                                    cmds.select(my_parent.parent.full_path())
                                    created_joint = cmds.joint(name=joint_name, p=(0, 0, 0))
                                    self.imported_joints.append(created_joint)
                                    print(f"DEBUG: Joint created in Maya - {created_joint}")
                                else:
                                    print(f"WARNING: Parent {my_parent.parent.full_path()} does not exist for {joint_name}")
                        else:
                            print(f"WARNING: my_parent is None while processing JOINT - {jnt[1]}")

                    elif "End Site" in line:
                        # End Site の処理開始
                        safe_close = True

                    elif "}" in line:
                        if safe_close:
                            safe_close = False
                            continue
                        my_parent = my_parent.parent if my_parent else None
                        if my_parent and cmds.objExists(my_parent.full_path()):
                            cmds.select(my_parent.full_path())

                    elif "CHANNELS" in line:
                        chan = line.strip().split()
                        for i in range(int(chan[1])):
                            if my_parent:
                                self._channels.append(f"{my_parent.full_path()}.{self.K_TRANSLATION_DICT[chan[2 + i]]}")
                            else:
                                print(f"WARNING: my_parent is None when setting channels for {chan[2 + i]}")

                    elif "OFFSET" in line:
                        offset = line.strip().split()
                        jnt_name = str(my_parent)

                        if safe_close:
                            jnt_name += "_tip"

                        if my_parent:
                            # **既存ジョイントがあるなら更新**
                            if cmds.objExists(my_parent.full_path()):
                                jnt = my_parent.full_path()
                                cmds.setAttr(jnt + ".translate", float(offset[1]), float(offset[2]), float(offset[3]))
                                print(f"DEBUG: Updated Joint Position - {jnt}")
                            else:
                                # **親ノードがない場合（Hips の場合）、ROOTとして作成**
                                if my_parent.parent and cmds.objExists(my_parent.parent.full_path()):
                                    cmds.select(my_parent.parent.full_path())
                                    jnt = cmds.joint(name=jnt_name, p=(0, 0, 0))
                                else:
                                    cmds.select(clear=True)
                                    jnt = cmds.joint(name=jnt_name, p=(float(offset[1]), float(offset[2]), float(offset[3])))

                                self.imported_joints.append(jnt)
                                print(f"DEBUG: Offset Joint created in Maya - {jnt}")

                            cmds.setAttr(jnt + ".rotateOrder", rot_order)
                            #cmds.setAttr(jnt + ".translate", float(offset[1]), float(offset[2]), float(offset[3]))
                        else:
                            print(f"WARNING: my_parent is None when setting OFFSET for {jnt_name}")

                    elif "MOTION" in line:
                        motion = True

                else:
                    if "Frame" not in line:
                        data = self.K_SPACE_RE.split(line.strip())
                        for index, value in enumerate(data):
                            if index < len(self._channels):
                                cmds.setKeyframe(self._channels[index], time=frame, value=float(value))
                            else:
                                print(f"WARNING: Index {index} out of range for channels.")
                        # 最後のフレームを記録
                        final_frame = frame
                        frame += 1

        cmds.playbackOptions(minTime=1, maxTime=final_frame, animationStartTime=1, animationEndTime=final_frame)
        cmds.currentTime(1)

        #self._reset_pose_callback()


    def _toggle_select_root_joint_callback(self):
        selection = cmds.ls(sl=True, type="joint", l=True)
        if not selection or selection[0] == self.root_node:
            # 何も選択していない or すでに選択中のジョイントを再選択 → 解除
            self.root_node = None
            self.textfield.setText("")
            #self.reload_button.setEnabled(False)
        else:
            # 新しく選択されたジョイントをセット
            self.root_node = selection[0]
            self.textfield.setText(self.root_node)
            #self.reload_button.setEnabled(True)


    def _reset_pose_callback(self):
        """
        選択された Namespace のジョイントを -10f にキーを打ち、T-Pose にする
        """
        ns = self.animation_transfer.K_NAME_SPACE
        root_candidates = cmds.ls(f"{ns}:*_grp", long=True)

        if not root_candidates:
            cmds.warning(f"Namespace `{ns}` 内に適切なグループ (`*_grp`) が見つかりません！")
            return

        root_joint_path = root_candidates[0]
        print(f"✅ ルートジョイントを `{root_joint_path}` に設定")

        joints = cmds.listRelatives(root_joint_path, allDescendents=True, type="joint", fullPath=True)
        if not joints:
            cmds.warning(f"⚠ `{root_joint_path}` 配下にジョイントが見つかりません！")
            return

        cmds.currentTime(-10, edit=True)

        for joint in joints:
            cmds.setKeyframe(joint, attribute="rotateX", value=0)
            cmds.setKeyframe(joint, attribute="rotateY", value=0)
            cmds.setKeyframe(joint, attribute="rotateZ", value=0)
        print(f"T-Pose を -10f に設定しました！")


    def _clear_animation(self):
        if self.root_node is None:
            cmds.error("Could not find root node to clear animation.")
            return

        # Select hierarchy
        cmds.select(str(self.root_node), hi=True)
        nodes = cmds.ls(sl=True)

        trans_attrs = ["translateX", "translateY", "translateZ"]
        rot_attrs = ["rotateX", "rotateY", "rotateZ"]
        for node in nodes:
            for attr in trans_attrs + rot_attrs:
                # Delete input connections
                connections = cmds.listConnections("%s.%s" % (node, attr), s=True, d=False)
                if connections is not None:
                    cmds.delete(connections)
            for attr in rot_attrs:
                # Reset rotation
                cmds.setAttr("%s.%s" % (node, attr), 0)



    def load_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Motion File", "", "NumPy Files (*.npy)")
        if file_path:
            self.file_path = file_path
            self.file_btn.setText(os.path.basename(file_path))


    def apply_motion(self):
        if not self.file_path:
            cmds.warning("Please select a motion file first!")
            return
        data = np.load(self.file_path)
        scale = self.scale_input.value()
        fps = self.fps_input.value()
        self.animation_transfer.plot(data.tolist()[0], scale=scale, fps=fps)
        cmds.inViewMessage(amg="Motion Applied!", pos="midCenter", fade=True)



def show_main_window():
    global motion_toolkit_ui
    try:
        motion_toolkit_ui.close()
    except:
        pass
    motion_toolkit_ui = MotionToolKit()
    motion_toolkit_ui.show()
    return motion_toolkit_ui


