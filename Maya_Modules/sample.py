
import pymel.core as pm
import maya.cmds as cmds

def get_item_list(node, item_array):
    children = node.getChildren()
    for child in children:
        type = child.nodeType()
        if str(type).find("nurbsCurve") > -1:
            if child.name().find("FK") > -1:
                item_array.append(child)
        get_item_list(child, item_array)
    return item_array

sel = pm.selected()
item_list = []

for i in sel:
    l = get_item_list(i, item_list)

print(item_list)

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
