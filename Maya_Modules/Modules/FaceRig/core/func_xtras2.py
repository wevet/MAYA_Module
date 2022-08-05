# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
from xtrasUI import *

def refresh_controller(*args):
    mc.textScrollList('resizeCtrlList', e=1, ra=1)
    if mc.objExists('C_facial_ctrlGrp'):
        mc.select('C_facial_ctrlGrp', hi=True, r=True)
        try:
            mc.select('C_facial_ctrlGrp', d=True)
        except ZeroDivisionError:
            pass

        list = mc.ls(sl=1)
        listClean = []
        for elt in list:
            if elt.endswith('ctrlGrp') is True:
                listClean.append(elt)

        for ctrl in listClean:
            mc.select(ctrl, r=True)
            ctrl = mc.ls(sl=1)[0]
            mc.textScrollList('resizeCtrlList', e=1, append=ctrl)

    else:
        mc.error('No controllers was found')

def control_group_child_set_to_menu(sel, *args):
    childrenName = sel.split('_ctrlGrp')[0]
    listOfChild = mc.ls('%s*_ctrl' % childrenName)
    for ctrl in listOfChild:
        mc.textScrollList('indeCtrl', e=True, a=ctrl)

def launch_xtras_resize_control_ui(*args):
    ReplaceController()

def specific_control_select(*args):
    check = mc.checkBox('independantCtrl', q=True, v=True)
    if check == 1:
        mc.textScrollList('indeCtrl', e=True, en=True, ams=True)
    else:
        mc.textScrollList('indeCtrl', e=True, en=False)

def get_size_value_of_selected_control(*args):
    sel = mc.textScrollList('indeCtrl', q=True, si=True)
    if len(sel) == 1:
        sel = sel[0]
        value = mc.getAttr('%s.scaleX' % sel)
        mc.floatSliderGrp('resizeCtrl', e=1, v=value)
    elif len(sel) > 1:
        mc.floatSliderGrp('resizeCtrl', e=1, v=1)
        mc.warning('複数のオブジェクトが選択されている場合、リサイズコントローラーのスライダーは1に設定されます')

def control_selection_with_checkbox(*args):
    check = mc.checkBox('independantCtrl', q=True, v=True)
    listCtrl = []
    if check is True:
        listCtrl = mc.textScrollList('indeCtrl', q=True, si=True)
    else:
        master = mc.textScrollList('resizeCtrlList', q=True, si=1)[0]
        info = master.split('_')
        listCtrl = mc.ls('%s_%s_*_ctrl' % (info[0], info[1]))
    mirror = mc.checkBox('mirrorCtrl', q=1, v=1)
    newListOfSel = []
    if mirror is True:
        for elt in listCtrl:
            side = elt.split('_')[0]
            name = elt.split(side + '_')[1]
            otherSide = ''
            if side == 'L':
                otherSide = 'R'
            elif side == 'R':
                otherSide = 'L'
            if otherSide == 'L' or otherSide == 'R':
                testName = '%s_%s' % (otherSide, name)
                if mc.objExists(testName):
                    newListOfSel.append(testName)

        for elt in listCtrl:
            newListOfSel.append(elt)

    else:
        newListOfSel = listCtrl
    return newListOfSel

def func_resize_control(*args):
    newListOfSel = control_selection_with_checkbox()
    value = mc.floatSliderGrp('resizeCtrl', q=True, v=True)
    for axis in ['X', 'Y', 'Z']:
        for elt in newListOfSel:
            mc.setAttr('%s.scale%s' % (elt, axis), value)

def make_this_XTRAS(*args):
    ctrlList = control_selection_with_checkbox()
    sides = []
    ctrls = mc.textScrollList('resizeCtrlList', q=1, si=1)
    type = mc.textScrollList('type', q=1, si=1)[0]
    axis = mc.textScrollList('axis', q=1, si=1)[0]
    negVal = mc.checkBox('negValue', q=1, v=1)
    value = mc.textScrollList('valueList', q=1, si=1)
    value = float(value[0])
    mirror = mc.checkBox('mirrorCtrl', q=1, v=1)
    tValue = [0, 0, 0]
    if negVal == 1:
        value = value * -1
    if axis == 'X':
        tValue = '%s 0 0' % value
    else:
        if axis == 'Y':
            tValue = '0 %s 0' % value
        else:
            tValue = '0 0 %s' % value
        mirrorVal = tValue
        if mirror == True and axis == 'X':
            mirrorVal = '%s 0 0' % (value * -1)
        lenght = len(ctrlList)
        for i in range(lenght):
            if mirror is True:
                for i in range(lenght):
                    if i < lenght / 2:
                        mc.select(ctrlList[i] + '.cv[*]', r=True)
                        print('inv side ctrl = %s' % ctrlList[i])
                        print('type = %s / mirrorVal = %s' % (type, mirrorVal))
                        if type == 'translate':
                            mel.eval('move -r %s;' % mirrorVal)
                        else:
                            pos = mc.xform(ctrlList[i] + '.cv[0]', q=1, ws=1, t=1)
                            mel.eval('rotate -os -fo %s ;' % mirrorVal)
                    else:
                        mc.select(ctrlList[i] + '.cv[*]', r=True)
                        print('good side ctrl = %s' % ctrlList[i])
                        print('type = %s / mirrorVal = %s' % (type, tValue))
                        if type == 'translate':
                            mel.eval('move -r %s;' % tValue)
                        else:
                            pos = mc.xform(ctrlList[i] + '.cv[0]', q=1, ws=1, t=1)
                            mel.eval('rotate -os -fo %s ;' % tValue)
                    i = i + 1

            else:
                mc.select(ctrlList[i] + '.cv[*]', r=True)
                if type == 'translate':
                    mel.eval('move -r %s;' % tValue)
                else:
                    pos = mc.xform(ctrlList[i] + '.cv[0]', q=1, ws=1, t=1)
                    mel.eval('rotate -os -fo %s ;' % tValue)

