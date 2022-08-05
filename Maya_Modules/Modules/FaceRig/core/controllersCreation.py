# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.mel as mel

def ctrlCreation(type, nameCtrl, *args):
    mc.select(cl=1)
    if type == 'rectangle':
        mel.eval('curve -d 1 -p -2 -3 0 -p -2 3 0 -p 2 3 0 -p 2 -3 0 -p -2 -3 0 -k 0 -k 1 -k 2 -k 3 -k 4 ;')
    elif type == 'square':
        mel.eval('curve -d 1 -p -2 2 0 -p -2 -2 0 -p 2 -2 0 -p 2 2 0 -p -2 2 0 -k 0 -k 1 -k 2 -k 3 -k 4 ;')
    elif type == 'triangle':
        mel.eval('curve -d 1 -p -2 -2 0 -p 2 -2 0 -p 0 2 0 -p -2 -2 0 -k 0 -k 1 -k 2 -k 3 ;')
    elif type == 'circle':
        mel.eval('circle -c 0 0 0 -nr 0 0 1 -sw 360 -r 2 -d 3 -ut 0 -tol 0.01 -s 8 -ch 1;')
        mc.scale(2, 2, 2)
    elif type == 'star':
        mel.eval('curve -d 1 -p -1 1 0 -p 0 3 0 -p 1 1 0 -p 3 0 0 -p 1 -1 0 -p 0 -3 0 -p -1 -1 0 -p -3 0 0 -p -1 1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 ;')
    elif type == 'cross':
        mel.eval('curve -d 1 -p -1 1 0 -p -1 3 0 -p -2 3 0 -p 0 5 0 -p 2 3 0 -p 1 3 0 -p 1 1 0 -p 3 1 0 -p 3 2 0 -p 5 0 0 -p 3 -2 0 -p 3 -1 0 -p 1 -1 0 -p 1 -3 0 -p 2 -3 0 -p 0 -5 0 -p -2 -3 0 -p -1 -3 0 -p -1 -1 0 -p -3 -1 0 -p -3 -2 0 -p -5 0 0 -p -3 2 0 -p -3 1 0 -p -1 1 0 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15 -k 16 -k 17 -k 18 -k 19 -k 20 -k 21 -k 22 -k 23 -k 24 ;')
    elif type == 'sphere':
        mc.sphere()
    elif type == 'custom':
        custCtrl = mc.textScrollList('otherCtrlShapeList', q=1, ai=1)
        mc.select(custCtrl, r=True)
    ctrl = mc.ls(sl=1)[0]
    side = nameCtrl.split('_')[0]
    mc.rename(ctrl, nameCtrl)
    if type != 'square':
        mc.scale(0.5, 0.5, 0.5)
    ctrl = nameCtrl
    mc.makeIdentity(a=1)
    mc.delete(ch=1)
    mc.setAttr('%s.overrideEnabled' % ctrl, 1)
    if side == 'L':
        mc.setAttr('%s.overrideColor' % ctrl, 13)
    elif side == 'R':
        mc.setAttr('%s.overrideColor' % ctrl, 6)
    else:
        mc.setAttr('%s.overrideColor' % ctrl, 17)
    return ctrl

def addAttrToController(controller, attribute, type):
    ctrl = mc.ls(controller)[0]
    if type == 'double':
        mc.addAttr(ctrl, ln=attribute, at=type, dv=0)
        mc.setAttr('%s.%s' % (ctrl, attribute), e=1, keyable=1)
    elif type == 'minMax0':
        mc.addAttr(ctrl, ln=attribute, at='double', min=0, max=1, dv=0)
        mc.setAttr('%s.%s' % (ctrl, attribute), e=1, keyable=1)
    elif type == 'minMax1':
        mc.addAttr(ctrl, ln=attribute, at='double', min=-1, max=1, dv=0)
        mc.setAttr('%s.%s' % (ctrl, attribute), e=1, keyable=1)
    elif type == 'sep':
        mc.addAttr(ctrl, ln='%sSep' % attribute, nn='------', at='enum', en='%s:' % attribute)
        mc.setAttr('%s.%sSep' % (ctrl, attribute), e=1, lock=1, keyable=1)
    elif type == 'int':
        mc.addAttr(ctrl, ln=attribute, at='long', dv=0, max=2, min=0)
        mc.setAttr('%s.%s' % (ctrl, attribute), e=1, lock=1, k=False, cb=False)

