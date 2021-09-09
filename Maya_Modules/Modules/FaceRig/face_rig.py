# -*- coding: utf-8 -*-

import maya.cmds as cmds
import maya.mel as mel
import re
import pickle

vw_rightCurve = []
vw_centerCurve = []
vw_leftCurve = []
vw_showCluster = []
vw_hideCluster = []
vw_faceSelCluster = []
vw_headObject = ' '
vw_faceEmotionData = []
vw_selItemIndex = [1]
vw_selClusterPosTemp = []
vw_sourceMesh = ' '
vw_targetMesh = ' '
vw_fileTemp = []
vw_faceButtonNum = False

#pathOri = sys.path
#vw_path = ''

pathOri = cmds.internalVar(usd=True)
vw_path = pathOri+'faceRig/Facial_Check/'


vw_selRightCurve = 'R_Eyebrow', 'R_UpEye', 'R_LowEye', 'R_Zygoma', 'R_Nasolabial', 'R_Cheek', 'R_Jaw'
vw_selCenterCurve = 'C_ForeHead', 'C_Eyebrow', 'C_UpLip', 'C_LowLip', 'C_FrontJaw', 'C_JawFull'
vw_selLeftCurve = 'L_Eyebrow', 'L_UpEye', 'L_LowEye', 'L_Zygoma', 'L_Nasolabial', 'L_Cheek', 'L_Jaw'

vw_facialList = \
    'BrowsD_L',\
    'BrowsD_R',\
    'BrowsU_C',\
    'BrowsU_L',\
    'BrowsU_R',\
    'EyeBlink_L',\
    'EyeBlink_R',\
    'EyeDown_L',\
    'EyeDown_R',\
    'EyeIn_L',\
    'EyeIn_R',\
    'EyeOpen_L',\
    'EyeOpen_R',\
    'EyeOut_L',\
    'EyeOut_R',\
    'EyeSquint_L',\
    'EyeSquint_R',\
    'EyeUp_L',\
    'EyeUp_R',\
    'CheekSquint_L',\
    'CheekSquint_R',\
    'LipsFunnel',\
    'LipsLowerClose',\
    'LipsLowerDown',\
    'LipsLowerOpen',\
    'LipsPucker',\
    'LipsStretch_L',\
    'LipsStretch_R',\
    'LipsUpperClose',\
    'LipsUpperUp',\
    'ChinUpperRaise',\
    'ChinLowerRaise',\
    'MouthDimple_L',\
    'MouthDimple_R',\
    'MouthFrown_L',\
    'MouthFrown_R',\
    'MouthLeft',\
    'MouthRight',\
    'MouthSmile_L',\
    'MouthSmile_R',\
    'Puff',\
    'Sneer',\
    'JawFwd',\
    'JawOpen',\
    'JawLeft',\
    'JawRight'

vw_facialListGuide = {
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


def facialSetCreateModeWin(*args):
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject
    global vw_path
    global vw_faceSelCluster

    if cmds.window('facialCreateWindow',ex=True):
        cmds.deleteUI('facialCreateWindow')
    elif cmds.window('facialEditWindow',ex=True):
        cmds.deleteUI('facialEditWindow')
    elif cmds.window('facialControlWindow',ex=True):
        cmds.deleteUI('facialControlWindow')
    elif cmds.window('copyModeWindow',ex=True):
        cmds.deleteUI('copyModeWindow')
        
    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')
    
    clusterFilter()    
    for x in vw_faceSelCluster:
        cmds.hide(x+'Handle')
           
    cmds.window('facialCreateWindow',title='ventaworks Facial Rig Tool',w=600,h=600,sizeable=False)
    cmds.columnLayout( columnAttach=('both',1), rowSpacing=0, cal='center',columnWidth=600)
    cmds.image('imageViewField',w=500,h=500,i=vw_path+'fs_createMode.jpg')
    cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'),
                   columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
    cmds.text('')
    cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                        labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                        numberOfRadioButtons=4, h=50, sl=1,
                        on1=facialSetCreateModeWin, on2=facialSetEditModeWin,
                        on3=facialSetControlModeWin, on4=copyKeyWin)
    cmds.setParent(u=True)
    cmds.textFieldButtonGrp('selHead', label='Select Head Object ', tx=vw_headObject[0],
                            buttonLabel='<<<', h=50, bc=selHeadInButton, ed=False)
    
    if vw_headObject != ' ':
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200), adjustableColumn=2, columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='R I G H T', h=30, bgc=(0.1,0.1,0.1))
        cmds.textScrollList('facialControlRightList', append=vw_rightCurve, sc=selectRightScrollCurve, h=130)
        cmds.button(label='Create Right Curve', h=40, c=createRightCurve)
        cmds.setParent(u=True)
        
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='C E N T E R', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlCenterList', append=vw_centerCurve, sc=selectCenterScrollCurve, h=130)
        cmds.button(label='Create Center Curve', h=40, c=createCenterCurve)
        cmds.setParent(u=True)
        
        cmds.columnLayout( columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='L E F T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlLeftList', append=vw_leftCurve, sc=selectLeftScrollCurve, h=130)
        cmds.button(label='Create Left Curve', h=40, c=createLeftCurve)
        cmds.setParent(u=True)
        cmds.setParent(u=True)
        cmds.button(label='Attach Curve', h=60, c=attachCommand, bgc=(0.9, 0.3, 0.9))
        curveExists()
    else:       
        pass

    cmds.showWindow('facialCreateWindow')
  
    mel.eval('SelectToolOptionsMarkingMenu;\
    buildSelectMM;\
    global string $gSelect; setToolTo $gSelect;\
    selectToolValues nurbsSelect;\
    toolPropertyShow;\
    changeToolIcon;\
    SelectToolOptionsMarkingMenuPopDown;\
    MarkingMenuPopDown;')    


