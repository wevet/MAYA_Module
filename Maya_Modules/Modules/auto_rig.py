# -*- coding: utf-8 -*-

import sys
import maya.api.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel
from functools import partial

kWindowName = 'CustomRig_Window'
kWindowHelpName = 'ReHelp_window'
kFKControlName = 'CreateFKControls'
kBiPedAutoRig = 'biPedAutoRig'
kScaleFkControles = 'scaleFkControles'

"""
using
import auto_rig
import importlib
importlib.reload(auto_rig)
auto_rig.create_main_window()
"""


def create_main_window():
    if cmds.window(kWindowName, exists=True):
        cmds.deleteUI(kWindowName)

    cmds.window(kWindowName, title="Rigging Tool", menuBar=False, widthHeight=(500, 300))
    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
    child1 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(create_help_window, kFKControlName), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.text(label='Lock following attributes:', font="plainLabelFont", align="left")
    cmds.paneLayout()
    cmds.textScrollList('Rig_FKControlLockAttribute', numberOfRows=8, allowMultiSelection=True,
                        append=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                        selectItem=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'], showIndexedItem=4)
    cmds.setParent('..')
    cmds.text(label='Type of constraint:', font="plainLabelFont", align="left")
    cmds.radioCollection('Rig_FKConstraintType')
    cmds.rowColumnLayout(numberOfColumns=3)
    cmds.radioButton('Rig_FKConstraintType_point', label='Point')
    cmds.radioButton('Rig_FKConstraintType_orient', label='Orient')
    cmds.radioButton('Rig_FKConstraintType_parent', label='Parent')
    cmds.radioCollection('Rig_FKConstraintType', edit=True, select='Rig_FKConstraintType_orient')
    cmds.setParent('..')
    cmds.button(label="Create FK Controls", command=create_fk_control_button)
    cmds.text(label='')
    cmds.button(label="Parent FK Controls", command=parent_fk_control_button)
    cmds.setParent('..')

    child4 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(create_help_window, kScaleFkControles), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.button(label="List All FK Control", command=list_fk_control_button)
    cmds.textFieldGrp('Rig_FKControlSelect', changeCommand=create_scale_fk_select_button)
    cmds.paneLayout()
    cmds.textScrollList('Rig_FKControlList', numberOfRows=8, allowMultiSelection=True,
                        append=[], showIndexedItem=4)
    cmds.setParent('..')
    cmds.floatSliderGrp('Rig_FKControlScale', field=True, label='Scale Fk Control ',
                        minValue=0.01, maxValue=5, fieldMinValue=0.01, fieldMaxValue=20, value=1, precision=2,
                        dragCommand=change_scale_fk_button, changeCommand=change_scale_fk_button)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Freeze transformations", command=freeze_transformation_button)
    cmds.text(label='Freeze transformations on selected controls.', font="plainLabelFont", align="left")
    cmds.setParent('..')
    cmds.setParent('..')

    child2 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.radioCollection('Rig_AddToJoints')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.radioButton('Rig_AddToJoints_selected', label='Selected joints')
    cmds.radioButton('Rig_AddToJoints_hierarchy', label='Joint hierarchy')
    cmds.radioCollection('Rig_AddToJoints', edit=True, select='Rig_AddToJoints_hierarchy')
    cmds.setParent('..')
    cmds.button(label="Add '_bn' To All Joints", command=rename_joint_button)
    cmds.text(label='')
    cmds.button(label="Create Main Groups", command=create_main_group_button)
    cmds.text(label='')
    cmds.button(label="Change displayed joint size", command=display_joint_size_button)
    cmds.setParent('..')

    child3 = cmds.rowColumnLayout(numberOfColumns=1)
    cmds.rowColumnLayout(numberOfColumns=1)
    cmds.button(label="Help", command=partial(create_help_window, kBiPedAutoRig), width=80)
    cmds.setParent('..')
    cmds.text(label='')
    cmds.radioCollection('Rig_MirrorTempSkeleton')
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.radioButton('Rig_MirrorTempSkeleton_true', label='Mirror joint position on both sides')
    cmds.radioButton('Rig_MirrorTempSkeleton_false', label='Unique positions')
    cmds.radioCollection('Rig_MirrorTempSkeleton', edit=True, select='Rig_MirrorTempSkeleton_true')
    cmds.setParent('..')
    cmds.button(label="Position Your Joints", command=create_temp_skeleton_button)
    cmds.text(label='')
    cmds.text(label='Choose which elements you want to incorporate:', font="plainLabelFont", align="left")
    cmds.rowColumnLayout(numberOfColumns=2)
    cmds.checkBox('Rig_AutoRigArm', label='Create Arms')
    cmds.checkBox('Rig_AutoRigUlna', label='Extra bone in forearm')
    cmds.checkBox('Rig_AutoRigLeg', label='Create Legs')
    cmds.checkBox('Rig_AutoRigFingers', label='Create Fingers')
    cmds.checkBox('Rig_AutoRigSpine', label='Create Spine')
    cmds.checkBox('Rig_AutoRigHead', label='Create Head')
    cmds.checkBox('Rig_AutoMasterCtrl', label='Master Control')
    cmds.setParent('..')
    cmds.intSliderGrp('Rig_numberOfJt', field=True, label='Number of bones in spine ',
                      minValue=2, maxValue=10, fieldMinValue=2, fieldMaxValue=20, value=4)
    cmds.floatSliderGrp('Rig_heightWaistFK', field=True, label='Height for the FK Control ',
                        minValue=0, maxValue=1, fieldMinValue=0, fieldMaxValue=21, value=0.28, precision=2)
    cmds.button(label="Create Your Rig", command=create_biped_rig_button)
    cmds.setParent('..')

    cmds.tabLayout(tabs, edit=True, tabLabel=(
        (child1, 'Create Fk Control'),
        (child4, 'Scale Fk Control'),
        (child2, 'Organize'),
        (child3, 'Biped Auto Rig')))
    cmds.showWindow()


def create_help_window(text, *args):
    if cmds.window(kWindowHelpName, exists=True):
        cmds.deleteUI(kWindowHelpName)

    cmds.window(kWindowHelpName, title="Help", menuBar=False)
    cmds.rowColumnLayout(numberOfColumns=1)

    if text == kFKControlName:
        cmds.text(label='Create Easy FK Controls', font="boldLabelFont", align="left")
        cmds.text(label='Select all the joints you want to create a FK control for.',
                  font="plainLabelFont",
                  align="left")
        cmds.text(label='Make sure you have named your joints properly.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Your joints should be named: nameOnJoint_bn',
                  font="plainLabelFont", align="left")
        cmds.text(label='Select the attributes you want to look on your control.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Select which type of constraint you want to create: point, parent or orient.',
                  font="plainLabelFont", align="left")
        cmds.text(label="")
        cmds.text(label='Parent FK Controls', font="boldLabelFont", align="left")
        cmds.text(label='Select the child fk control first then the parent control.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Example: hand_ctrl -> elbow_ctrl -> shoulder_ctrl.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Works with all controls created by the Reanimted Rigging Tool.',
                  font="plainLabelFont", align="left")

    if text == kBiPedAutoRig:
        cmds.text(label='Welcome To The Auto Rigging Script!', font="boldLabelFont", align="left")
        cmds.text(label='You can choose to create a full bi-ped rig or just some part of it.',
                  font="plainLabelFont",
                  align="left")
        cmds.text(label='To start you need to position out where you want your skeleton to go.',
                  font="plainLabelFont", align="left")
        cmds.text(label='Make sure your character are standing on the grid and facing front view. ',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Start by creating your temporary skeleton. Do this by clicking on "Position Your Joints".',
                  font="plainLabelFont", align="left")
        cmds.text(label='This skeleton you can scale, translate and rotate how ever you want to.',
                  font="plainLabelFont", align="left")
        cmds.text(label='It will not effect your final rig.',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Mirror joint position on both sides',
                  font="boldLabelFont", align="left")
        cmds.text(label='Use this option if your character is mirrored and has symmetric geometry. This is standard.',
                  font="plainLabelFont", align="left")
        cmds.text(label='')
        cmds.text(label='Unique positions', font="boldLabelFont", align="left")
        cmds.text(label='Use this option if your character has asymmetric geometry.',
                  font="plainLabelFont", align="left")
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

    if text == kScaleFkControles:
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


def create_fk_control_button(self):
    attr = cmds.textScrollList('Rig_FKControlLockAttribute', q=True, selectItem=True)
    radio_button = cmds.radioCollection('Rig_FKConstraintType', q=True, select=True)
    const = radio_button.rsplit('_', 1)[1]
    create_fk_control(jointList=cmds.ls(sl=True), lockAttributes=attr, constraint=const)


def parent_fk_control_button(self):
    parent_fk_control(controlList=cmds.ls(sl=True))


def rename_joint_button(self):
    if cmds.radioCollection('Rig_AddToJoints', q=True, select=True) == 'Rig_AddToJoints_hierarchy':
        cmds.select(hi=True)
        joint_list = cmds.ls(sl=True)
    else:
        joint_list = cmds.ls(sl=True)
    rename_joints(jointList=joint_list, add='_bn')


def create_main_group_button(self):
    create_main_group()


def create_temp_skeleton_button(self):
    if cmds.objExists('scale_tempSkeleton_ctrl'):
        cmds.delete('scale_tempSkeleton_ctrl')
        OpenMaya.MGlobal.displayInfo("Deleted you existing temporary skeleton and created a new one.")
    else:
        OpenMaya.MGlobal.displayInfo("Created a temporary skeleton.")

    create_temp_skeleton_spine()
    create_temp_skeleton_leg()
    cmds.select('c_neck_tempJt')
    create_temp_skeleton_arm()
    cmds.select('l_wrist_tempJt')
    create_temp_skeleton_finger()

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True, select=True) == 'Rig_MirrorTempSkeleton_false':
        cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
        cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

    temp_skeleton_control = create_temp_skeleton_control(name='scale_tempSkeleton_ctrl')
    cmds.parent('c_hip_tempJt', temp_skeleton_control)
    cmds.select(temp_skeleton_control)


