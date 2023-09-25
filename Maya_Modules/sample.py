
import maya.cmds as cmds

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


curves = cmds.ls(selection=True, dag=True, type="transform")
for curve in curves:
    if curve.find("FK") > -1:
        print(curve)

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
