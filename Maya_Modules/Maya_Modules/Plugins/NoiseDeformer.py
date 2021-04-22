# -*- coding: utf-8 -*-

import traceback
import maya._OpenMaya as OpenMaya
import maya._OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds



class NoiseDeformerNode(OpenMayaMPx.MPxDeformerNode):

    type_name = "NoiseDeformer"
    node_id = OpenMaya.MTypeId(0x70100)
  
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
        print("NoiseDeformerNode.Initializer")
        pass
  
    def deform(self, data_block, geometry_iter, matrix, multi_index):
        """
        変形処理
        """
        pass
  

def initializePlugin(MObj_mobject):
    # load時に呼ばれる
    MPlg_plugin = OpenMayaMPx.MFnPlugin(MObj_mobject)
    try:
        MPlg_plugin.registerNode(NoiseDeformerNode.type_name,
                                 NoiseDeformerNode.node_id,
                                 NoiseDeformerNode.creator,
                                 NoiseDeformerNode.initializer,
                                 OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        msg = "Failed to register node\n{0}"
        sys.stderr.write(msg.format(traceback.format_exc()))
  

def uninitializePlugin(MObj_mobject):
    # Unload時に呼ばれる
    MPlg_plugin = OpenMayaMPx.MFnPlugin(MObj_mobject)
    try:
        MPlg_plugin.deregisterNode(NoiseDeformerNode.node_id)
    except:
        msg = "Failed to unregister node\n{0}"
        sys.stderr.write(msg.format(traceback.format_exc()))


