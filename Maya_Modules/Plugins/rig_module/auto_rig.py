# coding: utf-8

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import maya.mel as mel


class AutoRig:

    def __init__(self):
        pass

    @staticmethod
    def create_fk_controls(**kwargs):
        selection = kwargs.setdefault("jointList")
        lock_attr = kwargs.setdefault("lockAttributes", ['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'])
        ulna = kwargs.setdefault("ulna", False)
        scale = kwargs.setdefault("scale", 1)
        rotate_order = kwargs.setdefault("rotateOrder", 0)
        fk_attr = kwargs.setdefault('addFkAttribute', True)
        constraint = kwargs.setdefault('constraint', 'orient')

        if not selection:
            OpenMaya.MGlobal.displayWarning("You have to at least select 1 joint.")

        ctrl_list = []

        for obj in selection:
            name_split = obj.rsplit('_', 1)
            if len(name_split) >= 2:
                cmds.setAttr(obj + ".rotateOrder", rotate_order)
                name = name_split[0]
                group = cmds.group(empty=True, name=name + '_ctrlGrp')
                cmds.parent(group, obj, r=True)
                cmds.parent(group, w=True)
                ctrl = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), name=name + '_ctrl', radius=1)
                cmds.setAttr(ctrl[0] + ".rotateOrder", rotate_order)
                cmds.parent(ctrl[0], group, r=True)
                cmds.scale(scale, scale, scale, group)
                if ulna is True:
                    ulnaJt = cmds.listRelatives(obj, parent=True)
                    cmds.orientConstraint(ctrl[0], obj, mo=False, skip='x')
                    cmds.orientConstraint(ctrl[0], ulnaJt, mo=True, skip=['y', 'z'])
                elif constraint == 'point':
                    cmds.pointConstraint(ctrl[0], obj, mo=False)
                elif constraint == 'parent':
                    cmds.parentConstraint(ctrl[0], obj, mo=False)
                elif constraint == 'orient':
                    cmds.orientConstraint(ctrl[0], obj, mo=False)

                if fk_attr is True:
                    cmds.addAttr(ctrl[0], longName='fkControl', attributeType='float', keyable=True)
                    lock_attr.append('fkControl')

                ctrl_list.append(ctrl[0])
                for loc in lock_attr:
                    cmds.setAttr(ctrl[0] + '.' + loc, lock=True, keyable=False, channelBox=False)
                cmds.setAttr(ctrl[0] + '.v', lock=False)
            else:
                OpenMaya.MGlobal.displayWarning("Your joints are not named correctly: jointName_bn")
        return ctrl_list

    @staticmethod
    def parent_fk_controls(**kwargs):
        control_list = kwargs.setdefault("controlList")
        control_grep_list = []
        control_parent_list = []

        for ctrl in control_list:
            name_split = ctrl.rsplit('_', 1)
            if 'ctrl' == name_split[-1]:
                index = control_list.index(ctrl)
                control_grep = cmds.listRelatives(ctrl, parent=True)[0]
                control_grep_list.append(control_grep)
                if ctrl != control_list[-1]:
                    parent_control = control_list[index + 1]
                    cmds.parentConstraint(parent_control, control_grep, maintainOffset=True)
                    control_parent_list.append(ctrl)
            else:
                value = " is not a control object. If it is, make sure it's named correctly: control_object"
                OpenMaya.MGlobal.displayWarning(ctrl + value)

        if not control_parent_list:
            clean_string = AutoRig.clean_list_tostring(dirtyList=control_parent_list)
            OpenMaya.MGlobal.displayInfo("Managed to successfully parent " + clean_string + ".")

        return control_grep_list

    @staticmethod
    def rename_joints(**kwargs):
        joint_list = kwargs.setdefault("jointList")
        add = kwargs.setdefault("add")
        new_joint_list = []
        for jt in joint_list:
            try:
                cmds.joint(jt, edit=True, name=jt + add)
                new_joint_list.append(jt + add)
            except ArithmeticError as e:
                OpenMaya.MGlobal.displayWarning(jt + " is not a joint." + e)
        return new_joint_list

    @staticmethod
    def create_main_groups():
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

    @staticmethod
    def create_temporary_skeleton_spine():
        cmds.joint(name='c_hip_tempJt', position=(0, 11.7, 0))
        cmds.joint(name='c_neck_tempJt', position=(0, 18, 0))
        cmds.joint('c_hip_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.joint(name='c_head_tempJt', position=(0, 18.6, 0.6))
        cmds.joint('c_neck_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.joint(name='c_headTop_tempJt', position=(0, 20.7, 0.6))
        cmds.joint('c_head_tempJt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.select('c_hip_tempJt')
        cmds.joint(name='c_lowerHip_tempJt', position=(0, 11.2, 0))

    @staticmethod
    def create_temporary_skeleton_leg():
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

    @staticmethod
    def create_temporary_skeleton_arm():
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

    @staticmethod
    def create_temporary_skeleton_fingers():
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
        AutoRig.create_finger_controller_for_temporary(
            joints=[
                'l_innerHand_tempJt',
                'l_indexFinger01_tempJt',
                'l_middleFinger01_tempJt',
                'l_ringFinger01_tempJt',
                'l_outerHand_tempJt']
        )

    @staticmethod
    def create_finger_controller_for_temporary(**kwargs):
        joints = kwargs.setdefault("joints")

        for jt in joints:
            cmds.select(jt, hierarchy=True)
            joint_list = cmds.ls(selection=True)

            for joint in joint_list[:-1]:
                pos = cmds.joint(joint, q=True, position=True)
                nameSplit = joint.rsplit('_', 1)
                name = nameSplit[0]
                cmds.select(joint)
                cmds.joint(name=name + 'Up_tempJt', position=(pos[0], pos[1] + 0.5, pos[2]))

    @staticmethod
    def create_arm_joints(**kwargs):
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

        clavicula_bn = cmds.joint(name=side + '_clavicula_bn',
                                  position=(clavicleLPos[0], clavicleLPos[1], clavicleLPos[2]))
        humerusBn = cmds.joint(name=side + '_humerus_bn', position=(shoulderPos[0], shoulderPos[1], shoulderPos[2]))
        cmds.joint(clavicula_bn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='zdown', rotationOrder='xyz')
        radiusBn = cmds.joint(name=side + '_radius_bn', position=(elbowPos[0], elbowPos[1], elbowPos[2]))

        cmds.joint(humerusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='yup', rotationOrder='xyz')

        manus_jt_temp = cmds.joint(name=side + '_manusTemp_jt', position=(wristPos[0], wristPos[1], wristPos[2]))
        cmds.joint(radiusBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='zdown', rotationOrder='xyz')
        cmds.joint(name=side + '_endArmTemp_jt', position=(middleHandPos[0], middleHandPos[1], middleHandPos[2]))

        cmds.joint(manus_jt_temp, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='yup', rotationOrder='xyz')
        spaceConstrain = cmds.aimConstraint('l_handUp_tempJt', manus_jt_temp, maintainOffset=False, aimVector=[0, 1, 0],
                                            upVector=[-1, 0, 0], worldUpType="scene", skip=['y', 'z'])

        cmds.select(manus_jt_temp)
        manus_bn = cmds.joint(name=side + '_manus_bn', position=(wristPos[0], wristPos[1], wristPos[2]))
        cmds.parent(manus_bn, radiusBn)
        cmds.joint(name=side + '_middleHand_bn', position=(middleHandPos[0], middleHandPos[1], middleHandPos[2]))
        cmds.delete(spaceConstrain, manus_jt_temp)

        ret = cmds.checkBox('reRig_autoRigUlna', q=True, value=True)
        if ret is True:
            manus_bn_pos = cmds.joint(manus_bn, query=True, relative=True, position=True)
            ulnaBn = cmds.insertJoint(radiusBn)
            cmds.joint(ulnaBn, edit=True, name=side + '_ulna_bn', component=True, relative=True,
                       position=(manus_bn_pos[0] / 2, 0, 0), rotationOrder='xyz')

        cmds.select(clavicula_bn, hierarchy=True)
        arm_joint_list = cmds.ls(selection=True)
        ik_fk_joints = AutoRig.duplicate_joints(side=side, jointList=arm_joint_list)

        if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true':
            arm_joint_list_r = cmds.mirrorJoint(arm_joint_list[0], mirrorYZ=True, mirrorBehavior=True,
                                                searchReplace=('l_', 'r_'))
            arm_ik_jt_hi_r = cmds.mirrorJoint(ik_fk_joints[0][0], mirrorYZ=True, mirrorBehavior=True,
                                              searchReplace=('l_', 'r_'))
            arm_fk_jt_hi_r = cmds.mirrorJoint(ik_fk_joints[1][0], mirrorYZ=True, mirrorBehavior=True,
                                              searchReplace=('l_', 'r_'))

            fk_controls_r = AutoRig.fk_setup(side='r', jointList=arm_fk_jt_hi_r, bodyPart='arm', scale=scale)
            ik_controls_r = AutoRig.ik_arm_setup(side='r', jointList=arm_ik_jt_hi_r, scale=scale)
            cmds.parent(arm_joint_list_r[0], 'JOINTS')
            AutoRig.fk_switch_control(bindSkeletonList=arm_joint_list_r, ikSkeletonList=arm_ik_jt_hi_r,
                                      fkSkeletonList=arm_fk_jt_hi_r, bodyPart='arm', scale=scale, side='r',
                                      ikControls=ik_controls_r[2], fkControls=fk_controls_r[0][1:])

        fk_controls = AutoRig.fk_setup(side=side, jointList=ik_fk_joints[1], bodyPart='arm', scale=scale)
        ik_controls = AutoRig.ik_arm_setup(side=side, jointList=ik_fk_joints[0], scale=scale)
        cmds.parent(arm_joint_list[0], 'JOINTS')
        AutoRig.fk_switch_control(bindSkeletonList=arm_joint_list, ikSkeletonList=ik_fk_joints[0],
                                  fkSkeletonList=ik_fk_joints[1], bodyPart='arm', scale=scale, side=side,
                                  ikControls=ik_controls[2], fkControls=fk_controls[0][1:])

    @staticmethod
    def create_leg_joints(**kwargs):
        side = kwargs.setdefault("side")
        scale = kwargs.setdefault("scale")

        if side == 'l':
            cmds.group(name='ikFk_legJt_doNotTouch', empty=True, parent='DO_NOT_TOUCH')

        femur_pos = cmds.joint(side + '_hip_tempJt', q=True, position=True)
        tibia_pos = cmds.joint(side + '_knee_tempJt', q=True, position=True)
        ped_pos = cmds.joint(side + '_ankle_tempJt', q=True, position=True)
        toe_pos = cmds.joint(side + '_toe_tempJt', q=True, position=True)
        toe_end_pos = cmds.joint(side + '_toeEnd_tempJt', q=True, position=True)

        cmds.select(clear=True)

        femur_jt_temp = cmds.joint(name=side + '_femurTemp_jt', position=(femur_pos[0], femur_pos[1], femur_pos[2]))
        cmds.aimConstraint(side + '_knee_tempJt', femur_jt_temp, maintainOffset=False, aimVector=[1, 0, 0],
                           upVector=[0, 1, 0], worldUpType='object', worldUpObject=side + '_hipFront_tempJt')
        cmds.select(femur_jt_temp)
        femusBn = cmds.joint(name=side + '_femur_bn', position=(femur_pos[0], femur_pos[1], femur_pos[2]))
        cmds.parent(femusBn, world=True)
        cmds.delete(femur_jt_temp)

        tibia_jt_temp = cmds.joint(name=side + '_tibiaTemp_jt', position=(tibia_pos[0], tibia_pos[1], tibia_pos[2]))
        cmds.aimConstraint(side + '_ankle_tempJt', tibia_jt_temp, maintainOffset=False, aimVector=[1, 0, 0],
                           upVector=[0, 1, 0], worldUpType='object', worldUpObject=side + '_kneeFront_tempJt')
        cmds.select(tibia_jt_temp)
        tibiaBn = cmds.joint(name=side + '_tibia_bn', position=(tibia_pos[0], tibia_pos[1], tibia_pos[2]))
        cmds.parent(tibiaBn, femusBn)
        cmds.delete(tibia_jt_temp)

        pedBn = cmds.joint(name=side + '_ped_bn', position=(ped_pos[0], ped_pos[1], ped_pos[2]))
        toeBn = cmds.joint(name=side + '_toe_bn', position=(toe_pos[0], toe_pos[1], toe_pos[2]))
        cmds.joint(pedBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='yup', rotationOrder='xyz')

        end_joint = cmds.joint(name=side + '_endLeg_jt', position=(toe_end_pos[0], toe_end_pos[1], toe_end_pos[2]))
        cmds.joint(toeBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='yup', rotationOrder='xyz')
        cmds.joint(end_joint, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                   secondaryAxisOrient='yup', rotationOrder='xyz')

        cmds.select(femusBn, hierarchy=True)
        leg_joint_list = cmds.ls(selection=True)
        ik_fk_joints = AutoRig.duplicate_joints(side=side, jointList=leg_joint_list)

        if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true':
            leg_joint_list_r = cmds.mirrorJoint(leg_joint_list[0], mirrorYZ=True,
                                                mirrorBehavior=True, searchReplace=('l_', 'r_'))
            leg_ik_jt_hi_r = cmds.mirrorJoint(ik_fk_joints[0][0], mirrorYZ=True,
                                              mirrorBehavior=True, searchReplace=('l_', 'r_'))
            leg_fk_jt_hi_r = cmds.mirrorJoint(ik_fk_joints[1][0], mirrorYZ=True,
                                              mirrorBehavior=True, searchReplace=('l_', 'r_'))

            fk_controls_r = AutoRig.fk_setup(side='r', jointList=leg_fk_jt_hi_r, bodyPart='leg', scale=scale)
            ik_controls_r = AutoRig.ik_leg_setup(side='r', jointList=leg_ik_jt_hi_r, scale=scale)
            AutoRig.fk_switch_control(bindSkeletonList=leg_joint_list_r, ikSkeletonList=leg_ik_jt_hi_r,
                                      fkSkeletonList=leg_fk_jt_hi_r, bodyPart='leg', scale=scale, side='r',
                                      ikControls=ik_controls_r[2], fkControls=fk_controls_r[0])

            if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
                cmds.parent(leg_joint_list_r[0], 'c_sacrum_bn')
                cmds.parentConstraint('c_ik_hip_ctrl', fk_controls_r[2], maintainOffset=True)
            else:
                cmds.parent(leg_joint_list_r[0], 'JOINTS')

        fk_controls = AutoRig.fk_setup(side=side, jointList=ik_fk_joints[1], bodyPart='leg', scale=scale)
        ik_controls = AutoRig.ik_leg_setup(side=side, jointList=ik_fk_joints[0], scale=scale)
        AutoRig.fk_switch_control(bindSkeletonList=leg_joint_list, ikSkeletonList=ik_fk_joints[0],
                                  fkSkeletonList=ik_fk_joints[1],
                                  bodyPart='leg', scale=scale, side=side,
                                  ikControls=ik_controls[2], fkControls=fk_controls[0])

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            cmds.parent(leg_joint_list[0], 'c_sacrum_bn')
            cmds.parentConstraint('c_sacrum_bn', 'ikFk_legJt_doNotTouch', maintainOffset=True)
            cmds.parentConstraint('c_ik_hip_ctrl', fk_controls[2], maintainOffset=True)
        else:
            cmds.parent(leg_joint_list[0], 'JOINTS')

    @staticmethod
    def create_head_joints(**kwargs):
        scale = kwargs.setdefault("scale")
        side = kwargs.setdefault("side")

        neckBn = 'c_cervical_bn'

        neck_pos = cmds.joint('c_neck_tempJt', q=True, p=True)
        head_pos = cmds.joint('c_head_tempJt', q=True, p=True)
        head_end_pos = cmds.joint('c_headTop_tempJt', q=True, p=True)

        cmds.select(clear=True)

        ret_spine_checked = cmds.checkBox('reRig_autoRigSpine', q=True, value=True)
        if ret_spine_checked:
            cmds.select(neckBn)
        else:
            neckBn = cmds.joint(name='c_neck_bn', position=(neck_pos[0], neck_pos[1], neck_pos[2]))

        headBn = cmds.joint(name='c_head_bn', position=(head_pos[0], head_pos[1], head_pos[2]))
        if head_pos[2] > neck_pos[2]:
            cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                       secondaryAxisOrient='yup', rotationOrder='xyz')
        else:
            cmds.joint(neckBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                       secondaryAxisOrient='ydown', rotationOrder='xyz')
        endTop = cmds.joint(name='c_headTop_jt', position=(head_end_pos[0], head_end_pos[1], head_end_pos[2]))

        if head_end_pos[2] > head_pos[2]:
            cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                       secondaryAxisOrient='yup', rotationOrder='xyz')
        else:
            cmds.joint(headBn, edit=True, zeroScaleOrient=True, orientJoint='xyz',
                       secondaryAxisOrient='ydown', rotationOrder='xyz')

        cmds.delete(endTop)

        joint_list = None
        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
            cmds.select(neckBn, hierarchy=True)
            joint_list = cmds.ls(selection=True)

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            joint_list = ['c_ik_cervical_jt', headBn]

        controls_grep = AutoRig.fk_setup(side=side, jointList=joint_list, bodyPart='head', scale=scale,
                                         parentJoints=False, useAllJoints=True)

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
            cmds.parent(joint_list[0], 'JOINTS')
        elif cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            cmds.parentConstraint('c_ik_shoulder_ctrl', controls_grep[2], maintainOffset=True)

    @staticmethod
    def create_spine_joint(**kwargs):
        side = kwargs.setdefault("side")
        scale = kwargs.setdefault("scale")
        joint_num = kwargs.setdefault("numberOfJoints")

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
        ik_fk_joints = AutoRig.duplicate_joints(side=side, jointList=joint_list)

        jtHierarchy = AutoRig.insert_joints(prefix='c', jointList=joint_list, numberOfJoints=joint_num)
        ikHierarchy = AutoRig.insert_joints(prefix='c_ik', jointList=ik_fk_joints[0], numberOfJoints=joint_num)
        fkHierarchy = AutoRig.insert_joints(prefix='c_fk', jointList=ik_fk_joints[1], fk=True,
                                            height=cmds.floatSliderGrp('reRig_heightWaistFK', q=True, value=True))

        fk_controls = AutoRig.fk_setup(side=side, jointList=fkHierarchy, bodyPart='spine', scale=scale)
        ik_controls = AutoRig.ik_spine_setup(side=side, jointList=ikHierarchy, scale=scale)

        cmds.select(jtHierarchy[0])
        sacrumBn = cmds.joint(name='c_sacrum_bn', p=(low_pelvis_pos[0], low_pelvis_pos[1], low_pelvis_pos[2]))
        cmds.select(ikHierarchy[0])
        sacrumJt = cmds.joint(name='c_ik_sacrum_bn', p=(low_pelvis_pos[0], low_pelvis_pos[1], low_pelvis_pos[2]))
        pelvis_control = AutoRig.create_pelvis_control(joint=sacrumJt,
                                                       locAttributes=['tx', 'ty', 'tz', 'sx', 'sy', 'sz', 'v'],
                                                       scale=scale)

        cmds.parentConstraint(ik_controls[0], fkHierarchy[0], maintainOffset=True)
        cmds.parentConstraint(fkHierarchy[0], jtHierarchy[0], maintainOffset=True)
        cmds.parentConstraint(ik_controls[0], fk_controls[1][0], maintainOffset=True)
        cmds.parentConstraint(fkHierarchy[-1], ik_controls[3], maintainOffset=False)
        cmds.parentConstraint(ik_controls[0], pelvis_control[1], maintainOffset=True)
        cmds.parent(pelvis_control[1], fk_controls[2])

        jtHierarchy.append(sacrumBn)
        ikHierarchy.append(sacrumJt)

        cmds.parent(jtHierarchy[0], 'JOINTS')

        for n in range(len(jtHierarchy))[1:]:
            cmds.orientConstraint(ikHierarchy[n], jtHierarchy[n], skip="none", maintainOffset=False)

    @staticmethod
    def create_finger_joints(**kwargs):
        side = kwargs.setdefault("side")
        scale = kwargs.setdefault("scale")

        if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                                select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
            cmds.mirrorJoint('l_collarbone_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))

        finished_list = []

        if cmds.objExists('l_innerHand_tempJt'):
            thumb = AutoRig.create_finger_joint(joint=side + '_innerHand_tempJt', side=side, scale=scale,
                                                finger='thumb',
                                                parentJoint=side + '_manus_bn')
            finished_list.append(thumb[1])

        if cmds.objExists(side + '_indexFinger01_tempJt'):
            index = AutoRig.create_finger_joint(joint=side + '_indexFinger01_tempJt', side=side, scale=scale,
                                                finger='indexFinger',
                                                parentJoint=side + '_middleHand_bn')
            finished_list.append(index[1])

        if cmds.objExists(side + '_middleFinger01_tempJt'):
            middle = AutoRig.create_finger_joint(joint=side + '_middleFinger01_tempJt', side=side, scale=scale,
                                                 finger='middleFinger',
                                                 parentJoint=side + '_middleHand_bn')
            finished_list.append(middle[1])

        if cmds.objExists(side + '_ringFinger01_tempJt'):
            ring = AutoRig.create_finger_joint(joint=side + '_ringFinger01_tempJt', side=side, scale=scale,
                                               finger='ringFinger',
                                               parentJoint=side + '_middleHand_bn')
            finished_list.append(ring[1])

        if cmds.objExists(side + '_outerHand_tempJt'):
            pinky = AutoRig.create_finger_joint(joint=side + '_outerHand_tempJt', side=side, scale=scale,
                                                finger='pinky',
                                                parentJoint=side + '_manus_bn')
            finished_list.append(pinky[1])

        group = cmds.group(finished_list, name=side + '_fk_fingers_grp')
        cmds.parentConstraint(side + '_manus_bn', group, maintainOffset=True)

        if cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True,
                                select=True) == 'ReRig_mirrorTempSkeleton_true' and side == 'r':
            cmds.delete('r_collarbone_tempJt')

    @staticmethod
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

    @staticmethod
    def create_master_control(**kwargs):
        scale = kwargs.setdefault("scale")
        master_control = AutoRig.create_temporary_skeleton_control(scale=scale, name='master_ctrl')
        cmds.parent(master_control, 'CONTROLS')
        parent_list = ['LEFT', 'RIGHT', 'CENTER']
        scale_list = ['LEFT', 'RIGHT', 'CENTER', 'JOINTS']

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
            parent_list.append('JOINTS')

        if cmds.checkBox('reRig_autoRigArm', q=True, value=True) is True:
            scale_list.append('ikFk_armJt_doNotTouch')
            if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
                parent_list.append('ikFk_armJt_doNotTouch')

        if cmds.checkBox('reRig_autoRigLeg', q=True, value=True) is True:
            scale_list.append('ikFk_legJt_doNotTouch')
            scale_list.append('r_ik_foot_doNotTouch')
            scale_list.append('l_ik_foot_doNotTouch')
            if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is False:
                parent_list.append('ikFk_legJt_doNotTouch')

        if cmds.checkBox('reRig_autoRigSpine', q=True, value=True) is True:
            scale_list.append('ikFk_spineJt_doNotTouch')

        for obj in parent_list:
            cmds.parentConstraint(master_control, obj, mo=True)
        for obj in scale_list:
            cmds.scaleConstraint(master_control, obj, mo=True)

    @staticmethod
    def insert_joints(**kwargs):
        prefix = kwargs.setdefault("prefix")
        joint_list = kwargs.setdefault("jointList")
        number_of_joints = kwargs.setdefault("numberOfJoints")
        fk = kwargs.setdefault("fk", False)
        height = kwargs.setdefault("height")
        cmds.select(joint_list[1])

        endJt = cmds.joint(joint_list[-1], query=True, relative=True, position=True)

        if fk is True:
            cmds.insertJoint(joint_list[1])
            cmds.joint(edit=True, name=prefix + '_thoracic_bn', component=True, relative=True,
                       position=(endJt[0] * height, 0, 0))
        else:
            for jt in range(1, number_of_joints)[::-1]:
                cmds.insertJoint(joint_list[1])
                cmds.joint(edit=True, name=prefix + '_thoracic' + str(jt) + '_bn', component=True, relative=True,
                           position=(endJt[0] / number_of_joints * jt, 0, 0))
        cmds.select(joint_list[0], hierarchy=True)
        joint_hierarchy = cmds.ls(selection=True)
        return joint_hierarchy

    @staticmethod
    def duplicate_joints(**kwargs):
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
        ik_joint_hierarchy = cmds.ls(selection=True)

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
        fk_joint_hierarchy = cmds.ls(selection=True)
        return ik_joint_hierarchy, fk_joint_hierarchy

    @staticmethod
    def fk_setup(**kwargs):
        side = kwargs.setdefault("side")
        part = kwargs.setdefault("bodyPart")
        joint_list = kwargs.setdefault("jointList")
        scale = kwargs.setdefault("scale")
        parent_joints = kwargs.setdefault("parentJoints", True)
        use_all_joints = kwargs.setdefault("useAllJoints", False)

        if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) is True and part == 'arm':
            control_list = AutoRig.create_fk_controls(jointList=joint_list[0:3],
                                                      lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                                      scale=scale)
            add_ctrl_list = AutoRig.create_fk_controls(jointList=joint_list[4:-1],
                                                       lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                                       hideAttr=['v'], ulna=True, scale=scale, rotateOrder=1)[0]
            control_list.append(add_ctrl_list)
        elif part == 'spine':
            control_list = AutoRig.create_fk_controls(jointList=joint_list[2:-1],
                                                      lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                                      scale=scale)
        elif use_all_joints is True:
            control_list = AutoRig.create_fk_controls(jointList=joint_list[0:],
                                                      lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                                      scale=scale)
        else:
            control_list = AutoRig.create_fk_controls(jointList=joint_list[0:-1],
                                                      lockAttributes=['tx', 'tz', 'ty', 'sx', 'sy', 'sz', 'v'],
                                                      scale=scale)

        control_group_list = AutoRig.parent_fk_controls(controlList=control_list[::-1])
        fk_body_control_group = cmds.group(control_group_list, name=side + "_fk_" + part + "_grp")

        if side == 'l':
            cmds.parent(fk_body_control_group, 'LEFT')
        if side == 'r':
            cmds.parent(fk_body_control_group, 'RIGHT')
        if side == 'c':
            cmds.parent(fk_body_control_group, 'CENTER')

        if parent_joints is True:
            cmds.parent(joint_list[0], 'ikFk_' + part + 'Jt_doNotTouch')
        return control_list, control_group_list, fk_body_control_group

    @staticmethod
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
        control_joints = control_joint_list[1], control_joint_list[-1]
        cmds.parent(control_joints, control_joint_list[2], world=True)
        cmds.delete(control_joint_list[0], control_joint_list[2])

        spine_ik_handle = cmds.ikHandle(name="c_spine_ikHandle", startJoint=joint_list[0],
                                        endEffector=joint_list[-1], solver="ikSplineSolver", parentCurve=False)

        cmds.select(spine_ik_handle[2])
        cmds.rename('c_ik_spine_curve')
        ik_curve = cmds.ls(selection=True)

        cmds.skinCluster(control_joints, ik_curve, toSelectedBones=True)
        cmds.parent(ik_curve, spine_ik_handle[0], 'c_ik_spine_doNotTouch')
        shoulder_control = AutoRig.create_shoulder_hip_control(scale=scale, bodyPart='shoulder',
                                                               joint=control_joints[1],
                                                               locAttributes=['sx', 'sy', 'sz', 'v'])

        hip_control = AutoRig.create_shoulder_hip_control(scale=scale, bodyPart='hip',
                                                          joint=control_joints[0],
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

    @staticmethod
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

        foot_ctrl = AutoRig.create_foot_control(side=side, control='footIkControl', joint=joint_list[2],
                                                ikHandle=[leg_ik_handle[0], ball_ik_handle[0], toe_ik_handle[0]],
                                                aimJoint=joint_list[4],
                                                locAttributes=['sx', 'sy', 'sz', 'v'], scale=scale,
                                                addAttributes=['onHeel', 'onToe', 'onBall', 'toeFlip', 'outerBank',
                                                               'innerBank'])

        knee_ctrl = AutoRig.create_pole_vector_control(side=side, joint=joint_list[1], bodyPart='knee',
                                                       ikHandle=leg_ik_handle[0],
                                                       locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'],
                                                       scale=scale)

        ik_foot_control_group = cmds.group(knee_ctrl, foot_ctrl[0], name=side + "_ik_leg_grp")

        if side == 'l':
            cmds.parent(ik_foot_control_group, 'LEFT')
        if side == 'r':
            cmds.parent(ik_foot_control_group, 'RIGHT')

        cmds.parent(foot_ctrl[1], 'DO_NOT_TOUCH')
        cmds.parent(joint_list[0], 'ikFk_legJt_doNotTouch')
        return foot_ctrl, knee_ctrl, ik_foot_control_group

    @staticmethod
    def ik_arm_setup(**kwargs):
        side = kwargs.setdefault("side")
        jtList = kwargs.setdefault("jointList")
        scale = kwargs.setdefault("scale")

        arm_ik_handle = cmds.ikHandle(name=side + "_arm_ikHandle",
                                      startJoint=jtList[1], endEffector=jtList[3], solver="ikRPsolver")
        has_checked = cmds.checkBox('reRig_autoRigUlna', q=True, value=True)
        if has_checked:
            wristPos = cmds.joint(jtList[4], q=True, position=True)
            cmds.move(wristPos[0], wristPos[1], wristPos[2], arm_ik_handle[1] + ".scalePivot",
                      arm_ik_handle[1] + ".rotatePivot")
            armCtrl = AutoRig.create_arm_control(side=side, control='handIkControl', joint=jtList[4],
                                                 ikHandle=arm_ik_handle[0],
                                                 scale=scale,
                                                 ulnaJoint=jtList[3], locAttributes=['sx', 'sy', 'sz', 'v'],
                                                 jointRotateOrder=1, controlRotateOrder=1, doNotTouchRotateOrder=1)
        else:
            armCtrl = AutoRig.create_arm_control(side=side, control='handIkControl', joint=jtList[3],
                                                 ikHandle=arm_ik_handle[0],
                                                 scale=scale, locAttributes=['sx', 'sy', 'sz', 'v'],
                                                 jointRotateOrder=1, controlRotateOrder=1, doNotTouchRotateOrder=1)

        elbowCtrl = AutoRig.create_pole_vector_control(side=side, joint=jtList[2], bodyPart='elbow',
                                                       ikHandle=arm_ik_handle[0],
                                                       locAttributes=['rx', 'rz', 'ry', 'sx', 'sy', 'sz', 'v'],
                                                       scale=scale)

        ikFootCtrlGrp = cmds.group(elbowCtrl, armCtrl[0], name=side + "_ik_arm_grp")

        if side == 'l':
            cmds.parent(ikFootCtrlGrp, 'LEFT')
        if side == 'r':
            cmds.parent(ikFootCtrlGrp, 'RIGHT')

        cmds.parent(armCtrl[1], 'DO_NOT_TOUCH')
        cmds.parent(jtList[0], 'ikFk_armJt_doNotTouch')
        return armCtrl, elbowCtrl, ikFootCtrlGrp

    @staticmethod
    def fk_switch_control(**kwargs):
        bind_list = kwargs.setdefault("bindSkeletonList")
        ik_list = kwargs.setdefault("ikSkeletonList")
        fk_list = kwargs.setdefault("fkSkeletonList")
        part = kwargs.setdefault('bodyPart')
        scale = kwargs.setdefault('scale')
        side = kwargs.setdefault('side')
        fk_controls = kwargs.setdefault('fkControls')
        ik_controls = kwargs.setdefault('ikControls')
        ulna = cmds.checkBox('reRig_autoRigUlna', q=True, value=True)
        num = 0

        constraint_control = None
        if part == 'leg':
            constraint_control = AutoRig.create_constraint_control(joint=bind_list[-3], bodyPart=part,
                                                                   locAttributes=['tx', 'ty', 'tz', 'rx', 'ry',
                                                                                  'rz', 'sx', 'sy', 'sz', 'v'],
                                                                   scale=scale, side=side)
        elif part == 'arm':
            constraint_control = AutoRig.create_constraint_control(joint=bind_list[-2], bodyPart=part,
                                                                   locAttributes=['tx', 'ty', 'tz', 'rx', 'ry',
                                                                                  'rz', 'sx', 'sy', 'sz', 'v'],
                                                                   scale=scale, side=side)

        ikFkSwitchBleCol = cmds.shadingNode('blendColors', asUtility=True, name=side + "_" + part + "IkFkSwitch_bleCol")
        cmds.setAttr(ikFkSwitchBleCol + ".color2G", 1)
        cmds.connectAttr(constraint_control[1], ikFkSwitchBleCol + ".blender")

        if part == 'arm':
            cmds.orientConstraint(fk_list[0], ik_list[0], skip="none", maintainOffset=False)
            cmds.orientConstraint(fk_list[0], bind_list[0], skip="none", maintainOffset=False)
            num = 1

        for n in range(num, len(bind_list)):
            if n == 3 and ulna is True and part == 'arm':
                parCon = cmds.orientConstraint(ik_list[n], fk_list[n], bind_list[n], skip=['y', 'z'],
                                               maintainOffset=False)
            elif n == 4 and ulna is True and part == 'arm':
                parCon = cmds.orientConstraint(ik_list[n], fk_list[n], bind_list[n], skip=['x'], maintainOffset=False)
            else:
                parCon = cmds.orientConstraint(ik_list[n], fk_list[n], bind_list[n], skip="none", maintainOffset=False)
            constrainAttr = cmds.listAttr(parCon, r=True, st='*jt*')
            cmds.connectAttr(ikFkSwitchBleCol + ".outputG", parCon[0] + "." + constrainAttr[0])
            cmds.connectAttr(ikFkSwitchBleCol + ".outputR", parCon[0] + "." + constrainAttr[1])

        for constraint_control in fk_controls:
            cmds.connectAttr(ikFkSwitchBleCol + ".outputR", constraint_control + ".visibility")
        cmds.connectAttr(ikFkSwitchBleCol + ".outputG", ik_controls + ".visibility")

    @staticmethod
    def create_finger_joint(**kwargs):
        joint = kwargs.setdefault("joint")
        side = kwargs.setdefault("side")
        scale = kwargs.setdefault("scale")
        finger = kwargs.setdefault("finger")
        parent_joint = kwargs.setdefault("parentJoint")
        cmds.select(joint, hierarchy=True)
        joint_list = cmds.ls(selection=True)

        joint_pos_list = []
        new_joint_temp_list = []
        main_skeleton_list = []
        delete_list = []
        main_skeleton_list.append(parent_joint)

        for joint in joint_list:
            jointPos = cmds.joint(joint, q=True, position=True)
            joint_pos_list.append(jointPos)

        length = len(joint_list) - (len(joint_list) / 2)
        for n in range(int(length)):
            cmds.select(parent_joint)
            joint = cmds.joint(name=side + '_' + finger + str(n + 1) + 'Temp_jt',
                               position=(joint_pos_list[n][0], joint_pos_list[n][1], joint_pos_list[n][2]))
            new_joint_temp_list.append([joint, joint_list[-n - 1]])
            delete_list.append(joint)

            if n != 0:
                cmds.aimConstraint(joint, new_joint_temp_list[n - 1][0], maintainOffset=False,
                                   aimVector=[1, 0, 0],
                                   upVector=[0, 1, 0],
                                   worldUpType='object',
                                   worldUpObject=new_joint_temp_list[n - 1][1])
                cmds.select(new_joint_temp_list[n - 1][0])

                if finger == 'pinky' or finger == 'thumb':
                    if finger == 'pinky' and n == 1:
                        pos = joint_pos_list[n - 1]
                        bn = cmds.joint(name=side + '_outerHand_bn', position=(pos[0], pos[1], pos[2]))
                    elif finger == 'thumb' and n == 1:
                        pos = joint_pos_list[n - 1]
                        bn = cmds.joint(name=side + '_innerHand_bn', position=(pos[0], pos[1], pos[2]))
                    else:
                        pos = joint_pos_list[n - 1]
                        bn = cmds.joint(name=side + '_' + finger + str(n - 1) + '_bn',
                                        position=(pos[0], pos[1], pos[2]))
                else:
                    pos = joint_pos_list[n - 1]
                    bn = cmds.joint(name=side + '_' + finger + str(n) + '_bn', position=(pos[0], pos[1], pos[2]))
                cmds.parent(bn, main_skeleton_list[n - 1])
                main_skeleton_list.append(bn)

        cmds.delete(delete_list)
        fk = AutoRig.fk_setup(side=side, jointList=main_skeleton_list[1:],
                              bodyPart=finger, scale=scale,
                              parentJoints=False, useAllJoints=True)
        return main_skeleton_list[1:], fk[2]

    @staticmethod
    def create_temporary_skeleton_control(**kwargs):
        scale = kwargs.setdefault('scale', 1)
        name = kwargs.setdefault('name')
        ctrl = cmds.circle(name=name, normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
        cmds.scale(5, 5, 5, ctrl)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        cmds.scale(scale, scale, scale, ctrl)
        cmds.makeIdentity(apply=True, t=1, r=1, s=1, n=0)
        return ctrl

    @staticmethod
    def create_pole_vector_control(**kwargs):
        side = kwargs.setdefault("side")
        joint = kwargs.setdefault("joint")
        part = kwargs.setdefault('bodyPart')
        ik_handle = kwargs.setdefault('ikHandle')
        loc_attr = kwargs.setdefault('locAttributes')
        scale = kwargs.setdefault('scale')
        group = cmds.group(empty=True, name=side + '_' + part + '_ctrlGrp')
        space_constraint = cmds.pointConstraint(joint, group, maintainOffset=False, skip="none")[0]
        cmds.delete(space_constraint)

        ctrl = cmds.curve(name=side + "_ik_" + part + "_ctrl", degree=3,
                          point=[(0, 0, 0), (0, 0.25, 0), (-0.5, 0.25, 0),
                                 (-0.5, -0.5, 0), (0.5, -0.5, 0), (0.5, 0.5, 0),
                                 (-0.3, 0.5, 0)],
                          knot=[0, 0, 0, 1, 2, 3, 4, 4, 4])
        cmds.parent(ctrl, group, r=True)
        cmds.scale(scale, scale, scale, group)
        cmds.poleVectorConstraint(ctrl, ik_handle)

        for attr in loc_attr:
            cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
        return group

    @staticmethod
    def create_arm_control(**kwargs):
        side = kwargs.setdefault("side")
        joint = kwargs.setdefault("joint")
        ulna_jt = kwargs.setdefault("ulnaJoint")
        ik_handle = kwargs.setdefault('ikHandle')
        loc_attr = kwargs.setdefault('locAttributes')
        scale = kwargs.setdefault('scale')
        joint_rotate_order = kwargs.setdefault('jointRotateOrder', 0)
        control_rotate_order = kwargs.setdefault('controlRotateOrder', 0)
        do_not_touch_rotate_order = kwargs.setdefault('doNotTouchRotateOrder', 0)

        ctrl = cmds.curve(name=side + "_ik_hand_ctrl", degree=1,
                          point=[(-0.14, 0.41, 0.65), (1.57, 0.41, 0.77), (1.57, -0.69, 0.77),
                                 (-0.14, -0.69, 0.65), (-0.14, 0.41, 0.65), (-0.14, 0.41, -0.78),
                                 (-0.14, -0.69, -0.78), (-0.14, -0.69, 0.65), (-0.14, -0.69, -0.78),
                                 (1.51, -0.69, -0.91), (1.57, -0.69, 0.77), (1.57, 0.41, 0.77),
                                 (1.51, 0.40, -0.91), (-0.14, 0.41, -0.78), (1.51, 0.40, -0.91),
                                 (1.51, -0.69, -0.91)],
                          knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        if side == 'r':
            cmds.scale(-1, 1, 1, ctrl)
            cmds.makeIdentity(ctrl, apply=True, scale=True)

        ik_arm_do_not_touch = cmds.group(name=side + "_ik_hand_doNotTouch", empty=True)
        spaceLoc = cmds.spaceLocator(name=side + '_ik_hand_space')[0]
        cmds.parent(spaceLoc, ik_arm_do_not_touch, relative=True)

        cmds.setAttr(ctrl + ".rotateOrder", control_rotate_order)
        cmds.setAttr(joint + ".rotateOrder", joint_rotate_order)
        cmds.setAttr(spaceLoc + ".rotateOrder", do_not_touch_rotate_order)
        cmds.setAttr(ik_arm_do_not_touch + ".rotateOrder", do_not_touch_rotate_order)

        group = cmds.group(empty=True, name=side + "_ik_hand_ctrlGrp")
        space_constraint = cmds.parentConstraint(joint, group, maintainOffset=False)
        cmds.delete(space_constraint)
        cmds.parent(ctrl, group, r=True)
        cmds.scale(scale, scale, scale, group)

        cmds.parentConstraint(ctrl, ik_arm_do_not_touch, maintainOffset=False)
        cmds.parent(ik_handle, ik_arm_do_not_touch)

        if cmds.checkBox('reRig_autoRigUlna', q=True, value=True) is True:
            cmds.orientConstraint(spaceLoc, ulna_jt, skip=['y', 'z'], maintainOffset=True)
            cmds.orientConstraint(spaceLoc, joint, skip='x', maintainOffset=False)
        else:
            cmds.orientConstraint(spaceLoc, joint, skip='none', maintainOffset=False)

        for attr in loc_attr:
            cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
        return group, ik_arm_do_not_touch

    @staticmethod
    def create_foot_control(**kwargs):
        side = kwargs.setdefault("side")
        joint = kwargs.setdefault("joint")
        ik_handle = kwargs.setdefault('ikHandle')
        loc_attr = kwargs.setdefault('locAttributes')
        scale = kwargs.setdefault('scale')
        aim_joint = kwargs.setdefault('aimJoint')
        add_attr = kwargs.setdefault('addAttributes')

        ret = cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true'
        if ret and side == 'r':
            cmds.mirrorJoint('l_hip_tempJt', mirrorBehavior=True, mirrorYZ=True, searchReplace=('l_', 'r_'))
            mel.eval('searchReplaceNames "1" "" "hierarchy";')

        ankle_pos = cmds.joint(joint, q=True, p=True, a=True)
        heel_pos = cmds.joint(side + '_heelFoot_tempJt', q=True, p=True, a=True)
        scaleY = ankle_pos[1] - heel_pos[1]

        ctrl = cmds.curve(name=side + "_ik_foot_ctrl", degree=1,
                          point=[(-0.9, -0.4, 2.4), (-0.9, -0.4, 2.4), (-0.9, -1.2, 2.6),
                                 (0.7, -1.2, 2.6), (0.7, -0.4, 2.4), (-0.9, -0.4, 2.4),
                                 (-1, 0.1, -1), (1, 0.1, -1), (0.7, -0.4, 2.4),
                                 (0.7, -1.2, 2.6), (1, -1.2, -1.2), (1, 0.1, -1),
                                 (1, -1.2, -1.2), (-1, -1.2, -1.2), (-1, 0.1, -1),
                                 (-1, -1.2, -1.2), (-0.9, -1.2, 2.6)],
                          knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

        group = cmds.group(empty=True, name=side + "_ik_foot_ctrlGrp")
        space_constraint = cmds.pointConstraint(joint, group, maintainOffset=False, skip="none")
        cmds.delete(space_constraint)
        cmds.parent(ctrl, group, r=True)

        cmds.scale(scale, scaleY / 1.2, scale, group)
        cmds.makeIdentity(group, apply=True, scale=True)
        space_constraint = cmds.aimConstraint(aim_joint, group, aimVector=(0.0, 0.0, 1.0), skip=["x", "z"])
        cmds.delete(space_constraint)

        ik_foot_do_not_touch = cmds.group(name=side + "_ik_foot_doNotTouch", empty=True)
        cmds.parentConstraint(ctrl, ik_foot_do_not_touch, maintainOffset=False, skipTranslate="none", skipRotate="none")
        on_heel = cmds.group(name=side + "_ik_onHell_negRX", empty=True, parent=ik_foot_do_not_touch)
        space_constraint = cmds.pointConstraint(side + '_heelFoot_tempJt', on_heel)
        cmds.delete(space_constraint)
        on_toe = cmds.group(name=side + "_ik_onToe_posRX", empty=True, parent=on_heel)
        space_constraint = cmds.pointConstraint(side + '_toeEnd_tempJt', on_toe)
        cmds.delete(space_constraint)

        outer_bank = None
        if side == 'l':
            outer_bank = cmds.group(name=side + "_ik_outerBank_negRZ", empty=True, parent=on_toe)
        elif side == 'r':
            outer_bank = cmds.group(name=side + "_ik_outerBank_posRZ", empty=True, parent=on_toe)
        space_constraint = cmds.pointConstraint(side + '_footOuter_tempJt', outer_bank)
        cmds.delete(space_constraint)

        inner_bank = None
        if side == 'l':
            inner_bank = cmds.group(name=side + "_ik_innerBank_posRZ", empty=True, parent=outer_bank)
        elif side == 'r':
            inner_bank = cmds.group(name=side + "_ik_innerBank_negRZ", empty=True, parent=outer_bank)
        space_constraint = cmds.pointConstraint(side + '_footInner_tempJt', inner_bank)
        cmds.delete(space_constraint)

        toe_flip = cmds.group(name=side + "_ik_toeFlip_negRX", empty=True, parent=inner_bank)
        space_constraint = cmds.pointConstraint(side + '_toe_tempJt', toe_flip)
        cmds.delete(space_constraint)

        on_ball = cmds.group(name=side + "_ik_onBall_posRX", empty=True, parent=inner_bank)
        space_constraint = cmds.pointConstraint(side + '_toe_tempJt', on_ball)
        cmds.delete(space_constraint)
        cmds.parent(ik_handle[0], on_ball)
        cmds.parent(ik_handle[1], inner_bank)
        cmds.parent(ik_handle[2], toe_flip)

        for attr in loc_attr:
            cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)

        for attr in add_attr:
            cmds.addAttr(ctrl, longName=attr, attributeType='float', keyable=True)

        multiply_divide = cmds.shadingNode('multiplyDivide', name=side + '_ik_foot_mulDiv', asUtility=True)
        cmds.setAttr(multiply_divide + '.input2X', -1)
        cmds.setAttr(multiply_divide + '.input2Y', -1)
        cmds.setAttr(multiply_divide + '.input2Z', -1)

        if 'onToe' in add_attr:
            cmds.connectAttr(ctrl + '.onToe', on_toe + '.rx')
        if 'onHeel' in add_attr:
            cmds.connectAttr(ctrl + '.onHeel', multiply_divide + '.input1X')
            cmds.connectAttr(multiply_divide + '.outputX', on_heel + '.rx')
        if side == 'l':
            if 'outerBank' in add_attr:
                cmds.connectAttr(ctrl + '.outerBank', multiply_divide + '.input1Y')
                cmds.connectAttr(multiply_divide + '.outputY', outer_bank + '.rz')
            if 'innerBank' in add_attr:
                cmds.connectAttr(ctrl + '.innerBank', inner_bank + '.rz')
        elif side == 'r':
            if 'outerBank' in add_attr:
                cmds.connectAttr(ctrl + '.outerBank', outer_bank + '.rz')
            if 'innerBank' in add_attr:
                cmds.connectAttr(ctrl + '.innerBank', multiply_divide + '.input1Y')
                cmds.connectAttr(multiply_divide + '.outputY', inner_bank + '.rz')
        if 'onBall' in add_attr:
            cmds.connectAttr(ctrl + '.onBall', on_ball + '.rx')
        if 'toeFlip' in add_attr:
            cmds.connectAttr(ctrl + '.toeFlip', multiply_divide + '.input1Z')
            cmds.connectAttr(multiply_divide + '.outputZ', toe_flip + '.rx')

        ret = cmds.radioCollection('ReRig_mirrorTempSkeleton', q=True, select=True) == 'ReRig_mirrorTempSkeleton_true'
        if ret and side == 'r':
            cmds.delete('r_hip_tempJt')
        return group, ik_foot_do_not_touch

    @staticmethod
    def create_shoulder_hip_control(**kwargs):
        joint = kwargs.setdefault("joint")
        part = kwargs.setdefault("bodyPart")
        loc_attr = kwargs.setdefault('locAttributes')
        scale = kwargs.setdefault('scale')
        rotation_order = kwargs.setdefault('rotationOrder', 'xyz')

        ctrl = None
        if part == "shoulder":
            ctrl = cmds.curve(name="c_ik_shoulder_ctrl", degree=1,
                              point=[(2.3, -0.3, 1.6), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3),
                                     (-2.3, -0.3, 1.6), (2.3, -0.3, 1.6),
                                     (2.5, -2.7, 1.9), (-2.5, -2.7, 1.9), (-2.5, -2.7, -1.9),
                                     (2.5, -2.7, -1.9), (2.5, -2.7, 1.9),
                                     (2.5, -2.7, -1.9), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3),
                                     (-2.5, -2.7, -1.9), (-2.5, -2.7, 1.9), (-2.3, -0.3, 1.6)],
                              knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
        elif part == "hip":
            ctrl = cmds.curve(name="c_ik_hip_ctrl", degree=1,
                              point=[(-2.5, 0.6, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9),
                                     (-2.5, 0.6, -1.9), (-2.5, 0.6, 1.9),
                                     (-2.5, -2.1, 1.9), (2.5, -2.1, 1.9), (2.5, 0.6, 1.9),
                                     (2.5, 0.6, -1.9), (2.5, -2.1, -1.9),
                                     (2.5, -2.1, 1.9), (-2.5, -2.1, 1.9), (-2.5, -2.1, -1.9),
                                     (-2.5, 0.6, -1.9), (-2.5, -2.1, -1.9), (2.5, -2.1, -1.9)],
                              knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])

        cmds.setAttr(ctrl + '.ry', 90)
        cmds.setAttr(ctrl + '.rx', 90)
        cmds.makeIdentity(ctrl, apply=True, rotate=True)

        group = cmds.group(name="c_ik_" + part + "_ctrlGrp", empty=True)
        space_constraint = cmds.parentConstraint(joint, group, maintainOffset=False)
        cmds.delete(space_constraint)
        cmds.parent(ctrl, group, r=True)
        cmds.scale(scale, scale, scale, group)

        do_not_touch = cmds.group(name='c_ik_' + part + '_doNotTouch', empty=True)
        cmds.parentConstraint(ctrl, do_not_touch, maintainOffset=False)
        spaceLoc = cmds.spaceLocator(name='c_ik_' + part + '_space')
        cmds.parent(spaceLoc, do_not_touch, relative=True)
        cmds.setAttr(spaceLoc[0] + '.tz', -0.5 * scale)
        cmds.parent(joint, do_not_touch)
        cmds.xform(ctrl, rotateOrder=rotation_order)
        for attr in loc_attr:
            cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
        return group, do_not_touch, spaceLoc[0], ctrl

    @staticmethod
    def create_pelvis_control(**kwargs):
        joint = kwargs.setdefault("joint")
        loc_attr = kwargs.setdefault('locAttributes')
        scale = kwargs.setdefault('scale')
        rotation_order = kwargs.setdefault('rotationOrder', 'xyz')

        group = cmds.group(empty=True, name='c_pelvis_ctrlGrp')
        space_constraint = cmds.parentConstraint(joint, group)
        cmds.delete(space_constraint)
        cmds.scale(scale, scale, scale, group)

        ctrl = cmds.circle(name='c_pelvis_ctrl', normal=(0, 1, 0), center=(0, 0, 0), ch=True, radius=1)[0]
        cmds.parent(ctrl, group, r=True)
        cmds.select(ctrl + '.cv[1]', ctrl + '.cv[3]', ctrl + '.cv[5]', ctrl + '.cv[7]')
        cmds.scale(-3, -3, -3)
        cmds.setAttr(ctrl + '.ty', -2)
        cmds.scale(0.7, 0.7, 0.7, ctrl)
        cmds.makeIdentity(ctrl, apply=True, scale=True, t=True)
        cmds.xform(ctrl, rotateOrder=rotation_order)
        for attr in loc_attr:
            cmds.setAttr(ctrl + '.' + attr, lock=True, keyable=False, channelBox=False)
        cmds.orientConstraint(ctrl, joint, skip='none', maintainOffset=False)
        return ctrl, group

    @staticmethod
    def create_constraint_control(**kwargs):
        joint = kwargs.setdefault("joint")
        part = kwargs.setdefault("bodyPart")
        locAttr = kwargs.setdefault('locAttributes')
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
                          point=[(0, 0.65, 0), (0, 0, 0), (-1, 0, 0),
                                 (0, 0, 0), (0, -1, 0), (0, 0, 0),
                                 (1, 0, 0), (0, 0, 0), (0, 0.65, 0)],
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

    @staticmethod
    def clean_list_tostring(**kwargs):
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
