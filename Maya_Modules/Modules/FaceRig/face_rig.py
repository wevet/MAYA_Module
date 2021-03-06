# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import re
import pickle
import sys
from functools import partial

vw_right_curve = []
vw_center_curve = []
vw_left_curve = []
vw_show_cluster = []
vw_hide_cluster = []
vw_face_select_cluster = []
vw_head_object = ' '
vw_face_emotion_data = []
vw_select_item_index = [1]
vw_select_cluster_pos_temp = []
vw_source_mesh = ' '
vw_target_mesh = ' '
vw_file_temp = []
vw_face_button_num = False

path_original = sys.path
vw_path = ''
path_original = cmds.internalVar(usd=True)
vw_path = path_original + 'FaceRig/Facial_Check/'
vw_select_right_curve = 'R_Eyebrow', 'R_UpEye', 'R_LowEye', 'R_Zygoma', 'R_Nasolabial', 'R_Cheek', 'R_Jaw'
vw_select_center_curve = 'C_ForeHead', 'C_Eyebrow', 'C_UpLip', 'C_LowLip', 'C_FrontJaw', 'C_JawFull'
vw_select_left_curve = 'L_Eyebrow', 'L_UpEye', 'L_LowEye', 'L_Zygoma', 'L_Nasolabial', 'L_Cheek', 'L_Jaw'

vw_facial_list = \
    'BrowsD_L', \
    'BrowsD_R', \
    'BrowsU_C', \
    'BrowsU_L', \
    'BrowsU_R', \
    'EyeBlink_L', \
    'EyeBlink_R', \
    'EyeDown_L', \
    'EyeDown_R', \
    'EyeIn_L', \
    'EyeIn_R', \
    'EyeOpen_L', \
    'EyeOpen_R', \
    'EyeOut_L', \
    'EyeOut_R', \
    'EyeSquint_L', \
    'EyeSquint_R', \
    'EyeUp_L', \
    'EyeUp_R', \
    'CheekSquint_L', \
    'CheekSquint_R', \
    'LipsFunnel', \
    'LipsLowerClose', \
    'LipsLowerDown', \
    'LipsLowerOpen', \
    'LipsPucker', \
    'LipsStretch_L', \
    'LipsStretch_R', \
    'LipsUpperClose', \
    'LipsUpperUp', \
    'ChinUpperRaise', \
    'ChinLowerRaise', \
    'MouthDimple_L', \
    'MouthDimple_R', \
    'MouthFrown_L', \
    'MouthFrown_R', \
    'MouthLeft', \
    'MouthRight', \
    'MouthSmile_L', \
    'MouthSmile_R', \
    'Puff', \
    'Sneer', \
    'JawFwd', \
    'JawOpen', \
    'JawLeft', \
    'JawRight'

vw_facial_list_guide = {
    'BrowsD_L': 'Brows DownLeft',
    'BrowsD_R': 'Brows DownRight',
    'BrowsU_C': 'Brows UpCenter',
    'BrowsU_L': 'Brows UpLeft',
    'BrowsU_R': 'Brows UpRight',
    'CheekSquint_L': 'CheekSquint_L',
    'CheekSquint_R': 'CheekSquint_R',
    'EyeBlink_L': 'EyeBlink_L',
    'EyeBlink_R': 'EyeBlink_R',
    'EyeDown_L': 'EyeDown_L',
    'EyeDown_R': 'EyeDown_R',
    'EyeIn_L': 'EyeIn_L',
    'EyeIn_R': 'EyeIn_R',
    'EyeOpen_L': 'EyeOpen_L',
    'EyeOpen_R': 'EyeOpen_R',
    'EyeOut_L': 'EyeOut_L',
    'EyeOut_R': 'EyeOut_R',
    'EyeSquint_L': 'EyeSquint_L',
    'EyeSquint_R': 'EyeSquint_R',
    'EyeUp_L': 'EyeUp_L',
    'EyeUp_R': 'EyeUp_R',
    'JawFwd': 'JawFwd',
    'JawLeft': 'JawLeft',
    'JawOpen': 'JawOpen',
    'JawRight': 'JawRight',
    'LipsFunnel': 'LipsFunnel',
    'LipsLowerClose': 'LipsLowerClose',
    'LipsLowerDown': 'LipsLowerDown',
    'LipsLowerOpen': 'LipsLowerOpen',
    'LipsPucker': 'LipsPucker',
    'LipsStretch_L': 'LipsStretch_L',
    'LipsStretch_R': 'LipsStretch_R',
    'LipsUpperClose': 'LipsUpperClose',
    'LipsUpperUp': 'LipsUpperUp',
    'MouthDimple_L': 'MouthDimple_L',
    'MouthDimple_R': 'MouthDimple_R',
    'MouthFrown_L': 'MouthFrown_L',
    'MouthFrown_R': 'MouthFrown_R',
    'MouthLeft': 'MouthLeft',
    'MouthRight': 'MouthRight',
    'MouthSmile_L': 'MouthSmile_L',
    'MouthSmile_R': 'MouthSmile_R',
    'Puff': 'Puff',
    'Sneer': 'Sneer',
    'ChinUpperRaise': 'ChinUpperRaise',
    'ChinLowerRaise': 'ChinLowerRaise'}


kFacialCreateWindow = 'facialCreateWindow'
kFacialEditWindow = 'facialEditWindow'
kFacialControlWindow = 'facialControlWindow'
kFacialCopyModeWindow = 'copyModeWindow'
kCreateLeftCurveWindow = 'createLeftCurveWindow'
kCreateCenterCurveWindow = 'createCenterCurveWindow'
kCreateRightCurveWindow = 'createRightCurveWindow'


