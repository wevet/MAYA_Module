# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel
import re
import controllers_creation
import importlib
from controllers_creation import *
from dictionnaire_ordonne import DictionnaireOrdonne
from controllers_creation import control_creation
importlib.reload(controllers_creation)

def add_sel_curve_creation(*args):
    curveSel = mc.ls(sl=1)
    nbObj = len(curveSel)
    if nbObj == 1:
        curveSel = curveSel[0]
        try:
            shape = mc.listRelatives(curveSel)[0]
            if mc.objectType(shape, isType='nurbsCurve'):
                mc.textScrollList('curveSelList', e=True, ra=True)
                mc.textScrollList('curveSelList', e=True, append=curveSel)
            else:
                raise mc.error('Please, select a curve')
        except ZeroDivisionError:
            mc.textScrollList('curveSelList', e=True, ra=True)
            raise mc.error('Please, select a curve')
    else:
        mc.warning('Select just one element')
        mc.textScrollList('curveSelList', e=True, ra=True)

def add_control_to_curve_creation(*args):
    sel = mc.ls(sl=1)
    lenSel = len(sel)
    if lenSel == 1:
        if not mc.objectType(mc.ls(sl=1), isType='joint'):
            if mc.objExists(mc.listRelatives(mc.ls(sl=1))[0]):
                sel = mc.ls(sl=1)[0]
                selShape = mc.listRelatives(sel)[0]
                if mc.objectType(selShape, isType='nurbsSurface') or mc.objectType(selShape, isType='nurbsCurve'):
                    mc.textScrollList('otherCtrlShapeList', e=1, ra=1)
                    mc.textScrollList('otherCtrlShapeList', e=1, a=sel)
                else:
                    mc.textScrollList('otherCtrlShapeList', e=1, ra=1)
                    raise mc.error('you need to put a "nurbs curve" or a "nurbs surface"')
            else:
                mc.textScrollList('otherCtrlShapeList', e=1, ra=1)
                raise mc.error('you need to put a "nurbs curve" or a "nurbs surface"')
        else:
            mc.textScrollList('otherCtrlShapeList', e=1, ra=1)
            raise mc.error('you cannot add a joint for this operation')
    else:
        mc.textScrollList('otherCtrlShapeList', e=1, ra=1)
        raise mc.error('Please select just one object')

