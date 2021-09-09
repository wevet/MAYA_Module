# -*- coding utf-8 -*-

import maya.cmds as cmds


def facePresetUI():
	if cmds.window('facePreset', ex=True):
		cmds.deleteUI('facePreset')
	
	cmds.window('facePreset', wh=(100, 100), sizeable=True)
	cmds.columnLayout(adjustableColumn=True)
	cmds.gridLayout(numberOfColumns=6, cellWidthHeight=(100, 405))
	
	cmds.frameLayout(label='EYE Brow', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='L_Brow_Default', h=30, c='setFace("L_BrowDefault")')
	cmds.button(label='R_Brow_Default', h=30, c='setFace("R_BrowDefault")')
	cmds.button(label='L_Brow_Up', h=30, c='setFace("L_BrowUp")')
	cmds.button(label='R_Brow_Up', h=30, c='setFace("R_BrowUp")')
	cmds.button(label='L_Brow_Down', h=30, c='setFace("L_BrowDown")')
	cmds.button(label='R_Brow_Down', h=30, c='setFace("R_BrowDown")')
	cmds.button(label='C_Brow_Up', h=30, c='setFace("C_BrowUp")')
	cmds.button(label='C_Brow_Down', h=30, c='setFace("C_BrowDown")')
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), c='setFace("setEyeBrow")')
	cmds.setParent(u=True)
		
	cmds.frameLayout(label='EYE', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='Two_EYE_Open', h=30, c='setFace("TwoEyeOpen")')
	cmds.button(label='Two_EYE_Close', h=30, c='setFace("TwoEyeClose")')
	cmds.button(label='L_EYE_Open', h=30, c='setFace("eyeDefault_L")')
	cmds.button(label='R_EYE_Open', h=30, c='setFace("eyeDefault_R")')
	cmds.button(label='L_EYE_Close', h=30, c='setFace("eyeBlink_L")')
	cmds.button(label='R_EYE_Close', h=30, c='setFace("eyeBlink_R")')
	cmds.button(label='L_EYE_Tired', h=30, c='setFace("eyeTired_L")')
	cmds.button(label='R_EYE_Tired', h=30, c='setFace("eyeTired_R")')
	cmds.button(label='L_EYE_Big_Open', h=30, c='setFace("eyeOpen_L")')
	cmds.button(label='R_EYE_Big_Open', h=30, c='setFace("eyeOpen_R")')
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), c='setFace("setEye")')
	cmds.setParent(u=True)

	cmds.frameLayout(label='Mouth', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='Mouth Default', h=30, c='setFace("MouthDefault")')
	cmds.button(label='Mouth Ah~', h=30, c='setFace("MouthAh")')
	cmds.button(label='Mouth AE~', h=30, c='setFace("MouthAE")')
	cmds.button(label='Mouth EE~', h=30, c='setFace("MouthEE")')
	cmds.button(label='Mouth Oh~', h=30, c='setFace("MouthOh")')
	cmds.button(label='Mouth Uh~', h=30, c='setFace("MouthUh")')
	cmds.button(label='Mouth EU~', h=30, c='setFace("MouthEU")')
	cmds.button(label='Mouth Open', h=30, c='setFace("MouthOpen")')
	cmds.button(label='Mouth Close', h=30, c='setFace("MouthClose")')
	cmds.button(label='Mouth Smile', h=30, c='setFace("MouthSmile")')
	cmds.button(label='Mouth Frown', h=30, c='setFace("MouthFrown")')
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), c='setFace("setMouth")')
	cmds.setParent(u=True)
	cmds.setParent(u=True)
	cmds.showWindow('facePreset')


