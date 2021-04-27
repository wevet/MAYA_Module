

import sys
import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaAnim as OpenMayaAnim
import maya.api.OpenMayaRender as OpenMayaRender
import maya.api.OpenMayaUI as OpenMayaUI
import maya.OpenMayaMPx as OpenMayaMPx


#print(OpenMayaMPx.MPxSelectionContext_className.__name__)

'''
選択したObjectをPrintする
'''
#cmds.select()
#oSel = cmds.ls(sl=True)
#print(oSel)


'''
選択したShapeNodeだけ
'''
#cmds.select(cmds.ls(selection=True, dagObjects=True, type='shape'))
#oSel = cmds.ls(sl=True)
#print(oSel)


'''
file save
'''
#cmds.file(save=True, force=True)
#cmds.file(save=True, force=True, type='mayaAscii')
#cmds.file(save=True, force=True, type='mayaBinary')


'''
file save rename
'''
#cmds.file(rename='Sample')
#cmds.file(save=True, type='mayaAscii', force=True)


'''
select objectType取得例
'''
#select_object = cmds.ls(sl=True)
#print(cmds.objectType(select_object))