def facialControllerExpression(*args):
    nameObj = 'Facial_Rig_ctrl'
    if not mc.objExists(nameObj):
        mel.eval('circle -c 0 0 0 -nr 0 0 1 -sw 360 -r 1 -d 3 -ut 0 -tol 0.01 -s 8 -ch 1;')
        ctrl1 = mc.ls(sl=1)[0]
        mel.eval('circle -c 0 0 0 -nr 0 0 1 -sw 360 -r 1 -d 3 -ut 0 -tol 0.01 -s 8 -ch 1;scale -r 0.354425 0.354425 0.354425 ;scale -r 0.557452 1 1 ;move -r -0.388623 0.402024 0 ;move -r -os -wd 0 -0.201012 0 ;')
        ctrl2 = mc.ls(sl=1)[0]
        mel.eval('duplicate -rr;')
        ctrl3 = mc.ls(sl=1)[0]
        mc.setAttr('%s.translateX' % ctrl3, 0.389)
        mel.eval('circle -c 0 0 0 -nr 0 0 1 -sw 360 -r 1 -d 3 -ut 0 -tol 0.01 -s 8 -ch 1; move -r -os -wd 0 0 0 ;scale -r 1 0.312984 1 ;scale -r 0.555694 0.555694 0.555694 ;move -r -os -wd 0 -0.515931 0 ;')
        ctrl4 = mc.ls(sl=1)[0]
        ctrlMaster = mc.group(n=nameObj, em=True)
        for i in range(2):
            for x in [ctrl1, ctrl2, ctrl3, ctrl4]:
                if i == 0:
                    mc.makeIdentity(x, a=1)
                    mc.delete(x, ch=1)
                    mc.select(cl=1)
                else:
                    mc.select(mc.listRelatives(x)[0], add=True)

        mc.select(ctrlMaster, add=True)
        mc.parent(r=True, s=True)
        mc.delete(ctrl1, ctrl2, ctrl3, ctrl4)
        mc.setAttr('%s.ove' % ctrlMaster, 1)
        mc.setAttr('%s.ovc' % ctrlMaster, 21)
        addAttrToController(ctrlMaster, 'mode', 'int')
        addAttrToController(ctrlMaster, 'mouthCorrection', 'sep')
        addAttrToController(ctrlMaster, 'open_mouth', 'double')
        addAttrToController(ctrlMaster, 'side_mouth', 'double')
        addAttrToController(ctrlMaster, 'twist_mouth', 'double')
        addAttrToController(ctrlMaster, 'jaw', 'minMax1')
        addAttrToController(ctrlMaster, 'jawDown', 'minMax1')
        mc.setAttr('%s.mode' % ctrlMaster, e=1, lock=1)
        mc.select(ctrlMaster, r=True)
    else:
        mc.warning('Facial Rig Controller was already found, this action is aborted')
        mc.select(nameObj, r=True)

def validPositionOfFacialControllerExpression(*args):
    facialCtrl = 'Facial_Rig_ctrl'
    if mc.objExists(facialCtrl):
        try:
            headCtrl = mc.textScrollList('headCtrlBlendShape', q=True, ai=True)[0]
            mc.parentConstraint(headCtrl, facialCtrl, mo=True)
            mc.scaleConstraint(headCtrl, facialCtrl, mo=True)
            for typ in ['t', 'r', 's']:
                for axis in ['x', 'y', 'z']:
                    mc.setAttr('%s.%s%s' % (facialCtrl, typ, axis), cb=False, k=False)

        except:
            raise mc.error('No controller was found into the Head Controller Field, please add your head controller before to do.')

    else:
        raise mc.error('No Facial_Rig_ctrl was found ! This action is aborted')

