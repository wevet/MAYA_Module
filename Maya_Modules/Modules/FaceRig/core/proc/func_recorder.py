# -*- coding: utf-8 -*-

import maya.cmds as mc, maya.mel as mel, dictOrdo
reload(dictOrdo)
from dictOrdo import DictionnaireOrdonne
import func_animEditMode
reload(func_animEditMode)
from func_animEditMode import *

def addHeadControllerToUINlendShape(*args):
    sel = mc.ls(sl=1)
    if len(sel) == 1:
        sel = sel[0]
        try:
            shape = mc.listRelatives(sel)[0]
            if mc.objectType(shape, isType='nurbsCurve') or mc.objectType(shape, isType='nurbsSurface'):
                mc.textScrollList('headCtrlBlendShape', e=True, ra=True)
                mc.textScrollList('headCtrlBlendShape', e=True, a=sel)
        except:
            mc.textScrollList('headCtrlBlendShape', e=True, ra=True)
            raise mc.error('please select a nurbs curve or nurbs object')

    else:
        mc.textScrollList('headCtrlBlendShape', e=True, ra=True)
        raise mc.error('please select just one element')


def addJawJntLip2(*args):
    try:
        mc.textScrollList('jawJntList2', e=1, ra=1)
        sel = mc.ls(sl=1)
        lenSel = len(sel)
        if lenSel == 1:
            sel = sel[0]
            if mc.objectType(sel, isType='joint'):
                mc.textScrollList('jawJntList2', e=1, append=sel)
    except:
        mc.error('You must do select your jaw joint')


def addJawCtrlForRecord(*args):
    ctrl = ''
    try:
        ctrl = mc.ls(sl=1)[0]
    except:
        pass

    if ctrl != '':
        if mc.objectType(ctrl, isType='transform'):
            shape = ''
            try:
                shape = mc.listRelatives(ctrl)[0]
            except:
                pass

            if shape != '':
                if mc.objectType(shape, isType='nurbsSurface') or mc.objectType(shape, isType='nurbsCurve'):
                    mc.textScrollList('jawCtrlList', e=True, ra=True)
                    mc.textScrollList('jawCtrlList', e=True, a=ctrl)
                else:
                    mc.error('Your selected controller is not a nurbs surface')
        else:
            mc.error('Please select a nurbs surface')
    else:
        mc.error('no selection found.')


def refreshBldMouthCrvList(*args):
    mc.textScrollList('listBldCrvMouth', e=1, ra=1)
    mc.select(cl=1)
    try:
        mc.select('*_Open_bld_crv', r=True)
    except:
        pass

    try:
        mc.select('*_Twist*_bld_crv', add=True)
    except:
        pass

    try:
        mc.select('*_Side*_bld_crv', add=True)
    except:
        pass

    try:
        mc.select('*_Jaw*_bld_crv', add=True)
    except:
        pass

    typeList = []
    crvList = mc.ls(sl=1)
    if len(crvList) > 0:
        for crv in crvList:
            type = crv.split('_')[2]
            if type != 'bld':
                if len(typeList) != 0:
                    test = 0
                    for elt in typeList:
                        if elt == type:
                            test = 0
                            break
                        else:
                            test = 1

                    if test != 0:
                        typeList.append(type)
                else:
                    typeList.append(type)

        for elt in typeList:
            mc.textScrollList('listBldCrvMouth', e=1, append=elt)

    else:
        raise mc.error('no blend shape correction for mouth was found')


