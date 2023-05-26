# -*- coding: utf-8 -*-
    
import maya.cmds as cmds
import maya.mel
from functools import partial

WINDOW_NAME = 'AnimationMirror'

class Animation_Mirror:
	def __init__(self):
		self._init_variables()
		self._create_animation_window()

	def _init_variables(self):
		self.centerJoint = []
		self.operatorTrans = []
		self.operatorRotate = []
		self.mirrorObject = []
		self.centerObject = []
		self.referenceObject = []
		self.gPlayBackSlider = ''
		self.startFrame = 0
		self.finishFrame = 0
		self.ind = 0
		self.iTo = 0
		self.iRo = 0

	def _create_animation_window(self):
		if cmds.window(WINDOW_NAME, exists=1):
			cmds.deleteUI(WINDOW_NAME)

		cmds.window(WINDOW_NAME, bgc=(0.265, 0.265, 0.265), iconName="Animation Mirror", title="Animation Mirror v1.0.0", h=400, s=0, w=280, nestedDockingEnabled=True)
		cmds.showWindow(WINDOW_NAME)
		cmds.window(WINDOW_NAME, h=300, s=0, e=1, w=280, resizeToFitChildren=1)
		cmds.frameLayout(cll=0, w=270, la="center", label="Animation Mirror Tool", lv=1, backgroundColor=(0, 0, 1), backgroundShade=0)
		cmds.columnLayout("ThisCreateCol", ann="ThisCreateCol", bgc=(0.242, 0.242, 0.3), co=('both', 0), rs=2)
		cmds.columnLayout("InfoTextCol", columnAlign="center", co=('both', 5), rs=5, columnWidth=250, ann="InfoTextCol", adjustableColumn=0)
		cmds.text(" ", h=2)
		cmds.text("1. Select central object", h=20, font="boldLabelFont")
		cmds.text("2. Add reference object", h=20, font="boldLabelFont")
		cmds.text("3. Add object for mirror", h=20, font="boldLabelFont")
		cmds.text(" ", h=2)
		cmds.separator(w=270)
		cmds.setParent('..')
		cmds.rowLayout("TranslationModeRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="TranslationModeRow")
		cmds.checkBox("TranslationsCheckbox", en=1, cc=partial(self._change_options_mirror), ann="TranslationsCheckbox", label="Translations", w=100, v=1)
		cmds.radioCollection()
		cmds.radioButton("XAxisTransRadio", ann="XAxisTransRadio", label="XZ", sl=1)
		cmds.radioButton("YAxisTransRadio", ann="YAxisTransRadio", label="YX")
		cmds.radioButton("ZAxisTransRadio", ann="ZAxisTransRadio", label="ZY")
		cmds.setParent('..')
		cmds.rowLayout("RotateModeRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="RotateModeRow")
		cmds.checkBox("RotationsCheckbox", en=1, cc=partial(self._change_options_mirror), ann="RotationsCheckbox", label="Rotations", w=100, v=1)
		cmds.checkBox("XAxisRotCheckbox", ann="XAxisRotCheckbox", en=1, v=0, label="X")
		cmds.checkBox("YAxisRotCheckbox", ann="YAxisRotCheckbox", en=1, v=1, label="Y")
		cmds.checkBox("ZAxisRotCheckbox", ann="ZAxisRotCheckbox", en=1, v=1, label="Z")
		cmds.setParent('..')
		cmds.rowLayout("MirrorRealRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="MirrorRealRow")
		cmds.button("MirrorRealButton", enableBackground=1, command=partial(self._mirror_animation, False), bgc=(0.25, 0.5, 0.4), h=30, ann="MirrorRealButton", label="Interactive Mirror", en=1, w=120)
		cmds.button("UndoMirrorButton", enableBackground=1, command=partial(self._delete_all_created), bgc=(0.65, 0.5, 0.4), h=30, ann="UndoMirrorButton", label="Undo", en=1, w=70)
		cmds.button("BakeMirrorButton", enableBackground=1, command=partial(self._fast_bake, 1), bgc=(1, 0.5, 0.4), h=30, ann="BakeMirrorButton", label="Bake", en=1, w=70)
		cmds.setParent('..')
		cmds.rowLayout("MirrorBakeRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="MirrorBakeRow")
		cmds.button("MirrorBakeButton", enableBackground=1, command=partial(self._mirror_animation, True), bgc=(0.25, 0.5, 0.4), h=30, ann="MirrorBakeButton", label="Mirror with Bake", en=1, w=264)
		cmds.setParent('..')

	def _change_options_mirror(self):
		if cmds.checkBox('TranslationsCheckbox', q=1, v=1):
			cmds.radioButton('XAxisTransRadio', en=1, e=1)
			cmds.radioButton('YAxisTransRadio', en=1, e=1)
			cmds.radioButton('ZAxisTransRadio', en=1, e=1)
		else:
			cmds.radioButton('XAxisTransRadio', en=0, e=1)
			cmds.radioButton('YAxisTransRadio', en=0, e=1)
			cmds.radioButton('ZAxisTransRadio', en=0, e=1)

		if cmds.checkBox('RotationsCheckbox', q=1, v=1):
			cmds.checkBox('XAxisRotCheckbox', en=1, e=1)
			cmds.checkBox('YAxisRotCheckbox', en=1, e=1)
			cmds.checkBox('ZAxisRotCheckbox', en=1, e=1)
		else:
			cmds.checkBox('XAxisRotCheckbox', en=0, e=1)
			cmds.checkBox('YAxisRotCheckbox', en=0, e=1)
			cmds.checkBox('ZAxisRotCheckbox', en=0, e=1)

	def _mirror_animation(self, with_bake: bool):
		# pm.melGlobals.initVar('string[]', 'centerObject')
		# pm.melGlobals.initVar('string[]', 'referenceObject')
		# pm.melGlobals.initVar('string[]', 'mirrorObject')
		# pm.melGlobals.initVar('string[]', 'centerJoint')
		# pm.melGlobals.initVar('int', 'ind')
		doTransforms = cmds.checkBox('TranslationsCheckbox', q=True, v=True)
		doRotations = cmds.checkBox('RotationsCheckbox', q=True, v=True)
		selected = cmds.ls(selection=1)
		if len(selected) < 3:
			print("Select at least two objects for mirror animation")

		self.centerJoint[self.ind] = str(selected[0])
		self.referenceObject[self.ind] = str(selected[1])
		self.mirrorObject[self.ind] = str(selected[2])
		if cmds.checkBox('RotationsCheckbox', q=True, v=True):
			referenceObjectRotate = cmds.xform(self.referenceObject[self.ind], query=True, rotation=True, objectSpace=True)
			if cmds.checkBox('XAxisRotCheckbox', q=True, v=True):
				valX = -1
			else:
				valX = 1

			if cmds.checkBox('YAxisRotCheckbox', q=True, v=True):
				valY = -1
			else:
				valY = 1

			if cmds.checkBox('ZAxisRotCheckbox', q=True, v=True):
				valZ = -1
			else:
				valZ = 1
			cmds.xform(self.mirrorObject[self.ind], ro=((referenceObjectRotate[0] * valX), (referenceObjectRotate[1] * valY), (referenceObjectRotate[2] * valZ)), os=1)

		cmds.select(cl=1)
		self.centerJoint[self.ind] = str(cmds.joint(rad=1))
		cmds.setAttr((self.centerJoint[self.ind] + ".visibility"), 0)
		cmds.parentConstraint(self.centerObject[self.ind], self.centerJoint[self.ind], weight=1)
		# parent for snap trans and rotations
		cmds.select(cl=1)
		cmds.select(self.centerJoint[self.ind])
		# select for continue hierarchy
		referenceJoint = cmds.joint(rad=1)
		# create ref joint in hierarchy
		cmds.pointConstraint(self.referenceObject[self.ind], referenceJoint, weight=1)
		cmds.orientConstraint(self.referenceObject[self.ind], referenceJoint, weight=1)
		cmds.delete(referenceJoint, cn=1)
		cmds.makeIdentity(referenceJoint, n=0, s=0, r=1, t=0, apply=True, pn=1)
		mirrorJoint = []
		# Mirror joint
		if cmds.checkBox('TranslationsCheckbox', q=True, v=True):
			if cmds.radioButton('XAxisTransRadio', q=1, sl=1):
				mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorXY=1, mirrorBehavior=1)

			if cmds.radioButton('YAxisTransRadio', q=1, sl=1):
				mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorYZ=1)

			if cmds.radioButton('ZAxisTransRadio', q=1, sl=1):
				mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorXZ=1)
		else:
			mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorYZ=1)

		# 鏡面後の基準関節の拘束
		cmds.pointConstraint(self.referenceObject[self.ind], referenceJoint, weight=1)
		cmds.orientConstraint(self.referenceObject[self.ind], referenceJoint, weight=1)
		if doRotations is True:
			cmds.orientConstraint(self.mirrorObject[self.ind], mirrorJoint, weight=1)
			cmds.delete(mirrorJoint, cn=1)
			cmds.makeIdentity(mirrorJoint, n=0, s=0, r=1, t=0, apply=True, pn=1)
			cmds.orientConstraint(mirrorJoint, self.mirrorObject[self.ind], weight=1)
			self._rotate_connect_operator(mirrorJoint[0], referenceJoint)
		if doTransforms is True:
			cmds.pointConstraint(mirrorJoint, self.mirrorObject[self.ind], weight=1)
			self._transform_connect_operator(mirrorJoint[0], referenceJoint)
		if with_bake is True:
			self._fast_bake(1)
		self.ind = self.ind + 1

	def _transform_connect_operator(self, mirrorJoint, referenceJoint):
		# pm.melGlobals.initVar('int', 'iTo')
		# pm.melGlobals.initVar('string[]', 'operatorTrans')
		transX = cmds.radioButton('XAxisTransRadio', q=True, sl=True)
		transY = cmds.radioButton('YAxisTransRadio', q=True, sl=True)
		transZ = cmds.radioButton('ZAxisTransRadio', q=True, sl=True)
		constraint_point = cmds.pointConstraint(referenceJoint, mirrorJoint, weight=1)

		if transX is True:
			self.operatorTrans[self.iTo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorTrans[self.iTo] + ".floatB"), -1)
			cmds.setAttr((self.operatorTrans[self.iTo] + ".operation"), 2)
			cmds.connectAttr((str(constraint_point[0]) + ".constraintTranslateX"), (self.operatorTrans[self.iTo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorTrans[self.iTo] + ".outFloat"), (mirrorJoint + ".translateX"), f=1)
			self.iTo = self.iTo + 1

		if transY is True:
			self.operatorTrans[self.iTo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorTrans[self.iTo] + ".floatB"), -1)
			cmds.setAttr((self.operatorTrans[self.iTo] + ".operation"), 2)
			cmds.connectAttr((str(constraint_point[0]) + ".constraintTranslateY"), (self.operatorTrans[self.iTo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorTrans[self.iTo] + ".outFloat"), (mirrorJoint + ".translateY"), f=1)
			self.iTo = self.iTo + 1

		if transZ is True:
			self.operatorTrans[self.iTo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorTrans[self.iTo] + ".floatB"), -1)
			cmds.setAttr((self.operatorTrans[self.iTo] + ".operation"), 2)
			cmds.connectAttr((str(constraint_point[0]) + ".constraintTranslateZ"), (self.operatorTrans[self.iTo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorTrans[self.iTo] + ".outFloat"), (mirrorJoint + ".translateZ"), f=1)
			self.iTo = self.iTo + 1

	def _rotate_connect_operator(self, mirrorJoint, referenceJoint):
		# pm.melGlobals.initVar('int', 'iRo')
		# pm.melGlobals.initVar('string[]', 'operatorRotate')
		rotateX = cmds.checkBox('XAxisRotCheckbox', q=True, v=True)
		rotateY = cmds.checkBox('YAxisRotCheckbox', q=True, v=True)
		rotateZ = cmds.checkBox('ZAxisRotCheckbox', q=True, v=True)
		if rotateX is True:
			self.operatorRotate[self.iRo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorRotate[self.iRo] + ".floatB"), -1)
			cmds.setAttr((self.operatorRotate[self.iRo] + ".operation"), 2)
			cmds.connectAttr((referenceJoint + ".rotateX"), (self.operatorRotate[self.iRo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorRotate[self.iRo] + ".outFloat"), (mirrorJoint + ".rotateX"), f=1)
			self.iRo = self.iRo + 1
		else:
			cmds.connectAttr((referenceJoint + ".rotateX"), (mirrorJoint + ".rotateX"), f=1)

		if rotateY is True:
			self.operatorRotate[self.iRo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorRotate[self.iRo] + ".floatB"), -1)
			cmds.setAttr((self.operatorRotate[self.iRo] + ".operation"), 2)
			cmds.connectAttr((referenceJoint + ".rotateY"), (self.operatorRotate[self.iRo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorRotate[self.iRo] + ".outFloat"), (mirrorJoint + ".rotateY"), f=1)
			self.iRo = self.iRo + 1
		else:
			cmds.connectAttr((referenceJoint + ".rotateY"), (mirrorJoint + ".rotateY"), f=1)

		if rotateZ is True:
			self.operatorRotate[self.iRo] = str(cmds.shadingNode('floatMath', asUtility=1))
			cmds.setAttr((self.operatorRotate[self.iRo] + ".floatB"), -1)
			cmds.setAttr((self.operatorRotate[self.iRo] + ".operation"), 2)
			cmds.connectAttr((referenceJoint + ".rotateZ"), (self.operatorRotate[self.iRo] + ".floatA"), f=1)
			cmds.connectAttr((self.operatorRotate[self.iRo] + ".outFloat"), (mirrorJoint + ".rotateZ"), f=1)
			self.iRo = self.iRo + 1
		else:
			cmds.connectAttr((referenceJoint + ".rotateZ"), (mirrorJoint + ".rotateZ"), f=1)

	def _delete_all_created(self):
		# pm.melGlobals.initVar('string[]', 'centerJoint')
		# pm.melGlobals.initVar('string[]', 'operatorTrans')
		# pm.melGlobals.initVar('string[]', 'operatorRotate')
		self._init_variables()

	def _fast_bake(self, defineFrames: int):
		# pm.melGlobals.initVar('string[]', 'mirrorObject')
		cmds.select(self.mirrorObject, r=1)
		# pm.melGlobals.initVar('string', 'gPlayBackSlider')
		# pm.melGlobals.initVar('float', 'startFrame')
		# pm.melGlobals.initVar('float', 'finishFrame')
		if defineFrames == 1:
			self._define_frames_range()

		cmds.refresh(suspend=1)
		# do not refresh viewport
		start = self.startFrame
		end = self.finishFrame
		cmds.bakeResults(sparseAnimCurveBake=False, minimizeRotation=True, removeBakedAttributeFromLayer=False,
						 bakeOnOverrideLayer=False, preserveOutsideKeys=True, simulation=0, sampleBy=1, time=(int(start), int(end)), disableImplicitControl=True)
		cmds.delete(sc=1)
		# delete static curves for baked object
		cmds.filterCurve()
		cmds.refresh(suspend=0)
		self._delete_all_created()

	def _define_frames_range(self):
		#pm.melGlobals.initVar('string', 'gPlayBackSlider')
		#pm.melGlobals.initVar('float', 'startFrame')
		#pm.melGlobals.initVar('float', 'finishFrame')
		#pm.melGlobals.initVar('int', 'selectedTimeField')

		# タイムスライダの選択領域を取得
		play_back_slider = maya.mel.eval('$tmpVar=$gPlayBackSlider')
		selectedFrames = cmds.timeControl(play_back_slider, q=True, rangeArray=True)
		if (selectedFrames[1] - selectedFrames[0]) <= 1:
			self.startFrame = float(cmds.playbackOptions(q=1, min=1))
			self.finishFrame = float(cmds.playbackOptions(q=1, max=1))
			self.selectedTimeField = 0
		else:
			self.startFrame = selectedFrames[0]
			self.finishFrame = selectedFrames[1]
			self.selectedTimeField = 1

def Initialize():
	animation_mirror = Animation_Mirror()