def create_system_on_curve_selected(*args):
    nbLoc = mc.intField('range', q=True, value=True)
    if nbLoc >= 3:
        custCtrl = mc.textScrollList('otherCtrlShapeList', q=1, ai=1)
        listAttr = ['receiveShadows', 'motionBlur', 'castsShadows', 'primaryVisibility', 'smoothShading', 'visibleInReflections', 'visibleInRefractions']
        test = 0
        curveSel = mc.textScrollList('curveSelList', q=True, ai=1)
        typeCtrl = mc.iconTextRadioCollection('ctrlShapeGrp', q=1, select=1)
        if typeCtrl == 4:
            ctrl = mc.textScrollList('otherCtrlShapeList', q=1, ai=1)
            lenCtrl = len(ctrl)
            if lenCtrl != 0:
                test = 1
        else:
            test = 1
        if test == 1:
            if curveSel != '':
                mc.select(curveSel, r=True)
                crv = mc.ls(sl=1)[0]
                crvList = []
                customNameList = []
                check = mc.checkBox('mirrorCheck', q=1, v=1)
                if len(crv) > 0:
                    side = mc.radioButtonGrp('sideRadio', q=1, sl=True)
                    if side == 1:
                        side = 'L'
                    elif side == 2:
                        side = 'C'
                        if check is True:
                            mc.warning('You cannot have a mirror for a Central Curve')
                    else:
                        side = 'R'
                    type = mc.radioCollection('typeRadioGrp', q=1, sl=1)
                    if type == 'custom':
                        type = mc.textField('otherNameList', q=1, tx=1)
                        if type == '':
                            type = 'default'
                        customNameList.append(type)
                    if not mc.objExists('%s_%s_crv' % (side, type)) or crv == '%s_%s_crv' % (side, type):
                        crv = mc.ls(crv)[0]
                        mc.rename(crv, '%s_%s_crv' % (side, type))
                        crv = '%s_%s_crv' % (side, type)
                        crvList.append(crv)
                        mc.textScrollList('curveSelList', e=True, ra=1)
                        mc.textScrollList('curveSelList', e=True, append=crv)
                        if mc.objExists('%s_%s*ctrlGrp' % (side, type)):
                            mc.delete('%s_%s*ctrlGrp' % (side, type))
                        if mc.objExists('%s_%s*grpOff' % (side, type)):
                            mc.delete('%s_%s*grpOff' % (side, type))
                        if check is True:
                            if mc.objExists('*_%s*ctrlGrp' % type):
                                mc.delete('*_%s*ctrlGrp' % type)
                            if mc.objExists('*_%s*grpOff' % type):
                                mc.delete('*_%s*grpOff' % type)
                            unique = ''
                            if side != 'C':
                                mc.select(crv, r=True)
                                mc.makeIdentity(a=1)
                                if side == 'L':
                                    if not mc.objExists('R_%s_crv' % type):
                                        mc.duplicate(crv, n='R_%s_crv' % type)
                                        unique = 1
                                    else:
                                        mc.delete('R_%s_crv' % type)
                                        mc.duplicate(crv, n='R_%s_crv' % type)
                                        mc.warning('R_%s_crvという名前のカーブが見つかり、ミラーを作成するために削除されました。' % type)
                                        unique = 1
                                elif side == 'R':
                                    if not mc.objExists('L_%s_crv' % type):
                                        mc.duplicate(crv, n='L_%s_crv' % type)
                                        unique = 1
                                    else:
                                        mc.delete('L_%s_crv' % type)
                                        mc.duplicate(crv, n='L_%s_crv' % type)
                                        mc.warning('L_%s_crvという名前のカーブが見つかり、ミラーを作成するために削除されました。' % type)
                                        unique = 1
                                if unique == 1:
                                    dupCrv = mc.ls(sl=1)[0]
                                    mc.select(cl=1)
                                    mc.group(n='TMP_sym_grp', em=1)
                                    symGrp = mc.ls(sl=1)[0]
                                    mc.parent(dupCrv, symGrp)
                                    mc.setAttr('%s.scaleX' % symGrp, -1)
                                    mc.makeIdentity(a=1)
                                    mc.parent(dupCrv, w=1)
                                    mc.delete(symGrp)
                                    crvList.append(dupCrv)
                                else:
                                    mc.warning('ミラーカーブの名前が一意でないため、処理が中断されました。')
                            else:
                                mc.warning('中央の側面が対称的なカーブを描くことはできません')
                        for crv in crvList:
                            mc.select(crv, r=True)
                            crv = mc.ls(sl=1)[0]
                            mc.makeIdentity(a=1)
                            mc.delete(ch=1)
                            nom = crv.split('_crv')[0]
                            mel.eval('rebuildCurve -ch 1 -rpo 1 -rt 0 -end 1 -kr 2 -kcp 0 -kep 1 -kt 0 -s ' + str(nbLoc - 1) + ' -d 3 -tol 0.01 "' + crv + '";')
                            posLoc = 0.5
                            if nbLoc > 1:
                                posLoc = 1.0 / (nbLoc - 1)
                            locList = []
                            ctrlList = []
                            for i in range(nbLoc):
                                mc.spaceLocator()
                                loc = mc.ls(sl=1)[0]
                                loc = mc.rename(loc, '%s_%s_loc' % (nom, str(i + 1)))
                                for axis in ['X', 'Y', 'Z']:
                                    mc.setAttr('%s.localScale%s' % (loc, axis), 0.01)

                                mc.select(crv, loc, r=True)
                                namePath = '%s_%s_mp' % (nom, str(i + 1))
                                namePath = nom + '_' + str(i + 1) + '_mp'
                                mc.pathAnimation(fractionMode=True, follow=False, startTimeU=0, endTimeU=100, n=namePath)
                                value = namePath + '_uValue'
                                mc.delete(value)
                                if nbLoc == 1:
                                    mc.setAttr(namePath + '.uValue', 0.5)
                                else:
                                    mc.setAttr(namePath + '.uValue', i * posLoc)
                                locList.append(loc)
                                mc.connectAttr('%s.xCoordinate' % namePath, '%s.translateX' % loc, f=1)
                                mc.connectAttr('%s.yCoordinate' % namePath, '%s.translateY' % loc, f=1)
                                mc.connectAttr('%s.zCoordinate' % namePath, '%s.translateZ' % loc, f=1)
                                cons = mc.listConnections(namePath)
                                for con in cons:
                                    if mc.objectType(con, isType='addDoubleLinear'):
                                        mc.delete(con)

                            for loc in locList:
                                mc.select(loc, r=True)
                                loc = mc.ls(sl=1)[0]
                                locName = loc.split('_loc')[0]
                                pos = mc.xform(loc, q=1, ws=1, t=1)
                                mc.select(cl=1)
                                mc.joint(n=locName + '_jntOff')
                                jntOff = mc.ls(sl=1)[0]
                                mc.xform(jntOff, ws=1, t=pos)
                                mc.parent(jntOff, loc)
                                mc.select(cl=1)
                                mc.joint(n=locName + '_jnt')
                                jnt = mc.ls(sl=1)[0]
                                mc.xform(jnt, ws=1, t=pos)
                                mc.parent(jnt, jntOff)

                            mc.select(cl=1)
                            for loc in locList:
                                mc.select(loc, r=True)
                                loc = mc.ls(sl=1)[0]
                                locName = loc.split('_loc')[0]
                                pos = mc.xform(loc, q=1, ws=1, t=1)
                                mc.select(cl=1)
                                control_creation(typeCtrl, locName + '_ctrl')
                                ctrl = mc.ls(sl=1)[0]
                                ctrlShape = mc.listRelatives(ctrl)[0]
                                for attr in listAttr:
                                    if mc.objExists(ctrlShape + '.' + attr):
                                        mc.setAttr('%s.%s' % (ctrlShape, attr), 0)

                                mc.xform(ctrl, ws=1, t=pos)
                                mc.makeIdentity(a=1)
                                mc.delete(ch=1)
                                mc.parentConstraint(ctrl, locName + '_jnt', skipRotate=['x', 'y', 'z'], mo=True)
                                mc.orientConstraint(ctrl, locName + '_jnt', mo=True)
                                mc.select(cl=1)
                                grp = mc.group(n='%s_ctrl_grpOff' % locName, em=1)
                                grp = mc.ls(sl=1)[0]
                                mc.xform(grp, ws=1, t=pos)
                                mc.makeIdentity(a=1)
                                mc.delete(ch=1)
                                mc.parent(ctrl, grp)
                                mc.select(loc, grp, r=True)
                                mc.parentConstraint(loc, grp, mo=1)
                                constraint = '%s_parentConstraint1.%sW0' % (grp, loc)
                                ctrlList.append(grp)

                            mc.select(cl=1)
                            mc.group(n=nom + '_ctrlGrp', em=1)
                            ctrlGrp = mc.ls(sl=1)[0]
                            for ctrl in ctrlList:
                                mc.parent(ctrl, ctrlGrp)

                            mc.select(cl=1)
                            mc.group(n=nom + '_grpOff', em=1)
                            jntGrp = mc.ls(sl=1)[0]
                            for loc in locList:
                                mc.parent(loc, jntGrp)

                            mc.select(cl=1)
                            group_out_liner_creation()
                            mc.parent(jntGrp, 'C_facial_jntGrp')
                            mc.parent(ctrlGrp, 'C_facial_ctrlGrp')
                            mc.select(cl=1)
                            mc.textScrollList('curveSelList', e=True, ra=1)
                            if check is True:
                                if side == 'C':
                                    mc.warning('中央の面は対称曲線にできないので、ミラーの作成はスキップされました。')

                    else:
                        raise mc.error('曲線の名前はユニークではありません プロセスが中断されました')
                else:
                    raise mc.error('実行前にカーブを追加してください。')
        else:
            raise mc.error('you need to have a custom before')
    else:
        mc.error('カーブには3つ以上のコントローラが必要です。')

