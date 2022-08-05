# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel

def goToEditMode(*args):
    headCtrl = ''
    try:
        headCtrl = mc.textScrollList('headCtrlBlendShape', q=True, ai=True)[0]
    except:
        pass

    if headCtrl != '':
        if mc.objExists('Facial_Rig_ctrl'):
            mode = mc.getAttr('Facial_Rig_ctrl.mode')
            if mode == 1:
                setAllAttributeOfCCFacialAt0()
                ctrlList2 = []
                mc.select('*ctrl', r=True)
                ctrlList = mc.ls(sl=1)
                for ctrl in ctrlList:
                    info = ctrl.split('ctrl')[0]
                    if mc.objExists('%sjnt' % info):
                        ctrlList2.append(ctrl)

                info = ctrl.split('ctrl')[0]
                if mc.objExists('%sjnt' % info):
                    ctrlList2.append(ctrl)
                for ctrl in ctrlList2:
                    try:
                        mp = ctrl.split('ctrl')[0] + 'mp'
                        loc = ctrl.split('ctrl')[0] + 'loc'
                        mc.connectAttr('%s.xCoordinate' % mp, '%s.translateX' % loc)
                        mc.connectAttr('%s.yCoordinate' % mp, '%s.translateY' % loc)
                        mc.connectAttr('%s.zCoordinate' % mp, '%s.translateZ' % loc)
                    except:
                        pass

                mc.select('*bld_recorder', r=True)
                locBldRecList = mc.ls(sl=1)
                for loc in locBldRecList:
                    info = loc.split('_')
                    resultPosNode = '%s_%s_%s_finalPos' % (info[0], info[1], info[2])
                    grpOff = '%s_%s_%s_ctrl_grpOff' % (info[0], info[1], info[2])
                    parCons = '%s_parentConstraint1' % grpOff
                    jntCons = '%s_%s_%s_jnt_scaleConstraint1' % (info[0], info[1], info[2])
                    jnt = '%s_%s_%s_jnt' % (info[0], info[1], info[2])
                    baseLoc = '%s_%s_%s_loc' % (info[0], info[1], info[2])
                    conformScaleNode = '%s_%s_%s_conformScale' % (info[0], info[1], info[2])
                    multNode = '%s_mult_add' % loc
                    minNode = '%s_%s_%s_%s_minTrans' % (info[0], info[1], info[2], info[3])
                    addNode = '%s_%s_%s_addTrans' % (info[0], info[1], info[2])
                    multNodeRot = '%s_mult_addRot' % loc
                    minNodeRot = '%s_%s_%s_%s_minRot' % (info[0], info[1], info[2], info[3])
                    addNodeRot = '%s_%s_%s_addRot' % (info[0], info[1], info[2])
                    multNodeScale = '%s_mult_addScale' % loc
                    minNodeScale = '%s_%s_%s_%s_minScale' % (info[0], info[1], info[2], info[3])
                    addNodeScale = '%s_%s_%s_addScale' % (info[0], info[1], info[2])
                    for x in ('X', 'Y', 'Z'):
                        try:
                            mc.connectAttr('%s.constraintRotate%s' % (parCons, x), '%s.rotate%s' % (grpOff, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr('%s.constraintTranslate%s' % (parCons, x), '%s.translate%s' % (grpOff, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr('%s.constraintScale%s' % (jntCons, x), '%s.scale%s' % (jnt, x), f=True)
                        except:
                            pass

                    for x in (multNode, minNode, addNode, multNodeRot, multNodeScale, minNodeRot, minNodeScale, addNodeRot, addNodeScale):
                        try:
                            mc.delete(x)
                        except:
                            pass

                    try:
                        mc.delete(conformScaleNode)
                    except:
                        pass

                    try:
                        mc.delete('Constant_scale')
                    except:
                        pass

                mc.setAttr('Facial_Rig_ctrl.mode', lock=False)
                mc.setAttr('Facial_Rig_ctrl.mode', 0)
                mc.setAttr('Facial_Rig_ctrl.mode', lock=True)
                mc.warning('You are back in Edit Mode')
            elif mode == 2:
                mc.error('You cannot back into the Edit mode if you have launch the Optimize Mode.')
            else:
                mc.warning('You are already in Edit Mode')
        else:
            mc.error('No Facial Rig Ctrl was found, this action will be aborted')
    else:
        raise mc.error('please add your head controller into the "Head Controller" field')

def setAllAttributeOfCCFacialAt0(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        listAttrCCFacial = ['openMouth', 'sideMouth', 'twistMouth', 'jawAmount', 'jawDown']
        listToAdd = []
        try:
            mc.select('*bld_crv', r=True)
            listToAdd = mc.ls(sl=1)
        except:
            pass

        if len(listToAdd) > 0:
            for elt in listToAdd:
                info = elt.split('_')
                name = ('').join([ i for i in info[2] if not i.isdigit() ])
                if name != 'bld':
                    if name != 'bldExp':
                        if name != 'Open':
                            if name != 'SideMin':
                                if name != 'SideMax':
                                    if name != 'TwistMin':
                                        if name != 'TwistMax':
                                            if name != 'squash':
                                                if name != 'stretch':
                                                    if name != 'Jaw':
                                                        if name != 'JawNeg':
                                                            if name != 'JawDown':
                                                                listAttrCCFacial.append('%s_%s_%s' % (info[0], info[1], info[2]))

            for x in listAttrCCFacial:
                try:
                    mc.setAttr('Facial_Rig_ctrl.%s' % x, 0)
                except:
                    pass

        else:
            mc.error('No blendshape made by the speed facial script was found. This action will be aborted')
    else:
        mc.error('The Facial_Rig_ctrl controller was not found, this operation will be aborted')

def discoAllMpToLoc(*args):
    ctrlList2 = []
    mc.select('*ctrl', r=True)
    ctrlList = mc.ls(sl=1)
    for ctrl in ctrlList:
        info = ctrl.split('ctrl')[0]
        if mc.objExists('%sjnt' % info):
            ctrlList2.append(ctrl)

    for ctrl in ctrlList2:
        for x in ('Orient', 'Position', 'Scale'):
            try:
                mc.deleteAttr('%s.%s_%s' % (ctrl, 'Follow_BlendShape', x))
            except:
                pass

        try:
            mp = ctrl.split('ctrl')[0] + 'mp'
            loc = ctrl.split('ctrl')[0] + 'loc'
            mc.disconnectAttr('%s.xCoordinate' % mp, '%s.translateX' % loc)
            mc.disconnectAttr('%s.yCoordinate' % mp, '%s.translateY' % loc)
            mc.disconnectAttr('%s.zCoordinate' % mp, '%s.translateZ' % loc)
        except:
            pass

def goToAnimMode(*args):
    testConstantScale = ''
    headCtrl = ''
    try:
        headCtrl = mc.textScrollList('headCtrlBlendShape', q=True, ai=True)[0]
    except:
        pass

    if headCtrl != '':
        if mc.objExists('Facial_Rig_ctrl'):
            mode = mc.getAttr('Facial_Rig_ctrl.mode')
            if mode == 0:
                listBldNode = mc.ls('*_bldExp')
                for bldNode in listBldNode:
                    blendTargets = mc.listAttr(bldNode + '.w', m=True)
                    for target in blendTargets:
                        mc.setAttr('%s.%s' % (bldNode, target), 0)

                setAllAttributeOfCCFacialAt0()
                discoAllMpToLoc()
                piv = mc.xform(headCtrl, q=True, ws=True, piv=True)
                mc.xform('blendShape_Loc_keepRecorder_RotAndScale_grp', ws=True, piv=[piv[0], piv[1], piv[2]])
                try:
                    mc.orientConstraint(headCtrl, 'blendShape_Loc_keepRecorder_RotAndScale_grp', mo=True)
                except:
                    pass

                mc.select('*bld_recorder', r=True)
                locBldRecList = mc.ls(sl=1)
                for loc in locBldRecList:
                    info = loc.split('_')
                    resultPosNode = '%s_%s_%s_finalPos' % (info[0], info[1], info[2])
                    grpOff = '%s_%s_%s_ctrl_grpOff' % (info[0], info[1], info[2])
                    parCons = '%s_parentConstraint1' % grpOff
                    jntCons = '%s_%s_%s_jnt_scaleConstraint1' % (info[0], info[1], info[2])
                    jnt = '%s_%s_%s_jnt' % (info[0], info[1], info[2])
                    baseLoc = '%s_%s_%s_loc' % (info[0], info[1], info[2])
                    conformScaleNode = '%s_%s_%s_conformScale' % (info[0], info[1], info[2])
                    multNode = '%s_mult_add' % loc
                    minNode = '%s_%s_%s_%s_minTrans' % (info[0], info[1], info[2], info[3])
                    addNode = '%s_%s_%s_addTrans' % (info[0], info[1], info[2])
                    multNodeRot = '%s_mult_addRot' % loc
                    minNodeRot = '%s_%s_%s_%s_minRot' % (info[0], info[1], info[2], info[3])
                    addNodeRot = '%s_%s_%s_addRot' % (info[0], info[1], info[2])
                    multNodeScale = '%s_mult_addScale' % loc
                    minNodeScale = '%s_%s_%s_%s_minScale' % (info[0], info[1], info[2], info[3])
                    addNodeScale = '%s_%s_%s_addScale' % (info[0], info[1], info[2])
                    if not mc.objExists(minNode):
                        mc.createNode('plusMinusAverage', n=minNode)
                        mc.setAttr('%s.operation' % minNode, 2)
                        mc.connectAttr('%s.translate' % loc, '%s.input3D[0]' % minNode, f=True)
                        mc.connectAttr('%s_%s_%s_loc.translate' % (info[0], info[1], info[2]), '%s.input3D[1]' % minNode, f=True)
                    if not mc.objExists(minNodeRot):
                        mc.createNode('plusMinusAverage', n=minNodeRot)
                        mc.setAttr('%s.operation' % minNodeRot, 2)
                        mc.connectAttr('%s.rotate' % loc, '%s.input3D[0]' % minNodeRot, f=True)
                        mc.connectAttr('%s_%s_%s_loc.rotate' % (info[0], info[1], info[2]), '%s.input3D[1]' % minNodeRot, f=True)
                    if not mc.objExists(minNodeScale):
                        mc.createNode('plusMinusAverage', n=minNodeScale)
                        mc.setAttr('%s.operation' % minNodeScale, 2)
                        mc.connectAttr('%s.scale' % loc, '%s.input3D[0]' % minNodeScale, f=True)
                        mc.connectAttr('%s_%s_%s_loc.scale' % (info[0], info[1], info[2]), '%s.input3D[1]' % minNodeScale, f=True)
                    if not mc.objExists(multNode):
                        mc.createNode('multiplyDivide', n=multNode)
                    if not mc.objExists(multNodeRot):
                        mc.createNode('multiplyDivide', n=multNodeRot)
                    if not mc.objExists(multNodeScale):
                        mc.createNode('multiplyDivide', n=multNodeScale)
                    if not mc.objExists(conformScaleNode):
                        mc.createNode('plusMinusAverage', n=conformScaleNode)
                    if not mc.objExists('Constant_scale'):
                        mc.createNode('condition', n='Constant_scale')
                        mc.setAttr('Constant_scale.firstTerm', 1)
                        for x in ('x', 'y', 'z'):
                            mc.connectAttr('Constant_scale.firstTerm', '%s.input3D[0].input3D%s' % (conformScaleNode, x))

                    try:
                        mc.connectAttr('%s_%s_%s_addScale.output3D' % (info[0], info[1], info[2]), '%s.input3D[1]' % conformScaleNode, f=True)
                        mc.connectAttr('%s.output3D' % conformScaleNode, '%s.scale' % jnt, f=True)
                    except:
                        pass

                    if not mc.objExists(addNode):
                        mc.createNode('plusMinusAverage', n=addNode)
                    if not mc.objExists(addNodeRot):
                        mc.createNode('plusMinusAverage', n=addNodeRot)
                    if not mc.objExists(addNodeScale):
                        mc.createNode('plusMinusAverage', n=addNodeScale)
                        mc.connectAttr('Constant_scale.outColorR', '%s.input3D[0].input3Dx' % addNodeScale)
                        mc.connectAttr('Constant_scale.outColorR', '%s.input3D[0].input3Dy' % addNodeScale)
                        mc.connectAttr('Constant_scale.outColorR', '%s.input3D[0].input3Dz' % addNodeScale)
                    for x in ('X', 'Y', 'Z'):
                        try:
                            mc.disconnectAttr('%s.constraintRotate%s' % (parCons, x), '%s.rotate%s' % (grpOff, x))
                        except:
                            pass

                        try:
                            mc.disconnectAttr('%s.constraintTranslate%s' % (parCons, x), '%s.translate%s' % (grpOff, x))
                        except:
                            pass

                        try:
                            mc.disconnectAttr('%s.constraintScale%s' % (jntCons, x), '%s.scale%s' % (jnt, x))
                        except:
                            pass

                    try:
                        mc.makeIdentity(grpOff, a=1)
                    except:
                        pass

                    nb = 0
                    for i in range(120):
                        if mc.objExists('%s.%sW%s' % (parCons, loc, i)):
                            nb = i
                            break
                        else:
                            i = i + 1

                    for x in ('X', 'Y', 'Z'):
                        try:
                            mc.connectAttr('%s.%sW%s' % (parCons, loc, nb), '%s.input2.input2%s' % (multNode, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr('%s.output3D' % minNode, '%s.input1' % multNode, f=True)
                        except:
                            pass

                    for x in ('X', 'Y', 'Z'):
                        try:
                            mc.connectAttr('%s.%sW%s' % (parCons, loc, nb), '%s.input2.input2%s' % (multNodeRot, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr('%s.output3D' % minNodeRot, '%s.input1' % multNodeRot, f=True)
                        except:
                            pass

                    for x in ('X', 'Y', 'Z'):
                        try:
                            mc.connectAttr('%s.%sW%s' % (jntCons, loc, nb), '%s.input2.input2%s' % (multNodeScale, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr('%s.output3D' % minNodeScale, '%s.input1' % multNodeScale, f=True)
                        except:
                            pass

                    try:
                        mc.select('%s.input3D[*]' % addNode, r=True)
                        lenght = len(mc.ls(sl=1))
                        test = 0
                        for input in mc.ls(sl=1):
                            testInput = mc.listConnections(input, p=True)
                            if testInput == '%s_mult_add.ouput' % loc:
                                break
                            else:
                                test = test + 1

                        if test >= lenght:
                            mc.connectAttr('%s.output' % multNode, '%s.input3D[%s]' % (addNode, test), f=True)
                    except:
                        mc.connectAttr('%s.output' % multNode, '%s.input3D[0]' % addNode, f=True)

                    try:
                        mc.select('%s.input3D[*]' % addNodeRot, r=True)
                        lenght = len(mc.ls(sl=1))
                        test = 0
                        for input in mc.ls(sl=1):
                            testInput = mc.listConnections(input, p=True)
                            if testInput == '%s_mult_addRot.ouput' % loc:
                                break
                            else:
                                test = test + 1

                        if test >= lenght:
                            mc.connectAttr('%s.output' % multNodeRot, '%s.input3D[%s]' % (addNodeRot, test), f=True)
                    except:
                        mc.connectAttr('%s.output' % multNodeRot, '%s.input3D[0]' % addNodeRot, f=True)

                    try:
                        mc.select('%s.input3D[*]' % addNodeScale, r=True)
                        lenght = len(mc.ls(sl=1))
                        test = 0
                        for input in mc.ls(sl=1):
                            testInput = mc.listConnections(input, p=True)
                            if testInput == '%s_mult_addScale.ouput' % loc:
                                break
                            else:
                                test = test + 1

                        if test >= lenght:
                            mc.connectAttr('%s.output' % multNodeScale, '%s.input3D[%s]' % (addNodeScale, test), f=True)
                    except:
                        mc.connectAttr('%s.output' % multNodeScale, '%s.input3D[1]' % addNodeScale, f=True)

                    try:
                        mc.connectAttr('%s.output3D' % addNodeScale, '%s.scale' % grpOff, f=True)
                    except:
                        pass

                ctrlListClean = []
                for loc in locBldRecList:
                    info = loc.split('_')
                    parCons = '%s_%s_%s_ctrl_grpOff_parentConstraint1' % (info[0], info[1], info[2])
                    weight = ''
                    for z in range(500):
                        if mc.objExists('%s.%sW%s' % (parCons, loc, str(z))):
                            weight = '%s.%sW%s' % (parCons, loc, str(z))
                            break

                    for x in ['X', 'Y', 'Z']:
                        try:
                            mc.connectAttr(weight, '%s_mult_add.input2%s' % (loc, x), f=True)
                        except:
                            pass

                        try:
                            mc.connectAttr(weight, '%s_mult_addRot.input2%s' % (loc, x), f=True)
                        except:
                            pass

                    ctrlListClean.append('%s_%s_%s' % (info[0], info[1], info[2]))

                list(set(ctrlListClean))
                for ctrl in ctrlListClean:
                    grpOff = '%s_ctrl_grpOff' % ctrl
                    try:
                        mc.connectAttr('%s_addTrans.output3D' % ctrl, '%s.translate' % grpOff, f=True)
                    except:
                        pass

                    try:
                        mc.connectAttr('%s_addRot.output3D' % ctrl, '%s.rotate' % grpOff, f=True)
                    except:
                        pass

                listCons = []
                connectIBInAnimMode()
                try:
                    mc.select('*bld*_bld_crv', r=True)
                except:
                    pass

                listCons = mc.ls(sl=1)
                if len(listCons) > 0:
                    for con in listCons:
                        mel.eval('selectKey -add -k -f 0 -f 1 ' + con + ';')
                        try:
                            mel.eval('selectKey -add -k -f -1 -f 0 -f 1 ' + con + ';')
                        except:
                            pass

                mc.setAttr('Facial_Rig_ctrl.mode', lock=False)
                mc.setAttr('Facial_Rig_ctrl.mode', 1)
                mc.setAttr('Facial_Rig_ctrl.mode', lock=True)
                mc.warning('You are now in Anim Mode')
            elif mode == 1:
                mc.warning('You already are in Anim Mode, this action will be skiped')
            else:
                mc.error('You cannot back into the Anim mode if you have launch the Optimize Mode.')
        else:
            mc.error('No Facial Rig Ctrl was found, this action will be aborted')
    else:
        mc.error('please add your head controller into the "Head Controller" field')

def connectIBInAnimMode(*args):
    IBNameLocList = []
    IBNameList = []
    IBListClean = []
    try:
        IBNameLocList = mc.ls('*bldIB*_recorder')
    except:
        pass

    if len(IBNameLocList) > 0:
        for locIB in IBNameLocList:
            name = locIB.split('_')[3]
            IBNameList.append(name)

        IBListClean = list(set(IBNameList))
    if len(IBListClean) > 0:
        for nameExp in IBListClean:
            if mc.objExists('*_%s*bldIB*_recorder' % nameExp):
                listOfElement = mc.ls('*_%s*bldIB*_recorder' % nameExp)
                for locIB in listOfElement:
                    locRecorder = locIB.split('IB')[0] + '_recorder'
                    info = locIB.split('_')
                    nb = info[4].split('IB')[1]
                    locNameExp = locRecorder.split('_recorder')[0]
                    locNameOri = '%s_%s_%s' % (info[0], info[1], info[2])
                    parentCons = '%s_ctrl_grpOff_parentConstraint1' % locNameOri
                    mc.select(parentCons, r=True)
                    i = 0
                    for i in range(9999):
                        if mc.objExists('%s.%sW%s' % (parentCons, locRecorder, i)):
                            break
                        else:
                            i = i + 1

                    weightPos = i
                    parentConsWeight = '%s.w%s' % (parentCons, weightPos)
                    for x in ('translate', 'rotate', 'scale'):
                        condNode = '%sIB%s_condIB%s' % (locNameExp, nb, x)
                        masterMult = ''
                        globalAdd = ''
                        if x == 'translate':
                            globalAdd = '%s_addTrans' % locNameOri
                            masterMult = '%s_mult_add' % locRecorder
                        else:
                            if x == 'rotate':
                                globalAdd = '%s_addRot' % locNameOri
                                masterMult = '%s_mult_addRot' % locRecorder
                            else:
                                globalAdd = '%s_addScale' % locNameOri
                                masterMult = '%s_mult_addScale' % locRecorder
                            try:
                                mc.connectAttr('%s.output' % masterMult, '%s.colorIfTrue' % condNode, f=True)
                            except:
                                pass

                            cons = mc.listConnections(globalAdd)
                            i = 0
                            for con in cons:
                                if con == masterMult:
                                    break
                                else:
                                    i = i + 1

                            mc.connectAttr('%s.outColor' % condNode, '%s.input3D[%s]' % (globalAdd, i), f=True)
                            deltaNode = '%s_%s_delta_IB_loc_recorder' % (locNameExp, x)
                            if not mc.objExists(deltaNode):
                                deltaNode = mc.createNode('plusMinusAverage', n=deltaNode)
                                mc.setAttr('%s.operation' % deltaNode, 2)
                            setRangeDelta = '%s_%s_setRange_IB_loc_recorder' % (locNameExp, x)
                            if not mc.objExists(setRangeDelta):
                                setRangeDelta = mc.createNode('setRange', n=setRangeDelta)
                            multDelta = '%s_%s_mult_delta_IB_loc_recorder' % (locNameExp, x)
                            if not mc.objExists(multDelta):
                                multDelta = mc.createNode('multiplyDivide', n=multDelta)
                            resultNode = '%s_%s_result_delta_IB_loc_recorder' % (locNameExp, x)
                            if not mc.objExists(resultNode):
                                resultNode = mc.createNode('plusMinusAverage', n=resultNode)
                            try:
                                mc.connectAttr('%s.%s' % (locRecorder, x), '%s.input3D[0]' % deltaNode, f=True)
                            except:
                                pass

                            try:
                                mc.connectAttr('%s.%s' % (locIB, x), '%s.input3D[1]' % deltaNode, f=True)
                            except:
                                pass

                            try:
                                for axis in ['X', 'Y', 'Z']:
                                    mc.connectAttr('%s.secondTerm' % condNode, '%s.oldMin%s' % (setRangeDelta, axis), f=True)
                                    mc.setAttr('%s.max%s' % (setRangeDelta, axis), 1)
                                    mc.setAttr('%s.oldMax%s' % (setRangeDelta, axis), 1)
                                    mc.connectAttr(parentConsWeight, '%s.value%s' % (setRangeDelta, axis), f=True)

                            except:
                                pass

                            try:
                                mc.connectAttr('%s.outValue' % setRangeDelta, '%s.input1' % multDelta, f=True)
                            except:
                                pass

                            try:
                                mc.connectAttr('%s.output3D' % deltaNode, '%s.input2' % multDelta, f=True)
                            except:
                                pass

                            try:
                                mc.connectAttr('%s.output' % multDelta, '%s.input3D[1]' % resultNode, f=True)
                            except:
                                pass

                            try:
                                mc.connectAttr('%s.colorIfFalse' % condNode, '%s.input3D[0]' % resultNode, f=True)
                            except:
                                pass

                            try:
                                mc.connectAttr('%s.output3D' % resultNode, '%s.colorIfTrue' % condNode, f=True)
                            except:
                                pass