def resize_locator(*args):
    value = mc.floatSliderGrp('resizeLocator', q=1, v=1)
    elts = mc.ls('*_loc')
    for elt in elts:
        mc.select(elt, r=True)
        loc = mc.ls(sl=1)[0]
        if mc.objExists('%sShape' % loc):
            locShape = '%sShape' % loc
            mc.setAttr('%s.localScaleX' % locShape, value)
            mc.setAttr('%s.localScaleY' % locShape, value)
            mc.setAttr('%s.localScaleZ' % locShape, value)

def resize_joint_display(*args):
    value = mc.floatSliderGrp('resizeJntDisplay', q=1, v=1)
    mel.eval('jointDisplayScale(%s)' % value)

def freeze_transform_control_group(*args):
    ctrlGrp = mc.textScrollList('resizeCtrlList', q=True, si=1)
    if ctrlGrp is None:
        mc.select(ctrlGrp, r=True)
        grp = mc.ls(sl=1)[0]
        info = grp.split('_')
        try:
            ctrlList = mc.ls('%s_%s*_ctrl' % (info[0], info[1]))
            for ctrl in ctrlList:
                mc.select(ctrl, r=True)
                mc.makeIdentity(a=1)
                mc.delete(ch=1)
            mc.select(cl=1)
            mc.warning('すべてのコントローラが正しくフリーズ変換されるようになりました。' % ctrlGrp)
        except ZeroDivisionError:
            mc.error("このグループにはコントローラが存在しないため、%s コントローラの選択に問題があることが判明しました。" % ctrlGrp, n=False)
    else:
        mc.error('このコマンドを実行する前に、ctrlGrpを1つ選択してください。', n=False)
    return

def freeze_transform_all(*args):
    listOfCtrlGrp = ''
    try:
        listOfCtrlGrp = mc.ls('*_ctrlGrp')
    except ZeroDivisionError:
        pass

    okFreeze = []
    if len(listOfCtrlGrp) > 0:
        for ctrlGrp in listOfCtrlGrp:
            info = ctrlGrp.split('_')
            listCtrl = []
            try:
                listCtrl = mc.ls('%s_%s*_ctrl' % (info[0], info[1]))
            except ZeroDivisionError:
                pass
            if len(listCtrl) > 0:
                for ctrl in listCtrl:
                    mc.makeIdentity(ctrl, a=True)
                    mc.delete(ctrl, ch=True)
                okFreeze.append(ctrlGrp)
        mc.warning('Freeze Transform are ok : %s' % ctrlGrp)
    else:
        mc.error('ctrl Grpが見つかりませんでした。', n=False)

def switch_control_color(*args):
    sel = mc.ls(sl=1)
    color = mc.colorIndexSliderGrp('colorChange', q=True, v=True)
    print('color = %s' % color)
    if len(sel) > 0:
        for elt in sel:
            try:
                mc.setAttr('%s.ove' % elt, 1)
                mc.setAttr('%s.ovc' % elt, color - 1)
            except ZeroDivisionError:
                pass

def clean_out_liner(*args):
    if mc.objExists('C_faceCurvesBld_grp'):
        if mc.objExists('blendShapes'):
            try:
                mc.parent('C_faceCurvesBld_grp', 'blendShapes')
            except ZeroDivisionError:
                pass
    try:
        mc.select('*_bld_crv', r=True)
        list = mc.ls(sl=1)
        for elt in list:
            mc.parent(elt, 'C_faceCurvesBld_grp')
    except ZeroDivisionError:
        pass

    if mc.objExists('*_rigConnect'):
        mc.select('*_rigConnect', r=True)
        for elt in mc.ls(sl=1):
            try:
                mc.parent(elt, 'C_facial_jntGrp')
            except ZeroDivisionError:
                pass

    try:
        mc.select('*_Pin', r=True)
        list = mc.ls(sl=1)
        if len(list) > 0:
            for elt in list:
                mc.parent(elt, 'C_Facial_Pin_Controller_grp')
    except ZeroDivisionError:
        pass

    for x in ('XTRAS', 'C_SKELETON_grp', 'C_CONTROLLER_grp'):
        try:
            mc.delete('*%s' % x)
        except ZeroDivisionError:
            pass
    try:
        mc.parent('C_Head_Facial_Rig_crvGrp', 'xtra_toHide')
    except ZeroDivisionError:
        pass
    mc.warning('Out liner is clean.')

