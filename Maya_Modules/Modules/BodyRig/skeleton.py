# -*- coding: utf-8 -*-

import maya.cmds as cmds
import random
import math


class SkeletonB(object):

    def __CreateSpineSkeleton__(self):
        self.HipJoint = cmds.joint(name='A_Hip_Jt', position=(0.008, 4.451, 0))
        cmds.joint('A_Hip_Jt', edit=True, zso=True, oj='xyz')

        numJt = range(4)
        jtPosX = 0.08
        jtPosY = 0.05
        for joints in numJt:
            extraStrJt = "Hip_Jt_"
            extraJt = cmds.joint(name=extraStrJt + str(joints), position=(0.008, 4.451, 0))
            cmds.joint(extraStrJt + str(joints), edit=True, zso=True, oj='xyz')
            cmds.select(extraStrJt + str(joints))
            jointList = cmds.ls(selection=True)
            if joints:
                jtPosY += 0.18
                jtPosX += -0.08
                cmds.select(extraStrJt + str(joints))
                cmds.move(0.3, 0.0, 0.0)
                cmds.move(joints * 0.008 - 0.2, 4.751 + joints * jtPosY, 0, extraStrJt + str(joints), absolute=True)

        cmds.move(jtPosX, 4.451 + 0.9 * 2, 0)

        self.NeckJoint = cmds.joint(name='D_Neck_Jt', position=(-0.089, 6.965, 0))
        cmds.joint('D_Neck_Jt', edit=True, zso=True, oj='xyz')

        self.HeadJoint = cmds.joint(name='E_Head_Jt', position=(-0.026, 7.306, 0))
        cmds.joint('E_Head_Jt', edit=True, zso=True, oj='xyz')

        self.HeadTipJoint = cmds.joint(name='F_HeadTip_Jt', position=(-0.015, 8.031, 0))
        cmds.select('A_Hip_Jt')
        cmds.joint(name='A_LowerHip_Jt', position=(-0.023, 4.327, 0))
        cmds.select("Hip_Jt_0")
        cmds.move(-0.008, 4.701, 0)
        cmds.select('A_Hip_Jt')

    def __CreateSkeletonLeg__(self):
        self.L_HipJoint = cmds.joint(name='L_Hip_Jt', position=(-0.12, 4.369, -0.689))
        cmds.select('L_Hip_Jt')
        self.L_KneeJoint = cmds.joint(name='L_Knee_Jt', position=(0.2, 2.36, -0.689))
        cmds.select('L_Knee_Jt')
        cmds.joint('L_Hip_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_AnkleJoint = cmds.joint(name='L_Ankle_Jt', position=(-0.24, 0.486, -0.689))
        cmds.joint('L_Knee_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.joint('L_Ankle_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_ToeJoint = cmds.joint(name='L_Toe_Jt', position=(0.32, 0.051, -0.689))
        self.L_ToeEndJoint = cmds.joint(name='L_ToeEnd_Jt', position=(0.69, 0.062, -0.689))
        cmds.joint('L_Toe_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def __CreateSkeletonArm__(self):
        cmds.select('D_Neck_Jt')
        self.L_CollarBoneJoint = cmds.joint(name='L_Collarbone_Jt', position=(-0.233, 6.565, -0.793))
        self.L_ShoulderJoint = cmds.joint(name='L_Shoulder_Jt', position=(0, 6.749, -1.31))
        cmds.joint('L_Collarbone_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_ElbowJoint = cmds.joint(name='L_Elbow_Jt', position=(0, 5.773, -2.092))
        cmds.joint('L_Shoulder_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_WristJoint = cmds.joint(name='L_Wrist_Jt', position=(0.503, 5.126, -2.82))
        cmds.joint('L_Elbow_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_MiddleHandJoint = cmds.joint(name='L_MiddleHand_Jt', position=(0.641, 4.961, -2.963))
        cmds.joint('L_Wrist_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.select('L_Wrist_Jt')

    def __CreateSkeletonFingers__(self):
        # Thumb
        self.L_Thumb01Joint = cmds.joint(name='L_Thumb01_Jt', position=(0.782, 4.973, -2.855))
        self.L_Thumb02Joint = cmds.joint(name='L_Thumb02_Jt', position=(0.895, 4.867, -2.855))
        cmds.joint('L_Thumb01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_Thumb03Joint = cmds.joint(name='L_Thumb03_Jt', position=(0.938, 4.79, -2.855))
        cmds.joint('L_Thumb02_Jt', edit=True, zso=True, oj='xyz', sao='yup')

        # Index
        cmds.select('L_Wrist_Jt')
        self.L_IndexFinger01Joint = cmds.joint(name='L_IndexFinger01_Jt', position=(0.749, 4.841, -3.093))
        self.L_IndexFinger02Joint = cmds.joint(name='L_IndexFinger02_Jt', position=(0.816, 4.697, -3.159))
        cmds.joint('L_IndexFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_IndexFinger03Joint = cmds.joint(name='L_IndexFinger03_Jt', position=(0.849, 4.568, -3.19))
        cmds.joint('L_IndexFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_IndexFinger04Joint = cmds.joint(name='l_indexFinger04_Jt', position=(0.861, 4.484, -3.198))
        cmds.joint('L_IndexFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

        # Middle
        cmds.select('L_Wrist_Jt')
        self.L_MiddleFinger01Joint = cmds.joint(name='L_MiddleFinger01_Jt', position=(0.637, 4.833, -3.183))
        self.L_MiddleFinger02Joint = cmds.joint(name='L_MiddleFinger02_Jt', position=(0.682, 4.703, -3.276))
        cmds.joint('L_MiddleFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_MiddleFinger03Joint = cmds.joint(name='L_MiddleFinger03_Jt', position=(0.702, 4.554, -3.322))
        cmds.joint('L_MiddleFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_MiddleFinger04Joint = cmds.joint(name='L_MiddleFinger04_Jt', position=(0.711, 4.441, -3.334))
        cmds.joint('L_MiddleFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

        # Ring
        cmds.select('L_Wrist_Jt')
        self.L_RingFinger01Joint = cmds.joint(name='L_RingFinger01_Jt', position=(0.488, 4.827, -3.25))
        self.L_RingFinger02Joint = cmds.joint(name='L_RingFinger02_Jt', position=(0.528, 4.713, -3.31))
        cmds.joint('L_RingFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_RingFinger03Joint = cmds.joint(name='L_RingFinger03_Jt', position=(0.541, 4.584, -3.354))
        cmds.joint('L_RingFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_RingFinger04Joint = cmds.joint(name='L_RingFinger04_Jt', position=(0.546, 4.49, -3.361))
        cmds.joint('L_RingFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

        # Pinky
        cmds.select('L_Wrist_Jt')
        self.L_Pinky01Joint = cmds.joint(name='L_Pinky01_tJt', position=(0.362, 4.818, -3.251))
        self.L_Pinky02Joint = cmds.joint(name='L_Pinky02_Jt', position=(0.375, 4.73, -3.283))
        cmds.joint('L_Pinky01_tJt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_Pinky03Joint = cmds.joint(name='L_Pinky03_Jt', position=(0.38, 4.617, -3.329))
        cmds.joint('L_Pinky02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.L_Pinky04Joint = cmds.joint(name='L_Pinky04_Jt', position=(0.385, 4.534, -3.341))
        cmds.joint('L_Pinky03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def __CreateFingerCtrl_(**kwargs):
        joints = kwargs.setdefault("joints")

        for jt in joints:
            cmds.select(jt, hierarchy=True)
            jointList = cmds.ls(selection=True)

            for joint in jointList[:-2]:
                pos = cmds.joint(joint, q=True, position=True)
                nameSplit = joint.rsplit('_', 1)
                name = nameSplit[0]
                cmds.select(joint)
                cmds.joint(name=name + 'Up_Jt', position=(pos[0] + 0.01, pos[1] + 0.05, pos[2] - 0.06))

    def __MirrorJointsHands__(self, **kwargs):
        cmds.select('D_Neck_Jt')
        self.MirrorEachJoint = cmds.mirrorJoint('L_Collarbone_Jt', mirrorXY=True, mirrorBehavior=True,
                                                searchReplace=('L_', 'R_'))

    def __MirrorJointsLegs__(self, **kwargs):
        cmds.select('A_LowerHip_Jt')
        self.MirrorEachJoint = cmds.mirrorJoint('L_Hip_Jt', mirrorXY=True, mirrorBehavior=True,
                                                searchReplace=('L_', 'R_'))
        slBone = cmds.select('A_Hip_Jt')

    def __create__(self, **kwargs):
        skeletonJT = SkeletonB()
        skeletonJT.__CreateSpineSkeleton__()
        skeletonJT.__CreateSkeletonLeg__()
        skeletonJT.__CreateSkeletonArm__()
        skeletonJT.__CreateSkeletonFingers__()
        skeletonJT.__MirrorJointsHands__()
        skeletonJT.__MirrorJointsLegs__()
