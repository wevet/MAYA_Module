# -*- coding: utf-8 -*-


import maya.cmds as cmds
from skeleton import SkeletonB
from functools import partial


"""
usage
import rig_window
import importlib
importlib.reload(RigWindow)
window = rig_window.AutoRig_OptionsWindow()
window.create()
"""


class RigWindow(object):

	def __init__(self):
		self.window = 'ar_optionsWindow'
		self.title = 'Auto Rigging Tool'
		self.size = (340, 550)
		self.supportsToolAction = True
		self.editMenu = cmds.menu(label='Edit')
		self.editMenuDiv = cmds.menuItem(d=True)
		self.edit_menu_radio = cmds.radioMenuItemCollection()

		self.editMenuTool = cmds.menuItem(
			label='As Tool',
			radioButton=True,
			enable=self.supportsToolAction,
			command=self.edit_menu_command
		)
		self.helpMenu = cmds.menu(label='Help')
		self.helpMenuItem = cmds.menuItem(label='Help on %s' % self.title, command=self.show_help_menu)

	def create(self):
		if cmds.window(self.window, exists=True):
			cmds.deleteUI(self.window, window=True)
		self.window = cmds.window(
			self.window,
			title=self.title,
			widthHeight=self.size,
			menuBar=True
		)

		self.show_main_window()
		cmds.showWindow()

	def show_main_window(self):

		cmds.columnLayout(columnAttach=('both', 2), rowSpacing=4, columnWidth=340)
		cmds.text("BIPEDAL CHARACTER", align="center")
		cmds.text("")
		cmds.text("Step 1: Create bipedal skeleton")
		# mc.text("___________________________________")

		buttonSkeletonControl = cmds.button(label='Create Skeleton', command=self.create_skeleton, width=110, height=40)

		cmds.text("  ")
		cmds.text("Step 2: Create Leg controls")

		cmds.text("____________________________________")
		cmds.text(label='LOWER BODY CONTROL', align='center')

		buttonRigFootControl = cmds.button(label='Legs Control', command=self.feet_control,
										   width=120, height=40)
		buttonRigSpineControl = cmds.button(label='Spine Control', command=self.spine_control,
											width=120, height=40, align="center")

		cmds.text("  ")
		cmds.text("Step 3: Create Torso/Arm controls")
		cmds.text("__________________________________")
		cmds.text(label='UPPER BODY CONTROL', align='center')

		buttonRigArmControl = cmds.button(label='Arm Control', command=self.arm_control,
										  width=120, height=40)
		buttonRigFingersControl = cmds.button(label='Fingers Control', command=self.finger_control,
											  width=120, height=40)
		buttonRigHeadControl = cmds.button(label='Head Control', command=self.head_control,
										   width=120, height=40)

		cmds.text("   ")
		cmds.text("Step 4: Create Master control")
		cmds.text("___________________________________")
		cmds.text("MASTER CONTROL", align='center')

		buttonMainControl = cmds.button(label='Master Control', command=self.master_control,
										width=120, height=40,
								   align='center')

		closeButton = cmds.button(label="Close", command=self.close_window,
								  width=120, height=40, align='center')

	def close_window(self, *args):
		if cmds.window(self.window, exists=True):
			cmds.deleteUI(self.window, window=True)

	def create_skeleton(self, *args):
		skeletonJT = SkeletonB()
		skeletonJT.__CreateSpineSkeleton__()
		skeletonJT.__CreateSkeletonLeg__()
		skeletonJT.__CreateSkeletonArm__()
		skeletonJT.__CreateSkeletonFingers__()
		skeletonJT.__MirrorJointsHands__()
		skeletonJT.__MirrorJointsLegs__()

	def edit_menu_command(self, *args):
		pass

	@staticmethod
	def show_help_menu(self, *args):
		cmds.launch(web='http://www.maya-python.com/')

	def feet_control(*args, **kwargs):
		Feet_Ctrl = range(2)
		Ankle = 'R_Ankle_Jt'
		foot_ctrl = True
		if foot_ctrl:

			# LeftFoot
			Feet_Ctrl[0] = cmds.curve(name="ik_LeftFoot_Ctrl", degree=1,
									  point=[(-0.440687, 0.0433772, 0.400889), (-0.440687, 0.0433772, -0.429444),
											 (0.898906, -0.240469, -0.384559), (0.975205, -0.496435, -0.384559),
											 (0.975205, -0.496435, 0.365874), (0.898906, -0.240469, 0.365874),
											 (0.898906, -0.240469, -0.384559), (-0.440687, 0.0433772, -0.429444),
											 (-0.440687, 0.0433772, 0.400889),
											 (-0.520228, -0.496554, 0.400889), (-0.520228, -0.496554, -0.429444),
											 (-0.440687, 0.0433772, -0.429444),
											 (-0.440687, 0.0433772, 0.400889), (0.898906, -0.240469, 0.365874),
											 (0.975205, -0.496435, 0.365874), (-0.520228, -0.496554, 0.400889),
											 (-0.520228, -0.496554, -0.429444), (0.975205, -0.496435, -0.384559)],
									  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17])

			# Move pivot to ankle centre
			AnkleLeft = 'L_Ankle_Jt'
			valIk = cmds.xform(AnkleLeft, query=True, ws=True, translation=True)
			cmds.xform(Feet_Ctrl[0], ws=1, t=(valIk[0], valIk[1], valIk[2]))
			# Ik Handles with foot bones
			cmds.ikHandle(name="ikHandle_L_Ctrl", startJoint="L_Hip_Jt", endEffector="L_Ankle_Jt", solver="ikRPsolver",
						  parentCurve=False)
			ikLeftMidToe = cmds.ikHandle(name="ikHandle_L_Ctrl_MidToe", startJoint="L_Ankle_Jt", endEffector="L_Toe_Jt",
										 solver="ikRPsolver", parentCurve=False)
			ikLeftEndToe = cmds.ikHandle(name="ikHandle_L_Ctrl_Toe", startJoint="L_Toe_Jt", endEffector="L_ToeEnd_Jt",
										 solver="ikRPsolver", parentCurve=False)
			grpIkLeft = cmds.group("ikHandle_L_Ctrl", n="GrpIk_LeftLeg")
			cmds.parent(grpIkLeft, Feet_Ctrl[0])

			# Add parent constraint and new controller to control feet rotation and its position
			ToeLeft = 'L_Toe_Jt'
			leftToeRot = cmds.curve(name="Left_Toe_Rotation", d=1,
									p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2), (0, 0, 4), (2, 0, 2), (0.5, 0, 2),
									   (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2), (0, 0, -4), (-2, 0, -2), (-0.5, 0, -2),
									   (-0.5, 0, 0)])
			valToe = cmds.xform(ToeLeft, query=True, ws=True, translation=True)
			cmds.xform(leftToeRot, ws=1, t=(valToe[0], valToe[1], valToe[2]))
			parentLeftFoot = cmds.parentConstraint(leftToeRot, "L_Toe_Jt", maintainOffset=True)
			cmds.parent(parentLeftFoot, Feet_Ctrl[0])
			cmds.parent(ikLeftMidToe, ikLeftEndToe, leftToeRot)

			# Add ball rotation for left ankle
			leftBallCtrl = [cmds.select("LeftBallCtrl", r=True), cmds.scale(0.4, 0.4, 0.4),
							cmds.rename('L_Ball_Rotation')]
			valBall = cmds.xform(AnkleLeft, query=True, ws=True, translation=True)
			cmds.xform(leftBallCtrl[0], ws=1, t=(valBall[0], valBall[1], valBall[2]))
			cmds.rotate('90deg', 0, 0, leftBallCtrl[0])
			cmds.parent("ikHandle_L_Ctrl", leftBallCtrl[0])
			cmds.parent("L_Ball_Rotation", Feet_Ctrl[0])

			# Left knee cap
			kneeLeft = 'L_Knee_Jt'
			leftKneeCap = [cmds.CreateNURBSCircle(), cmds.scale(0.3, 0.3, 0.3), cmds.select("nurbsCircle1"),
						   cmds.rename("nurbsCircle1", 'L_KneeCap'), cmds.setAttr('L_KneeCap.rz', 90)]
			cmds.xform(kneeLeft + ".tx", kneeLeft + ".ty", kneeLeft + ".tz")
			valKnee = cmds.xform(kneeLeft, query=True, ws=True, translation=True)
			cmds.xform(leftKneeCap[0], ws=1, t=(valKnee[0] + 2, valKnee[1], valKnee[2]))

			if leftKneeCap:
				cmds.poleVectorConstraint('L_KneeCap', 'ikHandle_L_Ctrl')

				# Right Foot
				Feet_Ctrl[1] = cmds.curve(name="ik_RightFoot_Ctrl", degree=1,
										  point=[(0.898914, -0.240476, 0.383674), (-0.440521, 0.0411603, 0.428909),
												 (-0.440521, 0.0411603, -0.400341), (0.898914, -0.240476, -0.365796),
												 (0.898914, -0.240476, 0.383674), (0.974311, -0.496509, 0.383674),
												 (0.974311, -0.496509, -0.365796), (-0.517088, -0.495087, -0.400341),
												 (-0.517088, -0.495087, 0.428909), (0.974311, -0.496509, 0.383674),
												 (0.898914, -0.240476, 0.383674), (-0.440521, 0.0411603, 0.428909),
												 (-0.517088, -0.495087, 0.428909),
												 (-0.517088, -0.495087, -0.400341), (-0.440521, 0.0411603, -0.400341),
												 (0.898914, -0.240476, -0.365796), (0.974311, -0.496509, -0.365796)],
										  knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])

				# Move pivot to ankle centre
				AnkleRight = 'R_Ankle_Jt'
				valIkRight = cmds.xform(AnkleRight, query=True, ws=True, translation=True)
				if AnkleRight != AnkleLeft:
					cmds.xform(Feet_Ctrl[1], ws=1, t=(valIkRight[0], valIkRight[1], valIkRight[2]))

					# Ik Handles with foot bones
					cmds.ikHandle(name="ikHandle_R_Ctrl", startJoint="R_Hip_Jt",
								  endEffector="R_Ankle_Jt",
								  solver="ikRPsolver",
								  parentCurve=False)
					ikRightMidToe = cmds.ikHandle(name="ikHandle_R_Ctrl_MidToe", startJoint="R_Ankle_Jt",
												  endEffector="R_Toe_Jt",
												  solver="ikRPsolver",
												  parentCurve=False)
					ikRightEndToe = cmds.ikHandle(name="ikHandle_R_Ctrl_Toe", startJoint="R_Toe_Jt",
												  endEffector="R_ToeEnd_Jt",
												  solver="ikRPsolver",
												  parentCurve=False)
					grpIkRight = cmds.group("ikHandle_R_Ctrl", n="GrpIk_RightLeg")
					cmds.parent(grpIkRight, Feet_Ctrl[1])

					# Add parent Constraint and new controller to control feet rotation and its position
					ToeRight = 'R_Toe_Jt'
					rightToeRot = cmds.curve(name="Right_Toe_Rotation", d=1,
											 p=[(-0.5, 0, 0), (-0.5, 0, 2), (-2, 0, 2), (0, 0, 4), (2, 0, 2),
												(0.5, 0, 2), (0.5, 0, 0), (0.5, 0, -2), (2, 0, -2), (0, 0, -4),
												(-2, 0, -2), (-0.5, 0, -2), (-0.5, 0, 0)]);
					valToeRight = cmds.xform(ToeRight, query=True, ws=True, translation=True)
					cmds.xform(rightToeRot, ws=1, t=(valToeRight[0], valToeRight[1], valToeRight[2]))
					parentRightFoot = cmds.parentConstraint(rightToeRot, "R_Toe_Jt", maintainOffset=True)
					cmds.parent(parentRightFoot, Feet_Ctrl[1])
					cmds.parent(ikRightMidToe, ikRightEndToe, rightToeRot)

					# Add ball rotation for left ankle
					rightBallCtrl = [cmds.select("RightBallCtrl", r=True), cmds.scale(0.4, 0.4, 0.4),
									 cmds.rename('R_Ball_Rotation')]
					valBallRight = cmds.xform(AnkleRight, query=True, ws=True, translation=True)
					cmds.xform(rightBallCtrl[0], ws=1, t=(valBallRight[0], valBallRight[1], valBallRight[2]))
					cmds.rotate('90deg', 0, 0, rightBallCtrl[0])
					cmds.parent("ikHandle_R_Ctrl", rightBallCtrl[0])
					cmds.parent("R_Ball_Rotation", Feet_Ctrl[1])

					# Right Knee cap
					kneeRight = 'R_Knee_Jt'
					rightKneeCap = [cmds.CreateNURBSCircle(), cmds.scale(0.3, 0.3, 0.3),
									cmds.select("nurbsCircle1"),
									cmds.rename("nurbsCircle1", 'R_KneeCap'),
									cmds.setAttr('R_KneeCap.rz', 90)]
					cmds.xform(kneeRight + ".tx", kneeRight + ".ty", kneeRight + ".tz")
					valKneeRight = cmds.xform(kneeRight, query=True, ws=True, translation=True)
					cmds.xform(rightKneeCap[0], ws=1, t=(valKneeRight[0] + 2, valKneeRight[1], valKneeRight[2]))

					if rightKneeCap:
						cmds.poleVectorConstraint('R_KneeCap', 'ikHandle_R_Ctrl')
						# Creating group for both feet
						grp = cmds.group(em=True, name="Foot_Grp")
						cmds.parent(Feet_Ctrl, 'Foot_Grp', relative=True)
						cmds.move(-0.24, 0.486, -0.689, grp + ".scalePivot", grp + ".rotatePivot", absolute=True)
						grpKnees = cmds.group(em=True, name="Knee_Grp")
						cmds.parent(rightKneeCap, leftKneeCap, grpKnees)

	def spine_control(*args, **kwargs):
		scaleParts = 0.4
		ctrl = True
		bodyPart = range(2)
		# Dictionary for parenting joints with controllers
		parentPart = {"Hip_Jt_1": 1, "D_Neck_Jt": 2, "A_Hip_Jt": 3}
		# Additional list for spline joints
		jointList = ["A_Hip_Jt", "Hip_Jt_0", "Hip_Jt_1", "Hip_Jt_2", "Hip_Jt_2", "D_Neck_Jt"]
		if ctrl:
			if parentPart["A_Hip_Jt"]:
				bodyPart[0] = cmds.curve(name="Ik_hip_ctrl", degree=1,
										 point=[(-2.5, 0.6, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9), (-2.5, 0.6, -1.9),
												(-2.5, 0.6, 1.9),
												(-2.5, -2.1, 1.9), (2.5, -2.1, 1.9), (2.5, 0.6, 1.9), (2.5, 0.6, -1.9),
												(2.5, -2.1, -1.9),
												(2.5, -2.1, 1.9), (-2.5, -2.1, 1.9), (-2.5, -2.1, -1.9),
												(-2.5, 0.6, -1.9), (-2.5, -2.1, -1.9),
												(2.5, -2.1, -1.9)],
										 knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
				Hip_Pos = [cmds.scale(scaleParts, scaleParts, scaleParts), cmds.setAttr(bodyPart[0] + ".ry", 90)]
				hipJt = "A_Hip_Jt"
				valHip = cmds.xform(hipJt, ws=True, query=True, translation=True)
				cmds.xform(bodyPart[0], ws=1, t=(valHip[0], valHip[1], valHip[2]))

				if parentPart != "A_Hip_Jt":
					bodyPart[1] = cmds.curve(name="Ik_shoulder_ctrl", degree=1,
											 point=[(2.3, -0.3, 1.6), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3),
													(-2.3, -0.3, 1.6), (2.3, -0.3, 1.6),
													(2.5, -2.7, 1.9), (-2.5, -2.7, 1.9), (-2.5, -2.7, -1.9),
													(2.5, -2.7, -1.9), (2.5, -2.7, 1.9),
													(2.5, -2.7, -1.9), (2.2, 0.2, -1.3), (-2.2, 0.2, -1.3),
													(-2.5, -2.7, -1.9), (-2.5, -2.7, 1.9),
													(-2.3, -0.3, 1.6)],
											 knot=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])
					Shoulders_Pos = [cmds.scale(scaleParts, scaleParts, scaleParts),
									 cmds.setAttr(bodyPart[1] + ".ry", 90)]
					shoJt = "D_Neck_Jt"
					valSho = cmds.xform(shoJt, ws=True, query=True, translation=True)
					cmds.xform(bodyPart[1], ws=1, t=(valSho[0], valSho[1], valSho[2]))
					spineIk = cmds.ikHandle(name="Spine_Ik", startJoint=jointList[3],
											endEffector=jointList[5], solver="ikSCsolver", parentCurve=False)

					# Middle spine control
					if parentPart["Hip_Jt_1"]:
						midSpine = 'Hip_Jt_1'
						toControlJoints = jointList[1], jointList[2]

						# Spine Ik before creating controller
						spine_01 = cmds.ikHandle(name="Spine_Ik_01", startJoint=jointList[0],
												 endEffector=jointList[2], solver="ikSCsolver", parentCurve=False)

						midSpineCtrl = [cmds.CreateNURBSCircle(), cmds.scale(1.2, 1.2, 1.2),
										cmds.select("nurbsCircle1"),
										cmds.rename("nurbsCircle1", 'S_Ctrl')]

						cmds.xform(midSpine + ".tx", midSpine + ".ty", midSpine + ".tz")
						valMidSpine = cmds.xform(midSpine, query=True, ws=True, translation=True)
						cmds.xform(midSpineCtrl[0], ws=1, t=(valMidSpine[0], valMidSpine[1], valMidSpine[2]))

			elif ctrl is True:
				if parentPart["A_Hip_Jt", "D_Neck_Jt", "Hip_Jt_1"] is False:
					parentPart.clear()
					cmds.delete()
					print(ctrl)
			else:
				cmds.error("No selection to control")

		# Parenting each spine ik to their controllers
		# Parent shoulder control
		cmds.parent('Spine_Ik', 'Ik_shoulder_ctrl', world=False)
		cmds.orientConstraint('Ik_shoulder_ctrl', jointList[5], maintainOffset=True)

		# Parent middle spine control
		cmds.parentConstraint("S_Ctrl", "Spine_Ik_01", skipTranslate='y', maintainOffset=True)

		# Parent hip control to the main hip
		cmds.parentConstraint("Ik_hip_ctrl", jointList[0], maintainOffset=True)

		# Parent all controls together
		cmds.parent("Ik_shoulder_ctrl", "S_Ctrl")
		cmds.parent("S_Ctrl", "Ik_hip_ctrl")
		cmds.parent("Spine_Ik_01", "S_Ctrl")
		cmds.group('Ik_hip_ctrl', name="UpperBody_Grp")

		# return the values
		return scaleParts, bodyPart, parentPart

	def arm_control(*args, **kwargs):
		# Right Arm control

		armListRight = ["R_Collarbone_Jt", "R_Shoulder_Jt", "R_Wrist_Jt"]
		armListLeft = ["L_Collarbone_Jt", "L_Shoulder_Jt", "L_Wrist_Jt"]

		armCtrl = True
		# Ik for right arm
		cmds.ikHandle(name="R_ArmCtrl", startJoint=armListRight[1],
					  endEffector=armListRight[2], solver="ikRPsolver", parentCurve=False)

		# Ik for left arm
		cmds.ikHandle(name="L_ArmCtrl", startJoint=armListLeft[1],
					  endEffector=armListLeft[2], solver="ikRPsolver", parentCurve=False)

		# Right arm fk controls
		for i in range(len(armListRight)):
			controls = [cmds.CreateNURBSCircle()]
			cmds.rename('nurbsCircle1', 'Fk_R_ForeArm_' + str(i))

			if i in range(len(armListRight)):
				scaleNurbs = 0.5
				cmds.rotate("-45deg", 0, 0, "Fk_R_ForeArm_" + str(i))
				cmds.scale(scaleNurbs, scaleNurbs, scaleNurbs)

		# Left arm fk controls
		for i in range(len(armListLeft)):
			controls = [cmds.CreateNURBSCircle()]
			cmds.rename('nurbsCircle1', 'Fk_L_ForeArm_' + str(i))

			if i in range(len(armListLeft)):
				scaleNurbs = 0.5
				cmds.rotate("45deg", 0, 0, "Fk_L_ForeArm_" + str(i))
				cmds.scale(scaleNurbs, scaleNurbs, scaleNurbs)

		# Fk Arms
		# Right
		FKarmR = ["Fk_R_ForeArm_0", "Fk_R_ForeArm_1", "Fk_R_ForeArm_2"]
		# Left
		FKarmL = ["Fk_L_ForeArm_0", "Fk_L_ForeArm_1", "Fk_L_ForeArm_2"]

		# Right Arm
		if armCtrl:
			if FKarmR[0] is "Fk_R_ForeArm_0":
				# Collar Bone
				valRcolar = cmds.xform(armListRight[0], query=True, ws=True, translation=True)
				cmds.xform(FKarmR[0], ws=1, t=(valRcolar[0], valRcolar[1], valRcolar[2]))
				cmds.rotate(0, 0, "90deg", FKarmR[0])
				# Parent and orient arm
				orient = cmds.orientConstraint(FKarmR[0], armListRight[0], mo=True)
				parent = cmds.parentConstraint(FKarmR[0], armListRight[0], mo=True)
				cmds.parent(FKarmR[0], "Ik_shoulder_ctrl")

			if FKarmR[1] is "Fk_R_ForeArm_1":
				# Shoulder Bone
				valRshoulder = cmds.xform(armListRight[1], query=True, ws=True, translation=True)
				cmds.xform(FKarmR[1], ws=1, t=(valRshoulder[0], valRshoulder[1], valRshoulder[2]))
				orient = cmds.orientConstraint(FKarmR[1], armListRight[1], mo=True)
				parent = cmds.parentConstraint(FKarmR[1], armListRight[1], mo=True)
				cmds.parent(FKarmR[1], "Ik_shoulder_ctrl")

			if FKarmR[2] is "Fk_R_ForeArm_2":
				# Wrist Bone
				valRwrist = cmds.xform(armListRight[2], query=True, ws=True, translation=True)
				cmds.xform(FKarmR[2], ws=1, t=(valRwrist[0], valRwrist[1], valRwrist[2]))
				# Parent to the shoulder control
				orient = cmds.orientConstraint(FKarmR[2], armListRight[2], mo=True)
				parent = cmds.parent("R_ArmCtrl", FKarmR[2])
				cmds.parent(FKarmR[2], "Ik_shoulder_ctrl")
				cmds.parent(FKarmR[2], FKarmR[1])
			else:
				return FKarmR

		# Left Arm
		if armCtrl:
			if FKarmL[0] is "Fk_L_ForeArm_0":
				# Collar Bone
				valRcolar = cmds.xform(armListLeft[0], query=True, ws=True, translation=True)
				cmds.xform(FKarmL[0], ws=1, t=(valRcolar[0], valRcolar[1], valRcolar[2]))
				cmds.rotate(0, 0, "90deg", FKarmL[0])
				# Parent and orient arm
				orient = cmds.orientConstraint(FKarmL[0], armListLeft[0], mo=True)
				parent = cmds.parentConstraint(FKarmL[0], armListLeft[0], mo=True)
				cmds.parent(FKarmL[0], "Ik_shoulder_ctrl")

			if FKarmL[1] is "Fk_L_ForeArm_1":
				# Shoulder Bone
				valRshoulder = cmds.xform(armListLeft[1], query=True, ws=True, translation=True)
				cmds.xform(FKarmL[1], ws=1, t=(valRshoulder[0], valRshoulder[1], valRshoulder[2]))
				orient = cmds.orientConstraint(FKarmL[1], armListLeft[1], mo=True)
				parent = cmds.parentConstraint(FKarmL[1], armListLeft[1], mo=True)
				cmds.parent(FKarmL[1], "Ik_shoulder_ctrl")

			if FKarmL[2] is "Fk_L_ForeArm_2":
				# Wrist Bone
				valRwrist = cmds.xform(armListLeft[2], query=True, ws=True, translation=True)
				cmds.xform(FKarmL[2], ws=1, t=(valRwrist[0], valRwrist[1], valRwrist[2]))
				orient = cmds.orientConstraint(FKarmL[2], armListLeft[2], mo=True)
				parent = cmds.parent("L_ArmCtrl", FKarmL[2])
				cmds.parent(FKarmL[2], "Ik_shoulder_ctrl")
				# Parent to the shoulder control
				cmds.parent(FKarmL[2], FKarmL[1])
			else:
				return FKarmL

		# Right elbow control
		elbowRight = 'R_Elbow_Jt'
		rightElbowCtrl = [cmds.CreateNURBSCircle(), cmds.scale(0.3, 0.3, 0.3), cmds.select("nurbsCircle1"),
						  cmds.rename("nurbsCircle1", 'R_ElbowCtrl'), cmds.setAttr('R_ElbowCtrl.rz', 90)]

		cmds.xform(elbowRight + ".tx", elbowRight + ".ty", elbowRight + ".tz")
		valElbow = cmds.xform(elbowRight, query=True, ws=True, translation=True)
		cmds.xform(rightElbowCtrl[0], ws=1, t=(valElbow[0] - 0.6, valElbow[1], valElbow[2]))
		if rightElbowCtrl:
			cmds.poleVectorConstraint(rightElbowCtrl[3], 'R_ArmCtrl')
			cmds.parent(rightElbowCtrl[3], FKarmR[2])

		# Left elbow control
		elbowLeft = 'L_Elbow_Jt'
		leftElbowCtrl = [cmds.CreateNURBSCircle(), cmds.scale(0.3, 0.3, 0.3), cmds.select("nurbsCircle1"),
						 cmds.rename("nurbsCircle1", 'L_ElbowCtrl'), cmds.setAttr('L_ElbowCtrl.rz', 90)]

		cmds.xform(elbowLeft + ".tx", elbowLeft + ".ty", elbowLeft + ".tz")
		valElbow = cmds.xform(elbowLeft, query=True, ws=True, translation=True)
		cmds.xform(leftElbowCtrl[0], ws=1, t=(valElbow[0] - 0.6, valElbow[1], valElbow[2]))
		if leftElbowCtrl:
			cmds.poleVectorConstraint(leftElbowCtrl[3], 'L_ArmCtrl')
			cmds.parent(leftElbowCtrl[3], FKarmL[2])
		# Finally parent Shoulder Control to both Collarbone Controls
		cmds.parent(FKarmR[1], FKarmR[0])
		cmds.parent(FKarmL[1], FKarmL[0])
		return FKarmR, FKarmL, armListRight, armListLeft, armCtrl

	def finger_control(*args, **kwargs):
		wrist = True
		wristJt = ["R_Wrist_Jt", "L_Wrist_Jt"]
		# Create Wrists for both hands
		if wrist is True:
			# Right hand  side
			wristRight = cmds.circle(name="Right_Wrist_Fk", ch=1, o=1, r=0.5, nr=(0, 1, 0))
			cmds.scale(0.5, 0.5, 0.5)

			valWristRight = cmds.xform(wristJt[0], query=True, ws=True, translation=True)
			cmds.xform(wristRight, ws=1, t=(valWristRight[0], valWristRight[1], valWristRight[2]))
			valRotRight = cmds.xform(wristJt[0], query=True, ws=True, rotation=True)
			cmds.xform(wristRight, ws=1, ro=(valRotRight[0], valRotRight[1], valRotRight[2]))
			orientWrist = cmds.orientConstraint(wristRight, wristJt[0], mo=True)
			# Parent to wrist control
			cmds.parent(wristRight, "Fk_R_ForeArm_2")

			wristLeft = cmds.circle(name="Left_Wrist_Fk", ch=1, o=1, r=0.5, nr=(0, 1, 0))
			cmds.scale(0.5, 0.5, 0.5)

			valWristLeft = cmds.xform(wristJt[1], query=True, ws=True, translation=True)
			cmds.xform(wristLeft, ws=1, t=(valWristLeft[0], valWristLeft[1], valWristLeft[2]))
			valRotLeft = cmds.xform(wristJt[1], query=True, ws=True, rotation=True)
			cmds.xform(wristLeft, ws=1, ro=(valRotLeft[0], valRotLeft[1], valRotLeft[2]))
			orientWrist = cmds.orientConstraint(wristLeft, wristJt[1], mo=True)
			# Parent to wrist control
			cmds.parent(wristLeft, "Fk_L_ForeArm_2")

			# Lists of the right fingers joints
			thumbJoints = ["R_Thumb01_Jt", "R_Thumb02_Jt"]
			indexJoints = ["R_IndexFinger01_Jt", "R_IndexFinger02_Jt", "R_IndexFinger03_Jt"]
			middleJoints = ["R_MiddleFinger01_Jt", "R_MiddleFinger02_Jt", "R_MiddleFinger03_Jt"]
			ringJoints = ["R_RingFinger01_Jt", "R_RingFinger02_Jt", "R_RingFinger03_Jt"]
			pinkyJoints = ["R_Pinky01_tJt", "R_Pinky02_Jt", "R_Pinky03_Jt"]
			# All joints
			# controlsJoints = [thumbJoints,indexJoints,middleJoints,ringJoints,pinkyJoints]

			for thumbs in range(len(thumbJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Thumb_Ctrl_" + str(thumbs)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(thumbJoints[thumbs], query=True, ws=True, translation=True)
				cmds.xform(controls[thumbs], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(thumbJoints[thumbs], query=True, ws=True, rotation=True)
				cmds.xform(controls[thumbs], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("R_Thumb_Ctrl_*", thumbJoints[thumbs], maintainOffset=True)
				point = cmds.pointConstraint("R_Thumb_Ctrl_*", thumbJoints[thumbs], maintainOffset=True)

			# Finally parent Controllers to the wrist
			cmds.parent("R_Thumb_Ctrl_1", "R_Thumb_Ctrl_0")
			cmds.parent("R_Thumb_Ctrl_0", "Right_Wrist_Fk")

			# Right index
			for index in range(len(indexJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Index_Ctrl_" + str(index)),
							cmds.scale(0.1, 0.1, 0.1)]

				# xform translation
				valPos = cmds.xform(indexJoints[index], query=True, ws=True, translation=True)
				cmds.xform(controls[index], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(indexJoints[index], query=True, ws=True, rotation=True)
				cmds.xform(controls[index], ws=1, ro=(valRot[0], valRot[1], valRot[2]))
				orient = cmds.orientConstraint("R_Index_Ctrl_*", indexJoints[index], maintainOffset=True)
				point = cmds.pointConstraint("R_Index_Ctrl_*", indexJoints[index], maintainOffset=True)
				# Finally parent controllers to the wrist
			cmds.parent("R_Index_Ctrl_2", "R_Index_Ctrl_1")
			cmds.parent("R_Index_Ctrl_1", "R_Index_Ctrl_0")
			cmds.parent("R_Index_Ctrl_0", "Right_Wrist_Fk")

			# Right middle
			for middle in range(len(middleJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Middle_Ctrl_" + str(middle)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(middleJoints[middle], query=True, ws=True, translation=True)
				cmds.xform(controls[middle], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(middleJoints[middle], query=True, ws=True, rotation=True)
				cmds.xform(controls[middle], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("R_Middle_Ctrl_*", middleJoints[middle], maintainOffset=True)
				point = cmds.pointConstraint("R_Middle_Ctrl_*", middleJoints[middle], maintainOffset=True)

			cmds.parent("R_Middle_Ctrl_2", "R_Middle_Ctrl_1")
			cmds.parent("R_Middle_Ctrl_1", "R_Middle_Ctrl_0")
			cmds.parent("R_Middle_Ctrl_0", "Right_Wrist_Fk")

			# Right ring
			for ring in range(len(ringJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Ring_Ctrl_" + str(ring)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(ringJoints[ring], query=True, ws=True, translation=True)
				cmds.xform(controls[ring], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(ringJoints[ring], query=True, ws=True, rotation=True)
				cmds.xform(controls[ring], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("R_Ring_Ctrl_*", ringJoints[ring], maintainOffset=True)
				point = cmds.pointConstraint("R_Ring_Ctrl_*", ringJoints[ring], maintainOffset=True)

			cmds.parent("R_Ring_Ctrl_2", "R_Ring_Ctrl_1")
			cmds.parent("R_Ring_Ctrl_1", "R_Ring_Ctrl_0")
			cmds.parent("R_Ring_Ctrl_0", "Right_Wrist_Fk")

			# Right pinky
			for pinky in range(len(pinkyJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "R_Pinky_Ctrl_" + str(pinky)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(pinkyJoints[pinky], query=True, ws=True, translation=True)
				cmds.xform(controls[pinky], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(pinkyJoints[pinky], query=True, ws=True, rotation=True)
				cmds.xform(controls[pinky], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("R_Pinky_Ctrl_*", pinkyJoints[pinky], maintainOffset=True)
				point = cmds.pointConstraint("R_Pinky_Ctrl_*", pinkyJoints[pinky], maintainOffset=True)

			cmds.parent("R_Pinky_Ctrl_2", "R_Pinky_Ctrl_1")
			cmds.parent("R_Pinky_Ctrl_1", "R_Pinky_Ctrl_0")
			cmds.parent("R_Pinky_Ctrl_0", "Right_Wrist_Fk")
			# Lists of the left fingers joints
			thumbJoints = ["L_Thumb01_Jt", "L_Thumb02_Jt"]
			indexJoints = ["L_IndexFinger01_Jt", "L_IndexFinger02_Jt", "L_IndexFinger03_Jt"]
			middleJoints = ["L_MiddleFinger01_Jt", "L_MiddleFinger02_Jt", "L_MiddleFinger03_Jt"]
			ringJoints = ["L_RingFinger01_Jt", "L_RingFinger02_Jt", "L_RingFinger03_Jt"]
			pinkyJoints = ["L_Pinky01_tJt", "L_Pinky02_Jt", "L_Pinky03_Jt"]
			# All joints
			# controlsJoints = [thumbJoints,indexJoints,middleJoints,ringJoints,pinkyJoints]

			# Right thumb
			for thumbs in range(len(thumbJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Thumb_Ctrl_" + str(thumbs)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(thumbJoints[thumbs], query=True, ws=True, translation=True)
				cmds.xform(controls[thumbs], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(thumbJoints[thumbs], query=True, ws=True, rotation=True)
				cmds.xform(controls[thumbs], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("L_Thumb_Ctrl_*", thumbJoints[thumbs], maintainOffset=True)
				point = cmds.pointConstraint("L_Thumb_Ctrl_*", thumbJoints[thumbs], maintainOffset=True)
			# Finally parent Controllers to the wrist
			cmds.parent("L_Thumb_Ctrl_1", "L_Thumb_Ctrl_0")
			cmds.parent("L_Thumb_Ctrl_0", "Left_Wrist_Fk")

			# Right index
			for index in range(len(indexJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Index_Ctrl_" + str(index)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(indexJoints[index], query=True, ws=True, translation=True)
				cmds.xform(controls[index], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(indexJoints[index], query=True, ws=True, rotation=True)
				cmds.xform(controls[index], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("L_Index_Ctrl_*", indexJoints[index], maintainOffset=True)
				point = cmds.pointConstraint("L_Index_Ctrl_*", indexJoints[index], maintainOffset=True)
			# Finally parent Controllers to the wrist
			cmds.parent("L_Index_Ctrl_2", "L_Index_Ctrl_1")
			cmds.parent("L_Index_Ctrl_1", "L_Index_Ctrl_0")
			cmds.parent("L_Index_Ctrl_0", "Left_Wrist_Fk")

			# Right middle
			for middle in range(len(middleJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Middle_Ctrl_" + str(middle)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(middleJoints[middle], query=True, ws=True, translation=True)
				cmds.xform(controls[middle], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(middleJoints[middle], query=True, ws=True, rotation=True)
				cmds.xform(controls[middle], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("L_Middle_Ctrl_*", middleJoints[middle], maintainOffset=True)
				point = cmds.pointConstraint("L_Middle_Ctrl_*", middleJoints[middle], maintainOffset=True)
			cmds.parent("L_Middle_Ctrl_2", "L_Middle_Ctrl_1")
			cmds.parent("L_Middle_Ctrl_1", "L_Middle_Ctrl_0")
			cmds.parent("L_Middle_Ctrl_0", "Left_Wrist_Fk")

			# Right ring
			for ring in range(len(ringJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Ring_Ctrl_" + str(ring)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(ringJoints[ring], query=True, ws=True, translation=True)
				cmds.xform(controls[ring], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(ringJoints[ring], query=True, ws=True, rotation=True)
				cmds.xform(controls[ring], ws=1, ro=(valRot[0], valRot[1], valRot[2]))

				orient = cmds.orientConstraint("L_Ring_Ctrl_*", ringJoints[ring], maintainOffset=True)
				point = cmds.pointConstraint("L_Ring_Ctrl_*", ringJoints[ring], maintainOffset=True)
			cmds.parent("L_Ring_Ctrl_2", "L_Ring_Ctrl_1")
			cmds.parent("L_Ring_Ctrl_1", "L_Ring_Ctrl_0")
			cmds.parent("L_Ring_Ctrl_0", "Left_Wrist_Fk")

			# Right pinky
			for pinky in range(len(pinkyJoints)):
				controls = [cmds.CreateNURBSCircle(), cmds.rename("nurbsCircle1", "L_Pinky_Ctrl_" + str(pinky)),
							cmds.scale(0.1, 0.1, 0.1)]
				# xform translation
				valPos = cmds.xform(pinkyJoints[pinky], query=True, ws=True, translation=True)
				cmds.xform(controls[pinky], ws=1, t=(valPos[0], valPos[1], valPos[2]))
				# xform rotation
				valRot = cmds.xform(pinkyJoints[pinky], query=True, ws=True, rotation=True)
				cmds.xform(controls[pinky], ws=1, ro=(valRot[0], valRot[1], valRot[2]))
				orient = cmds.orientConstraint("L_Pinky_Ctrl_*", pinkyJoints[pinky], maintainOffset=True)
				point = cmds.pointConstraint("L_Pinky_Ctrl_*", pinkyJoints[pinky], maintainOffset=True)
			cmds.parent("L_Pinky_Ctrl_2", "L_Pinky_Ctrl_1")
			cmds.parent("L_Pinky_Ctrl_1", "L_Pinky_Ctrl_0")
			cmds.parent("L_Pinky_Ctrl_0", "Left_Wrist_Fk")
			return wrist

	def head_control(*args, **kwargs):
		HeadJt = "E_Head_Jt"
		HeadCtrl = cmds.curve(name="Head_Ctrl", degree=3,
							  point=[(-0.801407, 0, 0.00716748), (-0.802768, 0.023587, -0.220859),
									 (-0.805489, 0.0707609, -0.676912),
									 (0.761595, -0.283043, -0.667253), (1.045492, -0.194522, -0.0218101),
									 (1.046678, -0.194804, 0.0403576), (0.758039, -0.282198, 0.63974),
									 (-0.806291, 0.0676615, 0.650803), (-0.803035, 0.0225538, 0.221713),
									 (-0.801407, 0, 0.00716748)], knot=[0, 0, 0, 1, 2, 3, 4, 5, 6, 7, 7, 7])
		cmds.scale(0.764, 1.591, 0.935)
		cmds.makeIdentity('Head_Ctrl', apply=True, translate=True, scale=True)
		valHead = cmds.xform(HeadJt, ws=True, query=True, translation=True)
		cmds.xform(HeadCtrl, ws=1, t=(valHead[0], valHead[1], valHead[2]))
		# orientHead = mc.orientConstraint(HeadCtrl, HeadJt)
		parentHead = cmds.parentConstraint(HeadCtrl, HeadJt)
		cmds.parent(HeadCtrl, "Ik_shoulder_ctrl")
		return HeadCtrl, HeadJt

	def master_control(*args, **kwargs):
		MasterCtrl = cmds.curve(name="Master_Ctrl", d=1, p=[(-4, 0, 0), (-2, 0, -1.5), (-2, 0, -0.5),
															(-0.5, 0, -0.5), (-0.5, 0, -2), (-1.5, 0, -2),
															(0, 0, -4), (1.5, 0, -2), (0.5, 0, -2), (0.5, 0, -0.5),
															(2, 0, -0.5), (2, 0, -1.5), (4, 0, 0), (2, 0, 1.5),
															(2, 0, 0.5), (0.5, 0, 0.5), (0.5, 0, 2), (1.5, 0, 2),
															(0, 0, 4), (-1.5, 0, 2), (-0.5, 0, 2), (-0.5, 0, 0.5),
															(-2, 0, 0.5), (-2, 0, 1.5), (-4, 0, 0)])
		# Parent everything to master control
		cmds.parent("A_Hip_Jt", MasterCtrl)
		cmds.parent("UpperBody_Grp", MasterCtrl)
		cmds.parent("Foot_Grp", MasterCtrl)
		cmds.parent("Knee_Grp", MasterCtrl)
		return MasterCtrl
