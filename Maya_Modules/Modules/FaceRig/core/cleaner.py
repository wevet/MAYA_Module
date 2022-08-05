# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
import re

def correctCustomName(*args):
    r = re.compile('([^a-zA-Z])')
    txt = mc.textField('otherNameList', q=True, tx=True)
    txtOk = r.sub('', txt)
    mc.textField('otherNameList', e=True, tx=txtOk)

def groupOutlinerCreation(*args):
    if not mc.objExists('C_SKELETON_grp'):
        mc.group(n='C_SKELETON_grp', em=True)
        mc.select(cl=1)
    if not mc.objExists('C_facial_jntGrp'):
        mc.group(n='C_facial_jntGrp', em=True)
        try:
            mc.parent('C_facial_jntGrp', 'C_SKELETON_grp')
        except:
            pass

        mc.select(cl=1)
    if not mc.objExists('C_facial_ctrlGrp'):
        mc.group(n='C_facial_ctrlGrp', em=True)
        mc.select(cl=1)