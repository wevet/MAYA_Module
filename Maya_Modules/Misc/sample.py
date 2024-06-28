# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import os



import maya.cmds as cmds

def _get_parent(node):
    parent = cmds.listRelatives(node, parent=True, path=True)
    if parent:
        yield parent
        for p in _get_parent(parent):
            yield p

def _get_root_node_valid(node_list):
    for node in node_list:
        if str(node[0]).find('FitSkeleton') > -1:
            return False
    return True

def _get_target_joints():
    ignore_list = ['fatYabs', 'fat', 'fatFront', 'fatWidth', 'fatFrontAbs', 'fatWidthAbs']
    children_joints = cmds.ls(type="joint")
    joints = []
    for joint in children_joints:
        nodes = _get_parent(joint)
        if nodes:
            node_list = list(nodes)
            was_valid = _get_root_node_valid(node_list)
            if was_valid:
                joints.append(joint)

            last_index = len(node_list) -1
            if len(node_list) > 0:
                obj = node_list[last_index][0]
        """
        try:
            value = cmds.getAttr(joint + ".fat")
        except ValueError:
            print("not attr => {}".format(joint))
            joints.append(joint)
            pass
        """

    return joints

cmds.select(_get_target_joints())


def _fbx_import_to_namespace(ns='targetNamespace'):
    # set namespace
    current_namespace = cmds.namespaceInfo(cur=True)
    if not cmds.namespace(ex=':%s' % ns):
        cmds.namespace(add=':%s' % ns)
    cmds.namespace(set=':%s' % ns)

    # import FBX
    path_list = cmds.fileDialog2(fm=1, ds=2, ff=('FBX(*.fbx)'))
    if not path_list:
        return
    mel.eval('FBXImportSetLockedAttribute -v true')
    #mel.eval('FBXImport -f "%s"' % path_list[0])
    import_root = cmds.file(path_list[0], i=True, gr=True, mergeNamespacesOnClash=True, namespace=current_namespace)
    # return current ns
    cmds.namespace(set=current_namespace)
    print(import_root)
_fbx_import_to_namespace(ns='RTG')


def _get_animated_attributes(node):
    key_attributes = cmds.listAttr(node, keyable=True)
    animated_attributes = []
    if not key_attributes:
        return animated_attributes
    print("---------------------------------------------selected node => {0}".format(node))
    for attr in key_attributes:
        params = cmds.listConnections(node, destination=True, source=True, plugs=True)
        isTL = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTL')
        isTA = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTA')
        isTU = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTU')
        isTT = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTT')
        if isTL is not None or isTA is not None or isTU is not None or isTT is not None:
            animated_attributes.append(attr)
        if params is not None:
            for param in params:
                print("params => {0}".format(param))
    return animated_attributes

def _set_anim_curves_objects():
    start_frame = cmds.playbackOptions(q=True, minTime=True)
    end_frame = cmds.playbackOptions(q=True, maxTime=True)
    # anm curveのみ出力
    anim_curves = cmds.ls(type='animCurve')
    for anim in anim_curves:
        print(anim)
        # 全てのキーを取得し、順番にソートする。キーがない場合に備えて `or []` を使っているが、
        # これは `sort` がクラッシュしないように、代わりに空のリストを使う。
        all_keys = sorted(cmds.keyframe(anim, q=True) or [])
        # 少なくとも1つのキーがあるかどうかを確認する。
        if all_keys:
            print(all_keys[0], all_keys[-1])


def get_all_curve_joint():
    objs = []
    curves = cmds.ls(type="nurbsCurve", ni=True, o=True, r=True, l=True)
    joints = cmds.ls(type="joint", ni=True, o=True, r=True, l=True)
    for i in curves:
        objs.append(i)
    for i in joints:
        objs.append(i)
    transforms = cmds.listRelatives(objs, p=True, type="transform")
    return transforms


def _unlock_all_attributes():
    locked = []
    objs = get_all_curve_joint()
    for obj in objs:
        attrs = cmds.listAttr(obj)
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
            try:
                attrObj = "{0}.{1}".format(obj, attr)
                if cmds.getAttr(attrObj, lock=True) is True:
                    cmds.setAttr(attrObj, lock=0)
                    locked.append(attrObj)
            except ValueError:
                continue
    print(locked)
_unlock_all_attributes()

#mel.eval("asSelectorbiped;")

def _run_attributes():
    for i in cmds.ls():
        print(cmds.listAttr(i))

    for i in cmds.ls():
        if cmds.attributeQuery("W0", node=i, exists=True) is True:
            print(i)
_run_attributes()


def _getSelected ():
    selection = mel.selected()
    return [i for i in selection if type(i) == mel.nodetypes.Transform]

def _getConnectionSRC (target, nodeType):
    result = list(set(target.connections(type = nodeType, d = False)))
    return result

def _getConnectionDST (target, nodeType):
    result = list(set(target.connections(type = nodeType, s = False)))
    return result

def _sample():
    for target in _getSelected():
        print(target)
        for pairBlend in _getConnectionSRC(target, "pairBlend"):
            print(pairBlend)
            for constraint in _getConnectionSRC(pairBlend, "constraint"):
                print(constraint)

_sample()

