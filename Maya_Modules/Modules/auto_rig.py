# -*- coding: utf-8 -*-

import sys
import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

kWindowName = 'ReRig_Window'
kWindowHelpName = 'ReHelp_window'

"""
using
import auto_rig
import importlib
importlib.reload(auto_rig)
auto_rig.CreateAutoRigWindow()
"""


def CreateAutoRigWindow():
    if cmds.window('ReRig_window', exists=True):
        cmds.deleteUI('ReRig_window')

    cmds.window('ReRig_window', title="Reanimted Rigging Tool", menuBar=False, widthHeight=(500, 300))

    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    child1 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(CreateHelpWindow, 'CreateFKControls'), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.text(label='Lock following attributes:', font="plainLabelFont", align="left")
    cmds.paneLayout()
    cmds.textScrollList('ReRig_fkControlLocAttr', numberOfRows=8, allowMultiSelection=True,
                        append=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                        selectItem=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'], showIndexedItem=4)
    cmds.setParent('..')
    cmds.text(label='Type of constraint:', font="plainLabelFont", align="left")
    cmds.radioCollection('ReRig_fkConstraintType')
    cmds.rowColumnLayout(numberOfColumns=3)
    cmds.radioButton('ReRig_fkConstraintType_point', label='Point')
    cmds.radioButton('ReRig_fkConstraintType_orient', label='Orient')
    cmds.radioButton('ReRig_fkConstraintType_parent', label='Parent')
    cmds.radioCollection('ReRig_fkConstraintType', edit=True, select='ReRig_fkConstraintType_orient')
    cmds.setParent('..')
    cmds.button(label="Create FK Controls", command=CreateFkControlesButton)
    cmds.text(label='')
    cmds.button(label="Parent FK Controls", command=ParentFKControlsButton)
    cmds.setParent('..')

    child4 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(CreateHelpWindow, 'scaleFkControles'), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.button(label="List all FK controles", command=ListFkControllesButton)
    cmds.textFieldGrp('ReRig_fkControlSelect', changeCommand=ChangeScaleFkSelectButton)
    cmds.paneLayout()
    cmds.textScrollList('ReRig_fkControlList', numberOfRows=8, allowMultiSelection=True,
                        append=[], showIndexedItem=4)
    cmds.setParent('..')
    cmds.floatSliderGrp('ReRig_fkControlScale', field=True, label='Scale Fk Controles ',
                        minValue=0.01, maxValue=5, fieldMinValue=0.01, fieldMaxValue=20, value=1, precision=2,
                        dragCommand=ChangeScaleFkButton, changeCommand=ChangeScaleFkButton)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Freeze transformations", command=FreezeTransformationsButton)
    cmds.text(label='Freeze transformations on selected controls.', font="plainLabelFont", align="left")
    cmds.setParent('..')
    cmds.setParent('..')

    child2 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.radioCollection('ReRig_addToJoints')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.radioButton('ReRig_addToJoints_selected', label='Selected joints')
    cmds.radioButton('ReRig_addToJoints_hierarchy', label='Joint hierarchy')
    cmds.radioCollection('ReRig_addToJoints', edit=True, select='ReRig_addToJoints_hierarchy')
    cmds.setParent('..')
    cmds.button(label="Add '_bn' To All Joints", command=RenameJointsButton)
    cmds.text(label='')
    cmds.button(label="Create Main Groups", command=CreateMainGroupsButton)
    cmds.text(label='')
    cmds.button(label="Change displayed joint size", command=DisplayJointSizeButton)
    cmds.setParent('..')

    child3 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(CreateHelpWindow, 'biPedAutoRig'), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.radioCollection('ReRig_mirrorTempSkeleton')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.radioButton('ReRig_mirrorTempSkeleton_true', label='Mirror joint position on both sides')
    cmds.radioButton('ReRig_mirrorTempSkeleton_false', label='Unique positions')
    cmds.radioCollection('ReRig_mirrorTempSkeleton', edit=True, select='ReRig_mirrorTempSkeleton_true')
    cmds.setParent('..')
    cmds.button(label="Position Your Joints", command=CreateTempSkeletonButton)
    cmds.text(label='')
    cmds.text(label='Choose which elements you want to incorporate:', font="plainLabelFont", align="left")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.checkBox('reRig_autoRigArm', label='Create Arms')
    cmds.checkBox('reRig_autoRigUlna', label='Extra bone in forearm')
    cmds.checkBox('reRig_autoRigLeg', label='Create Legs')
    cmds.checkBox('reRig_autoRigFingers', label='Create Fingers')
    cmds.checkBox('reRig_autoRigSpine', label='Create Spine')
    cmds.checkBox('reRig_autoRigHead', label='Create Head')
    cmds.checkBox('reRig_autoMasterCtrl', label='Master Control')
    cmds.setParent('..')
    cmds.intSliderGrp('reRig_numberOfJt', field=True, label='Number of bones in spine ',
                      minValue=2, maxValue=10, fieldMinValue=2, fieldMaxValue=20, value=4)
    cmds.floatSliderGrp('reRig_heightWaistFK', field=True, label='Height for the FK contol ',
                        minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=21, value=0.28, precision=2)
    cmds.button(label="Create Your Rig", command=CreateBiPedRigButton)
    cmds.setParent('..')

    cmds.tabLayout(tabs, edit=True, tabLabel=(
        (child1, 'Create Fk Controles'), (child4, 'Scale Fk Controls'),
        (child2, 'Organize'), (child3, 'Bi-Ped Auto Rig')))

    cmds.showWindow()


def CreateHelpWindow(text, *args):
    if cmds.window('ReHelp_window', exists=True):
        cmds.deleteUI('ReHelp_window')

    cmds.window('ReHelp_window', title="Help", menuBar=False)
    cmds.rowColumnLayout(numberOfColumns=1)
    if text == 'CreateFKControls':
        cmds.text(label='Create Easy FK Controls', font="boldLabelFont", align="left")
        cmds.text(label='Select all the joints you want to create a FK control for.', font="plainLabelFont",
                  align="left")
        cmds.text(label='Make sure you have named your joints properly.', font="plainLabelFont", align="left")
        cmds.text(label='Your joints should be named: nameOnJoint_bn', font="plainLabelFont", align="left")
        cmds.text(label='Select the attributes you want to look on your control.', font="plainLabelFont", align="left")
        cmds.text(label='Select which type of constraint you want to create: point, parent or orient.',
                  font="plainLabelFont", align="left")
        cmds.text(label="")
        cmds.text(label='Parent FK Controls', font="boldLabelFont", align="left")
        cmds.text(label='Select the child fk control first then the parent control.', font="plainLabelFont",
                  align="left")
        cmds.text(label='Example: hand_ctrl -> elbow_ctrl -> shoulder_ctrl.', font="plainLabelFont", align="left")
        cmds.text(label='Works with all controls created by the Reanimted Rigging Tool.', font="plainLabelFont",
                  align="left")
    if text == 'biPedAutoRig':
        cmds.text(label='Welcome To The Auto Rigging Script!', font="boldLabelFont", align="left")
        cmds.text(label='You can choose to create a full bi-ped rig or just some part of it.', font="plainLabelFont",
                  align="left")
        cmds.text(label='To start you need to position out where you want your skeleton to go.', font="plainLabelFont",
                  align="left")
        cmds.text(label='Make sure your character are standing on the grid and facing front view. ',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Start by creating your temporary skeleton. Do this by clicking on "Position Your Joints".',
                  font="plainLabelFont", align="left")
        cmds.text(label='This skeleton you can scale, translate and rotate how ever you want to.',
                  font="plainLabelFont", align="left")
        cmds.text(label='It will not effect your final rig.', font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Mirror joint position on both sides', font="boldLabelFont", align="left")
        cmds.text(label='Use this option if your character is mirrored and has symmetric geometry. This is standard.',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Unique positions', font="boldLabelFont", align="left")
        cmds.text(label='Use this option if your character has asymmetric geometry.', font="plainLabelFont",
                  align="left")
        cmds.text(label='')
        cmds.text(label='Create your final rig', font="boldLabelFont", align="left")
        cmds.text(label='When you are done with the position of your joints, you need to choose with element you',
                  font="plainLabelFont", align="left")
        cmds.text(label='want to incorporate (arms, legs, spine, fingers and head).',
                  font="plainLabelFont", align="left")
        cmds.text(label='You can also choose how many joint you want in your rig and how high up you waist fk control',
                  font="plainLabelFont", align="left")
        cmds.text(label='will be. This will only be calculated if you have selected "spine".',
                  font="plainLabelFont", align="left")
    if text == 'scaleFkControles':
        cmds.text(label='Scale FK Controls', font="boldLabelFont", align="left")
        cmds.text(label='Here you can scale all FK controls created with the script.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Start by listing all FK controls, which you do by clicking on "List all FK controls".',
                  font="plainLabelFont", align="left")
        cmds.text(label='Select X numbers of controls from the list, or type in key words in the field above.',
                  font="plainLabelFont", align="left")
        cmds.text(label='You can type in multiply keywords. Separate them with space. Ex: "thumb toe index"',
                  font="plainLabelFont", align="left")
        cmds.text(label='Use the slider or type in a value which you want your control to scale.',
                  font="plainLabelFont", align="left")
        cmds.text(label="When you are done, it's important to freeze your controls. Select the controls",
                  font="plainLabelFont", align="left")
        cmds.text(label='you have scaled (or all, if you are unsure) and "Freeze transformations".',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
    cmds.showWindow()


def CreateFkControlesButton(self):
    attr = cmds.textScrollList('ReRig_fkControlLocAttr', q=True, selectItem=True)
    radioButton = cmds.radioCollection('ReRig_fkConstraintType', q=True, select=True)
    const = radioButton.rsplit('_', 1)[1]
    CreateFkControles(jointList=cmds.ls(sl=True), lockAttributes=attr, constraint=const)


def ParentFKControlsButton(self):
    ParentFKControls(controlList=cmds.ls(sl=True))


def RenameJointsButton(self):
    if cmds.radioCollection('ReRig_addToJoints', q=True, select=True) == 'ReRig_addToJoints_hierarchy':
        cmds.select(hi=True)
        jtList = cmds.ls(sl=True)
    else:
        jtList = cmds.ls(sl=True)
    RenameJoints(jointList=jtList, add='_bn')


def CreateMainGroupsButton(self):
    CreateMainGroups()


def CreateTempSkeletonButton(self):
    if cmds.objExists('scale_tempSkeleton_ctrl'):
        cmds.delete('scale_tempSkeleton_ctrl')
        OpenMaya.MGlobal.displayInfo("Deleted you existing temporary skelition and created a new one.")
    else:
        OpenMaya.MGlobal.displayInfo("Created a temporary skeletion.")

    CreateTempSkeletonSpine()
    CreateTempSkeletonLeg()
    cmds.select('c_neck_tempJt')
    CreateTempSkeletonArm()
    cmds.select('l_wrist_tempJt')
    CreateTempSkeletonFingers()

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_false':
        cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
        cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

    tempSkelCtrl = CreateTempSkeletonControl(name='scale_tempSkeleton_ctrl')
    cmds.parent('c_hip_tempJt', tempSkelCtrl)
    cmds.select(tempSkelCtrl)


def ListFkControllesButton(self):
    fkListRawList = cmds.ls('*.fkControl')
    cleanList = []
    for item in fkListRawList:
        ctrl = item.split('.')
        cleanList.append(ctrl[0])
    cmds.textScrollList('ReRig_fkControlList', edit=True, append=cleanList)


def ChangeScaleFkButton(self):
    fkList = cmds.textScrollList('ReRig_fkControlList', q=True, selectItem=True)
    scale = cmds.floatSliderGrp('ReRig_fkControlScale', q=True, value=True)

    attr = ['sx', 'sy', 'sz']

    if fkList is None:
        OpenMaya.MGlobal.displayWarning("Please select the controls you want to change size.")
    else:
        for item in fkList:
            for a in attr:
                cmds.setAttr(item + '.' + a, lock=False)
            cmds.setAttr(item + '.sy', scale)
            cmds.setAttr(item + '.sz', scale)


def ChangeScaleFkSelectButton(self):
    text = cmds.textFieldGrp('ReRig_fkControlSelect', q=True, text=True)
    fkList = cmds.textScrollList('ReRig_fkControlList', q=True, allItems=True)
    keywords = text.split(' ')
    selectList = []
    cmds.textScrollList('ReRig_fkControlList', e=True, deselectAll=True)
    if fkList is None:
        OpenMaya.MGlobal.displayWarning("Your list with FK controls is empty! ):")
    else:
        for item in fkList:
            for key in keywords:
                if key in item:
                    selectList.append(item)

    cmds.textScrollList('ReRig_fkControlList', e=True, selectItem=selectList)


def FreezeTransformationsButton(self):
    fkList = cmds.textScrollList('ReRig_fkControlList', q=True, selectItem=True)
    attr = ['sx', 'sy', 'sz']
    if fkList is None:
        OpenMaya.MGlobal.displayWarning("Please select the FK controls you want to freeze.")
    else:
        for item in fkList:
            if cmds.getAttr(item + '.sx', lock=True) is False:
                cmds.makeIdentity(item, apply=True, scale=True)
                for a in attr:
                    cmds.setAttr(item + '.' + a, lock=True)


def CreateBiPedRigButton(self):
    if not cmds.objExists('scale_tempSkeleton_ctrl'):
        OpenMaya.MGlobal.displayWarning("You need to position your joints before you create your rig.")

    else:
        scale = cmds.getAttr('scale_tempSkeleton_ctrl.scaleX')

        resultList = []

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            CreateMainGroups()
            CreateSpineJoints(scale=scale, side='c',
                              numberOfJoints=cmds.intSliderGrp('reRig_numberOfJt', q=True, value=True))
            resultList.append('SPINE')

        if cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
            CreateMainGroups()
            CreateArmJoints(side='l', scale=scale)
            if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                                    select=True) == 'ReRig_mirrorTempSkeleton_false':
                CreateArmJoints(side='r', scale=scale)
            resultList.append('ARMS')

        if cmds.checkBox('reRig_autoRigLeg', q=True, value=True) is True:
            CreateMainGroups()
            CreateLegJoints(side='l', scale=scale)
            if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                                    select=True) == 'ReRig_mirrorTempSkeleton_false':
                CreateLegJoints(side='r', scale=scale)
            resultList.append('LEGS')

        if cmds.checkBox('reRig_autoRigHead', q=True, value=True) is True:
            CreateMainGroups()
            CreateHeadJoints(scale=scale, side='c')
            resultList.append('HEAD')

        if cmds.checkBox('reRig_autoRigFingers', q=True, value=True) is True and cmds.checkBox('reRig_autoRigArm',
                                                                                               q=True,
                                                                                               value=True) is True:
            CreateMainGroups()
            CreateFingerJoints(scale=scale, side='l')
            CreateFingerJoints(scale=scale, side='r')
            resultList.append('FINGERS')

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True and cmds.checkBox('reRig_autoRigArm',
                                                                                             q=True,
                                                                                             value=True) is True:
            ConnectArmToSpine()

        if cmds.checkBox('reRig_autoMasterCtrl', q=True, value=True) is True:
            CreateMasterControl(scale=scale)
            resultList.append('MASTER CONTROL')

        cleanString = CleanListToString(dirtyList=resultList)

        if cmds.checkBox('reRig_autoRigFingers', q=True, value=True) is True and cmds.checkBox('reRig_autoRigArm',
                                                                                               q=True,
                                                                                               value=True) is False:
            OpenMaya.MGlobal.displayWarning(
                "You can NOT create fingers without an arm! Successfully created: " + cleanString + '.')
        else:
            OpenMaya.MGlobal.displayInfo("Successfully created: " + cleanString + '.')


def DisplayJointSizeButton(self):
    mel.eval('jdsWin;')


def CreateFkControles(**kwargs):
    selection = kwargs.setdefault("jointList")
    locAttr = kwargs.setdefault("lockAttributes", ['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'])
    ulna = kwargs.setdefault("ulna", False)
    scale = kwargs.setdefault("scale", 1)
    rOrder = kwargs.setdefault("rotateOrder", 0)
    fkAttr = kwargs.setdefault('addFkAttribute', True)
    const = kwargs.setdefault('constraint', 'orient')

    if selection is []:
        OpenMaya.MGlobal.displayWarning("You have to at least select 1 joint.")

    ctrlList = []

    for obj in selection:
        nameSplit = obj.rsplit('_', 1)
        if len(nameSplit) >= 2:
            cmds.setAttr(obj + ".rotateOrder", rOrder)
            name = nameSplit[0]
            grp = cmds.group(empty=True, name=name + '_ctrlGrp')
            cmds.parent(grp, obj, r=True)
            cmds.parent(grp, w=True)
            ctrl = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), name=name + '_ctrl', radius=1)
            cmds.setAttr(ctrl[0] + ".rotateOrder", rOrder)
            cmds.parent(ctrl[0], grp, r=True)
            cmds.scale(scale, scale, scale, grp)
            if ulna is True:
                ulnaJt = cmds.listRelatives(obj, parent=True)
                cmds.orientConstraint(ctrl[0], obj, mo=False, skip='x')
                cmds.orientConstraint(ctrl[0], ulnaJt, mo=True, skip=['y', 'z'])
            elif const == 'point':
                cmds.pointConstraint(ctrl[0], obj, mo=False)
            elif const == 'parent':
                cmds.parentConstraint(ctrl[0], obj, mo=False)
            elif const == 'orient':
                cmds.orientConstraint(ctrl[0], obj, mo=False)

            if fkAttr is True:
                cmds.addAttr(ctrl[0], longName='fkControl', attributeType='float', keyable=True)
                locAttr.append('fkControl')
            ctrlList.append(ctrl[0])
            for loc in locAttr:
                cmds.setAttr(ctrl[0] + '.' + loc, lock=True, keyable=False, channelBox=False)
            cmds.setAttr(ctrl[0] + '.v', lock=False)
        else:
            OpenMaya.MGlobal.displayWarning("Your joints are not named correctly: jointName_bn")

    return ctrlList