def list_fk_control_button(self):
    fk_raw_list = cmds.ls('*.fkControl')
    clean_list = []
    for item in fk_raw_list:
        ctrl = item.split('.')
        clean_list.append(ctrl[0])
    cmds.textScrollList('Rig_FKControlList', edit=True, append=clean_list)


def change_scale_fk_button(self):
    fk_list = cmds.textScrollList('Rig_FKControlList', q=True, selectItem=True)
    scale = cmds.floatSliderGrp('Rig_FKControlScale', q=True, value=True)

    attr = ['sx', 'sy', 'sz']

    if fk_list is None:
        OpenMaya.MGlobal.displayWarning("Please select the controls you want to change size.")
    else:
        for item in fk_list:
            for a in attr:
                cmds.setAttr(item + '.' + a, lock=False)
            cmds.setAttr(item + '.sy', scale)
            cmds.setAttr(item + '.sz', scale)


def create_scale_fk_select_button(self):
    text = cmds.textFieldGrp('Rig_FKControlSelect', q=True, text=True)
    fk_list = cmds.textScrollList('Rig_FKControlList', q=True, allItems=True)
    keywords = text.split(' ')
    select_list = []
    cmds.textScrollList('Rig_FKControlList', e=True, deselectAll=True)
    if fk_list is None:
        OpenMaya.MGlobal.displayWarning("Your list with FK controls is empty! ):")
    else:
        for item in fk_list:
            for key in keywords:
                if key in item:
                    select_list.append(item)

    cmds.textScrollList('Rig_FKControlList', e=True, selectItem=select_list)


def freeze_transformation_button(self):
    fk_list = cmds.textScrollList('Rig_FKControlList', q=True, selectItem=True)
    attr = ['sx', 'sy', 'sz']
    if fk_list is None:
        OpenMaya.MGlobal.displayWarning("Please select the FK controls you want to freeze.")
    else:
        for item in fk_list:
            if cmds.getAttr(item + '.sx', lock=True) is False:
                cmds.makeIdentity(item, apply=True, scale=True)
                for a in attr:
                    cmds.setAttr(item + '.' + a, lock=True)


def create_biped_rig_button(self):
    if not cmds.objExists('scale_tempSkeleton_ctrl'):
        OpenMaya.MGlobal.displayWarning("You need to position your joints before you create your rig.")

    else:
        scale = cmds.getAttr('scale_tempSkeleton_ctrl.scaleX')
        result_list = []

        if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
            create_main_group()
            create_spine_joint(scale=scale, side='c',
                               numberOfJoints=cmds.intSliderGrp('Rig_numberOfJt', q=True, value=True))
            result_list.append('SPINE')

        if cmds.checkBox('Rig_AutoRigArm', q=True, value=True) is True:
            create_main_group()
            create_arm_joint(side='l', scale=scale)
            if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True,
                                    select=True) == 'Rig_MirrorTempSkeleton_false':
                create_arm_joint(side='r', scale=scale)
            result_list.append('ARMS')

        if cmds.checkBox('Rig_AutoRigLeg', q=True, value=True) is True:
            create_main_group()
            create_leg_joint(side='l', scale=scale)
            if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True,
                                    select=True) == 'Rig_MirrorTempSkeleton_false':
                create_leg_joint(side='r', scale=scale)
            result_list.append('LEGS')

        if cmds.checkBox('Rig_AutoRigHead', q=True, value=True) is True:
            create_main_group()
            create_head_joint(scale=scale, side='c')
            result_list.append('HEAD')

        if cmds.checkBox('Rig_AutoRigFingers', q=True, value=True) is True and cmds.checkBox('Rig_AutoRigArm',
                                                                                             q=True,
                                                                                             value=True) is True:
            create_main_group()
            create_finger_joint(scale=scale, side='l')
            create_finger_joint(scale=scale, side='r')
            result_list.append('FINGERS')

        if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True and cmds.checkBox('Rig_AutoRigArm',
                                                                                           q=True,
                                                                                           value=True) is True:
            connect_arm_to_spine()

        if cmds.checkBox('Rig_AutoMasterCtrl', q=True, value=True) is True:
            create_master_control(scale=scale)
            result_list.append('MASTER CONTROL')

        clean_string = clean_list_to_string(dirtyList=result_list)

        if cmds.checkBox('Rig_AutoRigFingers', q=True, value=True) is True and cmds.checkBox('Rig_AutoRigArm',
                                                                                             q=True,
                                                                                             value=True) is False:
            OpenMaya.MGlobal.displayWarning("You can not create fingers without an arm! : " + clean_string + '.')
        else:
            OpenMaya.MGlobal.displayInfo("Successfully created: " + clean_string + '.')


def display_joint_size_button(self):
    mel.eval('jdsWin;')


def create_fk_control(**kwargs):
    selection = kwargs.setdefault("jointList")
    lock_attribute = kwargs.setdefault("lockAttributes", ['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'])
    ulna = kwargs.setdefault("ulna", False)
    scale = kwargs.setdefault("scale", 1)
    rotate_order = kwargs.setdefault("rotateOrder", 0)
    fk_attribute = kwargs.setdefault('addFkAttribute', True)
    constraint = kwargs.setdefault('constraint', 'orient')

    if selection is []:
        OpenMaya.MGlobal.displayWarning("You have to at least select 1 joint.")

    control_list = []

    for obj in selection:
        name_split = obj.rsplit('_', 1)
        if len(name_split) >= 2:
            cmds.setAttr(obj + ".rotateOrder", rotate_order)
            name = name_split[0]
            grp = cmds.group(empty=True, name=name + '_ctrlGrp')
            cmds.parent(grp, obj, r=True)
            cmds.parent(grp, w=True)
            control = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), name=name + '_ctrl', radius=1)
            cmds.setAttr(control[0] + ".rotateOrder", rotate_order)
            cmds.parent(control[0], grp, r=True)
            cmds.scale(scale, scale, scale, grp)
            if ulna is True:
                ulnaJt = cmds.listRelatives(obj, parent=True)
                cmds.orientConstraint(control[0], obj, mo=False, skip='x')
                cmds.orientConstraint(control[0], ulnaJt, mo=True, skip=['y', 'z'])
            elif constraint == 'point':
                cmds.pointConstraint(control[0], obj, mo=False)
            elif constraint == 'parent':
                cmds.parentConstraint(control[0], obj, mo=False)
            elif constraint == 'orient':
                cmds.orientConstraint(control[0], obj, mo=False)

            if fk_attribute is True:
                cmds.addAttr(control[0], longName='fkControl', attributeType='float', keyable=True)
                lock_attribute.append('fkControl')
            control_list.append(control[0])
            for loc in lock_attribute:
                cmds.setAttr(control[0] + '.' + loc, lock=True, keyable=False, channelBox=False)
            cmds.setAttr(control[0] + '.v', lock=False)
        else:
            OpenMaya.MGlobal.displayWarning("Your joints are not named correctly: jointName_bn")

    return control_list


