# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
import random
import math
from functools import partial

"""
import human_rig as rig
import importlib
importlib.reload(rig)
window = rig.Human_rig_window()
window.create()
"""

class Human_rig_window(object):

	def __init__(self):
		self.window = 'ar_optionsWindow'
		self.title = 'Auto Rigging Tool'
		self.size = (340, 550)
		self.supportsToolAction = True

	def create(self):
		if cmds.window(self.window, exists=True):
			cmds.deleteUI(self.window, window=True)
		self.window = cmds.window(
			self.window,
			title=self.title,
			widthHeight=self.size,
			menuBar=True
		)
		self.show_common_menu()
		cmds.showWindow()
		
	def show_common_menu(self):
		# self.edit_menu = cmds.menu(label='Edit')
		self.edit_menu_division = cmds.menuItem(d=True)
		self.edit_menu_skeleton_radio = cmds.radioMenuItemCollection()
		self.edit_menu_tool = cmds.menuItem(
			label='As Tool',
			radioButton=True,
			enable=self.supportsToolAction,
			command=self.edit_menu_tool_command
		)
		#self.help_menu = cmds.menu(label='Help')
		#self.help_menu_item = cmds.menuItem(label='Help on %s' % self.title, command=self.help_menu_command)
		
		cmds.columnLayout(columnAttach=('both', 2), rowSpacing=4, columnWidth=340)
		cmds.text("BIPED CHARACTER", align="center")
		cmds.text("   ")
		cmds.text("Step 1: Create bipedal skeleton")
		self.button_skeleton_human = cmds.button(label='Human Skeleton',
												 command=partial(self.create_skeleton),
												 width=120, height=40)
		
		cmds.text("   ")
		cmds.text("Step 2: Create Leg controls")
		cmds.text(label='LOWER BODY CONTROL', align='center')
		button_rig_foot_ctrl = cmds.button(label='Legs Control',
										command=partial(self.feet_control),
										width=120, height=40)
		button_rig_spine_ctrl = cmds.button(label='Spine Control',
										 command=partial(self.spine_control),
										 width=120, height=40, align="center")

		cmds.text("   ")
		cmds.text("Step 3: Create Torso/Arm controls")
		cmds.text(label='UPPER BODY CONTROL', align='center')
		button_rig_arm_ctrl = cmds.button(label='Arm Control',
									   command=partial(self.arm_control),
									   width=120, height=40)
		button_rig_fingers_ctrl = cmds.button(label='Fingers Control',
										   command=partial(self.finger_control),
										   width=120, height=40)
		button_rig_head_ctrl = cmds.button(label='Head Control',
										command=partial(self.head_control),
										width=120, height=40)

		cmds.text("   ")
		cmds.text("Step 4: Create Master control")
		cmds.text("MASTER CONTROL", align='center')
		button_main_ctrl = cmds.button(label='Master Control',
									 command=partial(self.master_control),
									 width=120, height=40, align='center')
		close_button = cmds.button(label="Close",
								  command=partial(self.close_window),
								  width=120, height=40, align='center')
	
	def close_window(self, *args):
		if cmds.window(self.window, exists=True):
			cmds.deleteUI(self.window, window=True)

	def create_skeleton(self, *args):
		skeletonJT = Human_skeleton()
		skeletonJT.__create_spine_skeleton__()
		skeletonJT.__create_leg_skeleton__()
		skeletonJT.__create_arm_skeleton__()
		skeletonJT.__create_finger_skeleton__()
		skeletonJT.__mirror_joints_hands__()
		skeletonJT.__mirror_joints_legs__()

	def help_menu_command(self, *args):
		cmds.launch(web='http://www.maya-python.com/')

	def edit_menu_tool_command(self, *args):
		pass

	def edit_menu_action_command(self, *args):
		pass
	
	def feet_control(*args, **kwargs):
		feet_ctrl = list(range(2))
		Ankle = 'R_Ankle_Jt'
		foot_ctrl = True
		if foot_ctrl:
			#Left Foot	
			feet_ctrl[0] = cmds.curve(name="ik_LeftFoot_Ctrl", degree=1,
									  point=[(-0.440687, 0.0433772, 0.400889), (-0.440687, 0.0433772, -0.429444),
											 (0.898906, -0.240469, -0.384559), (0.975205, -0.496435, -0.384559),
											 (0.975205, -0.496435, 0.365874), (0.898906, -0.240469, 0.365874),
											 (0.898906, -0.240469, -0.384559), (-0.440687, 0.0433772, -0.429444),
											 (-0.440687, 0.0433772, 0.400889), (-0.520228, -0.496554, 0.400889),
											 (-0.520228, -0.496554, -0.429444), (-0.440687, 0.0433772, -0.429444),
											 (-0.440687, 0.0433772, 0.400889), (0.898906, -0.240469, 0.365874),
											 (0.975205, -0.496435, 0.365874), (-0.520228, -0.496554, 0.400889),
											 (-0.520228, -0.496554, -0.429444), (0.975205, -0.496435, -0.384559)],
									  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])
			ankle_left = 'L_Ankle_Jt'
			val_ik = cmds.xform(ankle_left, query=True, ws=True, translation=True)
			cmds.xform(feet_ctrl[0], ws=1, t=(val_ik[0], val_ik[1], val_ik[2]))
			# Ik Handles with foot bones
			cmds.ikHandle(name="ikHandle_L_Ctrl", startJoint="L_Hip_Jt",
						  endEffector="L_Ankle_Jt", solver="ikRPsolver", parentCurve=False)
			ik_left_mid_toe = cmds.ikHandle(name="ikHandle_L_Ctrl_MidToe", startJoint="L_Ankle_Jt",
										 endEffector="L_Toe_Jt", solver="ikRPsolver", parentCurve=False)
			ik_left_end_toe = cmds.ikHandle(name="ikHandle_L_Ctrl_Toe", startJoint="L_Toe_Jt",
										 endEffector="L_ToeEnd_Jt", solver="ikRPsolver", parentCurve=False)
			grp_ik_left = cmds.group("ikHandle_L_Ctrl", n="GrpIk_LeftLeg")
			cmds.parent(grp_ik_left, feet_ctrl[0])
			orient_left_foot = cmds.orientConstraint(feet_ctrl[0], "L_Ankle_Jt", maintainOffset=True)
			
			# Add parent Constraint and new controller to control feet rotation and its position
			toe_left = 'L_Toe_Jt'
			left_toe_rot = cmds.curve(name="Left_Toe_Rotation", d=1,
									p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
									   (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
									   (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
									   (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2), (-0.5, 0, 0)])
			scale = cmds.scale(0.15, 0.15, 0.15)
			val_toe = cmds.xform(toe_left, query=True, ws=True, translation=True)
			cmds.xform(left_toe_rot, ws=1, t=(val_toe[0], val_toe[1], val_toe[2]))
			parent_left_foot = cmds.parentConstraint(left_toe_rot, "L_Toe_Jt", maintainOffset=True)
			cmds.parent(parent_left_foot, feet_ctrl[0])
			left_foot_parent = cmds.parent(left_toe_rot, feet_ctrl[0])
			cmds.parent(ik_left_mid_toe, ik_left_end_toe, left_toe_rot)
			
			# Add ball rotation for left ankle 
			left_ball_curve = cmds.curve(name="LeftBallCtrl", degree=1,
										 point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
												(0.138488, 0, -0.990867), (-0.499831, 0, 0.0111455),
												(-0.0656259, 0, 1.009447), (-0.633433, 0, 1.013158),
												(-0.989704, 0, -0.00369912)],
										 knot=[0, 1, 2, 3, 4, 5, 6])
			left_ball_ctrl = [cmds.select("LeftBallCtrl", r=True), cmds.scale(0.4, 0.4, 0.4), cmds.rename('L_Ball_Rotation')]
			val_ball = cmds.xform(ankle_left, query=True, ws=True, translation=True)
			cmds.xform(left_ball_ctrl[0], ws=1, t=(val_ball[0], val_ball[1], val_ball[2]))
			cmds.rotate('90deg', 0, 0, left_ball_ctrl[0])
			cmds.parent("ikHandle_L_Ctrl", left_ball_ctrl[0])
			cmds.parent("L_Ball_Rotation", feet_ctrl[0])
			# Left knee cap
			knee_left = 'L_Knee_Jt'
			left_knee_cap = [cmds.CreateNURBSCircle(),
						   cmds.scale(0.3, 0.3, 0.3),
						   cmds.select("nurbsCircle1"),
						   cmds.rename("nurbsCircle1", 'L_KneeCap'),
						   cmds.setAttr('L_KneeCap.rz', 90)]
			cmds.xform(knee_left + ".tx", knee_left + ".ty", knee_left + ".tz")
			val_knee = cmds.xform(knee_left, query=True, ws=True, translation=True)
			cmds.xform(left_knee_cap[0], ws=1, t=(val_knee[0] + 2, val_knee[1], val_knee[2]))

			if left_knee_cap:
				cmds.poleVectorConstraint('L_KneeCap', 'ikHandle_L_Ctrl')
				#Right Foot
				feet_ctrl[1] = cmds.curve(name="ik_RightFoot_Ctrl", degree=1,
										  point=[(0.898914, -0.240476, 0.383674), (-0.440521, 0.0411603, 0.428909),
												 (-0.440521, 0.0411603, -0.400341), (0.898914, -0.240476, -0.365796),
												 (0.898914, -0.240476, 0.383674), (0.974311, -0.496509, 0.383674),
												 (0.974311, -0.496509, -0.365796), (-0.517088, -0.495087, -0.400341),
												 (-0.517088, -0.495087, 0.428909), (0.974311, -0.496509, 0.383674),
												 (0.898914, -0.240476, 0.383674), (-0.440521, 0.0411603, 0.428909),
												 (-0.517088, -0.495087, 0.428909), (-0.517088, -0.495087, -0.400341),
												 (-0.440521, 0.0411603, -0.400341), (0.898914, -0.240476, -0.365796),
												 (0.974311, -0.496509, -0.365796)],
										  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
				# Move pivot to ankle centre
				ankle_right = 'R_Ankle_Jt'
				val_ik_right = cmds.xform(ankle_right, query=True, ws=True, translation=True)
				if ankle_right != ankle_left:
					cmds.xform(feet_ctrl[1], ws=1, t=(val_ik_right[0], val_ik_right[1], val_ik_right[2]))
					cmds.ikHandle(name="ikHandle_R_Ctrl", startJoint="R_Hip_Jt",
								  endEffector="R_Ankle_Jt", solver="ikRPsolver", parentCurve=False)
					ik_right_mid_toe = cmds.ikHandle(name="ikHandle_R_Ctrl_MidToe", startJoint="R_Ankle_Jt",
												  endEffector="R_Toe_Jt", solver="ikRPsolver", parentCurve=False)
					ik_right_end_toe = cmds.ikHandle(name="ikHandle_R_Ctrl_Toe", startJoint="R_Toe_Jt",
												  endEffector="R_ToeEnd_Jt", solver="ikRPsolver", parentCurve=False)
					grp_ik_right = cmds.group("ikHandle_R_Ctrl", n="GrpIk_RightLeg")
					cmds.parent(grp_ik_right, feet_ctrl[1])
					orient_right_foot = cmds.orientConstraint(feet_ctrl[1], "R_Ankle_Jt", maintainOffset=True)

					toe_right = 'R_Toe_Jt'
					right_toe_rot = cmds.curve(name="Right_Toe_Rotation", d=1,
											   p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2),
												  (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
												  (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2),
												  (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
												  (-0.5, 0, 0)])

					scale = cmds.scale(0.15, 0.15, 0.15)
					val_toe_right = cmds.xform(toe_right, query=True, ws=True, translation=True)
					cmds.xform(right_toe_rot, ws=1, t=(val_toe_right[0], val_toe_right[1], val_toe_right[2]))
					parent_right_foot = cmds.parentConstraint(right_toe_rot, "R_Toe_Jt", maintainOffset=True)
					cmds.parent(parent_right_foot, feet_ctrl[1])
					left_foot_parent = cmds.parent(right_toe_rot, feet_ctrl[1])
					cmds.parent(ik_right_mid_toe, ik_right_end_toe, right_toe_rot)
					# Add ball rotation for left ankle 
					right_ball_curve = cmds.curve(name="RightBallCtrl", degree=1,
												  point=[(-0.989704, 0, -0.00369912), (-0.310562, 0, -0.998289),
														 (0.138488, 0, -0.990867), (-0.499831, 0, 0.0111455),
														 (-0.0656259, 0, 1.009447), (-0.633433, 0, 1.013158),
														 (-0.989704, 0, -0.00369912)],
												  knot=[0, 1, 2, 3, 4, 5, 6])

					right_ball_ctrl = [cmds.select("RightBallCtrl", r=True),
									 cmds.scale(0.4, 0.4, 0.4), cmds.rename('R_Ball_Rotation')]
					val_ball_right = cmds.xform(ankle_right, query=True, ws=True, translation=True)
					cmds.xform(right_ball_ctrl[0], ws=1, t=(val_ball_right[0], val_ball_right[1], val_ball_right[2]))
					cmds.rotate('90deg', 0, 0, right_ball_ctrl[0])
					cmds.parent("ikHandle_R_Ctrl", right_ball_ctrl[0])
					cmds.parent("R_Ball_Rotation", feet_ctrl[1])
					# Right Knee cap
					knee_right = 'R_Knee_Jt'
					right_knee_cap = [cmds.CreateNURBSCircle(),
									cmds.scale(0.3, 0.3, 0.3),
									cmds.select("nurbsCircle1"),
									cmds.rename("nurbsCircle1", 'R_KneeCap'),
									cmds.setAttr('R_KneeCap.rz', 90)]
					cmds.xform(knee_right + ".tx", knee_right + ".ty", knee_right + ".tz")
					val_knee_right = cmds.xform(knee_right, query=True, ws=True, translation=True)
					cmds.xform(right_knee_cap[0], ws=1, t=(val_knee_right[0] + 2, val_knee_right[1], val_knee_right[2]))
					if right_knee_cap:
						cmds.poleVectorConstraint('R_KneeCap', 'ikHandle_R_Ctrl')
						#Creating group for both feet
						grp = cmds.group(em=True, name="Foot_Grp")
						cmds.parent(feet_ctrl, 'Foot_Grp', relative=True)
						cmds.move(-0.24, 0.486, -0.689, grp + ".scalePivot", grp + ".rotatePivot", absolute=True)
						grp_knees = cmds.group(em=True, name="Knee_Grp")
						cmds.parent(right_knee_cap, left_knee_cap, grp_knees)

	def spine_control(*args, **kwargs):
		scale_parts = 0.4
		ctrl = True
		body_part = list(range(2))
		parent_part = {"Hip_Jt_1": 1, "D_Neck_Jt": 2, "A_Hip_Jt": 3}
		joint_list = ["A_Hip_Jt", "Hip_Jt_0", "Hip_Jt_1", "Hip_Jt_2", "Hip_Jt_2", "D_Neck_Jt"]
		if ctrl:
			if parent_part["A_Hip_Jt"]:
				body_part[0] = cmds.curve(name="Ik_hip_ctrl", degree=1,
										  point=[(-2.5, 0.6, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9),
												 (-2.5, 0.6, -1.9), (-2.5, 0.6, 1.9), (-2.5, -2.1, 1.9),
												 (2.5, -2.1, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9),
												 (2.5, -2.1, -1.9), (2.5, -2.1, 1.9), (-2.5, -2.1, 1.9),
												 (-2.5, -2.1, -1.9), (-2.5, 0.6, -1.9), (-2.5, -2.1, -1.9),
												 (2.5, -2.1, -1.9)],
										  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
				hip_pos = [cmds.scale(scale_parts, scale_parts, scale_parts), cmds.setAttr(body_part[0] + ".ry", 90)]
				hip_jt = "A_Hip_Jt"
				val_hip = cmds.xform(hip_jt, ws=True, query=True, translation=True)
				cmds.xform(body_part[0], ws=1, t=(val_hip[0], val_hip[1], val_hip[2]))
						
				if parent_part != "A_Hip_Jt":
					body_part[1] = cmds.curve(name="Ik_shoulder_ctrl", degree=1,
											  point=[(2.3, -0.3, 1.6), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3),
													 (-2.3, -0.3, 1.6), ( 2.3, -0.3, 1.6), (2.5, -2.7, 1.9),
													 (-2.5, -2.7, 1.9), (-2.5, -2.7, -1.9), (2.5, -2.7, -1.9),
													 (2.5, -2.7, 1.9), (2.5, -2.7, -1.9), (2.2, 0.2, -1.3),
													 (-2.2, 0.2, -1.3), (-2.5, -2.7, -1.9), (-2.5, -2.7, 1.9),
													 (-2.3, -0.3, 1.6)],
											  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
					shoulders_pos = [cmds.scale(scale_parts, scale_parts, scale_parts),
									 cmds.setAttr(body_part[1] + ".ry", 90)]
					sho_jt = "D_Neck_Jt"
					val_sho = cmds.xform(sho_jt, ws=True, query=True, translation=True)
					cmds.xform(body_part[1], ws=1, t=(val_sho[0], val_sho[1], val_sho[2]))
					spine_ik = cmds.ikHandle(name="Spine_Ik", startJoint=joint_list[3],
											endEffector=joint_list[5], solver="ikSCsolver", parentCurve=False)
							
					# Middle spine control
					if parent_part["Hip_Jt_1"]:
						mid_spine = 'Hip_Jt_1'
						to_contol_joints = joint_list[1], joint_list[2]
						spine_01 = cmds.ikHandle(name="Spine_Ik_01", startJoint=joint_list[0],
												 endEffector=joint_list[2], solver="ikSCsolver", parentCurve=False)
						mid_spine_ctrl = [cmds.CreateNURBSCircle(),
										cmds.scale(1.2, 1.2, 1.2),
										cmds.select("nurbsCircle1"),
										cmds.rename("nurbsCircle1", 'S_Ctrl')]
						cmds.xform(mid_spine + ".tx", mid_spine + ".ty", mid_spine + ".tz")
						val_mid_spine = cmds.xform(mid_spine, query=True, ws=True, translation=True)
						cmds.xform(mid_spine_ctrl[0], ws=1, t=(val_mid_spine[0], val_mid_spine[1], val_mid_spine[2]))
								
					elif ctrl is not True:
						if parent_part["A_Hip_Jt", "D_Neck_Jt", "Hip_Jt_1"] is False:
							parent_part.clear()
							cmds.delete()
							print(ctrl)
					else:
						cmds.error("No selection to control")

				cmds.parent('Spine_Ik', 'Ik_shoulder_ctrl', world=False)
				cmds.orientConstraint('Ik_shoulder_ctrl', joint_list[5], maintainOffset=True)
				cmds.parentConstraint("S_Ctrl", "Spine_Ik_01", skipTranslate='y', maintainOffset=True)
				cmds.parentConstraint("Ik_hip_ctrl", joint_list[0], maintainOffset=True)
				cmds.parent("Ik_shoulder_ctrl", "S_Ctrl")
				cmds.parent("S_Ctrl", "Ik_hip_ctrl")
				cmds.parent("Spine_Ik_01", "S_Ctrl")
				cmds.group('Ik_hip_ctrl', name="UpperBody_Grp")
				return scale_parts, body_part, parent_part
			else:
				# parentPart["A_Hip_Jt"]
				pass
		else:
			# ctrl
			pass

	def arm_control(*args, **kwargs):
		arm_list_right = ["R_Collarbone_Jt", "R_Shoulder_Jt", "R_Wrist_Jt"]
		arm_list_left = ["L_Collarbone_Jt", "L_Shoulder_Jt", "L_Wrist_Jt"]
		arm_ctrl = True
		cmds.ikHandle(name="R_ArmCtrl", startJoint=arm_list_right[1],
					  endEffector=arm_list_right[2], solver="ikRPsolver", parentCurve=False)
		cmds.ikHandle(name="L_ArmCtrl", startJoint=arm_list_left[1],
					  endEffector=arm_list_left[2], solver="ikRPsolver", parentCurve=False)

		#Right arm fk controls
		for i in range(len(arm_list_right)):
			controls = [cmds.CreateNURBSCircle()]
			cmds.rename('nurbsCircle1', 'Fk_R_ForeArm_' + str(i))
			if i in range(len(arm_list_right)):
				scale_nurbs = 0.5
				cmds.rotate("-45deg", 0, 0, "Fk_R_ForeArm_" + str(i))
				cmds.scale(scale_nurbs, scale_nurbs, scale_nurbs)
		
		#Left arm fk controls
		for i in range(len(arm_list_left)):
			controls = [cmds.CreateNURBSCircle()]
			cmds.rename('nurbsCircle1', 'Fk_L_ForeArm_' + str(i))
			if i in range(len(arm_list_left)):
				scale_nurbs = 0.5
				cmds.rotate("45deg", 0, 0, "Fk_L_ForeArm_" + str(i))
				cmds.scale(scale_nurbs, scale_nurbs, scale_nurbs)
		
		fk_arm_right = ["Fk_R_ForeArm_0", "Fk_R_ForeArm_1", "Fk_R_ForeArm_2"]
		fk_arm_left = ["Fk_L_ForeArm_0", "Fk_L_ForeArm_1", "Fk_L_ForeArm_2"]
		
		#Right Arm
		if arm_ctrl:
			if fk_arm_right[0] is "Fk_R_ForeArm_0":
				#Collar Bone
				val_right_collar = cmds.xform(arm_list_right[0], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_right[0], ws=1, t=(val_right_collar[0], val_right_collar[1], val_right_collar[2]))
				cmds.rotate(0, 0, "90deg", fk_arm_right[0])
				orient = cmds.orientConstraint(fk_arm_right[0], arm_list_right[0], mo=True)
				parent = cmds.parentConstraint(fk_arm_right[0], arm_list_right[0], mo=True)
				cmds.parent(fk_arm_right[0], "Ik_shoulder_ctrl")
			if fk_arm_right[1] is "Fk_R_ForeArm_1":
				#Shoulder Bone
				val_right_shoulder = cmds.xform(arm_list_right[1], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_right[1], ws=1, t=(val_right_shoulder[0], val_right_shoulder[1], val_right_shoulder[2]))
				orient = cmds.orientConstraint(fk_arm_right[1], arm_list_right[1], mo=True)
				parent = cmds.parentConstraint(fk_arm_right[1], arm_list_right[1], mo=True)
				cmds.parent(fk_arm_right[1], "Ik_shoulder_ctrl")
			if fk_arm_right[2] is "Fk_R_ForeArm_2":
				#Wrist Bone
				val_right_wrist = cmds.xform(arm_list_right[2], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_right[2], ws=1, t=(val_right_wrist[0], val_right_wrist[1], val_right_wrist[2]))
				orient = cmds.orientConstraint(fk_arm_right[2], arm_list_right[2], mo=True)
				parent = cmds.parent("R_ArmCtrl", fk_arm_right[2])
				cmds.parent(fk_arm_right[2], "Ik_shoulder_ctrl")
				cmds.parent(fk_arm_right[2], fk_arm_right[1])
			else:
				return fk_arm_right

		#Left Arm
		if arm_ctrl:
			if fk_arm_left[0] is "Fk_L_ForeArm_0":
				#Collar Bone
				val_right_collar = cmds.xform(arm_list_left[0], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_left[0], ws=1, t=(val_right_collar[0], val_right_collar[1], val_right_collar[2]))
				cmds.rotate(0, 0, "90deg", fk_arm_left[0])
				orient = cmds.orientConstraint(fk_arm_left[0], arm_list_left[0], mo=True)
				parent = cmds.parentConstraint(fk_arm_left[0], arm_list_left[0], mo=True)
				cmds.parent(fk_arm_left[0], "Ik_shoulder_ctrl")
			if fk_arm_left[1] is "Fk_L_ForeArm_1":
				#Shoulder Bone
				val_right_shoulder = cmds.xform(arm_list_left[1], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_left[1], ws=1, t=(val_right_shoulder[0], val_right_shoulder[1], val_right_shoulder[2]))
				orient = cmds.orientConstraint(fk_arm_left[1], arm_list_left[1], mo=True)
				parent = cmds.parentConstraint(fk_arm_left[1], arm_list_left[1], mo=True)
				cmds.parent(fk_arm_left[1], "Ik_shoulder_ctrl")
			if fk_arm_left[2] is "Fk_L_ForeArm_2":
				#Wrist Bone
				val_right_wrist = cmds.xform(arm_list_left[2], query=True, ws=True, translation=True)
				cmds.xform(fk_arm_left[2], ws=1, t=(val_right_wrist[0], val_right_wrist[1], val_right_wrist[2]))
				orient = cmds.orientConstraint(fk_arm_left[2], arm_list_left[2], mo=True)
				parent = cmds.parent("L_ArmCtrl", fk_arm_left[2])
				cmds.parent(fk_arm_left[2], "Ik_shoulder_ctrl")
				cmds.parent(fk_arm_left[2], fk_arm_left[1])
			else:
				return fk_arm_left
					
		#Right elbow control
		elbow_right = 'R_Elbow_Jt'
		right_elbow_ctrl = [cmds.CreateNURBSCircle(),
						  cmds.scale(0.3, 0.3, 0.3),
						  cmds.select("nurbsCircle1"),
						  cmds.rename("nurbsCircle1", 'R_ElbowCtrl'),
						  cmds.setAttr('R_ElbowCtrl.rz', 90)]
		cmds.xform(elbow_right + ".tx", elbow_right + ".ty", elbow_right + ".tz")
		val_elbow = cmds.xform(elbow_right, query=True, ws=True, translation=True)
		cmds.xform(right_elbow_ctrl[0], ws=1, t=(val_elbow[0] - 0.6, val_elbow[1], val_elbow[2]))
		if right_elbow_ctrl:
			cmds.poleVectorConstraint(right_elbow_ctrl[3], 'R_ArmCtrl')
			cmds.parent(right_elbow_ctrl[3], fk_arm_right[2])
		
		#Left elbow control
		elbow_left = 'L_Elbow_Jt'
		left_elbow_ctrl = [cmds.CreateNURBSCircle(),
						 cmds.scale(0.3, 0.3, 0.3),
						 cmds.select("nurbsCircle1"),
						 cmds.rename("nurbsCircle1", 'L_ElbowCtrl'),
						 cmds.setAttr('L_ElbowCtrl.rz', 90)]
		cmds.xform(elbow_left + ".tx", elbow_left + ".ty", elbow_left + ".tz")
		val_elbow = cmds.xform(elbow_left, query=True, ws=True, translation=True)
		cmds.xform(left_elbow_ctrl[0], ws=1, t=(val_elbow[0] - 0.6, val_elbow[1], val_elbow[2]))
		if left_elbow_ctrl:
			cmds.poleVectorConstraint(left_elbow_ctrl[3], 'L_ArmCtrl')
			cmds.parent(left_elbow_ctrl[3], fk_arm_left[2])

		cmds.parent(fk_arm_right[1], fk_arm_right[0])
		cmds.parent(fk_arm_left[1], fk_arm_left[0])
		return fk_arm_right, fk_arm_left, arm_list_right, arm_list_left, arm_ctrl
		
	def finger_control(*args, **kwargs):
		wrist = True
		wrist_jt = ["R_Wrist_Jt", "L_Wrist_Jt"]

		# Create Wrists for both hands
		if wrist is True:
			# Right hand  side
			wrist_right = cmds.circle(name="Right_Wrist_Fk", ch=1, o=1, r=0.5, nr=(0, 1, 0))
			cmds.scale(0.5, 0.5, 0.5)
			val_wrist_right = cmds.xform(wrist_jt[0], query=True, ws=True, translation=True)
			cmds.xform(wrist_right, ws=1, t=(val_wrist_right[0], val_wrist_right[1], val_wrist_right[2]))
			val_rot_right = cmds.xform(wrist_jt[0], query=True, ws=True, rotation=True)
			cmds.xform(wrist_right, ws=1, ro=(val_rot_right[0], val_rot_right[1], val_rot_right[2]))
			orient_wrist = cmds.orientConstraint(wrist_right, wrist_jt[0], mo=True)
			# Parent to wrist control
			cmds.parent(wrist_right, "Fk_R_ForeArm_2")

			# Left hand  side
			wrist_left = cmds.circle(name="Left_Wrist_Fk", ch=1, o=1, r=0.5, nr=(0, 1, 0))
			cmds.scale(0.5, 0.5, 0.5)
			val_wrist_left = cmds.xform(wrist_jt[1], query=True, ws=True, translation=True)
			cmds.xform(wrist_left, ws=1, t=(val_wrist_left[0], val_wrist_left[1], val_wrist_left[2]))
			val_rot_left = cmds.xform(wrist_jt[1], query=True, ws=True, rotation=True)
			cmds.xform(wrist_left, ws=1, ro=(val_rot_left[0], val_rot_left[1], val_rot_left[2]))
			orient_wrist = cmds.orientConstraint(wrist_left, wrist_jt[1], mo=True)
			# Parent to wrist control
			cmds.parent(wrist_left, "Fk_L_ForeArm_2")
				
			# Lists of the right fingers joints 
			thumb_joints = ["R_Thumb01_Jt", "R_Thumb02_Jt"]
			index_joints = ["R_IndexFinger01_Jt", "R_IndexFinger02_Jt", "R_IndexFinger03_Jt"]
			middle_joints = ["R_MiddleFinger01_Jt", "R_MiddleFinger02_Jt", "R_MiddleFinger03_Jt"]
			ring_joints = ["R_RingFinger01_Jt", "R_RingFinger02_Jt", "R_RingFinger03_Jt"]
			pinky_joints = ["R_Pinky01_tJt", "R_Pinky02_Jt", "R_Pinky03_Jt"]

			# Right thumb 
			for thumbs in range(len(thumb_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Thumb_Ctrl_" + str(thumbs)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(thumb_joints[thumbs], query=True, ws=True, translation=True)
				cmds.xform(controls[thumbs], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(thumb_joints[thumbs], query=True, ws=True, rotation=True)
				cmds.xform(controls[thumbs], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("R_Thumb_Ctrl_*", thumb_joints[thumbs], maintainOffset=True)
				point = cmds.pointConstraint("R_Thumb_Ctrl_*", thumb_joints[thumbs], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("R_Thumb_Ctrl_1", "R_Thumb_Ctrl_0")
			cmds.parent("R_Thumb_Ctrl_0", "Right_Wrist_Fk")
				
			# Right index
			for index in range(len(index_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Index_Ctrl_" + str(index)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(index_joints[index], query=True, ws=True, translation=True)
				cmds.xform(controls[index], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(index_joints[index], query=True, ws=True, rotation=True)
				cmds.xform(controls[index], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("R_Index_Ctrl_*", index_joints[index], maintainOffset=True)
				point = cmds.pointConstraint("R_Index_Ctrl_*", index_joints[index], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("R_Index_Ctrl_2", "R_Index_Ctrl_1")
			cmds.parent("R_Index_Ctrl_1", "R_Index_Ctrl_0")
			cmds.parent("R_Index_Ctrl_0", "Right_Wrist_Fk")

			# Right middle
			for middle in range(len(middle_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Middle_Ctrl_" + str(middle)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(middle_joints[middle], query=True, ws=True, translation=True)
				cmds.xform(controls[middle], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(middle_joints[middle], query=True, ws=True, rotation=True)
				cmds.xform(controls[middle], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("R_Middle_Ctrl_*", middle_joints[middle], maintainOffset=True)
				point = cmds.pointConstraint("R_Middle_Ctrl_*", middle_joints[middle], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("R_Middle_Ctrl_2", "R_Middle_Ctrl_1")
			cmds.parent("R_Middle_Ctrl_1", "R_Middle_Ctrl_0")
			cmds.parent("R_Middle_Ctrl_0", "Right_Wrist_Fk")
				
			# Right ring
			for ring in range(len(ring_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Ring_Ctrl_" + str(ring)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(ring_joints[ring], query=True, ws=True, translation=True)
				cmds.xform(controls[ring], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(ring_joints[ring], query=True, ws=True, rotation=True)
				cmds.xform(controls[ring], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("R_Ring_Ctrl_*", ring_joints[ring], maintainOffset=True)
				point = cmds.pointConstraint("R_Ring_Ctrl_*", ring_joints[ring], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("R_Ring_Ctrl_2", "R_Ring_Ctrl_1")
			cmds.parent("R_Ring_Ctrl_1", "R_Ring_Ctrl_0")
			cmds.parent("R_Ring_Ctrl_0", "Right_Wrist_Fk")
				
			# Right pinky
			for pinky in range(len(pinky_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Pinky_Ctrl_" + str(pinky)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(pinky_joints[pinky], query=True, ws=True, translation=True)
				cmds.xform(controls[pinky], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(pinky_joints[pinky], query=True, ws=True, rotation=True)
				cmds.xform(controls[pinky], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("R_Pinky_Ctrl_*", pinky_joints[pinky], maintainOffset=True)
				point = cmds.pointConstraint("R_Pinky_Ctrl_*", pinky_joints[pinky], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("R_Pinky_Ctrl_2", "R_Pinky_Ctrl_1")
			cmds.parent("R_Pinky_Ctrl_1", "R_Pinky_Ctrl_0")
			cmds.parent("R_Pinky_Ctrl_0", "Right_Wrist_Fk")

			# Lists of the left fingers joints 
			thumb_joints = ["L_Thumb01_Jt", "L_Thumb02_Jt"]
			index_joints = ["L_IndexFinger01_Jt", "L_IndexFinger02_Jt", "L_IndexFinger03_Jt"]
			middle_joints = ["L_MiddleFinger01_Jt", "L_MiddleFinger02_Jt", "L_MiddleFinger03_Jt"]
			ring_joints = ["L_RingFinger01_Jt", "L_RingFinger02_Jt", "L_RingFinger03_Jt"]
			pinky_joints = ["L_Pinky01_tJt", "L_Pinky02_Jt", "L_Pinky03_Jt"]

			# Left thumb
			for thumbs in range(len(thumb_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Thumb_Ctrl_" + str(thumbs)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(thumb_joints[thumbs], query=True, ws=True, translation=True)
				cmds.xform(controls[thumbs], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(thumb_joints[thumbs], query=True, ws=True, rotation=True)
				cmds.xform(controls[thumbs], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("L_Thumb_Ctrl_*", thumb_joints[thumbs], maintainOffset=True)
				point = cmds.pointConstraint("L_Thumb_Ctrl_*", thumb_joints[thumbs], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("L_Thumb_Ctrl_1", "L_Thumb_Ctrl_0")
			cmds.parent("L_Thumb_Ctrl_0", "Left_Wrist_Fk")
							
			# Left index
			for index in range(len(index_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Index_Ctrl_" + str(index)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(index_joints[index], query=True, ws=True, translation=True)
				cmds.xform(controls[index], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(index_joints[index], query=True, ws=True, rotation=True)
				cmds.xform(controls[index], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("L_Index_Ctrl_*", index_joints[index], maintainOffset=True)
				point = cmds.pointConstraint("L_Index_Ctrl_*", index_joints[index], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("L_Index_Ctrl_2", "L_Index_Ctrl_1")
			cmds.parent("L_Index_Ctrl_1", "L_Index_Ctrl_0")
			cmds.parent("L_Index_Ctrl_0", "Left_Wrist_Fk")

			# Left middle
			for middle in range(len(middle_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Middle_Ctrl_" + str(middle)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(middle_joints[middle], query=True, ws=True, translation=True)
				cmds.xform(controls[middle], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(middle_joints[middle], query=True, ws=True, rotation=True)
				cmds.xform(controls[middle], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("L_Middle_Ctrl_*", middle_joints[middle], maintainOffset=True)
				point = cmds.pointConstraint("L_Middle_Ctrl_*", middle_joints[middle], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("L_Middle_Ctrl_2", "L_Middle_Ctrl_1")
			cmds.parent("L_Middle_Ctrl_1", "L_Middle_Ctrl_0")
			cmds.parent("L_Middle_Ctrl_0", "Left_Wrist_Fk")
							
			# Left ring
			for ring in range(len(ring_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Ring_Ctrl_" + str(ring)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(ring_joints[ring], query=True, ws=True, translation=True)
				cmds.xform(controls[ring], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(ring_joints[ring], query=True, ws=True, rotation=True)
				cmds.xform(controls[ring], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("L_Ring_Ctrl_*", ring_joints[ring], maintainOffset=True)
				point = cmds.pointConstraint("L_Ring_Ctrl_*", ring_joints[ring], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("L_Ring_Ctrl_2", "L_Ring_Ctrl_1")
			cmds.parent("L_Ring_Ctrl_1", "L_Ring_Ctrl_0")
			cmds.parent("L_Ring_Ctrl_0", "Left_Wrist_Fk")
							
			# Left pinky
			for pinky in range(len(pinky_joints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Pinky_Ctrl_" + str(pinky)),
							cmds.scale(0.1, 0.1, 0.1)]
				val_pos = cmds.xform(pinky_joints[pinky], query=True, ws=True, translation=True)
				cmds.xform(controls[pinky], ws=1, t=(val_pos[0], val_pos[1], val_pos[2]))
				val_rot = cmds.xform(pinky_joints[pinky], query=True, ws=True, rotation=True)
				cmds.xform(controls[pinky], ws=1, ro=(val_rot[0], val_rot[1], val_rot[2]))
				orient = cmds.orientConstraint("L_Pinky_Ctrl_*", pinky_joints[pinky], maintainOffset=True)
				point = cmds.pointConstraint("L_Pinky_Ctrl_*", pinky_joints[pinky], maintainOffset=True)
			#Finally parent controller to the wrist
			cmds.parent("L_Pinky_Ctrl_2", "L_Pinky_Ctrl_1")
			cmds.parent("L_Pinky_Ctrl_1", "L_Pinky_Ctrl_0")
			cmds.parent("L_Pinky_Ctrl_0", "Left_Wrist_Fk")

			return wrist
	
	def head_control(*args, **kwargs):
		head_jt = "E_Head_Jt"
		head_ctrl = cmds.curve(name="Head_Ctrl", degree=3,
							  point=[(-0.801407, 0, 0.00716748), (-0.802768, 0.023587, -0.220859),
								   (-0.805489, 0.0707609, -0.676912), (0.761595, -0.283043, -0.667253),
								   (1.045492, -0.194522, -0.0218101), (1.046678, -0.194804, 0.0403576),
								   (0.758039, -0.282198, 0.63974), (-0.806291, 0.0676615, 0.650803),
								   (-0.803035, 0.0225538, 0.221713), (-0.801407, 0, 0.00716748)],
							  knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 7, 7])
		cmds.scale(0.764, 1.591, 0.935)
		cmds.makeIdentity('Head_Ctrl', apply=True, translate=True, scale=True)
		val_head = cmds.xform(head_jt, ws=True, query=True, translation=True)
		cmds.xform(head_ctrl, ws=1, t=(val_head[0], val_head[1], val_head[2]))
		parent_head = cmds.parentConstraint(head_ctrl, head_jt)
		cmds.parent(head_ctrl, "Ik_shoulder_ctrl")
		return head_ctrl, head_jt

	def master_control(*args, **kwargs):
		master_ctrl = cmds.curve(name="Master_Ctrl", d=1,
								 p=[(-4, 0, 0), (-2, 0, -1.5), (-2, 0, -0.5),
									(-0.5, 0, -0.5), (-0.5, 0, -2), (-1.5, 0, -2),
									(0, 0, -4), (1.5, 0, -2), (0.5, 0, -2), (0.5, 0, -0.5),
									(2, 0, -0.5), (2, 0, -1.5), (4, 0, 0), (2, 0, 1.5),
									(2, 0, 0.5), (0.5, 0, 0.5), (0.5, 0, 2), (1.5, 0, 2),
									(0, 0, 4), (-1.5, 0, 2), (-0.5, 0, 2), (-0.5, 0, 0.5),
									(-2, 0, 0.5), (-2, 0, 1.5), (-4, 0, 0)])
		cmds.parent("A_Hip_Jt", master_ctrl)
		cmds.parent("UpperBody_Grp", master_ctrl)
		cmds.parent("Foot_Grp", master_ctrl)
		cmds.parent("Knee_Grp", master_ctrl)
		return master_ctrl

class Human_skeleton(object):
	def __create_spine_skeleton__(self):
		self.hip_joint = cmds.joint(name='A_Hip_Jt', position=(0.008, 4.451, 0))
		cmds.joint('A_Hip_Jt', edit=True, zso=True, oj='xyz')
		num_jt = list(range(4))
		jt_pos_x = 0.08
		jt_pos_y = 0.05
		for joints in num_jt:
			extra_str_jt ="Hip_Jt_"
			extra_jt = cmds.joint(name=extra_str_jt + str(joints), position=(0.008, 4.451, 0))
			cmds.joint(extra_str_jt + str(joints), edit=True, zso=True, oj='xyz')
			cmds.select(extra_str_jt + str(joints))
			joint_list = cmds.ls(selection=True)
			if joints:
				jt_pos_y += 0.18
				jt_pos_x += -0.08
				cmds.select(extra_str_jt + str(joints))
				cmds.move(0.3, 0.0, 0.0)
				cmds.move(joints * 0.008 - 0.2, 4.751 + joints * jt_pos_y, 0, extra_str_jt + str(joints), absolute=True)
		cmds.move(jt_pos_x, 4.451 + 0.9 * 2, 0)
		self.neck_joint = cmds.joint(name='D_Neck_Jt', position=(-0.089, 6.965, 0))
		cmds.joint('D_Neck_Jt', edit=True, zso=True, oj='xyz')
		self.head_joint = cmds.joint(name='E_Head_Jt', position=(-0.026, 7.306, 0))
		cmds.joint('E_Head_Jt', edit=True, zso=True, oj='xyz')
		self.head_tip_joint = cmds.joint(name='F_HeadTip_Jt', position=(-0.015, 8.031, 0))
		cmds.select('A_Hip_Jt')
		cmds.joint(name='A_LowerHip_Jt', position=(-0.023, 4.327, 0))
		cmds.select("Hip_Jt_0")
		cmds.move(-0.008, 4.701, 0)
		cmds.select('A_Hip_Jt')

	def __create_leg_skeleton__(self):
		self.l_hip_joint = cmds.joint(name='L_Hip_Jt', position=(-0.12, 4.369, -0.689))
		cmds.select('L_Hip_Jt')
		self.l_knee_joint = cmds.joint(name='L_Knee_Jt', position=(0.2, 2.36, -0.689))
		cmds.select('L_Knee_Jt')
		cmds.joint('L_Hip_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_ankle_joint = cmds.joint(name='L_Ankle_Jt', position=(-0.24, 0.486, -0.689))
		cmds.joint('L_Knee_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		cmds.joint('L_Ankle_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_toe_joint = cmds.joint(name='L_Toe_Jt', position=(0.32, 0.051, -0.689))
		self.l_toe_end_joint = cmds.joint(name='L_ToeEnd_Jt', position=(0.69, 0.062, -0.689))
		cmds.joint('L_Toe_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		
	def __create_arm_skeleton__(self):
		cmds.select('D_Neck_Jt')
		self.l_collar_bone_joint = cmds.joint(name='L_Collarbone_Jt', position=(-0.233, 6.565, -0.793))
		self.l_shoulder_joint = cmds.joint(name='L_Shoulder_Jt', position=(0, 6.749, -1.31))
		cmds.joint('L_Collarbone_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_elbow_joint = cmds.joint(name='L_Elbow_Jt', position=(0, 5.773, -2.092))
		cmds.joint('L_Shoulder_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_wrist_joint = cmds.joint(name='L_Wrist_Jt', position=(0.503, 5.126, -2.82))
		cmds.joint('L_Elbow_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_middle_hand_joint = cmds.joint(name='L_MiddleHand_Jt', position=(0.641, 4.961, -2.963))
		cmds.joint('L_Wrist_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		cmds.select('L_Wrist_Jt')

	def __create_finger_skeleton__(self):
		# Thumb
		self.l_thumb01_joint = cmds.joint(name='L_Thumb01_Jt', position=(0.782, 4.973, -2.855))
		self.l_thumb02_joint = cmds.joint(name='L_Thumb02_Jt', position=(0.895, 4.867, -2.855))
		cmds.joint('L_Thumb01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_thumb03_joint = cmds.joint(name='L_Thumb03_Jt', position=(0.938, 4.79, -2.855))
		cmds.joint('L_Thumb02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Index
		cmds.select('L_Wrist_Jt')
		self.l_index_finger01_joint = cmds.joint(name='L_Index01_Jt', position=(0.749, 4.841, -3.093))
		self.l_index_finger02_joint = cmds.joint(name='L_Index02_Jt', position=(0.816, 4.697, -3.159))
		cmds.joint('L_Index01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_index_finger03_joint = cmds.joint(name='L_Index03_Jt', position=(0.849, 4.568, -3.19))
		cmds.joint('L_Index02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_index_finger04_joint = cmds.joint(name='l_index04_Jt', position=(0.861, 4.484, -3.198))
		cmds.joint('L_Index03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Middle
		cmds.select('L_Wrist_Jt')
		self.l_middle_finger01_joint = cmds.joint(name='L_Middle01_Jt', position=(0.637, 4.833, -3.183))
		self.l_middle_finger02_joint = cmds.joint(name='L_Middle02_Jt', position=(0.682, 4.703, -3.276))
		cmds.joint('L_Middle01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_middle_finger03_joint = cmds.joint(name='L_Middle03_Jt', position=(0.702, 4.554, -3.322))
		cmds.joint('L_Middle02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_middle_finger04_joint = cmds.joint(name='L_Middle04_Jt', position=(0.711, 4.441, -3.334))
		cmds.joint('L_Middle03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Ring
		cmds.select('L_Wrist_Jt')
		self.l_ring_finger01_joint = cmds.joint(name='L_Ring01_Jt', position=(0.488, 4.827, -3.25))
		self.l_ring_finger02_joint = cmds.joint(name='L_Ring02_Jt', position=(0.528, 4.713, -3.31))
		cmds.joint('L_Ring01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_ring_finger03_joint = cmds.joint(name='L_Ring03_Jt', position=(0.541, 4.584, -3.354))
		cmds.joint('L_Ring02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_ring_finger04_joint = cmds.joint(name='L_Ring04_Jt', position=(0.546, 4.49, -3.361))
		cmds.joint('L_Ring03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Pinky
		cmds.select('L_Wrist_Jt')
		self.l_pinky01_joint = cmds.joint(name='L_Pinky01_tJt', position=(0.362, 4.818, -3.251))
		self.l_pinky02_joint = cmds.joint(name='L_Pinky02_Jt', position=(0.375, 4.73, -3.283))
		cmds.joint('L_Pinky01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_pinky03_joint = cmds.joint(name='L_Pinky03_Jt', position=(0.38, 4.617, -3.329))
		cmds.joint('L_Pinky02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.l_pinky04_joint = cmds.joint(name='L_Pinky04_Jt', position=(0.385, 4.534, -3.341))
		cmds.joint('L_Pinky03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

	def __create_finger_control__(**kwargs):
		joints = kwargs.setdefault("joints")
		for jt in joints:
			cmds.select(jt, hierarchy=True)
			joint_list = cmds.ls(selection=True)
			for joint in joint_list[:-2]:
				pos = cmds.joint(joint, q=True, position=True)
				name_split = joint.rsplit('_', 1)
				name = name_split[0]
				cmds.select(joint)
				cmds.joint(name=name + 'Up_Jt', position=(pos[0] + 0.01, pos[1] + 0.05, pos[2] - 0.06))

	def __mirror_joints_hands__(self, **kwargs):
		cmds.select('D_Neck_Jt')
		self.mirror_each_joint = cmds.mirrorJoint('L_Collarbone_Jt',
												  mirrorXY=True,
												  mirrorBehavior=True, searchReplace=('L_', 'R_'))

	def __mirror_joints_legs__(self, **kwargs):
		cmds.select('A_LowerHip_Jt')
		self.mirror_each_joint = cmds.mirrorJoint('L_Hip_Jt',
												  mirrorXY=True,
												  mirrorBehavior=True, searchReplace=('L_', 'R_'))
		select_bone = cmds.select('A_Hip_Jt')