def ParentFKControls(**kwargs):
    ctrlList = kwargs.setdefault("controlList")
    ctrlGrpList = []
    ctrlParentList = []

    for ctrl in ctrlList:
        nameSplit = ctrl.rsplit('_', 1)
        if 'ctrl' == nameSplit[-1]:
            index = ctrlList.index(ctrl)
            ctrlGrp = cmds.listRelatives(ctrl, parent=True)[0]
            ctrlGrpList.append(ctrlGrp)
            if ctrl != ctrlList[-1]:
                parentCtrl = ctrlList[index + 1]
                cmds.parentConstraint(parentCtrl, ctrlGrp, maintainOffset=True)
                ctrlParentList.append(ctrl)
        else:
            OpenMaya.MGlobal.displayWarning(
                ctrl + " is not a control object. If it is, make sure it's named correctly: controlobject_ctrl")

    if ctrlParentList != []:
        cleanString = CleanListToString(dirtyList=ctrlParentList)
        OpenMaya.MGlobal.displayInfo("Managed to successfully parent " + cleanString + ".")

    return ctrlGrpList


def RenameJoints(**kwargs):
    jtList = kwargs.setdefault("jointList")
    add = kwargs.setdefault("add")

    newJtList = []

    for jt in jtList:
        try:
            cmds.joint(jt, edit=True, name=jt + add)
            newJtList.append(jt + add)
        except:
            OpenMaya.MGlobal.displayWarning(jt + " is not a joint.")

    return newJtList


