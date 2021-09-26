# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
from functools import partial

"""
import animal_rig
import importlib
importlib.reload(animal_rig)
window = animal_rig.AutoRig_OptionsWindow()
window.create()
"""


class generate_rig_window(object):

    def __init__(self):
        self.window = 'ar_optionsWindow'
        self.title = 'Auto Rigging Tool'
        self.size = (340, 700)
        self.supportsToolAction = True

    def create(self):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True)
        self.window = mc.window(
            self.window,
            title=self.title,
            widthHeight=self.size,
            menuBar=True
        )
        self.commonMenu()
        mc.showWindow()

    def commonMenu(self):
        self.editMenu = mc.menu(label='Edit')
        self.editMenuDiv = mc.menuItem(d=True)
        self.editMenuskelRadio = mc.radioMenuItemCollection()
        self.editMenuTool = mc.menuItem(
            label='As Tool',
            radioButton=True,
            enable=self.supportsToolAction,
            command=self.editMenuToolCmd
        )
        self.helpMenu = mc.menu(label='Help')
        self.helpMenuItem = mc.menuItem(label='Help on %s' % self.title, command=self.helpMenuCmd)

        mc.columnLayout(columnAttach=('both', 2), rowSpacing=4, columnWidth=340)
        mc.text("QUADRUPED CHARACTER", align="center")
        mc.text("")
        mc.text("Step 1: Create quadruped skeleton")
        self.buttonSkelQuad = mc.button(label='Quadruped Skeleton',
                                        command=self.skeletonButton_Q,
                                        width=120, height=40)

        mc.text("  ")
        mc.text("Step 2: Create Legs control")
        mc.text("____________________________________")
        mc.text(label='REAR BODY CONTROL', align='center')
        buttonMirrorJoints = mc.button(label='Mirror Joints',
                                       command=self.MirrorJoints,
                                       width=120, height=40)
        buttonRigFrontLegsCtrl = mc.button(label='Front Legs Control',
                                           command=self.Front_Legs_Control,
                                           width=120, height=40)
        buttonRigRearLegsCtrl = mc.button(label='Rear Legs Control',
                                          command=self.Rear_Legs_Control,
                                          width=120, height=40)
        buttonRigSpineCtrl = mc.button(label='Spine Control',
                                       command=self.Spine_Control,
                                       width=120, height=40,
                                       align="center")

        mc.text("  ")
        mc.text("Step 3: Create Neck/Head controls")
        mc.text("__________________________________")
        mc.text(label='FRONT BODY CONTROL', align='center')
        buttonRigNeckCtrl = mc.button(label='Neck Control',
                                      command=self.Neck_Control,
                                      width=120, height=40)
        buttonRigHeadCtrl = mc.button(label='Head Control',
                                      command=self.Head_Control,
                                      width=120, height=40)
        buttonRigJawCtrl = mc.button(label="Jaw Control",
                                     command=self.Jaw_Control,
                                     width=120, height=40)
        buttonRigTongueCtrl = mc.button(label="Tongue Control",
                                        command=self.Tongue_Control,
                                        width=120, height=40)

        mc.text("   ")
        mc.text("Step 4: Create Tail Control")
        buttonRigTailCtrl = mc.button(label="Tail Control",
                                      command=self.Tail_Control,
                                      width=120, height=40)
        mc.text("   ")
        mc.text("Step 5: Create Master control")
        mc.text(label='MASTER CONTROL', align='center')
        buttonMainCtrl = mc.button(label='Master Control',
                                   command=self.Master_Control,
                                   width=120, height=40,
                                   align='center')
        closeButton = mc.button(label="Close",
                                command=self.closeWindow,
                                width=120, height=40,
                                align='center')

    def closeWindow(self, *args):
        if mc.window(self.window, exists=True):
            mc.deleteUI(self.window, window=True);

    def skeletonButton_Q(*args, **kwargs):
        skeletonQT = animal_skeleton()
        skeletonQT.__CreateFrontLegsSkeleton__()
        skeletonQT.__CreateSpineSkeleton__()
        skeletonQT.__CreateBackLegsSkeleton__()
        skeletonQT.__Tail__()
        skeletonQT.__Head__()
        skeletonQT.__Jaw__()
        skeletonQT.__Ears__()
        skeletonQT.__Tongue__()

    def CreateMiddleLegsSkeleton(self, *args, **kwargs):
        mc.select("B03")
        self.M_PelvicJoint = mc.joint(name="L_Middle_Pelvis_Jt", position=(-0.037, 7.297, -1.41))
        mc.joint(name="L_Middle_Pelvis_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.M_KneeJoint = mc.joint(name="L_Middle_Knee_Jt", position=(0.411, 4.739, -1.487))
        mc.joint(name="L_Middle_Knee_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.M_HeelJoint = mc.joint(name="L_Middle_Heel_Jt", position=(-0.746, 2.537, -1.418))
        mc.joint(name="L_Middle_Heel_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.M_Toe01Joint = mc.joint(name="L_Middle_Toe01_Jt", position=(-0.634, 0.093, -1.432))
        mc.joint(name="L_Middle_Toe01_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.M_Toe02Joint = mc.joint(name="L_Middle_Toe02_Jt", position=(0.896, -0.093, -1.432))
        mc.joint(name="L_Middle_Toe02_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def MirrorJoints(self, *args):
        mc.select('A_Front_Hip_Jt')
        self.MirrorEachJoint = mc.mirrorJoint('L_Front_Shoulder_Jt', mirrorXY=True,
                                              mirrorBehavior=True,
                                              searchReplace=('L_', 'R_'))
        mc.select('B_Back_Hip_Jt')
        self.MirrorEachJoint = mc.mirrorJoint('L_Back_Pelvic_Jt', mirrorXY=True,
                                              mirrorBehavior=True,
                                              searchReplace=('L_', 'R_'))
        mc.select("Head_Jt")
        self.MirrorEachJoint = mc.mirrorJoint("L_Ear_Jt", mirrorXY=True,
                                              mirrorBehavior=True,
                                              searchReplace=("L_", "R_"))

    def helpMenuCmd(self, *args):
        mc.launch(web='http://www.maya-python.com/')

    def editMenuSaveCmd(self, *args):
        pass

    def editMenuResetCmd(self, *args):
        pass

    def editMenuToolCmd(self, *args):
        pass

    def editMenuActionCmd(self, *args):
        pass

    def Front_Legs_Control(*args, **kwargs):
        prefix_L = "L"
        prefix_R = "R"
        prefix = "_"
        Left_Foot = True
        Right_Foot = True
        Feet_Ctrl = [Left_Foot, Right_Foot]
        Feet_Ctrl[0] = [mc.curve(name=prefix_L + "_Front_Foot_Ctrl", degree=1,
                                 point=[(1.654147, -0.376619, 0.392),
                                        (1.654147, -0.376619, -0.391833),
                                        (0.471549, -0.376619, -0.640084),
                                        (-0.237383, -0.387065, -0.56856),
                                        (-0.80264, -0.294179, -0.326289),
                                        (-0.807391, -0.294179, 0.331393),
                                        (-0.242134, -0.387065, 0.622436),
                                        (0.466798, -0.376619, 0.664218),
                                        (1.654147, -0.376619, 0.392)],
                                 knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        mc.scale(1.4, 0.0, 1.5),
                        mc.setAttr(prefix_L + "_Front_Foot_Ctrl.overrideColor", 6),
                        mc.setAttr(prefix_L + "_Front_Foot_Ctrl.overrideEnabled", 1)]

        mc.makeIdentity(t=True, s=True, a=True, r=True)
        Ankle_Left = "L_Front_WristExtra_Jt"
        valFkLeft = mc.xform(Ankle_Left, query=True, ws=True, translation=True)
        mc.xform(Feet_Ctrl[0], ws=1, t=(valFkLeft[0], valFkLeft[1], valFkLeft[2]))

        Feet_Ctrl[1] = [mc.curve(name=prefix_R + "_Front_Foot_Ctrl", degree=1,
                                 point=[(1.654147, -0.376619, 0.392),
                                        (1.654147, -0.376619, -0.391833),
                                        (0.471549, -0.376619, -0.640084),
                                        (-0.237383, -0.387065, -0.56856),
                                        (-0.80264, -0.294179, -0.326289),
                                        (-0.807391, -0.294179, 0.331393),
                                        (-0.242134, -0.387065, 0.622436),
                                        (0.466798, -0.376619, 0.664218),
                                        (1.654147, -0.376619, 0.392)],
                                 knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        mc.scale(1.4, 0.0, -1.5),
                        mc.setAttr(prefix_R + "_Front_Foot_Ctrl.overrideColor", 3.5),
                        mc.setAttr(prefix_R + "_Front_Foot_Ctrl.overrideEnabled", 1)]

        Ankle_Right = "R_Front_WristExtra_Jt"
        valFkRight = mc.xform(Ankle_Right, query=True, ws=True, translation=True)
        mc.xform(Feet_Ctrl[1], ws=1, t=(valFkRight[0], valFkRight[1], valFkRight[2]))
        mc.makeIdentity(t=True, s=True, a=True, r=True)
        CurveWristsLeftCtrl = [mc.curve(name="L_Front_Feet_Ctrl", degree=1,
                                        point=[(-0.989704, 0, -0.00369912),
                                               (-0.310562, 0, -0.998289),
                                               (0.138488, 0, -0.990867),
                                               (-0.499831, 0, 0.0111455),
                                               (-0.0656259, 0, 1.009447),
                                               (-0.633433, 0, 1.013158),
                                               (-0.989704, 0, -0.00369912)],
                                        knot=[0, 1, 2, 3, 4, 5, 6]),
                               mc.scale(0.6, 0.6, 0.6),
                               mc.setAttr("L_Front_Feet_Ctrl.rotateX", 90, lock=True),
                               mc.setAttr("L_Front_Feet_Ctrl.scale", lock=True),
                               mc.setAttr("L_Front_Feet_Ctrl.overrideColor", 6),
                               mc.setAttr("L_Front_Feet_Ctrl.overrideEnabled", 1)]

        CurveWristsRightCtrl = [mc.curve(name="R_Front_Feet_Ctrl", degree=1,
                                         point=[(-0.989704, 0, -0.00369912),
                                                (-0.310562, 0, -0.998289),
                                                (0.138488, 0, -0.990867),
                                                (-0.499831, 0, 0.0111455),
                                                (-0.0656259, 0, 1.009447),
                                                (-0.633433, 0, 1.013158),
                                                (-0.989704, 0, -0.00369912)],
                                         knot=[0, 1, 2, 3, 4, 5, 6]),
                                mc.scale(0.6, 0.6, 0.6),
                                mc.setAttr("R_Front_Feet_Ctrl.rotateX", 90, lock=True),
                                mc.setAttr("R_Front_Feet_Ctrl.scale", lock=True),
                                mc.setAttr("R_Front_Feet_Ctrl.overrideColor", 3.5),
                                mc.setAttr("R_Front_Feet_Ctrl.overrideEnabled", 1)]
        Legs_Turn = ["FrontLeft", "FrontRight"]
        Legs_Ctrl = ["L_Front_Foot_Ctrl", "R_Front_Foot_Ctrl"]
        CurveFeetCtrl = [CurveWristsLeftCtrl, CurveWristsRightCtrl]

        # Left Side
        if Legs_Turn[0]:
            ikAnkle = mc.ikHandle(name="ikHandle_L_Front_Ctrl_Ankle",
                                  startJoint="L_Front_Shoulder_Jt",
                                  endEffector="L_Front_Wrist_Jt",
                                  solver="ikRPsolver", parentCurve=False)
            ikHeel = mc.ikHandle(name="ikHandle_L_Front_Ctrl_Heel",
                                 startJoint="L_Front_Wrist_Jt",
                                 endEffector="L_Front_WristExtra_Jt",
                                 solver="ikRPsolver", parentCurve=False)
            ikToe = mc.ikHandle(name="ikHandle_L_Front_Ctrl_Toe",
                                startJoint="L_Front_WristExtra_Jt",
                                endEffector="L_Front_Toe_Jt",
                                solver="ikRPsolver", parentCurve=False)
            grpIK_FrontLeft = mc.group("ikHandle_L_Front_Ctrl_Heel", "ikHandle_L_Front_Ctrl_Toe",
                                       n="GRP_Ik" + prefix + "ik_Front_Ctrl")

            # Parent feet controls
            AnkleLeft = "L_Front_Wrist_Jt"
            try:
                dist = 0.5
                setLoc = mc.xform(AnkleLeft, query=True, ws=True, translation=True)
                mc.xform(CurveFeetCtrl[0], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                mc.parent("ikHandle_L_Front_Ctrl_Ankle", "L_Front_Feet_Ctrl")

            except:
                mc.error("Wrong values!")
            mc.parent(grpIK_FrontLeft, Legs_Ctrl[0])
            sel = mc.ls(type="ikHandle")
            for ik in sel:
                mc.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = mc.spaceLocator(name="HelpLocs_" + str(j))
            heel = "L_Front_WristExtra_Jt"
            print(locs)
            if mc.ls("HelpLocs_0", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] - 1))
            if mc.ls("HelpLocs_1", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] + 1))
                sl = mc.ls(type="locator")
                for k in sl:
                    mc.setAttr("%s.visibility" % k, 0)
        grpLoc = mc.group("HelpLocs_0", "HelpLocs_1", n="GRP_Locs")

        # Parent under each foot's curves controls
        mc.parent(grpLoc, "ikHandle_L_Front_Ctrl_Heel")
        mc.parent("ikHandle_L_Front_Ctrl_Heel", "L_Front_Foot_Ctrl")
        mc.parent("L_Front_Feet_Ctrl", "L_Front_Foot_Ctrl")

        # Lock the scale attributes for both feet
        mc.setAttr(prefix_L + "_Front_Foot_Ctrl.scale", lock=True)
        mc.setAttr(prefix_R + "_Front_Foot_Ctrl.scale", lock=True)

        # Right Side
        if Legs_Turn[1]:
            ikAnkle = mc.ikHandle(name="ikHandle_R_Front_Ctrl_Ankle",
                                  startJoint="R_Front_Shoulder_Jt",
                                  endEffector="R_Front_Wrist_Jt",
                                  solver="ikRPsolver", parentCurve=False)
            ikHeel = mc.ikHandle(name="ikHandle_R_Front_Ctrl_Heel",
                                 startJoint="R_Front_Wrist_Jt",
                                 endEffector="R_Front_WristExtra_Jt",
                                 solver="ikRPsolver", parentCurve=False)
            ikToe = mc.ikHandle(name="ikHandle_R_Front_Ctrl_Toe",
                                startJoint="R_Front_WristExtra_Jt",
                                endEffector="R_Front_Toe_Jt",
                                solver="ikRPsolver", parentCurve=False)
            grpIK_FrontRight = mc.group("ikHandle_R_Front_Ctrl_Heel", "ikHandle_R_Front_Ctrl_Toe",
                                        n="GRP_Ik" + prefix + "ik_Front_Ctrl")

            # Parent feet controls
            AnkleRight = "R_Front_Wrist_Jt"
            try:
                dist = 0.5
                setLoc = mc.xform(AnkleRight, query=True, ws=True, translation=True)
                mc.xform(CurveFeetCtrl[1], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                mc.parent("ikHandle_R_Front_Ctrl_Ankle", "R_Front_Feet_Ctrl")

            except:
                mc.error("Wrong values!")
            mc.parent(grpIK_FrontRight, Legs_Ctrl[1])
            sel = mc.ls(type="ikHandle")
            for ik in sel:
                mc.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = mc.spaceLocator(name="HelpLocs_0" + str(j))
            heel = "R_Front_WristExtra_Jt"
            print(locs)
            if mc.ls("HelpLocs_00", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] - 1))
            if mc.ls("HelpLocs_01", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] + 1))
                sl = mc.ls(type="locator")
                for k in sl:
                    mc.setAttr("%s.visibility" % k, 0)
        grpLoc = mc.group("HelpLocs_00", "HelpLocs_01", n="GRP_Locs")
        mc.parent(grpLoc, "ikHandle_R_Front_Ctrl_Heel")
        mc.parent("ikHandle_R_Front_Ctrl_Heel", "R_Front_Foot_Ctrl")
        mc.parent("R_Front_Feet_Ctrl", "R_Front_Foot_Ctrl")

        # Knees
        Knee_L_Front_Jt = "L_Front_Elbow_Jt"
        Knee_R_Front_Jt = "R_Front_Elbow_Jt"
        # Left Knee Cap
        Knee_L_Front_Cap = [mc.curve(name=prefix_L + "_Elbow_Front_Cap", d=1,
                                     p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            mc.scale(0.2, 0.2, 0.2),
                            mc.setAttr(prefix_L + "_Elbow_Front_Cap.rotateZ", 90),
                            mc.setAttr(prefix_L + "_Elbow_Front_Cap.scale", lock=True),
                            mc.setAttr(prefix_L + "_Elbow_Front_Cap.scale", lock=True),
                            mc.setAttr(prefix_L + "_Elbow_Front_Cap.overrideColor", 6),
                            mc.setAttr(prefix_L + "_Elbow_Front_Cap.overrideEnabled", 1)]
        mc.xform(Knee_L_Front_Jt + ".tx", Knee_L_Front_Jt + ".ty", Knee_L_Front_Jt + ".tz")
        valKnee = mc.xform(Knee_L_Front_Jt, query=True, ws=True, translation=True)
        mc.xform(Knee_L_Front_Cap[0], ws=1, t=(valKnee[0] - 1.5, valKnee[1], valKnee[2]))
        mc.poleVectorConstraint(prefix_L + "_Elbow_Front_Cap", "ikHandle_L_Front_Ctrl_Ankle")
        mc.makeIdentity(t=True, a=True, r=True)

        # Right Knee Cap
        Knee_R_Front_Cap = [mc.curve(name=prefix_R + "_Elbow_Front_Cap", d=1,
                                     p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            mc.scale(0.2, 0.2, 0.2),
                            mc.setAttr(prefix_R + "_Elbow_Front_Cap.rotateZ", 90),
                            mc.setAttr(prefix_R + "_Elbow_Front_Cap.scale", lock=True),
                            mc.setAttr(prefix_R + "_Elbow_Front_Cap.overrideColor", 3.5),
                            mc.setAttr(prefix_R + "_Elbow_Front_Cap.overrideEnabled", 1)]
        mc.xform(Knee_R_Front_Jt + ".tx", Knee_R_Front_Jt + ".ty", Knee_R_Front_Jt + ".tz")
        valKnee = mc.xform(Knee_R_Front_Jt, query=True, ws=True, translation=True)
        mc.xform(Knee_R_Front_Cap[0], ws=1, t=(valKnee[0] - 1.5, valKnee[1], valKnee[2]))
        mc.poleVectorConstraint(prefix_R + "_Elbow_Front_Cap", "ikHandle_R_Front_Ctrl_Ankle")
        mc.makeIdentity(t=True, a=True, r=True)

        ShoulderChoice = [True, True]
        Shoulder_L_Jt = "L_Front_Shoulder_Jt"
        Shoulder_R_Jt = "R_Front_Shoulder_Jt"

        if ShoulderChoice[0] is True:
            Shoulder_Left_Ctrl = [mc.curve(name=prefix_L + "_Shoulder_Ctrl", d=1,
                                           p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
                                              (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
                                              (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
                                              (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
                                              (-0.5, 0, 0)]),
                                  mc.scale(0.35, 0.35, 0.35),
                                  mc.setAttr(prefix_L + "_Shoulder_Ctrl.rotateX", -90),
                                  mc.setAttr(prefix_L + "_Shoulder_Ctrl.overrideColor", 6),
                                  mc.setAttr(prefix_L + "_Shoulder_Ctrl.overrideEnabled", 1)]
            Shoulder_L_Val = mc.xform(Shoulder_L_Jt, translation=True, ws=True, query=True)
            mc.xform(Shoulder_Left_Ctrl, ws=1, t=(Shoulder_L_Val[0], Shoulder_L_Val[1], Shoulder_L_Val[2] - 1))
            mc.makeIdentity(t=True, r=True, s=True, a=True)
            mc.parentConstraint(prefix_L + "_Shoulder_Ctrl", Shoulder_L_Jt, mo=True)
            mc.setAttr(prefix_L + "_Shoulder_Ctrl.scale", lock=True)
            # mc.setAttr(prefix_L+"_Shoulder_Ctrl.rotate", lock=True)

        if ShoulderChoice[1] is True:
            Shoulder_Right_Ctrl = [mc.curve(name=prefix_R + "_Shoulder_Ctrl", d=1,
                                            p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
                                               (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
                                               (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
                                               (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
                                               (-0.5, 0, 0)]),
                                   mc.scale(0.35, 0.35, 0.35),
                                   mc.setAttr(prefix_R + "_Shoulder_Ctrl.rotateX", -90),
                                   mc.setAttr(prefix_R + "_Shoulder_Ctrl.overrideColor", 3.5),
                                   mc.setAttr(prefix_R + "_Shoulder_Ctrl.overrideEnabled", 1)]
            Shoulder_R_Val = mc.xform(Shoulder_R_Jt, translation=True, ws=True, query=True)
            mc.xform(Shoulder_Right_Ctrl, ws=1, t=(Shoulder_R_Val[0], Shoulder_R_Val[1], Shoulder_R_Val[2] + 1))
            mc.makeIdentity(t=True, r=True, s=True, a=True)
            mc.parentConstraint(prefix_R + "_Shoulder_Ctrl", Shoulder_R_Jt, mo=True)
            mc.setAttr(prefix_R + "_Shoulder_Ctrl.scale", lock=True)
            # mc.setAttr(prefix_R+"_Shoulder_Ctrl.rotate", lock=True)
        return Left_Foot, Right_Foot

    def Rear_Legs_Control(*args, **kwargs):
        prefix_L = "L"
        prefix_R = "R"
        prefix = "_"
        Left_Foot = True
        Right_Foot = True
        Feet_Ctrl = [Left_Foot, Right_Foot]
        Feet_Ctrl[0] = [mc.curve(name=prefix_L + "_Back_Foot_Ctrl", degree=1,
                                 point=[(1.654147, -0.376619, 0.392), (1.654147, -0.376619, -0.391833),
                                        (0.471549, -0.376619, -0.640084), (-0.237383, -0.387065, -0.56856),
                                        (-0.80264, -0.294179, -0.326289), (-0.807391, -0.294179, 0.331393),
                                        (-0.242134, -0.387065, 0.622436), (0.466798, -0.376619, 0.664218),
                                        (1.654147, -0.376619, 0.392)], knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        mc.scale(1.4, 0.0, 1.5),
                        mc.setAttr(prefix_L + "_Back_Foot_Ctrl.overrideColor", 6),
                        mc.setAttr(prefix_L + "_Back_Foot_Ctrl.overrideEnabled", 1)]

        Heel_Left = "L_Back_Toe01_Jt"
        valFkLeft = mc.xform(Heel_Left, query=True, ws=True, translation=True)
        mc.xform(Feet_Ctrl[0], ws=1, t=(valFkLeft[0], valFkLeft[1], valFkLeft[2]))
        mc.makeIdentity(t=True, s=True, a=True, r=True)

        Feet_Ctrl[1] = [mc.curve(name=prefix_R + "_Back_Foot_Ctrl", degree=1,
                                 point=[(1.654147, -0.376619, 0.392), (1.654147, -0.376619, -0.391833),
                                        (0.471549, -0.376619, -0.640084), (-0.237383, -0.387065, -0.56856),
                                        (-0.80264, -0.294179, -0.326289), (-0.807391, -0.294179, 0.331393),
                                        (-0.242134, -0.387065, 0.622436), (0.466798, -0.376619, 0.664218),
                                        (1.654147, -0.376619, 0.392)], knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        mc.scale(1.4, 0.0, -1.5),
                        mc.setAttr(prefix_R + "_Back_Foot_Ctrl.overrideColor", 3.5),
                        mc.setAttr(prefix_R + "_Back_Foot_Ctrl.overrideEnabled", 1)]

        Heel_Right = "R_Back_Toe01_Jt"
        valFkRight = mc.xform(Heel_Right, query=True, ws=True, translation=True)
        mc.xform(Feet_Ctrl[1], ws=1, t=(valFkRight[0], valFkRight[1], valFkRight[2]))
        mc.makeIdentity(t=True, s=True, a=True, r=True)

        CurveHeelLeftCtrl = [mc.curve(name="L_Back_Feet_Ctrl", degree=1,
                                      point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
                                             (0.138488, 0, -0.990867),
                                             (-0.499831, 0, 0.0111455), (-0.0656259, 0, 1.009447),
                                             (-0.633433, 0, 1.013158),
                                             (-0.989704, 0, -0.00369912)], knot=[0, 1, 2, 3, 4, 5, 6]),
                             mc.scale(0.6, 0.6, 0.6),
                             mc.setAttr("L_Back_Feet_Ctrl.rotateX", 90, lock=True),
                             mc.setAttr("L_Back_Feet_Ctrl.scale", lock=True),
                             mc.setAttr("L_Back_Feet_Ctrl.overrideColor", 6),
                             mc.setAttr("L_Back_Feet_Ctrl.overrideEnabled", 1)]

        CurveHeelRightCtrl = [mc.curve(name="R_Back_Feet_Ctrl", degree=1,
                                       point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
                                              (0.138488, 0, -0.990867),
                                              (-0.499831, 0, 0.0111455), (-0.0656259, 0, 1.009447),
                                              (-0.633433, 0, 1.013158),
                                              (-0.989704, 0, -0.00369912)], knot=[0, 1, 2, 3, 4, 5, 6]),
                              mc.scale(0.6, 0.6, 0.6),
                              mc.setAttr("R_Back_Feet_Ctrl.rotateX", 90, lock=True),
                              mc.setAttr("R_Back_Feet_Ctrl.scale", lock=True),
                              mc.setAttr("R_Back_Feet_Ctrl.overrideColor", 3.5),
                              mc.setAttr("R_Back_Feet_Ctrl.overrideEnabled", 1)]

        Legs_Turn = ["BackLeft", "BackRight"]
        Legs_Ctrl = ["L_Back_Foot_Ctrl", "R_Back_Foot_Ctrl"]

        CurveFeetCtrl = [CurveHeelLeftCtrl, CurveHeelRightCtrl]

        # Left Side
        if Legs_Turn[0]:
            ikAnkle = mc.ikHandle(name="ikHandle_L_Back_Ctrl_Ankle",
                                  startJoint="L_Back_Pelvic_Jt",
                                  endEffector="L_Back_Heel_Jt",
                                  solver="ikRPsolver", parentCurve=False)
            ikHeel = mc.ikHandle(name="ikHandle_L_Back_Ctrl_Heel",
                                 startJoint="L_Back_Heel_Jt",
                                 endEffector="L_Back_Toe01_Jt",
                                 solver="ikRPsolver", parentCurve=False)
            ikToe = mc.ikHandle(name="ikHandle_L_Back_Ctrl_Toe",
                                startJoint="L_Back_Toe01_Jt",
                                endEffector="L_Back_Toe02_Jt",
                                solver="ikRPsolver", parentCurve=False)
            grpIK_FrontLeft = mc.group("ikHandle_L_Back_Ctrl_Heel", "ikHandle_L_Back_Ctrl_Toe",
                                       n="GRP_Ik" + prefix + "ik_Back_Ctrl")

            # Parent feet controls
            HeelLeft = "L_Back_Heel_Jt"
            try:
                dist = 0.5
                setLoc = mc.xform(HeelLeft, query=True, ws=True, translation=True)
                mc.xform(CurveFeetCtrl[0], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                mc.parent("ikHandle_L_Back_Ctrl_Ankle", "L_Back_Feet_Ctrl")

            except:
                mc.error("Wrong values!")
            mc.parent(grpIK_FrontLeft, Legs_Ctrl[0])
            sel = mc.ls(type="ikHandle")
            for ik in sel:
                mc.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = mc.spaceLocator(name="HelpLocsB_" + str(j))
            heel = "L_Back_Toe01_Jt"
            print(locs)
            if mc.ls("HelpLocsB_0", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] - 1))
            if mc.ls("HelpLocsB_1", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] + 1))
                sl = mc.ls(type="locator")
                for k in sl:
                    mc.setAttr("%s.visibility" % k, 0)
        grpLoc = mc.group("HelpLocsB_0", "HelpLocsB_1", n="GRP_Locs")
        # Parent under each foot's curves controls
        mc.parent(grpLoc, "ikHandle_L_Back_Ctrl_Heel")
        mc.parent("ikHandle_L_Back_Ctrl_Heel", "L_Back_Foot_Ctrl")
        mc.parent("L_Back_Feet_Ctrl", "L_Back_Foot_Ctrl")

        # Right Side
        if Legs_Turn[1]:

            ikAnkle = mc.ikHandle(name="ikHandle_R_Back_Ctrl_Ankle",
                                  startJoint="R_Back_Pelvic_Jt",
                                  endEffector="R_Back_Heel_Jt",
                                  solver="ikRPsolver", parentCurve=False)
            ikHeel = mc.ikHandle(name="ikHandle_R_Back_Ctrl_Heel",
                                 startJoint="R_Back_Heel_Jt",
                                 endEffector="R_Back_Toe01_Jt",
                                 solver="ikRPsolver", parentCurve=False)
            ikToe = mc.ikHandle(name="ikHandle_R_Back_Ctrl_Toe",
                                startJoint="R_Back_Toe01_Jt",
                                endEffector="R_Back_Toe02_Jt",
                                solver="ikRPsolver", parentCurve=False)
            grpIK_FrontRight = mc.group("ikHandle_R_Back_Ctrl_Heel", "ikHandle_R_Back_Ctrl_Toe",
                                        n="GRP_Ik" + prefix + "ik_Back_Ctrl")

            # Parent feet controls
            AnkleRight = "R_Back_Heel_Jt"
            try:
                dist = 0.5
                setLoc = mc.xform(AnkleRight, query=True, ws=True, translation=True)
                mc.xform(CurveFeetCtrl[1], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                mc.parent("ikHandle_R_Back_Ctrl_Ankle", "R_Back_Feet_Ctrl")

            except:
                mc.error("Wrong values!")
            mc.parent(grpIK_FrontRight, Legs_Ctrl[1])
            sel = mc.ls(type="ikHandle")
            for ik in sel:
                mc.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = mc.spaceLocator(name="HelpLocsB_0" + str(j))
            heel = "R_Back_Toe01_Jt"
            print(locs)
            if mc.ls("HelpLocsB_00", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] - 1))
            if mc.ls("HelpLocsB_01", selection=True):
                valHeel = mc.xform(heel, ws=True, translation=True, query=True)
                mc.xform(locs, ws=True, t=(valHeel[0], valHeel[1], valHeel[2] + 1))
                sl = mc.ls(type="locator")
                for k in sl:
                    mc.setAttr("%s.visibility" % k, 0)
        grpLoc = mc.group("HelpLocsB_00", "HelpLocsB_01", n="GRP_LocsB")
        mc.parent(grpLoc, "ikHandle_R_Back_Ctrl_Heel")
        mc.parent("ikHandle_R_Back_Ctrl_Heel", "R_Back_Foot_Ctrl")
        mc.parent("R_Back_Feet_Ctrl", "R_Back_Foot_Ctrl")

        # KNEES
        Knee_L_Front_Jt = "L_Back_Knee_Jt"
        Knee_R_Front_Jt = "R_Back_Knee_Jt"
        # Left Knee Cap
        Knee_L_Front_Cap = [mc.curve(name=prefix_L + "_Knee_Back_Cap", d=1,
                                     p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            mc.scale(0.2, 0.2, 0.2),
                            mc.setAttr(prefix_L + "_Knee_Back_Cap.rotateZ", -90),
                            mc.setAttr(prefix_L + "_Knee_Back_Cap.scale", lock=True),
                            mc.setAttr(prefix_L + "_Knee_Back_Cap.scale", lock=True),
                            mc.setAttr(prefix_L + "_Knee_Back_Cap.overrideColor", 6),
                            mc.setAttr(prefix_L + "_Knee_Back_Cap.overrideEnabled", 1)]
        mc.xform(Knee_L_Front_Jt + ".tx", Knee_L_Front_Jt + ".ty", Knee_L_Front_Jt + ".tz")
        valKnee = mc.xform(Knee_L_Front_Jt, query=True, ws=True, translation=True)
        mc.xform(Knee_L_Front_Cap[0], ws=1, t=(valKnee[0] + 1, valKnee[1], valKnee[2]))
        mc.poleVectorConstraint(prefix_L + "_Knee_Back_Cap", "ikHandle_L_Back_Ctrl_Ankle")
        mc.makeIdentity(t=True, a=True, r=True)

        # Right Knee Cap
        Knee_R_Front_Cap = [mc.curve(name=prefix_R + "_Knee_Back_Cap", d=1,
                                     p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            mc.scale(0.2, 0.2, 0.2),
                            mc.setAttr(prefix_R + "_Knee_Back_Cap.rotateZ", -90),
                            mc.setAttr(prefix_R + "_Knee_Back_Cap.scale", lock=True),
                            mc.setAttr(prefix_R + "_Knee_Back_Cap.overrideColor", 3.5),
                            mc.setAttr(prefix_R + "_Knee_Back_Cap.overrideEnabled", 1)]
        mc.xform(Knee_R_Front_Jt + ".tx", Knee_R_Front_Jt + ".ty", Knee_R_Front_Jt + ".tz")
        valKnee = mc.xform(Knee_R_Front_Jt, query=True, ws=True, translation=True)
        mc.xform(Knee_R_Front_Cap[0], ws=1, t=(valKnee[0] + 1, valKnee[1], valKnee[2]))
        mc.poleVectorConstraint(prefix_R + "_Knee_Back_Cap", "ikHandle_R_Back_Ctrl_Ankle")
        mc.makeIdentity(t=True, a=True, r=True)

        # Lock the scale attributes for both feet
        mc.setAttr(prefix_L + "_Back_Foot_Ctrl.scale", lock=True)
        mc.setAttr(prefix_R + "_Back_Foot_Ctrl.scale", lock=True)
        return Left_Foot, Right_Foot

    def Spine_Control(*args, **kwargs):
        prefix = "_"
        # Near Spine
        rearSpineControl = [mc.curve(name="Rear_Spine" + prefix + "Ctrl", d=3,
                                     p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                        (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                        (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                        (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                        (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                        (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                        (-4.993259, 0, -0.0116669)]),
                            mc.scale(0.5, 2.0, 0.5),
                            mc.setAttr("Rear_Spine" + prefix + "Ctrl.scale", lock=True),
                            mc.setAttr("Rear_Spine" + prefix + "Ctrl.rotateX", 90),
                            mc.setAttr("Rear_Spine" + prefix + "Ctrl.rotateY", 90),
                            mc.setAttr("Rear_Spine" + prefix + "Ctrl.overrideColor", 14),
                            mc.setAttr("Rear_Spine" + prefix + "Ctrl.overrideEnabled", 1)]

        ikSpineOne = mc.ikHandle(name="Ik" + prefix + "Spine_01",
                                 startJoint="B03", endEffector="B_Back_Hip_Jt",
                                 solver="ikRPsolver", parentCurve=False)
        rearSpineJt = "B04"
        rearSpineVal = mc.xform(rearSpineJt, translation=True, query=True, ws=True)
        mc.xform(rearSpineControl[0], ws=1, t=(rearSpineVal[0], rearSpineVal[1], rearSpineVal[2]))
        mc.makeIdentity("Rear_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        mc.parentConstraint("Rear_Spine_Ctrl", rearSpineJt, mo=True)
        sel = mc.ls(type="ikHandle")
        for ik in sel:
            mc.setAttr("%s.visibility" % ik, 0)

        # Middle Spine
        middleSpineControl = [mc.curve(name="Middle_Spine" + prefix + "Ctrl", d=3,
                                       p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                          (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                          (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                          (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                          (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                          (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                          (-4.993259, 0, -0.0116669)]),
                              mc.scale(0.55, 2.0, 0.6),
                              mc.setAttr("Middle_Spine" + prefix + "Ctrl.scale", lock=True),
                              mc.setAttr("Middle_Spine" + prefix + "Ctrl.rotateX", 90),
                              mc.setAttr("Middle_Spine" + prefix + "Ctrl.rotateY", 90),
                              mc.setAttr("Middle_Spine" + prefix + "Ctrl.overrideColor", 14),
                              mc.setAttr("Middle_Spine" + prefix + "Ctrl.overrideEnabled", 1)]

        ikSpineTwo = mc.ikHandle(name="Ik" + prefix + "Spine_02",
                                 startJoint="B01", endEffector="B03",
                                 solver="ikRPsolver", parentCurve=False)
        middleSpineJt = "B02"
        middleSpineVal = mc.xform(middleSpineJt, translation=True, query=True, ws=True)
        mc.xform(middleSpineControl[0], ws=1, t=(middleSpineVal[0], middleSpineVal[1], middleSpineVal[2]))
        mc.makeIdentity("Middle_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        mc.parentConstraint("Middle_Spine_Ctrl", middleSpineJt, mo=True)
        ikExtraSpine = mc.ikHandle(name="Ik" + prefix + "Spine_Support",
                                   startJoint="A_Front_Hip_Jt", endEffector="B01",
                                   solver="ikRPsolver", parentCurve=False)
        mc.parent("Ik" + prefix + "Spine_Support", "Middle_Spine_Ctrl")
        sel = mc.ls(type="ikHandle")
        for ik in sel:
            mc.setAttr("%s.visibility" % ik, 0)

        # Front Spine
        frontSpineControl = [mc.curve(name="Front_Spine" + prefix + "Ctrl", d=3,
                                      p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                         (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                         (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                         (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                         (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                         (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                         (-4.993259, 0, -0.0116669)]),
                             mc.scale(0.45, 2.0, 0.6),
                             mc.setAttr("Front_Spine" + prefix + "Ctrl.overrideColor", 14),
                             mc.setAttr("Front_Spine" + prefix + "Ctrl.overrideEnabled", 1),
                             mc.setAttr("Front_Spine" + prefix + "Ctrl.rotateX", 90),
                             mc.setAttr("Front_Spine" + prefix + "Ctrl.rotateY", 90)]
        frontSpineJt = "A_Front_Hip_Jt"
        frontSpineVal = mc.xform(frontSpineJt, translation=True, query=True, ws=True)
        mc.xform(frontSpineControl[0], ws=1, t=(frontSpineVal[0], frontSpineVal[1], frontSpineVal[2]))
        mc.makeIdentity("Front_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        mc.setAttr("Front_Spine" + prefix + "Ctrl.scale", lock=True)
        mc.parentConstraint("Front_Spine_Ctrl", frontSpineJt, mo=True)
        mc.parentConstraint("Middle_Spine_Ctrl", "B03", mo=True)
        mc.parentConstraint("Rear_Spine_Ctrl", "B03", mo=True)

        # Main Spine
        MainSpineControl = [mc.curve(name="Main_Spine" + prefix + "Ctrl", d=3,
                                     p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                        (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                        (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                        (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                        (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                        (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                        (-4.993259, 0, -0.0116669)]),
                            mc.scale(0.657, 2.887, 1.0),
                            mc.setAttr("Main_Spine" + prefix + "Ctrl.overrideColor", 30),
                            mc.setAttr("Main_Spine" + prefix + "Ctrl.overrideEnabled", 1),
                            mc.setAttr("Main_Spine" + prefix + "Ctrl.rotateX", 90),
                            mc.setAttr("Main_Spine" + prefix + "Ctrl.rotateY", 90),
                            mc.setAttr("Main_Spine" + prefix + "Ctrl.rotateZ", -180)]
        MainSpineJt = "B02"
        MainSpineVal = mc.xform(MainSpineJt, translation=True, query=True, ws=True)
        mc.xform(MainSpineControl[0], ws=1, t=(MainSpineVal[0], MainSpineVal[1], MainSpineVal[2]))
        mc.makeIdentity("Main_Spine" + prefix + "Ctrl", t=True, r=True, s=True, a=True)
        mc.setAttr("Main_Spine" + prefix + "Ctrl.scale", lock=True)
        mc.group("Rear_Spine_Ctrl", "Middle_Spine_Ctrl", "Front_Spine_Ctrl", "R_Shoulder_Ctrl", "L_Shoulder_Ctrl",
                 name="GRP_All_Spine_Ctrl")
        mc.parent("GRP_All_Spine_Ctrl", "Main_Spine_Ctrl")
        mc.group("L_Shoulder_Ctrl", "R_Shoulder_Ctrl", name="GRP_Shoulder_Ctrl")
        mc.parent("GRP_Shoulder_Ctrl", "Front_Spine_Ctrl")

    def Neck_Control(*args, **kwargs):
        NeckJt = "Neck_Jt"
        NeckCtrl = [mc.curve(name="Neck_Ctrl", degree=3,
                             point=[(-0.801407, 0, 0.00716748), (-0.802768, 0.023587, -0.220859),
                                    (-0.805489, 0.0707609, -0.676912), (0.761595, -0.283043, -0.667253),
                                    (1.045492, -0.194522, -0.0218101), (1.046678, -0.194804, 0.0403576),
                                    (0.758039, -0.282198, 0.63974), (-0.806291, 0.0676615, 0.650803),
                                    (-0.803035, 0.0225538, 0.221713), (-0.801407, 0, 0.00716748)]),
                    mc.setAttr("Neck_Ctrl.overrideColor", 18),
                    mc.setAttr("Neck_Ctrl.overrideEnabled", 1)]
        mc.scale(2.1, 3.16, 2.8)
        mc.makeIdentity('Neck_Ctrl', apply=True, translate=True, scale=True)
        lockScaling = mc.setAttr("Neck_Ctrl.scale", lock=True)
        valNeck = mc.xform(NeckJt, ws=True, query=True, translation=True)
        mc.xform(NeckCtrl, ws=1, t=(valNeck[0], valNeck[1], valNeck[2]))
        mc.orientConstraint("Neck_Ctrl", NeckJt)
        mc.pointConstraint("Neck_Ctrl", NeckJt)
        grpNeck = mc.group("Neck_Ctrl", name="GRP_Neck")
        mc.parent("GRP_Neck", "Front_Spine_Ctrl")
        lockTranslation = mc.setAttr("Neck_Ctrl.translate", lock=True)
        return NeckCtrl, NeckJt

    def Head_Control(*args, **kwargs):
        HeadJt = "Head_Jt"
        HeadCtrl = [mc.circle(name="Head_Ctrl"),
                    mc.setAttr("Head_Ctrl.overrideColor", 18),
                    mc.setAttr("Head_Ctrl.overrideEnabled", 1),
                    mc.scale(1.5, 1.5, 2.5)]
        valHead = mc.xform(HeadJt, ws=True, query=True, translation=True)
        mc.xform(HeadCtrl[0], ws=1, t=(valHead[0], valHead[1], valHead[2]))
        rotHead = mc.xform(HeadJt, ws=True, query=True, rotation=True)
        angle = 90
        mc.xform(HeadCtrl[0], ws=1, ro=(rotHead[0], rotHead[1] - angle, rotHead[2]))
        mc.makeIdentity("Head_Ctrl", apply=True, translate=True, scale=True, rotate=True)
        lockScaling = mc.setAttr("Head_Ctrl.scale", lock=True)
        mc.parentConstraint(HeadCtrl[0], HeadJt)
        grpHead = mc.group(HeadCtrl[0], name="GRP_Head_Ctrl")
        mc.parent("GRP_Head_Ctrl", "Neck_Ctrl")
        lockTranslation = mc.setAttr("Head_Ctrl.translate", lock=True)
        EarJoint = ["L_Ear_Jt", "R_Ear_Jt"]

        if EarJoint[0]:
            prefix = "_"
            EarControl = [mc.curve(name="L_Ear" + prefix + "Ctrl", d=3,
                                   p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                      (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                      (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                      (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                      (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                      (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                      (-4.993259, 0, -0.0116669)]),
                          mc.scale(0.1, 0.5, 0.15),
                          mc.setAttr("L_Ear" + prefix + "Ctrl.scale", lock=True),
                          mc.setAttr("L_Ear" + prefix + "Ctrl.overrideColor", 6),
                          mc.setAttr("L_Ear" + prefix + "Ctrl.overrideEnabled", 1)]

            valEar = mc.xform(EarJoint[0], ws=True, query=True, translation=True)
            mc.xform(EarControl, ws=1, t=(valEar[0], valEar[1], valEar[2]))
            rotEar = mc.xform(EarJoint[0], ws=True, query=True, rotation=True)
            mc.xform(EarControl, ws=1, ro=(rotEar[0], rotEar[1], rotEar[2]))
            mc.makeIdentity(EarControl[0], a=True, t=True)

            for lock in EarControl:
                mc.setAttr("L_Ear" + prefix + "Ctrl.translate", lock=True)
            mc.orientConstraint(EarControl, EarJoint[0], mo=True)
            grpEarLeft = mc.group(EarControl, name="GRP_L_Ear_Ctrl")
            mc.parent("GRP_L_Ear_Ctrl", "Head_Ctrl")

        if EarJoint[1]:
            prefix = "_"
            EarControl = [mc.curve(name="R_Ear" + prefix + "Ctrl", d=3,
                                   p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                      (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                      (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                      (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                      (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                      (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                      (-4.993259, 0, -0.0116669)]),
                          mc.scale(0.1, 0.5, 0.15),
                          mc.setAttr("R_Ear" + prefix + "Ctrl.scale", lock=True),
                          mc.setAttr("R_Ear" + prefix + "Ctrl.overrideColor", 3.5),
                          mc.setAttr("R_Ear" + prefix + "Ctrl.overrideEnabled", 1)]
            valEar = mc.xform(EarJoint[1], ws=True, query=True, translation=True)
            mc.xform(EarControl, ws=1, t=(valEar[0], valEar[1] - 0.1, valEar[2]))
            rotEar = mc.xform(EarJoint[1], ws=True, query=True, rotation=True)
            mc.xform(EarControl, ws=1, ro=(rotEar[0], rotEar[1] - 180, rotEar[2]))
            mc.makeIdentity(EarControl[0], a=True, r=True, t=True)

            for lock in EarControl:
                mc.setAttr("R_Ear" + prefix + "Ctrl.translate", lock=True)
            mc.orientConstraint(EarControl, EarJoint[1], mo=True)
            grpEarRight = mc.group(EarControl, name="GRP_R_Ear_Ctrl")
            mc.parent("GRP_R_Ear_Ctrl", "Head_Ctrl")
        return HeadCtrl, HeadJt

    def Jaw_Control(*args, **kwargs):
        prefix = "_"
        JawJt = "Lower_Jaw_Jt"
        JawCtrl = [mc.curve(name="Jaw" + prefix + "Ctrl", d=1,
                            p=[(-0.484806, -0.465148, -0.560784), (-0.484806, -0.465148, 0.595512),
                               (-0.275612, 0.538987, 0.636341), (1.356108, 0.120597, 0.636341),
                               (2.161106, 0.0592024, 0.01008), (1.356108, 0.120597, -0.610974),
                               (-0.275612, 0.538987, -0.610974), (-0.484806, -0.465148, -0.560784),
                               (1.146913, -0.67078, -0.560784), (1.951911, -0.670601, 0.01008),
                               (1.146913, -0.67078, 0.595512), (1.356108, 0.120597, 0.636341),
                               (2.161106, 0.0592024, 0.01008), (1.356108, 0.120597, -0.610974),
                               (1.146913, -0.67078, -0.560784), (1.146913, -0.67078, 0.595512),
                               (-0.484806, -0.465148, 0.595512), (1.146913, -0.67078, 0.595512),
                               (1.951911, -0.670601, 0.01008), (2.161106, 0.0592024, 0.01008)]),
                   mc.setAttr("Jaw" + prefix + "Ctrl.overrideColor", 18),
                   mc.setAttr("Jaw" + prefix + "Ctrl.overrideEnabled", 1), mc.scale(0.5, 1, 1.15)]
        valPos = mc.xform(JawJt, query=True, ws=True, translation=True)
        mc.xform(JawCtrl[0], ws=1, t=(valPos[0], valPos[1], valPos[2]))
        valRot = mc.xform(JawJt, query=True, ws=True, rotation=True)
        mc.xform(JawCtrl[0], ws=1, ro=(valRot[0], valRot[1], valRot[2]))
        mc.setAttr("Jaw" + prefix + "Ctrl.rotateZ", -22)
        mc.makeIdentity(JawCtrl[0], a=True, r=True, t=True, s=True)
        mc.orientConstraint(JawCtrl[0], JawJt, mo=True)
        mc.pointConstraint(JawCtrl[0], JawJt, mo=True)
        mc.parent(JawCtrl[0], "Head_Ctrl")
        for lock in JawJt:
            mc.setAttr("Jaw" + prefix + "Ctrl.scale", lock=True),
            mc.setAttr("Jaw" + prefix + "Ctrl.translate", lock=True)

    def Tongue_Control(*args, **kwargs):
        tongueJoints = ["First_Tongue_Jt", "Second_Tongue_Jt", "Third_Tongue_Jt", "Fourth_Tongue_Jt", "Fifth_Tongue_Jt"]
        for tongueRing in range(len(tongueJoints)):
            controls = [mc.circle(name="Tongue_Ctrl_" + str(tongueRing)), mc.scale(0.5, 0.3, 0.5),
                        mc.setAttr("Tongue_Ctrl_" + str(tongueRing) + ".overrideColor", 18),
                        mc.setAttr("Tongue_Ctrl_" + str(tongueRing) + ".overrideEnabled", 1)]
            valPos = mc.xform(tongueJoints[tongueRing], query=True, ws=True, translation=True)
            mc.xform(controls[tongueRing - 1], ws=1, t=(valPos[0], valPos[1], valPos[2]))
            valRot = mc.xform(tongueJoints[tongueRing], query=True, ws=True, rotation=True)
            mc.xform(controls[tongueRing - 1], ws=1, ro=(valRot[0], valRot[1] - 90, valRot[2] - 15))
            mc.makeIdentity("Tongue_Ctrl_" + str(tongueRing), a=True, r=True, t=True, s=True)
            orient = mc.orientConstraint("Tongue_Ctrl_" + str(tongueRing), tongueJoints[tongueRing], maintainOffset=True)
        mc.parent("Tongue_Ctrl_4", "Tongue_Ctrl_3")
        mc.parent("Tongue_Ctrl_3", "Tongue_Ctrl_2")
        mc.parent("Tongue_Ctrl_2", "Tongue_Ctrl_1")
        mc.parent("Tongue_Ctrl_1", "Tongue_Ctrl_0")
        mc.parent("Tongue_Ctrl_0", "Jaw_Ctrl")
        for lock in range(len(tongueJoints)):
            mc.setAttr("Tongue_Ctrl_" + str(lock) + ".scale", lock=True),
            mc.setAttr("Tongue_Ctrl_" + str(lock) + ".translate", lock=True)

    def Tail_Control(*args, **kwargs):
        tailJoints = ["Tail_Jt_A", "Tail_Jt_B", "Tail_Jt_C", "Tail_Jt_D", "Tail_Jt_E"]
        for tailRing in range(len(tailJoints)):
            controls = [mc.curve(name="Tail_Ctrl_" + str(tailRing), d=3,
                                 p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                    (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                    (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                    (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                    (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                    (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                    (-4.993259, 0, -0.0116669)]),
                        mc.scale(0.15, 0.65, 0.20),
                        mc.setAttr("Tail_Ctrl_" + str(tailRing) + ".overrideColor", 22),
                        mc.setAttr("Tail_Ctrl_" + str(tailRing) + ".overrideEnabled", 1)]
            valPos = mc.xform(tailJoints[tailRing], query=True, ws=True, translation=True)
            mc.xform(controls[tailRing - 1], ws=1, t=(valPos[0], valPos[1], valPos[2]))
            valRot = mc.xform(tailJoints[tailRing], query=True, ws=True, rotation=True)
            mc.xform(controls[tailRing - 1], ws=1, ro=(valRot[0], valRot[1] + 90, valRot[2] - 90))
            mc.makeIdentity("Tail_Ctrl_" + str(tailRing), a=True, r=True, t=True, s=True)
            orient = mc.orientConstraint("Tail_Ctrl_" + str(tailRing), tailJoints[tailRing], maintainOffset=True)
        mc.parent("Tail_Ctrl_4", "Tail_Ctrl_3")
        mc.parent("Tail_Ctrl_3", "Tail_Ctrl_2")
        mc.parent("Tail_Ctrl_2", "Tail_Ctrl_1")
        mc.parent("Tail_Ctrl_1", "Tail_Ctrl_0")
        mc.group("Tail_Ctrl_0", name="GRP_Tail_Master")
        mc.parent("GRP_Tail_Master", "Rear_Spine_Ctrl")
        for lock in range(len(tailJoints)):
            mc.setAttr("Tail_Ctrl_" + str(lock) + ".scale", lock=True),
            mc.setAttr("Tail_Ctrl_" + str(lock) + ".translate", lock=True)
        return tailJoints

    def Master_Control(*args, **kwargs):
        mc.circle(name="Tiger_Ctrl")
        mc.scale(8.77, 8.77, 8.77)
        mc.setAttr("Tiger_Ctrl.rotateX", 90)
        mc.setAttr("Tiger_Ctrl.overrideColor", 10)
        mc.setAttr("Tiger_Ctrl.overrideEnabled", 1)
        mc.makeIdentity("Tiger_Ctrl", s=True, r=True, t=True, a=True)
        mc.group("Main_Spine_Ctrl", "R_Front_Foot_Ctrl", "L_Front_Foot_Ctrl",
                 "R_Back_Foot_Ctrl", "L_Back_Foot_Ctrl", "R_Elbow_Front_Cap",
                 "L_Elbow_Front_Cap", "R_Knee_Back_Cap", "L_Knee_Back_Cap", name="GRP_S_Main_Ctrl")
        mc.parent("GRP_S_Main_Ctrl", "Tiger_Ctrl")
        mc.setAttr("Tiger_Ctrl.scale", lock=True)

        # Bigger Controller
        mc.circle(name="Main_Tiger_Ctrl")
        mc.scale(9.77, 9.77, 9.77)
        mc.setAttr("Main_Tiger_Ctrl.rotateX", 90)
        mc.setAttr("Main_Tiger_Ctrl.overrideColor", 0)
        mc.setAttr("Main_Tiger_Ctrl.overrideEnabled", 1)
        mc.makeIdentity("Main_Tiger_Ctrl", s=True, r=True, t=True, a=True)
        mc.group("Tiger_Ctrl", "A_Front_Hip_Jt", name="GRP_B_Main_Ctrl")
        mc.parent("GRP_B_Main_Ctrl", "Main_Tiger_Ctrl")


"""
Animal Skeleton Class
"""
class animal_skeleton(object):
    def __CreateFrontLegsSkeleton__(self):
        self.F_HipJoint = mc.joint(name='A_Front_Hip_Jt', position=(4.086, 8.755, 0.002))
        mc.joint('A_Front_Hip_Jt', edit=True, zso=True, oj='xyz')
        self.F_ShoulderJoint = mc.joint(name='L_Front_Shoulder_Jt', position=(3.76, 6.725, -1.448))
        mc.joint('L_Front_Shoulder_Jt', edit=True, zso=True, oj='xyz')
        self.F_ElbowJoint = mc.joint(name='L_Front_Elbow_Jt', position=(2.729, 4.374, -1.503))
        mc.joint('L_Front_Elbow_Jt', edit=True, zso=True, oj='xyz')
        self.F_WristJoint = mc.joint(name='L_Front_Wrist_Jt', position=(3.5, 2.18, -1.466))
        mc.joint('L_Front_Wrist_Jt', edit=True, zso=True, oj='xyz')
        self.F_ToeJoint = mc.joint(name='L_Front_WristExtra_Jt', position=(3.354, 0.388, -1.437))
        mc.joint('L_Front_WristExtra_Jt', edit=True, zso=True, oj='xyz')
        self.F_ToeJoint = mc.joint(name='L_Front_Toe_Jt', position=(4.862, -0.144, -1.437))
        mc.joint('L_Front_Toe_Jt', edit=True, zso=True, oj='xyz')
        mc.select('A_Front_Hip_Jt')

    def __CreateSpineSkeleton__(self):
        mc.select('A_Front_Hip_Jt')
        self.Backbone_01 = mc.joint(name='B01', position=(2.064, 8.829, 0.041))
        mc.joint('B01', edit=True, zso=True, oj='xyz', sao='yup')
        self.Backbone_02 = mc.joint(name='B02', position=(0.216, 9.445, 0.038))
        mc.joint('B02', edit=True, zso=True, oj='xyz', sao='yup')
        self.Backbone_03 = mc.joint(name='B03', position=(-1.813, 9.481, 0.042))
        mc.joint('B03', edit=True, zso=True, oj='xyz', sao='yup')
        self.Backbone_04 = mc.joint(name='B04', position=(-3.761, 9.253, 0.038))
        mc.joint('B04', edit=True, zso=True, oj='xyz', sao='yup')
        self.BackHipJoint = mc.joint(name='B_Back_Hip_Jt', position=(-5.321, 8.599, 0.04))
        mc.joint('B_Back_Hip_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def __CreateBackLegsSkeleton__(self):
        mc.select('B_Back_Hip_Jt')
        self.B_PelvicJoint = mc.joint(name='L_Back_Pelvic_Jt', position=(-4.754, 7.296, -1.494))
        mc.joint(name='L_Back_Pelvic_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.B_KneeJoint = mc.joint(name='L_Back_Knee_Jt', position=(-2.06, 5.671, -1.542))
        mc.joint(name='L_Back_Knee_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.B_HeelJoint = mc.joint(name='L_Back_Heel_Jt', position=(-6.112, 2.462, -1.445))
        mc.joint(name='L_Back_Heel_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.B_Toe01Joint = mc.joint(name='L_Back_Toe01_Jt', position=(-6.006, 0.25, -1.45))
        mc.joint(name='L_Back_Toe01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.B_Toe02Joint = mc.joint(name='L_Back_Toe02_Jt', position=(-4.992, -0.103, -1.449))
        mc.joint(name='L_Back_Toe02_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def __Tail__(self):
        mc.select('B_Back_Hip_Jt')
        self.A_TailJoint = mc.joint(name='Tail_Jt_A', position=(-6.141, 8.196, 0))
        mc.joint(name='Tail_Jt_A', edit=True, zso=True, oj='xyz', sao='yup')
        self.B_TailJoint = mc.joint(name='Tail_Jt_B', position=(-7.002, 7.895, 0))
        mc.joint(name='Tail_Jt_B', edit=True, zso=True, oj='xyz', sao='yup')
        self.C_TailJoint = mc.joint(name='Tail_Jt_C', position=(-7.77, 7.752, 0))
        mc.joint(name='Tail_Jt_C', edit=True, zso=True, oj='xyz', sao='yup')
        self.D_TailJoint = mc.joint(name='Tail_Jt_D', position=(-8.498, 7.719, 0))
        mc.joint(name='Tail_Jt_D', edit=True, zso=True, oj='xyz', sao='yup')
        self.E_TailJoint = mc.joint(name='Tail_Jt_E', position=(-9.225, 7.848, 0))
        mc.joint(name='Tail_Jt_E', edit=True, zso=True, oj='xyz', sao='yup')
        self.F_TailJoint = mc.joint(name='Tail_Jt_F', position=(-9.866, 8.115, 0))
        mc.joint(name='Tail_Jt_F', edit=True, zso=True, oj='xyz', sao='yup')

    def __Head__(self):
        mc.select('A_Front_Hip_Jt')
        self.NeckJoint = mc.joint(name='Neck_Jt', position=(6.016, 9.717, 0))
        mc.joint(name='Neck_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.HeadJoint = mc.joint(name='Head_Jt', position=(7.634, 12.322, 0))
        mc.joint(name='Head_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.JawJoint = mc.joint(name='Jaw_Jt', position=(10.758, 10.99, 0))
        mc.joint(name='Jaw_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        mc.select("A_Front_Hip_Jt")

    def __Ears__(self):
        mc.select("Head_Jt")
        self.EarJoint = mc.joint(name="L_Ear_Jt", position=(7.71, 12.503, -0.896))
        mc.joint(name="L_Ear_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.EarJoint = mc.joint(name="L_Ear_Tip_Jt", position=(7.515, 13.229, -1.142))
        mc.joint(name="L_Ear_Tip_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def __Jaw__(self):
        mc.select("Head_Jt")
        self.LowerJawJoint = mc.joint(name="Lower_Jaw_Jt", position=(7.723, 10.89, 0.0))
        mc.joint(name="Lower_Jaw_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.TipJawJoint = mc.joint(name="Tip_Jaw_Jt", position=(10.119, 9.707, 0.019))
        mc.joint(name="Tip_Jaw_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def __Tongue__(self):
        mc.select("Lower_Jaw_Jt")
        self.FirstTongueJoint = mc.joint(name="First_Tongue_Jt", position=(8.106, 11.268, 0.0))
        mc.joint(name="First_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.SecondTongueJoint = mc.joint(name="Second_Tongue_Jt", position=(8.524, 11.148, 0.0))
        mc.joint(name="Second_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.ThirdTongueJoint = mc.joint(name="Third_Tongue_Jt", position=(8.838, 10.949, 0.0))
        mc.joint(name="Third_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.FourthTongueJoint = mc.joint(name="Fourth_Tongue_Jt", position=(9.162, 10.698, 0.0))
        mc.joint(name="Fourth_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.FifthTongueJoint = mc.joint(name="Fifth_Tongue_Jt", position=(9.47, 10.426, 0.0))
        mc.joint(name="Fifth_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")

