# -*- coding: utf-8 -*-

import traceback
import random
import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx


class NoiseDeformerNode(OpenMayaMPx.MPxDeformerNode):
    type_name = "NoiseDeformer"
    node_id = OpenMaya.MTypeId(0x70100)
    scale = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    @staticmethod
    def creator():
        """
        Node生成
        """
        return OpenMayaMPx.asMPxPtr(NoiseDeformerNode())

    @staticmethod
    def initializer():
        """
        Node初期化
        """

        # scale attributeを作成する
        n_attr = OpenMaya.MFnNumericAttribute()
        NoiseDeformerNode.scale = n_attr.create(
            "scale",
            "sc",
            OpenMaya.MFnNumericData.kDouble,
            1.0)

        n_attr.setKeyable(True)
        try:
            # 各アトリビュートノードに追加し
            # アトリビュートの値が変更した際に影響するアトリビュートを設定する
            NoiseDeformerNode.addAttribute(NoiseDeformerNode.scale)
            output_geometry = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom

            NoiseDeformerNode.attributeAffects(NoiseDeformerNode.scale, output_geometry)
        except:
            msg = "Failed to create attributes of {0} node\n{1}"
            sys.stderr.write(msg.format(NoiseDeformerNode.type_name, traceback.format_exc()))

    def deform(self, data_block, geometry_iter, matrix, multi_index):
        """
        変形処理
        """
        # scaleアトリビュートの値を取得
        DH_scale = data_block.inputValue(self.scale)
        scale = DH_scale.asDouble()

        # envelopeアトリビュートの値を取得
        DH_envelope = data_block.inputValue(self.envelope)
        envelope = DH_envelope.asFloat()

        while not geometry_iter.isDone():
            # 新しい位置を求める
            P_point = geometry_iter.position()
            P_replace_point = OpenMaya.MPoint()
            P_replace_point.x = P_point.x
            P_replace_point.y = P_point.y + random.random() * scale
            P_replace_point.z = P_point.z
            # 影響度を入れて次の位置にする
            P_point += (P_point - P_replace_point) * envelope
            geometry_iter.setPosition(P_point)
            geometry_iter.next()
        # end


def initializePlugin(MObj_mobject):
    # load時に呼ばれる
    MPlg_plugin = OpenMayaMPx.MFnPlugin(MObj_mobject)
    try:
        MPlg_plugin.registerNode(NoiseDeformerNode.type_name,
                                 NoiseDeformerNode.node_id,
                                 NoiseDeformerNode.creator,
                                 NoiseDeformerNode.initializer,
                                 OpenMayaMPx.MPxNode.kDeformerNode)
    except ArithmeticError as e:
        msg = "Failed to register node\n{0}"
        sys.stderr.write(msg.format(traceback.format_exc()))


def uninitializePlugin(MObj_mobject):
    # Unload時に呼ばれる
    MPlg_plugin = OpenMayaMPx.MFnPlugin(MObj_mobject)
    try:
        MPlg_plugin.deregisterNode(NoiseDeformerNode.node_id)
    except ArithmeticError as e:
        msg = "Failed to unregister node\n{0}"
        sys.stderr.write(msg.format(traceback.format_exc()))