def facialSetEditModeWin(*args):
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject
    global vw_faceSelCluster
    
    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')
    
    mel.eval('artAttrToolScript 3 "wire";')
    clusterFilter()    
    for x in vw_faceSelCluster:
        cmds.hide(x+'Handle')
            
    if vw_headObject != ' ':
        
        if cmds.window('facialCreateWindow', ex=True):
            cmds.deleteUI('facialCreateWindow')
        elif cmds.window('facialEditWindow', ex=True):
            cmds.deleteUI('facialEditWindow')
        elif cmds.window('facialControlWindow', ex=True):
            cmds.deleteUI('facialControlWindow')
        elif cmds.window('copyModeWindow', ex=True):
            cmds.deleteUI('copyModeWindow')
              
        cmds.window('facialEditWindow', title='ventaworks Facial Set Tool', w=600, h=600, sizeable=False)
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=600)
        cmds.image('imageViewField', w=500, h=500, i=vw_path+'fs_editMode.jpg')
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        cmds.text('')
        cmds.radioButtonGrp('radioModeField', cw4=(100, 100, 100, 100),
                            labelArray4=['Create Mode', 'Edit Mode', 'Control Mode', 'Copy Key'],
                            numberOfRadioButtons=4, h=50, sl=2,
                            on1=facialSetCreateModeWin, on2=facialSetEditModeWin,
                            on3=facialSetControlModeWin, on4=copyKeyWin)
        cmds.setParent(u=True)

        cmds.textFieldButtonGrp('selHead', label='Select Head Object ', tx=vw_headObject[0],
                                buttonLabel='<<<', h=50, bc=selHeadInButton, ed=False, eb=False)
        cmds.rowLayout(numberOfColumns=3, columnWidth3=(200, 200, 200),
                       adjustableColumn=2,
                       columnAlign=(1, 'center'),
                       columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='R I G H T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlRightList', append=vw_rightCurve, sc=selectRightScrollEditCurve, h=130)
        cmds.setParent(u=True)
        
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='C E N T E R', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlCenterList', append=vw_centerCurve, sc=selectCenterScrollEditCurve, h=130)
        cmds.setParent(u=True)
        
        cmds.columnLayout(columnAttach=('both', 2), rowSpacing=0, columnWidth=200)
        cmds.text(label='L E F T', h=30, bgc=(0.1, 0.1, 0.1))
        cmds.textScrollList('facialControlLeftList', append=vw_leftCurve, sc=selectLeftScrollEditCurve, h=130)
        cmds.setParent(u=True)
        cmds.setParent(u=True)
        cmds.gridLayout(numberOfColumns=2, cellWidthHeight=(300, 40))
        cmds.button('importMapField', label='Import Map', c=importMapImage, h=40)
        cmds.button('exportMapField', label='Export Map', c=exportMapImage, h=40)
        cmds.setParent(u=True)
        cmds.button(label='Create Controller', h=60, c=controllerCommand, bgc=(0.9, 0.3, 0.9))
        cmds.showWindow('facialEditWindow')
        curveExists()
    else:
        facialSetCreateModeWin()


def facialSetControlModeWin(*args):
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject
    global vw_facialList
    global vw_faceSelCluster
    global vw_faceEmotionData
    global vw_selItemIndex
    global vw_facialListGuide
    
    mel.eval('setObjectPickMask "Joint" false;')
    mel.eval('setObjectPickMask "Surface" false;')
    mel.eval('setObjectPickMask "Curve" false;')
    
    clusterFilter()
    allCurve = []
    num = 0
    
    for x in vw_faceSelCluster:
        cmds.hide(x+'Handle')
    
    for x in vw_leftCurve:
        allCurve.append(str(x))        
        allCurve.append(str(vw_rightCurve[num]))
        num += 1
        
    for x in vw_centerCurve:
        allCurve.append(str(x))
    
    cmds.select(cl=True)
        
    if vw_headObject != ' ':    
        if cmds.window('facialCreateWindow',ex=True):
            cmds.deleteUI('facialCreateWindow')
        elif cmds.window('facialEditWindow',ex=True):
            cmds.deleteUI('facialEditWindow')
        elif cmds.window('facialControlWindow',ex=True):
            cmds.deleteUI('facialControlWindow')
        elif cmds.window('copyModeWindow',ex=True):
            cmds.deleteUI('copyModeWindow')
            
        cmds.window('facialControlWindow',title='ventaworks Facial Set Tool',w=600,h=600,sizeable=False)
        cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=600)
        cmds.image('imageViewField',w=500,h=500,i=vw_path+'fs_controlMode.jpg')
        cmds.button('defaultFaceButtonField',label='default Face Image',h=30,aop=True,c=defaultFaceImage)
        cmds.rowLayout( numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
        cmds.text('')
        cmds.radioButtonGrp('radioModeField',cw4=(100,100,100,100) ,labelArray4=['Create Mode','Edit Mode','Control Mode','Copy Key'],\
        numberOfRadioButtons=4,h=50,sl=3,on1=facialSetCreateModeWin,on2=facialSetEditModeWin,on3=facialSetControlModeWin,on4=copyKeyWin)
        cmds.setParent(u=True)
        cmds.textFieldButtonGrp('selHead',label='Select Head Object ',tx=vw_headObject[0], buttonLabel='<<<',h=50,bc=selHeadInButton,ed=False,eb=False)
        cmds.text('faceGuideField',label=vw_facialListGuide.get('BrowsD_L'),h=50,fn='plainLabelFont',rs=True)
        cmds.rowLayout( numberOfColumns=3, columnWidth3=(240,240,110), adjustableColumn=3, columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)])
        
        cmds.columnLayout( columnAttach=('both',1), rowSpacing=0, columnWidth=240)
        cmds.text(label='F A C E   L I S T',h=30,bgc=(0.3,0.1,0.1))
        cmds.textScrollList('facialControlFaceList',append=vw_facialList,sc=selectFaceScrollControlCurve,h=300,sii=vw_selItemIndex[0],bgc=(0.4,0.3,0.3))
        cmds.setParent(u=True)
               
        cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=240)
        cmds.text(label='Curve Controller',h=30,bgc=(0.1,0.1,0.1))
        cmds.textScrollList('facialControlList',append=allCurve,sc=selectScrollControlCurve,h=300,ams=True)
        cmds.setParent(u=True)
        
        cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=110,h=333)
        cmds.text(label='SET Button',h=30,bgc=(0.1,0.1,0.1))
        cmds.button(label='S E T',h=100,c=controlModeSet,bgc=(0.5,0,0.0))
        cmds.button(label='copy',h=30,c=copyButton,bgc=(0.4,0.4,0.4))
        cmds.gridLayout(numberOfColumns=3,cellWidthHeight=(36.7,40))
        cmds.button(label='Pst',h=40,c=pasteButton,bgc=(0.4,0.4,0.4))
        cmds.button(label='CM',h=40,c=CmirrorPasteButton,bgc=(0.4,0.4,0.4))
        cmds.button(label='M',h=40,c=mirrorPasteButton,bgc=(0.4,0.4,0.4))
        cmds.setParent(u=True)
        
        cmds.text(label='File menu',h=30,bgc=(0.1,0.1,0.1))
        ##mc.button(label='All Reset',h=30,c=defaultSetButton)
        cmds.button(label='Select Reset',h=30,c=selectResetButton)
        cmds.button(label='Import',h=30,c=importButton)
        cmds.button(label='SAVE',h=50,c=saveButton,bgc=(0.9,0.2,0))
        cmds.setParent(u=True)
        cmds.setParent(u=True)
        
        cmds.button(label='Final Step',h=60,c=finalStep,bgc=(0.9,0.3,0.9))
        cmds.showWindow('facialControlWindow')
    
    else:
        facialSetCreateModeWin()
        
    selectFaceScrollControlCurve()    
    mel.eval('SelectToolOptionsMarkingMenu;\
    buildSelectMM;\
    global string $gSelect; setToolTo $gSelect;\
    selectToolValues nurbsSelect;\
    toolPropertyShow;\
    changeToolIcon;\
    SelectToolOptionsMarkingMenuPopDown;\
    MarkingMenuPopDown;')   