def facial_set_create_mode_window(*args):
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object
    global vw_path
    global vw_face_select_cluster

    if cmds.window(kFacialCreateWindow, ex=True):
        cmds.deleteUI(kFacialCreateWindow)
    elif cmds.window(kFacialEditWindow, ex=True):
        cmds.deleteUI(kFacialEditWindow)
    elif cmds.window(kFacialControlWindow, ex=True):
        cmds.deleteUI(kFacialControlWindow)
    elif cmds.window(kFacialCopyModeWindow, ex=True):
        cmds.deleteUI(kFacialCopyModeWindow)

    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')

    cluster_filter()
    for x in vw_face_select_cluster:
        cmds.hide(x + 'Handle')

    cmds.window(kFacialCreateWindow, title='Facial Rig Tool', w=600, h=600, sizeable=False)
    cmds.columnLayout(columnAttach=('both', 1), rowSpacing=0, cal='center', columnWidth=600)
    cmds.image('imageViewField', w=500, h=500, i=vw_path + 'fs_createMode.jpg')
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2,
                   columnAlign=(1, 'center'),
                   columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text('')
    cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                        labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                        numberOfRadioButtons=4, h=50, sl=1,
                        on1=facial_set_create_mode_window, on2=facial_set_edit_mode_window,
                        on3=facial_set_control_mode_window, on4=copy_key_window)
    cmds.setParent(u=True)
    cmds.textFieldButtonGrp('selHead', label='Select Head Object ', tx=vw_head_object[0],
                            buttonLabel='<<<', h=50,
                            bc=set_head_in_button, ed=False)

    if vw_head_object != ' ':
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200), adjustableColumn=2,
                       columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        # Right
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='R I G H T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlRightList', append=vw_right_curve, sc=select_right_scroll_curve, h=130)
        cmds.button(label='Create Right Curve', h=40, command=partial(create_right_curve))
        cmds.setParent(u=True)
        # Center
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='C E N T E R', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlCenterList', append=vw_center_curve, sc=select_center_scroll_curve, h=130)
        cmds.button(label='Create Center Curve', h=40, command=partial(create_center_curve))
        cmds.setParent(u=True)
        # Left
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='L E F T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlLeftList', append=vw_left_curve, sc=select_left_scroll_curve, h=130)
        cmds.button(label='Create Left Curve', h=40, command=partial(create_left_curve))
        cmds.setParent(u=True)

        cmds.setParent(u=True)
        cmds.button(label='Attach Curve', h=60, command=partial(attach_command), bgc=(0.9, 0.3, 0.9))
        curve_exists()
    else:
        pass

    cmds.showWindow(kFacialCreateWindow)
    mel.eval('SelectToolOptionsMarkingMenu;\
    buildSelectMM;\
    global string $gSelect; setToolTo $gSelect;\
    selectToolValues nurbsSelect;\
    toolPropertyShow;\
    changeToolIcon;\
    SelectToolOptionsMarkingMenuPopDown;\
    MarkingMenuPopDown;')


def facial_set_edit_mode_window(*args):
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object
    global vw_face_select_cluster

    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')
    mel.eval('artAttrToolScript 3 "wire";')
    cluster_filter()

    for x in vw_face_select_cluster:
        cmds.hide(x + 'Handle')

    if vw_head_object != ' ':
        if cmds.window(kFacialCreateWindow, ex=True):
            cmds.deleteUI(kFacialCreateWindow)
        elif cmds.window(kFacialEditWindow, ex=True):
            cmds.deleteUI(kFacialEditWindow)
        elif cmds.window(kFacialControlWindow, ex=True):
            cmds.deleteUI(kFacialControlWindow)
        elif cmds.window(kFacialCopyModeWindow, ex=True):
            cmds.deleteUI(kFacialCopyModeWindow)

        cmds.window(kFacialEditWindow, title='Facial Set Tool', w=600, h=600, sizeable=False)
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=600)
        cmds.image('imageViewField', w=500, h=500, i=vw_path + 'fs_editMode.jpg')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        cmds.text('')
        cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                            labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                            numberOfRadioButtons=4, h=50, sl=2,
                            on1=facial_set_create_mode_window, on2=facial_set_edit_mode_window,
                            on3=facial_set_control_mode_window, on4=copy_key_window)
        cmds.setParent(u=True)

        cmds.textFieldButtonGrp('selHead', label='Select Head Object ', tx=vw_head_object[0],
                                buttonLabel='<<<', h=50, bc=set_head_in_button, ed=False, eb=False)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200),
                       adjustableColumn=2,
                       columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        # Right
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='R I G H T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlRightList', append=vw_right_curve, sc=select_right_scroll_edit_curve, h=130)
        cmds.setParent(u=True)
        # Center
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='C E N T E R', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlCenterList', append=vw_center_curve, sc=select_center_scroll_edit_curve, h=130)
        cmds.setParent(u=True)
        # Left
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='L E F T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlLeftList', append=vw_left_curve, sc=select_left_scroll_edit_curve, h=130)
        cmds.setParent(u=True)

        cmds.setParent(u=True)
        cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(300, 40))
        cmds.button('importMapField', label='Import Map', command=partial(import_map_image), h=40)
        cmds.button('exportMapField', label='Export Map', command=partial(export_map_image), h=40)
        cmds.setParent(u=True)
        cmds.button(label='Create Controller', h=60, command=partial(controller_command), bgc=(0.9, 0.3, 0.9))
        cmds.showWindow(kFacialEditWindow)
        curve_exists()
    else:
        facial_set_create_mode_window()