def deleteBldMouthSelected(*args):
    fCtrl = 'Facial_Rig_ctrl'
    if mc.objExists(fCtrl):
        mode = mc.getAttr('%s.mode' % fCtrl)
        if mode == 0:
            sel = ''
            try:
                sel = mc.textScrollList('listBldCrvMouth', q=True, ams=False, si=True)[0]
            except:
                pass

            if len(sel) > 0:
                jawCtrl = ''
                ctrlFAttr = ''
                if sel.startswith('Open'):
                    ctrlFAttr = 'Facial_Rig_ctrl.open_mouth'
                else:
                    if sel.startswith('Side'):
                        ctrlFAttr = 'Facial_Rig_ctrl.side_mouth'
                        sel = 'Side*'
                    elif sel.startswith('Twist'):
                        ctrlFAttr = 'Facial_Rig_ctrl.twist_mouth'
                        sel = 'Twist*'
                    testToContinue = 1
                    IBFound = 0
                    selInfo = sel.split('_')
                    checkIB = []
                    try:
                        checkIB = mc.ls('*%s*IB*' % sel)
                    except:
                        checkIB = []

                if len(checkIB) > 0:
                    IBFound = 1
                    result = mc.confirmDialog(title='Confirm', message='An In Between Expression was found for this curve\n This In Between will be deleted with his blend curve\n Do you want continue ?', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                    if result == 'No':
                        testToContinue = 0
                    else:
                        testToContinue = 1
                if testToContinue == 1:
                    if IBFound == 1:
                        ibList = mc.ls('*%s*IB*' % sel)
                        mc.delete(ibList)
                    listCons = mc.listConnections(ctrlFAttr, s=True, scn=True)
                    for con in listCons:
                        if con.endswith('bld_crv') == False:
                            jawCtrl = con
                            break

                    mc.select('*%s_bld_crv' % sel, r=True)
                    try:
                        mc.select('*_bld*%s_bld_crv' % sel, d=True)
                    except:
                        pass

                    crvList = mc.ls(sl=1)
                    for crv in crvList:
                        info = crv.split('_')
                        name = info[0] + '_' + info[1]
                        nameAttr = info[2]
                        mc.select('%s_*_%s_bld_recorder' % (name, nameAttr), r=True)
                        listLoc = mc.ls(sl=1)
                        mc.delete(listLoc)
                        bld = info[0] + '_' + info[1] + '_bld'
                        blendTargets = mc.listAttr(bld + '.w', m=True)
                        i = 0
                        for target in blendTargets:
                            if target == crv:
                                try:
                                    mc.setAttr('%s.%s' % (bld, target), 0)
                                    break
                                except:
                                    connection = mc.listConnections('%s.%s' % (bld, target), p=True)
                                    mc.disconnectAttr(connection[1], '%s.%s' % (bld, target))

                            else:
                                i = i + 1

                        history = mc.listHistory(bld, f=True, lf=True)
                        shape = mc.ls(history, type=('mesh', 'nurbsSurface', 'nurbsCurve'))
                        object = mc.listRelatives(shape, fullPath=True, parent=True, type='transform')[0]
                        mc.blendShape(bld, edit=True, remove=True, t=(object, i, crv, 1.0))
                        mc.delete(crv)
                        try:
                            mc.delete(name + '_bld_' + crv)
                        except:
                            pass

                        newBlendTargets = mc.listAttr(bld + '.w', m=True)
                        if newBlendTargets == None:
                            mc.delete(bld)
                        testAttr = mc.ls('*%s*_bld_crv' % nameAttr)
                        lenght = len(testAttr)
                        if lenght == 0:
                            if nameAttr == 'Open':
                                try:
                                    mc.select('openMouth_DivideRot*', 'openMouth_setRange', r=True)
                                    mc.delete(mc.ls(sl=1))
                                    for axis in ['X', 'Y', 'Z']:
                                        try:
                                            mc.disconnectAttr('%s.rotate%s' % (jawCtrl, axis), 'Facial_Rig_ctrl.open_mouth')
                                        except:
                                            pass

                                except:
                                    pass

                            elif nameAttr != 'Jaw':
                                if nameAttr != 'JawDown':
                                    if nameAttr != 'JawNeg':
                                        nameAttr = nameAttr.split('M')[0]
                                        if nameAttr == 'Side':
                                            lenght2 = len(mc.ls('*%sM*bld_crv' % nameAttr))
                                            if lenght2 == 0:
                                                for axis in ['X', 'Y', 'Z']:
                                                    try:
                                                        mc.disconnectAttr('%s.rotate%s' % (jawCtrl, axis), 'Facial_Rig_ctrl.side_mouth')
                                                    except:
                                                        pass

                                        else:
                                            lenght3 = len(mc.ls('*%sM*bld_crv' % nameAttr))
                                            if lenght3 == 0:
                                                for axis in ['X', 'Y', 'Z']:
                                                    try:
                                                        mc.disconnectAttr('%s.rotate%s' % (jawCtrl, axis), 'Facial_Rig_ctrl.twist_mouth')
                                                    except:
                                                        pass

                        listToDel = []
                        actuallyOnList = mc.textScrollList('listBldCrvMouth', q=True, ai=True)
                        try:
                            sel = sel.split('*')[0]
                        except:
                            pass

                        for elt in actuallyOnList:
                            if elt.startswith(sel):
                                mc.textScrollList('listBldCrvMouth', e=True, ri=elt)
                                mc.warning('Your expression named : %s is now correctly deleted' % elt)

            else:
                mc.error('No expression was selected into the blendshape mouth list')
        else:
            mc.error('You need to be in Edit Mode for delete an expression')
    else:
        mc.error('the facial rig ctrl was not found.')
    return


def helpToFixBldSymMenuMouth(*args):
    sel = ''
    try:
        crv = textScrollList('listBldCrv', q=True, si=True)
        sel = mc.ls(sl=1)[0]
    except:
        pass

    if sel != '':
        try:
            info = sel.split('_')
        except:
            pass

        lenght = len(info)
        if info[(lenght - 1)] == 'crv' and info[(lenght - 2)] == 'bld':
            HelpToFixBldUI()
            mc.textField('bldShapeToRepair', e=True, tx=sel)
            locList = []
            mc.select('%s_%s_*_%s_bld_recorder' % (info[0], info[1], info[2]), r=True)
            locList = mc.ls(sl=1)
            if len(locList) > 0:
                for loc in locList:
                    mc.textScrollList('RecLocList', e=True, a=loc)


def refreshBldCrvList(*args):
    mc.textScrollList('listBldCrv', e=1, ra=1)
    typeList = []
    try:
        mc.select('*_bld_crv', r=True)
        try:
            mc.select('*_Open_bld_crv', d=True)
        except:
            pass

        try:
            mc.select('*_Twist*_bld_crv', d=True)
        except:
            pass

        try:
            mc.select('*_Side*_bld_crv', d=True)
        except:
            pass

        try:
            mc.select('*bldExp*', d=True)
        except:
            pass

        try:
            mc.select('*_Jaw*_bld_crv', d=True)
        except:
            pass

        for crv in mc.ls(sl=1):
            type = crv.split('_')[2]
            if len(typeList) != 0:
                test = 0
                for elt in typeList:
                    if elt == type:
                        test = 0
                        break
                    else:
                        test = 1

                if test != 0:
                    typeList.append(type)
            else:
                typeList.append(type)

        for name in typeList:
            mc.select('*%s_bld_crv' % name, r=True)
            try:
                mc.select('*bldExp*bld_crv', d=True)
            except:
                pass

            for crv in mc.ls(sl=1):
                mc.textScrollList('listBldCrv', e=1, append=crv)

    except:
        raise mc.error('no blend curve was found')


def selectBldCrvList(*args):
    try:
        sel = mc.textScrollList('listBldCrv', q=1, ams=1, si=1)
        mc.select(sel, r=True)
    except:
        raise mc.error('please select a curve in the dedicated text field')


def deleteSelBldCrvList(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            selList = []
            try:
                selList = mc.textScrollList('listBldCrv', q=1, si=1)
            except:
                pass

            try:
                if len(selList) > 0:
                    for sel in selList:
                        testToContinue = 1
                        IBFound = 0
                        selInfo = sel.split('_')
                        nameExpression = selInfo[2]
                        checkIB = []
                        try:
                            checkIB = mc.ls('*%s*IB*' % nameExpression)
                        except:
                            checkIB = []

                        if len(checkIB) > 0:
                            IBFound = 1
                            result = mc.confirmDialog(title='Confirm', message='An In Between Expression was found for this curve\n This In Between will be deleted with his blend curve\n Do you want continue ?', button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
                            if result == 'No':
                                testToContinue = 0
                                break
                            else:
                                testToContinue = 1
                        if testToContinue == 1:
                            mc.textScrollList('listBldCrv', e=1, ri=sel)
                            bld = '%s_%s_bldExp' % (selInfo[0], selInfo[1])
                            blendTargets = mc.listAttr(bld + '.w', m=True)
                            mc.setAttr('%s.%s' % (bld, sel), 0)
                            i = 0
                            for target in blendTargets:
                                if target == sel:
                                    break
                                else:
                                    i = i + 1

                            history = mc.listHistory(bld, f=True, lf=True)
                            shape = mc.ls(history, type=('mesh', 'nurbsSurface', 'nurbsCurve'))
                            object = mc.listRelatives(shape, fullPath=True, parent=True, type='transform')[0]
                            mc.blendShape(bld, edit=True, remove=True, t=(object, i, sel, 1.0))
                            try:
                                mc.deleteAttr('Facial_Rig_ctrl', at='%s_%s_%s' % (selInfo[0], selInfo[1], selInfo[2]))
                                mc.delete('%s_%s_%s' % (selInfo[0], selInfo[1], selInfo[2]))
                            except:
                                pass

                            mc.delete(sel)
                            try:
                                try:
                                    mc.delete(selInfo[0] + '_' + selInfo[1] + '_bldExp_' + sel)
                                except:
                                    pass

                            except:
                                pass

                            newBlendTargets = mc.listAttr(bld + '.w', m=True)
                            if newBlendTargets == None:
                                mc.delete(bld)
                            try:
                                mc.select('*%s_bld_crv' % selInfo[2], r=True)
                                mc.select('*bldExp_*_*_%s_bld_crv' % selInfo[2], d=True)
                                test = mc.ls(sl=1)
                            except:
                                try:
                                    mc.setAttr('%s.%s' % ('Facial_Rig_ctrl', selInfo[2]), lock=False)
                                    mc.deleteAttr('Facial_Rig_ctrl', at=selInfo[2])
                                    mc.warning('attribute %s was removed on Facial_Rig_ctrl' % selInfo[2])
                                except:
                                    pass

                            try:
                                mc.delete('%s_%s_*_%s_*_add*' % (selInfo[0], selInfo[1], selInfo[2]), '%s_%s_*_%s_*_min*' % (selInfo[0], selInfo[1], selInfo[2]))
                            except:
                                pass

                            try:
                                mc.delete('%s_%s*_%s_bld_recorder' % (selInfo[0], selInfo[1], selInfo[2]))
                                mc.warning('This element is correctly deleted : %s' % sel)
                            except:
                                pass

                            if IBFound == 1:
                                ibList = mc.ls('%s_%s*_%s*IB*' % (selInfo[0], selInfo[1], selInfo[2]))
                                mc.delete(ibList)

            except:
                mc.error('You must select one or some bld curve into the field before trying to delete.')

    return


def selectMirrorBlendShapeUI(*args):
    sel = mc.textScrollList('listBldCrv', q=1, si=1)
    mirrorSelect = []
    if len(sel) > 0:
        for elt in sel:
            info = elt.split('_')
            side = info[0]
            if info[0] == 'L':
                side = 'R'
            elif info[0] == 'R':
                side = 'L'
            if mc.objExists('%s_%s_%s_bld_crv' % (side, info[1], info[2])):
                mirrorSelect.append('%s_%s_%s_bld_crv' % (side, info[1], info[2]))
            else:
                mirrorSelect.append(elt)
            mc.textScrollList('listBldCrv', e=1, di=elt)

    if len(mirrorSelect) > 0:
        for elt in mirrorSelect:
            mc.textScrollList('listBldCrv', e=1, si=elt)

        mc.select(mirrorSelect, r=True)


def testBlendShape(*args):
    bldNodeName = ''
    value = mc.floatSliderGrp('testIt', q=1, v=1)
    try:
        crvs = mc.textScrollList('listBldCrv', q=1, ams=True, si=1)
        for crv in crvs:
            info = crv.split('_')
            bldNodeName = '%s_%s_bldExp' % (info[0], info[1])
            mc.setAttr(bldNodeName + '.' + crv, value)

    except:
        raise mc.error('please select a blendshape into the textScrollList before')


def fixBldLocSelected(*args):
    sel = mc.textScrollList('RecLocList', q=True, ams=True, si=True)
    axis = mc.radioButtonGrp('AxisToRepair', q=True, sl=True)
    if axis == 1:
        axis = 'X'
    elif axis == 2:
        axis = 'Y'
    else:
        axis = 'Z'
    if len(sel) > 0:
        for loc in sel:
            initVal = mc.getAttr('%s.rotate%s' % (loc, axis))
            mc.setAttr('%s.rotate%s' % (loc, axis), initVal * -1)
            mc.warning('%s is now fixed on the %s rotation axis' % (loc, axis))

    else:
        raise RuntimeError('Please select a locator into the list before')


def fixBldLocAll(*args):
    sel = mc.textScrollList('RecLocList', q=True, ai=True)
    axis = mc.radioButtonGrp('AxisToRepair', q=True, sl=True)
    if axis == 1:
        axis = 'X'
    elif axis == 2:
        axis = 'Y'
    else:
        axis = 'Z'
    if len(sel) > 0:
        for loc in sel:
            initVal = mc.getAttr('%s.rotate%s' % (loc, axis))
            mc.setAttr('%s.rotate%s' % (loc, axis), initVal * -1)
            mc.warning('%s is now fixed on the %s rotation axis' % (loc, axis))


def addScaleConstraintOnEachController(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            mc.select('C_facial_ctrlGrp', r=True, hi=True)
            mc.select('C_facial_ctrlGrp', d=True)
            listElement = mc.ls(sl=1)
            listClean = []
            for elt in listElement:
                if elt.endswith('_ctrl') == True:
                    listClean.append(elt)

            if len(listClean) > 0:
                for ctrl in listClean:
                    nameCtrl = ctrl.split('ctrl')[0]
                    mc.makeIdentity(ctrl, a=1, s=True, pn=True)
                    mc.select(ctrl, nameCtrl + 'jnt', r=True)
                    mc.scaleConstraint(mo=1)
                    constraint2 = '%s' % (nameCtrl + 'jnt_scaleConstraint1.' + ctrl + 'W0')

                mc.select('*_jnt', r=True)
                jntList = mc.ls(sl=1)
                for jnt in jntList:
                    try:
                        constraint = '%s_scaleConstraint1' % jnt
                        if mc.objExists(constraint):
                            mc.select(jnt, r=True)
                            grp = '%s_Scale_Offset' % jnt
                            if not mc.objExists(grp):
                                mc.group(n=grp)
                            mc.parent(constraint, grp)
                        ctrl = '%sctrl' % jnt.split('jnt')[0]
                        mc.select(ctrl, '%s_Scale_Offset' % jnt, r=True)
                        mc.scaleConstraint(mo=1)
                    except:
                        pass

                mc.warning('All curve controllers are now constraint in scale on itself joint')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')


def recordWithSelectionMouth(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvList = []
            CSel = mc.textScrollList('CenterRecordCrvsList', q=1, si=1)
            RSel = mc.textScrollList('RightRecordCrvsList', q=1, si=1)
            LSel = mc.textScrollList('LeftRecordCrvsList', q=1, si=1)
            try:
                for crv in CSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in RSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in LSel:
                    crvList.append(crv)

            except:
                pass

            lenght = len(crvList)
            if len(crvList) > 0:
                TMPBlendShapeCrv(crvList)
                validateMouthRecorder()
                mc.deleteUI('BlendShapeUIRecorderMouth')
            else:
                mc.error('You need to select some curve to record this expression')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')


def recordWithAllCurvesMouth(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvList = []
            CSel = mc.textScrollList('CenterRecordCrvsList', q=1, ai=1)
            RSel = mc.textScrollList('RightRecordCrvsList', q=1, ai=1)
            LSel = mc.textScrollList('LeftRecordCrvsList', q=1, ai=1)
            try:
                for crv in CSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in RSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in LSel:
                    crvList.append(crv)

            except:
                pass

            if len(crvList) > 0:
                TMPBlendShapeCrv(crvList)
                validateMouthRecorder()
                mc.deleteUI('BlendShapeUIRecorderMouth')
            else:
                mc.error('No facial has been found to record expression')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')


def validateMouthRecorder(*args):
    fCtrl = 'Facial_Rig_ctrl'
    negValueEnable = mc.checkBox('NegValueMouthCreation', q=True, v=True)
    if mc.objExists(fCtrl):
        mode = mc.getAttr(fCtrl + '.mode')
        if mode == 0:
            testToContinue = 0
            nodeList = mc.textScrollList('HiddenTMPNodeList', q=1, ai=1)
            name = mc.radioButtonGrp('nameAttr', q=1, sl=1)
            nameAttr = ''
            if name == 1:
                name = 'Open'
            elif name == 2:
                name = 'Side'
            elif name == 3:
                name = 'Twist'
            elif name == 4:
                jawNameQuery = mc.radioButtonGrp('nameAttrJaw', q=True, sl=True)
                name = ''
                if jawNameQuery == 1:
                    name = 'Jaw'
                elif jawNameQuery == 2:
                    name = 'JawNeg'
                elif jawNameQuery == 3:
                    name = 'JawDown'
            if name == 'Jaw' or name == 'JawNeg' or name == 'JawDown':
                axis = mc.radioButtonGrp('axisTrans2', q=True, sl=True)
            else:
                axis = mc.radioButtonGrp('axisRot2', q=True, sl=True)
                if axis == 1:
                    axis = 'X'
                elif axis == 2:
                    axis = 'Y'
                else:
                    axis = 'Z'
            jawJnt = mc.textScrollList('jawJntList2', q=1, ai=True)[0]
            valueMaxRange = 1
            if name.startswith('Jaw') == False:
                if name != 'JawNeg':
                    if name != 'JawDown':
                        valueMaxRange = mc.floatField('MaxValueActivation', q=True, v=True)
                        if negValueEnable == True:
                            valueMaxRange = valueMaxRange * -1
            if len(nodeList) > 0:
                for crv in nodeList:
                    crvBld = crv.split('_')[0] + '_' + crv.split('_')[1] + '_' + name + '_bld_crv'
                    if mc.objExists(crvBld):
                        mc.warning('A blendshape curve named %s already exists, please change the name of your expression' % crvBld)
                        validateMouthRecorder()
                        break
                    else:
                        testToContinue = 1

            if jawJnt != '':
                if valueMaxRange >= 1 or valueMaxRange <= -1:
                    if testToContinue == 1:
                        try:
                            for x in ('open_mouth', 'side_mouth', 'twist_mouth', 'jaw',
                                      'jawDown'):
                                try:
                                    mc.setAttr('cc_facial_expressions.%s' % x, 0)
                                except:
                                    pass

                        except:
                            pass

                        mc.textScrollList('HiddenTMPNodeList', e=1, ra=1)
                        mc.textScrollList('RecordPosCtrl', e=1, ra=1)
                        loop = 1
                        if name != 'Open':
                            if name != 'Jaw':
                                if name != 'JawNeg':
                                    if name != 'JawDown':
                                        loop = 2
                        for i in range(loop):
                            if loop != 1:
                                bldAttr = ''
                                if i == 0:
                                    bldAttr = 'Max'
                                else:
                                    bldAttr = 'Min'
                                nameAttr = '%s%s%s' % (name, bldAttr, str(valueMaxRange).split('.')[0])
                            else:
                                nameAttr = name
                            if i == 0:
                                for crv in nodeList:
                                    minMax = ''
                                    crvNameTMP = crv.split('_')[0] + '_' + crv.split('_')[1] + '_crvTMP'
                                    crvOri = crvNameTMP.split('TMP')[0]
                                    nodeNameTMP = '%s_1_POC_crv' % crvNameTMP
                                    Rcrv = ''
                                    newName = crv.split('_')[0] + '_' + crv.split('_')[1] + '_' + nameAttr + '_bld_crv'
                                    mc.select('%s_*_POC_loc' % crvNameTMP, r=True)
                                    locList = mc.ls(sl=1)
                                    lenLocTMP = len(locList)
                                    if not mc.objExists('C_faceCurvesBld_grp'):
                                        mc.group(n='C_faceCurvesBld_grp', em=1)
                                        mel.eval('HideSelectedObjects;doHideObjects true;')
                                    for i in range(lenLocTMP):
                                        mc.delete('%s_%s_POC_loc' % (crvNameTMP, str(i + 1)))
                                        if i != 0:
                                            mc.delete('%s_%s_POC_crv' % (crvNameTMP, str(i + 1)))
                                        else:
                                            mc.rename('%s_1_POC_crv' % crvNameTMP, newName)

                                    mc.parent(newName, 'C_faceCurvesBld_grp')
                                    getBackLocTMPToCrv(crvNameTMP)
                                    mc.select(newName, crvOri, r=True)
                                    createBldShape()
                                    mc.warning('%s has been created' % newName)
                                    mc.select(crv.split('crv')[0] + '*ctrl', r=True)
                                    listCtrl = mc.ls(sl=1)
                                    nbLoc = len(listCtrl)
                                    for i in range(nbLoc):
                                        mc.select(listCtrl[i], r=True)
                                        ctrl = mc.ls(sl=1)[0]
                                        info = ctrl.split('_')
                                        loc = '%sctrlTMP_Recorder' % ctrl.split('ctrl')[0]
                                        side = loc.split('_')[0]
                                        mc.rename(loc, '%s_%s_%s_%s_bld_recorder' % (side, info[1], info[2], nameAttr))
                                        loc = '%s_%s_%s_%s_bld_recorder' % (side, info[1], info[2], nameAttr)
                                        jnt = ctrl.split('ctrl')[0] + 'jnt'
                                        bld = '%s_%s_bld.%s_%s_%s_bld_crv' % (info[0], info[1], info[0], info[1], nameAttr)
                                        for a in ('scaleConstraint', 'parentConstraint'):
                                            constraint = ''
                                            number = 0
                                            if a == 'parentConstraint':
                                                bulletGrpOff = loc.split('_')[0] + '_' + loc.split('_')[1] + '_' + loc.split('_')[2] + '_ctrl_grpOff'
                                                constraint = mc.parentConstraint(loc, bulletGrpOff, mo=0)
                                            else:
                                                constraint = mc.scaleConstraint(loc, jnt, mo=0)
                                            cons = mc.listAttr(constraint)
                                            nb = len(cons)
                                            attr = cons[(nb - 1)]
                                            jnt = '%s_%s_%s_jnt' % (attr.split('_')[0], attr.split('_')[1], attr.split('_')[2])
                                            if name == 'Open':
                                                mc.setAttr('%s.%s' % ('Facial_Rig_ctrl',
                                                                      'open_mouth'), valueMaxRange)
                                            elif name == 'Jaw':
                                                mc.setAttr('%s.%s' % ('Facial_Rig_ctrl',
                                                                      'jaw'), 1)
                                            elif name == 'JawNeg':
                                                mc.setAttr('%s.%s' % ('Facial_Rig_ctrl',
                                                                      'jaw'), -1)
                                            elif name == 'JawDown':
                                                mc.setAttr('%s.%s' % ('Facial_Rig_ctrl',
                                                                      'jawDown'), 1)
                                            else:
                                                mc.setAttr(bld, 1)
                                            if a == 'parentConstraint':
                                                mc.connectAttr(bld, '%s_%s1.%s' % (jnt.split('jnt')[0] + 'ctrl_grpOff', a, attr), f=True)
                                            else:
                                                mc.connectAttr(bld, '%s_%s1.%s' % (jnt, a, attr), f=True)
                                            connectMouthOpenTwistSide(jawJnt, valueMaxRange, axis, nameAttr, minMax, name)

                                    bldNode = '%s_%s_bld' % (info[0], info[1])
                                    createNodalLinkConstraint(bldNode, newName)
                                    mc.select('%s_%s_*_ctrl' % (info[0], info[1]), r=True)
                                    ctrlList = mc.ls(sl=1)
                                    for ctrl in ctrlList:
                                        for x in ('X', 'Y', 'Z'):
                                            mc.setAttr('%s.scale%s' % (ctrl, x), 1)

                                mc.delete('TMP')
                            else:
                                crvList2 = []
                                mc.select('*%sMax%s_bld_crv' % (name, str(valueMaxRange).split('.')[0]), r=True)
                                crvList = mc.ls(sl=1)
                                for crv in crvList:
                                    test = crv.split('_')[2]
                                    if test == 'bld':
                                        crvList.remove(crv)

                                for crv in crvList:
                                    mc.select(crv, r=True)
                                    mc.duplicate(rr=True)
                                    mc.rename('%s1' % crv, '%s_%s_%s_bld_crv' % (crv.split('_')[0], crv.split('_')[1], nameAttr))
                                    crv2 = '%s_%s_%s_bld_crv' % (crv.split('_')[0], crv.split('_')[1], nameAttr)
                                    crvList2.append(crv2)

                                for crvMin in crvList2:
                                    info = crvMin.split('_')
                                    side = info[0]
                                    otherSide = ''
                                    if side == 'L':
                                        otherSide = 'R'
                                    else:
                                        if side == 'C':
                                            otherSide = 'C'
                                        else:
                                            otherSide = 'L'
                                        nameAttrWithoutMin = info[2].split('Min')[0]
                                        nb = info[2].split('Min')[1]
                                        mc.select('%s_%s_%sMax%s_bld_crv.cv[*]' % (otherSide, info[1], nameAttrWithoutMin, str(nb)), r=True)
                                        listCv = mc.ls(sl=1)[0]
                                        lenght = listCv.split(':')[1]
                                        lenght = int(lenght.split(']')[0])
                                        otherCrv = '%s_%s_%sMax%s_bld_crv' % (otherSide, info[1], nameAttrWithoutMin, str(nb))
                                        for i in range(lenght + 1):
                                            if otherSide != 'C':
                                                pos = mc.xform('%s.cv[%s]' % (otherCrv, i), q=True, ws=True, t=True)
                                                mc.xform('%s.cv[%s]' % (crvMin, i), ws=True, t=[pos[0] * -1, pos[1], pos[2]])
                                            else:
                                                pos = mc.xform('%s.cv[%s]' % (otherCrv, i), q=True, ws=True, t=True)
                                                mc.xform('%s.cv[%s]' % (crvMin, lenght - i), ws=True, t=[pos[0] * -1, pos[1], pos[2]])

                                    bldnode = '%s_%s_bld' % (crvMin.split('_')[0], crvMin.split('_')[1])
                                    crvOri = '%s_%s_crv' % (crvMin.split('_')[0], crvMin.split('_')[1])
                                    mc.select(crvMin, crvOri, r=True)
                                    createBldShape()

                                mc.select('*%sMax%s_bld_recorder' % (name, str(valueMaxRange).split('.')[0]), r=True)
                                locListRecorderToSym = mc.ls(sl=1)
                                locListMin = []
                                for loc in locListRecorderToSym:
                                    mc.select(loc, r=True)
                                    mc.duplicate(rr=True)
                                    mc.rename('%s1' % loc, '%s_%s_%s_%s_bld_recorder' % (loc.split('_')[0], loc.split('_')[1], loc.split('_')[2], nameAttr))
                                    loc2 = '%s_%s_%s_%s_bld_recorder' % (loc.split('_')[0], loc.split('_')[1], loc.split('_')[2], nameAttr)
                                    locListMin.append(loc2)

                                for loc2 in locListMin:
                                    info = loc2.split('_')
                                    side = info[0]
                                    otherSide = ''
                                    if side == 'L':
                                        otherSide = 'R'
                                    else:
                                        if side == 'C':
                                            otherSide = 'C'
                                        else:
                                            otherSide = 'L'
                                        nameAttrWithoutMin = info[3].split('Min')[0]
                                        nb = info[3].split('Min')[1]
                                        if otherSide != 'C':
                                            loc = '%s_%s_%s_%sMax%s_bld_recorder' % (otherSide, info[1], info[2], nameAttrWithoutMin, nb)
                                        else:
                                            lenght = len(mc.ls('C_%s_*_%sMax%s_bld_recorder' % (info[1], nameAttrWithoutMin, nb))) + 1
                                            loc = 'C_%s_%s_%sMax%s_bld_recorder' % (info[1], lenght - int(info[2]), nameAttrWithoutMin, nb)
                                        for x in ('tx', 'ty', 'tz', 'rx', 'ry', 'rz',
                                                  'sx', 'sy', 'sz'):
                                            pos = mc.getAttr('%s.%s' % (loc, x))
                                            if x == 'tx' or x == 'rz':
                                                mc.setAttr('%s.%s' % (loc2, x), pos * -1)
                                            else:
                                                mc.setAttr('%s.%s' % (loc2, x), pos)

                                for loc2 in locListMin:
                                    jnt = '%s_%s_%s_jnt' % (loc2.split('_')[0], loc2.split('_')[1], loc2.split('_')[2])
                                    bld = '%s_%s_bld.%s_%s_%s_bld_crv' % (loc2.split('_')[0], loc2.split('_')[1], loc2.split('_')[0], loc2.split('_')[1], nameAttr)
                                    for a in ('scaleConstraint', 'orientConstraint',
                                              'parentConstraint'):
                                        constraint = ''
                                        number = 0
                                        if a == 'orientConstraint':
                                            constraint = mc.orientConstraint(loc2, jnt, mo=0)
                                        elif a == 'parentConstraint':
                                            bulletGrpOff = loc2.split('_')[0] + '_' + loc2.split('_')[1] + '_' + loc2.split('_')[2] + '_ctrl_grpOff'
                                            constraint = mc.parentConstraint(loc2, bulletGrpOff, mo=0)
                                        else:
                                            constraint = mc.scaleConstraint(loc2, jnt, mo=0)
                                        cons = mc.listAttr(constraint)
                                        nb = len(cons)
                                        attr = cons[(nb - 1)]
                                        if a == 'parentConstraint':
                                            mc.connectAttr(bld, '%s_%s1.%s' % (jnt.split('jnt')[0] + 'ctrl_grpOff', a, attr), f=True)
                                        else:
                                            mc.connectAttr(bld, '%s_%s1.%s' % (jnt, a, attr), f=True)

                                for crv in crvList2:
                                    info = crv.split('_')
                                    bldNode = '%s_%s_bld' % (info[0], info[1])
                                    createNodalLinkConstraint(bldNode, crv)
                                    mc.select('%s_%s_*_ctrl' % (info[0], info[1]), r=True)
                                    ctrlList = mc.ls(sl=1)
                                    for ctrl in ctrlList:
                                        for x in ('X', 'Y', 'Z'):
                                            mc.setAttr('%s.scale%s' % (ctrl, x), 1)

                                connectMouthOpenTwistSide(jawJnt, valueMaxRange * -1, axis, nameAttr, 'Min', name)

            mc.textScrollList('HiddenTMPNodeList', e=1, ra=1)
            jawCtrl = mc.textScrollList('jawCtrlList', q=True, ai=True)[0]
            if fCtrl != jawCtrl:
                name = name.lower()
                rotAxis = mc.radioButtonGrp('axisRot2', q=True, sl=True)
                if rotAxis == 1:
                    rotAxis = 'X'
                else:
                    if rotAxis == 2:
                        rotAxis = 'Y'
                    else:
                        rotAxis = 'Z'
                    try:
                        mc.connectAttr('%s.rotate%s' % (jawCtrl, rotAxis), 'Facial_Rig_ctrl.%s_mouth' % name, f=True)
                    except:
                        pass

        else:
            mc.error('You need to be in Edit Mode for record a new expression.')


def connectMouthOpenTwistSide(jawJnt, valueMaxRange, axis, nameAttr, minMax, name, *args):
    ctrl = 'Facial_Rig_ctrl'
    if nameAttr == 'Open' or nameAttr.startswith('Jaw') == True:
        if nameAttr == 'Open':
            setRange = 'openMouth_setRange'
            divBld = 'openMouth_DivideRot%s' % axis
            supOther = []
            if axis == 'X':
                supOther.append('Y')
                supOther.append('Z')
            else:
                if axis == 'Y':
                    supOther.append('X')
                    supOther.append('Z')
                else:
                    supOther.append('X')
                    supOther.append('Y')
                for other in supOther:
                    if mc.objExists('openMouth_DivideRot%s' % other):
                        mc.delete('openMouth_DivideRot%s' % other)

                if not mc.objExists(setRange):
                    mc.shadingNode('setRange', asUtility=True, n=setRange)
                    mc.setAttr(setRange + '.maxX', 1)
                if not mc.objExists(divBld):
                    mc.shadingNode('multiplyDivide', asUtility=True, n=divBld)
                    mc.setAttr(divBld + '.input2X', valueMaxRange)
                    mc.setAttr(divBld + '.operation', 2)
                try:
                    mc.connectAttr('%s.rotate%s' % (jawJnt, axis), '%s.input1X' % divBld, f=True)
                except:
                    pass

                try:
                    mc.connectAttr('%s.outputX' % divBld, '%s.valueX' % setRange, f=True)
                except:
                    pass

    mc.select('*%s_bld_crv' % nameAttr, r=True)
    crvList = mc.ls(sl=1)
    for crv in crvList:
        test = crv.split('_')[2]
        if test == 'bld':
            crvList.remove(crv)

    for crv in crvList:
        bldNode = crv.split('_')[0] + '_' + crv.split('_')[1] + '_bld'
        if nameAttr == 'Open':
            try:
                mc.connectAttr('%s.outValueX' % setRange, '%s.%s' % (bldNode, crv), f=True)
            except:
                pass

        elif nameAttr.startswith('Jaw') == True:
            axis = mc.radioButtonGrp('axisTrans2', q=True, sl=True)
            if axis == 1:
                axis = 'x'
            elif axis == 2:
                axis = 'y'
            else:
                axis = 'z'
            correctAttr = ''
            if nameAttr == 'Jaw':
                correctAttr = 'jaw'
            elif nameAttr == 'JawDown':
                correctAttr = 'jawDown'
            elif nameAttr == 'JawNeg':
                correctAttr = 'jaw'
            jawCtrl = mc.textScrollList('jawCtrlList', q=True, ai=True)[0]
            condNodeJaw = 'jaw_activation_cond'
            if not mc.objExists(condNodeJaw):
                mc.createNode('condition', n=condNodeJaw)
                mc.connectAttr('%s.t%s' % (jawCtrl, axis), '%s.jaw' % ctrl, f=True)
            if nameAttr == 'Jaw' or nameAttr == 'JawNeg':
                if nameAttr == 'Jaw':
                    setRangeJaw = 'jaw_Activation_setRange'
                    mc.createNode('setRange', n=setRangeJaw)
                    valueOfJawCtrlAxis = mc.getAttr('%s.t%s' % (jawCtrl, axis))
                    for x in ['X', 'Y', 'Z']:
                        mc.setAttr('%s.oldMax%s' % (setRangeJaw, x), valueOfJawCtrlAxis)
                        mc.connectAttr('%s.t%s' % (jawCtrl, axis), '%s.value%s' % (setRangeJaw, x), f=True)

                elif nameAttr == 'JawNeg':
                    setRangeJawNeg = 'jawNeg_Activation_setRange'
                    mc.createNode('setRange', n=setRangeJawNeg)
                    valueOfJawCtrlAxis = mc.getAttr('%s.t%s' % (jawCtrl, axis))
                    for x in ['X', 'Y', 'Z']:
                        mc.setAttr('%s.oldMax%s' % (setRangeJawNeg, x), valueOfJawCtrlAxis)
                        mc.connectAttr('%s.t%s' % (jawCtrl, axis), '%s.value%s' % (setRangeJawNeg, x), f=True)

            mc.connectAttr('%s.t%s' % (jawCtrl, axis), '%s.%s' % (ctrl, correctAttr), f=True)
        else:
            attr = ''
            if name == 'Side':
                attr = 'side'
            else:
                attr = 'twist'
            crv = crv.split('_')[0] + '_' + crv.split('_')[1] + '_' + nameAttr + '_bld_crv'
            mc.setAttr('%s.%s_mouth' % (ctrl, attr), 0)
            mc.setAttr('%s.%s' % (bldNode, crv), 0)
            mc.setDrivenKeyframe('%s.%s' % (bldNode, crv), currentDriver='%s.%s_mouth' % (ctrl, attr))
            mc.setAttr('%s.%s_mouth' % (ctrl, attr), valueMaxRange)
            mc.setAttr('%s.%s' % (bldNode, crv), 1)
            mc.setDrivenKeyframe('%s.%s' % (bldNode, crv), currentDriver='%s.%s_mouth' % (ctrl, attr))
            mc.setAttr('%s.%s_mouth' % (ctrl, attr), 0)


def recordWithSelection(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvList = []
            CSel = mc.textScrollList('CenterRecordCrvsList', q=1, si=1)
            RSel = mc.textScrollList('RightRecordCrvsList', q=1, si=1)
            LSel = mc.textScrollList('LeftRecordCrvsList', q=1, si=1)
            if CSel != None:
                for crv in CSel:
                    crvList.append(crv)

            if RSel != None:
                for crv in RSel:
                    crvList.append(crv)

            if LSel != None:
                for crv in LSel:
                    crvList.append(crv)

            if len(crvList) > 0:
                TMPBlendShapeCrv(crvList)
                mc.button('ValidateExpButton', e=1, en=1)
            mc.deleteUI('BlendShapeUIRecorder')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')
    return


def recordWithAllCurves(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvList = []
            CSel = mc.textScrollList('CenterRecordCrvsList', q=1, ai=1)
            RSel = mc.textScrollList('RightRecordCrvsList', q=1, ai=1)
            LSel = mc.textScrollList('LeftRecordCrvsList', q=1, ai=1)
            try:
                for crv in CSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in RSel:
                    crvList.append(crv)

            except:
                pass

            try:
                for crv in LSel:
                    crvList.append(crv)

            except:
                pass

            if len(crvList) > 0:
                TMPBlendShapeCrv(crvList)
                mc.button('recorderBldExp', e=True, en=0)
                mc.button('ValidateExpButton', e=1, en=1)
                mc.deleteUI('BlendShapeUIRecorder')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')


def validateRecorder(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode == 0:
            nodeList = mc.textScrollList('HiddenTMPNodeList', q=1, ai=1)
            result = mc.promptDialog(title='Enter a blendshape name:', message='Enter BlendShape Name :', button=[
             'OK', 'Cancel'], defaultButton='OK', cancelButton='Cancel', dismissString='Cancel')
            if result == 'OK':
                name = mc.promptDialog(query=True, text=True)
                testToContinue = 0
                if name != '':
                    for crv in nodeList:
                        crvBld = crv.split('_')[0] + '_' + crv.split('_')[1] + '_' + name + '_bld_crv'
                        if mc.objExists(crvBld):
                            mc.warning('A blendshape curve named %s already exists, please change the name of your expression' % crvBld)
                            validateRecorder()
                            break
                        else:
                            testToContinue = 1

                else:
                    validateRecorder()
                if testToContinue == 1:
                    mc.button('ValidateExpButton', e=1, en=0)
                    mc.button('recorderBldExp', e=1, en=1)
                    mc.textScrollList('HiddenTMPNodeList', e=1, ra=1)
                    mc.textScrollList('RecordPosCtrl', e=1, ra=1)
                    for crv in nodeList:
                        bld2 = ''
                        crvNameTMP = crv.split('_')[0] + '_' + crv.split('_')[1] + '_crvTMP'
                        crvOri = crvNameTMP.split('TMP')[0]
                        nodeNameTMP = '%s_1_POC_crv' % crvNameTMP
                        Rcrv = ''
                        newName = crv.split('_')[0] + '_' + crv.split('_')[1] + '_' + name + '_bld_crv'
                        mc.select('%s_*_POC_loc' % crvNameTMP, r=True)
                        locList = mc.ls(sl=1)
                        lenLocTMP = len(locList)
                        if not mc.objExists('C_faceCurvesBld_grp'):
                            mc.group(n='C_faceCurvesBld_grp', em=1)
                            mel.eval('HideSelectedObjects;doHideObjects true;')
                        for i in range(lenLocTMP):
                            mc.delete('%s_%s_POC_loc' % (crvNameTMP, str(i + 1)))
                            if i != 0:
                                mc.delete('%s_%s_POC_crv' % (crvNameTMP, str(i + 1)))
                            else:
                                mc.rename('%s_1_POC_crv' % crvNameTMP, newName)

                        mc.parent(newName, 'C_faceCurvesBld_grp')
                        getBackLocTMPToCrv(crvNameTMP)
                        mc.select(newName, crvOri, r=True)
                        createBldShapeExp()
                        mc.select(crv.split('crv')[0] + '*ctrl', r=True)
                        listCtrl = mc.ls(sl=1)
                        nbLoc = len(listCtrl)
                        for i in range(nbLoc):
                            mc.select(listCtrl[i], r=True)
                            ctrl = mc.ls(sl=1)[0]
                            info = ctrl.split('_')
                            loc = ctrl.split('ctrl')[0] + 'ctrlTMP_Recorder'
                            side = loc.split('_')[0]
                            mc.rename(loc, '%s_%s_%s_%s_bld_recorder' % (side, info[1], info[2], name))
                            loc = '%s_%s_%s_%s_bld_recorder' % (side, info[1], info[2], name)
                            jnt = ctrl.split('ctrl')[0] + 'jnt'
                            bld = '%s_%s_bldExp.%s_%s_%s_bld_crv' % (info[0], info[1], info[0], info[1], name)
                            for a in ('scaleConstraint', 'parentConstraint'):
                                constraint = ''
                                number = 0
                                if a == 'parentConstraint':
                                    bulletGrpOff = loc.split('_')[0] + '_' + loc.split('_')[1] + '_' + loc.split('_')[2] + '_ctrl_grpOff'
                                    constraint = mc.parentConstraint(loc, bulletGrpOff, mo=0)
                                else:
                                    constraint = mc.scaleConstraint(loc, jnt, mo=0)
                                cons = mc.listAttr(constraint)
                                nb = len(cons)
                                attr = cons[(nb - 1)]
                                mc.setAttr(bld, 1)
                                jnt = attr.split('_')[0] + '_' + attr.split('_')[1] + '_' + attr.split('_')[2] + '_jnt'
                                if a == 'parentConstraint':
                                    mc.connectAttr(bld, '%s_%s1.%s' % (jnt.split('jnt')[0] + 'ctrl_grpOff', a, attr), f=True)
                                else:
                                    mc.connectAttr(bld, '%s_%s1.%s' % (jnt, a, attr), f=True)

                        crv = '%s_%s_%s_bld_crv' % (info[0], info[1], name)
                        bldNode = '%s_%s_bldExp' % (info[0], info[1])
                        createNodalLinkConstraint(bldNode, crv)
                        mc.select('%s_%s_*_ctrl' % (info[0], info[1]), r=True)
                        ctrlList = mc.ls(sl=1)
                        for ctrl in ctrlList:
                            for x in ('X', 'Y', 'Z'):
                                mc.setAttr('%s.scale%s' % (ctrl, x), 1)

                    mc.delete('TMP')
                    mc.textScrollList('HiddenTMPNodeList', e=1, ra=1)
                    mc.warning('your expression named : %s is now correctly record' % name)
        else:
            mc.error('you have change the mode between the recording expression and the step of validation.')
    else:
        mc.error('you need to create the facial controller')


def createBldShapeExp(*args):
    eltToBld = mc.ls(sl=1)
    info = eltToBld[0].split('_')
    bld = info[0] + '_' + info[1] + '_bldExp'
    if not mc.objExists(bld):
        mc.select(eltToBld[0], eltToBld[1], r=True)
        if mc.objExists(bld.split('Exp')[0]):
            mc.blendShape(eltToBld[0], eltToBld[1], n=bld, parallel=True)
        else:
            mel.eval('blendShape -frontOfChain -n "' + bld + '";')
    else:
        queryWeights = mc.blendShape(bld, q=True, w=1)
        targets = mc.blendShape(bld, q=1, t=1)
        numberOfBlendShapes = len(queryWeights)
        index = mc.blendShape(bld, q=1, wc=1)
        for i in range(999):
            try:
                mc.blendShape(bld, e=1, t=(str(eltToBld[1]), numberOfBlendShapes, str(eltToBld[0]), 1.0))
            except RuntimeError:
                pass

            if mc.objExists('%s.%s' % (bld, eltToBld[0])):
                break
            else:
                numberOfBlendShapes = numberOfBlendShapes + 1

        mc.warning('A new blend Shape was added for ' + eltToBld[1])


def TMPBlendShapeCrv(crvList, *args):
    mc.textScrollList('HiddenTMPNodeList', e=1, ra=True)
    crvTMPNodeList = []
    for crv in crvList:
        side = crv.split('_')[0]
        name = crv.split('_')[1]
        crvMaster = crv
        mc.select('%s_%s_*_ctrl' % (side, name), r=True)
        ctrls = mc.ls(sl=1)
        ctrlPosList = getRecordPosOfCtrl(ctrls)
        keepRotAndScaleRecordForBlendShape(ctrlPosList)
        createCurveWithPosCtrlList(ctrlPosList)
        replaceEditPointCrv(ctrlPosList)
        recupValueOfCtrl = testRecordBlendShape(ctrlPosList)
        crvTMPBldNode = '%sTMP_1_POC_crv_bldExp.%sTMP_1_POC_crv' % (crv, crv)
        crvTMPNodeList.append(crvTMPBldNode)

    for crvTMPNode in crvTMPNodeList:
        mc.textScrollList('HiddenTMPNodeList', e=1, a=crvTMPNode)

    return crvTMPNodeList


def getRecordPosOfCtrl(ctrls, *args):
    eltPosList = DictionnaireOrdonne()
    for elt in ctrls:
        posElt = mc.xform(elt, q=1, ws=1, t=1)
        eltPosList[elt] = posElt

    eltPosList.sort()
    for ctrl in eltPosList:
        value = '%s=%s' % (ctrl, eltPosList[ctrl])
        mc.textScrollList('RecordPosCtrl', e=1, a=value)

    return eltPosList


def keepRotAndScaleRecordForBlendShape(ctrlPosList, *args):
    if not mc.objExists('xtra_toHide'):
        mc.group(n='xtra_toHide', em=True)
        mc.setAttr('xtra_toHide.visibility', 0)
    if not mc.objExists('blendShape_Loc_keepRecorder_RotAndScale_grp'):
        mc.select(cl=1)
        mc.group(n='blendShape_Loc_keepRecorder_RotAndScale_grp', em=1)
        try:
            mc.parent('blendShape_Loc_keepRecorder_RotAndScale_grp', 'xtra_toHide')
            try:
                piv = mc.xform('cc_head', q=1, ws=1, piv=1)
                mc.xform('blendShape_Loc_keepRecorder_RotAndScale_grp', ws=1, piv=[piv[0], piv[1], piv[2]])
                mc.makeIdentity('blendShape_Loc_keepRecorder_RotAndScale_grp', a=1)
            except:
                pass

            if not mc.objExists('blendShape_Loc_keepRecorder_RotAndScale_grp_parentConstraint1'):
                mc.parentConstraint('cc_head', 'blendShape_Loc_keepRecorder_RotAndScale_grp', mo=0)
        except:
            pass

    for ctrl in ctrlPosList:
        loc = mc.spaceLocator(n='%sTMP_Recorder' % ctrl)[0]
        mc.parentConstraint(ctrl, loc, mo=0)
        mc.scaleConstraint(ctrl, loc, mo=0)
        mc.delete('%s_parentConstraint1' % loc, '%s_scaleConstraint1' % loc)
        mc.parent(loc, 'blendShape_Loc_keepRecorder_RotAndScale_grp')


def createCurveWithPosCtrlList(dict, *args):
    TMPGrp = 'TMP'
    if not mc.objExists(TMPGrp):
        mc.group(n=TMPGrp, em=1)
        mc.select(cl=1)
    keys = dict.keys()
    posList = []
    for key in keys:
        pos = dict[key]
        posList.append(pos)

    crvName = keys[0].split('_')[0] + '_' + keys[0].split('_')[1] + '_crv'
    crvTMP = mc.duplicateCurve(crvName, ch=False, n=crvName + 'TMP')[0]
    lenSpan = mc.getAttr('%s.spans' % crvTMP) + 1
    lenCtrl = keys.__len__()
    i = 0
    for key in keys:
        mc.select(cl=1)
        loc = mc.spaceLocator()[0]
        ep = crvTMP + '.ep[' + str(i) + ']'
        if lenSpan != lenCtrl:
            ep = crvTMP + '.ep[' + str(i + 1) + ']'
        POCCrv = mc.pointCurveConstraint(ep, ch=True, rpo=False, w=1, n='%s_%s_POC_crv' % (crvTMP, str(i + 1)))
        info = crvTMP.split('_')
        newLoc = POCCrv[1]
        crvDeform = POCCrv[0]
        newLoc = mc.rename(newLoc, '%s_%s_POC_loc' % (crvTMP, str(i + 1)))
        pivLoc = mc.xform('%s_%s_%s_loc' % (info[0], info[1], str(i + 1)), q=1, ws=1, piv=1)
        mc.xform(newLoc, ws=1, piv=[pivLoc[0], pivLoc[1], pivLoc[2]])
        for a in ['X', 'Y', 'Z']:
            mc.setAttr('%sShape.localScale%s' % (newLoc, a), 0.2)

        mc.delete(loc)
        mc.parentConstraint(key, newLoc, mo=0)
        mc.delete(newLoc + '_parentConstraint1')
        mc.parent(crvDeform, TMPGrp)
        mc.parent(newLoc, TMPGrp)
        i = i + 1

    mc.parent(crvTMP, TMPGrp)


def replaceEditPointCrv(dict, *args):
    locPos = []
    keys = dict.keys()
    posList = []
    locList = DictionnaireOrdonne()
    curveName = '%s_%s_crv' % (dict.keys()[0].split('_')[0], dict.keys()[0].split('_')[1])
    for key in keys:
        pos = dict[key]
        posList.append(pos)
        mpName = key.split('_ctrl')[0] + '_mp'
        mpValue = mc.getAttr(mpName + '.uValue')
        locList[mpName] = mpValue

    locList.sort()
    lenght = dict.__len__()
    testSpan = 0
    crvTMP = mc.duplicate(curveName, rr=True, n=curveName + 'TMP')[0]
    crvTMP = curveName + 'TMP'
    side = crvTMP.split('_')[0]
    mc.setAttr(crvTMP + '.ove', 1)
    if side == 'L':
        mc.setAttr(crvTMP + '.ovc', 6)
    else:
        if side == 'R':
            mc.setAttr(crvTMP + '.ovc', 13)
        else:
            mc.setAttr(crvTMP + '.ovc', 17)
        for loc in locList:
            if locList[loc] != 0:
                mc.select(loc, r=True)
                locPosWorld = mc.xform(loc.split('mp')[0] + 'loc', q=True, ws=True, t=True)
                epToChange = int(loc.split('_')[2])
                if testSpan == 0:
                    epToChange = epToChange - 1
                mc.select(crvTMP + '.ep[' + str(epToChange) + ']', r=True)
                editPointSel = crvTMP + '.ep[' + str(epToChange) + ']'
                mc.move(locPosWorld[0], locPosWorld[1], locPosWorld[2], a=True, ws=True)

        crvTMP = curveName + 'TMP'
        crvTMPShape = mc.listRelatives(crvTMP)[0]
        for loc in locList:
            mc.disconnectAttr(curveName + 'Shape.worldSpace[0]', loc + '.geometryPath')
            mc.connectAttr(crvTMPShape + '.worldSpace[0]', loc + '.geometryPath', f=True)


def testRecordBlendShape(dict, *args):
    keys = dict.keys()
    crvToTest = '%s_%s_crvTMP' % (keys[0].split('_')[0], keys[0].split('_')[1])
    crvTMP = crvToTest + '_1_POC_crv'
    recupValue = DictionnaireOrdonne()
    for key in keys:
        pos = mc.xform(key, q=1, os=1, t=1)
        recupValue[key] = pos
        for a in ['x', 'y', 'z']:
            mc.setAttr('%s.t%s' % (key, a), 0)
            mc.setAttr('%s.r%s' % (key, a), 0)

    createBldShapeToTestRecorder(crvToTest, crvTMP)
    return recupValue


def createBldShapeToTestRecorder(crvMaster, crvTMP, *args):
    mc.select(crvTMP, crvMaster, r=True)
    sel = mc.ls(sl=1)
    bldNameTMP = crvTMP + '_bldExp'
    mc.select(sel, r=True)
    mel.eval('blendShape -frontOfChain -n "' + bldNameTMP + '";')


def createNodalLinkConstraint(bldNode, crv, *args):
    info = crv.split('_')
    side = info[0]
    name = info[1]
    if not mc.objExists('%s.%s' % (bldNode, crv)):
        bldNode = '%s_%s_bldExp' % (side, name)
    if not mc.objExists('global_constant_for_bld_activation_cond'):
        mc.createNode('condition', n='global_constant_for_bld_activation_cond')
        mc.setAttr('global_constant_for_bld_activation_cond.firstTerm', 1)
    if not mc.objExists('%s_%s_plus_min' % (side, name)):
        minPlus = mc.createNode('plusMinusAverage', n='%s_%s_plus_min' % (side, name))
        mc.setAttr('%s_%s_plus_min.operation' % (side, name), 2)
        mc.connectAttr('global_constant_for_bld_activation_cond.firstTerm', '%s_%s_plus_min.input1D[0]' % (side, name), f=True)
        clamp = mc.createNode('clamp', n='%s_%s_clamp_value' % (side, name))
        mc.connectAttr('%s.output1D' % minPlus, '%s.inputR' % clamp, f=True)
        mc.setAttr('%s.maxR' % clamp, 1)
        mc.setAttr('%s.minR' % clamp, 0)
        mc.select('%s_%s_*_ctrl_grpOff_parentConstraint1' % (side, name), r=True)
        consList = mc.ls(sl=1)
        for cons in consList:
            nb = cons.split('_')[2]
            mc.connectAttr('%s.outputR' % clamp, '%s.%s_%s_%s_locW0' % (cons, side, name, str(nb)), f=True)

        mc.select('%s_%s_*_jnt_scaleConstraint1' % (side, name), r=True)
        consList = mc.ls(sl=1)
        for cons in consList:
            nb = cons.split('_')[2]
            mc.connectAttr('%s.outputR' % clamp, '%s.%s_%s_%s_ctrlW0' % (cons, side, name, str(nb)), f=True)

    minPlus = '%s_%s_plus_min' % (side, name)
    test = 0
    mc.select('%s.input1D[*]' % minPlus, r=True)
    for input in mc.ls(sl=1):
        testInput = mc.listConnections(input, p=True)
        if testInput != 'global_constant_for_bld_activation_cond.firstTerm':
            if testInput == crv:
                test = 0
                break
            else:
                test = test + 1

    mc.select('%s.input1D[*]' % minPlus, r=True)
    listInput = mc.ls(sl=1)
    if test > 0:
        for i in range(999):
            result = 'no'
            for input in listInput:
                if '%s.input1D[%s]' % (minPlus, i) == input:
                    result = 'yes'
                    listInput.remove(input)
                    break
                else:
                    result = 'no'

            if result == 'no':
                mc.connectAttr('%s.%s' % (bldNode, crv), '%s.input1D[%s]' % (minPlus, i))
                break


def getBackLocTMPToCrv(crvNameTMP, *args):
    crvNameOri = crvNameTMP.split('TMP')[0]
    info = crvNameTMP.split('_')
    mc.select('%s_%s_*_mp' % (info[0], info[1]), r=True)
    mpList = mc.ls(sl=1)
    for mp in mpList:
        mc.disconnectAttr(crvNameTMP + 'Shape.worldSpace[0]', mp + '.geometryPath')
        mc.connectAttr(crvNameOri + 'Shape.worldSpace[0]', mp + '.geometryPath', f=True)

    if mc.objExists(crvNameTMP + '1'):
        mc.delete(crvNameTMP + '1')


def createBldShape(*args):
    eltToBld = mc.ls(sl=1)
    mc.select(eltToBld[0], r=True)
    elt = mc.ls(sl=1)[0]
    info = elt.split('_')
    bld = info[0] + '_' + info[1] + '_bld'
    if not mc.objExists(bld):
        mc.select(eltToBld[0], eltToBld[1], r=True)
        list = mc.ls(sl=1)
        mel.eval('blendShape -frontOfChain -n "' + bld + '";')
    else:
        queryWeights = mc.blendShape(bld, q=True, w=1)
        targets = mc.blendShape(bld, q=1, t=1)
        numberOfBlendShapes = len(queryWeights)
        index = mc.blendShape(bld, q=1, wc=1)
        for i in range(999):
            try:
                mc.blendShape(bld, e=1, t=(str(eltToBld[1]), numberOfBlendShapes, str(eltToBld[0]), 1.0))
            except RuntimeError:
                pass

            if mc.objExists('%s.%s' % (bld, eltToBld[0])):
                break
            else:
                numberOfBlendShapes = numberOfBlendShapes + 1

        mc.warning('A new blend Shape was added for ' + eltToBld[1])