def CreateMainGroups():
    grpList = []

    if not cmds.objExists('SKIN'):
        cmds.group(empty=True, name='SKIN')
        grpList.append('SKIN')
    if not cmds.objExists('JOINTS'):
        cmds.group(empty=True, name='JOINTS')
        grpList.append('JOINTS')
    if not cmds.objExists('CONTROLS'):
        cmds.group(empty=True, name='CONTROLS')
        grpList.append('CONTROLS')
    if not cmds.objExists('DO_NOT_TOUCH'):
        cmds.group(empty=True, name='DO_NOT_TOUCH')
        grpList.append('DO_NOT_TOUCH')
    if not cmds.objExists('LEFT'):
        cmds.group(empty=True, name='LEFT')
        cmds.parent('LEFT', 'CONTROLS')
        cmds.setAttr("LEFT.overrideEnabled", True)
        cmds.setAttr("LEFT.overrideColor", 6)
        grpList.append('LEFT')
    if not cmds.objExists('RIGHT'):
        cmds.group(empty=True, name='RIGHT')
        cmds.parent('RIGHT', 'CONTROLS')
        grpList.append('RIGHT')
        cmds.setAttr("RIGHT.overrideEnabled", True)
        cmds.setAttr("RIGHT.overrideColor", 13)
    if not cmds.objExists('CENTER'):
        cmds.group(empty=True, name='CENTER')
        cmds.parent('CENTER', 'CONTROLS')
        cmds.setAttr("CENTER.overrideEnabled", True)
        cmds.setAttr("CENTER.overrideColor", 17)
        grpList.append('CENTER')
    return grpList


