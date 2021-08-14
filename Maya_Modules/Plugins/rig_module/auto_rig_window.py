# coding: utf-8

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds
import maya.mel as mel
import auto_rig as rig
from functools import partial


kPluginCmdName = 'AutoRigWindow'


class AutoRigWindow(OpenMayaMPx.MPxCommand):
    node_id = OpenMaya.MTypeId(0x70100)

    def __init__(self):
        OpenMayaMPx.MPxCommand.__init__(self)

    @staticmethod
    def creator():
        return OpenMayaMPx.asMPxPtr(AutoRigWindow())

    @staticmethod
    def create_auto_rig_window():
        if cmds.window('ReRig_window', exists=True):
            cmds.deleteUI('ReRig_window')

        cmds.window('ReRig_window', title="Reanimted Rigging Tool", menuBar=False, widthHeight=(500, 300))
        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

        # Fk controls tab
        child1 = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.button(label="Help", command=partial(AutoRigWindow.reate_help_window, 'CreateFKControls'), width=80)
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
        cmds.button(label="Create FK Controls", command=AutoRigWindow.create_fk_controls_button)
        cmds.text(label='')
        cmds.button(label="Parent FK Controls", command=AutoRigWindow.parent_fk_controls_button)
        cmds.setParent('..')

        # Scale FK Controls
        child4 = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.button(label="Help", command=partial(AutoRigWindow.create_help_window, 'scaleFkControles'), width=80)
        cmds.setParent('..')
        cmds.text(label='')
        cmds.button(label="List all FK controles", command=AutoRigWindow.list_fk_controls_button)
        cmds.textFieldGrp('ReRig_fkControlSelect', changeCommand=AutoRigWindow.change_scale_fk_select_button)
        cmds.paneLayout()
        cmds.textScrollList('ReRig_fkControlList', numberOfRows=8, allowMultiSelection=True, append=[],
                            showIndexedItem=4)
        cmds.setParent('..')
        cmds.floatSliderGrp('ReRig_fkControlScale', field=True, label='Scale Fk Controles ', minValue=0.01, maxValue=5,
                            fieldMinValue=0.01, fieldMaxValue=20, value=1, precision=2,
                            dragCommand=AutoRigWindow.change_scale_fk_button,
                            changeCommand=AutoRigWindow.hange_scale_fk_button)
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.button(label="Freeze transformations", command=AutoRigWindow.freeze_transformations_button)
        cmds.text(label='Freeze transformations on selected controls.', font="plainLabelFont", align="left")
        cmds.setParent('..')
        cmds.setParent('..')

        # Organize tab
        child2 = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.radioCollection('ReRig_addToJoints')
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.radioButton('ReRig_addToJoints_selected', label='Selected joints')
        cmds.radioButton('ReRig_addToJoints_hierarchy', label='Joint hierarchy')
        cmds.radioCollection('ReRig_addToJoints', edit=True, select='ReRig_addToJoints_hierarchy')
        cmds.setParent('..')
        cmds.button(label="Add '_bn' To All Joints", command=AutoRigWindow.rename_joints_button)
        cmds.text(label='')
        cmds.button(label="Create Main Groups", command=AutoRigWindow.create_main_groups_button)
        cmds.text(label='')
        cmds.button(label="Change displayed joint size", command=AutoRigWindow.display_joint_size_button)
        cmds.setParent('..')

        # Rigging tab
        child3 = cmds.rowColumnLayout(numberOfColumns=1)
        cmds.rowColumnLayout(numberOfColumns=1)
        cmds.button(label="Help", command=partial(AutoRigWindow.create_help_window, 'biPedAutoRig'), width=80)
        cmds.setParent('..')
        cmds.text(label='')
        cmds.radioCollection('ReRig_mirrorTempSkeleton')
        cmds.rowColumnLayout(numberOfColumns=2)
        cmds.radioButton('ReRig_mirrorTempSkeleton_true', label='Mirror joint position on both sides')
        cmds.radioButton('ReRig_mirrorTempSkeleton_false', label='Unique positions')
        cmds.radioCollection('ReRig_mirrorTempSkeleton', edit=True, select='ReRig_mirrorTempSkeleton_true')
        cmds.setParent('..')
        cmds.button(label="Position Your Joints", command=AutoRigWindow.create_temporary_skeleton_button)
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
        cmds.intSliderGrp('reRig_numberOfJt', field=True, label='Number of bones in spine ', minValue=2, maxValue=10,
                          fieldMinValue=2, fieldMaxValue=20, value=4)
        cmds.floatSliderGrp('reRig_heightWaistFK', field=True, label='Height for the FK contol ', minValue=0,
                            maxValue=1,
                            fieldMinValue=0, fieldMaxValue=21, value=0.28, precision=2)
        cmds.button(label="Create Your Rig", command=AutoRigWindow.create_biped_rig_button)
        cmds.setParent('..')
        cmds.tabLayout(tabs, edit=True, tabLabel=((child1, 'Create Fk Controles'), (child4, 'Scale Fk Controls'),
                                                  (child2, 'Organize'), (child3, 'Bi-Ped Auto Rig')))
        cmds.showWindow()

    @staticmethod
    def create_help_window(text):
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
            cmds.text(label='Select the attributes you want to look on your control.', font="plainLabelFont",
                      align="left")
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
            cmds.text(label='You can choose to create a full bi-ped rig or just some part of it.',
                      font="plainLabelFont",
                      align="left")
            cmds.text(label='To start you need to position out where you want your skeleton to go.',
                      font="plainLabelFont",
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
            cmds.text(
                label='Use this option if your character is mirrored and has symmetric geometry. This is standard.',
                font="plainLabelFont", align="left")
            cmds.text(label='')
            cmds.text(label='Unique positions', font="boldLabelFont", align="left")
            cmds.text(label='Use this option if your character has asymmetric geometry.', font="plainLabelFont",
                      align="left")
            cmds.text(label='')
            cmds.text(label='Create your final rig', font="boldLabelFont", align="left")
            cmds.text(label='When you are done with the position of your joints, you need to choose with element you',
                      font="plainLabelFont", align="left")
            cmds.text(label='want to incorporate (arms, legs, spine, fingers and head).', font="plainLabelFont",
                      align="left")
            cmds.text(
                label='You can also choose how many joint you want in your rig and how high up you waist fk control',
                font="plainLabelFont", align="left")
            cmds.text(label='will be. This will only be calculated if you have selected "spine".',
                      font="plainLabelFont",
                      align="left")
        if text == 'scaleFkControles':
            cmds.text(label='Scale FK Controls', font="boldLabelFont", align="left")
            cmds.text(label='Here you can scale all FK controls created with the script.', font="plainLabelFont",
                      align="left")
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

    @staticmethod
    def create_fk_controls_button():
        attr = cmds.textScrollList('ReRig_fkControlLocAttr', q=True, selectItem=True)
        radio_button = cmds.radioCollection('ReRig_fkConstraintType', q=True, select=True)
        const = radio_button.rsplit('_', 1)[1]
        rig.AutoRig.create_fk_controls(jointList=cmds.ls(sl=True), lockAttributes=attr, constraint=const)

    @staticmethod
    def parent_fk_controls_button():
        rig.AutoRig.parent_fk_controls(controlList=cmds.ls(sl=True))
        pass

    @staticmethod
    def rename_joints_button():
        if cmds.radioCollection('ReRig_addToJoints', q=True, select=True) == 'ReRig_addToJoints_hierarchy':
            cmds.select(hi=True)
            joint_list = cmds.ls(sl=True)
        else:
            joint_list = cmds.ls(sl=True)
        rig.AutoRig.rename_joints(jointList=joint_list, add='_bn')

    @staticmethod
    def create_main_groups_button():
        rig.AutoRig.create_main_groups()
        pass

    @staticmethod
    def create_temporary_skeleton_button():
        if cmds.objExists('scale_tempSkeleton_ctrl'):
            cmds.delete('scale_tempSkeleton_ctrl')
            OpenMaya.MGlobal.displayInfo("Deleted you existing temporary skelition and created a new one.")
        else:
            OpenMaya.MGlobal.displayInfo("Created a temporary skeletion.")

        rig.AutoRig.create_temporary_skeleton_spine()
        rig.AutoRig.create_temporary_skeleton_leg()
        cmds.select('c_neck_tempJt')
        rig.AutoRig.create_temporary_skeleton_arm()
        cmds.select('l_wrist_tempJt')
        rig.AutoRig.create_temporary_skeleton_fingers()

        if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_false':
            cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
            cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

        temporary_skeleton_control = rig.AutoRig.create_temporary_skeleton_control(name='scale_tempSkeleton_ctrl')
        cmds.parent('c_hip_tempJt', temporary_skeleton_control)
        cmds.select(temporary_skeleton_control)

    @staticmethod
    def list_fk_controls_button():
        fk_list_raw_list = cmds.ls('*.fkControl')
        clean_list = []
        for item in fk_list_raw_list:
            ctrl = item.split('.')
            clean_list.append(ctrl[0])
        cmds.textScrollList('ReRig_fkControlList', edit=True, append=clean_list)

    @staticmethod
    def change_scale_fk_button():
        fk_list = cmds.textScrollList('ReRig_fkControlList', q=True, selectItem=True)
        scale = cmds.floatSliderGrp('ReRig_fkControlScale', q=True, value=True)
        attr = ['sx', 'sy', 'sz']

        if fk_list is None:
            OpenMaya.MGlobal.displayWarning("Please select the controls you want to change size.")
        else:
            for item in fk_list:
                for a in attr:
                    cmds.setAttr(item + '.' + a, lock=False)
                cmds.setAttr(item + '.sy', scale)
                cmds.setAttr(item + '.sz', scale)

    @staticmethod
    def change_scale_fk_select_button():
        text = cmds.textFieldGrp('ReRig_fkControlSelect', q=True, text=True)
        fk_list = cmds.textScrollList('ReRig_fkControlList', q=True, allItems=True)
        keywords = text.split(' ')
        select_list = []

        cmds.textScrollList('ReRig_fkControlList', e=True, deselectAll=True)

        if fk_list is None:
            OpenMaya.MGlobal.displayWarning("Your list with FK controls is empty! ):")
        else:
            for item in fk_list:
                for key in keywords:
                    if key in item:
                        select_list.append(item)

        cmds.textScrollList('ReRig_fkControlList', e=True, selectItem=select_list)

    @staticmethod
    def freeze_transformations_button():
        fk_list = cmds.textScrollList('ReRig_fkControlList', q=True, selectItem=True)
        attr = ['sx', 'sy', 'sz']

        if fk_list is None:
            OpenMaya.MGlobal.displayWarning("Please select the FK controls you want to freeze.")
        else:
            for item in fk_list:
                if cmds.getAttr(item + '.sx', lock=True) is False:
                    cmds.makeIdentity(item, apply=True, scale=True)
                    for a in attr:
                        cmds.setAttr(item + '.' + a, lock=True)

    @staticmethod
    def create_biped_rig_button():
        if not cmds.objExists('scale_tempSkeleton_ctrl'):
            OpenMaya.MGlobal.displayWarning("You need to position your joints before you create your rig.")

        else:
            scale = cmds.getAttr('scale_tempSkeleton_ctrl.scaleX')
            result_list = []

            if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
                rig.AutoRig.create_main_groups()
                rig.AutoRig.create_spine_joint(scale=scale, side='c',
                                               numberOfJoints=cmds.intSliderGrp('reRig_numberOfJt', q=True, value=True))
                result_list.append('SPINE')

            if cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
                rig.AutoRig.create_main_groups()
                rig.AutoRig.create_arm_joints(side='l', scale=scale)
                ret_skeleton = cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True)
                if ret_skeleton == 'ReRig_mirrorTempSkeleton_false':
                    rig.AutoRig.create_arm_joints(side='r', scale=scale)
                result_list.append('ARMS')

            if cmds.checkBox('reRig_autoRigLeg', q=True, value=True) is True:
                rig.AutoRig.create_main_groups()
                rig.AutoRig.create_leg_joints(side='l', scale=scale)
                ret_skeleton = cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True)
                if ret_skeleton == 'ReRig_mirrorTempSkeleton_false':
                    rig.AutoRig.create_leg_joints(side='r', scale=scale)
                result_list.append('LEGS')

            if cmds.checkBox('reRig_autoRigHead', q=True, value=True) is True:
                rig.AutoRig.create_main_groups()
                rig.AutoRig.create_head_joints(scale=scale, side='c')
                result_list.append('HEAD')

            ret_finger = cmds.checkBox('reRig_autoRigFingers', q=True, value=True)
            if ret_finger is True and cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
                rig.AutoRig.create_main_groups()
                rig.AutoRig.create_finger_joints(scale=scale, side='l')
                rig.AutoRig.create_finger_joints(scale=scale, side='r')
                result_list.append('FINGERS')

            ret_spine = cmds.checkBox('reRig_autoRigSpine', q=True, value=True)
            if ret_spine is True and cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
                rig.AutoRig.connect_arm_to_spine()

            if cmds.checkBox('reRig_autoMasterCtrl', q=True, value=True) is True:
                rig.AutoRig.create_master_control(scale=scale)
                result_list.append('MASTER CONTROL')

            clean_string = rig.AutoRig.clean_list_tostring(dirtyList=result_list)

            ret_finger = cmds.checkBox('reRig_autoRigFingers', q=True, value=True)
            ret_arm = cmds.checkBox('reRig_autoRigArm', q=True, value=True)
            if ret_finger is True and ret_arm is False:
                OpenMaya.MGlobal.displayWarning("You can NOT create fingers without an arm! " + clean_string + '.')
            else:
                OpenMaya.MGlobal.displayInfo("Successfully created: " + clean_string + '.')

    @staticmethod
    def display_joint_size_button():
        mel.eval('jdsWin;')
        pass


def initializePlugin(mObject):
    mPlugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mPlugin.registerCommand(kPluginCmdName, AutoRigWindow.creator())
    except ArithmeticError as e:
        sys.stderr.write('Failed load plugin : %s' % kPluginCmdName)
        raise


def uninitializePlugin(mObject):
    mPlugin = OpenMayaMPx.MFnPlugin(mObject)
    try:
        mPlugin.deregisterCommand(kPluginCmdName)
    except ArithmeticError as e:
        sys.stderr.write('Failed unload plugin : %s' % kPluginCmdName)
        raise



