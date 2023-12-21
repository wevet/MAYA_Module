# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import os

file_path = cmds.file(q=True, sn=True)
file_name = os.path.basename(file_path)
raw_name, extension = os.path.splitext(file_name)
print(raw_name)
print(extension)

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
_fbx_import_to_namespace(ns='RTG')

cmds.select("RTG:group")

str = "RTG:NC003_Rig_Final:root"
names = str.split(":")
length = len(names) -1
print(names[length])

def _get_animated_attributes(node):
    keyable_attributes = cmds.listAttr(node, keyable=True)
    animated_attributes = []
    if not keyable_attributes:
        return animated_attributes
    print("---------------------------------------------selected node => {0}".format(node))
    for attr in keyable_attributes:
        params = cmds.listConnections(node, destination=True, source=True, plugs=True)
        """
        isTL = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTL')
        isTA = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTA')
        isTU = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTU')
        isTT = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTT')
        if isTL is not None or isTA is not None or isTU is not None or isTT is not None:
            animated_attributes.append(attr)
        """
        if params is not None:
            for param in params:
                print("params => {0}".format(param))
    return animated_attributes

node_list = cmds.ls(selection=True,dag=True,type="joint")
for node in node_list:
    #has_fk = node.find("FK") > -1 or node.find("fk") > -1
    #has_ik = node.find("IK") > -1 or node.find("ik") > -1
    #if has_fk or has_ik:
    attrs = _get_animated_attributes(node)
    for attr in attrs:
        print("attr => {0}".format(attr))

def _unlock_attributes(self, ctrl_list, data):
    for ctrl in ctrl_list:
        for attr in data[ctrl].keys():
            try:
                attr_obj = "{0}.{1}".format(ctrl, attr)
                lock_check = cmds.getAttr(attr_obj, lock=True)
                if lock_check is True:
                    cmds.setAttr(attr_obj, lock=0)
                    print("unlock attr => {0}.{1}".format(ctrl, attr))
            except ValueError:
                continue
    pass

curves = cmds.ls(selection=True, dag=True, type="transform")
for curve in curves:
    if curve.find("FK") > -1:
        print(curve)
#-----------------------------------------------------------------------------------------------------------


import maya.cmds as cmds

curves = cmds.ls(selection=True, dag=True, type="transform")
for curve in curves:
    print(curves)


#-----------------------------------------------------------------------------------------------------------

import maya.cmds as cmds

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

#-----------------------------------------------------------------------------------------------------------

import maya.cmds as cmds

obj = cmds.ls(sl = True)
print(obj)

cmds.cutKey()


import maya.cmds as cmds

def GetAllCurveJoint():
    objs = []
    curves = cmds.ls(type="nurbsCurve", ni=True, o=True, r=True, l=True)
    joints = cmds.ls(type="joint", ni=True, o=True, r=True, l=True)
    for i in curves:
        objs.append(i)
    for i in joints:
        objs.append(i)
    transforms = cmds.listRelatives(objs, p=True, type="transform")
    return transforms

def UnlockAll():
    locked = []
    objs = GetAllCurveJoint()
    for obj in objs:
        attrs = cmds.listAttr(obj)
        for attr in ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]:
            try:
                attrObj = "{0}.{1}".format(obj, attr)
                if cmds.getAttr(attrObj, lock=True) == True:
                    cmds.setAttr(attrObj, lock=0)
                    locked.append(attrObj)
            except ValueError:
                continue
    print(locked)
UnlockAll()

#-----------------------------------------------------------------------------------------------------------



import pymel.core as pm
import maya.cmds as cmds

for i in cmds.ls():
    print(cmds.listAttr(i))

for i in cmds.ls():
    if cmds.attributeQuery("W0", node=i, exists=True) is True:
        print(i)


def _getSelected ():
    selection = pm.selected()
    return [i for i in selection if type(i) == pm.nodetypes.Transform]

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
