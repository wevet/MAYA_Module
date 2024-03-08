# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
import random
import math
from functools import partial

"""
import Animal_Rig_Window as rig
import importlib
importlib.reload(rig)
window = rig.Animal_Rig_Window()
window.create()
"""

class Animal_Rig_Window(object):

    def __init__(self):
        self.window = 'AnimalRig_Window'
        self.title = 'Animal Auto Rigging Tool'
        self.size = (340, 700)
        self.supportsToolAction = True

        self.edit_menu_division = None
        self.edit_menu_skeleton_radio = None
        self.edit_menu_tool = None

        self.button_skeleton_quadruped = None

        self.m_pelvis_joint = None
        self.m_knee_joint = None
        self.m_heel_joint = None
        self.m_toe01_joint = None
        self.m_toe02_joint = None

        self.mirror_each_joint = None

    def create(self):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)
        self.window = cmds.window(self.window, title=self.title, widthHeight=self.size, menuBar=True)
        self.show_common_menu()
        cmds.showWindow()

    def show_common_menu(self):
        #self.edit_menu = cmds.menu(label='Edit')
        self.edit_menu_division = cmds.menuItem(d=True)
        self.edit_menu_skeleton_radio = cmds.radioMenuItemCollection()
        self.edit_menu_tool = cmds.menuItem(label='As Tool', radioButton=True, enable=self.supportsToolAction, command=self.edit_menu_tool_command)
        #self.help_menu = cmds.menu(label='Help')
        #self.help_menu_item = cmds.menuItem(label='Help on %s' % self.title, command=self.help_menu_command)

        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=4, columnWidth=340)
        cmds.text("QUADRUPED CHARACTER", align="center")
        cmds.text("  ")
        cmds.text("Step 1: Create quadruped skeleton")
        self.button_skeleton_quadruped = cmds.button(label='Quadruped Skeleton', command=partial(self.create_skeleton), width=120, height=40)

        cmds.text("  ")
        cmds.text("Step 2: Create Legs control")
        cmds.text("____________________________________")
        cmds.text(label='REAR BODY CONTROL', align='center')
        button_mirror_joints = cmds.button(label='Mirror Joints', command=partial(self.create_mirror_joints), width=120, height=40)
        button_rig_front_legs_ctrl = cmds.button(label='Front Legs Control', command=partial(self.create_front_legs_control), width=120, height=40)
        button_rig_rear_legs_ctrl = cmds.button(label='Rear Legs Control', command=partial(self.create_rear_legs_control), width=120, height=40)
        button_rig_spine_ctrl = cmds.button(label='Spine Control', command=partial(self.create_spine_control), width=120, height=40, align="center")

        cmds.text("  ")
        cmds.text("Step 3: Create Neck/Head controls")
        cmds.text("__________________________________")
        cmds.text(label='FRONT BODY CONTROL', align='center')
        button_rig_neck_ctrl = cmds.button(label='Neck Control', command=partial(self.create_neck_control), width=120, height=40)
        button_rig_head_ctrl = cmds.button(label='Head Control', command=partial(self.create_head_control), width=120, height=40)
        button_rig_jaw_ctrl = cmds.button(label="Jaw Control", command=partial(self.create_jaw_control), width=120, height=40)
        button_rig_tongue_ctrl = cmds.button(label="Tongue Control", command=partial(self.create_tongue_control), width=120, height=40)

        cmds.text("   ")
        cmds.text("Step 4: Create Tail Control")
        button_rig_tail_ctrl = cmds.button(label="Tail Control", command=partial(self.create_tail_control), width=120, height=40)

        cmds.text("   ")
        cmds.text("Step 5: Create Master control")
        cmds.text(label='MASTER CONTROL', align='center')
        button_main_ctrl = cmds.button(label='Master Control', command=partial(self.create_master_control), width=120, height=40, align='center')
        close_button = cmds.button(label="Close", command=partial(self.close_window), width=120, height=40, align='center')


    def close_window(self, *args):
        if cmds.window(self.window, exists=True):
            cmds.deleteUI(self.window, window=True)

    @staticmethod
    def create_skeleton(*args, **kwargs):
        skeleton = Animal_Skeleton()
        skeleton.create_front_legs_skeleton()
        skeleton.create_spine_skeleton()
        skeleton.create_back_legs_skeleton()
        skeleton.create_tail_skeleton()
        skeleton.create_head_skeleton()
        skeleton.create_jaw_skeleton()
        skeleton.create_ears_skeleton()
        skeleton.create_tongue_skeleton()

    def create_middle_legs_skeleton(self, *args, **kwargs):
        cmds.select("B03")
        self.m_pelvis_joint = cmds.joint(name="L_Middle_Pelvis_Jt", position=(-0.037, 7.297, -1.41))
        cmds.joint(name="L_Middle_Pelvis_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.m_knee_joint = cmds.joint(name="L_Middle_Knee_Jt", position=(0.411, 4.739, -1.487))
        cmds.joint(name="L_Middle_Knee_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.m_heel_joint = cmds.joint(name="L_Middle_Heel_Jt", position=(-0.746, 2.537, -1.418))
        cmds.joint(name="L_Middle_Heel_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.m_toe01_joint = cmds.joint(name="L_Middle_Toe01_Jt", position=(-0.634, 0.093, -1.432))
        cmds.joint(name="L_Middle_Toe01_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.m_toe02_joint = cmds.joint(name="L_Middle_Toe02_Jt", position=(0.896, -0.093, -1.432))
        cmds.joint(name="L_Middle_Toe02_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def create_mirror_joints(self, *args):
        cmds.select('A_Front_Hip_Jt')
        self.mirror_each_joint = cmds.mirrorJoint('L_Front_Shoulder_Jt', mirrorXY=True, mirrorBehavior=True, searchReplace=('L_', 'R_'))
        cmds.select('B_Back_Hip_Jt')
        self.mirror_each_joint = cmds.mirrorJoint('L_Back_Pelvic_Jt', mirrorXY=True, mirrorBehavior=True, searchReplace=('L_', 'R_'))
        cmds.select("Head_Jt")
        self.mirror_each_joint = cmds.mirrorJoint("L_Ear_Jt", mirrorXY=True, mirrorBehavior=True, searchReplace=("L_", "R_"))

    def edit_menu_tool_command(self, *args):
        pass

    @staticmethod
    def create_front_legs_control(*args, **kwargs):
        prefix_l = "L"
        prefix_r = "R"
        prefix = "_"
        left_foot = True
        right_foot = True
        feet_ctrl = [left_foot, right_foot]
        feet_ctrl[0] = [cmds.curve(name=prefix_l + "_Front_Foot_Ctrl", degree=1,
                                   point=[(1.654147, -0.376619, 0.392),
                                          (1.654147, -0.376619, -0.391833), (0.471549, -0.376619, -0.640084),
                                          (-0.237383, -0.387065, -0.56856), (-0.80264, -0.294179, -0.326289),
                                          (-0.807391, -0.294179, 0.331393), (-0.242134, -0.387065, 0.622436),
                                          (0.466798, -0.376619, 0.664218), (1.654147, -0.376619, 0.392)],
                                   knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        cmds.scale(1.4, 0.0, 1.5),
                        cmds.setAttr(prefix_l + "_Front_Foot_Ctrl.overrideColor", 6),
                        cmds.setAttr(prefix_l + "_Front_Foot_Ctrl.overrideEnabled", 1)]
        cmds.makeIdentity(t=True, s=True, a=True, r=True)
        ankle_left = "L_Front_WristExtra_Jt"
        val_fk_left = cmds.xform(ankle_left, query=True, ws=True, translation=True)
        cmds.xform(feet_ctrl[0], ws=1, t=(val_fk_left[0], val_fk_left[1], val_fk_left[2]))

        feet_ctrl[1] = [cmds.curve(name=prefix_r + "_Front_Foot_Ctrl", degree=1,
                                   point=[(1.654147, -0.376619, 0.392),
                                          (1.654147, -0.376619, -0.391833), (0.471549, -0.376619, -0.640084),
                                          (-0.237383, -0.387065, -0.56856), (-0.80264, -0.294179, -0.326289),
                                          (-0.807391, -0.294179, 0.331393), (-0.242134, -0.387065, 0.622436),
                                          (0.466798, -0.376619, 0.664218), (1.654147, -0.376619, 0.392)],
                                   knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        cmds.scale(1.4, 0.0, -1.5),
                        cmds.setAttr(prefix_r + "_Front_Foot_Ctrl.overrideColor", 3.5),
                        cmds.setAttr(prefix_r + "_Front_Foot_Ctrl.overrideEnabled", 1)]
        cmds.makeIdentity(t=True, s=True, a=True, r=True)
        ankle_right = "R_Front_WristExtra_Jt"
        val_fk_right = cmds.xform(ankle_right, query=True, ws=True, translation=True)
        cmds.xform(feet_ctrl[1], ws=1, t=(val_fk_right[0], val_fk_right[1], val_fk_right[2]))

        curve_wrists_left_ctrl = [cmds.curve(name="L_Front_Feet_Ctrl", degree=1,
                                          point=[(-0.989704, 0, -0.00369912),
                                                 (-0.310562, 0, -0.998289), (0.138488, 0, -0.990867),
                                                 (-0.499831, 0, 0.0111455), (-0.0656259, 0, 1.009447),
                                                 (-0.633433, 0, 1.013158), (-0.989704, 0, -0.00369912)],
                                             knot=[0, 1, 2, 3, 4, 5, 6]),
                                  cmds.scale(0.6, 0.6, 0.6),
                                  cmds.setAttr("L_Front_Feet_Ctrl.rotateX", 90, lock=True),
                                  cmds.setAttr("L_Front_Feet_Ctrl.scale", lock=True),
                                  cmds.setAttr("L_Front_Feet_Ctrl.overrideColor", 6),
                                  cmds.setAttr("L_Front_Feet_Ctrl.overrideEnabled", 1)]

        curve_wrists_right_ctrl = [cmds.curve(name="R_Front_Feet_Ctrl", degree=1,
                                           point=[(-0.989704, 0, -0.00369912),
                                                  (-0.310562, 0, -0.998289), (0.138488, 0, -0.990867),
                                                  (-0.499831, 0, 0.0111455), (-0.0656259, 0, 1.009447),
                                                  (-0.633433, 0, 1.013158), (-0.989704, 0, -0.00369912)],
                                              knot=[0, 1, 2, 3, 4, 5, 6]),
                                   cmds.scale(0.6, 0.6, 0.6),
                                   cmds.setAttr("R_Front_Feet_Ctrl.rotateX", 90, lock=True),
                                   cmds.setAttr("R_Front_Feet_Ctrl.scale", lock=True),
                                   cmds.setAttr("R_Front_Feet_Ctrl.overrideColor", 3.5),
                                   cmds.setAttr("R_Front_Feet_Ctrl.overrideEnabled", 1)]
        legs_turn = ["FrontLeft", "FrontRight"]
        legs_ctrl = ["L_Front_Foot_Ctrl", "R_Front_Foot_Ctrl"]
        curve_feet_ctrl = [curve_wrists_left_ctrl, curve_wrists_right_ctrl]

        # Left Side
        if legs_turn[0]:
            ik_ankle = cmds.ikHandle(name="ikHandle_L_Front_Ctrl_Ankle", startJoint="L_Front_Shoulder_Jt", endEffector="L_Front_Wrist_Jt", solver="ikRPsolver", parentCurve=False)
            ik_heel = cmds.ikHandle(name="ikHandle_L_Front_Ctrl_Heel", startJoint="L_Front_Wrist_Jt", endEffector="L_Front_WristExtra_Jt", solver="ikRPsolver", parentCurve=False)
            ik_toe = cmds.ikHandle(name="ikHandle_L_Front_Ctrl_Toe", startJoint="L_Front_WristExtra_Jt", endEffector="L_Front_Toe_Jt", solver="ikRPsolver", parentCurve=False)
            grp_ik_front_left = cmds.group("ikHandle_L_Front_Ctrl_Heel", "ikHandle_L_Front_Ctrl_Toe", n="GRP_Ik" + prefix + "ik_Front_Ctrl")
            ankle_left = "L_Front_Wrist_Jt"
            try:
                dist = 0.5
                setLoc = cmds.xform(ankle_left, query=True, ws=True, translation=True)
                cmds.xform(curve_feet_ctrl[0], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                cmds.parent("ikHandle_L_Front_Ctrl_Ankle", "L_Front_Feet_Ctrl")
            except:
                cmds.error("Wrong values!")

            cmds.parent(grp_ik_front_left, legs_ctrl[0])
            sel = cmds.ls(type="ikHandle")
            for ik in sel:
                cmds.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = cmds.spaceLocator(name="HelpLocs_" + str(j))
            heel = "L_Front_WristExtra_Jt"
            print(locs)
            if cmds.ls("HelpLocs_0", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locs, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] - 1))
            if cmds.ls("HelpLocs_1", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locs, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] + 1))
                sl = cmds.ls(type="locator")
                for k in sl:
                    cmds.setAttr("%s.visibility" % k, 0)
        grp_loc = cmds.group("HelpLocs_0", "HelpLocs_1", n="GRP_Locs")

        # Parent under each foot's curves controls
        cmds.parent(grp_loc, "ikHandle_L_Front_Ctrl_Heel")
        cmds.parent("ikHandle_L_Front_Ctrl_Heel", "L_Front_Foot_Ctrl")
        cmds.parent("L_Front_Feet_Ctrl", "L_Front_Foot_Ctrl")

        # Lock the scale attributes for both feet
        cmds.setAttr(prefix_l + "_Front_Foot_Ctrl.scale", lock=True)
        cmds.setAttr(prefix_r + "_Front_Foot_Ctrl.scale", lock=True)

        # Right Side
        if legs_turn[1]:
            ik_ankle = cmds.ikHandle(name="ikHandle_R_Front_Ctrl_Ankle", startJoint="R_Front_Shoulder_Jt", endEffector="R_Front_Wrist_Jt", solver="ikRPsolver", parentCurve=False)
            ik_heel = cmds.ikHandle(name="ikHandle_R_Front_Ctrl_Heel", startJoint="R_Front_Wrist_Jt", endEffector="R_Front_WristExtra_Jt", solver="ikRPsolver", parentCurve=False)
            ik_toe = cmds.ikHandle(name="ikHandle_R_Front_Ctrl_Toe", startJoint="R_Front_WristExtra_Jt", endEffector="R_Front_Toe_Jt", solver="ikRPsolver", parentCurve=False)
            grp_ik_front_right = cmds.group("ikHandle_R_Front_Ctrl_Heel", "ikHandle_R_Front_Ctrl_Toe", n="GRP_Ik" + prefix + "ik_Front_Ctrl")
            ankle_right = "R_Front_Wrist_Jt"
            try:
                dist = 0.5
                setLoc = cmds.xform(ankle_right, query=True, ws=True, translation=True)
                cmds.xform(curve_feet_ctrl[1], ws=1, t=(setLoc[0] - dist, setLoc[1], setLoc[2]))
                cmds.parent("ikHandle_R_Front_Ctrl_Ankle", "R_Front_Feet_Ctrl")
            except:
                cmds.error("Wrong values!")
            cmds.parent(grp_ik_front_right, legs_ctrl[1])
            sel = cmds.ls(type="ikHandle")
            for ik in sel:
                cmds.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locs = cmds.spaceLocator(name="HelpLocs_0" + str(j))
            heel = "R_Front_WristExtra_Jt"
            print(locs)
            if cmds.ls("HelpLocs_00", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locs, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] - 1))
            if cmds.ls("HelpLocs_01", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locs, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] + 1))
                sl = cmds.ls(type="locator")
                for k in sl:
                    cmds.setAttr("%s.visibility" % k, 0)
        grp_loc = cmds.group("HelpLocs_00", "HelpLocs_01", n="GRP_Locs")

        # Parent under each foot's curves controls
        cmds.parent(grp_loc, "ikHandle_R_Front_Ctrl_Heel")
        cmds.parent("ikHandle_R_Front_Ctrl_Heel", "R_Front_Foot_Ctrl")
        cmds.parent("R_Front_Feet_Ctrl", "R_Front_Foot_Ctrl")

        # Knees
        knee_l_front_jt = "L_Front_Elbow_Jt"
        knee_r_front_jt = "R_Front_Elbow_Jt"

        # Left Knee Cap
        knee_l_front_cap = [cmds.curve(name=prefix_l + "_Elbow_Front_Cap", d=1,
                                       p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            cmds.scale(0.2, 0.2, 0.2),
                            cmds.setAttr(prefix_l + "_Elbow_Front_Cap.rotateZ", 90),
                            cmds.setAttr(prefix_l + "_Elbow_Front_Cap.scale", lock=True),
                            cmds.setAttr(prefix_l + "_Elbow_Front_Cap.scale", lock=True),
                            cmds.setAttr(prefix_l + "_Elbow_Front_Cap.overrideColor", 6),
                            cmds.setAttr(prefix_l + "_Elbow_Front_Cap.overrideEnabled", 1)]
        cmds.xform(knee_l_front_jt + ".tx", knee_l_front_jt + ".ty", knee_l_front_jt + ".tz")
        val_knee = cmds.xform(knee_l_front_jt, query=True, ws=True, translation=True)
        cmds.xform(knee_l_front_cap[0], ws=1, t=(val_knee[0] - 1.5, val_knee[1], val_knee[2]))
        cmds.poleVectorConstraint(prefix_l + "_Elbow_Front_Cap", "ikHandle_L_Front_Ctrl_Ankle")
        cmds.makeIdentity(t=True, a=True, r=True)

        # Right Knee Cap
        knee_r_front_cap = [cmds.curve(name=prefix_r + "_Elbow_Front_Cap", d=1,
                                       p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                        (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                        (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                        (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                        (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                        (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                        (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                        (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                        (-4, 0, 0)]),
                            cmds.scale(0.2, 0.2, 0.2),
                            cmds.setAttr(prefix_r + "_Elbow_Front_Cap.rotateZ", 90),
                            cmds.setAttr(prefix_r + "_Elbow_Front_Cap.scale", lock=True),
                            cmds.setAttr(prefix_r + "_Elbow_Front_Cap.overrideColor", 3.5),
                            cmds.setAttr(prefix_r + "_Elbow_Front_Cap.overrideEnabled", 1)]
        cmds.xform(knee_r_front_jt + ".tx", knee_r_front_jt + ".ty", knee_r_front_jt + ".tz")
        val_knee = cmds.xform(knee_r_front_jt, query=True, ws=True, translation=True)
        cmds.xform(knee_r_front_cap[0], ws=1, t=(val_knee[0] - 1.5, val_knee[1], val_knee[2]))
        cmds.poleVectorConstraint(prefix_r + "_Elbow_Front_Cap", "ikHandle_R_Front_Ctrl_Ankle")
        cmds.makeIdentity(t=True, a=True, r=True)

        shoulder_choice = [True, True]
        shoulder_l_jt = "L_Front_Shoulder_Jt"
        shoulder_r_jt = "R_Front_Shoulder_Jt"

        if shoulder_choice[0] is True:
            shoulder_left_ctrl = [cmds.curve(name=prefix_l + "_Shoulder_Ctrl", d=1,
                                             p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
                                              (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
                                              (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
                                              (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
                                              (-0.5, 0, 0)]),
                                  cmds.scale(0.35, 0.35, 0.35),
                                  cmds.setAttr(prefix_l + "_Shoulder_Ctrl.rotateX", -90),
                                  cmds.setAttr(prefix_l + "_Shoulder_Ctrl.overrideColor", 6),
                                  cmds.setAttr(prefix_l + "_Shoulder_Ctrl.overrideEnabled", 1)]
            shoulder_l_val = cmds.xform(shoulder_l_jt, translation=True, ws=True, query=True)
            cmds.xform(shoulder_left_ctrl, ws=1, t=(shoulder_l_val[0], shoulder_l_val[1], shoulder_l_val[2] - 1))
            cmds.makeIdentity(t=True, r=True, s=True, a=True)
            cmds.parentConstraint(prefix_l + "_Shoulder_Ctrl", shoulder_l_jt, mo=True)
            cmds.setAttr(prefix_l + "_Shoulder_Ctrl.scale", lock=True)
            # mc.setAttr(prefix_L+"_Shoulder_Ctrl.rotate", lock=True)

        if shoulder_choice[1] is True:
            shoulder_right_ctrl = [cmds.curve(name=prefix_r + "_Shoulder_Ctrl", d=1,
                                              p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
                                               (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
                                               (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
                                               (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
                                               (-0.5, 0, 0)]),
                                   cmds.scale(0.35, 0.35, 0.35),
                                   cmds.setAttr(prefix_r + "_Shoulder_Ctrl.rotateX", -90),
                                   cmds.setAttr(prefix_r + "_Shoulder_Ctrl.overrideColor", 3.5),
                                   cmds.setAttr(prefix_r + "_Shoulder_Ctrl.overrideEnabled", 1)]
            shoulder_r_val = cmds.xform(shoulder_r_jt, translation=True, ws=True, query=True)
            cmds.xform(shoulder_right_ctrl, ws=1, t=(shoulder_r_val[0], shoulder_r_val[1], shoulder_r_val[2] + 1))
            cmds.makeIdentity(t=True, r=True, s=True, a=True)
            cmds.parentConstraint(prefix_r + "_Shoulder_Ctrl", shoulder_r_jt, mo=True)
            cmds.setAttr(prefix_r + "_Shoulder_Ctrl.scale", lock=True)
            # mc.setAttr(prefix_R+"_Shoulder_Ctrl.rotate", lock=True)
        return left_foot, right_foot

    @staticmethod
    def create_rear_legs_control(*args, **kwargs):
        prefix_l = "L"
        prefix_r = "R"
        prefix = "_"
        left_foot = True
        right_foot = True
        feet_ctrl = [left_foot, right_foot]
        # LeftFoot
        feet_ctrl[0] = [cmds.curve(name=prefix_l + "_Back_Foot_Ctrl", degree=1,
                                   point=[(1.654147, -0.376619, 0.392), (1.654147, -0.376619, -0.391833),
                                          (0.471549, -0.376619, -0.640084), (-0.237383, -0.387065, -0.56856),
                                          (-0.80264, -0.294179, -0.326289), (-0.807391, -0.294179, 0.331393),
                                          (-0.242134, -0.387065, 0.622436), (0.466798, -0.376619, 0.664218),
                                          (1.654147, -0.376619, 0.392)],
                                   knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        cmds.scale(1.4, 0.0, 1.5),
                        cmds.setAttr(prefix_l + "_Back_Foot_Ctrl.overrideColor", 6),
                        cmds.setAttr(prefix_l + "_Back_Foot_Ctrl.overrideEnabled", 1)]
        heel_left = "L_Back_Toe01_Jt"
        val_fk_left = cmds.xform(heel_left, query=True, ws=True, translation=True)
        cmds.xform(feet_ctrl[0], ws=1, t=(val_fk_left[0], val_fk_left[1], val_fk_left[2]))
        cmds.makeIdentity(t=True, s=True, a=True, r=True)

        # RightFoot
        feet_ctrl[1] = [cmds.curve(name=prefix_r + "_Back_Foot_Ctrl", degree=1,
                                   point=[(1.654147, -0.376619, 0.392), (1.654147, -0.376619, -0.391833),
                                          (0.471549, -0.376619, -0.640084), (-0.237383, -0.387065, -0.56856),
                                          (-0.80264, -0.294179, -0.326289), (-0.807391, -0.294179, 0.331393),
                                          (-0.242134, -0.387065, 0.622436), (0.466798, -0.376619, 0.664218),
                                          (1.654147, -0.376619, 0.392)],
                                   knot=[0, 1, 2, 3, 4, 5, 6, 7, 8]),
                        cmds.scale(1.4, 0.0, -1.5),
                        cmds.setAttr(prefix_r + "_Back_Foot_Ctrl.overrideColor", 3.5),
                        cmds.setAttr(prefix_r + "_Back_Foot_Ctrl.overrideEnabled", 1)]
        heel_right = "R_Back_Toe01_Jt"
        val_fk_right = cmds.xform(heel_right, query=True, ws=True, translation=True)
        cmds.xform(feet_ctrl[1], ws=1, t=(val_fk_right[0], val_fk_right[1], val_fk_right[2]))
        cmds.makeIdentity(t=True, s=True, a=True, r=True)

        curve_heel_left_ctrl = [cmds.curve(name="L_Back_Feet_Ctrl", degree=1,
                                        point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
                                               (0.138488, 0, -0.990867), (-0.499831, 0, 0.0111455),
                                               (-0.0656259, 0, 1.009447), (-0.633433, 0, 1.013158),
                                               (-0.989704, 0, -0.00369912)],
                                           knot=[0, 1, 2, 3, 4, 5, 6]),
                             cmds.scale(0.6, 0.6, 0.6),
                             cmds.setAttr("L_Back_Feet_Ctrl.rotateX", 90, lock=True),
                             cmds.setAttr("L_Back_Feet_Ctrl.scale", lock=True),
                             cmds.setAttr("L_Back_Feet_Ctrl.overrideColor", 6),
                             cmds.setAttr("L_Back_Feet_Ctrl.overrideEnabled", 1)]

        curve_heel_right_ctrl = [cmds.curve(name="R_Back_Feet_Ctrl", degree=1,
                                         point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
                                                (0.138488, 0, -0.990867), (-0.499831, 0, 0.0111455),
                                                (-0.0656259, 0, 1.009447), (-0.633433, 0, 1.013158),
                                                (-0.989704, 0, -0.00369912)],
                                            knot=[0, 1, 2, 3, 4, 5, 6]),
                              cmds.scale(0.6, 0.6, 0.6),
                              cmds.setAttr("R_Back_Feet_Ctrl.rotateX", 90, lock=True),
                              cmds.setAttr("R_Back_Feet_Ctrl.scale", lock=True),
                              cmds.setAttr("R_Back_Feet_Ctrl.overrideColor", 3.5),
                              cmds.setAttr("R_Back_Feet_Ctrl.overrideEnabled", 1)]
        legs_turn = ["BackLeft", "BackRight"]
        legs_ctrl = ["L_Back_Foot_Ctrl", "R_Back_Foot_Ctrl"]
        curve_feet_ctrl = [curve_heel_left_ctrl, curve_heel_right_ctrl]

        # Left Side
        if legs_turn[0]:
            ik_ankle = cmds.ikHandle(name="ikHandle_L_Back_Ctrl_Ankle", startJoint="L_Back_Pelvic_Jt", endEffector="L_Back_Heel_Jt", solver="ikRPsolver", parentCurve=False)
            ik_heel = cmds.ikHandle(name="ikHandle_L_Back_Ctrl_Heel", startJoint="L_Back_Heel_Jt", endEffector="L_Back_Toe01_Jt", solver="ikRPsolver", parentCurve=False)
            ik_toe = cmds.ikHandle(name="ikHandle_L_Back_Ctrl_Toe", startJoint="L_Back_Toe01_Jt", endEffector="L_Back_Toe02_Jt", solver="ikRPsolver", parentCurve=False)
            grp_ik_front_left = cmds.group("ikHandle_L_Back_Ctrl_Heel", "ikHandle_L_Back_Ctrl_Toe", n="GRP_Ik" + prefix + "ik_Back_Ctrl")
            heel_left = "L_Back_Heel_Jt"
            try:
                dist = 0.5
                set_loc = cmds.xform(heel_left, query=True, ws=True, translation=True)
                cmds.xform(curve_feet_ctrl[0], ws=1, t=(set_loc[0] - dist, set_loc[1], set_loc[2]))
                cmds.parent("ikHandle_L_Back_Ctrl_Ankle", "L_Back_Feet_Ctrl")
            except:
                cmds.error("Wrong values!")
            cmds.parent(grp_ik_front_left, legs_ctrl[0])
            sel = cmds.ls(type="ikHandle")
            for ik in sel:
                cmds.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locators = cmds.spaceLocator(name="HelpLocsB_" + str(j))
            heel = "L_Back_Toe01_Jt"
            print(locators)
            if cmds.ls("HelpLocsB_0", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locators, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] - 1))
            if cmds.ls("HelpLocsB_1", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locators, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] + 1))
                sl = cmds.ls(type="locator")
                for k in sl:
                    cmds.setAttr("%s.visibility" % k, 0)
        group_locator = cmds.group("HelpLocsB_0", "HelpLocsB_1", n="GRP_Locs")
        cmds.parent(group_locator, "ikHandle_L_Back_Ctrl_Heel")
        cmds.parent("ikHandle_L_Back_Ctrl_Heel", "L_Back_Foot_Ctrl")
        cmds.parent("L_Back_Feet_Ctrl", "L_Back_Foot_Ctrl")

        # Right Side
        if legs_turn[1]:
            ik_ankle = cmds.ikHandle(name="ikHandle_R_Back_Ctrl_Ankle", startJoint="R_Back_Pelvic_Jt", endEffector="R_Back_Heel_Jt", solver="ikRPsolver", parentCurve=False)
            ik_heel = cmds.ikHandle(name="ikHandle_R_Back_Ctrl_Heel", startJoint="R_Back_Heel_Jt", endEffector="R_Back_Toe01_Jt", solver="ikRPsolver", parentCurve=False)
            ik_toe = cmds.ikHandle(name="ikHandle_R_Back_Ctrl_Toe", startJoint="R_Back_Toe01_Jt", endEffector="R_Back_Toe02_Jt", solver="ikRPsolver", parentCurve=False)
            grp_ik_front_right = cmds.group("ikHandle_R_Back_Ctrl_Heel", "ikHandle_R_Back_Ctrl_Toe", n="GRP_Ik" + prefix + "ik_Back_Ctrl")
            ankle_right = "R_Back_Heel_Jt"
            try:
                dist = 0.5
                set_loc = cmds.xform(ankle_right, query=True, ws=True, translation=True)
                cmds.xform(curve_feet_ctrl[1], ws=1, t=(set_loc[0] - dist, set_loc[1], set_loc[2]))
                cmds.parent("ikHandle_R_Back_Ctrl_Ankle", "R_Back_Feet_Ctrl")
            except:
                cmds.error("Wrong values!")
            cmds.parent(grp_ik_front_right, legs_ctrl[1])
            sel = cmds.ls(type="ikHandle")
            for ik in sel:
                cmds.setAttr("%s.visibility" % ik, 0)

        for j in range(2):
            locators = cmds.spaceLocator(name="HelpLocsB_0" + str(j))
            heel = "R_Back_Toe01_Jt"
            print(locators)
            if cmds.ls("HelpLocsB_00", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locators, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] - 1))
            if cmds.ls("HelpLocsB_01", selection=True):
                val_heel = cmds.xform(heel, ws=True, translation=True, query=True)
                cmds.xform(locators, ws=True, t=(val_heel[0], val_heel[1], val_heel[2] + 1))
                sl = cmds.ls(type="locator")
                for k in sl:
                    cmds.setAttr("%s.visibility" % k, 0)

        group_locator = cmds.group("HelpLocsB_00", "HelpLocsB_01", n="GRP_LocsB")
        cmds.parent(group_locator, "ikHandle_R_Back_Ctrl_Heel")
        cmds.parent("ikHandle_R_Back_Ctrl_Heel", "R_Back_Foot_Ctrl")
        cmds.parent("R_Back_Feet_Ctrl", "R_Back_Foot_Ctrl")

        # Knee
        knee_l_front_jt = "L_Back_Knee_Jt"
        knee_r_front_jt = "R_Back_Knee_Jt"
        # Left Knee Cap
        knee_l_front_cap = [cmds.curve(name=prefix_l + "_Knee_Back_Cap", d=1,
                                       p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                          (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                          (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                          (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                          (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                          (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                          (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                          (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                          (-4, 0, 0)]),
                            cmds.scale(0.2, 0.2, 0.2),
                            cmds.setAttr(prefix_l + "_Knee_Back_Cap.rotateZ", -90),
                            cmds.setAttr(prefix_l + "_Knee_Back_Cap.scale", lock=True),
                            cmds.setAttr(prefix_l + "_Knee_Back_Cap.scale", lock=True),
                            cmds.setAttr(prefix_l + "_Knee_Back_Cap.overrideColor", 6),
                            cmds.setAttr(prefix_l + "_Knee_Back_Cap.overrideEnabled", 1)]
        cmds.xform(knee_l_front_jt + ".tx", knee_l_front_jt + ".ty", knee_l_front_jt + ".tz")
        val_knee = cmds.xform(knee_l_front_jt, query=True, ws=True, translation=True)
        cmds.xform(knee_l_front_cap[0], ws=1, t=(val_knee[0] + 1, val_knee[1], val_knee[2]))
        cmds.poleVectorConstraint(prefix_l + "_Knee_Back_Cap", "ikHandle_L_Back_Ctrl_Ankle")
        cmds.makeIdentity(t=True, a=True, r=True)

        # Right Knee Cap
        knee_r_front_cap = [cmds.curve(name=prefix_r + "_Knee_Back_Cap", d=1,
                                       p=[(-4, 0, 0), (-2, 3.146, -1.5), (-2, 3.464, -0.5),
                                          (-0.5, 3.9680, -0.5), (-0.5, 3.464, -2), (-1.5, 3.146, -2),
                                          (0, 0, -4), (1.5, 3.146, -2), (0.5, 3.464, -2),
                                          (0.5, 3.968, -0.5), (2, 3.464, -0.5), (2, 3.146, -1.5),
                                          (4, 0, 0), (2, 3.146, 1.5), (2, 3.464, 0.5),
                                          (0.5, 3.968, 0.5), (0.5, 3.464, 2), (1.5, 3.146, 2),
                                          (0, 0, 4), (-1.5, 3.146, 2), (-0.5, 3.464, 2),
                                          (-0.5, 3.968, 0.5), (-2, 3.464, 0.5), (-2, 3.146, 1.5),
                                          (-4, 0, 0)]),
                            cmds.scale(0.2, 0.2, 0.2),
                            cmds.setAttr(prefix_r + "_Knee_Back_Cap.rotateZ", -90),
                            cmds.setAttr(prefix_r + "_Knee_Back_Cap.scale", lock=True),
                            cmds.setAttr(prefix_r + "_Knee_Back_Cap.overrideColor", 3.5),
                            cmds.setAttr(prefix_r + "_Knee_Back_Cap.overrideEnabled", 1)]
        cmds.xform(knee_r_front_jt + ".tx", knee_r_front_jt + ".ty", knee_r_front_jt + ".tz")
        val_knee = cmds.xform(knee_r_front_jt, query=True, ws=True, translation=True)
        cmds.xform(knee_r_front_cap[0], ws=1, t=(val_knee[0] + 1, val_knee[1], val_knee[2]))
        cmds.poleVectorConstraint(prefix_r + "_Knee_Back_Cap", "ikHandle_R_Back_Ctrl_Ankle")
        cmds.makeIdentity(t=True, a=True, r=True)

        # Lock the scale attributes for both feet
        cmds.setAttr(prefix_l + "_Back_Foot_Ctrl.scale", lock=True)
        cmds.setAttr(prefix_r + "_Back_Foot_Ctrl.scale", lock=True)
        return left_foot, right_foot

    @staticmethod
    def create_spine_control(*args, **kwargs):
        prefix = "_"
        # Near Spine
        rear_spine_control = [cmds.curve(name="Rear_Spine" + prefix + "Ctrl", d=3,
                                       p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                          (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                          (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                          (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                          (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                          (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                          (-4.993259, 0, -0.0116669)]),
                              cmds.scale(0.5, 2.0, 0.5),
                              cmds.setAttr("Rear_Spine" + prefix + "Ctrl.scale", lock=True),
                              cmds.setAttr("Rear_Spine" + prefix + "Ctrl.rotateX", 90),
                              cmds.setAttr("Rear_Spine" + prefix + "Ctrl.rotateY", 90),
                              cmds.setAttr("Rear_Spine" + prefix + "Ctrl.overrideColor", 14),
                              cmds.setAttr("Rear_Spine" + prefix + "Ctrl.overrideEnabled", 1)]

        ik_spine_one = cmds.ikHandle(name="Ik" + prefix + "Spine_01", startJoint="B03", endEffector="B_Back_Hip_Jt", solver="ikRPsolver", parentCurve=False)
        rear_spine_jt = "B04"
        rear_spine_val = cmds.xform(rear_spine_jt, translation=True, query=True, ws=True)
        cmds.xform(rear_spine_control[0], ws=1, t=(rear_spine_val[0], rear_spine_val[1], rear_spine_val[2]))
        cmds.makeIdentity("Rear_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        cmds.parentConstraint("Rear_Spine_Ctrl", rear_spine_jt, mo=True)
        sel = cmds.ls(type="ikHandle")
        for ik in sel:
            cmds.setAttr("%s.visibility" % ik, 0)

        # Middle Spine
        middle_spine_control = [cmds.curve(name="Middle_Spine" + prefix + "Ctrl", d=3,
                                         p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                            (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                            (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                            (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                            (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                            (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                            (-4.993259, 0, -0.0116669)]),
                                cmds.scale(0.55, 2.0, 0.6),
                                cmds.setAttr("Middle_Spine" + prefix + "Ctrl.scale", lock=True),
                                cmds.setAttr("Middle_Spine" + prefix + "Ctrl.rotateX", 90),
                                cmds.setAttr("Middle_Spine" + prefix + "Ctrl.rotateY", 90),
                                cmds.setAttr("Middle_Spine" + prefix + "Ctrl.overrideColor", 14),
                                cmds.setAttr("Middle_Spine" + prefix + "Ctrl.overrideEnabled", 1)]

        ik_spine_two = cmds.ikHandle(name="Ik" + prefix + "Spine_02", startJoint="B01", endEffector="B03", solver="ikRPsolver", parentCurve=False)
        middle_spine_jt = "B02"
        middle_spine_val = cmds.xform(middle_spine_jt, translation=True, query=True, ws=True)
        cmds.xform(middle_spine_control[0], ws=1, t=(middle_spine_val[0], middle_spine_val[1], middle_spine_val[2]))
        cmds.makeIdentity("Middle_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        cmds.parentConstraint("Middle_Spine_Ctrl", middle_spine_jt, mo=True)

        ik_extra_spine = cmds.ikHandle(name="Ik" + prefix + "Spine_Support", startJoint="A_Front_Hip_Jt", endEffector="B01", solver="ikRPsolver", parentCurve=False)
        cmds.parent("Ik" + prefix + "Spine_Support", "Middle_Spine_Ctrl")
        sel = cmds.ls(type="ikHandle")
        for ik in sel:
            cmds.setAttr("%s.visibility" % ik, 0)

        # Front Spine
        front_spine_control = [cmds.curve(name="Front_Spine" + prefix + "Ctrl", d=3,
                                        p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                           (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                           (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                           (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                           (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                           (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                           (-4.993259, 0, -0.0116669)]),
                               cmds.scale(0.45, 2.0, 0.6),
                               cmds.setAttr("Front_Spine" + prefix + "Ctrl.overrideColor", 14),
                               cmds.setAttr("Front_Spine" + prefix + "Ctrl.overrideEnabled", 1),
                               cmds.setAttr("Front_Spine" + prefix + "Ctrl.rotateX", 90),
                               cmds.setAttr("Front_Spine" + prefix + "Ctrl.rotateY", 90)]
        front_spine_jt = "A_Front_Hip_Jt"
        front_spine_val = cmds.xform(front_spine_jt, translation=True, query=True, ws=True)
        cmds.xform(front_spine_control[0], ws=1, t=(front_spine_val[0], front_spine_val[1], front_spine_val[2]))
        cmds.makeIdentity("Front_Spine" + prefix + "Ctrl", t=True, r=True, a=True)
        cmds.setAttr("Front_Spine" + prefix + "Ctrl.scale", lock=True)
        cmds.parentConstraint("Front_Spine_Ctrl", front_spine_jt, mo=True)
        cmds.parentConstraint("Middle_Spine_Ctrl", "B03", mo=True)
        cmds.parentConstraint("Rear_Spine_Ctrl", "B03", mo=True)

        # Main Spine
        main_spine_control = [cmds.curve(name="Main_Spine" + prefix + "Ctrl", d=3,
                                       p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                          (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                          (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                          (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                          (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                          (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                          (-4.993259, 0, -0.0116669)]),
                              cmds.scale(0.657, 2.887, 1.0),
                              cmds.setAttr("Main_Spine" + prefix + "Ctrl.overrideColor", 30),
                              cmds.setAttr("Main_Spine" + prefix + "Ctrl.overrideEnabled", 1),
                              cmds.setAttr("Main_Spine" + prefix + "Ctrl.rotateX", 90),
                              cmds.setAttr("Main_Spine" + prefix + "Ctrl.rotateY", 90),
                              cmds.setAttr("Main_Spine" + prefix + "Ctrl.rotateZ", -180)]
        main_spine_jt = "B02"
        main_spine_val = cmds.xform(main_spine_jt, translation=True, query=True, ws=True)
        cmds.xform(main_spine_control[0], ws=1, t=(main_spine_val[0], main_spine_val[1], main_spine_val[2]))
        cmds.makeIdentity("Main_Spine" + prefix + "Ctrl", t=True, r=True, s=True, a=True)
        cmds.setAttr("Main_Spine" + prefix + "Ctrl.scale", lock=True)
        cmds.group("Rear_Spine_Ctrl", "Middle_Spine_Ctrl", "Front_Spine_Ctrl", "R_Shoulder_Ctrl", "L_Shoulder_Ctrl", name="GRP_All_Spine_Ctrl")
        cmds.parent("GRP_All_Spine_Ctrl", "Main_Spine_Ctrl")
        cmds.group("L_Shoulder_Ctrl", "R_Shoulder_Ctrl", name="GRP_Shoulder_Ctrl")
        cmds.parent("GRP_Shoulder_Ctrl", "Front_Spine_Ctrl")

    @staticmethod
    def create_neck_control(*args, **kwargs):
        neck_jt = "Neck_Jt"
        neck_ctrl = [cmds.curve(name="Neck_Ctrl", degree=3,
                               point=[(-0.801407, 0, 0.00716748), (-0.802768, 0.023587, -0.220859),
                                      (-0.805489, 0.0707609, -0.676912), (0.761595, -0.283043, -0.667253),
                                      (1.045492, -0.194522, -0.0218101), (1.046678, -0.194804, 0.0403576),
                                      (0.758039, -0.282198, 0.63974), (-0.806291, 0.0676615, 0.650803),
                                      (-0.803035, 0.0225538, 0.221713), (-0.801407, 0, 0.00716748)]),
                     cmds.setAttr("Neck_Ctrl.overrideColor", 18),
                     cmds.setAttr("Neck_Ctrl.overrideEnabled", 1)]
        cmds.scale(2.1, 3.16, 2.8)
        cmds.makeIdentity('Neck_Ctrl', apply=True, translate=True, scale=True)
        lock_scaling = cmds.setAttr("Neck_Ctrl.scale", lock=True)
        val_neck = cmds.xform(neck_jt, ws=True, query=True, translation=True)
        cmds.xform(neck_ctrl, ws=1, t=(val_neck[0], val_neck[1], val_neck[2]))
        cmds.orientConstraint("Neck_Ctrl", neck_jt)
        cmds.pointConstraint("Neck_Ctrl", neck_jt)
        grp_neck = cmds.group("Neck_Ctrl", name="GRP_Neck")
        cmds.parent("GRP_Neck", "Front_Spine_Ctrl")
        lock_translation = cmds.setAttr("Neck_Ctrl.translate", lock=True)
        return neck_ctrl, neck_jt

    @staticmethod
    def create_head_control(*args, **kwargs):
        head_jt = "Head_Jt"
        head_ctrl = [cmds.circle(name="Head_Ctrl"), cmds.setAttr("Head_Ctrl.overrideColor", 18), cmds.setAttr("Head_Ctrl.overrideEnabled", 1), cmds.scale(1.5, 1.5, 2.5)]
        val_head = cmds.xform(head_jt, ws=True, query=True, translation=True)
        cmds.xform(head_ctrl[0], ws=1, t=(val_head[0], val_head[1], val_head[2]))
        rot_head = cmds.xform(head_jt, ws=True, query=True, rotation=True)
        angle = 90
        cmds.xform(head_ctrl[0], ws=1, ro=(rot_head[0], rot_head[1] - angle, rot_head[2]))
        cmds.makeIdentity("Head_Ctrl", apply=True, translate=True, scale=True, rotate=True)
        lock_scaling = cmds.setAttr("Head_Ctrl.scale", lock=True)
        cmds.parentConstraint(head_ctrl[0], head_jt)
        grp_head = cmds.group(head_ctrl[0], name="GRP_Head_Ctrl")
        cmds.parent("GRP_Head_Ctrl", "Neck_Ctrl")
        lock_translation = cmds.setAttr("Head_Ctrl.translate", lock=True)
        ear_joint = ["L_Ear_Jt", "R_Ear_Jt"]

        if ear_joint[0]:
            prefix = "_"
            ear_control = [cmds.curve(name="L_Ear" + prefix + "Ctrl", d=3,
                                     p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                        (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                        (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                        (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                        (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                        (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                        (-4.993259, 0, -0.0116669)]),
                           cmds.scale(0.1, 0.5, 0.15),
                           cmds.setAttr("L_Ear" + prefix + "Ctrl.scale", lock=True),
                           cmds.setAttr("L_Ear" + prefix + "Ctrl.overrideColor", 6),
                           cmds.setAttr("L_Ear" + prefix + "Ctrl.overrideEnabled", 1)]
            val_ear = cmds.xform(ear_joint[0], ws=True, query=True, translation=True)
            cmds.xform(ear_control, ws=1, t=(val_ear[0], val_ear[1], val_ear[2]))
            rot_ear = cmds.xform(ear_joint[0], ws=True, query=True, rotation=True)
            cmds.xform(ear_control, ws=1, ro=(rot_ear[0], rot_ear[1], rot_ear[2]))
            cmds.makeIdentity(ear_control[0], a=True, t=True)

            for lock in ear_control:
                cmds.setAttr("L_Ear" + prefix + "Ctrl.translate", lock=True)
            cmds.orientConstraint(ear_control, ear_joint[0], mo=True)
            grp_ear_left = cmds.group(ear_control, name="GRP_L_Ear_Ctrl")
            cmds.parent("GRP_L_Ear_Ctrl", "Head_Ctrl")

        if ear_joint[1]:
            prefix = "_"
            ear_control = [cmds.curve(name="R_Ear" + prefix + "Ctrl", d=3,
                                     p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                        (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                        (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                        (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                        (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                        (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                        (-4.993259, 0, -0.0116669)]),
                           cmds.scale(0.1, 0.5, 0.15),
                           cmds.setAttr("R_Ear" + prefix + "Ctrl.scale", lock=True),
                           cmds.setAttr("R_Ear" + prefix + "Ctrl.overrideColor", 3.5),
                           cmds.setAttr("R_Ear" + prefix + "Ctrl.overrideEnabled", 1)]
            val_ear = cmds.xform(ear_joint[1], ws=True, query=True, translation=True)
            cmds.xform(ear_control, ws=1, t=(val_ear[0], val_ear[1] - 0.1, val_ear[2]))
            rot_ear = cmds.xform(ear_joint[1], ws=True, query=True, rotation=True)
            cmds.xform(ear_control, ws=1, ro=(rot_ear[0], rot_ear[1] - 180, rot_ear[2]))
            cmds.makeIdentity(ear_control[0], a=True, r=True, t=True)

            for lock in ear_control:
                cmds.setAttr("R_Ear" + prefix + "Ctrl.translate", lock=True)
            cmds.orientConstraint(ear_control, ear_joint[1], mo=True)
            grp_ear_right = cmds.group(ear_control, name="GRP_R_Ear_Ctrl")
            cmds.parent("GRP_R_Ear_Ctrl", "Head_Ctrl")
        return head_ctrl, head_jt

    @staticmethod
    def create_jaw_control(*args, **kwargs):
        prefix = "_"
        jaw_jt = "Lower_Jaw_Jt"
        jaw_ctrl = [cmds.curve(name="Jaw" + prefix + "Ctrl", d=1,
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
                    cmds.setAttr("Jaw" + prefix + "Ctrl.overrideColor", 18),
                    cmds.setAttr("Jaw" + prefix + "Ctrl.overrideEnabled", 1),
                    cmds.scale(0.5, 1, 1.15)]
        val_pos = cmds.xform(jaw_jt, query=True, ws=True, translation=True)
        cmds.xform(jaw_ctrl[0], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
        val_rot = cmds.xform(jaw_jt, query=True, ws=True, rotation=True)
        cmds.xform(jaw_ctrl[0], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
        cmds.setAttr("Jaw" + prefix + "Ctrl.rotateZ", -22)
        cmds.makeIdentity(jaw_ctrl[0], a=True, r=True, t=True, s=True)
        cmds.orientConstraint(jaw_ctrl[0], jaw_jt, mo=True)
        cmds.pointConstraint(jaw_ctrl[0], jaw_jt, mo=True)
        cmds.parent(jaw_ctrl[0], "Head_Ctrl")
        for lock in jaw_jt:
            cmds.setAttr("Jaw" + prefix + "Ctrl.scale", lock=True),
            cmds.setAttr("Jaw" + prefix + "Ctrl.translate", lock=True)

    @staticmethod
    def create_tongue_control(*args, **kwargs):
        tongue_joints = ["First_Tongue_Jt", "Second_Tongue_Jt", "Third_Tongue_Jt", "Fourth_Tongue_Jt", "Fifth_Tongue_Jt"]

        for tongue_ring in range(len(tongue_joints)):
            controls = [cmds.circle(name="Tongue_Ctrl_" + str(tongue_ring)), cmds.scale(0.5, 0.3, 0.5),
                        cmds.setAttr("Tongue_Ctrl_" + str(tongue_ring) + ".overrideColor", 18),
                        cmds.setAttr("Tongue_Ctrl_" + str(tongue_ring) + ".overrideEnabled", 1)]
            val_pos = cmds.xform(tongue_joints[tongue_ring], query=True, ws=True, translation=True)
            cmds.xform(controls[tongue_ring - 1], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
            val_rot = cmds.xform(tongue_joints[tongue_ring], query=True, ws=True, rotation=True)
            cmds.xform(controls[tongue_ring - 1], ws=1, ro=(val_rot[0], val_rot[1] - 90, val_rot[2] - 15))
            cmds.makeIdentity("Tongue_Ctrl_" + str(tongue_ring), a=True, r=True, t=True, s=True)
            orient = cmds.orientConstraint("Tongue_Ctrl_" + str(tongue_ring), tongue_joints[tongue_ring], maintainOffset=True)

        cmds.parent("Tongue_Ctrl_4", "Tongue_Ctrl_3")
        cmds.parent("Tongue_Ctrl_3", "Tongue_Ctrl_2")
        cmds.parent("Tongue_Ctrl_2", "Tongue_Ctrl_1")
        cmds.parent("Tongue_Ctrl_1", "Tongue_Ctrl_0")
        cmds.parent("Tongue_Ctrl_0", "Jaw_Ctrl")
        for lock in range(len(tongue_joints)):
            cmds.setAttr("Tongue_Ctrl_" + str(lock) + ".scale", lock=True),
            cmds.setAttr("Tongue_Ctrl_" + str(lock) + ".translate", lock=True)

    @staticmethod
    def create_tail_control(*args, **kwargs):
        tail_joints = ["Tail_Jt_A", "Tail_Jt_B", "Tail_Jt_C", "Tail_Jt_D", "Tail_Jt_E"]
        for tail_ring in range(len(tail_joints)):
            controls = [cmds.curve(name="Tail_Ctrl_" + str(tail_ring), d=3,
                                   p=[(-4.989444, 0, -0.0187419), (-4.686256, -0.000568063, -0.857419),
                                      (-4.079881, -0.00170419, -2.534775), (-0.0833425, 0.00681676, -4.722625),
                                      (4.329076, -0.0255628, -2.526971), (5.151345, 0.0954346, 0.477471),
                                      (5.150315, -0.356176, 0.504635), (4.332163, -0.233588, -2.496013),
                                      (-0.0870331, -0.27233, -4.710393), (-4.050575, -0.23995, -2.687489),
                                      (-5.22893, -0.330726, 0.650995), (-5.071816, -0.110242, 0.20922),
                                      (-4.993259, 0, -0.0116669)]),
                        cmds.scale(0.15, 0.65, 0.20),
                        cmds.setAttr("Tail_Ctrl_" + str(tail_ring) + ".overrideColor", 22),
                        cmds.setAttr("Tail_Ctrl_" + str(tail_ring) + ".overrideEnabled", 1)]
            val_pos = cmds.xform(tail_joints[tail_ring], query=True, ws=True, translation=True)
            cmds.xform(controls[tail_ring - 1], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
            val_rot = cmds.xform(tail_joints[tail_ring], query=True, ws=True, rotation=True)
            cmds.xform(controls[tail_ring - 1], ws=1, ro=(val_rot[0], val_rot[1] + 90, val_rot[2] - 90))
            cmds.makeIdentity("Tail_Ctrl_" + str(tail_ring), a=True, r=True, t=True, s=True)
            orient = cmds.orientConstraint("Tail_Ctrl_" + str(tail_ring), tail_joints[tail_ring], maintainOffset=True)
        cmds.parent("Tail_Ctrl_4", "Tail_Ctrl_3")
        cmds.parent("Tail_Ctrl_3", "Tail_Ctrl_2")
        cmds.parent("Tail_Ctrl_2", "Tail_Ctrl_1")
        cmds.parent("Tail_Ctrl_1", "Tail_Ctrl_0")
        cmds.group("Tail_Ctrl_0", name="GRP_Tail_Master")
        cmds.parent("GRP_Tail_Master", "Rear_Spine_Ctrl")
        for lock in range(len(tail_joints)):
            cmds.setAttr("Tail_Ctrl_" + str(lock) + ".scale", lock=True),
            cmds.setAttr("Tail_Ctrl_" + str(lock) + ".translate", lock=True)
        return tail_joints

    @staticmethod
    def create_master_control(*args, **kwargs):
        cmds.circle(name="Tiger_Ctrl")
        cmds.scale(8.77, 8.77, 8.77)
        cmds.setAttr("Tiger_Ctrl.rotateX", 90)
        cmds.setAttr("Tiger_Ctrl.overrideColor", 10)
        cmds.setAttr("Tiger_Ctrl.overrideEnabled", 1)
        cmds.makeIdentity("Tiger_Ctrl", s=True, r=True, t=True, a=True)
        cmds.group("Main_Spine_Ctrl", "R_Front_Foot_Ctrl", "L_Front_Foot_Ctrl", "R_Back_Foot_Ctrl", "L_Back_Foot_Ctrl", "R_Elbow_Front_Cap", "L_Elbow_Front_Cap", "R_Knee_Back_Cap", "L_Knee_Back_Cap", name="GRP_S_Main_Ctrl")
        cmds.parent("GRP_S_Main_Ctrl", "Tiger_Ctrl")
        cmds.setAttr("Tiger_Ctrl.scale", lock=True)

        # Bigger Controller
        cmds.circle(name="Main_Tiger_Ctrl")
        cmds.scale(9.77, 9.77, 9.77)
        cmds.setAttr("Main_Tiger_Ctrl.rotateX", 90)
        cmds.setAttr("Main_Tiger_Ctrl.overrideColor", 0)
        cmds.setAttr("Main_Tiger_Ctrl.overrideEnabled", 1)
        cmds.makeIdentity("Main_Tiger_Ctrl", s=True, r=True, t=True, a=True)
        cmds.group("Tiger_Ctrl", "A_Front_Hip_Jt", name="GRP_B_Main_Ctrl")
        cmds.parent("GRP_B_Main_Ctrl", "Main_Tiger_Ctrl")


class Animal_Skeleton(object):
    def __init__(self):
        self.f_hip_joint = None
        self.f_shoulder_joint = None
        self.f_elbow_joint = None
        self.f_wrist_joint = None
        self.f_toe_joint = None

        self.backbone_01 = None
        self.backbone_02 = None
        self.backbone_03 = None
        self.backbone_04 = None
        self.back_hip_joint = None

        self.b_pelvis_joint = None
        self.b_knee_joint = None
        self.b_heel_joint = None
        self.b_toe01_joint = None
        self.b_toe02_joint = None

        self.a_tail_joint = None
        self.b_tail_joint = None
        self.c_tail_joint = None
        self.d_tail_joint = None
        self.e_tail_joint = None
        self.f_tail_joint = None

        self.neck_joint = None
        self.head_joint = None
        self.jaw_joint = None

        self.ear_joint = None

        self.lower_jaw_joint = None
        self.tip_jaw_joint = None

        self.first_tongue_joint = None
        self.second_tongue_joint = None
        self.third_tongue_joint = None
        self.fourth_tongue_joint = None
        self.fifth_tongue_joint = None

    def create_front_legs_skeleton(self):
        self.f_hip_joint = cmds.joint(name='A_Front_Hip_Jt', position=(4.086, 8.755, 0.002))
        cmds.joint('A_Front_Hip_Jt', edit=True, zso=True, oj='xyz')
        self.f_shoulder_joint = cmds.joint(name='L_Front_Shoulder_Jt', position=(3.76, 6.725, -1.448))
        cmds.joint('L_Front_Shoulder_Jt', edit=True, zso=True, oj='xyz')
        self.f_elbow_joint = cmds.joint(name='L_Front_Elbow_Jt', position=(2.729, 4.374, -1.503))
        cmds.joint('L_Front_Elbow_Jt', edit=True, zso=True, oj='xyz')
        self.f_wrist_joint = cmds.joint(name='L_Front_Wrist_Jt', position=(3.5, 2.18, -1.466))
        cmds.joint('L_Front_Wrist_Jt', edit=True, zso=True, oj='xyz')
        self.f_toe_joint = cmds.joint(name='L_Front_WristExtra_Jt', position=(3.354, 0.388, -1.437))
        cmds.joint('L_Front_WristExtra_Jt', edit=True, zso=True, oj='xyz')
        self.f_toe_joint = cmds.joint(name='L_Front_Toe_Jt', position=(4.862, -0.144, -1.437))
        cmds.joint('L_Front_Toe_Jt', edit=True, zso=True, oj='xyz')
        cmds.select('A_Front_Hip_Jt')

    def create_spine_skeleton(self):
        cmds.select('A_Front_Hip_Jt')
        self.backbone_01 = cmds.joint(name='B01', position=(2.064, 8.829, 0.041))
        cmds.joint('B01', edit=True, zso=True, oj='xyz', sao='yup')
        self.backbone_02 = cmds.joint(name='B02', position=(0.216, 9.445, 0.038))
        cmds.joint('B02', edit=True, zso=True, oj='xyz', sao='yup')
        self.backbone_03 = cmds.joint(name='B03', position=(-1.813, 9.481, 0.042))
        cmds.joint('B03', edit=True, zso=True, oj='xyz', sao='yup')
        self.backbone_04 = cmds.joint(name='B04', position=(-3.761, 9.253, 0.038))
        cmds.joint('B04', edit=True, zso=True, oj='xyz', sao='yup')
        self.back_hip_joint = cmds.joint(name='B_Back_Hip_Jt', position=(-5.321, 8.599, 0.04))
        cmds.joint('B_Back_Hip_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def create_back_legs_skeleton(self):
        cmds.select('B_Back_Hip_Jt')
        self.b_pelvis_joint = cmds.joint(name='L_Back_Pelvic_Jt', position=(-4.754, 7.296, -1.494))
        cmds.joint(name='L_Back_Pelvic_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.b_knee_joint = cmds.joint(name='L_Back_Knee_Jt', position=(-2.06, 5.671, -1.542))
        cmds.joint(name='L_Back_Knee_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.b_heel_joint = cmds.joint(name='L_Back_Heel_Jt', position=(-6.112, 2.462, -1.445))
        cmds.joint(name='L_Back_Heel_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.b_toe01_joint = cmds.joint(name='L_Back_Toe01_Jt', position=(-6.006, 0.25, -1.45))
        cmds.joint(name='L_Back_Toe01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.b_toe02_joint = cmds.joint(name='L_Back_Toe02_Jt', position=(-4.992, -0.103, -1.449))
        cmds.joint(name='L_Back_Toe02_Jt', edit=True, zso=True, oj='xyz', sao='yup')

    def create_tail_skeleton(self):
        cmds.select('B_Back_Hip_Jt')
        self.a_tail_joint = cmds.joint(name='Tail_Jt_A', position=(-6.141, 8.196, 0))
        cmds.joint(name='Tail_Jt_A', edit=True, zso=True, oj='xyz', sao='yup')
        self.b_tail_joint = cmds.joint(name='Tail_Jt_B', position=(-7.002, 7.895, 0))
        cmds.joint(name='Tail_Jt_B', edit=True, zso=True, oj='xyz', sao='yup')
        self.c_tail_joint = cmds.joint(name='Tail_Jt_C', position=(-7.77, 7.752, 0))
        cmds.joint(name='Tail_Jt_C', edit=True, zso=True, oj='xyz', sao='yup')
        self.d_tail_joint = cmds.joint(name='Tail_Jt_D', position=(-8.498, 7.719, 0))
        cmds.joint(name='Tail_Jt_D', edit=True, zso=True, oj='xyz', sao='yup')
        self.e_tail_joint = cmds.joint(name='Tail_Jt_E', position=(-9.225, 7.848, 0))
        cmds.joint(name='Tail_Jt_E', edit=True, zso=True, oj='xyz', sao='yup')
        self.f_tail_joint = cmds.joint(name='Tail_Jt_F', position=(-9.866, 8.115, 0))
        cmds.joint(name='Tail_Jt_F', edit=True, zso=True, oj='xyz', sao='yup')

    def create_head_skeleton(self):
        cmds.select('A_Front_Hip_Jt')
        self.neck_joint = cmds.joint(name='Neck_Jt', position=(6.016, 9.717, 0))
        cmds.joint(name='Neck_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.head_joint = cmds.joint(name='Head_Jt', position=(7.634, 12.322, 0))
        cmds.joint(name='Head_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        self.jaw_joint = cmds.joint(name='Jaw_Jt', position=(10.758, 10.99, 0))
        cmds.joint(name='Jaw_Jt', edit=True, zso=True, oj='xyz', sao='yup')
        cmds.select("A_Front_Hip_Jt")

    def create_ears_skeleton(self):
        cmds.select("Head_Jt")
        self.ear_joint = cmds.joint(name="L_Ear_Jt", position=(7.71, 12.503, -0.896))
        cmds.joint(name="L_Ear_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.ear_joint = cmds.joint(name="L_Ear_Tip_Jt", position=(7.515, 13.229, -1.142))
        cmds.joint(name="L_Ear_Tip_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def create_jaw_skeleton(self):
        cmds.select("Head_Jt")
        self.lower_jaw_joint = cmds.joint(name="Lower_Jaw_Jt", position=(7.723, 10.89, 0.0))
        cmds.joint(name="Lower_Jaw_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.tip_jaw_joint = cmds.joint(name="Tip_Jaw_Jt", position=(10.119, 9.707, 0.019))
        cmds.joint(name="Tip_Jaw_Jt", edit=True, zso=True, oj="xyz", sao="yup")

    def create_tongue_skeleton(self):
        cmds.select("Lower_Jaw_Jt")
        self.first_tongue_joint = cmds.joint(name="First_Tongue_Jt", position=(8.106, 11.268, 0.0))
        cmds.joint(name="First_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.second_tongue_joint = cmds.joint(name="Second_Tongue_Jt", position=(8.524, 11.148, 0.0))
        cmds.joint(name="Second_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.third_tongue_joint = cmds.joint(name="Third_Tongue_Jt", position=(8.838, 10.949, 0.0))
        cmds.joint(name="Third_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.fourth_tongue_joint = cmds.joint(name="Fourth_Tongue_Jt", position=(9.162, 10.698, 0.0))
        cmds.joint(name="Fourth_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")
        self.fifth_tongue_joint = cmds.joint(name="Fifth_Tongue_Jt", position=(9.47, 10.426, 0.0))
        cmds.joint(name="Fifth_Tongue_Jt", edit=True, zso=True, oj="xyz", sao="yup")