def copyKeyWin(*args):
    global vw_sourceMesh
    global vw_targetMesh
    
    mel.eval('setObjectPickMask "Joint" true;')
    mel.eval('setObjectPickMask "Surface" true;')
    mel.eval('setObjectPickMask "Curve" true;')

    if cmds.window('facialCreateWindow',ex=True):
        cmds.deleteUI('facialCreateWindow')
    elif cmds.window('facialEditWindow',ex=True):
        cmds.deleteUI('facialEditWindow')
    elif cmds.window('facialControlWindow',ex=True):
        cmds.deleteUI('facialControlWindow')
    elif cmds.window('copyModeWindow',ex=True):
        cmds.deleteUI('copyModeWindow')

    cmds.window('copyModeWindow',title='ventaworks Facial Set Tool',w=600,h=600,sizeable=False)
    cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=600)
    cmds.image('imageViewField',w=500,h=500,i=vw_path+'fs_controlMode.jpg')
    cmds.rowLayout( numberOfColumns=3, columnWidth3=(100, 400, 100), adjustableColumn=2, columnAlign=(1, 'center'), columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)] )
    cmds.text('')
    cmds.radioButtonGrp('radioModeField',cw4=(100,100,100,100) ,labelArray4=['Create Mode','Edit Mode','Control Mode','Copy Key'],\
    numberOfRadioButtons=4,h=50,sl=4,on1=facialSetCreateModeWin,on2=facialSetEditModeWin,on3=facialSetControlModeWin,on4=copyKeyWin)
    cmds.setParent(u=True)
    cmds.columnLayout( columnAttach=('both',1), rowSpacing=0, columnWidth=600)
    
    if vw_sourceMesh==' ':
        cmds.textFieldButtonGrp('importSourceMeshField',label='Source Mesh',tx='', buttonLabel='<<<',h=50,bc=importSourceMesh,ed=False,eb=True)
    else:
        cmds.textFieldButtonGrp('importSourceMeshField',label='Source Mesh',tx=vw_sourceMesh, buttonLabel='<<<',h=50,bc=importSourceMesh,ed=False,eb=True)
    if vw_targetMesh==' ':
        cmds.textFieldButtonGrp('importTargetMeshField',label='Target Mesh',tx='', buttonLabel='<<<',h=50,bc=importTargetMesh,ed=False,eb=True)
    else:    
        cmds.textFieldButtonGrp('importTargetMeshField',label='Target Mesh',tx=vw_targetMesh, buttonLabel='<<<',h=50,bc=importTargetMesh,ed=False,eb=True)

    if vw_sourceMesh == ' ' or vw_targetMesh == ' ':
        cmds.button('copyKeyBtn',label='Copy Key',h=60,en=False,c=copyKeyProcess,bgc=(0.9,0.3,0.9))
        
    elif vw_sourceMesh != ' ' and vw_targetMesh != ' ':
        cmds.button('copyKeyBtn',label='Copy Key',h=60,en=True,c=copyKeyProcess,bgc=(0.9,0.3,0.9))

    cmds.showWindow('copyModeWindow')