def get_all_controllers_on_curves(*args):
    mc.textScrollList('CtrlOnCurve', e=1, ra=1)
    sel = mc.ls(sl=1)
    length = len(sel)
    if length == 1:
        sel = sel[0]
        if mc.objectType(sel, isType='transform'):
            if mc.objExists(sel + 'Shape'):
                type = ''
                try:
                    info = sel.split('_')
                    lenghtInfo = len(info)
                    type = info[(lenghtInfo - 1)]
                    if type == 'ctrl':
                        if mc.objExists('%s_%s_%s_%s' % (info[0], info[1], info[2], 'mp')):
                            if mc.objExists('%s_%s_crvOriginal' % (info[0], info[1])):
                                mc.button('restoreCrvBtn', l='Restore To Original Curve', e=1, en=1)
                                mc.button('rebuildCrvBtn', l='rebuild EP position curve', e=1, en=0)
                            else:
                                mc.button('restoreCrvBtn', l='Restore To Original Curve', e=1, en=0)
                                mc.button('rebuildCrvBtn', l='rebuild EP position curve', e=1, en=1)
                            try:
                                mc.select('%s_%s_*_ctrl' % (info[0], info[1]), r=True)
                                for elt in mc.ls(sl=1):
                                    nb = int(elt.split('_')[2])
                                    if nb > 1:
                                        mc.textScrollList('CtrlOnCurve', e=1, a=elt)

                                mc.select(sel, r=True)
                            except ZeroDivisionError:
                                pass

                except ZeroDivisionError:
                    pass
    else:
        raise mc.error('please select just one controller')

