# !/usr/bin/env python
# -*- coding: utf-8 -*-
    
import maya.cmds as cmds
import pymel.core as pm

WINDOW_NAME = 'AnimationMirror'

def _create_animation_window():

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
	cmds.checkBox("TranslationsCheckbox", en=1, cc=lambda *args: _change_options_mirror(), ann="TranslationsCheckbox", label="Translations", w=100, v=1)
	cmds.radioCollection()
	cmds.radioButton("XAxisTransRadio", ann="XAxisTransRadio", label="XZ", sl=1)
	cmds.radioButton("YAxisTransRadio", ann="YAxisTransRadio", label="YX")
	cmds.radioButton("ZAxisTransRadio", ann="ZAxisTransRadio", label="ZY")
	cmds.setParent('..')
	cmds.rowLayout("RotateModeRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="RotateModeRow")
	cmds.checkBox("RotationsCheckbox", en=1, cc=lambda *args: _change_options_mirror(), ann="RotationsCheckbox", label="Rotations", w=100, v=1)
	cmds.checkBox("XAxisRotCheckbox", ann="XAxisRotCheckbox", en=1, v=0, label="X")
	cmds.checkBox("YAxisRotCheckbox", ann="YAxisRotCheckbox", en=1, v=1, label="Y")
	cmds.checkBox("ZAxisRotCheckbox", ann="ZAxisRotCheckbox", en=1, v=1, label="Z")
	cmds.setParent('..')
	cmds.rowLayout("MirrorRealRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="MirrorRealRow")
	cmds.button("MirrorRealButton", enableBackground=1, c=lambda *args: _mirror_animation(0), bgc=(0.25, 0.5, 0.4), h=30, ann="MirrorRealButton", label="Interactive Mirror", en=1, w=120)
	cmds.button("UndoMirrorButton", enableBackground=1, c=lambda *args: _delete_all_created(), bgc=(0.65, 0.5, 0.4), h=30, ann="UndoMirrorButton", label="Undo", en=1, w=70)
	cmds.button("BakeMirrorButton", enableBackground=1, c=lambda *args: _fast_bake(1), bgc=(1, 0.5, 0.4), h=30, ann="BakeMirrorButton", label="Bake", en=1, w=70)
	cmds.setParent('..')
	cmds.rowLayout("MirrorBakeRow", numberOfColumns=6, columnAttach=(1, "left", 5), ann="MirrorBakeRow")
	cmds.button("MirrorBakeButton", enableBackground=1, c=lambda *args: _mirror_animation(1), bgc=(0.25, 0.5, 0.4), h=30, ann="MirrorBakeButton", label="Mirror with Bake", en=1, w=264)
	cmds.setParent('..')

def _globals_variables():
	pm.melGlobals.initVar('string[]', 'centerJoint')
	pm.melGlobals.initVar('string[]', 'operatorTrans')
	pm.melGlobals.initVar('string[]', 'operatorRotate')
	pm.melGlobals.initVar('string[]', 'mirrorObject')
	pm.melGlobals.initVar('string[]', 'centerObject')
	pm.melGlobals.initVar('string[]', 'referenceObject')

	pm.melGlobals.initVar('string', 'gPlayBackSlider')
	pm.melGlobals.initVar('float', 'startFrame')
	pm.melGlobals.initVar('float', 'finishFrame')

	pm.melGlobals.initVar('int', 'ind')
	#pm.melGlobals['ind'] = 0
	pm.melGlobals.initVar('int', 'iTo')
	pm.melGlobals.initVar('int', 'iRo')
	pm.melGlobals['centerJoint'] = []
	pm.melGlobals['ind'] = 0
	pm.melGlobals['iTo'] = 0
	pm.melGlobals['iRo'] = 0

def _change_options_mirror():
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

def _mirror_animation(withBake):
	#pm.melGlobals.initVar('string[]', 'centerObject')
	#pm.melGlobals.initVar('string[]', 'referenceObject')
	#pm.melGlobals.initVar('string[]', 'mirrorObject')
	#pm.melGlobals.initVar('string[]', 'centerJoint')
	#pm.melGlobals.initVar('int', 'ind')
	doTransforms = cmds.checkBox('TranslationsCheckbox', q=1, v=1)
	doRotations = cmds.checkBox('RotationsCheckbox', q=1, v=1)
	selected = cmds.ls(selection=1)
	if len(selected) < 3:
		pm.mel.error("Select at least two objects for mirror animation")
		
	pm.melGlobals['centerObject'][pm.melGlobals['ind']] = str(selected[0])
	pm.melGlobals['referenceObject'][pm.melGlobals['ind']] = str(selected[1])
	pm.melGlobals['mirrorObject'][pm.melGlobals['ind']] = str(selected[2])
	if cmds.checkBox('RotationsCheckbox', q=1, v=1):
		referenceObjectRotate = cmds.xform(pm.melGlobals['referenceObject'][pm.melGlobals['ind']], q=1, ro=1, os=1)
		if cmds.checkBox('XAxisRotCheckbox', q=1, v=1):
			valX = -1
		else:
			valX = 1
			
		if cmds.checkBox('YAxisRotCheckbox', q=1, v=1):
			valY = -1
		else:
			valY = 1
			
		if cmds.checkBox('ZAxisRotCheckbox', q=1, v=1):
			valZ = -1
		else:
			valZ = 1
		cmds.xform(pm.melGlobals['mirrorObject'][pm.melGlobals['ind']], ro=((referenceObjectRotate[0] * valX), (referenceObjectRotate[1] * valY), (referenceObjectRotate[2] * valZ)), os=1)
		
	cmds.select(cl=1)
	pm.melGlobals['centerJoint'][pm.melGlobals['ind']] = str(cmds.joint(rad=1))
	cmds.setAttr((pm.melGlobals['centerJoint'][pm.melGlobals['ind']] + ".visibility"), 0)
	cmds.parentConstraint(pm.melGlobals['centerObject'][pm.melGlobals['ind']], pm.melGlobals['centerJoint'][pm.melGlobals['ind']], weight=1)
	#parent for snap trans and rotations
	cmds.select(cl=1)
	cmds.select(pm.melGlobals['centerJoint'][pm.melGlobals['ind']])
	#select for continue hierarchy
	referenceJoint = cmds.joint(rad=1)
	#create ref joint in hierarchy
	cmds.pointConstraint(pm.melGlobals['referenceObject'][pm.melGlobals['ind']], referenceJoint, weight=1)
	cmds.orientConstraint(pm.melGlobals['referenceObject'][pm.melGlobals['ind']], referenceJoint, weight=1)
	cmds.delete(referenceJoint, cn=1)
	cmds.makeIdentity(referenceJoint, n=0, s=0, r=1, t=0, apply=True, pn=1)
	mirrorJoint = []
	#Mirror joint
	if cmds.checkBox('TranslationsCheckbox', q=1, v=1):
		if cmds.radioButton('XAxisTransRadio', q=1, sl=1):
			mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorXY=1, mirrorBehavior=1)
			
		if cmds.radioButton('YAxisTransRadio', q=1, sl=1):
			mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorYZ=1)
			
		if cmds.radioButton('ZAxisTransRadio', q=1, sl=1):
			mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorXZ=1)
	else:
		mirrorJoint = cmds.mirrorJoint(referenceJoint, mirrorBehavior=1, mirrorYZ=1)
		
	cmds.pointConstraint(pm.melGlobals['referenceObject'][pm.melGlobals['ind']], referenceJoint, weight=1)
	#Reference joint constrain after mirror (nessasary)
	cmds.orientConstraint(pm.melGlobals['referenceObject'][pm.melGlobals['ind']], referenceJoint, weight=1)
	if doRotations == 1:
		cmds.orientConstraint(pm.melGlobals['mirrorObject'][pm.melGlobals['ind']], mirrorJoint, weight=1)
		cmds.delete(mirrorJoint, cn=1)
		cmds.makeIdentity(mirrorJoint, n=0, s=0, r=1, t=0, apply=True, pn=1)
		cmds.orientConstraint(mirrorJoint, pm.melGlobals['mirrorObject'][pm.melGlobals['ind']], weight=1)
		pm.mel.rotate_connect_operator(mirrorJoint[0], referenceJoint)
		
	if doTransforms == 1:
		cmds.pointConstraint(mirrorJoint, pm.melGlobals['mirrorObject'][pm.melGlobals['ind']], weight=1)
		pm.mel.transform_connect_operator(mirrorJoint[0], referenceJoint)
		
	if withBake == 1:
		pm.mel.fast_bake(1)
	pm.melGlobals['ind'] = pm.melGlobals['ind'] + 1