def createRightCurve(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    
    if cmds.window('createLeftCurveWin',ex=True):
        cmds.deleteUI('createLeftCurveWin')
        
    if cmds.window('createCenterCurveWin',ex=True):
        cmds.deleteUI('createCenterCurveWin')
    
    if cmds.window('createRightCurveWin',ex=True):
        cmds.deleteUI('createRightCurveWin')
        
    cmds.window('createRightCurveWin',title='create Right Curve',w=250,h=350,sizeable=False)
    cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selRightCurveWin',append=vw_selRightCurve)
    
    for x in vw_selRightCurve:
        if cmds.objExists(x):
            cmds.textScrollList('selRightCurveWin',e=True,ri=x)
        else:
            pass
    
    cmds.button(label='O K ! !',h=60,c=selRightCurveList)
    cmds.showWindow('createRightCurveWin')


def selRightCurveList(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject
    
    selRightItem = cmds.textScrollList('selRightCurveWin',q=True,si=True)
    sideEdgeToCurve(selRightItem[0])
    vw_rightCurve.sort()
    curveExists()
    cmds.deleteUI('createRightCurveWin')
    

def createCenterCurve(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
        
    if cmds.window('createLeftCurveWin',ex=True):
        cmds.deleteUI('createLeftCurveWin')
        
    if cmds.window('createCenterCurveWin',ex=True):
        cmds.deleteUI('createCenterCurveWin')
    
    if cmds.window('createRightCurveWin',ex=True):
        cmds.deleteUI('createRightCurveWin')
            
    cmds.window('createCenterCurveWin',title='create Center Curve',w=250,h=350,sizeable=False)
    cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selCenterCurveWin',append=vw_selCenterCurve)
    
    for x in vw_selCenterCurve:
        if cmds.objExists(x):
            cmds.textScrollList('selCenterCurveWin',e=True,ri=x)
        else:
            pass
                
    cmds.button(label='O K ! !',h=60,c=selCenterCurveList)
    cmds.showWindow('createCenterCurveWin')


def selCenterCurveList(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    
    selCenterItem = cmds.textScrollList('selCenterCurveWin',q=True,si=True)
    centerEdgeToCurve(selCenterItem[0])
    vw_centerCurve.sort()
    cmds.deleteUI('createCenterCurveWin')
    curveExists()
        

def createLeftCurve(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
        
    if cmds.window('createLeftCurveWin',ex=True):
        cmds.deleteUI('createLeftCurveWin')
        
    if cmds.window('createCenterCurveWin',ex=True):
        cmds.deleteUI('createCenterCurveWin')
    
    if cmds.window('createRightCurveWin',ex=True):
        cmds.deleteUI('createRightCurveWin')
            
    cmds.window('createLeftCurveWin',title='create Left Curve',w=250,h=350,sizeable=False)
    cmds.columnLayout( columnAttach=('both',2), rowSpacing=0, columnWidth=250)
    cmds.textScrollList('selLeftCurveWin',append=vw_selLeftCurve)
    
    for x in vw_selLeftCurve:
        if cmds.objExists(x):
            cmds.textScrollList('selLeftCurveWin',e=True,ri=x)
        else:
            pass
                
    cmds.button(label='O K ! !',h=60,c=selLeftCurveList)
    cmds.showWindow('createLeftCurveWin')


def selLeftCurveList(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    
    selLeftItem = cmds.textScrollList('selLeftCurveWin',q=True,si=True)
    sideEdgeToCurve(selLeftItem[0])
    vw_leftCurve.sort()
    cmds.deleteUI('createLeftCurveWin')
    curveExists()


def curveExists():
    
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    
    vw_rightCurve = []
    vw_centerCurve = []
    vw_leftCurve = []

    cmds.select(all=True)
    allCurve = cmds.filterExpand(ex=True,sm=9)
    
    if allCurve == None:
        pass
        
    elif allCurve != None:
        for x in vw_selRightCurve:
            for y in allCurve:
                if re.search(x+'$',y):
                    vw_rightCurve.append(y)
                    
        for x in vw_selCenterCurve:
            for y in allCurve:
                if re.search(x+'$',y):
                    vw_centerCurve.append(y)
                        
        for x in vw_selLeftCurve:
            for y in allCurve:
                if re.search(x+'$',y):
                    vw_leftCurve.append(y)
                 
    cmds.select(cl=True)
   
    cmds.textScrollList('facialControlRightList',e=True,ra=True)
    cmds.textScrollList('facialControlRightList',e=True,append=vw_rightCurve)
    cmds.textScrollList('facialControlCenterList',e=True,ra=True)
    cmds.textScrollList('facialControlCenterList',e=True,append=vw_centerCurve)
    cmds.textScrollList('facialControlLeftList',e=True,ra=True)
    cmds.textScrollList('facialControlLeftList',e=True,append=vw_leftCurve)


def selHeadInButton(*args):
    global vw_headObject
    vw_headObject = cmds.ls(sl=True,fl=True)
    cmds.textFieldButtonGrp('selHead',e=True,tx=vw_headObject[0])
    facialSetCreateModeWin()


def centerEdgeToCurve(curveName):

    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    
    selVertex = cmds.ls(sl=True,fl=True)
    mel.eval('polyToCurve -n '+curveName+' -form 5 -degree 3;')
    cmds.select(curveName)
    cmds.rebuildCurve(curveName,ch=True,rpo=True,rt=0,end=0,kr=0,kcp=False,kep=False,kt=False,s=5,d=3)


def sideEdgeToCurve(curveName):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_headObject
    centerX = cmds.objectCenter(vw_headObject[0],x=True)
    centerY = cmds.objectCenter(vw_headObject[0],y=True)
    centerZ = cmds.objectCenter(vw_headObject[0],z=True)
           
    selVertex = cmds.ls(sl=True,fl=True)
    mel.eval('polyToCurve -n '+curveName+' -form 5 -degree 3;')
    cmds.select(curveName)
    cmds.rebuildCurve(curveName,ch=True,rpo=True,rt=0,end=0,kr=0,kcp=False,kep=False,kt=False,s=3,d=3)
    cmds.move(centerX,centerY,centerZ,curveName+'.scalePivot',curveName+'.rotatePivot',rpr=True,spr=True)
        

def selectRightScrollCurve(*args):
    selRight = cmds.textScrollList('facialControlRightList',q=True,si=True)
    cmds.textScrollList('facialControlCenterList',e=True,da=True)
    cmds.textScrollList('facialControlLeftList',e=True,da=True)
    cmds.select(selRight,r=True)


def selectCenterScrollCurve(*args):
    selCenter = cmds.textScrollList('facialControlCenterList',q=True,si=True)
    cmds.textScrollList('facialControlRightList',e=True,da=True)
    cmds.textScrollList('facialControlLeftList',e=True,da=True)
    cmds.select(selCenter,r=True)


def selectLeftScrollCurve(*args):
    selLeft = cmds.textScrollList('facialControlLeftList',q=True,si=True)
    cmds.textScrollList('facialControlRightList',e=True,da=True)
    cmds.textScrollList('facialControlCenterList',e=True,da=True)
    cmds.select(selLeft,r=True)


def attachCommand(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject
    
    confirmMsg = cmds.confirmDialog( title='Confirm',icn='question',message='Are you ok?', button=['Yes','No'],
                                     defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    if confirmMsg == 'Yes':
        allOriginCurve = vw_selRightCurve+vw_selCenterCurve+vw_selLeftCurve
        allCurve = vw_rightCurve + vw_centerCurve + vw_leftCurve  
        
        for d in allOriginCurve:
            for x in allCurve:
                if d == x:
                    if re.search('R_',x):
                        curveReName = 'L'+x[1:]
                        if cmds.objExists(curveReName):
                            pass
                        else:
                            cmds.duplicate(x,n=curveReName,rr=True)
                            cmds.scale(-1,1,1,curveReName,r=True)
                    else:
                        pass 
                    
                    if re.search('L_',x):
                        curveReName = 'R'+x[1:]
                        if cmds.objExists(curveReName):
                            pass
                        else:
                            cmds.duplicate(x,n=curveReName,rr=True)
                            cmds.scale(-1,1,1,curveReName,r=True)
                    
                    if re.match('C_',x):
                        pass
                else:
                    pass
                
        curveExists()
        allCurve = []            
        allCurve = vw_rightCurve + vw_leftCurve + vw_centerCurve  
        cmds.select(vw_headObject)
        mel.eval('artAttrToolScript 3 "wire";')
        allCurve = vw_rightCurve + vw_leftCurve + vw_centerCurve
    

        attachProgressWin = cmds.window(t='Attch Progress')
        cmds.columnLayout()
        progressValue = cmds.progressBar(maxValue=len(allCurve)-1, width=300)
        cmds.showWindow( attachProgressWin )
           

        for x in allCurve:
            cmds.select(x)
            mel.eval('DeleteHistory;')
            mel.eval('CenterPivot;')
            cmds.wire(vw_headObject,w=x,n=x+'_wire')
            cmds.setAttr(x+'_wire'+'.dropoffDistance[0]',100)
            cmds.setAttr(x+'_wire'+'.rotation',0)
            cmds.select(vw_headObject)
            
            mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+x+'_wire.weights" )')
            mel.eval('artAttrPaintOperation artAttrCtx Replace;')
            mel.eval('artAttrCtx -e -value 0 `currentCtx`;')
            mel.eval('artAttrCtx -e -clear `currentCtx`;')
            mel.eval('artAttrCtx -e -value 1 `currentCtx`;')
            cmds.progressBar(progressValue, edit=True, step=1)
        
        cmds.deleteUI(attachProgressWin)
        mel.eval('SelectToolOptionsMarkingMenu;\
        buildSelectMM;\
        global string $gSelect; setToolTo $gSelect;\
        selectToolValues nurbsSelect;\
        toolPropertyShow;\
        changeToolIcon;\
        SelectToolOptionsMarkingMenuPopDown;\
        MarkingMenuPopDown;')
        
        facialSetEditModeWin()
    elif confirmMsg == 'No':
        pass


def selectRightScrollEditCurve(*args):
    global vw_headObject

    selRight = cmds.textScrollList('facialControlRightList',q=True,si=True)
    cmds.textScrollList('facialControlCenterList',e=True,da=True)
    cmds.textScrollList('facialControlLeftList',e=True,da=True)
    
    if cmds.objExists(selRight[0]+'_wire'):
        cmds.select(vw_headObject,selRight[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+selRight[0]+'_wire.weights" )')
    else:
        pass
   
def selectCenterScrollEditCurve(*args):
    global vw_headObject

    selCenter = cmds.textScrollList('facialControlCenterList',q=True,si=True)
    cmds.textScrollList('facialControlRightList',e=True,da=True)
    cmds.textScrollList('facialControlLeftList',e=True,da=True)
    
    if cmds.objExists(selCenter[0]+'_wire'):
        cmds.select(vw_headObject,selCenter[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+selCenter[0]+'_wire.weights" )')
    else:
        pass    

def selectLeftScrollEditCurve(*args):
    global vw_headObject

    selLeft = cmds.textScrollList('facialControlLeftList',q=True,si=True)
    cmds.textScrollList('facialControlRightList',e=True,da=True)
    cmds.textScrollList('facialControlCenterList',e=True,da=True)
    
    if cmds.objExists(selLeft[0]+'_wire'):
        cmds.select(vw_headObject,selLeft[0])
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+selLeft[0]+'_wire.weights" )')
    else:
        pass  

def importMapImage(*args):
    rightList = []
    centerList = []
    leftList = []
    allList = []
    
    rightList = cmds.textScrollList('facialControlRightList',q=True,si=True)
    centerList = cmds.textScrollList('facialControlCenterList',q=True,si=True)
    leftList = cmds.textScrollList('facialControlLeftList',q=True,si=True)
    
    if rightList != None:
        allList.append(rightList)
    elif centerList != None:
        allList.append(centerList)
    elif leftList != None:
        allList.append(leftList)
    
    if allList == []:
        pass
    else:        
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+allList[0][0]+'_wire.weights" );')   
        mel.eval('artImportMapDialog "artAttrCtx";')
    
    
def exportMapImage(*args):    
    rightList = []
    centerList = []
    leftList = []
    allList = []
    
    rightList = cmds.textScrollList('facialControlRightList',q=True,si=True)
    centerList = cmds.textScrollList('facialControlCenterList',q=True,si=True)
    leftList = cmds.textScrollList('facialControlLeftList',q=True,si=True)
    
    if rightList != None:
        allList.append(rightList)
    elif centerList != None:
        allList.append(centerList)
    elif leftList != None:
        allList.append(leftList)
    
    if allList == []:
        pass
    else:
        mel.eval('artSetToolAndSelectAttr( "artAttrCtx", "wire.'+allList[0][0]+'_wire.weights" );')
        mel.eval('artExportMapValue "Luminance" artAttrCtx;')
        mel.eval('artExportFileTypeValue "JPEG" artAttrCtx;')
        mel.eval('artAttrCtx -e -exportfilesizex 4096 `currentCtx`;')
        mel.eval('artAttrCtx -e -exportfilesizey 4096 `currentCtx`;')
        mel.eval('artExportMapDialog "artAttrCtx";')
  

def controllerCommand(*args):
    global vw_selRightCurve
    global vw_selCenterCurve
    global vw_selLeftCurve
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_headObject

    confirmMsg = cmds.confirmDialog( title='Confirm',icn='question',message='Are you ok?', button=['Yes','No'],
                                     defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    if confirmMsg == 'Yes':    
        allCurve = vw_rightCurve+vw_centerCurve+vw_leftCurve
        selTemp = []
    
        stepNum = 1
        
        clusterProgressWin = cmds.window(t='cluster Progress')
        cmds.columnLayout()
        progressValue = cmds.progressBar(maxValue=len(allCurve)-1, width=300)
        cmds.showWindow(clusterProgressWin)
        
        for x in allCurve:
            
            if re.search(vw_selCenterCurve[-1]+'$',x):
                pass
            else:
                cmds.select(x+'.cv[0:]',r=True)
                sel = cmds.ls(sl=True,fl=True)
                for y in sel:
                    cmds.cluster(y,en=1,n=x)
                    
                cmds.progressBar(progressValue, edit=True, step=1)
        
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
        cmds.deleteUI(clusterProgressWin)
        facialSetControlModeWin()
    
    if confirmMsg == 'No':
        pass 


def selectFaceScrollControlCurve(*args):
    global vw_showCluster
    global vw_faceSelCluster
    global vw_faceEmotionData
    global vw_selItemIndex
    global vw_facialListGuide
    global vw_centerCurve
    global vw_selCenterCurve
       
    vw_selItemIndex = cmds.textScrollList('facialControlFaceList',q=True,sii=True)
    selectItem = cmds.textScrollList('facialControlFaceList',q=True,si=True)
    intNum = vw_selItemIndex[0]-1
    stepNum = 0

    if vw_faceEmotionData == []:
        defaultSetButton()
        
    elif vw_faceEmotionData[intNum] != []:
        for x in vw_faceSelCluster:
            cmds.setAttr(x+'Handle.translateX',vw_faceEmotionData[intNum][stepNum][0])
            cmds.setAttr(x+'Handle.translateY',vw_faceEmotionData[intNum][stepNum][1])
            cmds.setAttr(x+'Handle.translateZ',vw_faceEmotionData[intNum][stepNum][2])
            stepNum += 1
            
        for y in vw_centerCurve:
            if re.search(vw_selCenterCurve[-1]+'$',y):       
                cmds.setAttr(y+'.translateX',vw_faceEmotionData[intNum][-1][0])
                cmds.setAttr(y+'.translateY',vw_faceEmotionData[intNum][-1][1])
                cmds.setAttr(y+'.translateZ',vw_faceEmotionData[intNum][-1][2])
                cmds.setAttr(y+'.rotateX',vw_faceEmotionData[intNum][-1][3])
                cmds.setAttr(y+'.rotateY',vw_faceEmotionData[intNum][-1][4])
                cmds.setAttr(y+'.rotateZ',vw_faceEmotionData[intNum][-1][5])
            else:
                pass
  
    faceGuideValue = vw_facialListGuide.get(selectItem[0])
    cmds.text('faceGuideField',e=True,label=faceGuideValue)
    cmds.image('imageViewField',e=True,i=vw_path+'Facial_Check/'+selectItem[0]+'.jpg')


def defaultFaceImage(*args):
    global vw_faceButtonNum
    selectItem = cmds.textScrollList('facialControlFaceList',q=True,si=True)
    
    if vw_faceButtonNum is False:
        cmds.image('imageViewField',e=True,i=vw_path+'Facial_Check/defaultFace.jpg')
        vw_faceButtonNum = True
        
    elif vw_faceButtonNum is True:
        cmds.image('imageViewField',e=True,i=vw_path+'Facial_Check/'+selectItem[0]+'.jpg')
        vw_faceButtonNum = False
        

def controlModeSet(*args):
    global vw_showCluster
    global vw_faceSelCluster
    global vw_faceEmotionData
    global vw_selItemIndex
    global vw_centerCurve
    global vw_fileTemp
    global vw_facialList
    
    vw_selItemIndex = cmds.textScrollList('facialControlFaceList',q=True,sii=True)
    clAllPos = []

    fs = open('c:/Facial_temp.fd', 'wb')
    pickle.dump(vw_faceEmotionData, fs)
    fs.close()
        
    setProgressWin = cmds.window(t='Set Progress')
    cmds.columnLayout()
    progressValue = cmds.progressBar(maxValue=2500, width=300)
    cmds.showWindow(setProgressWin)
    
    if vw_faceEmotionData == []:
        defaultSetButton()
        for x in vw_faceSelCluster:
            clPosition = []
            posX = cmds.getAttr(x+'Handle.translateX')
            posY = cmds.getAttr(x+'Handle.translateY')
            posZ = cmds.getAttr(x+'Handle.translateZ')
            clPosition = [posX,posY,posZ]
            clAllPos.append(clPosition)
        
        for x in vw_centerCurve:
            if re.search(vw_selCenterCurve[-1]+'$',x):
                clPosition = []
                jawPosX = cmds.getAttr(x+'.translateX')
                jawPosY = cmds.getAttr(x+'.translateY')
                jawPosZ = cmds.getAttr(x+'.translateZ')
                jawRotX = cmds.getAttr(x+'.rotateX')
                jawRotY = cmds.getAttr(x+'.rotateY')
                jawRotZ = cmds.getAttr(x+'.rotateZ')
                clPosition = [jawPosX,jawPosY,jawPosZ,jawRotX,jawRotY,jawRotZ]
                clAllPos.append(clPosition)
            else:
                pass
                        
    elif vw_faceEmotionData != []:
        for x in vw_faceSelCluster:
            clPosition = []
            posX = cmds.getAttr(x+'Handle.translateX')
            posY = cmds.getAttr(x+'Handle.translateY')
            posZ = cmds.getAttr(x+'Handle.translateZ')
            clPosition = [posX,posY,posZ]
            clAllPos.append(clPosition)
            
        for x in vw_centerCurve:
            if re.search(vw_selCenterCurve[-1]+'$',x):
                clPosition = []
                jawPosX = cmds.getAttr(x+'.translateX')
                jawPosY = cmds.getAttr(x+'.translateY')
                jawPosZ = cmds.getAttr(x+'.translateZ')
                jawRotX = cmds.getAttr(x+'.rotateX')
                jawRotY = cmds.getAttr(x+'.rotateY')
                jawRotZ = cmds.getAttr(x+'.rotateZ')
                clPosition = [jawPosX,jawPosY,jawPosZ,jawRotX,jawRotY,jawRotZ]
                clAllPos.append(clPosition)
            else:
                pass
       
    vw_faceEmotionData[vw_selItemIndex[0]-1]=clAllPos
    for x in range(1500):
        cmds.progressBar(progressValue, edit=True, step=1)
    cmds.deleteUI(setProgressWin)
      
    if vw_fileTemp == []:
        saveButton()
    else:
        fs = open(vw_fileTemp[:-3]+'_tmp.fd','wb')
        pickle.dump(vw_faceEmotionData,fs)
        fs.close()
        
        '''
        if vw_selItemIndex[0] < len(vw_facialList):
            mc.textScrollList('facialControlFaceList',e=True,sii=vw_selItemIndex[0]+1)
            selectFaceScrollControlCurve()
        elif vw_selItemIndex[0] == len(vw_facialList):
            pass        
        '''
        

def copyButton(*args):
    global vw_selClusterPosTemp
    vw_selClusterPosTemp = []
    clPosition = []   
    clAllPos = []
        
    selCluster = cmds.ls(sl=True,fl=True)
    selCluster.sort()
    for x in selCluster:
        posX = cmds.getAttr(x+'.translateX')
        posY = cmds.getAttr(x+'.translateY')
        posZ = cmds.getAttr(x+'.translateZ')
        clPosition = [posX,posY,posZ]
        clAllPos.append(clPosition)
    
    vw_selClusterPosTemp = clAllPos


def pasteButton(*args):
    global vw_selClusterPosTemp
    
    selCluster = cmds.ls(sl=True,fl=True)
    selCluster.sort()
    stepNum = 0
    for x in selCluster:
        cmds.setAttr(x+'.translateX',vw_selClusterPosTemp[stepNum][0])
        cmds.setAttr(x+'.translateY',vw_selClusterPosTemp[stepNum][1])
        cmds.setAttr(x+'.translateZ',vw_selClusterPosTemp[stepNum][2])
        stepNum += 1   


def CmirrorPasteButton(*args):
    global vw_selClusterPosTemp
    
    selCluster = cmds.ls(sl=True,fl=True)
    selCluster.sort()
    selCluster.reverse()
    stepNum = 0
    for x in selCluster:
        cmds.setAttr(x+'.translateX',vw_selClusterPosTemp[stepNum][0]*-1)
        cmds.setAttr(x+'.translateY',vw_selClusterPosTemp[stepNum][1])
        cmds.setAttr(x+'.translateZ',vw_selClusterPosTemp[stepNum][2])
        stepNum += 1   
                 

def mirrorPasteButton(*args):
    global vw_selClusterPosTemp
    
    selCluster = cmds.ls(sl=True,fl=True)
    selCluster.sort()
    stepNum = 0
    for x in selCluster:
        cmds.setAttr(x+'.translateX',vw_selClusterPosTemp[stepNum][0]*-1)
        cmds.setAttr(x+'.translateY',vw_selClusterPosTemp[stepNum][1])
        cmds.setAttr(x+'.translateZ',vw_selClusterPosTemp[stepNum][2])
        stepNum += 1   
       

def defaultSetButton(*args):
    global vw_faceEmotionData
    
    vw_faceEmotionData = []
    posSet = []
    clusterSet = []
    curveSet = []
    
    itemNumber = cmds.textScrollList('facialControlFaceList',q=True,ni=True)
    
    for z in range(3):
        posSet.append(0.0)
    
    for y in range(len(vw_faceSelCluster)):
        clusterSet.append(posSet)
    
    for a in range(6):
        curveSet.append(0.0)
    
    clusterSet.append(curveSet)  
    for x in range(itemNumber):
        vw_faceEmotionData.append(clusterSet)


def selectResetButton(*args):
    global vw_showCluster
    global vw_faceSelCluster
    global vw_faceEmotionData
    global vw_selItemIndex
    global vw_facialListGuide
    global vw_centerCurve
    global vw_selCenterCurve
   
    vw_selItemIndex = cmds.textScrollList('facialControlFaceList',q=True,sii=True)
    selectItem = cmds.textScrollList('facialControlFaceList',q=True,si=True)
    intNum = vw_selItemIndex[0]-1
    stepNum = 0
         
    if vw_faceEmotionData == []:
        defaultSetButton()
        
    elif vw_faceEmotionData[intNum] != []:
        for x in vw_faceSelCluster:
            cmds.setAttr(x+'Handle.translateX',0.0)
            cmds.setAttr(x+'Handle.translateY',0.0)
            cmds.setAttr(x+'Handle.translateZ',0.0)
            stepNum += 1
            
        for y in vw_centerCurve:
            if re.search(vw_selCenterCurve[-1]+'$',y):       
                cmds.setAttr(y+'.translateX',0.0)
                cmds.setAttr(y+'.translateY',0.0)
                cmds.setAttr(y+'.translateZ',0.0)
                cmds.setAttr(y+'.rotateX',0.0)
                cmds.setAttr(y+'.rotateY',0.0)
                cmds.setAttr(y+'.rotateZ',0.0)
            else:
                pass
                
    controlModeSet()
    

def importButton(*args):
    global vw_facialList
    global vw_faceEmotionData
    global vw_faceSelCluster
    global vw_fileTemp
    
    fileData = []
    fileTemp = []
    convertTemp = []   
     
    stepNum = 0

    if vw_faceEmotionData == []:
        defaultSetButton()
    else:
        pass
        
    faceDataFilters = 'Facial Data File (*.fd)'
    openfileList = cmds.fileDialog2(cap='Import',fileMode=1, fileFilter=faceDataFilters, dialogStyle=2)
    
    if openfileList==None:
        print('no select file')
    else:
        openfilename = openfileList[0]
        vw_fileTemp = openfileList[0]
        fo = open(openfilename,'rb')
        vw_faceEmotionData = pickle.load(fo)
        fo.close()
        cmds.confirmDialog( title='Complete',icn="information" ,message='Import Complete!!', button='ok', defaultButton='ok')
    

def saveButton(*args):
    global vw_facialList
    global vw_faceEmotionData
    global vw_faceSelCluster
    global vw_fileTemp
    
    faceDataFilters = 'Facial Data File (*.fd)'
    savefileList = cmds.fileDialog2(cap='SAVE',fileFilter=faceDataFilters, dialogStyle=2)
    
    if savefileList==None:
        print('no select file')
        
    else:
        savefilename = savefileList[0]
        vw_fileTemp = savefileList[0]
        fs = open(savefilename,'wb')
        pickle.dump(vw_faceEmotionData,fs)
        fs.close()
        cmds.confirmDialog( title='Complete',icn="information" ,message='Save Complete!!', button='ok', defaultButton='ok')


def selectScrollControlCurve(*args):
    global vw_headObject
    global vw_showCluster 
    global vw_hideCluster
    global vw_faceSelCluster
    global vw_centerCurve
    global vw_selCenterCurve
    
    clusterFilter()
    selJawCurve = []
    selCurveList = cmds.textScrollList('facialControlList',q=True,si=True)
    selItemNum = cmds.textScrollList('facialControlList',q=True,nsi=True)
    
    if vw_faceSelCluster != []:
        if selItemNum > 1:
            cmds.select(cl=True)
            if selJawCurve == []:
                pass
            else:
                cmds.select(selCurveList[0])

            for y in range(selItemNum):
                for x in vw_faceSelCluster:
                    if re.search('^'+selCurveList[y],x):
                        vw_showCluster.append(x+'Handle')
                    else:
                        vw_hideCluster.append(x+'Handle')

            for z in vw_faceSelCluster:
                cmds.hide(z)

            for x in vw_showCluster:
                cmds.showHidden(x)
                   
        elif selItemNum == 1:        
            vw_showCluster = []
            vw_hideCluster = []
            cmds.hide(vw_faceSelCluster)
            cmds.select(cl=True)
            
            if re.search(vw_selCenterCurve[-1]+'$',selCurveList[0]):
                cmds.select(selCurveList[0])
                selJawCurve = selCurveList[0]
                            
            for x in vw_faceSelCluster:
                if re.search('^'+selCurveList[0],x):
                    cmds.showHidden(x+'Handle')
                else:
                    cmds.hide(x+'Handle')

        elif selItemNum == 0:
            print('nothing Select item!!')
    else:
        pass


def clusterFilter():
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve
    global vw_faceSelCluster
    
    vw_faceSelCluster = []
    selCluster = []
    allClusterNameSource = vw_rightCurve+vw_leftCurve+vw_centerCurve
    
    allObjects = cmds.ls(l=True)
    for obj in allObjects:
       if cmds.nodeType(obj) == 'cluster':
         selCluster.append(obj)
    
    for x in allClusterNameSource:
        for y in selCluster:
            if re.search('^'+x,y):
                vw_faceSelCluster.append(y)
            else:
                pass


def finalStep(*args):
    global vw_showCluster
    global vw_faceSelCluster
    global vw_faceEmotionData
    global vw_selItemIndex
    global vw_facialListGuide
    global vw_facialList
    global vw_headObject
    global vw_rightCurve
    global vw_centerCurve
    global vw_leftCurve

    confirmMsg = cmds.confirmDialog( title='Confirm',icn='question',message='Are you ok?', button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
    
    if confirmMsg == 'Yes':  
        blendShapeObj = []
        
        cmds.setAttr(vw_headObject[0]+'.tx',lock=False)
        cmds.setAttr(vw_headObject[0]+'.ty',lock=False)
        cmds.setAttr(vw_headObject[0]+'.tz',lock=False)
        cmds.setAttr(vw_headObject[0]+'.rx',lock=False)
        cmds.setAttr(vw_headObject[0]+'.ry',lock=False)
        cmds.setAttr(vw_headObject[0]+'.rz',lock=False)
        cmds.setAttr(vw_headObject[0]+'.sx',lock=False)
        cmds.setAttr(vw_headObject[0]+'.sy',lock=False)
        cmds.setAttr(vw_headObject[0]+'.sz',lock=False)
        cmds.setAttr(vw_headObject[0]+'.v',lock=False)
          
        headBoundingBox = cmds.xform(vw_headObject,q=True,bb=True)
        headSize = headBoundingBox[3]-headBoundingBox[0]
        progressWin = cmds.window(t='Final Progress')
        cmds.columnLayout()
        progressValue = cmds.progressBar(maxValue=len(vw_facialList)-1, width=300)
        cmds.showWindow( progressWin )
        
        for x in range(len(vw_facialList)):
            cmds.textScrollList('facialControlFaceList',e=True,sii=x+1)
            selectFaceScrollControlCurve()
            cmds.duplicate(str(vw_headObject[0]),rr=True,n=vw_facialList[x])
            cmds.setAttr(vw_facialList[x]+'.translateX',headSize+50)
            blendShapeObj.append(vw_facialList[x])
            cmds.progressBar(progressValue, edit=True, step=1)
        
        cmds.deleteUI(progressWin)
        defaultSetButton()
        selectFaceScrollControlCurve()
        blendShapeObj.append(str(vw_headObject[0]))
        cmds.blendShape(blendShapeObj,n='__Facial_List__')
        blendShapeObj.pop()
        allDelObj = blendShapeObj+vw_faceSelCluster
        AllCurve = vw_rightCurve+vw_leftCurve+vw_centerCurve
        cmds.delete(allDelObj)
        cmds.delete(AllCurve)
        mel.eval('setObjectPickMask "Joint" true;')
        mel.eval('setObjectPickMask "Surface" true;')
        mel.eval('setObjectPickMask "Curve" true;')

        cmds.setAttr(vw_headObject[0]+'.tx',lock=True)
        cmds.setAttr(vw_headObject[0]+'.ty',lock=True)
        cmds.setAttr(vw_headObject[0]+'.tz',lock=True)
        cmds.setAttr(vw_headObject[0]+'.rx',lock=True)
        cmds.setAttr(vw_headObject[0]+'.ry',lock=True)
        cmds.setAttr(vw_headObject[0]+'.rz',lock=True)
        cmds.setAttr(vw_headObject[0]+'.sx',lock=True)
        cmds.setAttr(vw_headObject[0]+'.sy',lock=True)
        cmds.setAttr(vw_headObject[0]+'.sz',lock=True)
        cmds.setAttr(vw_headObject[0]+'.v',lock=False)
                
    elif confirmMsg == 'No':
        pass


def importSourceMesh(*args):
    global vw_sourceMesh
    global vw_targetMesh
    SselObj = cmds.ls(sl=True)
    vw_sourceMesh = SselObj[0]
    cmds.textFieldButtonGrp('importSourceMeshField', e=True, tx=vw_sourceMesh, eb=True)
    copyKeyButtonEn()
      

def importTargetMesh(*args):
    global vw_sourceMesh
    global vw_targetMesh
    TselObj = cmds.ls(sl=True)
    vw_targetMesh = TselObj[0]
    cmds.textFieldButtonGrp('importTargetMeshField', e=True, tx=vw_targetMesh, eb=True)
    copyKeyButtonEn()


def copyKeyProcess(*args):
    global vw_sourceMesh
    global vw_targetMesh
    sourceAttrList = []
    targetAttrList = []
    sourceBlndfind = []
    targetBlndfind = []
    sourceListHis = cmds.listHistory(vw_sourceMesh)
    sourceBlndfind = cmds.ls(sourceListHis, typ='blendShape')
    sourceAttrList = cmds.listAttr(sourceBlndfind[0]+".w", m=True)
    targetListHis = cmds.listHistory(vw_targetMesh)
    targetBlndfind = cmds.ls(targetListHis, typ='blendShape')
    targetAttrList = cmds.listAttr(targetBlndfind[0]+".w", m=True)
    copyProgressWin = cmds.window(t='Progress')
    cmds.columnLayout()
    copyProgressValue = cmds.progressBar(maxValue=len(targetAttrList)-1, width=300)
    cmds.showWindow(copyProgressWin)

    for x in sourceAttrList:
        for y in targetAttrList:
            if re.search(x+'$', y):
                cmds.copyKey(sourceBlndfind[0]+'.'+x)
                cmds.pasteKey(targetBlndfind[0]+'.'+y)
                cmds.progressBar(copyProgressValue, edit=True, step=1)
            else:
                pass
    cmds.deleteUI(copyProgressWin)


def copyKeyButtonEn():
    global vw_sourceMesh
    global vw_targetMesh
    if vw_sourceMesh == ' ' or vw_targetMesh == ' ':
        cmds.button('copyKeyBtn', e=True, en=False)
    elif vw_sourceMesh != ' ' and vw_targetMesh != ' ':
        cmds.button('copyKeyBtn', e=True, en=True)


if __name__ == '__main__':
    vw_rightCurve = []
    vw_centerCurve = []
    vw_leftCurve = []
    vw_showCluster = []
    vw_hideCluster = []
    vw_faceSelCluster = []
    vw_headObject = ' '
    vw_faceEmotionData = []
    vw_selItemIndex = [1]
    vw_selClusterPosTemp = []
    vw_sourceMesh = ' '
    vw_targetMesh = ' '
    if vw_fileTemp == []:
        pass
    else:
        vw_fileTemp[0] = []
    facialSetCreateModeWin()
