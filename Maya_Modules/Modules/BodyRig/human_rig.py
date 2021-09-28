# -*- coding: utf-8 -*-

import maya.cmds as mc
import maya.api.OpenMaya as OpenMaya
import maya.mel as mel
import random
import math
from functools import partial

"""
import human_rig as rig
import importlib
importlib.reload(rig)
window = rig.AutoRig_OptionsWindow()
window.create()
"""


class AutoRig_OptionsWindow(object):

	def __init__(self):
		self.window = 'ar_optionsWindow'
		self.title = 'Auto Rigging Tool'
		self.size = (340,550)
		self.supportsToolAction = True

	def create(self):
		if mc.window(self.window, exists = True):
			mc.deleteUI(self.window, window = True)
		self.window = mc.window(
			self.window,
			title=self.title,
			widthHeight=self.size,
			menuBar=True
		)
		self.commonMenu()
		mc.showWindow()
		
	def commonMenu(self):
		self.editMenu = mc.menu(label = 'Edit')
		self.editMenuDiv = mc.menuItem(d=True)
		self.editMenuskelRadio = mc.radioMenuItemCollection()
		self.editMenuTool = mc.menuItem(
			label='As Tool',
			radioButton=True,
			enable=self.supportsToolAction,
			command=self.editMenuToolCmd
		)
		self.helpMenu = mc.menu(label='Help')
		self.helpMenuItem = mc.menuItem(label='Help on %s' %self.title, command=self.helpMenuCmd)
		
		mc.columnLayout(columnAttach=('both', 2), rowSpacing=4,columnWidth=340)	
		mc.text("BIPEDAL CHARACTER", align="center")
		mc.text("   ")
		mc.text("Step 1: Create bipedal skeleton")	
		self.buttonSkelBi = mc.button(label='Create Skeleton', command=self.skeletonButton_B, width=110, height=40);
		
		mc.text("   ")
		mc.text("Step 2: Create Leg controls")
		mc.text("____________________________________")
		mc.text(label='LOWER BODY CONTROL', align='center' )
		buttonRigFootCtrl = mc.button(label='Legs Control', command=self.Feet_Control, width=120, height=40)
		buttonRigSpineCtrl = mc.button(label='Spine Control', command=self.Spine_Control, width=120, height=40, align="center")

		mc.text("   ")
		mc.text("Step 3: Create Torso/Arm controls")
		mc.text("__________________________________")
		mc.text(label='UPPER BODY CONTROL', align='center' )
		buttonRigArmCtrl = mc.button(label='Arm Control', command=self.Arm_Control, width=120, height=40)
		buttonRigFingersCtrl = mc.button(label='Fingers Control', command=self.Fingers_Control, width=120, height=40)
		buttonRigHeadCtrl = mc.button(label='Head Control', command=self.Head_Control, width=120, height=40)

		mc.text("   ")
		mc.text("Step 4: Create Master control")
		mc.text("___________________________________")
		mc.text("MASTER CONTROL",align='center')
		buttonMainCtrl = mc.button(label='Master Control', command=self.Master_Control, width=120, height=40, align='center')
		closeButton = mc.button(label="Close", command=self.closeWindow, width=120, height=40, align='center')
	
	def closeWindow(self,*args):
		if mc.window(self.window, exists=True):
			mc.deleteUI(self.window, window=True)
		
	
	def skeletonButton_B(self,*args):
		skeletonJT = SkeletonB()
		skeletonJT.__CreateSpineSkeleton__()
		skeletonJT.__CreateSkeletonLeg__()
		skeletonJT.__CreateSkeletonArm__()
		skeletonJT.__CreateSkeletonFingers__()
		skeletonJT.__MirrorJointsHands__()
		skeletonJT.__MirrorJointsLegs__()

	def skeletonButton_Q(self,*args):
		skeletonQT = SkeletonQ()
		skeletonQT.__CreateFrontLegsSkeleton__()
		skeletonQT.__CreateSpineSkeleton__()
		skeletonQT.__CreateBackLegsSkeleton__()
		skeletonQT.__MirrorJointsFrontLegs__()
		skeletonQT.__MirrorJointsBackLegs__()
		skeletonQT.__Tail__()
		skeletonQT.__Head__()

	def helpMenuCmd(self,*args):
		mc.launch(web='http://www.maya-python.com/')

	def editMenuSaveCmd(self,*args): 
		pass

	def editMenuResetCmd(self,*args): 
		pass

	def editMenuToolCmd(self,*args): 
		pass

	def editMenuActionCmd(self,*args): 
		pass
	
	def Feet_Control(*args, **kwargs):
		Feet_Ctrl = range(2)
		Ankle = 'R_Ankle_Jt'
		foot_ctrl = True
		if foot_ctrl:
			#Left Foot	
			Feet_Ctrl[0] = mc.curve(name ="ik_LeftFoot_Ctrl", degree = 1, 
				point=[(-0.440687, 0.0433772, 0.400889), (-0.440687, 0.0433772, -0.429444),
					(0.898906, -0.240469, -0.384559),(0.975205, -0.496435, -0.384559),
					(0.975205, -0.496435, 0.365874), (0.898906, -0.240469, 0.365874),
					(0.898906, -0.240469, -0.384559),(-0.440687, 0.0433772, -0.429444), 
					(-0.440687, 0.0433772, 0.400889),(-0.520228, -0.496554, 0.400889 ), 
					(-0.520228, -0.496554, -0.429444 ), (-0.440687, 0.0433772, -0.429444),
					(-0.440687, 0.0433772, 0.400889), (0.898906, -0.240469, 0.365874),
					(0.975205, -0.496435, 0.365874),(-0.520228, -0.496554, 0.400889),
					(-0.520228, -0.496554, -0.429444),(0.975205, -0.496435,-0.384559)],
				knot=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17])
			# Move pivot to ankle centre
			AnkleLeft = 'L_Ankle_Jt'
			valIk = mc.xform(AnkleLeft, query=True,ws=True, translation = True)
			mc.xform(Feet_Ctrl[0], ws = 1 ,t = (valIk[0],valIk[1],valIk[2]))
			# Ik Handles with foot bones
			mc.ikHandle(name="ikHandle_L_Ctrl", startJoint="L_Hip_Jt", endEffector="L_Ankle_Jt", solver="ikRPsolver", parentCurve=False)
			ikLeftMidToe = mc.ikHandle(name="ikHandle_L_Ctrl_MidToe", startJoint="L_Ankle_Jt", endEffector="L_Toe_Jt", solver="ikRPsolver", parentCurve=False)
			ikLeftEndToe = mc.ikHandle(name="ikHandle_L_Ctrl_Toe", startJoint="L_Toe_Jt", endEffector="L_ToeEnd_Jt", solver="ikRPsolver", parentCurve=False)
			grpIkLeft = mc.group("ikHandle_L_Ctrl", n="GrpIk_LeftLeg")
			mc.parent(grpIkLeft, Feet_Ctrl[0])
			orientLeftFoot = mc.orientConstraint(Feet_Ctrl[0],"L_Ankle_Jt",maintainOffset = True)
			
			# Add parent constriant and new controller to control feet rotation and its position
			ToeLeft = 'L_Toe_Jt'
			leftToeRot = mc.curve(name = "Left_Toe_Rotation", d=1, 
				p=[(-0.5, 0, 0),(-0.5, 0, 2),(-2, 0, 2),
				(0, 0, 4),(2, 0, 2),(0.5, 0, 2),
				(0.5, 0, 0),(0.5, 0, -2),(2, 0, -2),
				(0, 0, -4),(-2, 0, -2),(-0.5, 0, -2),
				(-0.5, 0, 0)]);
			scale = mc.scale(0.15,0.15,0.15)
			valToe = mc.xform(ToeLeft, query=True,ws=True, translation = True)
			mc.xform(leftToeRot, ws = 1 ,t = (valToe[0],valToe[1],valToe[2]))
			parentLeftFoot = mc.parentConstraint(leftToeRot, "L_Toe_Jt", maintainOffset = True)
			mc.parent(parentLeftFoot, Feet_Ctrl[0])
			leftFootParent = mc.parent(leftToeRot,Feet_Ctrl[0])
			mc.parent(ikLeftMidToe,ikLeftEndToe,leftToeRot)
			
			# Add ball rotation for left ankle 
			LeftBallCurve = mc.curve(name = "LeftBallCtrl",degree=1, 
				point=[(-0.989704 ,0 ,-0.00369912),(-0.310562, 0, -0.998289),
				(0.138488, 0, -0.990867 ),(-0.499831, 0, 0.0111455),
				(-0.0656259, 0, 1.009447),(-0.633433, 0, 1.013158),
				(-0.989704, 0, -0.00369912)],
				knot=[0,1,2,3,4,5,6])
			leftBallCtrl =[mc.select("LeftBallCtrl", r=True),mc.scale(0.4,0.4,0.4), mc.rename('L_Ball_Rotation')]     
			valBall = mc.xform(AnkleLeft, query=True,ws=True, translation = True)
			mc.xform(leftBallCtrl[0], ws = 1 ,t = (valBall[0],valBall[1],valBall[2]))
			mc.rotate('90deg',0,0, leftBallCtrl[0])
			mc.parent("ikHandle_L_Ctrl",leftBallCtrl[0])
			mc.parent("L_Ball_Rotation", Feet_Ctrl[0])
			# Left knee cap
			kneeLeft = 'L_Knee_Jt'
			leftKneeCap = [mc.CreateNURBSCircle(),mc.scale(0.3,0.3,0.3),mc.select("nurbsCircle1"), mc.rename("nurbsCircle1", 'L_KneeCap'),mc.setAttr('L_KneeCap.rz', 90)]
			mc.xform(kneeLeft+".tx",kneeLeft+".ty",kneeLeft+".tz")
			valKnee = mc.xform(kneeLeft, query=True,ws=True, translation = True)
			mc.xform(leftKneeCap[0], ws = 1 ,t = (valKnee[0]+2,valKnee[1],valKnee[2]))

			if leftKneeCap:
				mc.poleVectorConstraint('L_KneeCap','ikHandle_L_Ctrl')
				#Right Foot
				Feet_Ctrl[1] = mc.curve(name ="ik_RightFoot_Ctrl", degree = 1, 
					point=[(0.898914, -0.240476, 0.383674), (-0.440521 ,0.0411603 ,0.428909 ),
					(-0.440521 ,0.0411603 ,-0.400341 ),(0.898914 ,-0.240476 ,-0.365796),
					(0.898914 ,-0.240476 ,0.383674 ), (0.974311 ,-0.496509 ,0.383674),
					(0.974311 ,-0.496509 ,-0.365796),(-0.517088, -0.495087, -0.400341), 
					(-0.517088, -0.495087, 0.428909),(0.974311, -0.496509, 0.383674),
					(0.898914 ,-0.240476 ,0.383674), (-0.440521 ,0.0411603 ,0.428909), 
					(-0.517088 ,-0.495087 ,0.428909),
					(-0.517088, -0.495087, -0.400341 ), (-0.440521, 0.0411603, -0.400341),
					(0.898914, -0.240476, -0.365796),(0.974311, -0.496509, -0.365796)],
					knot=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16])
				# Move pivot to ankle centre
				AnkleRight = 'R_Ankle_Jt'
				valIkRight = mc.xform(AnkleRight, query=True,ws=True, translation = True)
				if AnkleRight != AnkleLeft:
					mc.xform(Feet_Ctrl[1], ws = 1 ,t = (valIkRight[0],valIkRight[1],valIkRight[2]))
					# Ik Handles with foot bones
					mc.ikHandle(name="ikHandle_R_Ctrl", startJoint="R_Hip_Jt", endEffector="R_Ankle_Jt", solver="ikRPsolver", parentCurve=False)
					ikRightMidToe = mc.ikHandle(name="ikHandle_R_Ctrl_MidToe", startJoint="R_Ankle_Jt", endEffector="R_Toe_Jt", solver="ikRPsolver", parentCurve=False)
					ikRightEndToe = mc.ikHandle(name="ikHandle_R_Ctrl_Toe", startJoint="R_Toe_Jt", endEffector="R_ToeEnd_Jt", solver="ikRPsolver", parentCurve=False)
					grpIkRight = mc.group("ikHandle_R_Ctrl", n="GrpIk_RightLeg")
					mc.parent(grpIkRight, Feet_Ctrl[1])
					orientRightFoot = mc.orientConstraint(Feet_Ctrl[1],"R_Ankle_Jt",maintainOffset = True)
					# Add parent constriant and new controller to control feet rotation and its position
					ToeRight= 'R_Toe_Jt'
					rightToeRot = mc.curve(name = "Right_Toe_Rotation", d=1, 
						p=[(-0.5, 0, 0),(-0.5, 0, 2),(-2, 0, 2),
						(0, 0, 4),(2, 0, 2),(0.5, 0, 2),
						(0.5, 0, 0),(0.5, 0, -2),(2, 0, -2),
						(0, 0, -4),(-2, 0, -2),(-0.5, 0, -2),
						(-0.5, 0, 0)]);
					scale = mc.scale(0.15,0.15,0.15)
					valToeRight = mc.xform(ToeRight, query=True,ws=True, translation = True)
					mc.xform(rightToeRot, ws = 1 ,t = (valToeRight[0],valToeRight[1],valToeRight[2]))
					parentRightFoot = mc.parentConstraint(rightToeRot, "R_Toe_Jt", maintainOffset = True)
					mc.parent(parentRightFoot, Feet_Ctrl[1])
					leftFootParent = mc.parent(rightToeRot,Feet_Ctrl[1])
					mc.parent(ikRightMidToe,ikRightEndToe,rightToeRot)
					# Add ball rotation for left ankle 
					RightBallCurve = mc.curve(name = "RightBallCtrl",degree=1, 
						point=[(-0.989704 ,0 ,-0.00369912),(-0.310562, 0, -0.998289),
						(0.138488, 0, -0.990867 ),(-0.499831, 0, 0.0111455),
						(-0.0656259, 0, 1.009447),(-0.633433, 0, 1.013158),
						(-0.989704, 0, -0.00369912)],
						knot=[0,1,2,3,4,5,6])
					rightBallCtrl =[mc.select("RightBallCtrl", r=True),mc.scale(0.4,0.4,0.4), mc.rename('R_Ball_Rotation')]
					valBallRight = mc.xform(AnkleRight, query=True,ws=True, translation = True)
					mc.xform(rightBallCtrl[0], ws = 1 ,t = (valBallRight[0],valBallRight[1],valBallRight[2]))
					mc.rotate('90deg',0,0, rightBallCtrl[0])
					mc.parent("ikHandle_R_Ctrl",rightBallCtrl[0])
					mc.parent("R_Ball_Rotation", Feet_Ctrl[1])
					# Right Knee cap
					kneeRight= 'R_Knee_Jt'
					rightKneeCap = [mc.CreateNURBSCircle(),mc.scale(0.3,0.3,0.3),mc.select("nurbsCircle1"), mc.rename("nurbsCircle1", 'R_KneeCap'),mc.setAttr('R_KneeCap.rz', 90)]
					mc.xform(kneeRight+".tx",kneeRight+".ty",kneeRight+".tz")
					valKneeRight = mc.xform(kneeRight, query=True,ws=True, translation = True)
					mc.xform(rightKneeCap[0], ws = 1 ,t = (valKneeRight[0]+2,valKneeRight[1],valKneeRight[2]))
					if rightKneeCap:
						mc.poleVectorConstraint('R_KneeCap','ikHandle_R_Ctrl')
						#Creating group for both feet
						grp = mc.group(em=True, name = "Foot_Grp")
						mc.parent(Feet_Ctrl,'Foot_Grp',relative = True)
						mc.move(-0.24,0.486,-0.689, grp+".scalePivot", grp+".rotatePivot", absolute=True)
						grpKnees = mc.group(em=True, name = "Knee_Grp")
						mc.parent(rightKneeCap, leftKneeCap, grpKnees)

	def Spine_Control(*args, **kwargs):
		scaleParts=0.4
		ctrl = True
		bodyPart = range(2)
		# Dictionary for parenting joints with controllers
		parentPart = {"Hip_Jt_1":1,"D_Neck_Jt":2, "A_Hip_Jt":3}
		# Additional list for spline joints
		jointList = ["A_Hip_Jt","Hip_Jt_0","Hip_Jt_1","Hip_Jt_2","Hip_Jt_2","D_Neck_Jt"]
		if ctrl:
			if parentPart["A_Hip_Jt"]:
				bodyPart[0] = mc.curve(name="Ik_hip_ctrl", degree=1,
					point=[(-2.5, 0.6, 1.9),(2.5,0.6,1.9),(2.5,0.6,-1.9),(-2.5,0.6,-1.9),(-2.5,0.6,1.9),
					(-2.5,-2.1,1.9),(2.5,-2.1,1.9 ),(2.5,0.6,1.9),(2.5,0.6,-1.9),(2.5,-2.1,-1.9),
					(2.5,-2.1,1.9),(-2.5,-2.1,1.9),(-2.5,-2.1,-1.9),(-2.5,0.6,-1.9),(-2.5,-2.1,-1.9),
					(2.5,-2.1,-1.9 )],
					knot=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
				Hip_Pos = [mc.scale(scaleParts,scaleParts,scaleParts),mc.setAttr(bodyPart[0] +".ry",90)]
				hipJt = "A_Hip_Jt"
				valHip = mc.xform(hipJt,ws=True, query=True,translation = True)
				mc.xform(bodyPart[0],ws=1,t=(valHip[0],valHip[1],valHip[2]))
						
				if parentPart != "A_Hip_Jt":
					bodyPart[1] = mc.curve(name="Ik_shoulder_ctrl", degree=1,
						point=[(2.3,-0.3,1.6),(2.2,0.2,-1.3),(-2.2,0.2,-1.3),(-2.3,-0.3,1.6),( 2.3,-0.3,1.6),
						(2.5,-2.7,1.9),(-2.5,-2.7,1.9),(-2.5,-2.7,-1.9),(2.5,-2.7,-1.9),(2.5,-2.7,1.9),
						(2.5,-2.7,-1.9),(2.2,0.2,-1.3),(-2.2,0.2,-1.3),(-2.5,-2.7,-1.9),(-2.5,-2.7,1.9),
						(-2.3,-0.3,1.6)],
						knot=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15])
					Shoulders_Pos = [mc.scale(scaleParts,scaleParts,scaleParts),mc.setAttr(bodyPart[1] +".ry",90)]
					shoJt = "D_Neck_Jt"
					valSho = mc.xform(shoJt,ws=True,query=True,translation = True)
					mc.xform(bodyPart[1],ws=1,t=(valSho[0],valSho[1],valSho[2]))
					spineIk = mc.ikHandle(name="Spine_Ik", startJoint=jointList[3], endEffector=jointList[5], solver="ikSCsolver", parentCurve=False)
							
					# Middle spine control
					if parentPart["Hip_Jt_1"]:
						midSpine= 'Hip_Jt_1'
						toContolJoints = jointList[1], jointList[2]
						#Spink Ik before creating controller
						spine_01 = mc.ikHandle(name="Spine_Ik_01", startJoint=jointList[0], endEffector=jointList[2], solver="ikSCsolver", parentCurve=False)
						midSpineCtrl = [mc.CreateNURBSCircle(),mc.scale(1.2,1.2,1.2),mc.select("nurbsCircle1"), mc.rename("nurbsCircle1", 'S_Ctrl')]
						mc.xform(midSpine+".tx",midSpine+".ty",midSpine+".tz")
						valMidSpine = mc.xform(midSpine, query=True,ws=True, translation = True)
						mc.xform(midSpineCtrl[0], ws = 1 ,t = (valMidSpine[0],valMidSpine[1],valMidSpine[2]))
								
					elif ctrl != True:
						if parentPart["A_Hip_Jt","D_Neck_Jt", "Hip_Jt_1"] is False:
							parentPart.clear()
							mc.delete()
							print ctrl
					else:
						mc.error("No selection to control")
				# Parenting each spine ik to their controllers
				# Parent shoulder control
				mc.parent('Spine_Ik','Ik_shoulder_ctrl', world=False)
				mc.orientConstraint('Ik_shoulder_ctrl',jointList[5], maintainOffset=True)
				# Parent middle spine control
				mc.parentConstraint("S_Ctrl", "Spine_Ik_01",skipTranslate='y',maintainOffset=True)
				# Parent hip control to the main hip
				mc.parentConstraint("Ik_hip_ctrl", jointList[0],maintainOffset=True)
				# Parent all controls together
				mc.parent("Ik_shoulder_ctrl", "S_Ctrl")
				mc.parent("S_Ctrl", "Ik_hip_ctrl")
				mc.parent("Spine_Ik_01", "S_Ctrl")
				mc.group('Ik_hip_ctrl',name="UpperBody_Grp")
				# return the values
				return scaleParts, bodyPart, parentPart
			else:
				# parentPart["A_Hip_Jt"]
				pass
		else:
			# ctrl
			pass

	def Arm_Control(*args, **kwargs):
		armListRight = ["R_Collarbone_Jt","R_Shoulder_Jt","R_Wrist_Jt"]
		armListLeft = ["L_Collarbone_Jt","L_Shoulder_Jt","L_Wrist_Jt"]
		armCtrl = True
		#Ik for right arm
		mc.ikHandle(name="R_ArmCtrl", startJoint=armListRight[1], endEffector=armListRight[2], solver="ikRPsolver", parentCurve=False)
		#Ik for left arm
		mc.ikHandle(name="L_ArmCtrl", startJoint=armListLeft[1], endEffector=armListLeft[2], solver="ikRPsolver", parentCurve=False)

		#Right arm fk controls
		for i in range(len(armListRight)):
			controls = [mc.CreateNURBSCircle()]
			mc.rename('nurbsCircle1', 'Fk_R_ForeArm_'+str(i))
			if i in range(len(armListRight)):
				scaleNurbs = 0.5
				mc.rotate("-45deg",0,0,"Fk_R_ForeArm_"+str(i))
				mc.scale(scaleNurbs,scaleNurbs,scaleNurbs)
		
		#Left arm fk controls
		for i in range(len(armListLeft)):
			controls = [mc.CreateNURBSCircle()]
			mc.rename('nurbsCircle1', 'Fk_L_ForeArm_'+str(i))
			if i in range(len(armListLeft)):
				scaleNurbs = 0.5
				mc.rotate("45deg",0,0,"Fk_L_ForeArm_"+str(i))
				mc.scale(scaleNurbs,scaleNurbs,scaleNurbs)
		
		#Fk Arms
		#Right
		FKarmR = ["Fk_R_ForeArm_0","Fk_R_ForeArm_1","Fk_R_ForeArm_2"]
		#Left
		FKarmL = ["Fk_L_ForeArm_0","Fk_L_ForeArm_1","Fk_L_ForeArm_2"]
		
		#Right Arm
		if armCtrl:
			if FKarmR[0] is "Fk_R_ForeArm_0":
				#Collar Bone
				valRcolar = mc.xform(armListRight[0], query=True,ws=True, translation = True)
				mc.xform(FKarmR[0], ws = 1 ,t = (valRcolar[0],valRcolar[1],valRcolar[2]))
				mc.rotate(0,0,"90deg",FKarmR[0])
				orient = mc.orientConstraint(FKarmR[0],armListRight[0], mo = True)
				parent = mc.parentConstraint(FKarmR[0],armListRight[0], mo = True)
				mc.parent(FKarmR[0],"Ik_shoulder_ctrl")

			if FKarmR[1] is "Fk_R_ForeArm_1":
				#Shoulder Bone
				valRshoulder = mc.xform(armListRight[1], query=True,ws=True, translation = True)
				mc.xform(FKarmR[1], ws = 1 ,t = (valRshoulder[0],valRshoulder[1],valRshoulder[2]))
				orient = mc.orientConstraint(FKarmR[1],armListRight[1], mo = True)
				parent = mc.parentConstraint(FKarmR[1],armListRight[1], mo = True)
				mc.parent(FKarmR[1],"Ik_shoulder_ctrl")

			if FKarmR[2] is "Fk_R_ForeArm_2":
				#Wrist Bone
				valRwrist = mc.xform(armListRight[2], query=True,ws=True, translation = True)
				mc.xform(FKarmR[2], ws = 1 ,t = (valRwrist[0],valRwrist[1],valRwrist[2]))
				orient = mc.orientConstraint(FKarmR[2],armListRight[2], mo = True)
				parent = mc.parent("R_ArmCtrl",FKarmR[2])
				mc.parent(FKarmR[2],"Ik_shoulder_ctrl")
				mc.parent(FKarmR[2], FKarmR[1])
			else:
				return FKarmR

		#Left Arm
		if armCtrl:
			if FKarmL[0] is "Fk_L_ForeArm_0":
				#Collar Bone
				valRcolar = mc.xform(armListLeft[0], query=True,ws=True, translation = True)
				mc.xform(FKarmL[0], ws = 1 ,t = (valRcolar[0],valRcolar[1],valRcolar[2]))
				mc.rotate(0,0,"90deg",FKarmL[0])
				orient = mc.orientConstraint(FKarmL[0],armListLeft[0], mo = True)
				parent = mc.parentConstraint(FKarmL[0],armListLeft[0], mo = True)
				mc.parent(FKarmL[0],"Ik_shoulder_ctrl")

			if FKarmL[1] is "Fk_L_ForeArm_1":
				#Shoulder Bone
				valRshoulder = mc.xform(armListLeft[1], query=True,ws=True, translation = True)
				mc.xform(FKarmL[1], ws = 1 ,t = (valRshoulder[0],valRshoulder[1],valRshoulder[2]))
				orient = mc.orientConstraint(FKarmL[1],armListLeft[1], mo = True)
				parent = mc.parentConstraint(FKarmL[1],armListLeft[1], mo = True)
				mc.parent(FKarmL[1],"Ik_shoulder_ctrl")

			if FKarmL[2] is "Fk_L_ForeArm_2":
				#Wrist Bone
				valRwrist = mc.xform(armListLeft[2], query=True,ws=True, translation = True)
				mc.xform(FKarmL[2], ws = 1 ,t = (valRwrist[0],valRwrist[1],valRwrist[2]))
				orient = mc.orientConstraint(FKarmL[2],armListLeft[2], mo = True)
				parent = mc.parent("L_ArmCtrl",FKarmL[2])
				mc.parent(FKarmL[2],"Ik_shoulder_ctrl")
				mc.parent(FKarmL[2], FKarmL[1])
			else:
				return FKarmL
					
		#Right elbow control
		elbowRight = 'R_Elbow_Jt'
		rightElbowCtrl = [mc.CreateNURBSCircle(),mc.scale(0.3,0.3,0.3),mc.select("nurbsCircle1"), mc.rename("nurbsCircle1", 'R_ElbowCtrl'), mc.setAttr('R_ElbowCtrl.rz', 90)]
		
		mc.xform(elbowRight+".tx",elbowRight+".ty",elbowRight+".tz")
		valElbow = mc.xform(elbowRight, query=True,ws=True, translation = True)
		mc.xform(rightElbowCtrl[0], ws = 1 ,t = (valElbow[0]-0.6,valElbow[1],valElbow[2]))
		if rightElbowCtrl:
			mc.poleVectorConstraint(rightElbowCtrl[3],'R_ArmCtrl')
			mc.parent(rightElbowCtrl[3],FKarmR[2])
		
		#Left elbow control
		elbowLeft = 'L_Elbow_Jt'
		leftElbowCtrl = [mc.CreateNURBSCircle(),mc.scale(0.3,0.3,0.3),mc.select("nurbsCircle1"), mc.rename("nurbsCircle1", 'L_ElbowCtrl'), mc.setAttr('L_ElbowCtrl.rz', 90)]
		
		mc.xform(elbowLeft+".tx",elbowLeft+".ty",elbowLeft+".tz")
		valElbow = mc.xform(elbowLeft, query=True,ws=True, translation = True)
		mc.xform(leftElbowCtrl[0], ws = 1 ,t = (valElbow[0]-0.6,valElbow[1],valElbow[2]))
		if leftElbowCtrl:
			mc.poleVectorConstraint(leftElbowCtrl[3],'L_ArmCtrl')
			mc.parent(leftElbowCtrl[3],FKarmL[2])
		mc.parent(FKarmR[1],FKarmR[0])
		mc.parent(FKarmL[1],FKarmL[0])
		return FKarmR,FKarmL,armListRight,armListLeft,armCtrl
		
	def Fingers_Control(*args,**kwargs):
		wrist = True
		wristJt = ["R_Wrist_Jt","L_Wrist_Jt"]

		# Create Wrists for both hands
		if wrist is True:
			# Right hand  side
			wristRight = mc.circle(name = "Right_Wrist_Fk",ch=1, o=1, r=0.5, nr=(0,1,0))
			mc.scale(0.5,0.5,0.5)
			valWristRight = mc.xform(wristJt[0], query=True,ws=True, translation = True)
			mc.xform(wristRight, ws = 1 ,t = (valWristRight[0],valWristRight[1],valWristRight[2]))
			valRotRight = mc.xform(wristJt[0], query=True,ws=True, rotation = True)
			mc.xform(wristRight, ws = 1 ,ro = (valRotRight[0],valRotRight[1],valRotRight[2]))
			orientWrist = mc.orientConstraint(wristRight, wristJt[0],mo = True)
			# Parent to wrist control
			mc.parent(wristRight,"Fk_R_ForeArm_2")
			
			wristLeft = mc.circle(name = "Left_Wrist_Fk",ch=1, o=1, r=0.5, nr=(0,1,0))
			mc.scale(0.5,0.5,0.5)
			
			valWristLeft = mc.xform(wristJt[1], query=True,ws=True, translation = True)
			mc.xform(wristLeft, ws = 1 ,t = (valWristLeft[0],valWristLeft[1],valWristLeft[2]))
			valRotLeft = mc.xform(wristJt[1], query=True,ws=True, rotation = True)
			mc.xform(wristLeft, ws = 1 ,ro = (valRotLeft[0],valRotLeft[1],valRotLeft[2]))
			orientWrist = mc.orientConstraint(wristLeft, wristJt[1],mo = True)
			# Parent to wrist control
			mc.parent(wristLeft,"Fk_L_ForeArm_2")
				
			# Lists of the right fingers joints 
			thumbJoints = ["R_Thumb01_Jt","R_Thumb02_Jt"]
			indexJoints = ["R_IndexFinger01_Jt","R_IndexFinger02_Jt","R_IndexFinger03_Jt"]
			middleJoints = ["R_MiddleFinger01_Jt","R_MiddleFinger02_Jt","R_MiddleFinger03_Jt"]
			ringJoints = ["R_RingFinger01_Jt","R_RingFinger02_Jt","R_RingFinger03_Jt"]
			pinkyJoints = ["R_Pinky01_tJt","R_Pinky02_Jt","R_Pinky03_Jt"]
			# All joints
			# controlsJoints = [thumbJoints,indexJoints,middleJoints,ringJoints,pinkyJoints]

			# Right thumb 
			for thumbs in range(len(thumbJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "R_Thumb_Ctrl_"+str(thumbs)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(thumbJoints[thumbs],query=True,ws=True,translation=True)
				mc.xform(controls[thumbs],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(thumbJoints[thumbs],query=True,ws=True,rotation=True)
				mc.xform(controls[thumbs],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("R_Thumb_Ctrl_*",thumbJoints[thumbs], maintainOffset=True)
				point = mc.pointConstraint("R_Thumb_Ctrl_*",thumbJoints[thumbs], maintainOffset=True)

			#Finally parent controlers to the wrist   
			mc.parent("R_Thumb_Ctrl_1","R_Thumb_Ctrl_0")
			mc.parent("R_Thumb_Ctrl_0","Right_Wrist_Fk")
				
			# Right index
			for index in range(len(indexJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "R_Index_Ctrl_"+str(index)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(indexJoints[index],query=True,ws=True,translation=True)
				mc.xform(controls[index],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(indexJoints[index],query=True,ws=True,rotation=True)
				mc.xform(controls[index],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("R_Index_Ctrl_*",indexJoints[index], maintainOffset=True)
				point = mc.pointConstraint("R_Index_Ctrl_*",indexJoints[index], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("R_Index_Ctrl_2", "R_Index_Ctrl_1")
			mc.parent("R_Index_Ctrl_1","R_Index_Ctrl_0")
			mc.parent("R_Index_Ctrl_0", "Right_Wrist_Fk")

			# Right middle
			for middle in range(len(middleJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "R_Middle_Ctrl_"+str(middle)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(middleJoints[middle],query=True,ws=True,translation=True)
				mc.xform(controls[middle],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(middleJoints[middle],query=True,ws=True,rotation=True)
				mc.xform(controls[middle],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("R_Middle_Ctrl_*",middleJoints[middle], maintainOffset=True)
				point = mc.pointConstraint("R_Middle_Ctrl_*",middleJoints[middle], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("R_Middle_Ctrl_2", "R_Middle_Ctrl_1")
			mc.parent("R_Middle_Ctrl_1","R_Middle_Ctrl_0")
			mc.parent("R_Middle_Ctrl_0", "Right_Wrist_Fk")
				
			# Right ring
			for ring in range(len(ringJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "R_Ring_Ctrl_"+str(ring)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(ringJoints[ring],query=True,ws=True,translation=True)
				mc.xform(controls[ring],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(ringJoints[ring],query=True,ws=True,rotation=True)
				mc.xform(controls[ring],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("R_Ring_Ctrl_*",ringJoints[ring], maintainOffset=True)
				point = mc.pointConstraint("R_Ring_Ctrl_*",ringJoints[ring], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("R_Ring_Ctrl_2", "R_Ring_Ctrl_1")
			mc.parent("R_Ring_Ctrl_1","R_Ring_Ctrl_0")
			mc.parent("R_Ring_Ctrl_0", "Right_Wrist_Fk")
				
			# Right pinky
			for pinky in range(len(pinkyJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "R_Pinky_Ctrl_"+str(pinky)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(pinkyJoints[pinky],query=True,ws=True,translation=True)
				mc.xform(controls[pinky],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(pinkyJoints[pinky],query=True,ws=True,rotation=True)
				mc.xform(controls[pinky],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("R_Pinky_Ctrl_*",pinkyJoints[pinky], maintainOffset=True)
				point = mc.pointConstraint("R_Pinky_Ctrl_*",pinkyJoints[pinky], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("R_Pinky_Ctrl_2", "R_Pinky_Ctrl_1")
			mc.parent("R_Pinky_Ctrl_1","R_Pinky_Ctrl_0")
			mc.parent("R_Pinky_Ctrl_0", "Right_Wrist_Fk")

			# Lists of the left fingers joints 
			thumbJoints = ["L_Thumb01_Jt","L_Thumb02_Jt"]
			indexJoints = ["L_IndexFinger01_Jt","L_IndexFinger02_Jt","L_IndexFinger03_Jt"]
			middleJoints = ["L_MiddleFinger01_Jt","L_MiddleFinger02_Jt","L_MiddleFinger03_Jt"]
			ringJoints = ["L_RingFinger01_Jt","L_RingFinger02_Jt","L_RingFinger03_Jt"]
			pinkyJoints = ["L_Pinky01_tJt","L_Pinky02_Jt","L_Pinky03_Jt"]
			#All joints
			#controlsJoints = [thumbJoints,indexJoints,middleJoints,ringJoints,pinkyJoints]

			#Left thumb
			for thumbs in range(len(thumbJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "L_Thumb_Ctrl_"+str(thumbs)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(thumbJoints[thumbs],query=True,ws=True,translation=True)
				mc.xform(controls[thumbs],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(thumbJoints[thumbs],query=True,ws=True,rotation=True)
				mc.xform(controls[thumbs],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("L_Thumb_Ctrl_*",thumbJoints[thumbs], maintainOffset=True)
				point = mc.pointConstraint("L_Thumb_Ctrl_*",thumbJoints[thumbs], maintainOffset=True)

			#Finally parent controlers to the wrist   
			mc.parent("L_Thumb_Ctrl_1","L_Thumb_Ctrl_0")
			mc.parent("L_Thumb_Ctrl_0","Left_Wrist_Fk")
							
			# Leftt index
			for index in range(len(indexJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "L_Index_Ctrl_"+str(index)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(indexJoints[index],query=True,ws=True,translation=True)
				mc.xform(controls[index],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(indexJoints[index],query=True,ws=True,rotation=True)
				mc.xform(controls[index],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("L_Index_Ctrl_*",indexJoints[index], maintainOffset=True)
				point = mc.pointConstraint("L_Index_Ctrl_*",indexJoints[index], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("L_Index_Ctrl_2", "L_Index_Ctrl_1")
			mc.parent("L_Index_Ctrl_1","L_Index_Ctrl_0")
			mc.parent("L_Index_Ctrl_0", "Left_Wrist_Fk")

			# Left middle
			for middle in range(len(middleJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "L_Middle_Ctrl_"+str(middle)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(middleJoints[middle],query=True,ws=True,translation=True)
				mc.xform(controls[middle],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(middleJoints[middle],query=True,ws=True,rotation=True)
				mc.xform(controls[middle],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("L_Middle_Ctrl_*",middleJoints[middle], maintainOffset=True)
				point = mc.pointConstraint("L_Middle_Ctrl_*",middleJoints[middle], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("L_Middle_Ctrl_2", "L_Middle_Ctrl_1")
			mc.parent("L_Middle_Ctrl_1","L_Middle_Ctrl_0")
			mc.parent("L_Middle_Ctrl_0", "Left_Wrist_Fk")    
							
			# Left ring
			for ring in range(len(ringJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "L_Ring_Ctrl_"+str(ring)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(ringJoints[ring],query=True,ws=True,translation=True)
				mc.xform(controls[ring],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(ringJoints[ring],query=True,ws=True,rotation=True)
				mc.xform(controls[ring],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("L_Ring_Ctrl_*",ringJoints[ring], maintainOffset=True)
				point = mc.pointConstraint("L_Ring_Ctrl_*",ringJoints[ring], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("L_Ring_Ctrl_2", "L_Ring_Ctrl_1")
			mc.parent("L_Ring_Ctrl_1","L_Ring_Ctrl_0")
			mc.parent("L_Ring_Ctrl_0", "Left_Wrist_Fk")  
							
			# Left pinky
			for pinky in range(len(pinkyJoints)):
				controls = [mc.CreateNURBSCircle(), mc.rename("nurbsCircle1", "L_Pinky_Ctrl_"+str(pinky)), mc.scale(0.1,0.1,0.1)]
				#xform translation
				valPos = mc.xform(pinkyJoints[pinky],query=True,ws=True,translation=True)
				mc.xform(controls[pinky],ws=1,t=(valPos[0],valPos[1],valPos[2]))
				#xform rotation
				valRot = mc.xform(pinkyJoints[pinky],query=True,ws=True,rotation=True)
				mc.xform(controls[pinky],ws=1,ro=(valRot[0],valRot[1],valRot[2]))
				orient = mc.orientConstraint("L_Pinky_Ctrl_*",pinkyJoints[pinky], maintainOffset=True)
				point = mc.pointConstraint("L_Pinky_Ctrl_*",pinkyJoints[pinky], maintainOffset=True)

			#Finally parent controlers to the wrist
			mc.parent("L_Pinky_Ctrl_2", "L_Pinky_Ctrl_1")
			mc.parent("L_Pinky_Ctrl_1","L_Pinky_Ctrl_0")
			mc.parent("L_Pinky_Ctrl_0", "Left_Wrist_Fk")
			
			return wrist
	
	def Head_Control(*args,**kwargs):
		HeadJt = "E_Head_Jt"
		HeadCtrl = mc.curve(name="Head_Ctrl",degree=3,
			point=[(-0.801407, 0, 0.00716748),(-0.802768, 0.023587, -0.220859), (-0.805489, 0.0707609, -0.676912),
			(0.761595, -0.283043, -0.667253), (1.045492, -0.194522, -0.0218101), (1.046678, -0.194804, 0.0403576),
			(0.758039, -0.282198, 0.63974),(-0.806291, 0.0676615, 0.650803),(-0.803035, 0.0225538, 0.221713),
			(-0.801407, 0, 0.00716748)],
			knot=[0,0,0,1,2,3,4,5,6,7,7,7])
		mc.scale(0.764,1.591,0.935)
		mc.makeIdentity( 'Head_Ctrl', apply=True, translate=True,scale=True)
		valHead = mc.xform(HeadJt,ws=True,query=True,translation=True)
		mc.xform(HeadCtrl,ws=1,t = (valHead[0],valHead[1],valHead[2]))
		parentHead = mc.parentConstraint(HeadCtrl, HeadJt)
		mc.parent(HeadCtrl,"Ik_shoulder_ctrl")	
		return HeadCtrl,HeadJt

	def Master_Control(*args,**kwargs):
		MasterCtrl = mc.curve(name = "Master_Ctrl",d=1, 
			p=[(-4, 0, 0),(-2, 0, -1.5),(-2, 0, -0.5),
			(-0.5, 0, -0.5),(-0.5, 0, -2),(-1.5, 0, -2),
			(0, 0, -4),(1.5, 0, -2),(0.5, 0, -2),(0.5, 0, -0.5),
			(2, 0, -0.5),(2, 0, -1.5),(4, 0, 0),(2, 0, 1.5),
			(2, 0, 0.5),(0.5, 0, 0.5),(0.5, 0, 2),(1.5, 0, 2),
			(0, 0, 4),(-1.5, 0, 2),(-0.5, 0, 2),(-0.5, 0, 0.5),
			(-2, 0, 0.5),(-2, 0, 1.5),(-4, 0, 0)]);
		mc.parent("A_Hip_Jt", MasterCtrl)
		mc.parent("UpperBody_Grp", MasterCtrl)
		mc.parent("Foot_Grp",MasterCtrl)
		mc.parent("Knee_Grp", MasterCtrl)	
		return MasterCtrl


class SkeletonB(object):

	def __CreateSpineSkeleton__(self):
		self.HipJoint = mc.joint(name='A_Hip_Jt', position=(0.008, 4.451, 0))
		mc.joint('A_Hip_Jt', edit=True, zso=True, oj='xyz')
		numJt = range(4)
		jtPosX = 0.08
		jtPosY = 0.05
		for joints in numJt: 
			extraStrJt ="Hip_Jt_"
			extraJt = mc.joint(name= extraStrJt+str(joints), position=(0.008, 4.451,0))
			mc.joint(extraStrJt+str(joints), edit=True, zso=True, oj='xyz')
			mc.select(extraStrJt+str(joints))
			jointList = mc.ls(selection=True)
			if joints:
				jtPosY += 0.18
				jtPosX += -0.08
				mc.select(extraStrJt+str(joints))
				mc.move(0.3,0.0,0.0)
				#mc.move(0.008*randPos,4.751+jtPosY,0, extraStrJt+str(joints), absolute= True)
				mc.move(joints*0.008-0.2,4.751+joints*jtPosY,0, extraStrJt+str(joints), absolute= True)
		mc.move(jtPosX, 4.451+0.9*2, 0)
		self.NeckJoint = mc.joint(name='D_Neck_Jt', position=(-0.089, 6.965, 0))
		mc.joint('D_Neck_Jt', edit=True, zso=True, oj='xyz')
		self.HeadJoint = mc.joint(name='E_Head_Jt', position=(-0.026, 7.306, 0))
		mc.joint('E_Head_Jt', edit=True, zso=True, oj='xyz')
		self.HeadTipJoint = mc.joint(name='F_HeadTip_Jt', position=(-0.015, 8.031, 0))
		mc.select('A_Hip_Jt')
		mc.joint(name='A_LowerHip_Jt', position=(-0.023, 4.327, 0))
		#Move the first created back joint a little upward
		mc.select("Hip_Jt_0")
		mc.move(-0.008,4.701,0)
		#0.008, 4.451, 0
		mc.select('A_Hip_Jt')

	def __CreateSkeletonLeg__(self):
		self.L_HipJoint =  mc.joint(name='L_Hip_Jt', position=(-0.12, 4.369, -0.689))
		mc.select('L_Hip_Jt')
		self.L_KneeJoint = mc.joint(name='L_Knee_Jt', position=(0.2, 2.36, -0.689))
		mc.select('L_Knee_Jt')
		mc.joint('L_Hip_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_AnkleJoint = mc.joint(name='L_Ankle_Jt', position=(-0.24, 0.486, -0.689))
		mc.joint('L_Knee_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		mc.joint('L_Ankle_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_ToeJoint = mc.joint(name='L_Toe_Jt', position=(0.32, 0.051, -0.689))
		self.L_ToeEndJoint = mc.joint(name='L_ToeEnd_Jt', position=(0.69, 0.062, -0.689))
		mc.joint('L_Toe_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		
	def __CreateSkeletonArm__(self):
		mc.select('D_Neck_Jt')
		self.L_CollarBoneJoint = mc.joint(name='L_Collarbone_Jt', position=(-0.233, 6.565, -0.793))
		self.L_ShoulderJoint = mc.joint(name='L_Shoulder_Jt', position=(0, 6.749, -1.31))
		mc.joint('L_Collarbone_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_ElbowJoint = mc.joint(name='L_Elbow_Jt', position=(0, 5.773, -2.092))
		mc.joint('L_Shoulder_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_WristJoint = mc.joint(name='L_Wrist_Jt', position=(0.503, 5.126, -2.82))
		mc.joint('L_Elbow_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_MiddleHandJoint = mc.joint(name='L_MiddleHand_Jt', position=(0.641, 4.961, -2.963))
		mc.joint('L_Wrist_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		mc.select('L_Wrist_Jt');

	def __CreateSkeletonFingers__(self):
		# Thumb
		self.L_Thumb01Joint = mc.joint(name='L_Thumb01_Jt', position=(0.782, 4.973, -2.855))
		self.L_Thumb02Joint = mc.joint(name='L_Thumb02_Jt', position=(0.895, 4.867, -2.855))
		mc.joint('L_Thumb01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_Thumb03Joint = mc.joint(name='L_Thumb03_Jt', position=(0.938, 4.79, -2.855))
		mc.joint('L_Thumb02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Index
		mc.select('L_Wrist_Jt')
		self.L_IndexFinger01Joint = mc.joint(name='L_IndexFinger01_Jt', position=(0.749, 4.841, -3.093))
		self.L_IndexFinger02Joint = mc.joint(name='L_IndexFinger02_Jt', position=(0.816, 4.697, -3.159))
		mc.joint('L_IndexFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_IndexFinger03Joint = mc.joint(name='L_IndexFinger03_Jt', position=(0.849, 4.568, -3.19))
		mc.joint('L_IndexFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_IndexFinger04Joint = mc.joint(name='l_indexFinger04_Jt', position=(0.861, 4.484, -3.198))
		mc.joint('L_IndexFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Middle
		mc.select('L_Wrist_Jt')
		self.L_MiddleFinger01Joint = mc.joint(name='L_MiddleFinger01_Jt', position=(0.637, 4.833, -3.183))
		self.L_MiddleFinger02Joint = mc.joint(name='L_MiddleFinger02_Jt', position=(0.682, 4.703, -3.276))
		mc.joint('L_MiddleFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_MiddleFinger03Joint = mc.joint(name='L_MiddleFinger03_Jt', position=(0.702, 4.554, -3.322))
		mc.joint('L_MiddleFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_MiddleFinger04Joint = mc.joint(name='L_MiddleFinger04_Jt', position=(0.711, 4.441, -3.334))
		mc.joint('L_MiddleFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Ring
		mc.select('L_Wrist_Jt')
		self.L_RingFinger01Joint = mc.joint(name='L_RingFinger01_Jt', position=(0.488, 4.827, -3.25))
		self.L_RingFinger02Joint =mc.joint(name='L_RingFinger02_Jt', position=(0.528, 4.713, -3.31))
		mc.joint('L_RingFinger01_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_RingFinger03Joint =mc.joint(name='L_RingFinger03_Jt', position=(0.541, 4.584, -3.354 ))
		mc.joint('L_RingFinger02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_RingFinger04Joint = mc.joint(name='L_RingFinger04_Jt', position=(0.546, 4.49, -3.361))
		mc.joint('L_RingFinger03_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		# Pinky
		mc.select('L_Wrist_Jt')
		self.L_Pinky01Joint = mc.joint(name='L_Pinky01_tJt', position=(0.362, 4.818, -3.251))
		self.L_Pinky02Joint = mc.joint(name='L_Pinky02_Jt', position=(0.375, 4.73, -3.283))
		mc.joint('L_Pinky01_tJt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_Pinky03Joint = mc.joint(name='L_Pinky03_Jt', position=(0.38, 4.617, -3.329))
		mc.joint('L_Pinky02_Jt', edit=True, zso=True, oj='xyz', sao='yup')
		self.L_Pinky04Joint = mc.joint(name='L_Pinky04_Jt', position=(0.385, 4.534, -3.341))
		mc.joint('L_Pinky03_Jt', edit=True, zso=True, oj='xyz', sao='yup')

	def __CreateFingerCtrl_(**kwargs):
		joints = kwargs.setdefault("joints")
		for jt in joints:
			mc.select(jt, hierarchy=True)
			jointList = mc.ls(selection=True)
			for joint in jointList[:-2]:
				pos = mc.joint(joint, q=True, position=True)
				nameSplit = joint.rsplit('_', 1)
				name = nameSplit[0]
				mc.select(joint)
				mc.joint(name=name+'Up_Jt', position=(pos[0]+0.01, pos[1]+0.05, pos[2]-0.06))

	def __MirrorJointsHands__(self, **kwargs):
		mc.select('D_Neck_Jt');
		self.MirrorEachJoint = mc.mirrorJoint('L_Collarbone_Jt',mirrorXY=True,mirrorBehavior=True,searchReplace=('L_','R_'))
		#mc.mirrorJoint('L_Collarbone_Jt',mirrorBehavior=True,myz=True)

	def __MirrorJointsLegs__(self, **kwargs):
		mc.select('A_LowerHip_Jt')
		self.MirrorEachJoint = mc.mirrorJoint('L_Hip_Jt',mirrorXY=True,mirrorBehavior=True,searchReplace=('L_', 'R_'))	
		#mc.mirrorJoint('L_Collarbone_Jt',mirrorBehavior=True,myz=True)
		slBone = mc.select('A_Hip_Jt')
		
	def __create__(self, **kwargs):
		skeletonJT = SkeletonB()
		skeletonJT.__CreateSpineSkeleton__()
		skeletonJT.__CreateSkeletonLeg__()
		skeletonJT.__CreateSkeletonArm__()
		skeletonJT.__CreateSkeletonFingers__()
		skeletonJT.__MirrorJointsHands__()
		skeletonJT.__MirrorJointsLegs__()
