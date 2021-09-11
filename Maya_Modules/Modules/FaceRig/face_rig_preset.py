# -*- coding utf-8 -*-

import maya.cmds as cmds
from functools import partial

kWindowName = 'facePreset'


def face_preset_window():
	if cmds.window(kWindowName, ex=True):
		cmds.deleteUI(kWindowName)
	
	cmds.window(kWindowName, wh=(100, 100), sizeable=True)
	cmds.columnLayout(adjustableColumn=True)
	cmds.gridLayout(numberOfColumns=6, cellWidthHeight=(100, 405))
	
	cmds.frameLayout(label='EYE Brow', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='L_Brow_Default', h=30, command=partial(set_face, "L_BrowDefault"))
	cmds.button(label='R_Brow_Default', h=30, command=partial(set_face, "R_BrowDefault"))
	cmds.button(label='L_Brow_Up', h=30, command=partial(set_face, "L_BrowUp"))
	cmds.button(label='R_Brow_Up', h=30, command=partial(set_face, "R_BrowUp"))
	cmds.button(label='L_Brow_Down', h=30, command=partial(set_face, "L_BrowDown"))
	cmds.button(label='R_Brow_Down', h=30, command=partial(set_face, "R_BrowDown"))
	cmds.button(label='C_Brow_Up', h=30, command=partial(set_face, "C_BrowUp"))
	cmds.button(label='C_Brow_Down', h=30, command=partial(set_face, "C_BrowDown"))
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), command=partial(set_face, "setEyeBrow"))
	cmds.setParent(u=True)
		
	cmds.frameLayout(label='EYE', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='Two_EYE_Open', h=30, command=partial(set_face, "TwoEyeOpen"))
	cmds.button(label='Two_EYE_Close', h=30, command=partial(set_face, "TwoEyeClose"))
	cmds.button(label='L_EYE_Open', h=30, command=partial(set_face, "eyeDefault_L"))
	cmds.button(label='R_EYE_Open', h=30, command=partial(set_face, "eyeDefault_R"))
	cmds.button(label='L_EYE_Close', h=30, command=partial(set_face, "eyeBlink_L"))
	cmds.button(label='R_EYE_Close', h=30, command=partial(set_face, "eyeBlink_R"))
	cmds.button(label='L_EYE_Tired', h=30, command=partial(set_face, "eyeTired_L"))
	cmds.button(label='R_EYE_Tired', h=30, command=partial(set_face, "eyeTired_R"))
	cmds.button(label='L_EYE_Big_Open', h=30, command=partial(set_face, "eyeOpen_L"))
	cmds.button(label='R_EYE_Big_Open', h=30, command=partial(set_face, "eyeOpen_R"))
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), command=partial(set_face, "setEye"))
	cmds.setParent(u=True)

	cmds.frameLayout(label='Mouth', h=405)
	cmds.columnLayout(adjustableColumn=True, h=405)
	cmds.button(label='Mouth Default', h=30, command=partial(set_face, "MouthDefault"))
	cmds.button(label='Mouth Ah~', h=30, command=partial(set_face, "MouthAh"))
	cmds.button(label='Mouth AE~', h=30, command=partial(set_face, "MouthAE"))
	cmds.button(label='Mouth EE~', h=30, command=partial(set_face, "MouthEE"))
	cmds.button(label='Mouth Oh~', h=30, command=partial(set_face, "MouthOh"))
	cmds.button(label='Mouth Uh~', h=30, command=partial(set_face, "MouthUh"))
	cmds.button(label='Mouth EU~', h=30, command=partial(set_face, "MouthEU"))
	cmds.button(label='Mouth Open', h=30, command=partial(set_face, "MouthOpen"))
	cmds.button(label='Mouth Close', h=30, command=partial(set_face, "MouthClose"))
	cmds.button(label='Mouth Smile', h=30, command=partial(set_face, "MouthSmile"))
	cmds.button(label='Mouth Frown', h=30, command=partial(set_face, "MouthFrown"))
	cmds.setParent(u=True)
	cmds.button(label='Set Key', h=30, bgc=(0.8, 0.2, 0.2), command=partial(set_face, "setMouth"))
	cmds.setParent(u=True)
	cmds.setParent(u=True)
	cmds.showWindow('facePreset')