def parent_fk_control(**kwargs):
    control_list = kwargs.setdefault("controlList")
    control_group_list = []
    control_parent_list = []

    for ctrl in control_list:
        name_split = ctrl.rsplit('_', 1)
        if 'ctrl' == name_split[-1]:
            index = control_list.index(ctrl)
            control_group = cmds.listRelatives(ctrl, parent=True)[0]
            control_group_list.append(control_group)
            if ctrl != control_list[-1]:
                parent_control = control_list[index + 1]
                cmds.parentConstraint(parent_control, control_group, maintainOffset=True)
                control_parent_list.append(ctrl)
        else:
            OpenMaya.MGlobal.displayWarning(ctrl + " not a control object. it's named correctly: control_object")

    if control_parent_list is not []:
        clean_string = clean_list_to_string(dirtyList=control_parent_list)
        OpenMaya.MGlobal.displayInfo("Managed to successfully parent " + clean_string + ".")

    return control_group_list


def rename_joints(**kwargs):
    joint_list = kwargs.setdefault("jointList")
    add = kwargs.setdefault("add")
    new_joint_list = []

    for joint in joint_list:
        try:
            cmds.joint(joint, edit=True, name=joint + add)
            new_joint_list.append(joint + add)
        except ArithmeticError as e:
            OpenMaya.MGlobal.displayWarning(joint + " not a joint.")
    return new_joint_list


def create_main_group():
    group_list = []

    if not cmds.objExists('SKIN'):
        cmds.group(empty=True, name='SKIN')
        group_list.append('SKIN')

    if not cmds.objExists('JOINTS'):
        cmds.group(empty=True, name='JOINTS')
        group_list.append('JOINTS')

    if not cmds.objExists('CONTROLS'):
        cmds.group(empty=True, name='CONTROLS')
        group_list.append('CONTROLS')

    if not cmds.objExists('DO_NOT_TOUCH'):
        cmds.group(empty=True, name='DO_NOT_TOUCH')
        group_list.append('DO_NOT_TOUCH')

    if not cmds.objExists('LEFT'):
        cmds.group(empty=True, name='LEFT')
        cmds.parent('LEFT', 'CONTROLS')
        cmds.setAttr("LEFT.overrideEnabled", True)
        cmds.setAttr("LEFT.overrideColor", 6)
        group_list.append('LEFT')

    if not cmds.objExists('RIGHT'):
        cmds.group(empty=True, name='RIGHT')
        cmds.parent('RIGHT', 'CONTROLS')
        group_list.append('RIGHT')
        cmds.setAttr("RIGHT.overrideEnabled", True)
        cmds.setAttr("RIGHT.overrideColor", 13)

    if not cmds.objExists('CENTER'):
        cmds.group(empty=True, name='CENTER')
        cmds.parent('CENTER', 'CONTROLS')
        cmds.setAttr("CENTER.overrideEnabled", True)
        cmds.setAttr("CENTER.overrideColor", 17)
        group_list.append('CENTER')
    return group_list