def setFace(num):
	eyeBrowList = ['BrowsD_L', 'BrowsD_R', 'BrowsU_C', 'BrowsU_L', 'BrowsU_R']
	eyeList = ['EyeBlink_L', 'EyeBlink_R', 'EyeOpen_L', 'EyeOpen_R', 'CheekSquint_L', 'CheekSquint_R']
	mouthList = ['LipsFunnel', 'LipsLowerClose', 'LipsLowerDown', 'LipsLowerOpen', 'LipsPucker',
				 'LipsStretch_L', 'LipsStretch_R', 'LipsUpperClose',  'LipsUpperUp',
				 'ChinUpperRaise',  'ChinLowerRaise',
				 'MouthDimple_L', 'MouthDimple_R', 'MouthFrown_L', 'MouthFrown_R', 'MouthLeft',
				 'MouthRight', 'MouthSmile_L', 'MouthSmile_R',
				 'Puff', 'Sneer', 'JawFwd', 'JawOpen', 'JawLeft', 'JawRight']

	newFace = ['__Smile', '__EyeSmile', '__miso', '__misoOpen', '__bigOpen']
	faceAll = eyeBrowList+eyeList+mouthList

	sel = cmds.ls(sl=True)
	selSplit = sel[0].split(':')
	selFace = '__Facial_List__'
	face_preset = []
	
	if num == 'L_BrowDefault':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsD_L', 0)
		cmds.setAttr(selFace + '.BrowsU_L', 0)

	elif num == 'R_BrowDefault':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsD_R', 0)
		cmds.setAttr(selFace + '.BrowsU_R', 0)
						
	elif num == 'L_BrowUp':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsD_L', 0)
		cmds.setAttr(selFace + '.BrowsU_L', 1)

	elif num == 'R_BrowUp':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsD_R', 0)
		cmds.setAttr(selFace + '.BrowsU_R', 1)

	elif num == 'L_BrowDown':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsU_L', 0)
		cmds.setAttr(selFace + '.BrowsD_L', 1)
			
	elif num == 'R_BrowDown':
		cmds.setAttr(selFace + '.BrowsU_C', 0)
		cmds.setAttr(selFace + '.BrowsU_R', 0)
		cmds.setAttr(selFace + '.BrowsD_R', 1)

	elif num == 'C_BrowUp':
		cmds.setAttr(selFace + '.BrowsU_C', 1)

	elif num == 'C_BrowDown':
		cmds.setAttr(selFace + '.BrowsU_C', -1)
											
	elif num == 'TwoEyeOpen':
		cmds.setAttr(selFace + '.EyeOpen_L', 0)
		cmds.setAttr(selFace + '.EyeBlink_L', 0)
		cmds.setAttr(selFace + '.EyeOpen_R', 0)
		cmds.setAttr(selFace + '.EyeBlink_R', 0)

	elif num == 'TwoEyeClose':
		cmds.setAttr(selFace + '.EyeOpen_L', 0)
		cmds.setAttr(selFace + '.EyeBlink_L', 1)
		cmds.setAttr(selFace + '.EyeOpen_R', 0)
		cmds.setAttr(selFace + '.EyeBlink_R', 1)
		
	elif num == 'eyeDefault_L':
		cmds.setAttr(selFace + '.EyeOpen_L', 0)
		cmds.setAttr(selFace + '.EyeBlink_L', 0)
		
	elif num == 'eyeDefault_R':
		cmds.setAttr(selFace + '.EyeOpen_R', 0)
		cmds.setAttr(selFace + '.EyeBlink_R', 0)

	elif num == 'eyeBlink_L':
		cmds.setAttr(selFace + '.EyeOpen_L', 0)
		cmds.setAttr(selFace + '.EyeBlink_L', 1)

	elif num == 'eyeBlink_R':
		cmds.setAttr(selFace + '.EyeOpen_R', 0)
		cmds.setAttr(selFace + '.EyeBlink_R', 1)
		
	elif num == 'eyeTired_L':
		cmds.setAttr(selFace + '.EyeOpen_L', 0)
		cmds.setAttr(selFace + '.EyeBlink_L', 0.3)
		
	elif num == 'eyeTired_R':
		cmds.setAttr(selFace + '.EyeOpen_R', 0)
		cmds.setAttr(selFace + '.EyeBlink_R', 0.3)
	
	elif num == 'eyeOpen_L':
		cmds.setAttr(selFace + '.EyeBlink_L', 0)
		cmds.setAttr(selFace + '.EyeOpen_L', 1)

	elif num == 'eyeOpen_R':
		cmds.setAttr(selFace + '.EyeBlink_R', 0)
		cmds.setAttr(selFace + '.EyeOpen_R', 1)
	
	elif num == 'MouthDefault':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)

	elif num == 'MouthAh':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.JawOpen', 0.7)
	
	elif num == 'MouthAE':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.JawOpen', 0.4)
		cmds.setAttr(selFace + '.MouthDimple_L', 0.6)
		cmds.setAttr(selFace + '.MouthDimple_R', 0.6)
		
	elif num == 'MouthEE':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.JawOpen', 0.2)
		cmds.setAttr(selFace + '.LipsStretch_L', 1)
		cmds.setAttr(selFace + '.LipsStretch_R', 1)
		cmds.setAttr(selFace + '.MouthDimple_L', 0.3)
		cmds.setAttr(selFace + '.MouthDimple_R', 0.3)
		
	elif num == 'MouthOh':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.LipsPucker', 1)
		cmds.setAttr(selFace + '.JawOpen', 0.5)

	elif num == 'MouthUh':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.LipsPucker', 1)

	elif num == 'MouthEU':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.JawOpen', 0.15)
		cmds.setAttr(selFace + '.LipsStretch_L', 0.7)
		cmds.setAttr(selFace + '.LipsStretch_R', 0.7)
		cmds.setAttr(selFace + '.MouthFrown_L', 0.4)
		cmds.setAttr(selFace + '.MouthFrown_R', 0.4)

	elif num == 'MouthOpen':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.JawOpen', 1)
	
	elif num == 'MouthClose':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		
	elif num == 'MouthSmile':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.MouthSmile_L', 1)
		cmds.setAttr(selFace + '.MouthSmile_R', 1)

	elif num == 'MouthFrown':
		for x in mouthList:
			cmds.setAttr(selFace + '.' + x, 0)
		cmds.setAttr(selFace + '.MouthFrown_L', 1)
		cmds.setAttr(selFace + '.MouthFrown_R', 1)

	elif num == '_Default':
		for x in faceAll:
			cmds.setAttr(selFace + '.' + x, 0)
		for y in newFace:
			cmds.setAttr(selFace + '.' + y, 0)
		
	elif num == '_Smile':
		for x in faceAll:
			cmds.setAttr(selFace + '.' + x, 0)
		for y in newFace:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(selFace + '.' + y, 0)
		cmds.setAttr(selFace + '.__Smile', 1)

	elif num == '_EyeSmile_Open':
		cmds.setAttr(selFace + '.__EyeSmile', 0)
		
	elif num == '_EyeSmile':
		cmds.setAttr(selFace + '.__EyeSmile', 1)

	elif num == '_Miso':
		for x in faceAll:
			cmds.setAttr(selFace + '.' + x, 0)
		for y in newFace:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(selFace + '.' + y, 0)
		cmds.setAttr(selFace + '.__miso', 1)

	elif num == '_MisoOpen':
		for x in faceAll:
			cmds.setAttr(selFace + '.' + x, 0)
		for y in newFace:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(selFace + '.' + y, 0)
		cmds.setAttr(selFace + '.__misoOpen', 1)

	elif num == '_BigOpen':
		for x in faceAll:
			cmds.setAttr(selFace + '.' + x, 0)
		for y in newFace:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(selFace + '.' + y, 0)
		cmds.setAttr(selFace + '.__bigOpen', 1)

	elif num == 'setEyeBrow':
		for x in eyeBrowList:
			cmds.setKeyframe(selFace, at=x)

	elif num == 'setEye':
		for x in eyeList:
			cmds.setKeyframe(selFace, at=x)

	elif num == 'setMouth':
		for x in mouthList:
			cmds.setKeyframe(selFace, at=x)

	elif num == 'setNewFace':
		for x in newFace:
			cmds.setKeyframe(selFace, at=x)
	else:
		pass

	# face_preset != []
	if face_preset is not []:
		cmds.setAttr(selFace + '.BrowsD_L', face_preset[0])
		cmds.setAttr(selFace + '.BrowsD_R', face_preset[1])
		cmds.setAttr(selFace + '.BrowsU_C', face_preset[2])
		cmds.setAttr(selFace + '.BrowsU_L', face_preset[3])
		cmds.setAttr(selFace + '.BrowsU_R', face_preset[4])
		cmds.setAttr(selFace + '.EyeBlink_L', face_preset[5])
		cmds.setAttr(selFace + '.EyeBlink_R', face_preset[6])
		cmds.setAttr(selFace + '.CheekSquint_L', face_preset[7])
		cmds.setAttr(selFace + '.CheekSquint_R', face_preset[8])
		cmds.setAttr(selFace + '.LipsFunnel', face_preset[9])
		cmds.setAttr(selFace + '.LipsLowerClose', face_preset[10])
		cmds.setAttr(selFace + '.LipsLowerDown', face_preset[11])
		cmds.setAttr(selFace + '.LipsLowerOpen', face_preset[12])
		cmds.setAttr(selFace + '.LipsPucker', face_preset[13])
		cmds.setAttr(selFace + '.LipsStretch_L', face_preset[14])
		cmds.setAttr(selFace + '.LipsStretch_R', face_preset[15])
		cmds.setAttr(selFace + '.LipsUpperClose', face_preset[16])
		cmds.setAttr(selFace + '.LipsUpperUp', face_preset[17])
		cmds.setAttr(selFace + '.ChinUpperRaise', face_preset[18])
		cmds.setAttr(selFace + '.ChinLowerRaise', face_preset[19])
		cmds.setAttr(selFace + '.MouthDimple_L', face_preset[20])
		cmds.setAttr(selFace + '.MouthDimple_R', face_preset[21])
		cmds.setAttr(selFace + '.MouthFrown_L', face_preset[22])
		cmds.setAttr(selFace + '.MouthFrown_R', face_preset[23])
		cmds.setAttr(selFace + '.MouthLeft', face_preset[24])
		cmds.setAttr(selFace + '.MouthRight', face_preset[25])
		cmds.setAttr(selFace + '.MouthSmile_L', face_preset[26])
		cmds.setAttr(selFace + '.MouthSmile_R', face_preset[27])
		cmds.setAttr(selFace + '.Puff', face_preset[28])
		cmds.setAttr(selFace + '.Sneer', face_preset[29])
		cmds.setAttr(selFace + '.JawFwd', face_preset[30])
		cmds.setAttr(selFace + '.JawOpen', face_preset[31])
		cmds.setAttr(selFace + '.JawLeft', face_preset[32])
		cmds.setAttr(selFace + '.JawRight', face_preset[33])
	else:
		pass


if __name__ == '__main__':
	facePresetUI()
	
