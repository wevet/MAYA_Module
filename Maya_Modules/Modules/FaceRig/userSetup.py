# -*- coding: utf-8 -*-


import sys
import maya.cmds as cmds
import maya.utils
import facial_rig_ui as facial_rig

def face_rig_loader():
    cmds.setParent('MayaWindow')
    cmds.menu(label=u'Face Rig Tools', tearOff=True)
    cmds.menuItem(subMenu=True, label='Setup', tearOff=True)
    cmds.menuItem(label='Create Window', command="""import importlib\r\nimportlib.reload(facial_rig)\r\nfacial_rig.FaceRigMainUI().show_ui()""")
    cmds.setParent('..', menu=True)
    print("""
_____________________________________
  ______              _____  _       
 |  ____/\           |  __ \(_)      
 | |__ /  \   ___ ___| |__) |_  __ _ 
 |  __/ /\ \ / __/ _ \  _  /| |/ _` |
 | | / ____ \ (_|  __/ | \ \| | (_| |
 |_|/_/    \_\___\___|_|  \_\_|\__, |
                                __/ |
                               |___/ 
_____________________________________
    """)

maya.utils.executeDeferred(face_rig_loader)

