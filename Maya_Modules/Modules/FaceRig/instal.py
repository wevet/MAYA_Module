# -*- coding: utf-8 -*-


import maya.cmds as mc
import os 
import sys
OS = sys.platform


# installation of facial rig path
instalPath = "put your path installation here"
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
    mc.warning('A new path was added into your python path for the facial rig script at : %s' % newPath)

print(sys.path)

from core.facial_rig_UI import *
UI()