def facial_set_control_mode_window(*args):
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object
    global vw_facial_list
    global vw_face_select_cluster
    global vw_face_emotion_data
    global vw_select_item_index
    global vw_facial_list_guide

    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" false;')
    mel.eval('setObjectPickMask "Curve" false;')
    cluster_filter()
    all_curve = []
    num = 0

    for x in vw_face_select_cluster:
        cmds.hide(x + 'Handle')
    for x in vw_left_curve:
        all_curve.append(str(x))
        all_curve.append(str(vw_right_curve[num]))
        num += 1
    for x in vw_center_curve:
        all_curve.append(str(x))

    cmds.select(cl=True)
    if vw_head_object != ' ':
        if cmds.window(kFacialCreateWindow, ex=True):
            cmds.deleteUI(kFacialCreateWindow)
        elif cmds.window(kFacialEditWindow, ex=True):
            cmds.deleteUI(kFacialEditWindow)
        elif cmds.window(kFacialControlWindow, ex=True):
            cmds.deleteUI(kFacialControlWindow)
        elif cmds.window(kFacialCopyModeWindow, ex=True):
            cmds.deleteUI(kFacialCopyModeWindow)

        cmds.window(kFacialControlWindow, title='Facial Set Tool', w=600, h=600, sizeable=False)
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=600)
        cmds.image('imageViewField', w=500, h=500, i=vw_path + 'fs_controlMode.jpg')
        cmds.button('defaultFaceButtonField', label='default Face Image', h=30, aop=True,
                    command=partial(default_face_image))
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        cmds.text('')
        cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                            labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                            numberOfRadioButtons=4, h=50, sl=3,
                            on1=facial_set_create_mode_window,
                            on2=facial_set_edit_mode_window,
                            on3=facial_set_control_mode_window,
                            on4=copy_key_window)

        cmds.setParent(u=True)
        cmds.textFieldButtonGrp('selHead', label='Select Head Object ', tx=vw_head_object[0], buttonLabel='<<<', h=50,
                                bc=set_head_in_button, ed=False, eb=False)
        cmds.text('faceGuideField', label=vw_facial_list_guide.get('BrowsD_L'), h=50, fn='plainLabelFont', rs=True)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(240, 240, 110), adjustableColumn=3, columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])

        # FaceList
        cmds.columnLayout(columnAttach=('both', 1), rowSpacing=0, columnWidth=240)
        cmds.text(label='F A C E   L I S T', h=30, bgc=(0.3, 0.1, 0.1))
        cmds.textScrollList('facialControlFaceList', append=vw_facial_list, sc=select_face_scroll_control_curve, h=300,
                            sii=vw_select_item_index[0], bgc=(0.4, 0.3, 0.3))
        cmds.setParent(u=True)

        # Curve Ctrl
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=240)
        cmds.text(label='Curve Controller', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlList', append=all_curve, sc=select_scroll_control_curve, h=300, ams=True)
        cmds.setParent(u=True)

        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=110, h=333)
        cmds.text(label='SET Button', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.button(label='S E T', h=100, command=partial(control_mode_set), bgc=(0.5, 0, 0.0))
        cmds.button(label='copy', h=30, command=partial(copy_button), bgc=(0.4, 0.4, 0.4))
        cmds.gridLayout(numberOfColumns=3, cellWidthHeight=(36.7, 40))
        cmds.button(label='Pst', h=40, command=partial(paste_button), bgc=(0.4, 0.4, 0.4))
        cmds.button(label='CM', h=40, command=partial(copy_mirror_paste_button), bgc=(0.4, 0.4, 0.4))
        cmds.button(label='M', h=40, command=partial(mirror_paste_button), bgc=(0.4, 0.4, 0.4))
        cmds.setParent(u=True)

        cmds.text(label='File menu', h=30, bgc=(0.1, 0.1, 0.1))
        ##mc.button(label='All Reset',h=30,c=defaultSetButton)
        cmds.button(label='Select Reset', h=30, command=partial(select_reset_button))
        cmds.button(label='Import', h=30, command=partial(import_button))
        cmds.button(label='SAVE', h=50, command=partial(save_button), bgc=(0.9, 0.2, 0))
        cmds.setParent(u=True)
        cmds.setParent(u=True)

        cmds.button(label='Final Step', h=60, command=partial(final_step), bgc=(0.9, 0.3, 0.9))
        cmds.showWindow(kFacialControlWindow)

    else:
        facial_set_create_mode_window()

    select_face_scroll_control_curve()
    mel.eval('SelectToolOptionsMarkingMenu;\
    buildSelectMM;\
    global string $gSelect; setToolTo $gSelect;\
    selectToolValues nurbsSelect;\
    toolPropertyShow;\
    changeToolIcon;\
    SelectToolOptionsMarkingMenuPopDown;\
    MarkingMenuPopDown;')


def copy_key_window(*args):
    global vw_source_mesh
    global vw_target_mesh

    mel.eval('setObjectPickMask "Joint" true;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')

    if cmds.window(kFacialCreateWindow, ex=True):
        cmds.deleteUI(kFacialCreateWindow)
    elif cmds.window(kFacialEditWindow, ex=True):
        cmds.deleteUI(kFacialEditWindow)
    elif cmds.window(kFacialControlWindow, ex=True):
        cmds.deleteUI(kFacialControlWindow)
    elif cmds.window(kFacialCopyModeWindow, ex=True):
        cmds.deleteUI(kFacialCopyModeWindow)

    cmds.window(kFacialCopyModeWindow, title='Facial Set Tool', w=600, h=600, sizeable=False)
    cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=600)
    cmds.image('imageViewField', w=500, h=500, i=vw_path + 'fs_controlMode.jpg')
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'),
                   columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
    cmds.text('')
    cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                        labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                        numberOfRadioButtons=4, h=50, sl=4, on1=facial_set_create_mode_window, on2=facial_set_edit_mode_window,
                        on3=facial_set_control_mode_window, on4=copy_key_window)
    cmds.setParent(u=True)
    cmds.columnLayout(columnAttach=('both', 1), rowSpacing=0, columnWidth=600)

    if vw_source_mesh == ' ':
        cmds.textFieldButtonGrp('importSourceMeshField', label='Source Mesh', tx='', buttonLabel='<<<', h=50,
                                bc=import_source_mesh, ed=False, eb=True)
    else:
        cmds.textFieldButtonGrp('importSourceMeshField', label='Source Mesh', tx=vw_source_mesh, buttonLabel='<<<', h=50,
                                bc=import_source_mesh, ed=False, eb=True)

    if vw_target_mesh == ' ':
        cmds.textFieldButtonGrp('importTargetMeshField', label='Target Mesh', tx='', buttonLabel='<<<', h=50,
                                bc=import_target_mesh, ed=False, eb=True)
    else:
        cmds.textFieldButtonGrp('importTargetMeshField', label='Target Mesh', tx=vw_target_mesh, buttonLabel='<<<', h=50,
                                bc=import_target_mesh, ed=False, eb=True)

    if vw_source_mesh == ' ' or vw_target_mesh == ' ':
        cmds.button('copyKeyBtn', label='Copy Key', h=60, en=False,
                    command=partial(copy_key_process), bgc=(0.9, 0.3, 0.9))
    elif vw_source_mesh != ' ' and vw_target_mesh != ' ':
        cmds.button('copyKeyBtn', label='Copy Key', h=60, en=True,
                    command=partial(copy_key_process), bgc=(0.9, 0.3, 0.9))

    cmds.showWindow(kFacialCopyModeWindow)


