# -*- coding: utf-8 -*-

MadeBy = "Nag"
ScriptName = "Auto Eyelids Rig"
Version = "1.0"
WIN_NAME = "WIN_AUTO_EYELIDS_RIG"

from maya import cmds, OpenMaya
import math


class AER:
	"""
	まぶたの自動リグ（注：ボール入力の目のみ有効）
	"""
	def __init__(self):
		self.parent_joint = None
		self.parent_control = None
		self.eye_locator = None
		self.eye_name = None
		self.upper_lid_vertex = None
		self.lower_lid_vertex = None

	## PREREQUISITE FOR RIG ##	
	def eye_parent_joint(self, *args):
		"""
		Organise rig hierarchy - Define a parent joint for the eyelid rig.
		Called by 'UI' function.
		Call functions: None
		"""
		parentJointSel = cmds.ls(sl=1, typ="joint")
		if len(parentJointSel) != 0:
			self.parent_joint = parentJointSel[0]
			cmds.textField(self.txtfJnt, e=1, tx=self.parent_joint)
		else:
			self.parent_joint = None
			cmds.textField(self.txtfJnt, e=1, tx="")
			cmds.error("選択ミスです。ジョイントを選択してください。")

	def eye_parent_control(self, *args):
		"""
		Organise rig hierarchy - Define a parent controller for the eyelid rig.
		Called by 'UI' function.
		Call functions: None
		"""
		# selectionMask Nurbs カーブ
		parentCtrlSel = cmds.filterExpand(sm=9)
		if parentCtrlSel is None:
			parentCtrlShape = parentCtrlSel[0]
			self.parent_control = cmds.listRelatives((parentCtrlSel[0]), parent=1)[0]
			print(self.parent_control)
			cmds.textField(self.txtfCtrl, e=1, tx=self.parent_control)
		else:
			self.parent_control = None
			cmds.textField(self.txtfCtrl, e=1, tx="")
			cmds.error("Curve Controllerを選択してください。")

	def place_eye_center(self, *args):
		"""
		Place locator in the center of the eyeball.
		Called by 'UI' function.
		Call functions: None
		"""
		selection = cmds.filterExpand(sm=12)
		self.eye_name = cmds.textField(self.txtfEye, q=1, tx=1)
		
		if selection is None:
			self.eye_locator = None
			self.eye_name = None
			cmds.error("Please select the eyeball.")
		else:
			eyeball = selection[0]
			if not self.eye_name:
				self.eye_name = name = "DefaultEye"
			else:
				name = self.eye_name
			
			eyeTemp = cmds.duplicate(eyeball)[0]
			cmds.xform(eyeTemp, cp=1)
			self.eye_locator = cmds.spaceLocator(n=(name + "_eyeCenter_locator"))[0]
			cnstrTemp = cmds.pointConstraint(eyeTemp, self.eye_locator)
			cmds.delete(cnstrTemp)
			cmds.delete(eyeTemp)
			# lock locator
			cmds.setAttr(self.eye_locator + ".overrideEnabled", 1)
			cmds.setAttr(self.eye_locator + ".overrideDisplayType", 2)
			cmds.select(cl=1)
			# Update UI
			cmds.textField(self.txtfLoc, e=1, tx=self.eye_locator)
			cmds.button(self.btnPlaceCenter, e=1, en=0)
			cmds.button(self.btnUndoPlaceCenter, e=1, en=1)

	def place_eye_center_undo(self, *args):
		"""
		Undo 'placeEyeCenter' function.
		Called by 'UI' function.
		Call functions: None
		"""
		try:
			cmds.delete(self.eye_locator)
		except ValueError:
			cmds.warning("'" + self.eye_locator + "'" + " doesn't exists.\n")
		finally:
			self.eye_locator = None
			self.eye_name = None
			cmds.textField(self.txtfLoc, e=1, tx="")
			cmds.button(self.btnPlaceCenter, e=1, en=1)
			cmds.button(self.btnUndoPlaceCenter, e=1, en=0)

	def up_eyelid_vertex_set(self, *args):
		"""
		List selected vertices as upper lid vertices.
		Called by 'UI' function.
		Call functions: None
		"""
		self.upper_lid_vertex = cmds.filterExpand(sm=31)
		if self.upper_lid_vertex is None:
			cmds.scrollField(self.scrollfUpLid, e=1, cl=1)
			cmds.error("Please select vertices of the upper eye lid.\n")
		else:
			cmds.scrollField(self.scrollfUpLid, e=1, cl=1)
			for vtx in self.upper_lid_vertex:
				vtxNum = vtx.rpartition(".")[2]
				cmds.scrollField(self.scrollfUpLid, e=1, it=(str(vtxNum) + " "))

	def low_eyelid_vertex_set(self, *args):
		"""
		List selected vertices as lower lid vertices.
		Called by 'UI' function.
		Call functions: None
		"""
		self.lower_lid_vertex = cmds.filterExpand(sm=31)
		
		if self.lower_lid_vertex is None:
			cmds.scrollField(self.scrollfLowLid, e=1, cl=1)
			cmds.error("Please select vertices of the lower lid.\n")
		else:
			cmds.scrollField(self.scrollfLowLid, e=1, cl=1)
			for vtx in self.lower_lid_vertex:
				vtxNum = vtx.rpartition(".")[2]
				cmds.scrollField(self.scrollfLowLid, e=1, it=(str(vtxNum) + " "))
	## PREREQUISITE FOR RIG -end ##

	## FUNCTIONS TO BUILD RIG ##
	def vertex_to_joint(self, eyeCenter, eyePrefix, upperLidVtx, lowerLidVtx, parentJnt):
		"""
		Creates one joint per vertex of the eyelid and parent it to the center of the eye.
		Called by 'buildRig' function.
		Call functions: None
		"""
		cmds.select(cl=1)
		self.upLidJntList = []
		self.lowLidJntList = []
		
		# 両方のリストで共通する頂点を見つけ、二重のジョイント生成を避けるためにそれらを削除します。
		commonVtx = set(upperLidVtx) & set(lowerLidVtx)
		for vtx in commonVtx:
			lowerLidVtx.remove(vtx)
		
		# Organize rig hierarchy
		hierarchySecondGrp = cmds.group(n=(eyePrefix + "_Eyelids_JNT_GRP"), em = 1)
		hierarchyUpGrp = cmds.group(n=(eyePrefix + "_UpEyelid_joints_GRP"), em = 1)
		hierarchyLowGrp = cmds.group(n=(eyePrefix + "_LowEyelid_joints_GRP"), em = 1)
		
		cmds.parent(hierarchyUpGrp, hierarchySecondGrp)
		cmds.parent(hierarchyLowGrp, hierarchySecondGrp)
		hierarchyMainGrp = "Eyelids_JNT_GRP"
		
		if parentJnt is not None:
			jntChildren = cmds.listRelatives(parentJnt, children=1)
			if hierarchyMainGrp in jntChildren:
				cmds.parent(hierarchySecondGrp, (parentJnt + "|" + hierarchyMainGrp))
			else:
				cmds.group(n=hierarchyMainGrp, em=1, p=parentJnt)
				cmds.parent(hierarchySecondGrp, (parentJnt + "|" + hierarchyMainGrp))
		else:
			if cmds.objExists("|" + hierarchyMainGrp):
				cmds.parent(hierarchySecondGrp, ("|" + hierarchyMainGrp))
			else:
				cmds.group(n=hierarchyMainGrp, em=1)
				cmds.parent(hierarchySecondGrp, ("|" + hierarchyMainGrp))
		
		# Upper eyelid
		x = 1
		for upVtx in upperLidVtx:
			cmds.select(cl=1)
			jnt = cmds.joint(rad=0.01, n=(eyePrefix + "_UpEyelid_JNT%d_SKIN" % x))
			self.upLidJntList.append(jnt)
			position = cmds.xform(upVtx, q=1, ws=1, t=1)
			cmds.xform(jnt, ws=1, t=position)
			centerPosition = cmds.xform(eyeCenter, q=1, ws=1, t=1)
			cmds.select(cl=1)
			centerJnt = cmds.joint(rad=0.01, n=(eyePrefix + "_UpEyelid_JNT%d_BASE" % x))
			cmds.xform(centerJnt, ws=1, t=centerPosition)
			cmds.parent(jnt, centerJnt)
			cmds.joint(centerJnt, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
			cmds.parent(centerJnt, hierarchyUpGrp)
			x += 1
		
		# Lower eyelid
		y = 1
		for lowVtx in lowerLidVtx:
			cmds.select(cl=1)
			jnt = cmds.joint(rad=0.01, n=(eyePrefix + "_LowEyelid_JNT%d_SKIN" % y))
			self.lowLidJntList.append(jnt)
			position = cmds.xform(lowVtx, q=1, ws=1, t=1)
			cmds.xform(jnt, ws=1, t=position)
			centerPosition = cmds.xform(eyeCenter, q=1, ws=1, t=1)
			cmds.select(cl=1)
			centerJnt = cmds.joint(rad=0.01, n=(eyePrefix + "_LowEyelid_JNT%d_BASE" % y))
			cmds.xform(centerJnt, ws=1, t=centerPosition)
			cmds.parent(jnt, centerJnt)
			cmds.joint(centerJnt, e=1, oj="xyz", secondaryAxisOrient="yup", ch=1, zso=1)
			cmds.parent(centerJnt, hierarchyLowGrp)
			y += 1
		
		# Creates a set containing the joints for skinning
		jntsForSkin = []
		jntsForSkin.extend(self.upLidJntList)
		jntsForSkin.extend(self.lowLidJntList)
		setSkinJnts = cmds.sets(em=1, n=(eyePrefix + "_jointsForSkin"))
		for jnt in jntsForSkin:
			cmds.sets(jnt, e=1, forceElement=setSkinJnts)

	def place_rig_locator(self, eyePrefix, upLidJntList, lowLidJntList):
		"""
		Creates one locator per eyelid vertex and constrain each joint to it (aim).
		Called by 'buildRig' function.
		Call functions: None
		"""
		self.upLidLocList = []
		self.lowLidLocList = []
		# Organize rig hierarchy
		hierarchyThirdGrp = cmds.group(n=(eyePrefix + "_Eyelids_locator_GRP"), em=1)
		hierarchyUpGrp = cmds.group(n=(eyePrefix + "_UpEyelid_locator_GRP"), em=1)
		hierarchyLowGrp = cmds.group(n=(eyePrefix + "_LowEyelid_locator_GRP"), em=1)
		cmds.parent(hierarchyUpGrp, hierarchyThirdGrp)
		cmds.parent(hierarchyLowGrp, hierarchyThirdGrp)
		
		self.grpTheseEyelidsRig = (eyePrefix + "_Eyelids_RIG_GRP")
		if cmds.objExists(eyePrefix + "_Eyelids_RIG_GRP"):
			cmds.parent(hierarchyThirdGrp, self.grpTheseEyelidsRig)
		else:
			self.grpTheseEyelidsRig = cmds.group(n=(eyePrefix + "_Eyelids_RIG_GRP"), em=1)
			cmds.parent(hierarchyThirdGrp, self.grpTheseEyelidsRig)

		grpAllEyelidsRig = "Eyelids_RIG_GRP"
		if cmds.objExists("Eyelids_RIG_GRP"):
			cmds.parent(self.grpTheseEyelidsRig, grpAllEyelidsRig)
		else:
			grpAllEyelidsRig = cmds.group(n="Eyelids_RIG_GRP", em=1)
			cmds.parent(self.grpTheseEyelidsRig, grpAllEyelidsRig)
		cmds.setAttr(grpAllEyelidsRig + ".visibility", 0)
		
		# Upper eyelid
		for upLidJnt in upLidJntList:
			locName = upLidJnt.replace("_SKIN", "_locator")
			loc = cmds.spaceLocator(n=locName)[0]
			self.upLidLocList.append(loc)
			cmds.setAttr(loc + "Shape.localScaleX", 0.025)
			cmds.setAttr(loc + "Shape.localScaleY", 0.025)
			cmds.setAttr(loc + "Shape.localScaleZ", 0.025)
			positionLoc = cmds.xform(upLidJnt, q=1, ws=1, t=1)
			cmds.xform(loc, ws=1, t=positionLoc)
			parentJnt = cmds.listRelatives(upLidJnt, p=1)[0]
			cmds.aimConstraint(loc, parentJnt, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0))
			cmds.parent(loc, hierarchyUpGrp)
		
		# Lower eyelid
		for lowLidJnt in lowLidJntList:
			locName = lowLidJnt.replace("_SKIN", "_locator")
			loc = cmds.spaceLocator(n=locName)[0]
			self.lowLidLocList.append(loc)
			cmds.setAttr(loc + "Shape.localScaleX", 0.025)
			cmds.setAttr(loc + "Shape.localScaleY", 0.025)
			cmds.setAttr(loc + "Shape.localScaleZ", 0.025)
			positionLoc = cmds.xform(lowLidJnt, q=1, ws=1, t=1)
			cmds.xform(loc, ws=1, t=positionLoc)
			parentJnt = cmds.listRelatives(lowLidJnt, p=1)[0]
			cmds.aimConstraint(loc, parentJnt, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0))
			cmds.parent(loc, hierarchyLowGrp)
	
	def create_eyelids_curve(self, eyePrefix, upperLidVtx, lowerLidVtx, rigGrp):
		"""
		Creates nurbsCurve out of each lid vertices.
		Called by 'buildRig' function.
		Call functions: None
		"""
		cmds.select(cl=1)
		# Organize rig hierarchy
		self.hierarchyCrvGrp = cmds.group(n=(eyePrefix + "_Eyelids_curves_GRP"), em=1)
		self.hierarchyUpCrvGrp = cmds.group(n=(eyePrefix + "_UpEyelid_curves_GRP"), em=1)
		self.hierarchyLowCrvGrp = cmds.group(n=(eyePrefix + "_LowEyelid_curves_GRP"), em=1)
		
		cmds.parent(self.hierarchyUpCrvGrp, self.hierarchyCrvGrp)
		cmds.parent(self.hierarchyLowCrvGrp, self.hierarchyCrvGrp)
		cmds.parent(self.hierarchyCrvGrp, rigGrp)
		
		# Upper eyelid
		cmds.select(upperLidVtx)
		edgeUpLid = cmds.polyListComponentConversion(fv=1, te=1, internal=1)
		cmds.select(edgeUpLid)
		tempCrvUp = cmds.polyToCurve(form=0, degree=1)[0]
		cmds.select(tempCrvUp)
		cmds.delete(ch=1)
		upLidCrvName = eyePrefix + "_UpEyelid_BASE_curve"
		self.upLidCrv = cmds.rename(tempCrvUp, upLidCrvName)
		cmds.parent(self.upLidCrv, self.hierarchyUpCrvGrp)
		
		# Lower eyelid
		cmds.select(lowerLidVtx)
		edgeLowLid = cmds.polyListComponentConversion(fv=1, te=1, internal=1)
		cmds.select(edgeLowLid)
		tempCrvLow = cmds.polyToCurve(form=0, degree=1)[0]
		cmds.select(tempCrvLow)
		cmds.delete(ch=1)
		lowLidCrvName = eyePrefix + "_LowEyelid_BASE_curve"
		self.lowLidCrv = cmds.rename(tempCrvLow, lowLidCrvName)
		cmds.parent(self.lowLidCrv, self.hierarchyLowCrvGrp)

	def get_dag_path(self, objectName):
		"""
		Called by 'getUParam' function.
		Call functions: None
		"""
		if isinstance(objectName, list) is True:
			oNodeList = []
			for o in objectName:
				selectionList = OpenMaya.MSelectionList()
				selectionList.add(o)
				oNode = OpenMaya.MDagPath()
				selectionList.getDagPath(0, oNode)
				oNodeList.append(oNode)
			return oNodeList
		else:
			selectionList = OpenMaya.MSelectionList()
			selectionList.add(objectName)
			oNode = OpenMaya.MDagPath()
			selectionList.getDagPath(0, oNode)
			return oNode

	def get_u_param(self, pnt=[], crv=None, *args):
		"""
		Called by 'connectLocToCrv' function.
		Call functions: 'getDagPath'
		"""
		point = OpenMaya.MPoint(pnt[0], pnt[1], pnt[2])
		curveFn = OpenMaya.MFnNurbsCurve(self.get_dag_path(crv))
		paramUtill = OpenMaya.MScriptUtil()
		paramPtr = paramUtill.asDoublePtr()
		isOnCurve = curveFn.isPointOnCurve(point)
		if isOnCurve is True:
			curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
		else:
			point = curveFn.closestPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
			curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
		param = paramUtill.getDouble(paramPtr)  
		return param

	def connect_locator_to_curve(self, upLidLocList, upLidCrv, lowLidLocList, lowLidCrv):
		"""
		Connect locators to lid curves via pointOnCurveInfo nodes.
		Called by 'buildRig' function.
		Call functions: None
		"""
		
		# Upper eyelid
		for upLidLoc in upLidLocList:
			position = cmds.xform(upLidLoc, q=1, ws=1, t=1)
			u = self.get_u_param(position, upLidCrv)
			name = upLidLoc.replace("_locator", "_pointOnCurveInfo")
			ptOnCrvInfo = cmds.createNode("pointOnCurveInfo", n=name)
			cmds.connectAttr(upLidCrv + ".worldSpace", ptOnCrvInfo + ".inputCurve")
			cmds.setAttr(ptOnCrvInfo + ".parameter", u)
			cmds.connectAttr(ptOnCrvInfo + ".position", upLidLoc + ".t")
		
		# Lower eyelid
		for lowLidLoc in lowLidLocList:
			position = cmds.xform(lowLidLoc, q=1, ws=1, t=1)
			u = self.get_u_param(position, lowLidCrv)
			name = lowLidLoc.replace("_locator", "_pointOnCurveInfo")
			ptOnCrvInfo = cmds.createNode("pointOnCurveInfo", n=name)
			cmds.connectAttr(lowLidCrv + ".worldSpace", ptOnCrvInfo + ".inputCurve")
			cmds.setAttr(ptOnCrvInfo + ".parameter", u)
			cmds.connectAttr(ptOnCrvInfo + ".position", lowLidLoc + ".t")

	def eyelids_corners(self, upLidEpCrvPos, upLidCrv, lowLidEpCrvPos, lowLidCrv):
		"""
		Define eye corners position (for example if upper lid and lower lid curves are not 'closed').
		Called by 'createDriverCrv' function.
		Call functions: None
		"""
		cornerUp1 = upLidEpCrvPos[0]
		cornerUp2 = upLidEpCrvPos[4]
		cornerLow1 = lowLidEpCrvPos[0]
		cornerLow2 = lowLidEpCrvPos[4]
		
		# distance formula is: d = sqrt((Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2)
		distTEMP1 = math.sqrt((cornerUp1[0] - cornerLow1[0])**2 + (cornerUp1[1] - cornerLow1[1])**2 + (cornerUp1[2] - cornerLow1[2])**2)
		distTEMP2 = math.sqrt((cornerUp1[0] - cornerLow2[0])**2 + (cornerUp1[1] - cornerLow2[1])**2 + (cornerUp1[2] - cornerLow2[2])**2)

		# cornerUp1 が cornerLow2 に cornerLow1 よりも近い場合。
		# cornerUp1 と cornerLow2 の間の距離の中心が、"CornerA" と "CornerB" になります。
		# コーナーA, コーナーB となります.
		# 他の2点によって定義されます.
		if distTEMP1 > distTEMP2:
			# CornerA
			cmds.select(cl=1)
			cmds.select(upLidCrv + ".ep[0]")
			cmds.select(lowLidCrv + ".ep[4]", tgl=1)
			clusterTEMP1 = cmds.cluster(en=1)[1]
			locTEMP1 = cmds.spaceLocator()[0]
			cmds.pointConstraint(clusterTEMP1, locTEMP1, mo=0, w=1)
			self.cornerAPos = cmds.xform(locTEMP1, q=1, ws=1, t=1)
			cmds.delete(clusterTEMP1)
			cmds.delete(locTEMP1)
			# CornerB
			cmds.select(cl=1)
			cmds.select(upLidCrv + ".ep[4]")
			cmds.select(lowLidCrv + ".ep[0]", tgl=1)
			clusterTEMP2 = cmds.cluster(en=1)[1]
			locTEMP2 = cmds.spaceLocator()[0]
			cmds.pointConstraint(clusterTEMP2, locTEMP2, mo=0, w=1)
			self.cornerBPos = cmds.xform(locTEMP2, q=1, ws=1, t=1)
			cmds.delete(clusterTEMP2)
			cmds.delete(locTEMP2)
		else:
			# CornerA
			cmds.select(cl=1)
			cmds.select(upLidCrv + ".ep[0]")
			cmds.select(lowLidCrv + ".ep[0]", tgl=1)
			clusterTEMP1 = cmds.cluster(en=1)[1]
			locTEMP1 = cmds.spaceLocator()[0]
			cmds.pointConstraint(clusterTEMP1, locTEMP1, mo=0, w=1)
			self.cornerAPos = cmds.xform(locTEMP1, q=1, ws=1, t=1)
			cmds.delete(clusterTEMP1)
			cmds.delete(locTEMP1)
			# CornerB
			cmds.select(cl=1)
			cmds.select(upLidCrv + ".ep[4]")
			cmds.select(lowLidCrv + ".ep[4]", tgl=1)
			clusterTEMP2 = cmds.cluster(en=1)[1]
			locTEMP2 = cmds.spaceLocator()[0]
			cmds.pointConstraint(clusterTEMP2, locTEMP2, mo=0, w=1)
			self.cornerBPos = cmds.xform(locTEMP2, q=1, ws=1, t=1)
			cmds.delete(clusterTEMP2)
			cmds.delete(locTEMP2)
		return self.cornerAPos, self.cornerBPos

	def eyelids_left_and_right(self):
		print("eyelids_left_and_right")
		"""
		With the position of each eye corner and the upper and lower lids, find out where is the left and the right of the eye.
		Called by 'createDriverCrv' function.
		Call functions: [...]
		"""
		pass

	def eyelids_curve_CVS(self, upLidCrv, lowLidCrv):
		"""
		List CVs of each guide curve.
		Called by 'createDriverCrv' function.
		Call functions: None
		"""
		upLidCVs = []
		x = 0
		while x < 7:
			posCv = cmds.xform((upLidCrv + ".cv[%d]" % x), q=1, ws=1, t=1)
			upLidCVs.append(posCv)
			x += 1
		
		lowLidCVs = []
		y = 0
		while y < 7:
			posCv = cmds.xform((lowLidCrv + ".cv[%d]" % y), q=1, ws=1, t=1)
			lowLidCVs.append(posCv)
			y += 1
		return upLidCVs, lowLidCVs
	
	def eyelids_match_topology(self, cornerAPos, cornerBPos, upLidCVsPos, lowLidCVsPos):
		"""
		Reorganise the CVs of each curve so they have the same topology.
		Called by 'createDriverCrv' function.
		Call functions: None
		"""
		# Order of CVs in base lists:			Order of CVs in ordered lists:
		# (upLidCVsPos, lowLidCVsPos)			(upLidCVsOrdered, lowLidCVsOrdered)
		# -----------------------				-------------------------
		# INDEX | 		CV		|				| INDEX | 		CV		|
		# ------|---------------|				|-------|---------------|
		# 	0	| corner: ?		|				|	0	| corner A		|
		# 	1	| 				|				|	1	| 				|
		# 	2	| 				|				|	2	| 				|
		# 	3	| middle of crv |				|	3	| middle of crv	|
		# 	4	| 				|				|	4	| 				|
		# 	5	| 				|				|	5	| 				|
		# 	6	| other corner  |				|	6	| corner B		|
		# -----------------------				-------------------------
		# - baseList の first_CV と cornerAPos の間の距離を計測します．
		# - baseList の first_CV と cornerBPos との距離を計測します．
		# - CV が cornerA に近い場合， baseList を orderedList の先頭から末尾に追加します．
		# - else (CV が cornerB に近い場合) append baseList to orderedList from end to beginning (ベースリストをorderedListの最後に追加する)
		# return orderedLists
		# distance formula is: d = sqrt((Ax-Bx)**2 + (Ay-By)**2 + (Az-Bz)**2)
		distTEMP1 = math.sqrt((((upLidCVsPos[0])[0]) - cornerAPos[0])**2 + (((upLidCVsPos[0])[1]) - cornerAPos[1])**2 + (((upLidCVsPos [0])[2]) - cornerAPos[2])**2)
		distTEMP2 = math.sqrt((((upLidCVsPos[0])[0]) - cornerBPos[0])**2 + (((upLidCVsPos[0])[1]) - cornerBPos[1])**2 + (((upLidCVsPos [0])[2]) - cornerBPos[2])**2)
		if distTEMP1 < distTEMP2:
			upLidCVsOrdered = upLidCVsPos
		else:
			# reversed 'upLidCVsPos'
			upLidCVsOrdered = upLidCVsPos[::-1]
		
		distTEMP3 = math.sqrt((((lowLidCVsPos[0])[0]) - cornerAPos[0])**2 + (((lowLidCVsPos[0])[1]) - cornerAPos[1])**2 + (((lowLidCVsPos[0])[2]) - cornerAPos[2])**2)
		distTEMP4 = math.sqrt((((lowLidCVsPos[0])[0]) - cornerBPos[0])**2 + (((lowLidCVsPos[0])[1]) - cornerBPos[1])**2 + (((lowLidCVsPos[0])[2]) - cornerBPos[2])**2)
		if distTEMP3 < distTEMP4:
			lowLidCVsOrdered = lowLidCVsPos
		else:
			# reversed 'lowLidCVsPos'
			lowLidCVsOrdered = lowLidCVsPos[::-1]
		return upLidCVsOrdered, lowLidCVsOrdered

	def create_driver_curve(self, upLidBaseCrv, upRigGrp, lowLidBaseCrv, lowRigGrp):
		"""
		Create a driver curve for each lid curve and connect it to the base curve with a wire deformer.
		Called by 'buildRig' function.
		Call functions: 'eyelidsCorners', 'eyeLidsLeftAndRight' (unused), 'eyelidsCrvCVs', 'eyelidsMatchTopology'
		"""
		
		## Upper eyelid ##
		upLidDriverCrvTEMP = cmds.duplicate(upLidBaseCrv)[0]
		# delete history
		cmds.delete(upLidDriverCrvTEMP, ch=1)
		cmds.rebuildCurve(upLidDriverCrvTEMP, rpo=1, end=1, kr=2, kcp=0, kep=1, kt=0, s=4, d=7, tol=0.01)

		# 上まぶたのドライバーカーブのEPの位置をリストアップする
		upLidEpPosTEMP = []
		x = 0
		while x < 5:
			posEp = cmds.xform((upLidDriverCrvTEMP + ".ep[%d]" % x), q=1, ws=1, t=1)
			upLidEpPosTEMP.append(posEp)
			x += 1
		cmds.delete(upLidDriverCrvTEMP)

		# コーナー配置のためのアップリッド「ガイド」カーブを作成し、CVsの位置とインデックスを問い合わせる。
		upLidGuideCrv = cmds.curve(d=3, ep=(upLidEpPosTEMP[0], upLidEpPosTEMP[1], upLidEpPosTEMP[2], upLidEpPosTEMP[3], upLidEpPosTEMP[4]))
		
		## Lower eyelid ##
		lowLidDriverCrvTEMP = cmds.duplicate(lowLidBaseCrv)[0]
		# delete history
		cmds.delete(lowLidDriverCrvTEMP, ch=1)
		cmds.rebuildCurve(lowLidDriverCrvTEMP, rpo=1, end=1, kr=2, kcp=0, kep=1, kt=0, s=4, d=7, tol=0.01)

		# 下まぶたのドライバーカーブのEPの位置をリストアップする
		lowLidEpPosTEMP = []
		x = 0
		while x < 5:
			posEp = cmds.xform((lowLidDriverCrvTEMP + ".ep[%d]" % x), q=1, ws=1, t=1)
			lowLidEpPosTEMP.append(posEp)
			x += 1
		cmds.delete(lowLidDriverCrvTEMP)

		# コーナー配置のためのlowLidの「ガイド」カーブを作成し、CVsの位置とインデックスを問い合わせる。
		lowLidGuideCrv = cmds.curve(d=3, ep=(lowLidEpPosTEMP[0], lowLidEpPosTEMP[1], lowLidEpPosTEMP[2], lowLidEpPosTEMP[3], lowLidEpPosTEMP[4]))

		# Find position of eye corners
		self.cornerAPos, self.cornerBPos = self.eyelids_corners(upLidEpPosTEMP, upLidGuideCrv, lowLidEpPosTEMP, lowLidGuideCrv)

		# "CornerA" と "CornerB" は "leftCorner" と "rightCorner" として定義される。
		# ADD FUNC WHEN OK - self.eyeLidsLeftAndRight (self.cornerAPos, self.cornerBPos)
		# List CVs positions of upLidGuideCrv and lowLidGuideCrv
		upLidCVsPos, lowLidCVsPos = self.eyelids_curve_CVS(upLidGuideCrv, lowLidGuideCrv)
		
		# List CVs positions in the right order (to match topology)
		upLidCVsOrdered, lowLidCVsOrdered = self.eyelids_match_topology(self.cornerAPos, self.cornerBPos, upLidCVsPos, lowLidCVsPos)

		# Create upper driver curve
		self.upLidDriverCrv = cmds.curve(d=3, p=(upLidCVsOrdered[0], upLidCVsOrdered[1], upLidCVsOrdered[2], upLidCVsOrdered[3], upLidCVsOrdered[4], upLidCVsOrdered[5], upLidCVsOrdered[6]))
		upLidDriverCrvName = upLidBaseCrv.replace("_BASE_", "_DRIVER_")
		self.upLidDriverCrv = cmds.rename(self.upLidDriverCrv, upLidDriverCrvName)
		cmds.parent(self.upLidDriverCrv, upRigGrp)
		cmds.delete(upLidGuideCrv)
		
		# Create lower driver curve
		lowCrvTEMP = cmds.curve(d=3, p=(lowLidCVsOrdered[0], lowLidCVsOrdered[1], lowLidCVsOrdered[2], lowLidCVsOrdered[3], lowLidCVsOrdered[4], lowLidCVsOrdered[5], lowLidCVsOrdered[6]))
		lowLidDriverCrvName = lowLidBaseCrv.replace("_BASE_", "_DRIVER_")
		self.lowLidDriverCrv = cmds.rename(lowCrvTEMP, lowLidDriverCrvName)
		cmds.parent(self.lowLidDriverCrv, lowRigGrp)
		cmds.delete(lowLidGuideCrv)
		
		cmds.select(cl=1)
		wireNodeUpLidName = upLidBaseCrv.replace("_BASE_curve", "_controlCurve_wire")
		wireUpLid = cmds.wire(upLidBaseCrv, n=wireNodeUpLidName, w=self.upLidDriverCrv, gw=0, en=1, ce=0, li=0)
		
		cmds.select(cl=1)
		wireNodeLowLidName = lowLidBaseCrv.replace("_BASE_curve", "_controlCurve_wire")
		wireUpLid = cmds.wire(lowLidBaseCrv, n=wireNodeLowLidName, w=self.lowLidDriverCrv, gw=0, en=1, ce=0, li=0)

	def create_joint_controls(self, eyePrefix, cornerAPos, cornerBPos, upLidDriverCrv, lowLidDriverCrv, rigGrp):
		# MODIFIER
		"""
		Creates controller joints for each point of the eyelids driver curves.
		Called by 'buildRig' function.
		Call functions: None
		"""
		
		# Find position of EPs of each driver curve for joint placement
		upLidEpDriverCrvPos = []
		x = 0
		while x < 5:
			posEp = cmds.xform((upLidDriverCrv + ".ep[%d]" % x), q=1, ws=1, t=1)
			upLidEpDriverCrvPos.append(posEp)
			x += 1
		
		lowLidEpDriverCrvPos = []
		y = 0
		while y < 5:
			posEp = cmds.xform((lowLidDriverCrv + ".ep[%d]" % y), q=1, ws=1, t=1)
			lowLidEpDriverCrvPos.append (posEp)
			y += 1
		
		# Place controller joints
		ctrlJnt_CornerA = cmds.joint(rad=0.05, p=self.cornerAPos, n=(eyePrefix + "_cornerA_CTRL_JNT"))
		ctrlJnt_CornerB = cmds.joint(rad=0.05, p=self.cornerBPos, n=(eyePrefix + "_cornerB_CTRL_JNT"))
		ctrlJnt_upLidMain = cmds.joint(rad=0.05, p=upLidEpDriverCrvPos[2], n=(eyePrefix + "_UpEyelid_MAIN_CTRL_JNT"))
		ctrlJnt_lowLidMain = cmds.joint(rad=0.05, p=lowLidEpDriverCrvPos[2], n=(eyePrefix + "_LowEyelid_MAIN_CTRL_JNT"))
		ctrlJnt_upLidSecA = cmds.joint(rad=0.05, p=upLidEpDriverCrvPos[1], n=(eyePrefix + "_UpEyelid_SecondaryA_CTRL_JNT"))
		ctrlJnt_upLidSecB = cmds.joint(rad=0.05, p=upLidEpDriverCrvPos[3], n=(eyePrefix + "_UpEyelid_SecondaryB_CTRL_JNT"))
		ctrlJnt_lowLidSecA = cmds.joint(rad=0.05, p=lowLidEpDriverCrvPos[1], n=(eyePrefix + "_LowEyelid_SecondaryA_CTRL_JNT"))
		ctrlJnt_lowLidSecB = cmds.joint(rad=0.05, p=lowLidEpDriverCrvPos[3], n=(eyePrefix + "_LowEyelid_SecondaryB_CTRL_JNT"))
		
		self.ctrlJnts = [ctrlJnt_CornerA, ctrlJnt_upLidSecA, ctrlJnt_upLidMain, ctrlJnt_upLidSecB, ctrlJnt_CornerB, ctrlJnt_lowLidSecB, ctrlJnt_lowLidMain, ctrlJnt_lowLidSecA]
		# Index:			0				1					2					3					4				5					6					7
		
		# Organise rig hierarchy
		hierarchyCtrlJntGrp = cmds.group(n=(eyePrefix + "_Eyelids_CTRL_JNT_GRP"), em=1)
		cmds.parent (hierarchyCtrlJntGrp, rigGrp)
		for jnt in self.ctrlJnts:
			cmds.parent(jnt, hierarchyCtrlJntGrp)
		
		# Skin controllers joints to each driver curve
		# Upper eyelid
		cmds.select(cl=1)
		cmds.select(self.ctrlJnts[:5])
		cmds.select(upLidDriverCrv, tgl=1)
		cmds.skinCluster()
		# Lower eyelid
		cmds.select(cl=1)
		cmds.select(self.ctrlJnts[0])
		cmds.select(self.ctrlJnts[4:], tgl=1)
		cmds.select(lowLidDriverCrv, tgl=1)
		cmds.skinCluster()

	def create_curve_controls(self, eyePrefix, parentCtrl, control_joints):
		"""
		Creates controller curve for each controller joint.
		Called by 'buildRig' function.
		Call functions: None
		"""
		# Organize rig hierarchy
		hierarchySecondGrp = cmds.group(n=(eyePrefix + "_Eyelids_CTRL_GRP"), em=1)
		hierarchyMainGrp = "Eyelids_CTRL_GRP"
		
		if parentCtrl is None:
			ctrlChildren = cmds.listRelatives(parentCtrl, children=1)
			if hierarchyMainGrp in ctrlChildren:
				cmds.parent(hierarchySecondGrp, (parentCtrl + "|" + hierarchyMainGrp))
			else:
				cmds.group(n=hierarchyMainGrp, em=1, p=parentCtrl)
				cmds.parent(hierarchySecondGrp, (parentCtrl + "|" + hierarchyMainGrp))
		else:
			if cmds.objExists("|" + hierarchyMainGrp):
				cmds.parent(hierarchySecondGrp, ("|" + hierarchyMainGrp))
			else:
				cmds.group(n=hierarchyMainGrp, em=1)
				cmds.parent(hierarchySecondGrp, ("|" + hierarchyMainGrp))
		
		# Creates the controller object
		cmds.select(cl=1)
		TEMP_CTRL1 = cmds.circle(r=0.15)[0]
		TEMP_CTRL2 = cmds.duplicate()[0]
		cmds.setAttr(TEMP_CTRL2 + ".rotateY", 90)
		TEMP_CTRL3 = cmds.duplicate()[0]
		cmds.setAttr(TEMP_CTRL3 + ".rotateX", 90)
		cmds.parent(TEMP_CTRL2, TEMP_CTRL3, TEMP_CTRL1)
		cmds.makeIdentity(apply=1, t=1, r=1, s=1, n=0, pn=1)
		cmds.pickWalk(d="down")
		cmds.select(TEMP_CTRL1, tgl=1)
		cmds.parent(r=1, s=1)
		cmds.delete(TEMP_CTRL2, TEMP_CTRL3)
		cmds.select(cl=1)
		
		# Place the controllers and constrain the joints
		self.ctrlList = []
		ctrlOffsetGrpList = []
		
		for jnt in control_joints:
			ctrlName = jnt[:-9]
			ctrlName = "CTRL_" + ctrlName
			ctrl = cmds.duplicate(TEMP_CTRL1, n=ctrlName)[0]
			self.ctrlList.append(ctrl)
			pointC_TEMP = cmds.pointConstraint(jnt, ctrl)
			cmds.delete(pointC_TEMP)
			origName = "ORIG_" + ctrlName
			origGrp = cmds.group(n=origName, em=1)
			parentC_TEMP = cmds.parentConstraint(ctrl, origGrp)
			cmds.delete(parentC_TEMP)
			if ctrl.find("_Secondary") != -1:
				# If controller is 'secondary'
				offsetGrpName = origName.replace("ORIG_", "OFFSET_")
				offsetGrp = cmds.duplicate(origGrp, n=offsetGrpName)
				cmds.parent(ctrl, offsetGrp)
				cmds.parent(offsetGrp, origGrp)
				ctrlOffsetGrpList.extend(offsetGrp)
			else:
				cmds.parent(ctrl, origGrp)
			cmds.parent(origGrp, hierarchySecondGrp)
			cmds.parentConstraint(ctrl, jnt)
		cmds.delete(TEMP_CTRL1)
		cmds.select(cl=1)
		
		# Constraints between main controllers and secondary ones
		# self.ctrlList = same order as 'control_joints' list
		# [ctrl_CornerA, ctrl_upLidSecA, ctrl_upLidMain, ctrl_upLidSecB, ctrl_CornerB, ctrl_lowLidSecB, ctrl_lowLidMain, ctrl_lowLidSecA]
		# Index: 0				1				2				3				4				5				6			7
		# ctrlOffsetGrpList = [OFFSET_Up_secondaryA, OFFSET_Up_secondaryB, OFFSET_Low_secondaryB, OFFSET_Low_secondaryA]
		# Index: 						0					1						2						3
		cmds.parentConstraint(self.ctrlList[0], ctrlOffsetGrpList[0], mo=1)
		cmds.parentConstraint(self.ctrlList[2], ctrlOffsetGrpList[0], mo=1)
		cmds.parentConstraint(self.ctrlList[2], ctrlOffsetGrpList[1], mo=1)
		cmds.parentConstraint(self.ctrlList[4], ctrlOffsetGrpList[1], mo=1)
		cmds.parentConstraint(self.ctrlList[4], ctrlOffsetGrpList[2], mo=1)
		cmds.parentConstraint(self.ctrlList[6], ctrlOffsetGrpList[2], mo=1)
		cmds.parentConstraint(self.ctrlList[6], ctrlOffsetGrpList[3], mo=1)
		cmds.parentConstraint(self.ctrlList[0], ctrlOffsetGrpList[3], mo=1)
		
		# Secondary controllers visibility (drove by main controllers)
		cmds.select(cl=1)
		cmds.select(self.ctrlList[2], self.ctrlList[6])
		cmds.addAttr(ln="SecondaryControls", at="bool", k=0)
		cmds.setAttr((self.ctrlList[2] + ".SecondaryControls"), 1, channelBox=1)
		cmds.setAttr((self.ctrlList[6] + ".SecondaryControls"), 1, channelBox=1)
		# Upper lid
		cmds.connectAttr((self.ctrlList[2] + ".SecondaryControls"), (self.ctrlList[1] + ".visibility"), f=1)
		cmds.connectAttr((self.ctrlList[2] + ".SecondaryControls"), (self.ctrlList[3] + ".visibility"), f=1)
		# Lower lid
		cmds.connectAttr((self.ctrlList[6] + ".SecondaryControls"), (self.ctrlList[5] + ".visibility"), f=1)
		cmds.connectAttr((self.ctrlList[6] + ".SecondaryControls"), (self.ctrlList[7] + ".visibility"), f=1)
		# Lock and hide unused channels
		for ctrl in self.ctrlList:
			cmds.setAttr((ctrl + ".sx"), lock=1, keyable=0, channelBox=0)
			cmds.setAttr((ctrl + ".sy"), lock=1, keyable=0, channelBox=0)
			cmds.setAttr((ctrl + ".sz"), lock=1, keyable=0, channelBox=0)
			cmds.setAttr((ctrl + ".v"), lock=1, keyable=0, channelBox=0)

	def add_smart_blink(self, eyePrefix, upLidBaseCrv, upLidDriverCrv, lowLidBaseCrv, lowLidDriverCrv, ctrlList, rigGrp, upCrvRigGrp, lowCrvRigGrp):
		"""
		Add a 'smart blink' feature to the eyelid rig, allowing to blink wherever the controllers are (blendshapes + wire deformers system).
		Called by 'buildRig' function.
		Call functions: None
		"""
		# Variables names containing 'SB' = smartBlink
		ctrlUpLidMain = ctrlList[2]
		ctrlLowLidMain = ctrlList[6]
		
		# STEP 1:
		bothLidsSB_Crv = cmds.duplicate(upLidDriverCrv, n=(eyePrefix + "_Eyelids_smartBlink_curve"))[0]
		cmds.parent(bothLidsSB_Crv, rigGrp)
		both_lids_smart_blink_blend_shape = cmds.blendShape(upLidDriverCrv, lowLidDriverCrv, bothLidsSB_Crv, n=(eyePrefix + "_Eyelids_smartBlink_BLENDSHAPE"))[0]
		cmds.select(cl=1)
		cmds.select(ctrlUpLidMain)
		cmds.addAttr(ln="SmartBlinkHeight", at="float", min=0, max=1, k=1)
		cmds.connectAttr((ctrlUpLidMain + ".SmartBlinkHeight"), (both_lids_smart_blink_blend_shape + "." + upLidDriverCrv), f=1)
		SBReverse = cmds.shadingNode("reverse", asUtility=1, n=(eyePrefix + "_Eyelids_smartBlink_reverse"))
		cmds.connectAttr((ctrlUpLidMain + ".SmartBlinkHeight"), (SBReverse + ".inputX"), f=1)
		cmds.connectAttr((SBReverse + ".outputX"), (both_lids_smart_blink_blend_shape + "." + lowLidDriverCrv), f=1)
		
		# STEP 2:
		upLidSB_Crv = cmds.duplicate(self.upLidCrv, n=(eyePrefix + "_UpEyelid_smartBlink_curve"))[0]
		lowLidSB_Crv = cmds.duplicate(self.lowLidCrv, n=(eyePrefix + "_LowEyelid_smartBlink_curve"))[0]
		cmds.setAttr((ctrlUpLidMain + ".SmartBlinkHeight"), 1)
		cmds.select(cl=1)
		wireUpLid = cmds.wire(upLidSB_Crv, n=(eyePrefix + "_UpEyelid_smartBlink_wire"), w=bothLidsSB_Crv, gw=0, en=1, ce=0, li=0)
		cmds.setAttr((wireUpLid[0] + ".scale[0]"), 0)
		cmds.setAttr((ctrlUpLidMain + ".SmartBlinkHeight"), 0)
		cmds.select(cl=1)
		wireLowLid = cmds.wire(lowLidSB_Crv, n=(eyePrefix + "_LowEyelid_smartBlink_wire"), w=bothLidsSB_Crv, gw=0, en=1, ce=0, li=0)
		cmds.setAttr((wireLowLid[0] + ".scale[0]"), 0)
		
		# STEP 3:
		up_lid_smart_blink_blend_shape = cmds.blendShape(upLidSB_Crv, self.upLidCrv, n=(eyePrefix + "_UpEyelid_smartBlink_BLENDSHAPE"))[0]
		low_lid_smart_blink_blend_shape = cmds.blendShape(lowLidSB_Crv, self.lowLidCrv, n=(eyePrefix + "_LowEyelid_smartBlink_BLENDSHAPE"))[0]
		
		# FINAL STEP:
		cmds.select(ctrlUpLidMain, ctrlLowLidMain)
		cmds.addAttr(ln="SmartBlink", at="float", min=0, max=1, k=1)
		cmds.connectAttr((ctrlUpLidMain + ".SmartBlink"), (up_lid_smart_blink_blend_shape + "." + upLidSB_Crv), f=1)
		cmds.connectAttr((ctrlLowLidMain + ".SmartBlink"), (low_lid_smart_blink_blend_shape + "." + lowLidSB_Crv), f=1)
		cmds.setAttr((ctrlUpLidMain + ".SmartBlinkHeight"), 0.15)
	## FUNCTIONS TO BUILD RIG -end ##

	def build_rigging(self, *args):
		"""
		Build eyelids rig.
		Called by 'UI' function.
		Call functions: 'vtxToJnt', 'placeRigLoc', 'createEyelidsCrv', 'connectLocToCrv', 'createDriverCrv', 'createJntCtrls', 'createCrvCtrls', 'addSmartBlink'
		"""
		
		if self.eye_locator is None or self.eye_name is None or self.upper_lid_vertex is None or self.lower_lid_vertex is None :
			cmds.error("目の中心、まぶたの頂点を定義してください.")
		else:
			# Step 1: まぶたの頂点ごとにジョイントを1つずつ配置する
			self.vertex_to_joint(self.eye_locator, self.eye_name, self.upper_lid_vertex, self.lower_lid_vertex, self.parent_joint)
			# Step 2: まぶたの頂点ごとにロケータを配置し、各ジョイントをそれに拘束する（IKのように動作するように）。
			self.place_rig_locator(self.eye_name, self.upLidJntList, self.lowLidJntList)
			# Step 3: それぞれのまぶたに「高解像度」のカーブを作成します（各頂点はカーブのポイントになります）。
			self.create_eyelids_curve(self.eye_name, self.upper_lid_vertex, self.lower_lid_vertex, self.grpTheseEyelidsRig)
			# Step 4: 各ロケータを point On Curve ノードでカーブに接続し、カーブの CV が動くと、対応するロケータが追従します(ジョイントも同様)
			self.connect_locator_to_curve(self.upLidLocList, self.upLidCrv, self.lowLidLocList, self.lowLidCrv)
			# Step 5: 制御点が5つだけの「低解像度」カーブを作成し、それをワイヤーデフォーマで高解像度カーブを駆動するようにする
			self.create_driver_curve(self.upLidCrv, self.hierarchyUpCrvGrp, self.lowLidCrv, self.hierarchyLowCrvGrp)
			# Step 6: 「ドライバーカーブ」を駆動するためのコントローラージョイントを作成する
			self.create_joint_controls(self.eye_name, self.cornerAPos, self.cornerBPos, self.upLidDriverCrv, self.lowLidDriverCrv, self.grpTheseEyelidsRig)
			# Step 7: カーブ・コントローラを作成し、それに対応するジョイントを取り付ける
			self.create_curve_controls(self.eye_name, self.parent_control, self.ctrlJnts)
			# Step 8: スマートブリンクのチェックボックスがチェックされていれば、スマートブリンクの機能を追加する。
			if cmds.checkBox(self.isSmartBlink, q=1, v=1) == 1:
				self.add_smart_blink(self.eye_name, self.upLidCrv, self.upLidDriverCrv, self.lowLidCrv, self.lowLidDriverCrv, self.ctrlList, self.hierarchyCrvGrp, self.hierarchyUpCrvGrp, self.hierarchyLowCrvGrp)
			
			# Clear scene & script variables #
			cmds.delete(self.eye_locator)
			cmds.select(cl=1)
			self.parent_joint = None
			self.parent_control = None
			self.eye_locator = None
			self.eye_name = None
			self.upper_lid_vertex = None
			self.lower_lid_vertex = None
			
			# Update UI #
			cmds.textField(self.txtfEye, e=1, tx="")
			cmds.textField(self.txtfJnt, e=1, tx="")
			cmds.textField(self.txtfCtrl, e=1, tx="")
			cmds.textField(self.txtfLoc, e=1, tx="")
			cmds.button(self.btnPlaceCenter, e=1, en=1)
			cmds.button(self.btnUndoPlaceCenter, e=1, en=0)
			cmds.scrollField(self.scrollfUpLid, e=1, cl=1)
			cmds.scrollField(self.scrollfLowLid, e=1, cl=1)
			cmds.checkBox(self.isSmartBlink, e=1, v=1)
			
			# End message
			cmds.inViewMessage(amg="<hl>Eyelids have been successfully rigged.</hl>", pos="midCenterTop", fade=True)
			#print("Eyelids have been successfully rigged.")

	def show_ui(self):
		"""
		Creates UI - Main function
		Call functions: 'eyeParentJnt', 'eyeParentCtrl', 'placeEyeCenter', 'placeEyeCenterUndo', 'upLidVtxSet', 'lowLidVtxSet', 'buildRig'
		"""
		# Main window
		winWidth = 320
		UKDP_mainWin = WIN_NAME
		if cmds.window(WIN_NAME, exists=1):
			cmds.deleteUI(WIN_NAME, window=1)
		cmds.window(WIN_NAME, title="Auto Eyelids Rig", s=0, mxb=0)
		# Main layout
		cmds.columnLayout(co=("both", 5))
		
		# Define eye name
		cmds.text(h=5, l="")
		cmds.rowLayout(numberOfColumns=2)
		cmds.text(w=120, l="Eye name (ex.: L_Eye)")
		self.txtfEye = cmds.textField(w=166)
		cmds.setParent("..")
		cmds.text(h=10, l="")
		cmds.frameLayout(w=winWidth, collapsable=1, collapse=1, marginWidth=5, l="Define rig hierarchy (optional)")
		
		# Define parent joint
		cmds.text(h=10, l="")
		cmds.text(l="まぶたの親ジョイントを選択します")
		self.btnEyeParentJnt = cmds.button(l="Set", c=self.eye_parent_joint)
		self.txtfJnt = cmds.textField(ed=0)
		cmds.text(h=10, l="")
		
		# Define parent control
		cmds.text(l="まぶたの親をコントロールします (would be the head control)")
		self.btnEyeParentCtrl = cmds.button(w=(winWidth - 50), l="Set", c=self.eye_parent_control)
		self.txtfCtrl = cmds.textField(w=(winWidth - 50), ed=0)
		cmds.text(h=5, l="")
		cmds.setParent("..")
		cmds.separator(h=15, w=winWidth, style="in")
		
		# Define eyeball center
		cmds.text(h=30, l="目玉を選択し、「中央に配置」をクリックします。")
		cmds.rowLayout(numberOfColumns=2)
		self.btnPlaceCenter = cmds.button(w=((winWidth / 2) - 2), l="Place center", c=self.place_eye_center)
		self.btnUndoPlaceCenter = cmds.button(w=((winWidth / 2) - 2), l="Undo", c=self.place_eye_center_undo, en=0)
		cmds.setParent("..")
		cmds.text(h=5, l="")
		self.txtfLoc = cmds.textField(w=winWidth, ed=0)
		cmds.separator(h=15, w=winWidth, style="in")

		# List upper lid vertices
		cmds.text(h=30, l="上まぶたの頂点を選択し、クリックします。'Set'.")
		self.btnUpLid = cmds.button(w=winWidth, l="Set", c=self.up_eyelid_vertex_set)
		self.scrollfUpLid = cmds.scrollField(w=winWidth, h=35, wordWrap=1, ed=0, en=0)
		cmds.separator(h=15, w=winWidth, style="in")

		# List lower lid vertices
		cmds.text(h=30, l="下まぶたの頂点を選択し、クリックします。'Set'.")
		self.btnLowLid = cmds.button(w=winWidth, l="Set", c=self.low_eyelid_vertex_set)
		self.scrollfLowLid = cmds.scrollField(w=winWidth, h=35, wordWrap=1, ed=0, en=0)
		cmds.separator(h=15, w=winWidth, style="in")
		
		# Allow/disallow smart blink
		self.isSmartBlink = cmds.checkBox(h=30, l="Add smart blink?", v=1)
		
		# Build final rig
		self.btnBuild = cmds.button(w=winWidth, h=60, l="BUILD RIG", c=self.build_rigging, bgc=(0.1, 0.7, 0.7))
		cmds.text(h=5, l="")
		
		# Script info
		cmds.text(en=0, w=winWidth, l=MadeBy + " " + ScriptName + " " + Version)
		cmds.text(h=5, l="")
		cmds.setParent("..")
		cmds.showWindow(WIN_NAME)


autoEyelidsRig = AER()
