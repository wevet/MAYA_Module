# -*- coding: utf-8 -*-

import os
import pymel.core as pm
from maya import cmds, OpenMaya, OpenMayaAnim



class Batch_Job:

    def __init__(self):
        self.dummy_key_frame = -50
        self.start_frame = 0
        self.anim_curves = []
        self.controllers = []
        self.all_joints = []
        self.pole_legs = []

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
                if not ctrl in self.anim_curves:
                    # コントローラーがキーが使える属性を取得したかどうかを確認する、そうでなければ、コントロールをミラーリングする理由はない
                    if cmds.listAttr(ctrl, keyable=True):
                        self.controllers.append(ctrl)
                        if str(ctrl).find("PoleLeg") > -1:
                            print("found leg => {0}".format(ctrl))
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
        for ctrl in self.anim_curves:
            attributes = cmds.listAttr(ctrl, keyable=True, unlocked=True)
            if attributes:
                for attr in attributes:
                    attr_obj = "{}.{}".format(ctrl, attr)
                    lock_check = cmds.getAttr(attr_obj, lock=True)
                    if lock_check is True:
                        cmds.setAttr(attr_obj, lock=0)
                        print("unlock attr => {0}.{1}".format(ctrl, attr))
            #cmds.setKeyframe(ctrl, v=0, t=self.dummy_key_frame)
            pass

        #再生時間を変更する
        cmds.playbackOptions(edit=1, minTime=self.dummy_key_frame)
        cmds.currentTime(self.dummy_key_frame)
        pass

    def _export_fbx(self, file_path):
        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')
        cmds.file(file_path, force=True, options="v=0;", type="FBX export")


    # @TODO
    # export処理を行う
    # controllerかjointを取得し更にPoleVectorを選択する
    def start(self):
        print("start build export")

        self._build_key_frame()
        scene_name = self._get_scene_name()
        print(scene_name)

        self.all_joints = []
        self.all_joints = self._get_all_joints()
        self.all_joints.extend(self.pole_legs)
        pm.select(self.all_joints)
        for obj in self.all_joints:
            print(obj)

        time_range = self._get_frame_range()
        #self._bake_connected(self.all_joints, time_range)

        filepath = cmds.file(q=True, sn=True)  # directory/sample.ma
        filename = os.path.basename(filepath)  # sample.ma
        base_directory = filepath.split(filename)[-2]  # directory/
        output_directory = base_directory + "Exported/" # exportedディレクトリを作成
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        file_path = os.path.join(output_directory, "{}.fbx".format(scene_name))
        self._export_fbx(file_path)
        print("EXPORT FINISHED", file_path)
        pass



if __name__ == "__main__":
    batch = Batch_Job()
    batch.start()