def CreateTempSkeletonSpine():
    cmds.joint(name='c_hip_tempJt', position=(0, 11.7, 0))
    cmds.joint(name='c_neck_tempJt', position=(0, 18, 0))
    cmds.joint('c_hip_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='c_head_tempJt', position=(0, 18.6, 0.6))
    cmds.joint('c_neck_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='c_headTop_tempJt', position=(0, 20.7, 0.6))
    cmds.joint('c_head_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.select('c_hip_tempJt')
    cmds.joint(name='c_lowerHip_tempJt', position=(0, 11.2, 0))


def CreateTempSkeletonLeg():
    cmds.joint(name='l_hip_tempJt', position=(1.2, 10.7, 0))
    cmds.joint(name='l_hipFront_tempJt', position=(1.2, 10.7, 0.8))
    cmds.select('l_hip_tempJt')
    cmds.joint(name='l_knee_tempJt', position=(1.2, 5.8, 0.5))
    cmds.joint(name='l_kneeFront_tempJt', position=(1.2, 5.8, 1.3))
    cmds.select('l_knee_tempJt')
    cmds.joint('l_hip_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_ankle_tempJt', position=(1.2, 1.2, -0.3))
    cmds.joint('l_knee_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_heelFoot_tempJt', position=(1.2, 0, -1.1))
    cmds.joint('l_ankle_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_toe_tempJt', position=(1.2, 0, 1.1))
    cmds.joint('l_heelFoot_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_toeEnd_tempJt', position=(1.2, 0, 2.2))
    cmds.joint('l_toe_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.select('l_heelFoot_tempJt')
    cmds.joint(name='l_footOuter_tempJt', position=(2, 0, 1.1))
    cmds.select('l_heelFoot_tempJt')
    cmds.joint(name='l_footInner_tempJt', position=(0.7, 0, 1.1))


def CreateTempSkeletonArm():
    cmds.joint(name='l_collarbone_tempJt', position=(1, 16.5, 0))
    cmds.joint(name='l_shoulder_tempJt', position=(2.2, 17.4, 0))
    cmds.joint('l_collarbone_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_elbow_tempJt', position=(5.3, 16.9, -0.5))
    cmds.joint('l_shoulder_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_wrist_tempJt', position=(8.2, 16.7, 0))
    cmds.joint('l_elbow_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_middleHand_tempJt', position=(9, 16.7, 0))
    cmds.joint('l_wrist_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.select('l_wrist_tempJt')
    cmds.joint(name='l_handUp_tempJt', position=(8.2, 17.5, 0))


def CreateTempSkeletonFingers():
    cmds.joint(name='l_innerHand_tempJt', position=(8.3, 16.7, 0.4))
    cmds.joint(name='l_thumb01_tempJt', position=(9, 16.7, 0.8))
    cmds.joint('l_innerHand_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_thumb02_tempJt', position=(9.5, 16.7, 0.8))
    cmds.joint('l_thumb01_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_thumb03_tempJt', position=(10, 16.7, 0.8))
    cmds.joint('l_thumb02_tempJt', edit=True, zso=True, oj='xyz', sao='yup')

    cmds.select('l_middleHand_tempJt')
    cmds.joint(name='l_indexFinger01_tempJt', position=(9.6, 16.7, 0.3))
    cmds.joint(name='l_indexFinger02_tempJt', position=(10.1, 16.7, 0.3))
    cmds.joint('l_indexFinger01_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_indexFinger03_tempJt', position=(10.6, 16.7, 0.3))
    cmds.joint('l_indexFinger02_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_indexFinger04_tempJt', position=(11, 16.7, 0.3))
    cmds.joint('l_indexFinger03_tempJt', edit=True, zso=True, oj='xyz', sao='yup')

    cmds.select('l_middleHand_tempJt')
    cmds.joint(name='l_middleFinger01_tempJt', position=(9.6, 16.7, 0))
    cmds.joint(name='l_middleFinger02_tempJt', position=(10.1, 16.7, 0))
    cmds.joint('l_middleFinger01_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_middleFinger03_tempJt', position=(10.6, 16.7, 0))
    cmds.joint('l_middleFinger02_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_middleFinger04_tempJt', position=(11, 16.7, 0))
    cmds.joint('l_middleFinger03_tempJt', edit=True, zso=True, oj='xyz', sao='yup')

    cmds.select('l_middleHand_tempJt')
    cmds.joint(name='l_ringFinger01_tempJt', position=(9.6, 16.7, -0.3))
    cmds.joint(name='l_ringFinger02_tempJt', position=(10.1, 16.7, -0.3))
    cmds.joint('l_ringFinger01_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_ringFinger03_tempJt', position=(10.6, 16.7, -0.3))
    cmds.joint('l_ringFinger02_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_ringFinger04_tempJt', position=(11, 16.7, -0.3))
    cmds.joint('l_ringFinger03_tempJt', edit=True, zso=True, oj='xyz', sao='yup')

    cmds.select('l_wrist_tempJt')
    cmds.joint(name='l_outerHand_tempJt', position=(8.3, 16.7, -0.4))
    cmds.joint(name='l_pinky01_tempJt', position=(9, 16.7, -0.8))
    cmds.joint('l_outerHand_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_pinky02_tempJt', position=(9.5, 16.7, -0.8))
    cmds.joint('l_pinky01_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_pinky03_tempJt', position=(10, 16.7, -0.8))
    cmds.joint('l_pinky02_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='l_pinky04_tempJt', position=(10.4, 16.7, -0.8))
    cmds.joint('l_pinky03_tempJt', edit=True, zso=True, oj='xyz', sao='yup')

    CreateFingerControllerForTemp(joints=['l_innerHand_tempJt', 'l_indexFinger01_tempJt', 'l_middleFinger01_tempJt',
                                          'l_ringFinger01_tempJt', 'l_outerHand_tempJt'])


def CreateFingerControllerForTemp(**kwargs):
    joints = kwargs.setdefault("joints")
    for jt in joints:
        cmds.select(jt, hierarchy=True)
        jointList = cmds.ls(selection=True)

        for joint in jointList[:-1]:
            pos = cmds.joint(joint, q=True, position=True)
            nameSplit = joint.rsplit('_', 1)
            name = nameSplit[0]
            cmds.select(joint)
            cmds.joint(name=name + 'Up_tempJt', position=(pos[0], pos[1] + 0.5, pos[2]))


def CreateArmJoints(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")

    if side == 'l':
        cmds.group(name='ikFk_armJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

    clavicleLPos = cmds.joint(side + '_collarbone_tempJt', q=True, position=True)
    shoulderPos = cmds.joint(side + '_shoulder_tempJt', q=True, position=True)
    elbowPos = cmds.joint(side + '_elbow_tempJt', q=True, position=True)
    wristPos = cmds.joint(side + '_wrist_tempJt', q=True, position=True)
    middleHandPos = cmds.joint(side + '_middleHand_tempJt', q=True, position=True)

    cmds.select(clear=True)

    claviculaBn = cmds.joint(name=side + '_clavicula_bn', position=(clavicleLPos[0], clavicleLPos[1], clavicleLPos[2]))
    humerusBn = cmds.joint(name=side + '_humerus_bn', position=(shoulderPos[0], shoulderPos[1], shoulderPos[2]))
    cmds.joint(claviculaBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='xyz')
    radiusBn = cmds.joint(name=side + '_radius_bn', position=(elbowPos[0], elbowPos[1], elbowPos[2]))
    cmds.joint(humerusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='yup', rotationOrder='xyz')

    manusJtTemp = cmds.joint(name=side + '_manusTemp_jt', position=(wristPos[0], wristPos[1], wristPos[2]))
    cmds.joint(radiusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='xyz')
    cmds.joint(name=side + '_endArmTemp_jt', position=(middleHandPos[0], middleHandPos[1], middleHandPos[2]))
    cmds.joint(manusJtTemp, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='yup', rotationOrder='xyz')
    spaceConstrain = cmds.aimConstraint('l_handUp_tempJt', manusJtTemp, maintainOffset=False, aimVector=[0, 1, 0],
                                        upVector=[-1, 0, 0], worldUpType="scene", skip=['y', 'z'])
    cmds.select(manusJtTemp)
    manusBn = cmds.joint(name=side + '_manus_bn', position=(wristPos[0], wristPos[1], wristPos[2]))
    cmds.parent(manusBn, radiusBn)
    cmds.joint(name=side + '_middleHand_bn', position=(middleHandPos[0], middleHandPos[1], middleHandPos[2]))
    cmds.delete(spaceConstrain, manusJtTemp)

    if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) is True:
        manusBnPos = cmds.joint(manusBn, query=True, relative=True, position=True)
        ulnaBn = cmds.insertJoint(radiusBn)
        cmds.joint(ulnaBn, edit=True, name=side + '_ulna_bn', component=True, relative=True,
                   position=(manusBnPos[0] / 2, 0, 0), rotationOrder='xyz')

    cmds.select(claviculaBn, hierarchy=True)
    armJointList = cmds.ls(selection=True)
    ikFkJoints = DuplicateJoints(side=side, jointList=armJointList)

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true':
        armJointList_r = cmds.mirrorJoint(armJointList[0], mirrorYZ=True, mirrorBehavior=True,
                                          searchReplace=('l_', 'r_'))
        armIkJtHi_r = cmds.mirrorJoint(ikFkJoints[0][0], mirrorYZ=True, mirrorBehavior=True, searchReplace=('l_', 'r_'))
        armFkJtHi_r = cmds.mirrorJoint(ikFkJoints[1][0], mirrorYZ=True, mirrorBehavior=True, searchReplace=('l_', 'r_'))

        fkCtrls_r = FkSetup(side='r', jointList=armFkJtHi_r, bodyPart='arm', scale=scale)
        ikCtrls_r = IkArmSetup(side='r', jointList=armIkJtHi_r, scale=scale)
        cmds.parent(armJointList_r[0], 'JOINTS')

        IfFkSwitch(bindSkeletonList=armJointList_r, ikSkeletonList=armIkJtHi_r, fkSkeletonList=armFkJtHi_r,
                   bodyPart='arm', scale=scale, side='r', ikControls=ikCtrls_r[2], fkControls=fkCtrls_r[0][1:])

    fkCtrls = FkSetup(side=side, jointList=ikFkJoints[1], bodyPart='arm', scale=scale)
    ikCtrls = IkArmSetup(side=side, jointList=ikFkJoints[0], scale=scale)
    cmds.parent(armJointList[0], 'JOINTS')

    IfFkSwitch(bindSkeletonList=armJointList, ikSkeletonList=ikFkJoints[0], fkSkeletonList=ikFkJoints[1],
               bodyPart='arm', scale=scale, side=side, ikControls=ikCtrls[2], fkControls=fkCtrls[0][1:])


def CreateLegJoints(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")

    if side == 'l':
        cmds.group(name='ikFk_legJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

    femurPos = cmds.joint(side + '_hip_tempJt', q=True, position=True)
    tibiaPos = cmds.joint(side + '_knee_tempJt', q=True, position=True)
    pedPos = cmds.joint(side + '_ankle_tempJt', q=True, position=True)
    toePos = cmds.joint(side + '_toe_tempJt', q=True, position=True)
    toeEndPos = cmds.joint(side + '_toeEnd_tempJt', q=True, position=True)

    cmds.select(clear=True)

    femurJtTemp = cmds.joint(name=side + '_femurTemp_jt', position=(femurPos[0], femurPos[1], femurPos[2]))
    cmds.aimConstraint(side + '_knee_tempJt', femurJtTemp, maintainOffset=False, aimVector=[1, 0, 0],
                       upVector=[0, 1, 0], worldUpType='object', worldUpObject=side + '_hipFront_tempJt')
    cmds.select(femurJtTemp)
    femusBn = cmds.joint(name=side + '_femur_bn', position=(femurPos[0], femurPos[1], femurPos[2]))
    cmds.parent(femusBn, world=True)
    cmds.delete(femurJtTemp)

    tibiaJtTemp = cmds.joint(name=side + '_tibiaTemp_jt', position=(tibiaPos[0], tibiaPos[1], tibiaPos[2]))
    cmds.aimConstraint(side + '_ankle_tempJt', tibiaJtTemp, maintainOffset=False, aimVector=[1, 0, 0],
                       upVector=[0, 1, 0], worldUpType='object', worldUpObject=side + '_kneeFront_tempJt')
    cmds.select(tibiaJtTemp)
    tibiaBn = cmds.joint(name=side + '_tibia_bn', position=(tibiaPos[0], tibiaPos[1], tibiaPos[2]))
    cmds.parent(tibiaBn, femusBn)
    cmds.delete(tibiaJtTemp)

    pedBn = cmds.joint(name=side + '_ped_bn', position=(pedPos[0], pedPos[1], pedPos[2]))
    toeBn = cmds.joint(name=side + '_toe_bn', position=(toePos[0], toePos[1], toePos[2]))
    cmds.joint(pedBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
               rotationOrder='xyz')
    endJt = cmds.joint(name=side + '_endLeg_jt', position=(toeEndPos[0], toeEndPos[1], toeEndPos[2]))
    cmds.joint(toeBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
               rotationOrder='xyz')
    cmds.joint(endJt, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
               rotationOrder='xyz')

    cmds.select(femusBn, hierarchy=True)
    legJointList = cmds.ls(selection=True)

    ikFkJoints = DuplicateJoints(side=side, jointList=legJointList)

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true':
        legJointList_r = cmds.mirrorJoint(legJointList[0], mirrorYZ=True, mirrorBehavior=True,
                                          searchReplace=('l_', 'r_'))
        legIkJtHi_r = cmds.mirrorJoint(ikFkJoints[0][0], mirrorYZ=True, mirrorBehavior=True,
                                       searchReplace=('l_', 'r_'))
        legFkJtHi_r = cmds.mirrorJoint(ikFkJoints[1][0], mirrorYZ=True, mirrorBehavior=True,
                                       searchReplace=('l_', 'r_'))

        fkCtrls_r = FkSetup(side='r', jointList=legFkJtHi_r, bodyPart='leg', scale=scale)
        ikCtrls_r = IkLegSetup(side='r', jointList=legIkJtHi_r, scale=scale)
        IfFkSwitch(bindSkeletonList=legJointList_r, ikSkeletonList=legIkJtHi_r, fkSkeletonList=legFkJtHi_r,
                   bodyPart='leg', scale=scale, side='r', ikControls=ikCtrls_r[2], fkControls=fkCtrls_r[0])

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            cmds.parent(legJointList_r[0], 'c_sacrum_bn')
            cmds.parentConstraint('c_ik_hip_ctrl', fkCtrls_r[2], maintainOffset=True)
        else:
            cmds.parent(legJointList_r[0], 'JOINTS')

    fkCtrls = FkSetup(side=side, jointList=ikFkJoints[1], bodyPart='leg', scale=scale)
    ikCtrls = IkLegSetup(side=side, jointList=ikFkJoints[0], scale=scale)
    IfFkSwitch(bindSkeletonList=legJointList, ikSkeletonList=ikFkJoints[0], fkSkeletonList=ikFkJoints[1],
               bodyPart='leg', scale=scale, side=side, ikControls=ikCtrls[2], fkControls=fkCtrls[0])

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
        cmds.parent(legJointList[0], 'c_sacrum_bn')
        cmds.parentConstraint('c_sacrum_bn', 'ikFk_legJt_doNotTouch', maintainOffset=True)
        cmds.parentConstraint('c_ik_hip_ctrl', fkCtrls[2], maintainOffset=True)
    else:
        cmds.parent(legJointList[0], 'JOINTS')


def CreateHeadJoints(**kwargs):
    scale = kwargs.setdefault("scale")
    side = kwargs.setdefault("side")
    neckBn = 'c_cervical_bn'
    neckPos = cmds.joint('c_neck_tempJt', q=True, p=True)
    headPos = cmds.joint('c_head_tempJt', q=True, p=True)
    headEndPos = cmds.joint('c_headTop_tempJt', q=True, p=True)

    cmds.select(clear=True)

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
        cmds.select(neckBn)
    else:
        neckBn = cmds.joint(name='c_neck_bn', position=(neckPos[0], neckPos[1], neckPos[2]))

    headBn = cmds.joint(name='c_head_bn', position=(headPos[0], headPos[1], headPos[2]))
    if headPos[2] > neckPos[2]:
        cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
                   rotationOrder='xyz')
    else:
        cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='ydown',
                   rotationOrder='xyz')
    endTop = cmds.joint(name='c_headTop_jt', position=(headEndPos[0], headEndPos[1], headEndPos[2]))
    if headEndPos[2] > headPos[2]:
        cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
                   rotationOrder='xyz')
    else:
        cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='ydown',
                   rotationOrder='xyz')

    cmds.delete(endTop)

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
        cmds.select(neckBn, hierarchy=True)
        jtList = cmds.ls(selection=True)
    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
        jtList = ['c_ik_cervical_jt', headBn]

    ctrlsGrp = FkSetup(side=side, jointList=jtList, bodyPart='head', scale=scale, parentJoints=False, useAllJoints=True)

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
        cmds.parent(jtList[0], 'JOINTS')
    elif cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
        cmds.parentConstraint('c_ik_shoulder_ctrl', ctrlsGrp[2], maintainOffset=True)


def CreateSpineJoints(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")
    numJt = kwargs.setdefault("numberOfJoints")

    cmds.group(name='ikFk_spineJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

    pelvisPos = cmds.joint('c_hip_tempJt', q=True, position=True)
    neckPos = cmds.joint('c_neck_tempJt', q=True, position=True)
    lowPelvisPos = cmds.joint('c_lowerHip_tempJt', q=True, position=True)
    rootPos = [lowPelvisPos[0] + ((pelvisPos[0] - lowPelvisPos[0]) / 2),
               lowPelvisPos[1] + ((pelvisPos[1] - lowPelvisPos[1]) / 2),
               lowPelvisPos[2] + ((pelvisPos[2] - lowPelvisPos[2]) / 2)]

    cmds.select(clear=True)

    rootJt = cmds.joint(name='c_root_bn', position=(rootPos[0], rootPos[1], rootPos[2]))
    lumbarBn = cmds.joint(name='c_lumbar_bn', position=(pelvisPos[0], pelvisPos[1], pelvisPos[2]))
    cmds.joint(rootJt, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='yzx')
    cervicalBn = cmds.joint(name='c_cervical_bn', position=(neckPos[0], neckPos[1], neckPos[2]))
    cmds.joint(lumbarBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='yzx')
    cmds.joint(cervicalBn, edit=True, zeroScaleOrient=True, orientJoint='none')

    cmds.select(rootJt, hierarchy=True)
    jtList = cmds.ls(selection=True)
    ikFkJoints = DuplicateJoints(side=side, jointList=jtList)

    jtHierarchy = InsertJoints(prefix='c', jointList=jtList, numberOfJoints=numJt)
    ikHierarchy = InsertJoints(prefix='c_ik', jointList=ikFkJoints[0], numberOfJoints=numJt)
    fkHierarchy = InsertJoints(prefix='c_fk', jointList=ikFkJoints[1], fk=True,
                               height=cmds.floatSliderGrp('reRig_heightWaistFK', q=True, value=True))

    fkCtrls = FkSetup(side=side, jointList=fkHierarchy, bodyPart='spine', scale=scale)
    ikCtrls = IkSpineSetup(side=side, jointList=ikHierarchy, scale=scale)

    cmds.select(jtHierarchy[0])
    sacrumBn = cmds.joint(name='c_sacrum_bn', p=(lowPelvisPos[0], lowPelvisPos[1], lowPelvisPos[2]))
    cmds.select(ikHierarchy[0])
    sacrumJt = cmds.joint(name='c_ik_sacrum_bn', p=(lowPelvisPos[0], lowPelvisPos[1], lowPelvisPos[2]))
    pelvisCtrl = CreatePelvisControl(joint=sacrumJt, locAttributes=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)

    cmds.parentConstraint(ikCtrls[0], fkHierarchy[0], maintainOffset=True)
    cmds.parentConstraint(fkHierarchy[0], jtHierarchy[0], maintainOffset=True)
    cmds.parentConstraint(ikCtrls[0], fkCtrls[1][0], maintainOffset=True)
    cmds.parentConstraint(fkHierarchy[-1], ikCtrls[3], maintainOffset=False)
    cmds.parentConstraint(ikCtrls[0], pelvisCtrl[1], maintainOffset=True)
    cmds.parent(pelvisCtrl[1], fkCtrls[2])

    jtHierarchy.append(sacrumBn)
    ikHierarchy.append(sacrumJt)

    cmds.parent(jtHierarchy[0], 'JOINTS')

    for n in range(len(jtHierarchy))[1:]:
        cmds.orientConstraint(ikHierarchy[n], jtHierarchy[n], skip="none", maintainOffset=False)


def CreateFingerJoints(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                            select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
        cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

    finishedList = []

    if cmds.objExists('l_innerHand_tempJt'):
        thumb = FingerSetup(joint=side + '_innerHand_tempJt', side=side, scale=scale, finger='thumb',
                            parentJoint=side + '_manus_bn')
        finishedList.append(thumb[1])

    if cmds.objExists(side + '_indexFinger01_tempJt'):
        index = FingerSetup(joint=side + '_indexFinger01_tempJt', side=side, scale=scale, finger='indexFinger',
                            parentJoint=side + '_middleHand_bn')
        finishedList.append(index[1])

    if cmds.objExists(side + '_middleFinger01_tempJt'):
        middle = FingerSetup(joint=side + '_middleFinger01_tempJt', side=side, scale=scale, finger='middleFinger',
                             parentJoint=side + '_middleHand_bn')
        finishedList.append(middle[1])

    if cmds.objExists(side + '_ringFinger01_tempJt'):
        ring = FingerSetup(joint=side + '_ringFinger01_tempJt', side=side, scale=scale, finger='ringFinger',
                           parentJoint=side + '_middleHand_bn')
        finishedList.append(ring[1])

    if cmds.objExists(side + '_outerHand_tempJt'):
        pinky = FingerSetup(joint=side + '_outerHand_tempJt', side=side, scale=scale, finger='pinky',
                            parentJoint=side + '_manus_bn')
        finishedList.append(pinky[1])

    grp = cmds.group(finishedList, name=side + '_fk_fingers_grp')
    cmds.parentConstraint(side + '_manus_bn', grp, maintainOffset=True)

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                            select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
        cmds.delete('r_collarbone_tempJt')


def ConnectArmToSpine():
    shoulderPos = cmds.joint('l_collarbone_tempJt', q=True, p=True)
    cmds.select('c_lumbar_bn', hierarchy=True)
    jointList = cmds.ls(selection=True)
    for joint in jointList[1:-1]:
        lenght = cmds.xform(joint, q=True, translation=True)[0]
        height = cmds.xform(joint, q=True, translation=True, worldSpace=True)[1]
        if height < shoulderPos[1] and height + lenght > shoulderPos[1]:
            cmds.parent('l_clavicula_bn', 'r_clavicula_bn', joint)
            cmds.parentConstraint(joint, 'ikFk_armJt_doNotTouch', maintainOffset=True)
    cmds.parentConstraint('c_ik_shoulder_ctrl', 'l_fk_arm_grp', maintainOffset=True)
    cmds.parentConstraint('c_ik_shoulder_ctrl', 'r_fk_arm_grp', maintainOffset=True)


def CreateMasterControl(**kwargs):
    scale = kwargs.setdefault("scale")
    masterCtrl = CreateTempSkeletonControl(scale=scale, name='master_ctrl')
    cmds.parent(masterCtrl, 'CONTROLS')
    parentList = ['LEFT', 'RIGHT', 'CENTER']
    scaleList = ['LEFT', 'RIGHT', 'CENTER', 'JOINTS']

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
        parentList.append('JOINTS')

    if cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
        scaleList.append('ikFk_armJt_doNotTouch')
        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
            parentList.append('ikFk_armJt_doNotTouch')

    if cmds.checkBox('reRig_autoRigLeg', q=True, value=True) is True:
        scaleList.append('ikFk_legJt_doNotTouch')
        scaleList.append('r_ik_foot_doNotTouch')
        scaleList.append('l_ik_foot_doNotTouch')
        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
            parentList.append('ikFk_legJt_doNotTouch')

    if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
        scaleList.append('ikFk_spineJt_doNotTouch')
    for obj in parentList:
        cmds.parentConstraint(masterCtrl, obj, mo=True)
    for obj in scaleList:
        cmds.scaleConstraint(masterCtrl, obj, mo=True)


def InsertJoints(**kwargs):
    prefix = kwargs.setdefault("prefix")
    jtList = kwargs.setdefault("jointList")
    numJt = kwargs.setdefault("numberOfJoints")
    fk = kwargs.setdefault("fk", False)
    height = kwargs.setdefault("height")

    cmds.select(jtList[1])
    endJt = cmds.joint(jtList[-1], query=True, relative=True, position=True)

    if fk is True:
        cmds.insertJoint(jtList[1])
        cmds.joint(edit=True, name=prefix + '_thoracic_bn', component=True, relative=True,
                   position=(endJt[0] * height, 0, 0))
    else:
        for jt in range(1, numJt)[::-1]:
            cmds.insertJoint(jtList[1])
            cmds.joint(edit=True, name=prefix + '_thoracic' + str(jt) + '_bn', component=True, relative=True,
                       position=(endJt[0] / numJt * jt, 0, 0))
    cmds.select(jtList[0], hierarchy=True)
    jointHierarchy = cmds.ls(selection=True)
    return jointHierarchy


def DuplicateJoints(**kwargs):
    side = kwargs.setdefault("side")
    jtList = kwargs.setdefault("jointList")

    for joints in jtList[1:]:
        cmds.setAttr(joints + ".translateY", 0.0)
        cmds.setAttr(joints + ".translateZ", 0.0)

    cmds.duplicate(jtList, returnRootsOnly=True)
    if side == 'l':
        mel.eval('searchReplaceNames "l_" "l_ik_" "hierarchy";')
    elif side == 'r':
        mel.eval('searchReplaceNames "r_" "r_ik_" "hierarchy";')
    elif side == 'c':
        mel.eval('searchReplaceNames "c_" "c_ik_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    mel.eval('searchReplaceNames "_bn" "_jt" "hierarchy";')
    cmds.select(hierarchy=True)
    ikJtHi = cmds.ls(selection=True)
    cmds.select(jtList)
    cmds.duplicate(jtList, returnRootsOnly=True)
    if side == 'l':
        mel.eval('searchReplaceNames "l_" "l_fk_" "hierarchy";')
    elif side == 'r':
        mel.eval('searchReplaceNames "r_" "r_fk_" "hierarchy";')
    elif side == 'c':
        mel.eval('searchReplaceNames "c_" "c_fk_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    mel.eval('searchReplaceNames "_bn" "_jt" "hierarchy";')
    cmds.select(hierarchy=True)
    fkJtHi = cmds.ls(selection=True)
    return ikJtHi, fkJtHi


def FkSetup(**kwargs):
    side = kwargs.setdefault("side")
    part = kwargs.setdefault("bodyPart")
    jtList = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")
    parentJoints = kwargs.setdefault("parentJoints", True)
    useAllJoints = kwargs.setdefault("useAllJoints", False)

    if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) == True and part == 'arm':
        ctrlList = CreateFkControles(jointList=jtList[0:3], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)
        manusCtrl = CreateFkControles(jointList=jtList[4:-1], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                      hideAttr=['v'], ulna=True, scale=scale, rotateOrder=1)[0]
        ctrlList.append(manusCtrl)
    elif part == 'spine':
        ctrlList = CreateFkControles(jointList=jtList[2:-1], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)
    elif useAllJoints is True:
        ctrlList = CreateFkControles(jointList=jtList[0:], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)
    else:
        ctrlList = CreateFkControles(jointList=jtList[0:-1], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)

    ctrlGrpList = ParentFKControls(controlList=ctrlList[::-1])
    fkBodyCtrlGrp = cmds.group(ctrlGrpList, name=side + "_fk_" + part + "_grp")

    if side == 'l':
        cmds.parent(fkBodyCtrlGrp, 'LEFT')
    if side == 'r':
        cmds.parent(fkBodyCtrlGrp, 'RIGHT')
    if side == 'c':
        cmds.parent(fkBodyCtrlGrp, 'CENTER')

    if parentJoints is True:
        cmds.parent(jtList[0], 'ikFk_' + part + 'Jt_doNotTouch')
    return ctrlList, ctrlGrpList, fkBodyCtrlGrp


def IkSpineSetup(**kwargs):
    jtList = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    cmds.group(name='c_ik_spine_doNotTouch', empty=True, parent='DO_NOT_TOUCH')
    cmds.select(jtList)
    cmds.duplicate(jtList, returnRootsOnly=True)
    mel.eval('searchReplaceNames "c_ik_" "c_ik_controlJoints_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    cmds.select(hierarchy=True)
    ctrlJtList = cmds.ls(selection=True)
    ctrlJts = ctrlJtList[1], ctrlJtList[-1]
    cmds.parent(ctrlJts, ctrlJtList[2], world=True)
    cmds.delete(ctrlJtList[0], ctrlJtList[2])

    spineIkHandle = cmds.ikHandle(name="c_spine_ikHandle", startJoint=jtList[0],
                                  endEffector=jtList[-1], solver="ikSplineSolver", parentCurve=False)

    cmds.select(spineIkHandle[2])
    cmds.rename('c_ik_spine_curve')
    ikCurve = cmds.ls(selection=True)

    cmds.skinCluster(ctrlJts, ikCurve, toSelectedBones=True)
    cmds.parent(ikCurve, spineIkHandle[0], 'c_ik_spine_doNotTouch')

    shoulderCtrl = CreateShoulderHipControl(scale=scale, bodyPart='shoulder', joint=ctrlJts[1],
                                            locAttributes=['sx', 'sy', 'sz', 'v'])
    hipCtrl = CreateShoulderHipControl(scale=scale, bodyPart='hip', joint=ctrlJts[0],
                                       locAttributes=['sx', 'sy', 'sz', 'v'])

    cmds.setAttr(spineIkHandle[0] + '.dTwistControlEnable', True)
    cmds.setAttr(spineIkHandle[0] + '.dWorldUpType', 4)
    cmds.setAttr(spineIkHandle[0] + '.dWorldUpAxis', 0)
    cmds.connectAttr(hipCtrl[2] + '.worldMatrix[0]', spineIkHandle[0] + '.dWorldUpMatrix')
    cmds.connectAttr(shoulderCtrl[2] + '.worldMatrix[0]', spineIkHandle[0] + '.dWorldUpMatrixEnd')

    ikSpineCtrlGrp = cmds.group(shoulderCtrl[0], hipCtrl[0], name="c_ik_spine_grp")
    cmds.parent(ikSpineCtrlGrp, 'CENTER')
    cmds.parent(shoulderCtrl[1], hipCtrl[1], 'DO_NOT_TOUCH')
    cmds.parent(jtList[0], 'ikFk_spineJt_doNotTouch')
    return hipCtrl[3], hipCtrl[0], shoulderCtrl[3], shoulderCtrl[0]


def IkLegSetup(**kwargs):
    side = kwargs.setdefault("side")
    jtList = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    legIkHandle = cmds.ikHandle(name=side + "_leg_ikHandle", startJoint=jtList[0],
                                endEffector=jtList[2], solver="ikRPsolver")
    ballIkHandle = cmds.ikHandle(name=side + "_ballFoot_ikHandle", startJoint=jtList[2],
                                 endEffector=jtList[3], solver="ikSCsolver")
    toeIkHandle = cmds.ikHandle(name=side + "_toeFoot_ikHandle", startJoint=jtList[3],
                                endEffector=jtList[4], solver="ikSCsolver")

    footCtrl = CreateFootControl(side=side, control='footIkControl', joint=jtList[2],
                                 ikHandle=[legIkHandle[0], ballIkHandle[0], toeIkHandle[0]], aimJoint=jtList[4],
                                 locAttributes=['sx', 'sy', 'sz', 'v'], scale=scale,
                                 addAttributes=['onHeel', 'onToe', 'onBall', 'toeFlip', 'outerBank', 'innerBank'])
    kneeCtrl = CreatePoleVectorControl(side=side, joint=jtList[1], bodyPart='knee', ikHandle=legIkHandle[0],
                                       locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'], scale=scale)

    ikFootCtrlGrp = cmds.group(kneeCtrl, footCtrl[0], name=side + "_ik_leg_grp")

    if side == 'l':
        cmds.parent(ikFootCtrlGrp, 'LEFT')
    if side == 'r':
        cmds.parent(ikFootCtrlGrp, 'RIGHT')

    cmds.parent(footCtrl[1], 'DO_NOT_TOUCH')
    cmds.parent(jtList[0], 'ikFk_legJt_doNotTouch')
    return footCtrl, kneeCtrl, ikFootCtrlGrp


def IkArmSetup(**kwargs):
    side = kwargs.setdefault("side")
    jtList = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    armIkHandle = cmds.ikHandle(name=side + "_arm_ikHandle", startJoint=jtList[1],
                                endEffector=jtList[3], solver="ikRPsolver")

    if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) is True:
        wristPos = cmds.joint(jtList[4], q=True, position=True)
        cmds.move(wristPos[0], wristPos[1], wristPos[2],
                  armIkHandle[1] + ".scalePivot", armIkHandle[1] + ".rotatePivot")
        armCtrl = CreateArmCtrl(side=side, control='handIkControl', joint=jtList[4], ikHandle=armIkHandle[0],
                                scale=scale,
                                ulnaJoint=jtList[3], locAttributes=['sx', 'sy', 'sz', 'v'], jointRotateOrder=1,
                                controlRotateOrder=1,
                                doNotTouchRotateOrder=1)
    else:
        armCtrl = CreateArmCtrl(side=side, control='handIkControl', joint=jtList[3], ikHandle=armIkHandle[0],
                                scale=scale,
                                locAttributes=['sx', 'sy', 'sz', 'v'], jointRotateOrder=1, controlRotateOrder=1,
                                doNotTouchRotateOrder=1)
    elbowCtrl = CreatePoleVectorControl(side=side, joint=jtList[2], bodyPart='elbow', ikHandle=armIkHandle[0],
                                        locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'], scale=scale)

    ikFootCtrlGrp = cmds.group(elbowCtrl, armCtrl[0], name=side + "_ik_arm_grp")
    if side == 'l':
        cmds.parent(ikFootCtrlGrp, 'LEFT')
    if side == 'r':
        cmds.parent(ikFootCtrlGrp, 'RIGHT')
    cmds.parent(armCtrl[1], 'DO_NOT_TOUCH')
    cmds.parent(jtList[0], 'ikFk_armJt_doNotTouch')
    return armCtrl, elbowCtrl, ikFootCtrlGrp


def IfFkSwitch(**kwargs):
    bnList = kwargs.setdefault("bindSkeletonList")
    ikList = kwargs.setdefault("ikSkeletonList")
    fkList = kwargs.setdefault("fkSkeletonList")
    part = kwargs.setdefault('bodyPart')
    scale = kwargs.setdefault('scale')
    side = kwargs.setdefault('side')
    fkCtrls = kwargs.setdefault('fkControls')
    ikCtrls = kwargs.setdefault('ikControls')

    ulna = cmds.checkBox('reRig_autoRigUlna', q=True, value=True)

    num = 0

    if part == 'leg':
        ctrl = CreateIkFkSwitchControl(joint=bnList[-3], bodyPart=part,
                                       locAttributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                       scale=scale, side=side)
    elif part == 'arm':
        ctrl = CreateIkFkSwitchControl(joint=bnList[-2], bodyPart=part,
                                       locAttributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                       scale=scale, side=side)

    ikFkSwitchBleCol = cmds.shadingNode('blendColors', asUtility=True, name=side + "_" + part + "IkFkSwitch_bleCol")
    cmds.setAttr(ikFkSwitchBleCol + ".color2G", 1)
    cmds.connectAttr(ctrl[1], ikFkSwitchBleCol + ".blender")

    if part == 'arm':
        cmds.orientConstraint(fkList[0], ikList[0], skip="none", maintainOffset=False)
        cmds.orientConstraint(fkList[0], bnList[0], skip="none", maintainOffset=False)
        num = 1

    for n in range(num, len(bnList)):
        if n == 3 and ulna is True and part == 'arm':
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip=['y', 'z'], maintainOffset=False)
        elif n == 4 and ulna is True and part == 'arm':
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip=['x'], maintainOffset=False)
        else:
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip="none", maintainOffset=False)
        constrainAttr = cmds.listAttr(parCon, r=True, st='*jt*')
        cmds.connectAttr(ikFkSwitchBleCol + ".outputG", parCon[0] + "." + constrainAttr[0])
        cmds.connectAttr(ikFkSwitchBleCol + ".outputR", parCon[0] + "." + constrainAttr[1])

    for ctrl in fkCtrls:
        cmds.connectAttr(ikFkSwitchBleCol + ".outputR", ctrl + ".visibility")
    cmds.connectAttr(ikFkSwitchBleCol + ".outputG", ikCtrls + ".visibility")


def FingerSetup(**kwargs):
    joint = kwargs.setdefault("joint")
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")
    finger = kwargs.setdefault("finger")
    parentJoint = kwargs.setdefault("parentJoint")

    cmds.select(joint, hierarchy=True)
    jtList = cmds.ls(selection=True)

    jointPosList = []
    newJointTempList = []
    mainSkeletionList = []
    deleteList = []

    mainSkeletionList.append(parentJoint)

    for jt in jtList:
        jointPos = cmds.joint(jt, q=True, position=True)
        jointPosList.append(jointPos)

    for n in range(len(jtList) - (len(jtList) / 2)):
        cmds.select(parentJoint)
        jt = cmds.joint(name=side + '_' + finger + str(n + 1) + 'Temp_jt',
                        position=(jointPosList[n][0], jointPosList[n][1], jointPosList[n][2]))
        newJointTempList.append([jt, jtList[-n - 1]])
        deleteList.append(jt)

        if n != 0:
            cmds.aimConstraint(jt, newJointTempList[n - 1][0], maintainOffset=False, aimVector=[1, 0, 0],
                               upVector=[0, 1, 0], worldUpType='object', worldUpObject=newJointTempList[n - 1][1])

            cmds.select(newJointTempList[n - 1][0])
            if finger == 'pinky' or finger == 'thumb':
                if finger == 'pinky' and n == 1:
                    bn = cmds.joint(name=side + '_outerHand_bn',
                                    position=(jointPosList[n - 1][0], jointPosList[n - 1][1], jointPosList[n - 1][2]))
                elif finger == 'thumb' and n == 1:
                    bn = cmds.joint(name=side + '_innerHand_bn',
                                    position=(jointPosList[n - 1][0], jointPosList[n - 1][1], jointPosList[n - 1][2]))
                else:
                    bn = cmds.joint(name=side + '_' + finger + str(n - 1) + '_bn',
                                    position=(jointPosList[n - 1][0], jointPosList[n - 1][1], jointPosList[n - 1][2]))
            else:
                bn = cmds.joint(name=side + '_' + finger + str(n) + '_bn',
                                position=(jointPosList[n - 1][0], jointPosList[n - 1][1], jointPosList[n - 1][2]))
            cmds.parent(bn, mainSkeletionList[n - 1])
            mainSkeletionList.append(bn)

    cmds.delete(deleteList)
    fk = FkSetup(side=side, jointList=mainSkeletionList[1:], bodyPart=finger, scale=scale, parentJoints=False,
                 useAllJoints=True)
    return mainSkeletionList[1:], fk[2]


def CreateTempSkeletonControl(**kwargs):
    scale = kwargs.setdefault('scale', 1)
    name = kwargs.setdefault('name')
    ctrl = cmds.circle(name=name, normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
    cmds.scale(5, 5, 5, ctrl)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    cmds.scale(scale, scale, scale, ctrl)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    return ctrl


def CreatePoleVectorControl(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault('bodyPart')
    ikHandle = kwargs.setdefault('ikHandle')
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    grp = cmds.group(empty=True, name=side + '_' + part + '_ctrlGrp')
    spaceConstrain = cmds.pointConstraint(joint, grp, maintainOffset=False, skip="none")[0]
    cmds.delete(spaceConstrain)

    ctrl = cmds.curve(name=side + "_ik_" + part + "_ctrl", degree=3,
                      point=[(0, 0, 0), (0, 0.25, 0), (-0.5, 0.25, 0), (-0.5, -0.5, 0),
                             (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.3, 0.5, 0)],
                      knot=[0, 0, 0, 1, 2, 3, 4, 4, 4])
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)
    cmds.poleVectorConstraint(ctrl, ikHandle)

    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp


def CreateArmCtrl(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    ulnaJt = kwargs.setdefault("ulnaJoint")
    ikHandle = kwargs.setdefault('ikHandle')
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    jtRO = kwargs.setdefault('jointRotateOrder', 0)
    ctrlRO = kwargs.setdefault('controlRotateOrder', 0)
    dntRO = kwargs.setdefault('doNotTouchRotateOrder', 0)

    ctrl = cmds.curve(name=side + "_ik_hand_ctrl", degree=1,
                      point=[(-0.14, 0.41, 0.65), (1.57, 0.41, 0.77), (1.57, -0.69, 0.77), (-0.14, -0.69, 0.65),
                             (-0.14, 0.41, 0.65),
                             (-0.14, 0.41, -0.78), (-0.14, -0.69, -0.78), (-0.14, -0.69, 0.65), (-0.14, -0.69, -0.78),
                             (1.51, -0.69, -0.91),
                             (1.57, -0.69, 0.77), (1.57, 0.41, 0.77), (1.51, 0.40, -0.91), (-0.14, 0.41, -0.78),
                             (1.51, 0.40, -0.91),
                             (1.51, -0.69, -0.91)],
                      knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    if side == 'r':
        cmds.scale(-1, 1, 1, ctrl)
        cmds.makeIdentity(ctrl, apply=True, scale=True)

    ikArmDoNotTouch = cmds.group(name=side + "_ik_hand_doNotTouch", empty=True)
    spaceLoc = cmds.spaceLocator(name=side + '_ik_hand_space')[0]
    cmds.parent(spaceLoc, ikArmDoNotTouch, relative=True)

    cmds.setAttr(ctrl + ".rotateOrder", ctrlRO)
    cmds.setAttr(joint + ".rotateOrder", jtRO)
    cmds.setAttr(spaceLoc + ".rotateOrder", dntRO)
    cmds.setAttr(ikArmDoNotTouch + ".rotateOrder", dntRO)

    grp = cmds.group(empty=True, name=side + "_ik_hand_ctrlGrp")
    spaceConstrain = cmds.parentConstraint(joint, grp, maintainOffset=False)
    cmds.delete(spaceConstrain)
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)

    cmds.parentConstraint(ctrl, ikArmDoNotTouch, maintainOffset=False)
    cmds.parent(ikHandle, ikArmDoNotTouch)

    if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) is True:
        cmds.orientConstraint(spaceLoc, ulnaJt, skip=['y', 'z'], maintainOffset=True)
        cmds.orientConstraint(spaceLoc, joint, skip='x', maintainOffset=False)
    else:
        cmds.orientConstraint(spaceLoc, joint, skip='none', maintainOffset=False)

    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp, ikArmDoNotTouch


def CreateFootControl(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    ikHandle = kwargs.setdefault('ikHandle')
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    aimJoint = kwargs.setdefault('aimJoint')
    addAttr = kwargs.setdefault('addAttributes')

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                            select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
        cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
        mel.eval('searchReplaceNames "1" "" "hierarchy";')

    anklePos = cmds.joint(joint, q=True, p=True, a=True)
    heelPos = cmds.joint(side + '_heelFoot_tempJt', q=True, p=True, a=True)

    scaleY = anklePos[1] - heelPos[1]

    ctrl = cmds.curve(name=side + "_ik_foot_ctrl", degree=1,
                      point=[(-0.9, -0.4, 2.4), (-0.9, -0.4, 2.4), (-0.9, -1.2, 2.6), (0.7, -1.2, 2.6),
                             (0.7, -0.4, 2.4),
                             (-0.9, -0.4, 2.4), (-1, 0.1, -1), (1, 0.1, -1), (0.7, -0.4, 2.4), (0.7, -1.2, 2.6),
                             (1, -1.2, -1.2),
                             (1, 0.1, -1), (1, -1.2, -1.2), (-1, -1.2, -1.2), (-1, 0.1, -1), (-1, -1.2, -1.2),
                             (-0.9, -1.2, 2.6)],
                      knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

    grp = cmds.group(empty=True, name=side + "_ik_foot_ctrlGrp")
    spaceConstrain = cmds.pointConstraint(joint, grp, maintainOffset=False, skip="none")
    cmds.delete(spaceConstrain)
    cmds.parent(ctrl, grp, r=True)

    cmds.scale(scale, scaleY / 1.2, scale, grp)
    cmds.makeIdentity(grp, apply=True, scale=True)
    spaceConstrain = cmds.aimConstraint(aimJoint, grp, aimVector=(0.0, 0.0, 1.0), skip=["x", "z"])
    cmds.delete(spaceConstrain)

    ikFootDoNotTouch = cmds.group(name=side + "_ik_foot_doNotTouch", empty=True)
    cmds.parentConstraint(ctrl, ikFootDoNotTouch, maintainOffset=False, skipTranslate="none", skipRotate="none")

    onHeel = cmds.group(name=side + "_ik_onHell_negRX", empty=True, parent=ikFootDoNotTouch)
    spaceConstrain = cmds.pointConstraint(side + '_heelFoot_tempJt', onHeel)
    cmds.delete(spaceConstrain)

    onToe = cmds.group(name=side + "_ik_onToe_posRX", empty=True, parent=onHeel)
    spaceConstrain = cmds.pointConstraint(side + '_toeEnd_tempJt', onToe)
    cmds.delete(spaceConstrain)

    if side == 'l':
        outerBank = cmds.group(name=side + "_ik_outerBank_negRZ", empty=True, parent=onToe)
    elif side == 'r':
        outerBank = cmds.group(name=side + "_ik_outerBank_posRZ", empty=True, parent=onToe)
    spaceConstrain = cmds.pointConstraint(side + '_footOuter_tempJt', outerBank)
    cmds.delete(spaceConstrain)

    if side == 'l':
        innerBank = cmds.group(name=side + "_ik_innerBank_posRZ", empty=True, parent=outerBank)
    elif side == 'r':
        innerBank = cmds.group(name=side + "_ik_innerBank_negRZ", empty=True, parent=outerBank)
    spaceConstrain = cmds.pointConstraint(side + '_footInner_tempJt', innerBank)
    cmds.delete(spaceConstrain)

    toeFlip = cmds.group(name=side + "_ik_toeFlip_negRX", empty=True, parent=innerBank)
    spaceConstrain = cmds.pointConstraint(side + '_toe_tempJt', toeFlip)
    cmds.delete(spaceConstrain)

    onBall = cmds.group(name=side + "_ik_onBall_posRX", empty=True, parent=innerBank)
    spaceConstrain = cmds.pointConstraint(side + '_toe_tempJt', onBall)
    cmds.delete(spaceConstrain)

    cmds.parent(ikHandle[0], onBall)
    cmds.parent(ikHandle[1], innerBank)
    cmds.parent(ikHandle[2], toeFlip)

    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)

    for attr in addAttr:
        cmds.addAttr(ctrl, longName=attr, attributeType='float', keyable=True)

    multiplyDivide = cmds.shadingNode('multiplyDivide', name=side + '_ik_foot_mulDiv', asUtility=True)
    cmds.setAttr(multiplyDivide + '.input2X', -1)
    cmds.setAttr(multiplyDivide + '.input2Y', -1)
    cmds.setAttr(multiplyDivide + '.input2Z', -1)

    if 'onToe' in addAttr:
        cmds.connectAttr(ctrl + '.onToe', onToe + '.rx')
    if 'onHeel' in addAttr:
        cmds.connectAttr(ctrl + '.onHeel', multiplyDivide + '.input1X')
        cmds.connectAttr(multiplyDivide + '.outputX', onHeel + '.rx')
    if side == 'l':
        if 'outerBank' in addAttr:
            cmds.connectAttr(ctrl + '.outerBank', multiplyDivide + '.input1Y')
            cmds.connectAttr(multiplyDivide + '.outputY', outerBank + '.rz')
        if 'innerBank' in addAttr:
            cmds.connectAttr(ctrl + '.innerBank', innerBank + '.rz')
    elif side == 'r':
        if 'outerBank' in addAttr:
            cmds.connectAttr(ctrl + '.outerBank', outerBank + '.rz')
        if 'innerBank' in addAttr:
            cmds.connectAttr(ctrl + '.innerBank', multiplyDivide + '.input1Y')
            cmds.connectAttr(multiplyDivide + '.outputY', innerBank + '.rz')
    if 'onBall' in addAttr:
        cmds.connectAttr(ctrl + '.onBall', onBall + '.rx')
    if 'toeFlip' in addAttr:
        cmds.connectAttr(ctrl + '.toeFlip', multiplyDivide + '.input1Z')
        cmds.connectAttr(multiplyDivide + '.outputZ', toeFlip + '.rx')

    if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                            select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
        cmds.delete('r_hip_tempJt')

    return grp, ikFootDoNotTouch


def CreateShoulderHipControl(**kwargs):
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault("bodyPart")
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    ro = kwargs.setdefault('rotationOrder', 'xyz')

    if part == "shoulder":
        ctrl = cmds.curve(name="c_ik_shoulder_ctrl", degree=1,
                          point=[(2.3, -0.3, 1.6), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3), (-2.3, -0.3, 1.6),
                                 (2.3, -0.3, 1.6),
                                 (2.5, -2.7, 1.9), (-2.5, -2.7, 1.9), (-2.5, -2.7, -1.9), (2.5, -2.7, -1.9),
                                 (2.5, -2.7, 1.9),
                                 (2.5, -2.7, -1.9), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3), (-2.5, -2.7, -1.9),
                                 (-2.5, -2.7, 1.9),
                                 (-2.3, -0.3, 1.6)],
                          knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    elif part == "hip":
        ctrl = cmds.curve(name="c_ik_hip_ctrl", degree=1,
                          point=[(-2.5, 0.6, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9), (-2.5, 0.6, -1.9),
                                 (-2.5, 0.6, 1.9),
                                 (-2.5, -2.1, 1.9), (2.5, -2.1, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9),
                                 (2.5, -2.1, -1.9),
                                 (2.5, -2.1, 1.9), (-2.5, -2.1, 1.9), (-2.5, -2.1, -1.9), (-2.5, 0.6, -1.9),
                                 (-2.5, -2.1, -1.9),
                                 (2.5, -2.1, -1.9)],
                          knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
    cmds.setAttr(ctrl + '.ry', 90)
    cmds.setAttr(ctrl + '.rx', 90)
    cmds.makeIdentity(ctrl, apply=True, rotate=True)

    grp = cmds.group(name="c_ik_" + part + "_ctrlGrp", empty=True)
    spaceConstrain = cmds.parentConstraint(joint, grp, maintainOffset=False)
    cmds.delete(spaceConstrain)
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)

    doNotTouch = cmds.group(name='c_ik_' + part + '_doNotTouch', empty=True)
    cmds.parentConstraint(ctrl, doNotTouch, maintainOffset=False)
    spaceLoc = cmds.spaceLocator(name='c_ik_' + part + '_space')
    cmds.parent(spaceLoc, doNotTouch, relative=True)
    cmds.setAttr(spaceLoc[0] + '.tz', -0.5 * scale)
    cmds.parent(joint, doNotTouch)
    cmds.xform(ctrl, rotateOrder=ro)

    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp, doNotTouch, spaceLoc[0], ctrl


def CreatePelvisControl(**kwargs):
    joint = kwargs.setdefault("joint")
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    ro = kwargs.setdefault('rotationOrder', 'xyz')
    grp = cmds.group(empty=True, name='c_pelvis_ctrlGrp')
    spaceConstrain = cmds.parentConstraint(joint, grp)
    cmds.delete(spaceConstrain)
    cmds.scale(scale, scale, scale, grp)

    ctrl = cmds.circle(name='c_pelvis_ctrl', normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
    cmds.parent(ctrl, grp, r=True)
    cmds.select(ctrl + '.cv[1]', ctrl + '.cv[3]', ctrl + '.cv[5]', ctrl + '.cv[7]')
    cmds.scale(-3, -3, -3)
    cmds.setAttr(ctrl + '.ty', -2)
    cmds.scale(0.7, 0.7, 0.7, ctrl)
    cmds.makeIdentity(ctrl, apply=True, scale=True, t=True)

    cmds.xform(ctrl, rotateOrder=ro)
    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)

    cmds.orientConstraint(ctrl, joint, skip='none', maintainOffset=False)

    return ctrl, grp


def CreateIkFkSwitchControl(**kwargs):
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault("bodyPart")
    locAttr = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    side = kwargs.setdefault('side')
    grp = cmds.group(name=side + "_" + part + "IkFkSwitch_ctrlGrp", empty=True)
    cmds.scale(scale, scale, scale, grp)
    if part == 'arm':
        spaceConstraint = cmds.parentConstraint(joint, grp)
    elif part == 'leg':
        spaceConstraint = cmds.pointConstraint(joint, grp)
    cmds.delete(spaceConstraint)

    ctrl = cmds.curve(name=side + "_" + part + "IkFkSwitch_ctrl", degree=3,
                      point=[(0, 0.65, 0), (0, 0, 0), (-1, 0, 0), (0, 0, 0),
                             (0, -1, 0), (0, 0, 0), (1, 0, 0), (0, 0, 0), (0, 0.65, 0)],
                      knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 6, 6])
    cmds.parent(ctrl, grp, r=True)

    if side == 'l' and part == 'arm':
        cmds.xform(ctrl, translation=[0, 1.5, 0], relative=True)
    elif side == 'r' and part == 'arm':
        cmds.xform(ctrl, translation=[0, -1.5, 0], relative=True)
    elif side == 'l' and part == 'leg':
        cmds.xform(ctrl, translation=[1.5, 0, 0], relative=True)
    elif side == 'r' and part == 'leg':
        cmds.xform(ctrl, translation=[-1.5, 0, 0], relative=True)

    cmds.parentConstraint(joint, grp, maintainOffset=True, skipRotate="none", skipTranslate="none")
    cmds.addAttr(ctrl, longName='ikFkSwitch', attributeType='float', minValue=0.0, maxValue=1.0, keyable=True)
    for attr in locAttr:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    if side == 'l':
        cmds.parent(grp, 'LEFT')
    elif side == 'r':
        cmds.parent(grp, 'RIGHT')
    return ctrl, ctrl + '.ikFkSwitch'


def CleanListToString(**kwargs):
    orginalList = kwargs.setdefault("dirtyList")
    cleanString = ''
    for obj in orginalList:
        if obj == orginalList[0]:
            cleanString = obj
        elif len(orginalList) > 1 and obj == orginalList[-1]:
            cleanString = cleanString + ' and ' + obj
        else:
            cleanString = cleanString + ', ' + obj

    return cleanString