def set_face(num):
	eye_brow_list = ['BrowsD_L', 'BrowsD_R', 'BrowsU_C', 'BrowsU_L', 'BrowsU_R']
	eye_list = ['EyeBlink_L', 'EyeBlink_R', 'EyeOpen_L', 'EyeOpen_R', 'CheekSquint_L', 'CheekSquint_R']
	mouth_list = ['LipsFunnel', 'LipsLowerClose', 'LipsLowerDown', 'LipsLowerOpen', 'LipsPucker',
				 'LipsStretch_L', 'LipsStretch_R', 'LipsUpperClose',  'LipsUpperUp',
				 'ChinUpperRaise',  'ChinLowerRaise',
				 'MouthDimple_L', 'MouthDimple_R', 'MouthFrown_L', 'MouthFrown_R', 'MouthLeft',
				 'MouthRight', 'MouthSmile_L', 'MouthSmile_R',
				 'Puff', 'Sneer', 'JawFwd', 'JawOpen', 'JawLeft', 'JawRight']

	new_face = ['__Smile', '__EyeSmile', '__miso', '__misoOpen', '__bigOpen']
	face_all = eye_brow_list+eye_list+mouth_list

	sel = cmds.ls(sl=True)
	sel_split = sel[0].split(':')
	sel_face = '__Facial_List__'
	face_preset = []
	
	if num == 'L_BrowDefault':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsD_L', 0)
		cmds.setAttr(sel_face + '.BrowsU_L', 0)

	elif num == 'R_BrowDefault':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsD_R', 0)
		cmds.setAttr(sel_face + '.BrowsU_R', 0)
						
	elif num == 'L_BrowUp':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsD_L', 0)
		cmds.setAttr(sel_face + '.BrowsU_L', 1)

	elif num == 'R_BrowUp':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsD_R', 0)
		cmds.setAttr(sel_face + '.BrowsU_R', 1)

	elif num == 'L_BrowDown':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsU_L', 0)
		cmds.setAttr(sel_face + '.BrowsD_L', 1)
			
	elif num == 'R_BrowDown':
		cmds.setAttr(sel_face + '.BrowsU_C', 0)
		cmds.setAttr(sel_face + '.BrowsU_R', 0)
		cmds.setAttr(sel_face + '.BrowsD_R', 1)

	elif num == 'C_BrowUp':
		cmds.setAttr(sel_face + '.BrowsU_C', 1)

	elif num == 'C_BrowDown':
		cmds.setAttr(sel_face + '.BrowsU_C', -1)
											
	elif num == 'TwoEyeOpen':
		cmds.setAttr(sel_face + '.EyeOpen_L', 0)
		cmds.setAttr(sel_face + '.EyeBlink_L', 0)
		cmds.setAttr(sel_face + '.EyeOpen_R', 0)
		cmds.setAttr(sel_face + '.EyeBlink_R', 0)

	elif num == 'TwoEyeClose':
		cmds.setAttr(sel_face + '.EyeOpen_L', 0)
		cmds.setAttr(sel_face + '.EyeBlink_L', 1)
		cmds.setAttr(sel_face + '.EyeOpen_R', 0)
		cmds.setAttr(sel_face + '.EyeBlink_R', 1)
		
	elif num == 'eyeDefault_L':
		cmds.setAttr(sel_face + '.EyeOpen_L', 0)
		cmds.setAttr(sel_face + '.EyeBlink_L', 0)
		
	elif num == 'eyeDefault_R':
		cmds.setAttr(sel_face + '.EyeOpen_R', 0)
		cmds.setAttr(sel_face + '.EyeBlink_R', 0)

	elif num == 'eyeBlink_L':
		cmds.setAttr(sel_face + '.EyeOpen_L', 0)
		cmds.setAttr(sel_face + '.EyeBlink_L', 1)

	elif num == 'eyeBlink_R':
		cmds.setAttr(sel_face + '.EyeOpen_R', 0)
		cmds.setAttr(sel_face + '.EyeBlink_R', 1)
		
	elif num == 'eyeTired_L':
		cmds.setAttr(sel_face + '.EyeOpen_L', 0)
		cmds.setAttr(sel_face + '.EyeBlink_L', 0.3)
		
	elif num == 'eyeTired_R':
		cmds.setAttr(sel_face + '.EyeOpen_R', 0)
		cmds.setAttr(sel_face + '.EyeBlink_R', 0.3)
	
	elif num == 'eyeOpen_L':
		cmds.setAttr(sel_face + '.EyeBlink_L', 0)
		cmds.setAttr(sel_face + '.EyeOpen_L', 1)

	elif num == 'eyeOpen_R':
		cmds.setAttr(sel_face + '.EyeBlink_R', 0)
		cmds.setAttr(sel_face + '.EyeOpen_R', 1)
	
	elif num == 'MouthDefault':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)

	elif num == 'MouthAh':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.JawOpen', 0.7)
	
	elif num == 'MouthAE':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.JawOpen', 0.4)
		cmds.setAttr(sel_face + '.MouthDimple_L', 0.6)
		cmds.setAttr(sel_face + '.MouthDimple_R', 0.6)
		
	elif num == 'MouthEE':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.JawOpen', 0.2)
		cmds.setAttr(sel_face + '.LipsStretch_L', 1)
		cmds.setAttr(sel_face + '.LipsStretch_R', 1)
		cmds.setAttr(sel_face + '.MouthDimple_L', 0.3)
		cmds.setAttr(sel_face + '.MouthDimple_R', 0.3)
		
	elif num == 'MouthOh':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.LipsPucker', 1)
		cmds.setAttr(sel_face + '.JawOpen', 0.5)

	elif num == 'MouthUh':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.LipsPucker', 1)

	elif num == 'MouthEU':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.JawOpen', 0.15)
		cmds.setAttr(sel_face + '.LipsStretch_L', 0.7)
		cmds.setAttr(sel_face + '.LipsStretch_R', 0.7)
		cmds.setAttr(sel_face + '.MouthFrown_L', 0.4)
		cmds.setAttr(sel_face + '.MouthFrown_R', 0.4)

	elif num == 'MouthOpen':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.JawOpen', 1)
	
	elif num == 'MouthClose':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		
	elif num == 'MouthSmile':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.MouthSmile_L', 1)
		cmds.setAttr(sel_face + '.MouthSmile_R', 1)

	elif num == 'MouthFrown':
		for x in mouth_list:
			cmds.setAttr(sel_face + '.' + x, 0)
		cmds.setAttr(sel_face + '.MouthFrown_L', 1)
		cmds.setAttr(sel_face + '.MouthFrown_R', 1)

	elif num == '_Default':
		for x in face_all:
			cmds.setAttr(sel_face + '.' + x, 0)
		for y in new_face:
			cmds.setAttr(sel_face + '.' + y, 0)
		
	elif num == '_Smile':
		for x in face_all:
			cmds.setAttr(sel_face + '.' + x, 0)
		for y in new_face:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(sel_face + '.' + y, 0)
		cmds.setAttr(sel_face + '.__Smile', 1)

	elif num == '_EyeSmile_Open':
		cmds.setAttr(sel_face + '.__EyeSmile', 0)
		
	elif num == '_EyeSmile':
		cmds.setAttr(sel_face + '.__EyeSmile', 1)

	elif num == '_Miso':
		for x in face_all:
			cmds.setAttr(sel_face + '.' + x, 0)
		for y in new_face:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(sel_face + '.' + y, 0)
		cmds.setAttr(sel_face + '.__miso', 1)

	elif num == '_MisoOpen':
		for x in face_all:
			cmds.setAttr(sel_face + '.' + x, 0)
		for y in new_face:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(sel_face + '.' + y, 0)
		cmds.setAttr(sel_face + '.__misoOpen', 1)

	elif num == '_BigOpen':
		for x in face_all:
			cmds.setAttr(sel_face + '.' + x, 0)
		for y in new_face:
			if y == '__EyeSmile':
				pass
			else:
				cmds.setAttr(sel_face + '.' + y, 0)
		cmds.setAttr(sel_face + '.__bigOpen', 1)

	elif num == 'setEyeBrow':
		for x in eye_brow_list:
			cmds.setKeyframe(sel_face, at=x)

	elif num == 'setEye':
		for x in eye_list:
			cmds.setKeyframe(sel_face, at=x)

	elif num == 'setMouth':
		for x in mouth_list:
			cmds.setKeyframe(sel_face, at=x)

	elif num == 'setNewFace':
		for x in new_face:
			cmds.setKeyframe(sel_face, at=x)
	else:
		pass

	# face_preset != []
	if face_preset is not []:
		cmds.setAttr(sel_face + '.BrowsD_L', face_preset[0])
		cmds.setAttr(sel_face + '.BrowsD_R', face_preset[1])
		cmds.setAttr(sel_face + '.BrowsU_C', face_preset[2])
		cmds.setAttr(sel_face + '.BrowsU_L', face_preset[3])
		cmds.setAttr(sel_face + '.BrowsU_R', face_preset[4])
		cmds.setAttr(sel_face + '.EyeBlink_L', face_preset[5])
		cmds.setAttr(sel_face + '.EyeBlink_R', face_preset[6])
		cmds.setAttr(sel_face + '.CheekSquint_L', face_preset[7])
		cmds.setAttr(sel_face + '.CheekSquint_R', face_preset[8])
		cmds.setAttr(sel_face + '.LipsFunnel', face_preset[9])
		cmds.setAttr(sel_face + '.LipsLowerClose', face_preset[10])
		cmds.setAttr(sel_face + '.LipsLowerDown', face_preset[11])
		cmds.setAttr(sel_face + '.LipsLowerOpen', face_preset[12])
		cmds.setAttr(sel_face + '.LipsPucker', face_preset[13])
		cmds.setAttr(sel_face + '.LipsStretch_L', face_preset[14])
		cmds.setAttr(sel_face + '.LipsStretch_R', face_preset[15])
		cmds.setAttr(sel_face + '.LipsUpperClose', face_preset[16])
		cmds.setAttr(sel_face + '.LipsUpperUp', face_preset[17])
		cmds.setAttr(sel_face + '.ChinUpperRaise', face_preset[18])
		cmds.setAttr(sel_face + '.ChinLowerRaise', face_preset[19])
		cmds.setAttr(sel_face + '.MouthDimple_L', face_preset[20])
		cmds.setAttr(sel_face + '.MouthDimple_R', face_preset[21])
		cmds.setAttr(sel_face + '.MouthFrown_L', face_preset[22])
		cmds.setAttr(sel_face + '.MouthFrown_R', face_preset[23])
		cmds.setAttr(sel_face + '.MouthLeft', face_preset[24])
		cmds.setAttr(sel_face + '.MouthRight', face_preset[25])
		cmds.setAttr(sel_face + '.MouthSmile_L', face_preset[26])
		cmds.setAttr(sel_face + '.MouthSmile_R', face_preset[27])
		cmds.setAttr(sel_face + '.Puff', face_preset[28])
		cmds.setAttr(sel_face + '.Sneer', face_preset[29])
		cmds.setAttr(sel_face + '.JawFwd', face_preset[30])
		cmds.setAttr(sel_face + '.JawOpen', face_preset[31])
		cmds.setAttr(sel_face + '.JawLeft', face_preset[32])
		cmds.setAttr(sel_face + '.JawRight', face_preset[33])
	else:
		pass


if __name__ == '__main__':
	face_preset_window()
	