def create_temp_skeleton_spine():
    cmds.joint(name='c_hip_tempJt', position=(0, 11.7, 0))
    cmds.joint(name='c_neck_tempJt', position=(0, 18, 0))
    cmds.joint('c_hip_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='c_head_tempJt', position=(0, 18.6, 0.6))
    cmds.joint('c_neck_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.joint(name='c_headTop_tempJt', position=(0, 20.7, 0.6))
    cmds.joint('c_head_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
    cmds.select('c_hip_tempJt')
    cmds.joint(name='c_lowerHip_tempJt', position=(0, 11.2, 0))


def create_temp_skeleton_leg():
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


def create_temp_skeleton_arm():
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


def create_temp_skeleton_finger():
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

    create_finger_control_for_temp(joints=['l_innerHand_tempJt',
                                           'l_indexFinger01_tempJt',
                                           'l_middleFinger01_tempJt',
                                          'l_ringFinger01_tempJt',
                                           'l_outerHand_tempJt'])


def create_finger_control_for_temp(**kwargs):
    joints = kwargs.setdefault("joints")
    for jt in joints:
        cmds.select(jt, hierarchy=True)
        joint_list = cmds.ls(selection=True)

        for joint in joint_list[:-1]:
            pos = cmds.joint(joint, q=True, position=True)
            name_split = joint.rsplit('_', 1)
            name = name_split[0]
            cmds.select(joint)
            cmds.joint(name=name + 'Up_tempJt', position=(pos[0], pos[1] + 0.5, pos[2]))


def create_arm_joint(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")

    if side == 'l':
        cmds.group(name='ikFk_armJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

    clavicle_l_pos = cmds.joint(side + '_collarbone_tempJt', q=True, position=True)
    shoulder_pos = cmds.joint(side + '_shoulder_tempJt', q=True, position=True)
    elbow_pos = cmds.joint(side + '_elbow_tempJt', q=True, position=True)
    wrist_pos = cmds.joint(side + '_wrist_tempJt', q=True, position=True)
    middle_hand_pos = cmds.joint(side + '_middleHand_tempJt', q=True, position=True)

    cmds.select(clear=True)

    claviculaBn = cmds.joint(name=side + '_clavicula_bn', position=(clavicle_l_pos[0], clavicle_l_pos[1], clavicle_l_pos[2]))
    humerusBn = cmds.joint(name=side + '_humerus_bn', position=(shoulder_pos[0], shoulder_pos[1], shoulder_pos[2]))
    cmds.joint(claviculaBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='xyz')
    radiusBn = cmds.joint(name=side + '_radius_bn', position=(elbow_pos[0], elbow_pos[1], elbow_pos[2]))
    cmds.joint(humerusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='yup', rotationOrder='xyz')

    manusJtTemp = cmds.joint(name=side + '_manusTemp_jt', position=(wrist_pos[0], wrist_pos[1], wrist_pos[2]))
    cmds.joint(radiusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='xyz')
    cmds.joint(name=side + '_endArmTemp_jt', position=(middle_hand_pos[0], middle_hand_pos[1], middle_hand_pos[2]))
    cmds.joint(manusJtTemp, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='yup', rotationOrder='xyz')

    space_constraint = cmds.aimConstraint('l_handUp_tempJt', manusJtTemp,
                                          maintainOffset=False,
                                          aimVector=[0, 1, 0],
                                          upVector=[-1, 0, 0], worldUpType="scene", skip=['y', 'z'])
    cmds.select(manusJtTemp)
    manusBn = cmds.joint(name=side + '_manus_bn', position=(wrist_pos[0], wrist_pos[1], wrist_pos[2]))
    cmds.parent(manusBn, radiusBn)
    cmds.joint(name=side + '_middleHand_bn', position=(middle_hand_pos[0], middle_hand_pos[1], middle_hand_pos[2]))
    cmds.delete(space_constraint, manusJtTemp)

    if cmds.checkBox('Rig_AutoRigUlna', q=True, value=True) is True:
        manusBnPos = cmds.joint(manusBn, query=True, relative=True, position=True)
        ulnaBn = cmds.insertJoint(radiusBn)
        cmds.joint(ulnaBn, edit=True, name=side + '_ulna_bn', component=True, relative=True,
                   position=(manusBnPos[0] / 2, 0, 0), rotationOrder='xyz')

    cmds.select(claviculaBn, hierarchy=True)
    arm_joint_list = cmds.ls(selection=True)
    ik_fk_joints = duplicate_joint(side=side, jointList=arm_joint_list)

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True, select=True) == 'Rig_MirrorTempSkeleton_true':
        arm_joint_list_r = cmds.mirrorJoint(arm_joint_list[0], mirrorYZ=True, mirrorBehavior=True,
                                          searchReplace=('l_', 'r_'))
        armIkJtHi_r = cmds.mirrorJoint(ik_fk_joints[0][0], mirrorYZ=True,
                                       mirrorBehavior=True, searchReplace=('l_', 'r_'))
        armFkJtHi_r = cmds.mirrorJoint(ik_fk_joints[1][0], mirrorYZ=True,
                                       mirrorBehavior=True, searchReplace=('l_', 'r_'))

        fk_control_r = fk_setup(side='r', jointList=armFkJtHi_r, bodyPart='arm', scale=scale)
        ik_control_r = ik_arm_setup(side='r', jointList=armIkJtHi_r, scale=scale)
        cmds.parent(arm_joint_list_r[0], 'JOINTS')

        if_fk_switch(bindSkeletonList=arm_joint_list_r,
                     ikSkeletonList=armIkJtHi_r,
                     fkSkeletonList=armFkJtHi_r,
                     bodyPart='arm', scale=scale, side='r',
                     ikControls=ik_control_r[2],
                     fkControls=fk_control_r[0][1:])

    fk_control = fk_setup(side=side, jointList=ik_fk_joints[1], bodyPart='arm', scale=scale)
    ik_control = ik_arm_setup(side=side, jointList=ik_fk_joints[0], scale=scale)
    cmds.parent(arm_joint_list[0], 'JOINTS')

    if_fk_switch(bindSkeletonList=arm_joint_list,
                 ikSkeletonList=ik_fk_joints[0],
                 fkSkeletonList=ik_fk_joints[1],
                 bodyPart='arm', scale=scale, side=side,
                 ikControls=ik_control[2],
                 fkControls=fk_control[0][1:])


def create_leg_joint(**kwargs):
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
    leg_joint_list = cmds.ls(selection=True)

    ik_fk_joints = duplicate_joint(side=side, jointList=leg_joint_list)

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True, select=True) == 'Rig_MirrorTempSkeleton_true':
        leg_joint_list_r = cmds.mirrorJoint(leg_joint_list[0], mirrorYZ=True, mirrorBehavior=True,
                                          searchReplace=('l_', 'r_'))
        legIkJtHi_r = cmds.mirrorJoint(ik_fk_joints[0][0], mirrorYZ=True, mirrorBehavior=True,
                                       searchReplace=('l_', 'r_'))
        legFkJtHi_r = cmds.mirrorJoint(ik_fk_joints[1][0], mirrorYZ=True, mirrorBehavior=True,
                                       searchReplace=('l_', 'r_'))

        fk_control_r = fk_setup(side='r', jointList=legFkJtHi_r, bodyPart='leg', scale=scale)
        ik_control_r = ik_leg_setup(side='r', jointList=legIkJtHi_r, scale=scale)
        if_fk_switch(bindSkeletonList=leg_joint_list_r, ikSkeletonList=legIkJtHi_r, fkSkeletonList=legFkJtHi_r,
                     bodyPart='leg', scale=scale, side='r', ikControls=ik_control_r[2], fkControls=fk_control_r[0])

        if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
            cmds.parent(leg_joint_list_r[0], 'c_sacrum_bn')
            cmds.parentConstraint('c_ik_hip_ctrl', fk_control_r[2], maintainOffset=True)
        else:
            cmds.parent(leg_joint_list_r[0], 'JOINTS')

    fk_control = fk_setup(side=side, jointList=ik_fk_joints[1], bodyPart='leg', scale=scale)
    ik_control = ik_leg_setup(side=side, jointList=ik_fk_joints[0], scale=scale)
    if_fk_switch(bindSkeletonList=leg_joint_list, ikSkeletonList=ik_fk_joints[0], fkSkeletonList=ik_fk_joints[1],
                 bodyPart='leg', scale=scale, side=side, ikControls=ik_control[2], fkControls=fk_control[0])

    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
        cmds.parent(leg_joint_list[0], 'c_sacrum_bn')
        cmds.parentConstraint('c_sacrum_bn', 'ikFk_legJt_doNotTouch', maintainOffset=True)
        cmds.parentConstraint('c_ik_hip_ctrl', fk_control[2], maintainOffset=True)
    else:
        cmds.parent(leg_joint_list[0], 'JOINTS')


def create_head_joint(**kwargs):
    scale = kwargs.setdefault("scale")
    side = kwargs.setdefault("side")
    neckBn = 'c_cervical_bn'
    neck_pos = cmds.joint('c_neck_tempJt', q=True, p=True)
    head_pos = cmds.joint('c_head_tempJt', q=True, p=True)
    head_end_pos = cmds.joint('c_headTop_tempJt', q=True, p=True)
    cmds.select(clear=True)

    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
        cmds.select(neckBn)
    else:
        neckBn = cmds.joint(name='c_neck_bn', position=(neck_pos[0], neck_pos[1], neck_pos[2]))

    headBn = cmds.joint(name='c_head_bn', position=(head_pos[0], head_pos[1], head_pos[2]))
    if head_pos[2] > neck_pos[2]:
        cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
                   rotationOrder='xyz')
    else:
        cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='ydown',
                   rotationOrder='xyz')
    endTop = cmds.joint(name='c_headTop_jt', position=(head_end_pos[0], head_end_pos[1], head_end_pos[2]))
    if head_end_pos[2] > head_pos[2]:
        cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='yup',
                   rotationOrder='xyz')
    else:
        cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz', secondaryAxisOrient='ydown',
                   rotationOrder='xyz')

    cmds.delete(endTop)

    joint_list = []
    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is False:
        cmds.select(neckBn, hierarchy=True)
        joint_list = cmds.ls(selection=True)
    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
        joint_list = ['c_ik_cervical_jt', headBn]

    control_group = fk_setup(side=side, jointList=joint_list, bodyPart='head',
                             scale=scale, parentJoints=False, useAllJoints=True)

    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is False:
        cmds.parent(joint_list[0], 'JOINTS')
    elif cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
        cmds.parentConstraint('c_ik_shoulder_ctrl', control_group[2], maintainOffset=True)