def _transform_connect_operator(mirrorJoint, referenceJoint):
	#pm.melGlobals.initVar('int', 'iTo')
	#pm.melGlobals.initVar('string[]', 'operatorTrans')
	transX = cmds.radioButton('XAxisTransRadio', q=1, sl=1)
	transY = cmds.radioButton('YAxisTransRadio', q=1, sl=1)
	transZ = cmds.radioButton('ZAxisTransRadio', q=1, sl=1)
	constPoint = cmds.pointConstraint(referenceJoint, mirrorJoint, weight=1)
	if transX == 1:
		pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".operation"), 2)
		cmds.connectAttr((str(constPoint[0]) + ".constraintTranslateX"), (pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".outFloat"), (mirrorJoint + ".translateX"), f=1)
		pm.melGlobals['iTo'] = pm.melGlobals['iTo'] + 1
		
	if transY == 1:
		pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".operation"), 2)
		cmds.connectAttr((str(constPoint[0]) + ".constraintTranslateY"), (pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".outFloat"), (mirrorJoint + ".translateY"), f=1)
		pm.melGlobals['iTo'] = pm.melGlobals['iTo'] + 1
		
	if transZ == 1:
		pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".operation"), 2)
		cmds.connectAttr((str(constPoint[0]) + ".constraintTranslateZ"), (pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorTrans'][pm.melGlobals['iTo']] + ".outFloat"), (mirrorJoint + ".translateZ"), f=1)
		pm.melGlobals['iTo'] = pm.melGlobals['iTo'] + 1

def _rotate_connect_operator(mirrorJoint, referenceJoint):
	#pm.melGlobals.initVar('int', 'iRo')
	#pm.melGlobals.initVar('string[]', 'operatorRotate')
	rotateX = cmds.checkBox('XAxisRotCheckbox', q=1, v=1)
	rotateY = cmds.checkBox('YAxisRotCheckbox', q=1, v=1)
	rotateZ = cmds.checkBox('ZAxisRotCheckbox', q=1, v=1)
	if rotateX == 1:
		pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".operation"), 2)
		cmds.connectAttr((referenceJoint + ".rotateX"), (pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".outFloat"), (mirrorJoint + ".rotateX"), f=1)
		pm.melGlobals['iRo'] = pm.melGlobals['iRo'] + 1
	else:
		cmds.connectAttr((referenceJoint + ".rotateX"), (mirrorJoint + ".rotateX"), f=1)
		
	if rotateY == 1:
		pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".operation"), 2)
		cmds.connectAttr((referenceJoint + ".rotateY"), (pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".outFloat"), (mirrorJoint + ".rotateY"), f=1)
		pm.melGlobals['iRo'] = pm.melGlobals['iRo'] + 1
	else:
		cmds.connectAttr((referenceJoint + ".rotateY"), (mirrorJoint + ".rotateY"), f=1)
		
	if rotateZ == 1:
		pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] = str(cmds.shadingNode('floatMath', asUtility=1))
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatB"), -1)
		cmds.setAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".operation"), 2)
		cmds.connectAttr((referenceJoint + ".rotateZ"), (pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".floatA"), f=1)
		cmds.connectAttr((pm.melGlobals['operatorRotate'][pm.melGlobals['iRo']] + ".outFloat"), (mirrorJoint + ".rotateZ"), f=1)
		pm.melGlobals['iRo'] = pm.melGlobals['iRo'] + 1
	else:
		cmds.connectAttr((referenceJoint + ".rotateZ"), (mirrorJoint + ".rotateZ"), f=1)
