# -*- coding: utf-8 -*-

import os
import stat
import pymel.core as pm
from maya import cmds, OpenMaya, OpenMayaAnim
import maya.mel as mel



class Batch_Job:

    SOURCE_TRANSFORM_ATTRIBUTE = ["tx", "ty", "tz", "rx", "ry", "rz"]

    def __init__(self):
        self.dummy_key_frame = -50
        self.start_frame = 0
        self.anim_curves = []
        self.controllers = []
        self.all_joints = []
        self.pole_legs = []
        self.has_native_os = False

    @staticmethod
    def _get_scene_name():
        return os.path.splitext(os.path.basename(cmds.file(q=True, sn=True)))[0]

    @staticmethod
    def _get_all_joints():
        """
        joints = cmds.ls(type="joint")
        character_root_list = [joint for joint in joints if ":root" in joint]
        pm.select(character_root_list)
        selected = pm.selected()
        children_joints = cmds.listRelatives(allDescendants=True, type='joint')
        """
        children_joints = cmds.ls(type="joint")
        return children_joints

    @staticmethod
    def _get_frame_range():
        start = int(pm.playbackOptions(q=True, min=True))
        end = int(pm.playbackOptions(q=True, max=True))
        return start, end

    def _get_bake_attributes(self, objects):
        result = []
        if not objects:
            raise ValueError("No objects specified")
        connections = cmds.listConnections(
            objects,
            plugs=True,
            source=True,
            connections=True,
            destination=False
        ) or []
        for dst_obj, src_obj in zip(connections[::2], connections[1::2]):
            nodeType = cmds.nodeType(src_obj)
            if not nodeType.startswith("animCurve"):
                result.append(dst_obj)
        return result

    def _bake_connected(self, objects, time, sample_by=1):
        bake_attributes = self._get_bake_attributes(objects)
        if bake_attributes:
            cmds.bakeResults(
                bake_attributes,
                time=time,
                shape=True,
                simulation=True,
                sampleBy=sample_by,
                controlPoints=False,
                minimizeRotation=True,
                bakeOnOverrideLayer=False,
                preserveOutsideKeys=False,
                sparseAnimCurveBake=False,
                disableImplicitControl=True,
                removeBakedAttributeFromLayer=False,
            )
        else:
            print("Cannot find any connection to bake!")

    # anim curve objectを取得
    def _get_controllers(self):
        # Finding all the nurb curves to get the shape node on the anim_curves
        nurbs_curve_list = cmds.ls(type="nurbsCurve")
        nurbs_surface_list = cmds.ls(type="nurbsSurface")
        if nurbs_surface_list:
            for curve in nurbs_surface_list:
                nurbs_curve_list.append(curve)

        shape_list = nurbs_curve_list
        self.anim_curves = []
        self.controllers = []

        # get controllers
        for shape in shape_list:
            parent = cmds.listRelatives(shape, parent=True)[0]
            # 同じ名前のコントローラが複数あるかどうかを確認する
            dub_names = cmds.ls(parent, exactType="transform")
            for ctrl in dub_names:
                if not ctrl in self.controllers:
                    # コントローラーがキーが使える属性を取得したかどうかを確認する、そうでなければ、コントロールをミラーリングする理由はない
                    if cmds.listAttr(ctrl, keyable=True):
                        self.controllers.append(ctrl)
                        if str(ctrl).find("PoleLeg") > -1:
                            print("found leg => {}".format(ctrl))
                            self.pole_legs.append(ctrl)

        # get anim curves
        anim_curves = cmds.ls(type='animCurve')
        for anim in anim_curves:
            # 全てのキーを取得し、順番にソートする。キーがない場合に備えて `or []` を使っているが、これは `sort` がクラッシュしないように、代わりに空のリストを使う。
            all_keys = sorted(cmds.keyframe(anim, q=True) or [])
            # 少なくとも1つのキーがあるかどうかを確認する。
            if all_keys:
                self.anim_curves.append(anim)
        pass

    # -50fにkeyframeを打つ（値は0）
    def _build_key_frame(self):
        self._get_controllers()
        self.start_frame = cmds.currentTime(q=True)
        cmds.currentTime(self.dummy_key_frame)
        for ctrl in self.controllers:
            attributes = cmds.listAttr(ctrl, keyable=True, unlocked=True)
            if attributes:
                for attr in attributes:
                    attr_obj = "{}.{}".format(ctrl, attr)
                    lock_check = cmds.getAttr(attr_obj, lock=True)
                    if lock_check is True:
                        cmds.setAttr(attr_obj, lock=0)
                        print("unlock attr => {}.{}".format(ctrl, attr))

            for value in self.SOURCE_TRANSFORM_ATTRIBUTE:
                attr_value = "{}.{}".format(ctrl, value)
                cmds.setKeyframe(attr_value, v=0, t=self.dummy_key_frame)

        #再生時間を変更する
        cmds.playbackOptions(edit=1, minTime=self.dummy_key_frame)
        cmds.currentTime(self.dummy_key_frame)
        pass

    @staticmethod
    def _set_fbx_options(*args, **kwargs):
        mel.eval('FBXResetExport;')
        # ・・・エキスポート設定をリセットします。
        mel.eval('FBXProperty "Export|IncludeGrp|Animation" -v 1')
        # ・・・fbxエキスポートオプションの、アニメーション設定の部分です。
        mel.eval('FBXExportBakeComplexAnimation -v 1;')
        # ・・・のコマンドは、アニメーションのベイク処理（Bake Animation）オプションに相当するスクリプトです。
        mel.eval('FBXExportShapes -v 0;')
        # ・・・シェイプを出力するかどうか
        mel.eval('FBXExportSkins -v 0;')
        # ・・・スキンをエキスポートするかどうか
        mel.eval('FBXExportSmoothMesh -v 0;')
        # ・・・スムースメッシュをエキスポートするかどうか
        mel.eval('FBXExportSmoothingGroups -v 0;')
        # ・・・スムージンググループをエキスポートするかどうか
        mel.eval('FBXExportUseSceneName -v 1;')
        # ・・・アニメーションクリップ名にシーン名を使うかどうか（使わないと、Take1に）
        mel.eval('FBXExportCameras -v 0;')
        # ・・・カメラをエキスポートするかどうか
        mel.eval('FBXExportLights -v 0;')
        # ・・・ライトをエキスポートするかどうか
        mel.eval('FBXExportInAscii -v 0;')
        # ・・・アスキー形式にするかどうか
        mel.eval('FBXExportInputConnections -v 1;')
        # ・・・コネクションを含めるかどうか
        mel.eval('FBXExportApplyConstantKeyReducer -v 0;')
        # ・・・アニメーションで単一のキーを削除するかどうか
        mel.eval('FBXExportEmbeddedTextures -v 0;')
        # ・・・テクスチャを内包するかどうか

    def _export_fbx(self, file_path):
        """
        mel.eval('FBXResetExport')
        mel.eval('FBXExportBakeComplexAnimation -v 1')
        mel.eval('FBXExportInAscii -v 1')
        """

        # https://tm8r.hateblo.jp/entry/2017/01/06/101025
        #cmds.FBXExport('-f', file_path, '-s', True)

        """
        # @TODO
        #  1の場合はOSネイティブ
        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            mel.eval('savePrefsChanges;')
        """

        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            self.has_native_os = True
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            print("modify FileDialogStyle")

        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        mel.eval('FBXResetExport')
        mel.eval('FBXExportBakeComplexAnimation -v 1')
        mel.eval('FBXExportInAscii -v 1')
        mel.eval('FBXExport -f "' + file_path + '" -s')
        #cmds.file(file_path, force=True, exportSelected=True, type="FBX export")
        pass

    def start(self):
        asset_file_path = cmds.file(q=True, sn=True)
        filename = os.path.basename(asset_file_path)  # sample.ma
        self._build_key_frame()
        scene_name = self._get_scene_name()

        base_directory = asset_file_path.split(filename)[-2]
        output_directory = base_directory + "Exported/"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        file_path = os.path.join(output_directory, "{}.fbx".format(scene_name))

        print("BAKE STARTED => {}".format(file_path))
        self.all_joints = []
        self.all_joints = self._get_all_joints()
        self.all_joints.extend(self.pole_legs)
        cmds.select(self.all_joints, r=True)
        for joint in self.all_joints:
            print("find joint => {}".format(joint))
        # -50fから最終fまで選択しBake
        time_range = self._get_frame_range()
        self._bake_connected(self.all_joints, time_range)
        print("BAKE FINISHED => {}".format(file_path))

        print("EXPORT STARTED => {}".format(file_path))
        self._export_fbx(file_path)
        print("EXPORT FINISHED => {}".format(file_path))

        if self.has_native_os is True:
            mel.eval('optionVar -iv FileDialogStyle 1 ;')
            print("revert native os")
        pass


if __name__ == "__main__":
    """
    file_path_list = cmds.fileDialog2(fileFilter="*.ma", dialogStyle=2, okc="Accept", fm=4)
    if file_path_list:
        for file_path in file_path_list:
            cmds.file(file_path, o=True, force=True)
            batch = Batch_Job()
            batch.start()
            cmds.file(new=True, force=True)
    """
    pass

# @TODO
# batch files
def run(file_path):

    print('## Scene File Open >> {}'.format(file_path))
    cmds.file(file_path, o=True, force=True)
    batch = Batch_Job()
    batch.start()

    # exeで処理していた場合は終了
    if not cmds.about(batch=1):
        cmds.evalDeferred('from maya import cmds;cmds.quit(f=1)')