def create_spine_joint(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")
    number_of_joint = kwargs.setdefault("numberOfJoints")
    cmds.group(name='ikFk_spineJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

    pelvis_pos = cmds.joint('c_hip_tempJt', q=True, position=True)
    neck_pos = cmds.joint('c_neck_tempJt', q=True, position=True)
    low_pelvis_pos = cmds.joint('c_lowerHip_tempJt', q=True, position=True)
    root_pos = [low_pelvis_pos[0] + ((pelvis_pos[0] - low_pelvis_pos[0]) / 2),
               low_pelvis_pos[1] + ((pelvis_pos[1] - low_pelvis_pos[1]) / 2),
               low_pelvis_pos[2] + ((pelvis_pos[2] - low_pelvis_pos[2]) / 2)]

    cmds.select(clear=True)

    root_joint = cmds.joint(name='c_root_bn', position=(root_pos[0], root_pos[1], root_pos[2]))
    lumbarBn = cmds.joint(name='c_lumbar_bn', position=(pelvis_pos[0], pelvis_pos[1], pelvis_pos[2]))
    cmds.joint(root_joint, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='yzx')
    cervicalBn = cmds.joint(name='c_cervical_bn', position=(neck_pos[0], neck_pos[1], neck_pos[2]))
    cmds.joint(lumbarBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
               secondaryAxisOrient='zdown', rotationOrder='yzx')
    cmds.joint(cervicalBn, edit=True, zeroScaleOrient=True, orientJoint='none')

    cmds.select(root_joint, hierarchy=True)
    joint_list = cmds.ls(selection=True)
    ik_fk_joints = duplicate_joint(side=side, jointList=joint_list)

    jtHierarchy = insert_joint(prefix='c', jointList=joint_list, numberOfJoints=number_of_joint)
    ikHierarchy = insert_joint(prefix='c_ik', jointList=ik_fk_joints[0], numberOfJoints=number_of_joint)
    fkHierarchy = insert_joint(prefix='c_fk', jointList=ik_fk_joints[1], fk=True,
                               height=cmds.floatSliderGrp('Rig_heightWaistFK', q=True, value=True))

    fk_control = fk_setup(side=side, jointList=fkHierarchy, bodyPart='spine', scale=scale)
    ik_control = ik_spine_setup(side=side, jointList=ikHierarchy, scale=scale)

    cmds.select(jtHierarchy[0])
    sacrumBn = cmds.joint(name='c_sacrum_bn', p=(low_pelvis_pos[0], low_pelvis_pos[1], low_pelvis_pos[2]))
    cmds.select(ikHierarchy[0])
    sacrumJt = cmds.joint(name='c_ik_sacrum_bn', p=(low_pelvis_pos[0], low_pelvis_pos[1], low_pelvis_pos[2]))
    pelvis_control = create_pelvis_control(joint=sacrumJt,
                                           locAttributes=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                           scale=scale)

    cmds.parentConstraint(ik_control[0], fkHierarchy[0], maintainOffset=True)
    cmds.parentConstraint(fkHierarchy[0], jtHierarchy[0], maintainOffset=True)
    cmds.parentConstraint(ik_control[0], fk_control[1][0], maintainOffset=True)
    cmds.parentConstraint(fkHierarchy[-1], ik_control[3], maintainOffset=False)
    cmds.parentConstraint(ik_control[0], pelvis_control[1], maintainOffset=True)
    cmds.parent(pelvis_control[1], fk_control[2])
    jtHierarchy.append(sacrumBn)
    ikHierarchy.append(sacrumJt)
    cmds.parent(jtHierarchy[0], 'JOINTS')
    for n in range(len(jtHierarchy))[1:]:
        cmds.orientConstraint(ikHierarchy[n], jtHierarchy[n], skip="none", maintainOffset=False)


def create_finger_joint(**kwargs):
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True,
                            select=True) == 'Rig_MirrorTempSkeleton_true' and side == 'r':
        cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

    finished_list = []

    if cmds.objExists('l_innerHand_tempJt'):
        thumb = finger_setup(joint=side + '_innerHand_tempJt', side=side, scale=scale, finger='thumb',
                             parentJoint=side + '_manus_bn')
        finished_list.append(thumb[1])

    if cmds.objExists(side + '_indexFinger01_tempJt'):
        index = finger_setup(joint=side + '_indexFinger01_tempJt', side=side, scale=scale, finger='indexFinger',
                             parentJoint=side + '_middleHand_bn')
        finished_list.append(index[1])

    if cmds.objExists(side + '_middleFinger01_tempJt'):
        middle = finger_setup(joint=side + '_middleFinger01_tempJt', side=side, scale=scale, finger='middleFinger',
                              parentJoint=side + '_middleHand_bn')
        finished_list.append(middle[1])

    if cmds.objExists(side + '_ringFinger01_tempJt'):
        ring = finger_setup(joint=side + '_ringFinger01_tempJt', side=side, scale=scale, finger='ringFinger',
                            parentJoint=side + '_middleHand_bn')
        finished_list.append(ring[1])

    if cmds.objExists(side + '_outerHand_tempJt'):
        pinky = finger_setup(joint=side + '_outerHand_tempJt', side=side, scale=scale, finger='pinky',
                             parentJoint=side + '_manus_bn')
        finished_list.append(pinky[1])

    grp = cmds.group(finished_list, name=side + '_fk_fingers_grp')
    cmds.parentConstraint(side + '_manus_bn', grp, maintainOffset=True)

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True,
                            select=True) == 'Rig_MirrorTempSkeleton_true' and side == 'r':
        cmds.delete('r_collarbone_tempJt')


def connect_arm_to_spine():
    shoulder_pos = cmds.joint('l_collarbone_tempJt', q=True, p=True)
    cmds.select('c_lumbar_bn', hierarchy=True)
    joint_list = cmds.ls(selection=True)
    for joint in joint_list[1:-1]:
        length = cmds.xform(joint, q=True, translation=True)[0]
        height = cmds.xform(joint, q=True, translation=True, worldSpace=True)[1]
        if height < shoulder_pos[1] and height + length > shoulder_pos[1]:
            cmds.parent('l_clavicula_bn', 'r_clavicula_bn', joint)
            cmds.parentConstraint(joint, 'ikFk_armJt_doNotTouch', maintainOffset=True)
    cmds.parentConstraint('c_ik_shoulder_ctrl', 'l_fk_arm_grp', maintainOffset=True)
    cmds.parentConstraint('c_ik_shoulder_ctrl', 'r_fk_arm_grp', maintainOffset=True)


def create_master_control(**kwargs):
    scale = kwargs.setdefault("scale")
    master_control = create_temp_skeleton_control(scale=scale, name='master_ctrl')
    cmds.parent(master_control, 'CONTROLS')
    parent_list = ['LEFT', 'RIGHT', 'CENTER']
    scale_list = ['LEFT', 'RIGHT', 'CENTER', 'JOINTS']

    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is False:
        parent_list.append('JOINTS')

    if cmds.checkBox('Rig_AutoRigArm', q=True, value=True) is True:
        scale_list.append('ikFk_armJt_doNotTouch')
        if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is False:
            parent_list.append('ikFk_armJt_doNotTouch')

    if cmds.checkBox('Rig_AutoRigLeg', q=True, value=True) is True:
        scale_list.append('ikFk_legJt_doNotTouch')
        scale_list.append('r_ik_foot_doNotTouch')
        scale_list.append('l_ik_foot_doNotTouch')
        if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is False:
            parent_list.append('ikFk_legJt_doNotTouch')

    if cmds.checkBox('Rig_AutoRigSpine', q=True, value=True) is True:
        scale_list.append('ikFk_spineJt_doNotTouch')
    for obj in parent_list:
        cmds.parentConstraint(master_control, obj, mo=True)
    for obj in scale_list:
        cmds.scaleConstraint(master_control, obj, mo=True)


def insert_joint(**kwargs):
    prefix = kwargs.setdefault("prefix")
    joint_list = kwargs.setdefault("jointList")
    number_of_joint = kwargs.setdefault("numberOfJoints")
    fk = kwargs.setdefault("fk", False)
    height = kwargs.setdefault("height")

    cmds.select(joint_list[1])
    end_joint = cmds.joint(joint_list[-1], query=True, relative=True, position=True)

    if fk is True:
        cmds.insertJoint(joint_list[1])
        cmds.joint(edit=True, name=prefix + '_thoracic_bn', component=True, relative=True,
                   position=(end_joint[0] * height, 0, 0))
    else:
        for jt in range(1, number_of_joint)[::-1]:
            cmds.insertJoint(joint_list[1])
            cmds.joint(edit=True, name=prefix + '_thoracic' + str(jt) + '_bn', component=True, relative=True,
                       position=(end_joint[0] / number_of_joint * jt, 0, 0))
    cmds.select(joint_list[0], hierarchy=True)
    joint_hierarchy = cmds.ls(selection=True)
    return joint_hierarchy