def _delete_all_created():
	#pm.melGlobals.initVar('string[]', 'centerJoint')
	#pm.melGlobals.initVar('string[]', 'operatorTrans')
	#pm.melGlobals.initVar('string[]', 'operatorRotate')
	if pm.catch(lambda:
				cmds.delete(pm.melGlobals['centerJoint'], pm.melGlobals['operatorTrans'], pm.melGlobals['operatorRotate'],
							pm.melGlobals['mirrorObject'], pm.melGlobals['centerObject'], pm.melGlobals['referenceObject'],
							pm.melGlobals['gPlayBackSlider'], pm.melGlobals['startFrame'], pm.melGlobals['finishFrame'],
							pm.melGlobals['ind'], pm.melGlobals['iTo'], pm.melGlobals['iRo'])):
		pm.mel.warning("Some temporary objects have been removed from the scene", n=1)
		#delete $centerJoint $operatorTrans $operatorRotate;
	_globals_variables()
	
def _fast_bake(defineFrames):
	#pm.melGlobals.initVar('string[]', 'mirrorObject')
	cmds.select(pm.melGlobals['mirrorObject'], r=1)
	#pm.melGlobals.initVar('string', 'gPlayBackSlider')
	#pm.melGlobals.initVar('float', 'startFrame')
	#pm.melGlobals.initVar('float', 'finishFrame')
	if defineFrames == 1:
		_define_frames_range()
		
	cmds.refresh(suspend=1)
	#do not refresh viewport
	start = pm.melGlobals['startFrame']
	end = pm.melGlobals['finishFrame']
	cmds.bakeResults(sparseAnimCurveBake=False, minimizeRotation=True, removeBakedAttributeFromLayer=False, bakeOnOverrideLayer=False, preserveOutsideKeys=True,
					 simulation=0, sampleBy=1, time=(int(start), int(end)), disableImplicitControl=True)
	cmds.delete(sc=1)
	#delete static curves for baked object
	cmds.filterCurve()
	cmds.refresh(suspend=0)
	_delete_all_created()
	
def _define_frames_range():
	pm.melGlobals.initVar('string', 'gPlayBackSlider')
	pm.melGlobals.initVar('float', 'startFrame')
	pm.melGlobals.initVar('float', 'finishFrame')
	pm.melGlobals.initVar('int', 'selectedTimeField')
	selectedFrames = pm.util.defaultlist(float, cmds.timeControl(pm.melGlobals['gPlayBackSlider'], q=1, ra=1))
	if (selectedFrames[1] - selectedFrames[0]) <= 1:
		pm.melGlobals['startFrame'] = float(cmds.playbackOptions(q=1, min=1))
		pm.melGlobals['finishFrame'] = float(cmds.playbackOptions(q=1, max=1))
		pm.melGlobals['selectedTimeField'] = 0
	else:
		pm.melGlobals['startFrame'] = selectedFrames[0]
		pm.melGlobals['finishFrame'] = selectedFrames[1]
		pm.melGlobals['selectedTimeField'] = 1
	pass
	

def Initialize():
	_create_animation_window()
	_globals_variables()