def create_right_curve(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    
    if cmds.window(kCreateLeftCurveWindow, ex=True):
        cmds.deleteUI(kCreateLeftCurveWindow)
    if cmds.window(kCreateCenterCurveWindow, ex=True):
        cmds.deleteUI(kCreateCenterCurveWindow)
    if cmds.window(kCreateRightCurveWindow, ex=True):
        cmds.deleteUI(kCreateRightCurveWindow)

    cmds.window(kCreateRightCurveWindow, title='create Right Curve', w=250, h=350, sizeable=False)
    cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selRightCurveWin', append=vw_select_right_curve)

    for x in vw_select_right_curve:
        if cmds.objExists(x):
            cmds.textScrollList('selRightCurveWin', e=True, ri=x)
        else:
            pass
    cmds.button(label='O K ! !', h=60, command=partial(set_right_curve_window))
    cmds.showWindow(kCreateRightCurveWindow)


def set_right_curve_window(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object

    select_right_item = cmds.textScrollList('selRightCurveWin', q=True, si=True)
    side_edge_to_curve(select_right_item[0])
    vw_right_curve.sort()
    cmds.deleteUI(kCreateRightCurveWindow)
    curve_exists()


def create_center_curve(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve

    if cmds.window(kCreateLeftCurveWindow, ex=True):
        cmds.deleteUI(kCreateLeftCurveWindow)
    if cmds.window(kCreateCenterCurveWindow, ex=True):
        cmds.deleteUI(kCreateCenterCurveWindow)
    if cmds.window(kCreateRightCurveWindow, ex=True):
        cmds.deleteUI(kCreateRightCurveWindow)
    cmds.window(kCreateCenterCurveWindow, title='create Center Curve', w=250, h=350, sizeable=False)
    cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selCenterCurveWin', append=vw_select_center_curve)

    for x in vw_select_center_curve:
        if cmds.objExists(x):
            cmds.textScrollList('selCenterCurveWin', e=True, ri=x)
        else:
            pass
    cmds.button(label='O K ! !', h=60, command=partial(set_center_curve_list))
    cmds.showWindow(kCreateCenterCurveWindow)


def set_center_curve_list(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve

    select_center_item = cmds.textScrollList('selCenterCurveWin', q=True, si=True)
    center_edge_to_curve(select_center_item[0])
    vw_center_curve.sort()
    cmds.deleteUI(kCreateCenterCurveWindow)
    curve_exists()


def create_left_curve(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve

    if cmds.window(kCreateLeftCurveWindow, ex=True):
        cmds.deleteUI(kCreateLeftCurveWindow)
    if cmds.window(kCreateCenterCurveWindow, ex=True):
        cmds.deleteUI(kCreateCenterCurveWindow)
    if cmds.window(kCreateRightCurveWindow, ex=True):
        cmds.deleteUI(kCreateRightCurveWindow)

    cmds.window(kCreateLeftCurveWindow, title='create Left Curve', w=250, h=350, sizeable=False)
    cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selLeftCurveWin', append=vw_select_left_curve)

    for x in vw_select_left_curve:
        if cmds.objExists(x):
            cmds.textScrollList('selLeftCurveWin', e=True, ri=x)
        else:
            pass
    cmds.button(label='O K ! !', h=60, command=partial(set_left_curve_list))
    cmds.showWindow(kCreateLeftCurveWindow)


def set_left_curve_list(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve

    select_left_item = cmds.textScrollList('selLeftCurveWin', q=True, si=True)
    side_edge_to_curve(select_left_item[0])
    vw_left_curve.sort()
    cmds.deleteUI(kCreateLeftCurveWindow)
    curve_exists()


def curve_exists():
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve

    vw_right_curve = []
    vw_center_curve = []
    vw_left_curve = []

    cmds.select(all=True)
    all_curve = cmds.filterExpand(ex=True, sm=9)

    if all_curve is None:
        pass
    elif all_curve is not None:
        for x in vw_select_right_curve:
            for y in all_curve:
                if re.search(x + '$', y):
                    vw_right_curve.append(y)
        for x in vw_select_center_curve:
            for y in all_curve:
                if re.search(x + '$', y):
                    vw_center_curve.append(y)
        for x in vw_select_left_curve:
            for y in all_curve:
                if re.search(x + '$', y):
                    vw_left_curve.append(y)

    cmds.select(cl=True)
    cmds.textScrollList('facialControlRightList', e=True, ra=True)
    cmds.textScrollList('facialControlRightList', e=True, append=vw_right_curve)
    cmds.textScrollList('facialControlCenterList', e=True, ra=True)
    cmds.textScrollList('facialControlCenterList', e=True, append=vw_center_curve)
    cmds.textScrollList('facialControlLeftList', e=True, ra=True)
    cmds.textScrollList('facialControlLeftList', e=True, append=vw_left_curve)


def set_head_in_button(*args):
    global vw_head_object
    vw_head_object = cmds.ls(sl=True, fl=True)
    cmds.textFieldButtonGrp('selHead', e=True, tx=vw_head_object[0])
    facial_set_create_mode_window()


def center_edge_to_curve(curveName):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve

    # selVertex = cmds.ls(sl=True, fl=True)
    mel.eval('polyToCurve -n ' + curveName + ' -form 5 -degree 3;')
    cmds.select(curveName)
    cmds.rebuildCurve(curveName, ch=True, rpo=True, rt=0, end=0, kr=0, kcp=False, kep=False, kt=False, s=5, d=3)


def side_edge_to_curve(curveName):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_head_object
    centerX = cmds.objectCenter(vw_head_object[0], x=True)
    centerY = cmds.objectCenter(vw_head_object[0], y=True)
    centerZ = cmds.objectCenter(vw_head_object[0], z=True)
    # selVertex = cmds.ls(sl=True, fl=True)
    mel.eval('polyToCurve -n ' + curveName + ' -form 5 -degree 3;')
    cmds.select(curveName)
    cmds.rebuildCurve(curveName, ch=True, rpo=True, rt=0, end=0, kr=0, kcp=False, kep=False, kt=False, s=3, d=3)
    cmds.move(centerX, centerY, centerZ, curveName + '.scalePivot', curveName + '.rotatePivot', rpr=True, spr=True)


def select_right_scroll_curve(*args):
    select_right = cmds.textScrollList('facialControlRightList', q=True, si=True)
    cmds.textScrollList('facialControlCenterList', e=True, da=True)
    cmds.textScrollList('facialControlLeftList', e=True, da=True)
    cmds.select(select_right, r=True)


def select_center_scroll_curve(*args):
    select_center = cmds.textScrollList('facialControlCenterList', q=True, si=True)
    cmds.textScrollList('facialControlRightList', e=True, da=True)
    cmds.textScrollList('facialControlLeftList', e=True, da=True)
    cmds.select(select_center, r=True)


def select_left_scroll_curve(*args):
    select_left = cmds.textScrollList('facialControlLeftList', q=True, si=True)
    cmds.textScrollList('facialControlRightList', e=True, da=True)
    cmds.textScrollList('facialControlCenterList', e=True, da=True)
    cmds.select(select_left, r=True)


def attach_command(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object

    confirm_message = cmds.confirmDialog(title='Confirm', icn='question', message='Are you ok?',
                                    button=['Yes', 'No'],
                                    defaultButton='Yes',
                                    cancelButton='No',
                                    dismissString='No')

    if confirm_message == 'Yes':
        all_origin_curve = vw_select_right_curve + vw_select_center_curve + vw_select_left_curve
        all_curve = vw_right_curve + vw_center_curve + vw_left_curve

        for d in all_origin_curve:
            for x in all_curve:
                if d == x:
                    if re.search('R_', x):
                        curve_rename = 'L' + x[1:]
                        if cmds.objExists(curve_rename):
                            pass
                        else:
                            cmds.duplicate(x, n=curve_rename, rr=True)
                            cmds.scale(-1, 1, 1, curve_rename, r=True)
                    else:
                        pass

                    if re.search('L_', x):
                        curve_rename = 'R' + x[1:]
                        if cmds.objExists(curve_rename):
                            pass
                        else:
                            cmds.duplicate(x, n=curve_rename, rr=True)
                            cmds.scale(-1, 1, 1, curve_rename, r=True)

                    if re.match('C_', x):
                        pass
                else:
                    pass

        curve_exists()
        # allCurve = []
        # allCurve = vw_rightCurve + vw_leftCurve + vw_centerCurve
        cmds.select(vw_head_object)
        mel.eval('artAttrToolScript 3 "wire";')
        all_curve = vw_right_curve + vw_left_curve + vw_center_curve

        attach_progress_window = cmds.window(t='Attach Progress')
        cmds.columnLayout()
        progress_value = cmds.progressBar(maxValue=len(all_curve) - 1, width=300)
        cmds.showWindow(attach_progress_window)

        for x in all_curve:
            cmds.select(x)
            mel.eval('DeleteHistory;')
            mel.eval('CenterPivot;')
            cmds.wire(vw_head_object, w=x, n=x + '_wire')
            cmds.setAttr(x + '_wire' + '.dropoffDistance[0]', 100)
            cmds.setAttr(x + '_wire' + '.rotation', 0)
            cmds.select(vw_head_object)

            mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + x + '_wire.weights" )')
            mel.eval('artAttrPaintOperation artAttrCtx Replace;')
            mel.eval('artAttrCtx -e -value 0 `currentCtx`;')
            mel.eval('artAttrCtx -e -clear `currentCtx`;')
            mel.eval('artAttrCtx -e -value 1 `currentCtx`;')
            cmds.progressBar(progress_value, edit=True, step=1)

        cmds.deleteUI(attach_progress_window)
        mel.eval('SelectToolOptionsMarkingMenu;\
        buildSelectMM;\
        global string $gSelect; setToolTo $gSelect;\
        selectToolValues nurbsSelect;\
        toolPropertyShow;\
        changeToolIcon;\
        SelectToolOptionsMarkingMenuPopDown;\
        MarkingMenuPopDown;')

        facial_set_edit_mode_window()
    elif confirm_message == 'No':
        pass


def select_right_scroll_edit_curve(*args):
    global vw_head_object

    select_right = cmds.textScrollList('facialControlRightList', q=True, si=True)
    cmds.textScrollList('facialControlCenterList', e=True, da=True)
    cmds.textScrollList('facialControlLeftList', e=True, da=True)

    if cmds.objExists(select_right[0] + '_wire'):
        cmds.select(vw_head_object, select_right[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + select_right[0] + '_wire.weights" )')
    else:
        pass


def select_center_scroll_edit_curve(*args):
    global vw_head_object

    select_center = cmds.textScrollList('facialControlCenterList', q=True, si=True)
    cmds.textScrollList('facialControlRightList', e=True, da=True)
    cmds.textScrollList('facialControlLeftList', e=True, da=True)

    if cmds.objExists(select_center[0] + '_wire'):
        cmds.select(vw_head_object, select_center[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + select_center[0] + '_wire.weights" )')
    else:
        pass


def select_left_scroll_edit_curve(*args):
    global vw_head_object

    select_left = cmds.textScrollList('facialControlLeftList', q=True, si=True)
    cmds.textScrollList('facialControlRightList', e=True, da=True)
    cmds.textScrollList('facialControlCenterList', e=True, da=True)

    if cmds.objExists(select_left[0] + '_wire'):
        cmds.select(vw_head_object, select_left[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + select_left[0] + '_wire.weights" )')
    else:
        pass


def import_map_image(*args):
    # rightList = []
    # centerList = []
    # leftList = []

    all_list = []
    right_list = cmds.textScrollList('facialControlRightList', q=True, si=True)
    center_list = cmds.textScrollList('facialControlCenterList', q=True, si=True)
    left_list = cmds.textScrollList('facialControlLeftList', q=True, si=True)

    if right_list is not None:
        all_list.append(right_list)
    elif center_list is not None:
        all_list.append(center_list)
    elif left_list is not None:
        all_list.append(left_list)

    if all_list is []:
        pass
    else:
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + all_list[0][0] + '_wire.weights" );')
        mel.eval('artImportMapDialog "artAttrCtx";')


def export_map_image(*args):
    # rightList = []
    # centerList = []
    # leftList = []
    all_list = []

    right_list = cmds.textScrollList('facialControlRightList', q=True, si=True)
    center_list = cmds.textScrollList('facialControlCenterList', q=True, si=True)
    left_list = cmds.textScrollList('facialControlLeftList', q=True, si=True)

    if right_list is not None:
        all_list.append(right_list)
    elif center_list is not None:
        all_list.append(center_list)
    elif left_list is not None:
        all_list.append(left_list)

    if all_list is []:
        pass
    else:
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.' + all_list[0][0] + '_wire.weights" );')
        mel.eval('artExportMapValue "Luminance" artAttrCtx;')
        mel.eval('artExportFileTypeValue "JPEG" artAttrCtx;')
        mel.eval('artAttrCtx -e -exportfilesizex 4096 `currentCtx`;')
        mel.eval('artAttrCtx -e -exportfilesizey 4096 `currentCtx`;')
        mel.eval('artExportMapDialog "artAttrCtx";')


def controller_command(*args):
    global vw_select_right_curve
    global vw_select_center_curve
    global vw_select_left_curve
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_head_object

    confirm_message = cmds.confirmDialog(title='Confirm', icn='question', message='Are you ok?',
                                         button=['Yes', 'No'],
                                         defaultButton='Yes',
                                         cancelButton='No',
                                         dismissString='No')

    if confirm_message == 'Yes':
        all_curve = vw_right_curve + vw_center_curve + vw_left_curve
        # selTemp = []
        # stepNum = 1

        cluster_progress_window = cmds.window(t='cluster Progress')
        cmds.columnLayout()
        progress_value = cmds.progressBar(maxValue=len(all_curve) - 1, width=300)
        cmds.showWindow(cluster_progress_window)

        for x in all_curve:
            if re.search(vw_select_center_curve[-1] + '$', x):
                pass
            else:
                cmds.select(x + '.cv[0:]', r=True)
                sel = cmds.ls(sl=True, fl=True)
                for y in sel:
                    cmds.cluster(y, en=1, n=x)
                cmds.progressBar(progress_value, edit=True, step=1)

                '''
                if len(sel) <= limitNum:
                    for y in sel:
                        mc.cluster(y,en=1,n=x)              
                elif len(sel) > limitNum:
                    for z in sel:
                        selTemp.append(z)
                        if len(selTemp) == memberNum:
                            mc.cluster(selTemp,en=1,n=x)
                            selTemp = []
                        elif stepNum == 1:
                            mc.cluster(z,en=1,n=x)  
                        elif stepNum == len(sel):
                            mc.cluster(z,en=1,n=x)
                        else:
                            pass
                        stepNum += 1
                    stepNum = 1
                selTemp = []
                '''
        cmds.deleteUI(cluster_progress_window)
        facial_set_control_mode_window()

    if confirm_message == 'No':
        pass


def select_face_scroll_control_curve(*args):
    global vw_show_cluster
    global vw_face_select_cluster
    global vw_face_emotion_data
    global vw_select_item_index
    global vw_facial_list_guide
    global vw_center_curve
    global vw_select_center_curve

    vw_select_item_index = cmds.textScrollList('facialControlFaceList', q=True, sii=True)
    select_item = cmds.textScrollList('facialControlFaceList', q=True, si=True)
    int_num = vw_select_item_index[0] - 1
    step_num = 0

    if vw_face_emotion_data is []:
        default_set_button()

    elif vw_face_emotion_data[int_num] is not []:
        for x in vw_face_select_cluster:
            cmds.setAttr(x + 'Handle.translateX', vw_face_emotion_data[int_num][step_num][0])
            cmds.setAttr(x + 'Handle.translateY', vw_face_emotion_data[int_num][step_num][1])
            cmds.setAttr(x + 'Handle.translateZ', vw_face_emotion_data[int_num][step_num][2])
            step_num += 1

        for y in vw_center_curve:
            if re.search(vw_select_center_curve[-1] + '$', y):
                cmds.setAttr(y + '.translateX', vw_face_emotion_data[int_num][-1][0])
                cmds.setAttr(y + '.translateY', vw_face_emotion_data[int_num][-1][1])
                cmds.setAttr(y + '.translateZ', vw_face_emotion_data[int_num][-1][2])
                cmds.setAttr(y + '.rotateX', vw_face_emotion_data[int_num][-1][3])
                cmds.setAttr(y + '.rotateY', vw_face_emotion_data[int_num][-1][4])
                cmds.setAttr(y + '.rotateZ', vw_face_emotion_data[int_num][-1][5])
            else:
                pass

    face_guide_value = vw_facial_list_guide.get(select_item[0])
    cmds.text('faceGuideField', e=True, label=face_guide_value)
    cmds.image('imageViewField', e=True, i=vw_path + 'Facial_Check/' + select_item[0] + '.jpg')


def default_face_image(*args):
    global vw_face_button_num
    select_item = cmds.textScrollList('facialControlFaceList', q=True, si=True)

    if vw_face_button_num is False:
        cmds.image('imageViewField', e=True, i=vw_path + 'Facial_Check/defaultFace.jpg')
        vw_face_button_num = True

    elif vw_face_button_num is True:
        cmds.image('imageViewField', e=True, i=vw_path + 'Facial_Check/' + select_item[0] + '.jpg')
        vw_face_button_num = False


def control_mode_set(*args):
    global vw_show_cluster
    global vw_face_select_cluster
    global vw_face_emotion_data
    global vw_select_item_index
    global vw_center_curve
    global vw_file_temp
    global vw_facial_list

    vw_select_item_index = cmds.textScrollList('facialControlFaceList', q=True, sii=True)
    clear_all_pos = []

    fs = open('c:/Facial_temp.fd', 'wb')
    pickle.dump(vw_face_emotion_data, fs)
    fs.close()

    set_progress_window = cmds.window(t='Set Progress')
    cmds.columnLayout()
    progress_value = cmds.progressBar(maxValue=2500, width=300)
    cmds.showWindow(set_progress_window)

    if vw_face_emotion_data is []:
        default_set_button()
        for x in vw_face_select_cluster:
            # clPosition = []
            posX = cmds.getAttr(x + 'Handle.translateX')
            posY = cmds.getAttr(x + 'Handle.translateY')
            posZ = cmds.getAttr(x + 'Handle.translateZ')
            clPosition = [posX, posY, posZ]
            clear_all_pos.append(clPosition)

        for x in vw_center_curve:
            if re.search(vw_select_center_curve[-1] + '$', x):
                # clPosition = []
                jawPosX = cmds.getAttr(x + '.translateX')
                jawPosY = cmds.getAttr(x + '.translateY')
                jawPosZ = cmds.getAttr(x + '.translateZ')
                jawRotX = cmds.getAttr(x + '.rotateX')
                jawRotY = cmds.getAttr(x + '.rotateY')
                jawRotZ = cmds.getAttr(x + '.rotateZ')
                clPosition = [jawPosX, jawPosY, jawPosZ, jawRotX, jawRotY, jawRotZ]
                clear_all_pos.append(clPosition)
            else:
                pass

    elif vw_face_emotion_data is not []:
        for x in vw_face_select_cluster:
            # clPosition = []
            posX = cmds.getAttr(x + 'Handle.translateX')
            posY = cmds.getAttr(x + 'Handle.translateY')
            posZ = cmds.getAttr(x + 'Handle.translateZ')
            clPosition = [posX, posY, posZ]
            clear_all_pos.append(clPosition)

        for x in vw_center_curve:
            if re.search(vw_select_center_curve[-1] + '$', x):
                # clPosition = []
                jawPosX = cmds.getAttr(x + '.translateX')
                jawPosY = cmds.getAttr(x + '.translateY')
                jawPosZ = cmds.getAttr(x + '.translateZ')
                jawRotX = cmds.getAttr(x + '.rotateX')
                jawRotY = cmds.getAttr(x + '.rotateY')
                jawRotZ = cmds.getAttr(x + '.rotateZ')
                clPosition = [jawPosX, jawPosY, jawPosZ, jawRotX, jawRotY, jawRotZ]
                clear_all_pos.append(clPosition)
            else:
                pass

    vw_face_emotion_data[vw_select_item_index[0] - 1] = clear_all_pos
    for x in range(1500):
        cmds.progressBar(progress_value, edit=True, step=1)
    cmds.deleteUI(set_progress_window)

    if vw_file_temp is []:
        save_button()
    else:
        fs = open(vw_file_temp[:-3] + '_tmp.fd', 'wb')
        pickle.dump(vw_face_emotion_data, fs)
        fs.close()


def copy_button(*args):
    global vw_select_cluster_pos_temp
    vw_select_cluster_pos_temp = []
    # clPosition = []
    clear_all_pos = []
    select_cluster = cmds.ls(sl=True, fl=True)
    select_cluster.sort()

    for x in select_cluster:
        posX = cmds.getAttr(x + '.translateX')
        posY = cmds.getAttr(x + '.translateY')
        posZ = cmds.getAttr(x + '.translateZ')
        clear_position = [posX, posY, posZ]
        clear_all_pos.append(clear_position)
    vw_select_cluster_pos_temp = clear_all_pos


def paste_button(*args):
    global vw_select_cluster_pos_temp

    select_cluster = cmds.ls(sl=True, fl=True)
    select_cluster.sort()
    step_num = 0
    for x in select_cluster:
        cmds.setAttr(x + '.translateX', vw_select_cluster_pos_temp[step_num][0])
        cmds.setAttr(x + '.translateY', vw_select_cluster_pos_temp[step_num][1])
        cmds.setAttr(x + '.translateZ', vw_select_cluster_pos_temp[step_num][2])
        step_num += 1


def copy_mirror_paste_button(*args):
    global vw_select_cluster_pos_temp

    select_cluster = cmds.ls(sl=True, fl=True)
    select_cluster.sort()
    select_cluster.reverse()
    step_num = 0
    for x in select_cluster:
        cmds.setAttr(x + '.translateX', vw_select_cluster_pos_temp[step_num][0] * -1)
        cmds.setAttr(x + '.translateY', vw_select_cluster_pos_temp[step_num][1])
        cmds.setAttr(x + '.translateZ', vw_select_cluster_pos_temp[step_num][2])
        step_num += 1


def mirror_paste_button(*args):
    global vw_select_cluster_pos_temp

    select_cluster = cmds.ls(sl=True, fl=True)
    select_cluster.sort()
    step_num = 0
    for x in select_cluster:
        cmds.setAttr(x + '.translateX', vw_select_cluster_pos_temp[step_num][0] * -1)
        cmds.setAttr(x + '.translateY', vw_select_cluster_pos_temp[step_num][1])
        cmds.setAttr(x + '.translateZ', vw_select_cluster_pos_temp[step_num][2])
        step_num += 1


def default_set_button(*args):
    global vw_face_emotion_data

    vw_face_emotion_data = []
    pos_set = []
    cluster_set = []
    curve_set = []
    item_number = cmds.textScrollList('facialControlFaceList', q=True, ni=True)

    for z in range(3):
        pos_set.append(0.0)
    for y in range(len(vw_face_select_cluster)):
        cluster_set.append(pos_set)
    for a in range(6):
        curve_set.append(0.0)

    cluster_set.append(curve_set)
    for x in range(item_number):
        vw_face_emotion_data.append(cluster_set)


def select_reset_button(*args):
    global vw_show_cluster
    global vw_face_select_cluster
    global vw_face_emotion_data
    global vw_select_item_index
    global vw_facial_list_guide
    global vw_center_curve
    global vw_select_center_curve

    vw_select_item_index = cmds.textScrollList('facialControlFaceList', q=True, sii=True)
    # selectItem = cmds.textScrollList('facialControlFaceList', q=True, si=True)
    int_num = vw_select_item_index[0] - 1
    step_num = 0

    if vw_face_emotion_data is []:
        default_set_button()
    elif vw_face_emotion_data[int_num] is not []:
        for x in vw_face_select_cluster:
            cmds.setAttr(x + 'Handle.translateX', 0.0)
            cmds.setAttr(x + 'Handle.translateY', 0.0)
            cmds.setAttr(x + 'Handle.translateZ', 0.0)
            step_num += 1
        for y in vw_center_curve:
            if re.search(vw_select_center_curve[-1] + '$', y):
                cmds.setAttr(y + '.translateX', 0.0)
                cmds.setAttr(y + '.translateY', 0.0)
                cmds.setAttr(y + '.translateZ', 0.0)
                cmds.setAttr(y + '.rotateX', 0.0)
                cmds.setAttr(y + '.rotateY', 0.0)
                cmds.setAttr(y + '.rotateZ', 0.0)
            else:
                pass

    control_mode_set()


def import_button(*args):
    global vw_facial_list
    global vw_face_emotion_data
    global vw_face_select_cluster
    global vw_file_temp

    # fileData = []
    # fileTemp = []
    # convertTemp = []
    # stepNum = 0

    if vw_face_emotion_data is []:
        default_set_button()
    else:
        pass

    face_data_filters = 'Facial Data File (*.fd)'
    openfile_list = cmds.fileDialog2(cap='Import', fileMode=1, fileFilter=face_data_filters, dialogStyle=2)

    if openfile_list is None:
        print('no select file')
    else:
        openfilename = openfile_list[0]
        vw_file_temp = openfile_list[0]
        fo = open(openfilename, 'rb')
        vw_face_emotion_data = pickle.load(fo)
        fo.close()
        cmds.confirmDialog(title='Complete', icn="information", message='Import Complete!!',
                           button='ok',
                           defaultButton='ok')


def save_button(*args):
    global vw_facial_list
    global vw_face_emotion_data
    global vw_face_select_cluster
    global vw_file_temp

    face_data_filters = 'Facial Data File (*.fd)'
    save_file_list = cmds.fileDialog2(cap='SAVE', fileFilter=face_data_filters, dialogStyle=2)

    if save_file_list is None:
        print('no select file')
    else:
        save_file_name = save_file_list[0]
        vw_file_temp = save_file_list[0]
        fs = open(save_file_name, 'wb')
        pickle.dump(vw_face_emotion_data, fs)
        fs.close()
        cmds.confirmDialog(title='Complete', icn="information", message='Save Complete!!',
                           button='ok',
                           defaultButton='ok')


def select_scroll_control_curve(*args):
    global vw_head_object
    global vw_show_cluster
    global vw_hide_cluster
    global vw_face_select_cluster
    global vw_center_curve
    global vw_select_center_curve

    cluster_filter()
    select_jaw_curve = []
    select_curve_list = cmds.textScrollList('facialControlList', q=True, si=True)
    select_item_num = cmds.textScrollList('facialControlList', q=True, nsi=True)

    if vw_face_select_cluster is not []:
        if select_item_num > 1:
            cmds.select(cl=True)
            if select_jaw_curve is []:
                pass
            else:
                cmds.select(select_curve_list[0])

            for y in range(select_item_num):
                for x in vw_face_select_cluster:
                    if re.search('^' + select_curve_list[y], x):
                        vw_show_cluster.append(x + 'Handle')
                    else:
                        vw_hide_cluster.append(x + 'Handle')

            for z in vw_face_select_cluster:
                cmds.hide(z)
            for x in vw_show_cluster:
                cmds.showHidden(x)

        elif select_item_num == 1:
            vw_show_cluster = []
            vw_hide_cluster = []
            cmds.hide(vw_face_select_cluster)
            cmds.select(cl=True)

            if re.search(vw_select_center_curve[-1] + '$', select_curve_list[0]):
                cmds.select(select_curve_list[0])
                # selJawCurve = selCurveList[0]

            for x in vw_face_select_cluster:
                if re.search('^' + select_curve_list[0], x):
                    cmds.showHidden(x + 'Handle')
                else:
                    cmds.hide(x + 'Handle')

        elif select_item_num == 0:
            print('nothing Select item!!')
    else:
        pass


def cluster_filter():
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve
    global vw_face_select_cluster

    vw_face_select_cluster = []
    select_cluster = []
    all_cluster_name_source = vw_right_curve + vw_left_curve + vw_center_curve
    all_objects = cmds.ls(l=True)

    for obj in all_objects:
        if cmds.nodeType(obj) == 'cluster':
            select_cluster.append(obj)
    for x in all_cluster_name_source:
        for y in select_cluster:
            if re.search('^' + x, y):
                vw_face_select_cluster.append(y)
            else:
                pass


def final_step(*args):
    global vw_show_cluster
    global vw_face_select_cluster
    global vw_face_emotion_data
    global vw_select_item_index
    global vw_facial_list_guide
    global vw_facial_list
    global vw_head_object
    global vw_right_curve
    global vw_center_curve
    global vw_left_curve

    confirm_message = cmds.confirmDialog(title='Confirm', icn='question', message='Are you ok?',
                                    button=['Yes', 'No'],
                                    defaultButton='Yes',
                                    cancelButton='No',
                                    dismissString='No')

    if confirm_message == 'Yes':
        blend_shape_obj = []
        cmds.setAttr(vw_head_object[0] + '.tx', lock=False)
        cmds.setAttr(vw_head_object[0] + '.ty', lock=False)
        cmds.setAttr(vw_head_object[0] + '.tz', lock=False)
        cmds.setAttr(vw_head_object[0] + '.rx', lock=False)
        cmds.setAttr(vw_head_object[0] + '.ry', lock=False)
        cmds.setAttr(vw_head_object[0] + '.rz', lock=False)
        cmds.setAttr(vw_head_object[0] + '.sx', lock=False)
        cmds.setAttr(vw_head_object[0] + '.sy', lock=False)
        cmds.setAttr(vw_head_object[0] + '.sz', lock=False)
        cmds.setAttr(vw_head_object[0] + '.v', lock=False)

        head_bounding_box = cmds.xform(vw_head_object, q=True, bb=True)
        head_size = head_bounding_box[3] - head_bounding_box[0]
        progress_window = cmds.window(t='Final Progress')
        cmds.columnLayout()
        progress_value = cmds.progressBar(maxValue=len(vw_facial_list) - 1, width=300)
        cmds.showWindow(progress_window)

        for x in range(len(vw_facial_list)):
            cmds.textScrollList('facialControlFaceList', e=True, sii=x + 1)
            select_face_scroll_control_curve()
            cmds.duplicate(str(vw_head_object[0]), rr=True, n=vw_facial_list[x])
            cmds.setAttr(vw_facial_list[x] + '.translateX', head_size + 50)
            blend_shape_obj.append(vw_facial_list[x])
            cmds.progressBar(progress_value, edit=True, step=1)

        cmds.deleteUI(progress_window)
        default_set_button()
        select_face_scroll_control_curve()
        blend_shape_obj.append(str(vw_head_object[0]))
        cmds.blendShape(blend_shape_obj, n='__Facial_List__')
        blend_shape_obj.pop()
        all_delete_object = blend_shape_obj + vw_face_select_cluster
        all_curve = vw_right_curve + vw_left_curve + vw_center_curve
        cmds.delete(all_delete_object)
        cmds.delete(all_curve)
        mel.eval('setObjectPickMask "Joint" true;')
        mel.eval('setObjectPickMask "Surface" true;')
        mel.eval('setObjectPickMask "Curve" true;')

        cmds.setAttr(vw_head_object[0] + '.tx', lock=True)
        cmds.setAttr(vw_head_object[0] + '.ty', lock=True)
        cmds.setAttr(vw_head_object[0] + '.tz', lock=True)
        cmds.setAttr(vw_head_object[0] + '.rx', lock=True)
        cmds.setAttr(vw_head_object[0] + '.ry', lock=True)
        cmds.setAttr(vw_head_object[0] + '.rz', lock=True)
        cmds.setAttr(vw_head_object[0] + '.sx', lock=True)
        cmds.setAttr(vw_head_object[0] + '.sy', lock=True)
        cmds.setAttr(vw_head_object[0] + '.sz', lock=True)
        cmds.setAttr(vw_head_object[0] + '.v', lock=False)
    elif confirm_message == 'No':
        pass


def import_source_mesh(*args):
    global vw_source_mesh
    global vw_target_mesh
    source_object = cmds.ls(sl=True)
    vw_source_mesh = source_object[0]
    cmds.textFieldButtonGrp('importSourceMeshField', e=True, tx=vw_source_mesh, eb=True)
    copy_key_button_enter()


def import_target_mesh(*args):
    global vw_source_mesh
    global vw_target_mesh
    source_object = cmds.ls(sl=True)
    vw_target_mesh = source_object[0]
    cmds.textFieldButtonGrp('importTargetMeshField', e=True, tx=vw_target_mesh, eb=True)
    copy_key_button_enter()


def copy_key_process(*args):
    global vw_source_mesh
    global vw_target_mesh
    # sourceAttrList = []
    # targetAttrList = []
    # sourceBlndfind = []
    # targetBlndfind = []
    source_list_history = cmds.listHistory(vw_source_mesh)
    source_blend_find = cmds.ls(source_list_history, typ='blendShape')
    source_attribute_list = cmds.listAttr(source_blend_find[0] + ".w", m=True)
    target_list_history = cmds.listHistory(vw_target_mesh)
    target_blend_find = cmds.ls(target_list_history, typ='blendShape')
    target_attribute_list = cmds.listAttr(target_blend_find[0] + ".w", m=True)
    copy_progress_window = cmds.window(t='Progress')
    cmds.columnLayout()
    copy_progress_value = cmds.progressBar(maxValue=len(target_attribute_list) - 1, width=300)
    cmds.showWindow(copy_progress_window)

    for x in source_attribute_list:
        for y in target_attribute_list:
            if re.search(x + '$', y):
                cmds.copyKey(source_blend_find[0] + '.' + x)
                cmds.pasteKey(target_blend_find[0] + '.' + y)
                cmds.progressBar(copy_progress_value, edit=True, step=1)
            else:
                pass
    cmds.deleteUI(copy_progress_window)


def copy_key_button_enter():
    global vw_source_mesh
    global vw_target_mesh
    if vw_source_mesh == ' ' or vw_target_mesh == ' ':
        cmds.button('copyKeyBtn', e=True, en=False)
    elif vw_source_mesh != ' ' and vw_target_mesh != ' ':
        cmds.button('copyKeyBtn', e=True, en=True)


if __name__ == '__main__':
    vw_right_curve = []
    vw_center_curve = []
    vw_left_curve = []
    vw_show_cluster = []
    vw_hide_cluster = []
    vw_face_select_cluster = []
    vw_head_object = ' '
    vw_face_emotion_data = []
    vw_select_item_index = [1]
    vw_select_cluster_pos_temp = []
    vw_source_mesh = ' '
    vw_target_mesh = ' '
    if vw_file_temp is []:
        pass
    else:
        vw_file_temp[0] = []
    facial_set_create_mode_window()
