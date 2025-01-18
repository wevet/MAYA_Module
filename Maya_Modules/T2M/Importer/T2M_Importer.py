# -*- coding: utf-8 -*-

from typing import List
import numpy as np
import os
from maya import cmds
from maya.api import OpenMaya, OpenMayaAnim
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets, QtCore
from shiboken2 import wrapInstance

# Mayaのメインウィンドウを取得
def get_maya_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


# ジョイントのラベルリスト
JOINT_LABELS = [
    "Hip", "LeftLeg", "RightLeg", "Spine1", "LeftKnee", "RightKnee", "Spine2",
    "LeftFoot", "RightFoot", "Spine3", "LeftToe", "RightToe", "Neck", "LeftShoulder",
    "RightShoulder", "Head", "LeftArm", "RightArm", "LeftElbow", "RightElbow",
    "LeftHand", "RightHand",
]

# キネマティックチェーンの名前、インデックス、カラーを定義
KINE_CHAIN = [
    ("Spine", [0, 3, 6, 9, 12, 15], 1),
    ("LeftLeg", [0, 1, 4, 7, 10], 6),
    ("RightLeg", [0, 2, 5, 8, 11], 13),
    ("LeftArm", [9, 13, 16, 18, 20], 6),
    ("RightArm", [9, 14, 17, 19, 21], 13)
]


def get_locators():
    """
    ジョイントラベルに基づいてlocatorとcurveを取得または作成します。

    Returns:
        tuple: locatorのリストとcurveのリスト
    """
    locators = []
    chains = []

    grp = "loc_grp"
    if not cmds.objExists(grp):
        grp = cmds.createNode("transform", n=grp)

    # 各ジョイントラベルに対してlocatorを作成または取得
    for lbl in JOINT_LABELS:
        loc = 'loc_{}'.format(lbl)
        # オブジェクトが存在しない場合、新しく作成
        if not cmds.objExists(loc):
            loc = cmds.spaceLocator(n=loc)[0]
            cmds.parent(loc, grp, r=False)
        locators.append(loc)

    # キネマティックチェーンに基づいてcurveを作成または取得
    for name, indices, color in KINE_CHAIN:
        crv = 'chain_{}'.format(name)
        if not cmds.objExists(crv):
            p = []
            k = []
            for i in range(len(indices)):
                p.append((0, 0, 0))
                k.append(i)
            crv = cmds.curve(d=1, p=p, k=k, n=crv)
            cmds.parent(crv, grp, r=False)

            crv_shape = cmds.listRelatives(crv, s=True, f=True)[0]
            cmds.setAttr(crv_shape + '.overrideEnabled', True)
            cmds.setAttr(crv_shape + '.overrideColor', color)

            for j, idx in enumerate(indices):
                loc_shape = cmds.listRelatives(locators[idx], s=True, f=True)[0]
                cmds.connectAttr('{}.worldPosition[0]'.format(loc_shape), '{}.controlPoints[{}]'.format(crv_shape, j), f=True)
        chains.append(crv)
    cmds.select(cl=True)
    return locators, chains


def get_trans_animCurve(node: str):
    """
    指定されたノードのtx,ty,tzのanimCurveを取得または作成します。

    Args:
        node (str): ノード名

    Returns:
        list: animCurveのリスト
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


def plot(data: List[List[List[float]]], scale: float = 1.0, fps: int = 30):
    """
    与えられたデータを使用してアニメーションをプロットします。

    Args:
        data (List[List[List[float]]]): アニメーションデータ
        scale (float, optional): スケール値。デフォルトは1.0。

    Returns:
        list: プロットされたlocatorのリスト
    """
    locators, _ = get_locators()

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
    # デフォルトは30FPS
    cmds.currentUnit(t=fps_map.get(fps, "ntsc"))

    # アニメーション設定
    cmds.currentUnit(t="ntsc")
    cmds.playbackOptions(min=1, max=int(frames * 1.5), ast=1, aet=int(frames * 1.5))
    cmds.currentTime(1)

    # animCurveにキーフレームを追加
    for i, loc in enumerate(locators):
        ms_list = OpenMaya.MSelectionList()
        for anim_curve in get_trans_animCurve(loc):
            ms_list.add(anim_curve)

        mfn_curves: List[OpenMayaAnim.MFnAnimCurve] = []
        # MFnAnimCurveを取得
        for j in range(3):
            mfn_curve = OpenMayaAnim.MFnAnimCurve(ms_list.getDependNode(j))
            # 既存のキーフレームを削除
            for k in range(mfn_curve.numKeys):
                mfn_curve.remove(0)
            mfn_curves.append(mfn_curve)

        # frame数ぶんキーフレームを追加
        for frame in range(frames):
            k_time = OpenMaya.MTime(frame + 1, OpenMaya.MTime.kSeconds)  # 時間単位を秒に設定
            k_time.value = frame / fps  # FPS に基づいた時間設定
            for m, k_value in enumerate(data[frame][i]):
                mfn_curves[m].addKey(k_time, k_value * scale)
    return locators


# GUIクラス
class MotionLoaderUI(QtWidgets.QDialog):
    def __init__(self, parent=get_maya_window()):
        super(MotionLoaderUI, self).__init__(parent)
        self.setWindowTitle("Motion Loader")
        self.setMinimumWidth(300)

        self.file_path = ""
        self.scale = 100.0
        self.fps = 30

        self.layout = QtWidgets.QVBoxLayout(self)

        # ファイル選択ボタン
        self.file_btn = QtWidgets.QPushButton("Select Motion File")
        self.file_btn.clicked.connect(self.load_file)
        self.layout.addWidget(self.file_btn)

        # スケール入力
        self.scale_label = QtWidgets.QLabel("Scale:")
        self.layout.addWidget(self.scale_label)
        self.scale_input = QtWidgets.QDoubleSpinBox()
        self.scale_input.setRange(0.1, 1000.0)
        self.scale_input.setValue(self.scale)
        self.layout.addWidget(self.scale_input)

        # FPS設定
        self.fps_label = QtWidgets.QLabel("FPS:")
        self.layout.addWidget(self.fps_label)
        self.fps_input = QtWidgets.QSpinBox()
        self.fps_input.setRange(1, 120)
        self.fps_input.setValue(self.fps)
        self.layout.addWidget(self.fps_input)

        # 実行ボタン
        self.load_btn = QtWidgets.QPushButton("Apply Motion")
        self.load_btn.clicked.connect(self.apply_motion)
        self.layout.addWidget(self.load_btn)


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
        plot(data.tolist()[0], scale=scale, fps=fps)
        cmds.inViewMessage(amg="Motion Applied!", pos="midCenter", fade=True)



def show_main_window():
    global motion_loader_ui
    try:
        motion_loader_ui.close()
    except:
        pass
    motion_loader_ui = MotionLoaderUI()
    motion_loader_ui.show()
    return motion_loader_ui