def AttachAndOrganizeCCFacial(*args):
    try:
        mc.select('animCurveU*', r=True)
        mc.delete(mc.ls(sl=1))
    except:
        pass

    bldCrvs = []
    try:
        mc.select('*_bld_crv', r=True)
        try:
            mc.select('*_*_bld_*bld_crv', d=True)
        except:
            pass

        try:
            mc.select('*_*_bldExp_*bld_crv', d=True)
        except:
            pass

        sel = mc.ls(sl=1)
        for bldCrv in sel:
            bldCrvs.append(bldCrv)

        attrs = []
        mc.select('Facial_Rig_ctrl', r=True)
        ctrl = mc.ls(sl=1)[0]
        listAttrs = mc.listAttr(ctrl)
        nb = len(listAttrs)
        ctrlF = 'Facial_Rig_ctrl'
        attrs = []
        listAttrs = mc.listAttr(ctrlF)
        count = 0
        for attr in listAttrs:
            if count == 0:
                if attr == 'mouthCorrectionSep':
                    count = 1
            else:
                attrs.append(attr)

        try:
            mc.select('*_Open_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            mc.select('*_squash_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            mc.select('*_stretch_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            mc.select('*_Side*_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            mc.select('*_Twist*_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            mc.select('*_Jaw*_bld_crv', r=True)
            listToRemove = mc.ls(sl=1)
            for elt in listToRemove:
                for crv in bldCrvs:
                    if elt == crv:
                        bldCrvs.remove(crv)
        except:
            pass

        try:
            for crv in bldCrvs:
                if crv.split('_')[2] == 'bld':
                    bldCrvs.remove(crv)
        except:
            pass

        try:
            for crv in bldCrvs:
                if crv.split('_')[2] == 'bld':
                    bldCrvs.remove(crv)
        except:
            pass
        supAndAddNewAttributeToFacialController(attrs, bldCrvs)
    except:
        raise mc.error('no blendshape was found, this action will be aborted')

def supAndAddNewAttributeToFacialController(attrs, bldCrvs, *args):
    radValue = 1
    attrs = attrs
    partList = []
    typeList = []
    partList2 = []
    typeList2 = []
    attrsToRemove = []
    ctrl = 'Facial_Rig_ctrl'
    if mc.objExists(ctrl):
        for crv in bldCrvs:
            mc.select(crv, r=True)
            part = crv.split('_')[2]
            partList.append(part)
            for elt in partList:
                try:
                    ind = partList2.index(elt)
                except:
                    partList2.append(elt)

            type = crv.split('_')[1]
            typeList.append(type)
            for elt in typeList:
                try:
                    ind = typeList2.index(elt)
                except:
                    typeList2.append(elt)

        for attr in attrs:
            for elt in partList2:
                if elt == attr:
                    attrsToRemove.append(elt)

        for crv in bldCrvs:
            attr = crv.split('_bld_crv')[0]
            attrsToRemove.append(attr)

        lenght = len(attrsToRemove)
        if lenght > 0:
            for attrCtrl in attrs:
                for attr in attrsToRemove:
                    if attr == attrCtrl:
                        try:
                            mc.setAttr('%s.%s' % (ctrl, attr), lock=False)
                        except:
                            pass

                        try:
                            mc.deleteAttr(ctrl + '.' + attr)
                        except:
                            pass

        if radValue == 1:
            for elt in partList2:
                ctrl = 'Facial_Rig_ctrl'
                if mc.objExists('%s.%s' % (ctrl, elt)):
                    try:
                        mc.setAttr('%s.%s' % (ctrl, elt), lock=False)
                        mc.deleteAttr(ctrl + '.' + elt)
                    except:
                        pass

                mc.addAttr(ctrl, ln=elt, at='bool')
                mc.setAttr(ctrl + '.' + elt, e=1, k=1, lock=1)
                for crv in bldCrvs:
                    mc.select(crv, r=True)
                    crv = mc.ls(sl=1)[0]
                    part = crv.split('_')[2]
                    if part == elt:
                        mc.addAttr(ctrl, ln=crv.split('_bld_crv')[0], at='double', min=0, max=1, dv=0)
                        mc.setAttr(ctrl + '.' + crv.split('_bld_crv')[0], e=1, k=1)
                        info = crv.split('_')
                        name = crv.split('_bld_crv')[0]
                        bldNodeName = info[0] + '_' + info[1] + '_bldExp'
                        mc.setAttr('%s.%s' % (ctrl, name), 0)
                        mc.setAttr('%s.%s' % (bldNodeName, crv), 0)
                        mc.setDrivenKeyframe('%s.%s' % (bldNodeName, crv), currentDriver='%s.%s' % (ctrl, name))
                        mc.setAttr('%s.%s' % (ctrl, name), 1)
                        mc.setAttr('%s.%s' % (bldNodeName, crv), 1)
                        mc.setDrivenKeyframe('%s.%s' % (bldNodeName, crv), currentDriver='%s.%s' % (ctrl, name))
                        mc.setAttr('%s.%s' % (ctrl, name), 0)
        mc.select(ctrl, r=True)