def send_UValue_to_slider_replace_controller(*args):
    ctrl = mc.textScrollList('CtrlOnCurve', q=1, si=1)[0]
    range_slider_replace(ctrl)
    mp = ctrl.split('ctrl')[0] + 'mp'
    getUValue = mc.getAttr(mp + '.uValue')
    mc.floatSliderGrp('replaceCtrlSys', e=1, v=getUValue)

def change_UValue_of_controller(*args):
    check = mc.checkBox('CheckBoxSymOnRebuildEP', q=True, v=True)
    ctrl = ''
    try:
        ctrl = mc.textScrollList('CtrlOnCurve', q=1, si=1)[0]
    except ZeroDivisionError:
        pass

    if ctrl != '':
        value = mc.floatSliderGrp('replaceCtrlSys', q=1, v=1)
        mp = ctrl.split('ctrl')[0] + 'mp'
        mc.setAttr(mp + '.uValue', value)
        if check is True:
            side = ctrl.split('_')[0]
            otherSide = ''
            if side == 'L':
                otherSide = 'R'
            elif side == 'R':
                otherSide = 'L'
            ctrlSym = '%s_%s' % (otherSide, ctrl.split(side + '_')[1])
            if mc.objExists(ctrlSym):
                mp2 = ctrlSym.split('ctrl')[0] + 'mp'
                mc.setAttr(mp2 + '.uValue', value)

def range_slider_replace(ctrl, *args):
    info = ctrl.split('_')
    ctrlNb = int(ctrl.split('_')[2])
    ctrlSup = '%s_%s_%s_ctrl' % (info[0], info[1], str(ctrlNb + 1))
    if not mc.objExists(ctrlSup):
        ctrlSup = ''
    else:
        ctrlSup = '%s_%s_%s_mp' % (info[0], info[1], str(ctrlNb + 1))
    ctrlMin = '%s_%s_%s_ctrl' % (info[0], info[1], str(ctrlNb - 1))
    if not mc.objExists(ctrlMin):
        ctrlMin = ''
    else:
        ctrlMin = '%s_%s_%s_mp' % (info[0], info[1], str(ctrlNb - 1))
    if ctrlMin != '':
        v = mc.getAttr('%s.uValue' % ctrlMin)
        mc.floatSliderGrp('replaceCtrlSys', e=True, min=v)
    else:
        mc.floatSliderGrp('replaceCtrlSys', e=True, min=0)
    if ctrlSup != '':
        v = mc.getAttr('%s.uValue' % ctrlSup)
        mc.floatSliderGrp('replaceCtrlSys', e=True, max=v)
    else:
        mc.floatSliderGrp('replaceCtrlSys', e=True, max=1)