def duplicate_joint(**kwargs):
    side = kwargs.setdefault("side")
    joint_list = kwargs.setdefault("jointList")

    for joints in joint_list[1:]:
        cmds.setAttr(joints + ".translateY", 0.0)
        cmds.setAttr(joints + ".translateZ", 0.0)

    cmds.duplicate(joint_list, returnRootsOnly=True)
    if side == 'l':
        mel.eval('searchReplaceNames "l_" "l_ik_" "hierarchy";')
    elif side == 'r':
        mel.eval('searchReplaceNames "r_" "r_ik_" "hierarchy";')
    elif side == 'c':
        mel.eval('searchReplaceNames "c_" "c_ik_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    mel.eval('searchReplaceNames "_bn" "_jt" "hierarchy";')
    cmds.select(hierarchy=True)
    ik_joint = cmds.ls(selection=True)
    cmds.select(joint_list)
    cmds.duplicate(joint_list, returnRootsOnly=True)
    if side == 'l':
        mel.eval('searchReplaceNames "l_" "l_fk_" "hierarchy";')
    elif side == 'r':
        mel.eval('searchReplaceNames "r_" "r_fk_" "hierarchy";')
    elif side == 'c':
        mel.eval('searchReplaceNames "c_" "c_fk_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    mel.eval('searchReplaceNames "_bn" "_jt" "hierarchy";')
    cmds.select(hierarchy=True)
    fk_joint = cmds.ls(selection=True)
    return ik_joint, fk_joint


def fk_setup(**kwargs):
    side = kwargs.setdefault("side")
    part = kwargs.setdefault("bodyPart")
    joint_list = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")
    parent_joint = kwargs.setdefault("parentJoints", True)
    use_all_joints = kwargs.setdefault("useAllJoints", False)

    if cmds.checkBox('Rig_AutoRigUlna', q=True, value=True) is True and part == 'arm':
        control_list = create_fk_control(jointList=joint_list[0:3],
                                     lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)

        hand_control = create_fk_control(jointList=joint_list[4:-1],
                                      lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                      hideAttr=['v'], ulna=True,
                                      scale=scale, rotateOrder=1)[0]
        control_list.append(hand_control)
    elif part == 'spine':
        control_list = create_fk_control(jointList=joint_list[2:-1], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)
    elif use_all_joints is True:
        control_list = create_fk_control(jointList=joint_list[0:], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)
    else:
        control_list = create_fk_control(jointList=joint_list[0:-1], lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                     scale=scale)

    control_group_list = parent_fk_control(controlList=control_list[::-1])
    fk_body_control_group = cmds.group(control_group_list, name=side + "_fk_" + part + "_grp")

    if side == 'l':
        cmds.parent(fk_body_control_group, 'LEFT')
    if side == 'r':
        cmds.parent(fk_body_control_group, 'RIGHT')
    if side == 'c':
        cmds.parent(fk_body_control_group, 'CENTER')

    if parent_joint is True:
        cmds.parent(joint_list[0], 'ikFk_' + part + 'Jt_doNotTouch')
    return control_list, control_group_list, fk_body_control_group


def ik_spine_setup(**kwargs):
    joint_list = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    cmds.group(name='c_ik_spine_doNotTouch', empty=True, parent='DO_NOT_TOUCH')
    cmds.select(joint_list)
    cmds.duplicate(joint_list, returnRootsOnly=True)
    mel.eval('searchReplaceNames "c_ik_" "c_ik_controlJoints_" "hierarchy";')
    mel.eval('searchReplaceNames "1" "" "hierarchy";')
    cmds.select(hierarchy=True)
    control_joint_list = cmds.ls(selection=True)
    control_joint = control_joint_list[1], control_joint_list[-1]
    cmds.parent(control_joint, control_joint_list[2], world=True)
    cmds.delete(control_joint_list[0], control_joint_list[2])

    spine_ik_handle = cmds.ikHandle(name="c_spine_ikHandle", startJoint=joint_list[0],
                                  endEffector=joint_list[-1], solver="ikSplineSolver", parentCurve=False)

    cmds.select(spine_ik_handle[2])
    cmds.rename('c_ik_spine_curve')
    ik_curve = cmds.ls(selection=True)

    cmds.skinCluster(control_joint, ik_curve, toSelectedBones=True)
    cmds.parent(ik_curve, spine_ik_handle[0], 'c_ik_spine_doNotTouch')

    shoulder_control = create_shoulder_hip_control(scale=scale, bodyPart='shoulder', joint=control_joint[1],
                                               locAttributes=['sx', 'sy', 'sz', 'v'])
    hip_control = create_shoulder_hip_control(scale=scale, bodyPart='hip', joint=control_joint[0],
                                          locAttributes=['sx', 'sy', 'sz', 'v'])

    cmds.setAttr(spine_ik_handle[0] + '.dTwistControlEnable', True)
    cmds.setAttr(spine_ik_handle[0] + '.dWorldUpType', 4)
    cmds.setAttr(spine_ik_handle[0] + '.dWorldUpAxis', 0)
    cmds.connectAttr(hip_control[2] + '.worldMatrix[0]', spine_ik_handle[0] + '.dWorldUpMatrix')
    cmds.connectAttr(shoulder_control[2] + '.worldMatrix[0]', spine_ik_handle[0] + '.dWorldUpMatrixEnd')

    ik_spine_control_group = cmds.group(shoulder_control[0], hip_control[0], name="c_ik_spine_grp")
    cmds.parent(ik_spine_control_group, 'CENTER')
    cmds.parent(shoulder_control[1], hip_control[1], 'DO_NOT_TOUCH')
    cmds.parent(joint_list[0], 'ikFk_spineJt_doNotTouch')
    return hip_control[3], hip_control[0], shoulder_control[3], shoulder_control[0]


def ik_leg_setup(**kwargs):
    side = kwargs.setdefault("side")
    joint_list = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    leg_ik_handle = cmds.ikHandle(name=side + "_leg_ikHandle", startJoint=joint_list[0],
                                endEffector=joint_list[2], solver="ikRPsolver")
    ball_ik_handle = cmds.ikHandle(name=side + "_ballFoot_ikHandle", startJoint=joint_list[2],
                                 endEffector=joint_list[3], solver="ikSCsolver")
    toe_ik_handle = cmds.ikHandle(name=side + "_toeFoot_ikHandle", startJoint=joint_list[3],
                                endEffector=joint_list[4], solver="ikSCsolver")

    footCtrl = create_foot_control(side=side, control='footIkControl', joint=joint_list[2],
                                   ikHandle=[leg_ik_handle[0], ball_ik_handle[0], toe_ik_handle[0]],
                                   aimJoint=joint_list[4],
                                   locAttributes=['sx', 'sy', 'sz', 'v'], scale=scale,
                                   addAttributes=['onHeel', 'onToe', 'onBall', 'toeFlip', 'outerBank', 'innerBank'])

    kneeCtrl = create_pole_vector_control(side=side, joint=joint_list[1], bodyPart='knee',
                                          ikHandle=leg_ik_handle[0],
                                          locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'],
                                          scale=scale)

    ik_foot_control_group = cmds.group(kneeCtrl, footCtrl[0], name=side + "_ik_leg_grp")

    if side == 'l':
        cmds.parent(ik_foot_control_group, 'LEFT')
    if side == 'r':
        cmds.parent(ik_foot_control_group, 'RIGHT')

    cmds.parent(footCtrl[1], 'DO_NOT_TOUCH')
    cmds.parent(joint_list[0], 'ikFk_legJt_doNotTouch')
    return footCtrl, kneeCtrl, ik_foot_control_group


def ik_arm_setup(**kwargs):
    side = kwargs.setdefault("side")
    joint_list = kwargs.setdefault("jointList")
    scale = kwargs.setdefault("scale")

    arm_ik_handle = cmds.ikHandle(name=side + "_arm_ikHandle", startJoint=joint_list[1],
                                endEffector=joint_list[3], solver="ikRPsolver")

    if cmds.checkBox('Rig_AutoRigUlna', q=True, value=True) is True:
        wristPos = cmds.joint(joint_list[4], q=True, position=True)
        cmds.move(wristPos[0], wristPos[1], wristPos[2],
                  arm_ik_handle[1] + ".scalePivot", arm_ik_handle[1] + ".rotatePivot")
        arm_control = create_arm_control(side=side, control='handIkControl', joint=joint_list[4], ikHandle=arm_ik_handle[0],
                                     scale=scale,
                                     ulnaJoint=joint_list[3], locAttributes=['sx', 'sy', 'sz', 'v'], jointRotateOrder=1,
                                     controlRotateOrder=1,
                                     doNotTouchRotateOrder=1)
    else:
        arm_control = create_arm_control(side=side, control='handIkControl', joint=joint_list[3], ikHandle=arm_ik_handle[0],
                                     scale=scale,
                                     locAttributes=['sx', 'sy', 'sz', 'v'], jointRotateOrder=1, controlRotateOrder=1,
                                     doNotTouchRotateOrder=1)

    elbow_control = create_pole_vector_control(side=side, joint=joint_list[2],
                                               bodyPart='elbow',
                                               ikHandle=arm_ik_handle[0],
                                               locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'], scale=scale)

    ik_foot_control_group = cmds.group(elbow_control, arm_control[0], name=side + "_ik_arm_grp")
    if side == 'l':
        cmds.parent(ik_foot_control_group, 'LEFT')
    if side == 'r':
        cmds.parent(ik_foot_control_group, 'RIGHT')
    cmds.parent(arm_control[1], 'DO_NOT_TOUCH')
    cmds.parent(joint_list[0], 'ikFk_armJt_doNotTouch')
    return arm_control, elbow_control, ik_foot_control_group


def if_fk_switch(**kwargs):
    bnList = kwargs.setdefault("bindSkeletonList")
    ikList = kwargs.setdefault("ikSkeletonList")
    fkList = kwargs.setdefault("fkSkeletonList")
    part = kwargs.setdefault('bodyPart')
    scale = kwargs.setdefault('scale')
    side = kwargs.setdefault('side')
    fk_control = kwargs.setdefault('fkControls')
    ik_control = kwargs.setdefault('ikControls')
    elbow_bone = cmds.checkBox('Rig_AutoRigUlna', q=True, value=True)

    num = 0
    ctrl = []
    if part == 'leg':
        ctrl = create_ik_fk_switch_control(joint=bnList[-3],
                                           bodyPart=part,
                                           locAttributes=['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v'],
                                           scale=scale, side=side)
    elif part == 'arm':
        ctrl = create_ik_fk_switch_control(joint=bnList[-2],
                                           bodyPart=part,
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
        if n == 3 and elbow_bone is True and part == 'arm':
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip=['y', 'z'], maintainOffset=False)
        elif n == 4 and elbow_bone is True and part == 'arm':
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip=['x'], maintainOffset=False)
        else:
            parCon = cmds.orientConstraint(ikList[n], fkList[n], bnList[n], skip="none", maintainOffset=False)
        constrainAttr = cmds.listAttr(parCon, r=True, st='*jt*')
        cmds.connectAttr(ikFkSwitchBleCol + ".outputG", parCon[0] + "." + constrainAttr[0])
        cmds.connectAttr(ikFkSwitchBleCol + ".outputR", parCon[0] + "." + constrainAttr[1])

    for ctrl in fk_control:
        cmds.connectAttr(ikFkSwitchBleCol + ".outputR", ctrl + ".visibility")
    cmds.connectAttr(ikFkSwitchBleCol + ".outputG", ik_control + ".visibility")


def finger_setup(**kwargs):
    joint = kwargs.setdefault("joint")
    side = kwargs.setdefault("side")
    scale = kwargs.setdefault("scale")
    finger = kwargs.setdefault("finger")
    parentJoint = kwargs.setdefault("parentJoint")

    cmds.select(joint, hierarchy=True)
    joint_list = cmds.ls(selection=True)

    joint_pos_list = []
    new_joint_temp_list = []
    main_skeleton_list = []
    delete_list = []

    main_skeleton_list.append(parentJoint)

    for joint in joint_list:
        jointPos = cmds.joint(joint, q=True, position=True)
        joint_pos_list.append(jointPos)

    value = len(joint_list) - (len(joint_list) / 2)
    for n in range(int(value)):
        cmds.select(parentJoint)
        joint = cmds.joint(name=side + '_' + finger + str(n + 1) + 'Temp_jt',
                        position=(joint_pos_list[n][0], joint_pos_list[n][1], joint_pos_list[n][2]))
        new_joint_temp_list.append([joint, joint_list[-n - 1]])
        delete_list.append(joint)

        if n != 0:
            cmds.aimConstraint(joint, new_joint_temp_list[n - 1][0], maintainOffset=False, aimVector=[1, 0, 0],
                               upVector=[0, 1, 0], worldUpType='object', worldUpObject=new_joint_temp_list[n - 1][1])

            cmds.select(new_joint_temp_list[n - 1][0])
            if finger == 'pinky' or finger == 'thumb':
                if finger == 'pinky' and n == 1:
                    bn = cmds.joint(name=side + '_outerHand_bn',
                                    position=(joint_pos_list[n - 1][0], joint_pos_list[n - 1][1], joint_pos_list[n - 1][2]))
                elif finger == 'thumb' and n == 1:
                    bn = cmds.joint(name=side + '_innerHand_bn',
                                    position=(joint_pos_list[n - 1][0], joint_pos_list[n - 1][1], joint_pos_list[n - 1][2]))
                else:
                    bn = cmds.joint(name=side + '_' + finger + str(n - 1) + '_bn',
                                    position=(joint_pos_list[n - 1][0], joint_pos_list[n - 1][1], joint_pos_list[n - 1][2]))
            else:
                bn = cmds.joint(name=side + '_' + finger + str(n) + '_bn',
                                position=(joint_pos_list[n - 1][0], joint_pos_list[n - 1][1], joint_pos_list[n - 1][2]))
            cmds.parent(bn, main_skeleton_list[n - 1])
            main_skeleton_list.append(bn)

    cmds.delete(delete_list)
    fk = fk_setup(side=side, jointList=main_skeleton_list[1:], bodyPart=finger, scale=scale, parentJoints=False,
                  useAllJoints=True)
    return main_skeleton_list[1:], fk[2]


def create_temp_skeleton_control(**kwargs):
    scale = kwargs.setdefault('scale', 1)
    name = kwargs.setdefault('name')
    control = cmds.circle(name=name, normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
    cmds.scale(5, 5, 5, control)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    cmds.scale(scale, scale, scale, control)
    cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
    return control


def create_pole_vector_control(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault('bodyPart')
    ikHandle = kwargs.setdefault('ikHandle')
    lock_attribute = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    grp = cmds.group(empty=True, name=side + '_' + part + '_ctrlGrp')
    space_constraint = cmds.pointConstraint(joint, grp, maintainOffset=False, skip="none")[0]
    cmds.delete(space_constraint)

    ctrl = cmds.curve(name=side + "_ik_" + part + "_ctrl", degree=3,
                      point=[(0, 0, 0), (0, 0.25, 0), (-0.5, 0.25, 0), (-0.5, -0.5, 0),
                             (0.5, -0.5, 0), (0.5, 0.5, 0), (-0.3, 0.5, 0)],
                      knot=[0, 0, 0, 1, 2, 3, 4, 4, 4])
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)
    cmds.poleVectorConstraint(ctrl, ikHandle)

    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp


def create_arm_control(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    ulnaJt = kwargs.setdefault("ulnaJoint")
    ik_handle = kwargs.setdefault('ikHandle')
    lock_attribute = kwargs.setdefault('locAttributes')
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
    space_constraint = cmds.parentConstraint(joint, grp, maintainOffset=False)
    cmds.delete(space_constraint)
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)

    cmds.parentConstraint(ctrl, ikArmDoNotTouch, maintainOffset=False)
    cmds.parent(ik_handle, ikArmDoNotTouch)

    if cmds.checkBox('Rig_AutoRigUlna', q=True, value=True) is True:
        cmds.orientConstraint(spaceLoc, ulnaJt, skip=['y', 'z'], maintainOffset=True)
        cmds.orientConstraint(spaceLoc, joint, skip='x', maintainOffset=False)
    else:
        cmds.orientConstraint(spaceLoc, joint, skip='none', maintainOffset=False)

    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp, ikArmDoNotTouch


def create_foot_control(**kwargs):
    side = kwargs.setdefault("side")
    joint = kwargs.setdefault("joint")
    ik_handle = kwargs.setdefault('ikHandle')
    lock_attribute = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    aimJoint = kwargs.setdefault('aimJoint')
    addAttr = kwargs.setdefault('addAttributes')

    if cmds.radioCollection('Rig_MirrorTempSkeleton', q=True,
                            select=True) == 'Rig_MirrorTempSkeleton_true' and side == 'r':
        cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
        mel.eval('searchReplaceNames "1" "" "hierarchy";')

    ankle_pos = cmds.joint(joint, q=True, p=True, a=True)
    heel_pos = cmds.joint(side + '_heelFoot_tempJt', q=True, p=True, a=True)

    scaleY = ankle_pos[1] - heel_pos[1]

    ctrl = cmds.curve(name=side + "_ik_foot_ctrl", degree=1,
                      point=[(-0.9, -0.4, 2.4), (-0.9, -0.4, 2.4), (-0.9, -1.2, 2.6), (0.7, -1.2, 2.6),
                             (0.7, -0.4, 2.4),
                             (-0.9, -0.4, 2.4), (-1, 0.1, -1), (1, 0.1, -1), (0.7, -0.4, 2.4), (0.7, -1.2, 2.6),
                             (1, -1.2, -1.2),
                             (1, 0.1, -1), (1, -1.2, -1.2), (-1, -1.2, -1.2), (-1, 0.1, -1), (-1, -1.2, -1.2),
                             (-0.9, -1.2, 2.6)],
                      knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

    grp = cmds.group(empty=True, name=side + "_ik_foot_ctrlGrp")
    space_constraint = cmds.pointConstraint(joint, grp, maintainOffset=False, skip="none")
    cmds.delete(space_constraint)
    cmds.parent(ctrl, grp, r=True)

    cmds.scale(scale, scaleY / 1.2, scale, grp)
    cmds.makeIdentity(grp, apply=True, scale=True)
    space_constraint = cmds.aimConstraint(aimJoint, grp, aimVector=(0.0, 0.0, 1.0), skip=["x", "z"])
    cmds.delete(space_constraint)

    ikFootDoNotTouch = cmds.group(name=side + "_ik_foot_doNotTouch", empty=True)
    cmds.parentConstraint(ctrl, ikFootDoNotTouch, maintainOffset=False, skipTranslate="none", skipRotate="none")

    onHeel = cmds.group(name=side + "_ik_onHell_negRX", empty=True, parent=ikFootDoNotTouch)
    space_constraint = cmds.pointConstraint(side + '_heelFoot_tempJt', onHeel)
    cmds.delete(space_constraint)

    onToe = cmds.group(name=side + "_ik_onToe_posRX", empty=True, parent=onHeel)
    space_constraint = cmds.pointConstraint(side + '_toeEnd_tempJt', onToe)
    cmds.delete(space_constraint)

    outerBank = None
    if side == 'l':
        outerBank = cmds.group(name=side + "_ik_outerBank_negRZ", empty=True, parent=onToe)
    elif side == 'r':
        outerBank = cmds.group(name=side + "_ik_outerBank_posRZ", empty=True, parent=onToe)
    space_constraint = cmds.pointConstraint(side + '_footOuter_tempJt', outerBank)
    cmds.delete(space_constraint)

    innerBank = None
    if side == 'l':
        innerBank = cmds.group(name=side + "_ik_innerBank_posRZ", empty=True, parent=outerBank)
    elif side == 'r':
        innerBank = cmds.group(name=side + "_ik_innerBank_negRZ", empty=True, parent=outerBank)
    space_constraint = cmds.pointConstraint(side + '_footInner_tempJt', innerBank)
    cmds.delete(space_constraint)

    # toe setting
    toeFlip = cmds.group(name=side + "_ik_toeFlip_negRX", empty=True, parent=innerBank)
    space_constraint = cmds.pointConstraint(side + '_toe_tempJt', toeFlip)
    cmds.delete(space_constraint)

    # ball setting
    onBall = cmds.group(name=side + "_ik_onBall_posRX", empty=True, parent=innerBank)
    space_constraint = cmds.pointConstraint(side + '_toe_tempJt', onBall)
    cmds.delete(space_constraint)
    cmds.parent(ik_handle[0], onBall)
    cmds.parent(ik_handle[1], innerBank)
    cmds.parent(ik_handle[2], toeFlip)

    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)

    for attr in addAttr:
        cmds.addAttr(ctrl, longName=attr, attributeType='float', keyable=True)

    multiply_divide = cmds.shadingNode('multiplyDivide', name=side + '_ik_foot_mulDiv', asUtility=True)
    cmds.setAttr(multiply_divide + '.input2X', -1)
    cmds.setAttr(multiply_divide + '.input2Y', -1)
    cmds.setAttr(multiply_divide + '.input2Z', -1)

    if 'onToe' in addAttr:
        cmds.connectAttr(ctrl + '.onToe', onToe + '.rx')
    if 'onHeel' in addAttr:
        cmds.connectAttr(ctrl + '.onHeel', multiply_divide + '.input1X')
        cmds.connectAttr(multiply_divide + '.outputX', onHeel + '.rx')

    if side == 'l':
        if 'outerBank' in addAttr:
            cmds.connectAttr(ctrl + '.outerBank', multiply_divide + '.input1Y')
            cmds.connectAttr(multiply_divide + '.outputY', outerBank + '.rz')
        if 'innerBank' in addAttr:
            cmds.connectAttr(ctrl + '.innerBank', innerBank + '.rz')
    elif side == 'r':
        if 'outerBank' in addAttr:
            cmds.connectAttr(ctrl + '.outerBank', outerBank + '.rz')
        if 'innerBank' in addAttr:
            cmds.connectAttr(ctrl + '.innerBank', multiply_divide + '.input1Y')
            cmds.connectAttr(multiply_divide + '.outputY', innerBank + '.rz')

    if 'onBall' in addAttr:
        cmds.connectAttr(ctrl + '.onBall', onBall + '.rx')
    if 'toeFlip' in addAttr:
        cmds.connectAttr(ctrl + '.toeFlip', multiply_divide + '.input1Z')
        cmds.connectAttr(multiply_divide + '.outputZ', toeFlip + '.rx')

    if cmds.radioCollection('Rig_MirrorTempSkeleton',
                            q=True,
                            select=True) == 'Rig_MirrorTempSkeleton_true' and side == 'r':
        cmds.delete('r_hip_tempJt')
    return grp, ikFootDoNotTouch


def create_shoulder_hip_control(**kwargs):
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault("bodyPart")
    lock_attribute = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    ro = kwargs.setdefault('rotationOrder', 'xyz')

    ctrl = None
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
    space_constraint = cmds.parentConstraint(joint, grp, maintainOffset=False)
    cmds.delete(space_constraint)
    cmds.parent(ctrl, grp, r=True)
    cmds.scale(scale, scale, scale, grp)

    doNotTouch = cmds.group(name='c_ik_' + part + '_doNotTouch', empty=True)
    cmds.parentConstraint(ctrl, doNotTouch, maintainOffset=False)
    spaceLoc = cmds.spaceLocator(name='c_ik_' + part + '_space')
    cmds.parent(spaceLoc, doNotTouch, relative=True)
    cmds.setAttr(spaceLoc[0] + '.tz', -0.5 * scale)
    cmds.parent(joint, doNotTouch)
    cmds.xform(ctrl, rotateOrder=ro)

    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    return grp, doNotTouch, spaceLoc[0], ctrl


def create_pelvis_control(**kwargs):
    joint = kwargs.setdefault("joint")
    lock_attribute = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    ro = kwargs.setdefault('rotationOrder', 'xyz')
    grp = cmds.group(empty=True, name='c_pelvis_ctrlGrp')
    space_constraint = cmds.parentConstraint(joint, grp)
    cmds.delete(space_constraint)
    cmds.scale(scale, scale, scale, grp)

    ctrl = cmds.circle(name='c_pelvis_ctrl', normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
    cmds.parent(ctrl, grp, r=True)
    cmds.select(ctrl + '.cv[1]', ctrl + '.cv[3]', ctrl + '.cv[5]', ctrl + '.cv[7]')
    cmds.scale(-3, -3, -3)
    cmds.setAttr(ctrl + '.ty', -2)
    cmds.scale(0.7, 0.7, 0.7, ctrl)
    cmds.makeIdentity(ctrl, apply=True, scale=True, t=True)

    cmds.xform(ctrl, rotateOrder=ro)
    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    cmds.orientConstraint(ctrl, joint, skip='none', maintainOffset=False)
    return ctrl, grp


def create_ik_fk_switch_control(**kwargs):
    joint = kwargs.setdefault("joint")
    part = kwargs.setdefault("bodyPart")
    lock_attribute = kwargs.setdefault('locAttributes')
    scale = kwargs.setdefault('scale')
    side = kwargs.setdefault('side')
    grp = cmds.group(name=side + "_" + part + "IkFkSwitch_ctrlGrp", empty=True)
    cmds.scale(scale, scale, scale, grp)

    space_constraint = None
    if part == 'arm':
        space_constraint = cmds.parentConstraint(joint, grp)
    elif part == 'leg':
        space_constraint = cmds.pointConstraint(joint, grp)
    cmds.delete(space_constraint)

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
    for attr in lock_attribute:
        cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
    if side == 'l':
        cmds.parent(grp, 'LEFT')
    elif side == 'r':
        cmds.parent(grp, 'RIGHT')
    return ctrl, ctrl + '.ikFkSwitch'


def clean_list_to_string(**kwargs):
    original_list = kwargs.setdefault("dirtyList")
    clean_string = ''
    for obj in original_list:
        if obj == original_list[0]:
            clean_string = obj
        elif len(original_list) > 1 and obj == original_list[-1]:
            clean_string = clean_string + ' and ' + obj
        else:
            clean_string = clean_string + ', ' + obj
    return clean_string
