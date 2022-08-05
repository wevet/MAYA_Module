# -*- coding: utf-8 -*-

import maya.cmds as mc, maya.mel as mel

def refreshCtrl(*args):
    mc.textScrollList('resizeCtrlList', e=1, ra=1)
    if mc.objExists('C_facial_ctrlGrp'):
        mc.select('C_facial_ctrlGrp', hi=True, r=True)
        try:
            mc.select('C_facial_ctrlGrp', d=True)
        except:
            pass

        list = mc.ls(sl=1)
        listClean = []
        for elt in list:
            if elt.endswith('ctrlGrp') == True:
                listClean.append(elt)

        for ctrl in listClean:
            mc.select(ctrl, r=True)
            ctrl = mc.ls(sl=1)[0]
            mc.textScrollList('resizeCtrlList', e=1, append=ctrl)

    else:
        mc.error('No controllers was found')


def ctrlGrpChildSetToMenu(sel, *args):
    childrenName = sel.split('_ctrlGrp')[0]
    listOfChild = mc.ls('%s*_ctrl' % childrenName)
    for ctrl in listOfChild:
        mc.textScrollList('indeCtrl', e=True, a=ctrl)


def launchXtrasResizeCtrlUI(*args):
    replaceController()


def specificCtrlSel(*args):
    check = mc.checkBox('independantCtrl', q=True, v=True)
    if check == 1:
        mc.textScrollList('indeCtrl', e=True, en=True, ams=True)
    else:
        mc.textScrollList('indeCtrl', e=True, en=False)


def getSizeValueOfSelectedCtrl(*args):
    sel = mc.textScrollList('indeCtrl', q=True, si=True)
    if len(sel) == 1:
        sel = sel[0]
        value = mc.getAttr('%s.scaleX' % sel)
        mc.floatSliderGrp('resizeCtrl', e=1, v=value)
    elif len(sel) > 1:
        mc.floatSliderGrp('resizeCtrl', e=1, v=1)
        mc.warning('The resize controller slider will be set at 1 when you have more than one object selected')


def ctrlSelectionWithCheckBox(*args):
    check = mc.checkBox('independantCtrl', q=True, v=True)
    listCtrl = []
    if check == True:
        listCtrl = mc.textScrollList('indeCtrl', q=True, si=True)
    else:
        master = mc.textScrollList('resizeCtrlList', q=True, si=1)[0]
        info = master.split('_')
        listCtrl = mc.ls('%s_%s_*_ctrl' % (info[0], info[1]))
    mirror = mc.checkBox('mirrorCtrl', q=1, v=1)
    newListOfSel = []
    if mirror == True:
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


def func_resizeCtrl(*args):
    newListOfSel = ctrlSelectionWithCheckBox()
    value = mc.floatSliderGrp('resizeCtrl', q=True, v=True)
    for axis in ['X', 'Y', 'Z']:
        for elt in newListOfSel:
            mc.setAttr('%s.scale%s' % (elt, axis), value)


def MakeThisXTRAS(*args):
    ctrlList = ctrlSelectionWithCheckBox()
    sides = []
    ctrls = mc.textScrollList('resizeCtrlList', q=1, si=1)
    type = mc.textScrollList('type', q=1, si=1)[0]
    axis = mc.textScrollList('axis', q=1, si=1)[0]
    negVal = mc.checkBox('negValue', q=1, v=1)
    value = mc.textScrollList('valueList', q=1, si=1)
    value = float(value[0])
    mirror = mc.checkBox('mirrorCtrl', q=1, v=1)
    tValue = [
     0, 0, 0]
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
            if mirror == True:
                for i in range(lenght):
                    if i < lenght / 2:
                        mc.select(ctrlList[i] + '.cv[*]', r=True)
                        print 'inv side ctrl = %s' % ctrlList[i]
                        print 'type = %s / mirrorVal = %s' % (type, mirrorVal)
                        if type == 'translate':
                            mel.eval('move -r %s;' % mirrorVal)
                        else:
                            pos = mc.xform(ctrlList[i] + '.cv[0]', q=1, ws=1, t=1)
                            mel.eval('rotate -os -fo %s ;' % mirrorVal)
                    else:
                        mc.select(ctrlList[i] + '.cv[*]', r=True)
                        print 'good side ctrl = %s' % ctrlList[i]
                        print 'type = %s / mirrorVal = %s' % (type, tValue)
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


def resizeLoc(*args):
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


def resizeJntDisp(*args):
    value = mc.floatSliderGrp('resizeJntDisplay', q=1, v=1)
    mel.eval('jointDisplayScale(%s)' % value)


def freezeTransfCtrlGrp(*args):
    ctrlGrp = mc.textScrollList('resizeCtrlList', q=True, si=1)
    if ctrlGrp != None:
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
            mc.warning('all controller inside your : %s are now correctly freeze transform' % ctrlGrp)
        except:
            mc.error("Problem found between the selection of the %s controller maybe any controllers doesn't exists for this group" % ctrlGrp, n=False)

    else:
        mc.error('Please select one ctrlGrp into the list before trying to execute this command', n=False)
    return


def freezeTransAll(*args):
    listOfCtrlGrp = ''
    try:
        listOfCtrlGrp = mc.ls('*_ctrlGrp')
    except:
        pass

    okFreeze = []
    if len(listOfCtrlGrp) > 0:
        for ctrlGrp in listOfCtrlGrp:
            info = ctrlGrp.split('_')
            listCtrl = []
            try:
                listCtrl = mc.ls('%s_%s*_ctrl' % (info[0], info[1]))
            except:
                pass

            if len(listCtrl) > 0:
                for ctrl in listCtrl:
                    mc.makeIdentity(ctrl, a=True)
                    mc.delete(ctrl, ch=True)

                okFreeze.append(ctrlGrp)

        mc.warning('Freeze Transform are okey for : %s' % ctrlGrp)
    else:
        mc.error('No ctrl grp has been found, this action will be aborted', n=False)


def switchCtrlColor(*args):
    sel = mc.ls(sl=1)
    color = mc.colorIndexSliderGrp('colorChange', q=True, v=True)
    print 'color = %s' % color
    if len(sel) > 0:
        for elt in sel:
            try:
                mc.setAttr('%s.ove' % elt, 1)
                mc.setAttr('%s.ovc' % elt, color - 1)
            except:
                pass


def cleanOutliner(*args):
    if mc.objExists('C_faceCurvesBld_grp'):
        if mc.objExists('blendShapes'):
            try:
                mc.parent('C_faceCurvesBld_grp', 'blendShapes')
            except:
                pass

    try:
        mc.select('*_bld_crv', r=True)
        list = mc.ls(sl=1)
        for elt in list:
            parent(elt, 'C_faceCurvesBld_grp')

    except:
        pass

    if mc.objExists('*_rigConnect'):
        mc.select('*_rigConnect', r=True)
        for elt in mc.ls(sl=1):
            try:
                mc.parent(elt, 'C_facial_jntGrp')
            except:
                pass

    try:
        mc.select('*_Pin', r=True)
        list = mc.ls(sl=1)
        if len(list) > 0:
            for elt in list:
                mc.parent(elt, 'C_Facial_Pin_Controller_grp')

    except:
        pass

    for x in ('XTRAS', 'C_SKELETON_grp', 'C_CONTROLLER_grp'):
        try:
            mc.delete('*%s' % x)
        except:
            pass

    try:
        mc.parent('C_Head_Facial_Rig_crvGrp', 'xtra_toHide')
    except:
        pass

    mc.warning('Your Outliner is now Clean')