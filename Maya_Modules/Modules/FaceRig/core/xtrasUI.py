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
        window3 = mc.window('XtrasMenu', title='EXTRA OPTIONS (clean out liner, none render controls...)', resizeToFitChildren=True, fw=1, mxb=False, w=350, h=200, s=False)
        mc.frameLayout(labelVisible=0)
        self.control_list()
        self.display_objects()
        self.other_control()
        mc.setParent('..')
        mc.showWindow(window3)

    def control_list(self):
        mc.frameLayout(l='Resize your controller and Locator')
        mc.text(l='その前に、"Ctrl List:" でコントローラグループを選択します。')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Ctrl List:', fn='boldLabelFont')
        mc.separator(w=18, style='none')
        mc.textScrollList('resizeCtrlList', w=140, h=80, sc=control_resize)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.button(l='Refresh', w=100, c=refresh_controller)
        mc.button(l='Freeze Trans', w=100, c=freeze_transform_control_group)
        mc.button(l='Freeze Trans All', w=100, c=freeze_transform_all)
        mc.setParent('..')
        mc.setParent('..')

    def display_objects(self):
        mc.frameLayout(l='Display of Controller / Locator / Joint')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Resize Locator:')
        mc.separator(w=17, style='none')
        mc.floatSliderGrp('resizeLocator', w=150, min=0.001, max=10, v=1, field=1, cw2=(40, 200), pre=3, cc=resize_locator)
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Joint Size Display:')
        mc.separator(w=2, style='none')
        mc.floatSliderGrp('resizeJntDisplay', w=150, min=0.01, max=10, v=1, field=1, cw2=(40, 200), pre=2, dc=resize_joint_display)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')

    def other_control(self):
        mc.frameLayout(l='Others Options')
        mc.text(l='Select an element (controller / mesh / etc...)', fn='boldLabelFont')
        mc.rowLayout(nc=4)
        mc.separator(w=10, style='none')
        mc.text(l='Color Change:')
        mc.separator(w=17, style='none')
        mc.colorIndexSliderGrp('colorChange', label='', min=0, max=20, value=10, cw3=[1, 40, 150], cc=switch_control_color)
        mc.setParent('..')
        mc.separator(style='in')
        mc.button(l='Clean Out liner', c=clean_out_liner)
        mc.text(l="コントローラーなどでリグをスケールさせたい場合は、'C Curves Setup' を自分のリグの親にしてください。'C_facial_jntGrp'にはコンストレイントを作らないようにします。")
        mc.separator(h=10, style='none')
        mc.setParent('..')

def launch_XTRAS_menu_ui(*args):
    XtrasMenuUI()

class ReplaceController:
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
        mc.button(l='Make this action', w=100, c=make_this_XTRAS)
        mc.checkBox('negValue', l='Negative Value ?', v=0)
        mc.checkBox('independent control', l='Specific Ctrl', v=0, cc=specific_control_select)
        mc.checkBox('mirrorCtrl', l='Mirror')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=10, style='none')
        mc.textScrollList('independent control', en=0, h=80, w=317, sc=get_size_value_of_selected_control)
        mc.setParent('..')
        mc.rowLayout(nc=7)
        mc.separator(w=10, style='none')
        mc.text(l='resize control:')
        mc.separator(w=15, style='none')
        mc.floatSliderGrp('resize control', w=250, min=0.001, max=10, v=1, field=1, cw2=(40, 200), pre=3, cc=func_resize_control)
        mc.separator(w=5, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(windowReplace)

# no reference
def launch_XTRAS_resize_control_ui(*args):
    ReplaceController()

def control_resize(*args):
    sel = mc.textScrollList('resizeCtrlList', q=1, si=1)[0]
    if mc.window('ReplaceCtrl', exists=True):
        mc.textScrollList('independent control', e=True, ra=True)
        control_group_child_set_to_menu(sel)
        mc.floatSliderGrp('resizeCtrl', e=1, v=1)
    else:
        launch_xtras_resize_control_ui()
        control_group_child_set_to_menu(sel)

