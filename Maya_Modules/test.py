# coding: utf-8


import maya.cmds as cmds

cmds.select('*_jnt')
Label_sel = cmds.ls(selection=True)
for each in Label_sel:
    print(each)






