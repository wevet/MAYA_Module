# -*- coding: utf-8 -*-

import maya.cmds as mc
import func_xtras2
import importlib
importlib.reload(func_xtras2)
from func_xtras2 import *

class XtrasMenuUI:
    def __init__(self):
        if mc.window('XtrasMenu', exists=True):
            mc.deleteUI('XtrasMenu')
        window3 = mc.window('XtrasMenu', title='XTRAS OPTIONS (clean outliner, none renderable ctrls...)', resizeToFitChildren=True, fw=1, mxb=False, w=350, h=200, s=False)
        mc.frameLayout(labelVisible=0)
        self.ctrlList()
        self.displayCLJ()
        self.others()
        mc.setParent('..')
        mc.showWindow(window3)

    def ctrlList(self):
        mc.frameLayout(l='Resize your controller and Locator')
        mc.text(l='Before to go, select a controller group in "Ctrl List:"')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Ctrl List:', fn='boldLabelFont')
        mc.separator(w=18, style='none')
        mc.textScrollList('resizeCtrlList', w=140, h=80, sc=ctrlResize)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.button(l='Refresh', w=100, c=refreshCtrl)
        mc.button(l='Freeze Trans', w=100, c=freezeTransfCtrlGrp)
        mc.button(l='Freeze Trans All', w=100, c=freezeTransAll)
        mc.setParent('..')
        mc.setParent('..')

    def displayCLJ(self):
        mc.frameLayout(l='Display of Controller / Locator / Joint')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Resize Locator:')
        mc.separator(w=17, style='none')
        mc.floatSliderGrp('resizeLocator', w=150, min=0.001, max=10, v=1, field=1, cw2=(40,
                                                                                        200), pre=3, cc=resizeLoc)
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Joint Size Display:')
        mc.separator(w=2, style='none')
        mc.floatSliderGrp('resizeJntDisplay', w=150, min=0.01, max=10, v=1, field=1, cw2=(40,
                                                                                          200), pre=2, dc=resizeJntDisp)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')

    def others(self):
        mc.frameLayout(l='Others Options')
        mc.text(l='Select an element (controller / mesh / etc...)', fn='boldLabelFont')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Color Change:')
        mc.separator(w=17, style='none')
        mc.colorIndexSliderGrp('colorChange', label='', min=0, max=20, value=10, cw3=[1, 40, 150], cc=switchCtrlColor)
        mc.setParent('..')
        mc.separator(style='in')
        mc.button(l='Clean Outliner', c=cleanOutliner)
        mc.text(l="If you want scale your rig with a controller or something else,\n parent 'C_curves_setup' at your own rig. \n Don't make any constraint at the 'C_facial_jntGrp'")
        mc.separator(h=10, style='none')
        mc.setParent('..')

def launchXtrasMenuUI(*args):
    XtrasMenuUI()

class replaceController:
    def __init__(self):
        if mc.window('ReplaceCtrl', exists=True):
            mc.deleteUI('ReplaceCtrl')
        windowReplace = mc.window('ReplaceCtrl', t='Replace Controller', w=347, h=229, sizeable=False)
        mc.columnLayout()
        mc.frameLayout(l='Translate / Rotate / Scale Your Controller')
        mc.rowLayout(nc=6)
        mc.separator(w=10, style='none')
        mc.text(l='Type:', w=60, fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.text(l='Axis:', w=60, fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.text(l='Value:', w=60, fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=10)
        mc.separator(w=10, style='none')
        mc.textScrollList('type', w=60, h=60, append=['translate', 'rotate'])
        mc.separator(w=10, style='none')
        mc.textScrollList('axis', w=60, h=60, append=['X', 'Y', 'Z'])
        mc.separator(w=10, style='none')
        mc.textScrollList('valueList', w=60, h=60, append=['0.01', '0.1', '1', '5', '10', '15', '30', '45', '90'])
        mc.separator(w=10, style='none')
        mc.columnLayout()
        mc.button(l='Make this action', w=100, c=MakeThisXTRAS)
        mc.checkBox('negValue', l='Negative Value ?', v=0)
        mc.checkBox('independantCtrl', l='Specific Ctrl', v=0, cc=specificCtrlSel)
        mc.checkBox('mirrorCtrl', l='Mirror')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=10, style='none')
        mc.textScrollList('indeCtrl', en=0, h=80, w=317, sc=getSizeValueOfSelectedCtrl)
        mc.setParent('..')
        mc.rowLayout(nc=7)
        mc.separator(w=10, style='none')
        mc.text(l='Resize Ctrl:')
        mc.separator(w=15, style='none')
        mc.floatSliderGrp('resizeCtrl', w=250, min=0.001, max=10, v=1, field=1, cw2=(40,
                                                                                     200), pre=3, cc=func_resizeCtrl)
        mc.separator(w=5, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(windowReplace)

def launchXtrasResizeCtrlUI(*args):
    replaceController()

def ctrlResize(*args):
    sel = mc.textScrollList('resizeCtrlList', q=1, si=1)[0]
    if mc.window('ReplaceCtrl', exists=True):
        mc.textScrollList('indeCtrl', e=True, ra=True)
        ctrlGrpChildSetToMenu(sel)
        mc.floatSliderGrp('resizeCtrl', e=1, v=1)
    else:
        launchXtrasResizeCtrlUI()
        ctrlGrpChildSetToMenu(sel)