def rebuild_EP_position_curve(*args):
    testEmpty = 0
    ctrlName = None
    try:
        ctrlName = mc.textScrollList('CtrlOnCurve', q=1, ai=1)
        testEmpty = len(ctrlName)
    except ZeroDivisionError:
        pass

    print(testEmpty)
    if testEmpty > 0:
        sides = []
        side = ctrlName[0].split('_')[0]
        sides.append(side)
        result = mc.confirmDialog(title='Symmetry Request', message='対称的なカーブを作りますか？', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
        if result == 'Yes':
            if side == 'L':
                if mc.objExists('R_%s_crv' % ctrlName[0].split('_')[1]):
                    if mc.objExists('R_%s_1_ctrl' % ctrlName[0].split('_')[1]):
                        sides.append('R')
            elif side == 'R':
                if mc.objExists('L_%s_crv' % ctrlName[0].split('_')[1]):
                    if mc.objExists('L_%s_1_ctrl' % ctrlName[0].split('_')[1]):
                        sides.append('L')
        for side in sides:
            name = side + '_' + ctrlName[0].split('_')[1]
            crv = name + '_crv'
            mc.select('%s_*_loc' % name, r=True)
            ctrls = mc.ls(sl=1)
            ctrlPosList = get_record_position_of_location(ctrls)
            lenght = len(ctrlPosList)
            loc1pos = mc.getAttr('%s_1_mp.uValue' % name)
            span = lenght
            if loc1pos == 0:
                span = span - 1
            crvTMP = mc.duplicate(crv, rr=True, n=crv + 'TMP')[0]
            mel.eval('rebuildCurve -ch 0 -rpo 1 -rt 0 -end 1 -kr 2 -kcp 0 -kep 1 -kt 0 -s ' + str(span) + ' -d 3 -tol 0.01 "' + crvTMP + '";')
            for loc in ctrlPosList:
                locPosWorld = mc.xform(loc, q=True, ws=True, t=True)
                epToChange = int(loc.split('_')[2])
                epToChange = epToChange - 1
                mc.select(crvTMP + '.ep[' + str(epToChange) + ']', r=True)
                editPointSel = crvTMP + '.ep[' + str(epToChange) + ']'
                mc.move(locPosWorld[0], locPosWorld[1], locPosWorld[2], a=True, ws=True)

            for loc in ctrlPosList:
                mp = loc.split('loc')[0] + 'mp'
                mc.disconnectAttr(crv + 'Shape.worldSpace[0]', mp + '.geometryPath')
                mc.connectAttr(crvTMP + 'Shape.worldSpace[0]', mp + '.geometryPath', f=True)

            curveOri = mc.rename(crv, crv + 'Original')
            mc.rename(crvTMP, crvTMP.split('TMP')[0])

def get_record_position_of_location(ctrls, *args):
    eltPosList = DictionnaireOrdonne()
    for elt in ctrls:
        posElt = mc.xform(elt, q=1, ws=1, t=1)
        eltPosList[elt] = posElt
    eltPosList.sort()
    return eltPosList

def restore_to_original_curve(*args):
    ctrlName = mc.textScrollList('CtrlOnCurve', q=1, ai=1)
    side = ctrlName[0].split('_')[0]
    name = '%s_%s' % (side, ctrlName[0].split('_')[1])
    crv = '%s_crv' % name
    curveOri = crv + 'Original'
    if mc.objExists(curveOri):
        ctrlPosList = mc.ls('%s_*_loc' % name)
        for loc in ctrlPosList:
            mp = loc.split('loc')[0] + 'mp'
            mc.disconnectAttr(crv + 'Shape.worldSpace[0]', mp + '.geometryPath')
            mc.connectAttr(curveOri + 'Shape.worldSpace[0]', mp + '.geometryPath', f=True)

        mc.button('restoreCrvBtn', l='Restore To Original Curve', e=1, en=0)
        mc.button('rebuildCrvBtn', l='rebuild EP position curve', e=1, en=1)
        mc.delete(crv)
        mc.rename(curveOri, crv)
        curveOri = crv
        if mc.objExists('C_Head_Facial_Rig_crvGrp'):
            mc.parent(curveOri, 'C_Head_Facial_Rig_crvGrp')
        else:
            mc.parent(curveOri, w=True)

def add_head_joint(*args):
    headSel = mc.ls(sl=True)
    nbObj = len(headSel)
    if nbObj == 1:
        headSel = headSel[0]
        if mc.objectType(headSel, isType='joint'):
            mc.textScrollList('headSelList', e=True, ra=True)
            mc.textScrollList('headSelList', e=True, append=headSel)
            mc.select(cl=1)
        else:
            mc.select(cl=1)
            mc.textScrollList('headSelList', e=True, ra=True)
            raise mc.error('ジョイントを必要とします。')
    else:
        raise mc.error('Please select just one element')

def add_head_controller(*args):
    headCtrlSel = mc.ls(sl=1)
    nbObj = len(headCtrlSel)
    if nbObj == 1:
        headCtrl = headCtrlSel[0]
        shape = mc.listRelatives(headCtrl)[0]
        if mc.objectType(shape, isType='nurbsCurve') or mc.objectType(shape, isType='nurbsSurface'):
            mc.textScrollList('headCtrlList', e=True, ra=True)
            mc.textScrollList('headCtrlList', e=True, append=headCtrl)
            mc.select(cl=1)
            mc.warning(headCtrl + ' is now set for Head Control')
        else:
            mc.select(cl=1)
            raise mc.error('you must do select a nurbs object')
    else:
        raise mc.error('Please select just one object')

def add_control_list(*args):
    typeList = ['eyeBrow', 'upperLid', 'lowerLid', 'upperCheeks', 'cheeks', 'nose', 'crease', 'upperLip', 'lowerLip']
    ret = 'no'
    ret2 = ''
    customList = mc.ls(sl=True)
    for elt in customList:
        mc.select(elt, r=True)
        elt = mc.ls(sl=1)[0]
        if not mc.objectType(elt, isType='joint'):
            elt = mc.listRelatives(elt)[0]
            if mc.objectType(elt, isType='nurbsCurve'):
                ret = 'ok'
            elif mc.objectType(elt, isType='nurbsSurface'):
                ret = 'ok'
            if ret == 'ok':
                name = elt.split('_')
                ctrlGrp = '%s_%s_ctrlGrp' % (name[0], name[1])
                jnt = '%s_%s_grpOff' % (name[0], name[1])
                eltShape = mc.listRelatives(elt)
                for type in typeList:
                    if name[1] != type:
                        if mc.objExists(jnt):
                            if mc.textScrollList('CustomCtrlList', si=ctrlGrp, ex=True) is False:
                                mc.textScrollList('CustomCtrlList', e=True, append=ctrlGrp)
                            else:
                                try:
                                    mc.textScrollList('CustomCtrlList', q=True, si=True)
                                    mc.textScrollList('CustomCtrlList', e=True, ri=ctrlGrp)
                                    mc.textScrollList('CustomCtrlList', e=True, append=ctrlGrp)
                                except ZeroDivisionError:
                                    pass
                        else:
                            mc.warning('no joint relationship has been found with this selection')

def remove_control_list(*args):
    itemSel = mc.textScrollList('CustomCtrlList', q=1, si=1)
    mc.textScrollList('CustomCtrlList', e=1, ri=itemSel)

def execute_head(*args):
    sides = ['L', 'R', 'C']
    jntList = []
    typeList = ['crv', 'crvOriginal']
    customList = []
    scriptNameList = ['eyeBrow', 'upperLid', 'upperLip', 'lowerLid', 'upperCheeks', 'cheeks', 'nose', 'crease', 'lowerLip', 'upperLip']
    headCtrl = mc.textScrollList('headCtrlList', q=1, ai=1)[0]
    headJnt = mc.textScrollList('headSelList', q=1, ai=1)[0]
    if headCtrl != '':
        if headJnt != '':
            customCtrl = mc.textScrollList('CustomCtrlList', q=1, ai=1)
            if customCtrl != '':
                mc.select(customCtrl, r=True)
                customCtrlList = mc.ls(sl=1)
                length = len(customCtrlList)
                if length > 0:
                    for elt in customCtrlList:
                        mc.select(elt, r=True)
                        ctrl = mc.ls(sl=1)[0]
                        name = ctrl.split('_')[1]
                        customList.append(name)

            for elt in scriptNameList:
                customList.append(elt)

            for side in sides:
                for type in typeList:
                    for elt in customList:
                        if mc.objExists('%s_%s_%s' % (side, elt, type)):
                            if not mc.objExists('C_Head_Facial_Rig_crvGrp'):
                                mc.group(n='C_Head_Facial_Rig_crvGrp', em=True)
                                mc.parent('C_Head_Facial_Rig_crvGrp', headCtrl)
                            print('%s_%s_%s' % (side, elt, type))
                            try:
                                if type == 'crv':
                                    mc.parent('%s_%s_%s' % (side, elt, type), 'C_Head_Facial_Rig_crvGrp')
                                elif type == 'crvOriginal':
                                    if not mc.objExists('C_Head_Facial_Rig_OrignalCurves_grp'):
                                        mc.group(n='C_Head_Facial_Rig_OrignalCurves_grp', em=True)
                                    mc.parent('%s_%s_%s' % (side, elt, type), 'C_Head_Facial_Rig_OrignalCurves_grp')
                            except ZeroDivisionError:
                                pass

            try:
                mc.parent('C_facial_ctrlGrp', headCtrl)
            except ZeroDivisionError:
                pass

            try:
                mc.parent('C_facial_jntGrp', headCtrl)
            except ZeroDivisionError:
                pass

            if not mc.objExists('xtra_toHide'):
                mc.group(n='xtra_toHide', em=True)
            if not mc.objExists('C_Facial_Pin_Controller_grp'):
                mc.group(n='C_Facial_Pin_Controller_grp', em=1)
            try:
                mc.parent('C_Facial_Pin_Controller_grp', 'xtra_toHide')
            except ZeroDivisionError:
                pass

            try:
                mc.parent('C_Head_Facial_Rig_OrignalCurves_grp', 'xtra_toHide')
            except ZeroDivisionError:
                pass

            try:
                mc.parent('C_Head_Facial_Rig_crvGrp', 'xtra_toHide')
            except ZeroDivisionError:
                pass
            try:
                mc.setAttr('xtra_toHide.visibility', 0)
            except ZeroDivisionError:
                pass
            try:
                mc.delete('C_CONTROLLER_grp')
            except ZeroDivisionError:
                pass

def add_head_geometry(*args):
    headSel = mc.ls(sl=True)
    nbObj = len(headSel)
    if nbObj == 1:
        shape = mc.listRelatives(headSel[0])[0]
        if mc.objectType(shape, isType='mesh'):
            mc.textScrollList('headGeoList', e=True, ra=True)
            mc.textScrollList('headGeoList', e=True, append=headSel)
            mc.select(cl=1)
        else:
            mc.textScrollList('headGeoList', e=True, ra=True)
            raise mc.error('メッシュオブジェクトを入れる必要があります。')

def refresh_joint(*args):
    mc.textScrollList('jntListScript', e=1, ra=1)
    mc.select('*grpOff', r=True)
    mc.select('*_ctrl_grpOff', d=True)
    list = mc.ls(sl=1)
    jntList = []
    print('list = %s' % list)
    for jnt in list:
        jnt = mc.ls(jnt)[0]
        name = jnt.split('grpOff')[0]
        mc.select(name + '*jnt', r=True)
        joints = mc.ls(sl=1)
        for elt in joints:
            jntList.append(elt)
            mc.textScrollList('jntListScript', e=1, append=elt)

def add_to_current_skin(*args):
    headGeo = ''
    try:
        headGeo = mc.textScrollList('headGeoList', q=1, ai=1)[0]
    except ZeroDivisionError:
        pass

    if headGeo != '':
        headGeoChild = mc.listRelatives(headGeo)[0]
        jntList2 = []
        jntList = mc.textScrollList('jntListScript', q=1, ai=1)
        lenList = len(jntList)
        for i in range(lenList):
            mc.select(jntList[i], r=True)
            sel = mc.ls(sl=1)[0]
            jntList2.append(sel)

        if headGeo != '':
            if jntList2 != '':
                mc.select(cl=1)
                mc.select(jntList2, headGeo, r=True)
                mel.eval('AddInfluenceOptions;')
    else:
        mc.error('please check your head geometry field')

def skin_tool(*args):
    try:
        headGeo = mc.textScrollList('headGeoList', q=1, ai=1)
        mc.select(headGeo, r=True)
        headGeo = mc.ls(sl=1)[0]
        mel.eval('ArtPaintSkinWeightsToolOptions;')
    except ZeroDivisionError:
        raise mc.error('Head Geometry fieldが空でないことを確認してください。')

def delete_skin_and_make_skin(*args):
    try:
        headGeo = mc.textScrollList('headGeoList', q=1, ai=1)
        mc.select(headGeo, r=True)
        headGeo = mc.ls(sl=1)[0]
        headChilds = mc.listRelatives(headGeo)[0]
        skin = ''
        headShape = mc.listRelatives(headChilds)[0]
        attrsHead = mc.listConnections(headShape)
        for attr in attrsHead:
            type = mc.objectType(attr)
            if type == 'skinCluster':
                skin = attr
                mc.skinCluster(skin, e=1, ub=1)
                break

        jntList = mc.textScrollList('jntListScript', q=1, ai=1)
        mc.select(cl=1)
        for jnt in jntList:
            mc.select(jnt, add=True)

        mc.select(headShape, r=True)
        mel.eval('SmoothBindSkin;')
    except ZeroDivisionError:
        raise mc.error('please check if your head geo field is not empty')

def add_button_of_additional_part(*args):
    sel = mc.ls(sl=1)
    if len(sel) > 0:
        for elt in sel:
            listToAdd = mc.textScrollList('addAdditionnalCtrl', q=True, ai=True)
            info = []
            test1 = 'no'
            if mc.objectType(elt, isType='joint'):
                info = []
                try:
                    info = elt.split('_')
                except ZeroDivisionError:
                    pass

                if len(info) == 4:
                    test1 = 'ok'
            elif mc.objectType(elt, isType='transform'):
                if mc.objExists(elt + 'Shape') and mc.objectType(elt + 'Shape', isType='nurbsSurface'):
                    info = []
                    try:
                        info = elt.split('_')
                    except ZeroDivisionError:
                        pass

                    if len(info) == 4:
                        test1 = 'ok'
            if test1 == 'ok':
                test2 = 'no'
                if mc.objExists('%s_%s_%s_ctrl' % (info[0], info[1], info[2])):
                    if mc.objExists('%s_%s_ctrlGrp' % (info[0], info[1])):
                        if mc.objExists('%s_%s_crv' % (info[0], info[1])):
                            if mc.objExists('%s_%s_crvOriginal' % (info[0], info[1])):
                                elt = '%s_%s_ctrlGrp' % (info[0], info[1])
                                test2 = 'ok'
                            else:
                                mc.error('カーブを追加しようとする前に、このカーブ : %s_%s_crv を再構築する必要があります。' % (info[0], info[1]))
                if test2 == 'ok':
                    try:
                        if len(listToAdd) > 0:
                            testAdd = 'no'
                            for ctrl in listToAdd:
                                if ctrl != elt:
                                    testAdd = 'ok'
                                else:
                                    testAdd = 'no'

                            if testAdd == 'ok':
                                mc.textScrollList('addAdditionnalCtrl', e=True, a=elt)
                    except ZeroDivisionError:
                        mc.textScrollList('addAdditionnalCtrl', e=True, a=elt)

    else:
        mc.error('please select one or many controllers to add')

def remove_button_of_additional_part(*args):
    sel = mc.textScrollList('addAdditionnalCtrl', q=1, si=1)
    mc.textScrollList('addAdditionnalCtrl', e=1, ri=sel)

def validate_additional_part(*args):
    headGeo = ''
    try:
        headGeo = mc.textScrollList('headGeoList', q=1, ai=1)[0]
    except ZeroDivisionError:
        pass

    jntListToAdd = []
    additionalList = []
    try:
        additionalList = mc.textScrollList('addAdditionnalCtrl', q=1, ai=1)
    except ZeroDivisionError:
        pass

    if headGeo != '':
        if len(additionalList) > 0:
            for elt in additionalList:
                info = elt.split('_')
                listJnt = mc.ls('%s_%s_*_jnt' % (info[0], info[1]))
                for jnt in listJnt:
                    jntListToAdd.append(jnt)

            if len(jntListToAdd) > 0:
                mc.select(jntListToAdd, headGeo, r=True)
                mel.eval('AddInfluenceOptions;')
    else:
        raise mc.error('Please add your head geometry into the proper field before')

def correct_custom_name(*args):
    r = re.compile('([^a-zA-Z])')
    txt = mc.textField('otherNameList', q=True, tx=True)
    txtOk = r.sub('', txt)
    mc.textField('otherNameList', e=True, tx=txtOk)

def group_out_liner_creation(*args):
    if not mc.objExists('C_SKELETON_grp'):
        mc.group(n='C_SKELETON_grp', em=True)
        mc.select(cl=1)
    if not mc.objExists('C_facial_jntGrp'):
        mc.group(n='C_facial_jntGrp', em=True)
        try:
            mc.parent('C_facial_jntGrp', 'C_SKELETON_grp')
        except ZeroDivisionError:
            pass
        mc.select(cl=1)
    if not mc.objExists('C_facial_ctrlGrp'):
        mc.group(n='C_facial_ctrlGrp', em=True)
        mc.select(cl=1)


