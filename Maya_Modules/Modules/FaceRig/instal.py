# -*- coding: utf-8 -*-

import maya.cmds as mc
import os 
import sys
OS = sys.platform

instalPath = "ここにパスのインストールをします"
paths = sys.path
newPath = ''
if OS.startswith('win'):
    pathElement = instalPath.split("/")
    print(pathElement)
    for elt in pathElement:
        if elt != pathElement[len(pathElement)-1]:
            newPath = newPath + str(elt) + '\\'
        else:
            newPath = newPath + str(elt)
else:
    newPath = instalPath

result = 'no'
for path in paths:
    if path == newPath:
        result = 'no'
        break
    else:
        result = 'yes'
if result == 'yes':
    sys.path.append(newPath)
    mc.warning('フェイシャルリグスクリプトのPythonパスに、以下の新しいパスが追加されました。 : %s' % newPath)

print(sys.path)

from core.facial_rig_ui import *
face_rig = FaceRigMainUI()
face_rig.show_ui()
