# -*- coding: utf-8 -*-

import sys
import os
import maya.cmds as mc
import maya.mel as mel
from pymel import versions
version = versions.current()
version = str(version)
num = ''
for i in range(4):
    if version[i].isdigit():
        num = num + version[i]

mayaVersion = ['2017', '2018', '2019', '2020', '2022', '2023']
num = int(num)
numNb = num
for v in mayaVersion:
    if num >= 2017:
        num = 'yes'

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
paths = sys.path
folderList = ['utils', 'proc', 'icons', 'ui']
for fold in folderList:
    newPath = '%s\\%s' % (PROJECT_DIR, fold)
    result = 'no'
    for path in paths:
        if path == newPath:
            result = 'no'
            break
        else:
            result = 'yes'
    if result == 'yes':
        sys.path.append(os.path.join(PROJECT_DIR, fold))

import cleaner
import importlib
import func_creation
import func_animEditMode
import about
import xtrasUI
import func_recorder
import UKDP_AER
from cleaner import correctCustomName
from func_creation import *
from func_animEditMode import *
from about import *
from xtrasUI import *
from func_recorder import *

importlib.reload(cleaner)
importlib.reload(func_creation)
importlib.reload(func_animEditMode)
importlib.reload(about)
importlib.reload(xtrasUI)
importlib.reload(func_recorder)
importlib.reload(UKDP_AER)

class UI():
    def __init__(self):
        if mc.window('RIG', exists=True):
            mc.deleteUI('RIG')
        if mc.window('RIG', exists=True):
            mc.deleteUI('RIG')
        if mc.window('CustomBlendWindow', exists=True):
            mc.deleteUI('CustomBlendWindow')
        if mc.window('XtrasMenu', exists=True):
            mc.deleteUI('XtrasMenu')
        if mc.window('SkinDetached', exists=True):
            mc.deleteUI('SkinDetached')
        if mc.window('NewExpUI', exists=True):
            mc.deleteUI('NewExpUI')
        if mc.window('BlendShapeUICCFacial', exists=True):
            mc.deleteUI('BlendShapeUICCFacial')
        if mc.window('BlendShapeUIRecorder', exists=True):
            mc.deleteUI('BlendShapeUIRecorder')
        if mc.window('BlendShapeUIRecorderMouth', exists=True):
            mc.deleteUI('BlendShapeUIRecorderMouth')
        if mc.window('HelpToFixUI', exists=True):
            mc.deleteUI('HelpToFixUI')
        if mc.window('ComeBackToEditUI', exists=True):
            mc.deleteUI('ComeBackToEditUI')
        if mc.window('ComeBackToEditMouthUI', exists=True):
            mc.deleteUI('ComeBackToEditMouthUI')
        if mc.window('HelpToFixUIMouth', exists=True):
            mc.deleteUI('HelpToFixUIMouth')
        if mc.window('saveClone', exists=True):
            mc.deleteUI('saveClone')
        if mc.window('ReplaceCtrl', exists=True):
            mc.deleteUI('ReplaceCtrl')
        window = mc.window('RIG', title='Speed Facial Rig v 2.0 Lite', resizeToFitChildren=False, h=900, sizeable=True, w=395)
        mc.columnLayout(adj=True)
        self.menuBarUI()
        self.entete()
        self.tabLayoutUI()
        mc.setParent('..')
        mc.frameLayout(labelVisible=0)
        mc.button(l='XTRAS Menu \n(help to resize and replace each element, \nwill be used before facial expression)', c=launchXtrasMenuUI)
        mc.textScrollList('HiddenTMPNodeList', vis=0, h=30)
        mc.textScrollList('RecordPosCtrl', vis=0, h=30)
        mc.setParent('..')
        mc.showWindow(window)

    def menuBarUI(self):
        menuBarLayout = mc.menuBarLayout(menuBarVisible=True, po=True)
        mc.menu(label='File Mode')
        mc.menuItem(label='Edit Mode', c=goToEditMode)
        mc.menuItem(label='Anim Mode', c=goToAnimMode)
        mc.separator(w=5, style='in')
        mc.menu(label='Help')
        mc.menuItem(label='About / Contact', c=helpBarAbout)

    def entete(self):
        mc.columnLayout()
        mc.rowLayout(nc=2)
        mc.separator(w=90, style='none')
        mc.separator(w=210, h=20, style='in')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=35, style='none')
        mc.text(fn='boldLabelFont', w=320, l='SPEED FACIAL RIG Lite')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=90, style='none')
        mc.separator(w=210, h=20, style='in')
        mc.setParent('..')
        mc.setParent('..')

    def tabLayoutUI(self):
        mc.tabLayout(tv=0)
        tabs = mc.tabLayout(innerMarginWidth=1, innerMarginHeight=1, cr=20, h=700, w=385, scr=1)
        child1 = mc.frameLayout(labelVisible=0)
        self.creationPlacement()
        self.userReplaceUI()
        self.attachNewSystem()
        mc.setParent('..')
        child2 = mc.frameLayout(labelVisible=0)
        self.addToCurrentSkinUI(version)
        self.addNewPartOnYourRig()
        mc.setParent('..')
        child3 = mc.frameLayout(labelVisible=0)
        self.makeTheFacialControllerUI()
        self.mouthBlendShapeMenuUI()
        self.blendShapeMenuUI()
        self.attachToFacialController()
        mc.setParent('..')
        child4 = mc.frameLayout(labelVisible=0)
        self.OthersMenuUI()
        mc.setParent('..')
        mc.tabLayout(tabs, edit=True, tabLabel=((child1, 'Setup And Creation'), (child2, 'Make Skin'), (child3, 'Make Blendshape'), (child4, 'Others')))
        mc.setParent('..')

    def creationPlacement(self):
        mc.frameLayout(l='I - Creation and Placement', collapsable=1, collapse=0, labelVisible=1)
        mc.text(l='Select your curve and define side and type', fn='boldLabelFont')
        self.curveSel()
        self.sideCreationUI()
        self.typeCreationUI()
        self.selShapeCtrlCreationUI()

    def curveSel(self):
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Curve sel:', fn='boldLabelFont')
        mc.separator(w=25, style='none')
        mc.textScrollList('curveSelList', w=170, h=20)
        mc.separator(w=5, style='none')
        mc.button(l='Add', w=80, c=func_creation.addSelCurveCreation)
        mc.setParent('..')
        mc.separator(style='double')

    def sideCreationUI(self):
        mc.columnLayout()
        mc.rowLayout(nc=2)
        mc.separator(w=170, style='none')
        mc.text(l='Side: ', fn='boldLabelFont')
        mc.setParent('..')
        mc.separator(h=10, style='double')
        mc.rowLayout(nc=4)
        mc.separator(w=17, style='none')
        mc.radioButtonGrp('sideRadio', label='', labelArray3=['L', 'C', 'R'], numberOfRadioButtons=3, cw4=[30, 60, 60, 10], sl=2)
        mc.separator(w=55, style='none')
        mc.checkBox('mirrorCheck', l='Create Mirror')
        mc.setParent('..')
        mc.separator(style='double')

    def typeCreationUI(self):
        mc.rowLayout(nc=2)
        mc.separator(w=170, style='none')
        mc.text(l='Type: ', fn='boldLabelFont')
        mc.setParent('..')
        mc.radioCollection('typeRadioGrp')
        mc.rowLayout(nc=9)
        mc.separator(w=16, style='none')
        rb1 = mc.radioButton('eyeBrow', l='EyeBrow    ')
        mc.separator(w=1, style='none')
        rb2 = mc.radioButton('upperLid', l='UpperLid   ')
        mc.separator(w=1, style='none')
        rb3 = mc.radioButton('lowerLid', l='LowerLid   ')
        mc.separator(w=1, style='none')
        rb4 = mc.radioButton('upperCheeks', l='UpperCheeks')
        mc.separator(w=1, style='none')
        mc.setParent('..')
        mc.rowLayout(nc=9)
        mc.separator(w=15, style='none')
        rb5 = mc.radioButton('cheeks', l='Cheeks     ')
        mc.separator(w=5, style='none')
        rb6 = mc.radioButton('nose', l='Nose       ')
        mc.separator(w=10, style='none')
        rb7 = mc.radioButton('crease', l='Crease     ')
        mc.separator(w=7, style='none')
        rb8 = mc.radioButton('upperLip', l='UpperLip   ')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        rb9 = mc.radioButton('lowerLip', l='LowerLip   ')
        mc.separator(w=2, style='none')
        rb10 = mc.radioButton('custom', l='Custom     ')
        mc.setParent('..')
        mc.radioCollection('typeRadioGrp', edit=True, select=rb1)
        mc.rowLayout(nc=2)
        mc.separator(w=40, style='none')
        mc.text(l='For your custom name, please respect this nomenclature:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=135, style='none')
        mc.text(l='up_mouth = "BAD" ', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=133, style='none')
        mc.text(l='upMouth = "GOOD"', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        mc.text(l='Custom name:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        if numNb >= 2016:
            mc.textField('otherNameList', w=150, h=20, tcc=cleaner.correctCustomName)
        else:
            mc.textField('otherNameList', w=150, h=20)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='double')

    def selShapeCtrlCreationUI(self):
        mc.text('Select a type of shape controller', fn='boldLabelFont')
        mc.iconTextRadioCollection('ctrlShapeGrp')
        mc.rowLayout(nc=8)
        mc.separator(w=20, style='none')
        rbc1 = mc.iconTextRadioButton('sphere', l='Sphere', i='sphereF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc2 = mc.iconTextRadioButton('circle', l='Circle', i='circleF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc3 = mc.iconTextRadioButton('triangle', l='Triangle', i='triangleF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc4 = mc.iconTextRadioButton('custom', l='Custom', i='interrogationPoint.png', st='iconAndTextHorizontal')
        mc.setParent('..')
        mc.iconTextRadioCollection('ctrlShapeGrp', edit=True, select=rbc1)
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Custom Control:', fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.textScrollList('otherCtrlShapeList', w=150, h=20)
        mc.separator(w=5, style='none')
        mc.button(l='Add', w=80, c=func_creation.addCtrlToCurveCreation)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Enter the number of controller:', fn='boldLabelFont')
        mc.separator(w=20, style='none')
        mc.intField('range', min=3, max=99, v=3, w=30)
        mc.separator(w=18, style='none')
        mc.button(l='Create system', w=100, c=func_creation.createSystemOnCurveSelected)
        mc.setParent('..')
        mc.setParent('..')

    def userReplaceUI(self):
        mc.frameLayout('II - User Replace Postion Controller System', collapsable=1, collapse=1)
        mc.frameLayout('How To:', collapsable=1, collapse=1)
        mc.text(l='Select a controller made by the upper section\n click on Get Controllers\nselect it into the textField')
        mc.text(l='and tweak his position with the slider\n make the same thing for others if you need it\nafter that, you need to click on rebuild EP position curve\n doing the same thing for each curves even \nif you do not move controllers')
        mc.separator(style='in')
        mc.setParent('..')
        mc.separator(style='none')
        mc.text('Select a controller made by this facial and click to "Get All Controller"')
        mc.button(l='Get All Controller', c=getAllControllersOnCurves)
        mc.separator(style='double')
        mc.rowLayout(nc=2)
        mc.separator(w=20, style='none')
        mc.text(l='Controllers available for this curve:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        mc.textScrollList('CtrlOnCurve', h=90, w=150, sc=sendUValueToSliderReplaceController)
        mc.separator(w=20, style='none')
        mc.columnLayout()
        mc.floatSliderGrp('replaceCtrlSys', w=150, min=0.0, max=1, v=0, field=1, cw2=(40,
                                                                                      300), pre=3, cc=changeUValueOfController, dc=changeUValueOfController)
        mc.rowLayout(nc=2)
        mc.text(l='Active Symetry:', en=1)
        mc.checkBox('CheckBoxSymOnRebuildEP', l='', en=1)
        mc.setParent('..')
        mc.button('rebuildCrvBtn', l='rebuild EP position curve', w=150, c=rebuildEPPosCurve)
        mc.button('restoreCrvBtn', l='Restore To Original Curve', w=150, en=0, c=restoreToOriginalCurve)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')

    def attachNewSystem(self):
        mc.frameLayout(l='III - Attach the new system on your model', collapsable=1, collapse=1, w=330)
        mc.rowLayout(nc=2)
        mc.separator(w=60, style='none')
        mc.text(l='Add the different element and click on Execute')
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Head joint:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        mc.textScrollList('headSelList', w=150, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=addHeadJnt)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Head Ctrl:', fn='boldLabelFont')
        mc.separator(w=21, style='none')
        mc.textScrollList('headCtrlList', w=150, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=addHeadCtrl)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Custom Ctrl:', fn='boldLabelFont')
        mc.separator(w=8, style='none')
        mc.textScrollList('CustomCtrlList', w=150, h=50)
        mc.separator(w=10, style='none')
        mc.columnLayout()
        mc.button(l='Add', w=80, c=addCtrlList)
        mc.button(l='Remove', w=80, c=removeCtrlList)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='double', h=5)
        mc.rowLayout(nc=2)
        mc.separator(w=35, style='none')
        mc.button(l='Validate The Head Part Settings', w=300, c=executeHead)
        mc.setParent('..')
        mc.setParent('..')

    def addToCurrentSkinUI(version, self):
        mc.frameLayout(l='Skin method')
        if num == 'yes':
            mc.frameLayout(l='Reminder:', collapsable=1, collapse=1)
            mc.text(l='Reminder:', fn='boldLabelFont')
            mc.text(l='if you have used Geodesic Voxel method on "Bind Skin",\n you need to delete your skin, click on:')
            mc.text(l='"Delete And Make a New Skin"', fn='boldLabelFont')
            mc.text(l="or if you haven't choose this option click on:")
            mc.text(l='"ADD TO CURRENT SKIN"', fn='boldLabelFont')
            mc.separator(style='double')
            mc.setParent('..')
        mc.text(l='Select your skinned head geometry')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Head Geo:', fn='boldLabelFont')
        mc.separator(w=28, style='none')
        mc.textScrollList('headGeoList', w=150, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=addHeadGeo)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='New joint:', fn='boldLabelFont')
        mc.separator(w=28, style='none')
        mc.textScrollList('jntListScript', w=150, h=80)
        mc.separator(w=10, style='none')
        mc.button(l='Refresh', w=80, c=refreshJnt)
        mc.setParent('..')
        if num == 'yes':
            mc.rowLayout(nc=4)
            mc.separator(w=15, style='none')
            mc.button(l='Delete And Make a New Skin', w=160, c=deleteSkinAndMakeSkin)
            mc.separator(w=10, style='none')
            mc.button(l='Add To Current Skin', w=160, c=addToCurrentSkin)
            mc.setParent('..')
        else:
            mc.button(l='Add To Current Skin', c=addToCurrentSkin)

    def addNewPartOnYourRig(self):
        mc.frameLayout(l='Only If you have already use add to current', collapsable=1, collapse=0)
        mc.text(l='This part is only requiered if you need to add additionnal part')
        mc.text(l='Reminder: Add your head geo into the head geo field')
        mc.rowLayout(nc=6)
        mc.separator(w=5, style='none')
        mc.text(l='Additionnal Part:', fn='boldLabelFont')
        mc.separator(w=1, style='none')
        mc.textScrollList('addAdditionnalCtrl', w=150, h=60)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.button(l='Add', w=80, c=addBtnOfAdditionnalPart)
        mc.button(l='Remove', w=80, c=removeBtnOfAdditionnalPart)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='in')
        mc.button(l='Validate Additionnal Part', c=validateAdditionnalPart)
        mc.separator(style='double')
        mc.setParent('..')
        mc.button(l='Skin Tool', c=SkinTool)
        mc.setParent('..')

    def makeTheFacialControllerUI(self):
        mc.frameLayout(l='I - Make The Facial Controller', collapsable=1, collapse=0)
        mc.frameLayout(l='How To:', collapsable=1, collapse=1)
        mc.text(l='In First, you need to have a Facial Controller, \nwho every blendshape were connected')
        mc.separator(style='in')
        mc.text(l='To Do this:', fn='boldLabelFont')
        mc.text(l='select your head controller and put it into the "Head Ctrl" field\nAfter that click on "Make Facial Controller"\nMove it and click on "Confirm Position"', fn='boldLabelFont')
        mc.separator(style='in')
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(style='none', w=5)
        mc.text(l='Head Controller:', fn='boldLabelFont')
        mc.separator(style='none', w=10)
        mc.textScrollList('headCtrlBlendShape', w=155, h=20)
        mc.separator(style='none', w=5)
        mc.button(l='Add', w=80, c=addHeadControllerToUINlendShape)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=4)
        mc.separator(style='none', w=30)
        mc.button(l='Make Facial Controller', w=150, c=facialControllerExpression)
        mc.separator(style='none', w=5)
        mc.button(l='Confirm Position', w=150, c=validPositionOfFacialControllerExpression)
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='Becarefull before to use this, \nbe sure to have no value on rotation \nand translation on each controller', fn='boldLabelFont')
        mc.button(l='Add Scale Constaint Between Each Controller And Joint', c=addScaleConstraintOnEachController)
        mc.setParent('..')

    def mouthBlendShapeMenuUI(self):
        mc.frameLayout(l='II - BlendShape For Improve Mouth Mouvement', collapsable=1, collapse=1)
        mc.separator(h=5, style='none')
        self.mouthBlendShapeGeneralList()
        mc.separator(style='double')
        self.mouthBlendShapeCreationUI()
        mc.setParent('..')

    def mouthBlendShapeGeneralList(self):
        mc.frameLayout(l='A - List Of Existing BlendShape Mouth and Edit', collapsable=1, collapse=0)
        mc.rowLayout(nc=2)
        mc.separator(w=75, style='none')
        mc.text('list of Blend Shape Mouth correction:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=5, style='none')
        mc.textScrollList('listBldCrvMouth', w=170, h=90, ams=True)
        mc.separator(w=5, style='none')
        mc.rowLayout(nc=2)
        mc.columnLayout()
        mc.button(l='Refresh', w=80, c=refreshBldMouthCrvList)
        mc.button(l='Delete', w=80, c=deleteBldMouthSelected)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='If you need to fix a blendshape orient after the symetry, \nselect it in text scroll list and click "Help To Fix"', fn='boldLabelFont')
        mc.button(l='Help To Fix', c=helpToFixBldSymMenuMouth)
        mc.setParent('..')

    def mouthBlendShapeCreationUI(self):
        mc.text('Add your Jaw joint:', fn='boldLabelFont')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text('Jaw Joint:', fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.textScrollList('jawJntList2', w=170, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=addJawJntLip2)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text('Jaw Ctrl:', fn='boldLabelFont')
        mc.separator(w=17, style='none')
        mc.textScrollList('jawCtrlList', w=170, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=addJawCtrlForRecord)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=2)
        mc.separator(w=15, style='none')
        mc.text(l='Select the type:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=70, style='none')
        mc.radioButtonGrp('nameAttr', label='', labelArray3=['Open', 'Side', 'Twist'], numberOfRadioButtons=3, cw4=[10, 60, 60, 60], sl=1, cc=HideUIMouthOption)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=2)
        mc.separator(w=15, style='none')
        mc.text(l='Set the axis rotation of your jaw joint:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=55, style='none')
        mc.radioButtonGrp('axisRot2', label='', labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, cw4=[20, 70, 70, 70], sl=1)
        mc.setParent('..')
        mc.text(l='Set in degrees the maximum value activation of your expression')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Maximum value of activation:', fn='boldLabelFont')
        mc.separator(w=5, style='none')
        mc.floatField('MaxValueActivation', w=50, pre=3, min=1, max=150, v=35)
        mc.separator(style='none', w=10)
        mc.checkBox('NegValueMouthCreation', l='Neg Value?')
        mc.setParent('..')
        mc.separator(style='in')
        mc.button('recordMouthExpUIBtn', l='Record This Mouth Expression', c=launchRecorderMouthUI)

    def blendShapeMenuUI(self):
        mc.frameLayout(l='III - Make BlendShape', collapsable=1, collapse=1)
        self.makeGeneralBlendShapeUI()
        mc.separator(style='double')
        self.blendShapeGeneralList()
        mc.setParent('..')

    def blendShapeGeneralList(self):
        mc.frameLayout(l='B - List Of reExisting Blendshape:', collapsable=1, collapse=0)
        mc.rowLayout(nc=2)
        mc.separator(w=20, style='none')
        mc.text('List of Blend Shape Curve:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=5, style='none')
        mc.textScrollList('listBldCrv', w=165, h=150, ams=True, sc=getBldCrvValue)
        mc.separator(w=5, style='none')
        mc.rowLayout(nc=3)
        mc.columnLayout()
        mc.button(l='Refresh', w=80, c=refreshBldCrvList)
        mc.button(l='Select', w=80, c=selectBldCrvList)
        mc.button(l='Delete', w=80, c=deleteSelBldCrvList)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=6)
        mc.separator(w=5, style='none')
        mc.text(l='Select by search:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        mc.textField('searchByName', w=150, fn='boldLabelFont')
        mc.separator(w=8, style='none')
        mc.button(l='Search', w=80, c=searchByName)
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=5, style='none')
        mc.text(l='Select your blendshape into the BlendShape List Curve and test it')
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        mc.text(l='Test it:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        mc.floatSliderGrp('testIt', w=250, min=0.0, max=1, v=0, field=1, cw2=(40, 300), pre=3, cc=testBlendShape)
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='If you need to fix a blendshape orient after the symetry, \nselect it in text scroll list and click "Help To Fix"', fn='boldLabelFont')
        mc.button(l='Help To Fix', c=helpToFixBldSymMenu)
        mc.setParent('..')

    def makeGeneralBlendShapeUI(self):
        mc.frameLayout(l='A - Make Blendshape (Record Your actual Expression)', collapsable=1, collapse=0)
        mc.button('recorderBldExp', l='Record This Expression', c=launchRecorderUI)
        mc.separator(style='double')
        mc.button('ValidateExpButton', l='Validate your expression', w=150, en=0, c=validateRecorder)
        mc.separator(style='double')
        mc.setParent('..')

    def attachToFacialController(self):
        mc.frameLayout(labelVisible=0)
        mc.separator(style='in')
        mc.text(l='When you have make some blendShape click on:', fn='boldLabelFont')
        mc.rowLayout(nc=2)
        mc.separator(style='none', w=33)
        mc.button(l='Connect / Reload Blendshape To Facial Controller', w=300, c=AttachAndOrganizeCCFacial)
        mc.setParent('..')
        mc.separator(style='none')
        mc.setParent('..')

    def OthersMenuUI(self):
        mc.text(l='Eye Section:', fn='boldLabelFont')
        self.RealisticEyeLidUI()

    def RealisticEyeLidUI(self):
        mc.frameLayout(l='Make Realistic Eye Rig', collapsable=1, collapse=0)
        mc.text(l='This part use the script of UKDP based on Marco Giordano tutorial')
        mc.button(l='Launch The script', c=lauchMarcoUI)
        mc.setParent('..')

class recordExpressionsUI():
    def __init__(self):
        if mc.window('BlendShapeUIRecorder', exists=True):
            mc.deleteUI('BlendShapeUIRecorder')
        window = mc.window('BlendShapeUIRecorder', title='Record BlendShape Position for:', resizeToFitChildren=True, fw=1, mxb=False, w=345, h=200)
        mc.frameLayout(labelVisible=0)
        mc.text(l='Select each curve you want to record', fn='boldLabelFont')
        mc.text(l='Available curves to Record')
        mc.rowLayout(nc=7)
        mc.separator(w=10, style='none')
        mc.columnLayout()
        mc.text(l='Left Side:', fn='boldLabelFont')
        mc.textScrollList('LeftRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Center Side:', fn='boldLabelFont')
        mc.textScrollList('CenterRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Right Side:', fn='boldLabelFont')
        mc.textScrollList('RightRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.separator(style='double')
        mc.rowLayout(nc=5)
        mc.separator(style='none', w=28)
        mc.button(l='Record with this selection', w=135, c=recordWithSelection)
        mc.separator(w=15, style='none')
        mc.button(l='Record with all curves', w=135, c=recordWithAllCurves)
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(window)

class recordExpressionsUIMouth():
    def __init__(self):
        if mc.window('BlendShapeUIRecorderMouth', exists=True):
            mc.deleteUI('BlendShapeUIRecorderMouth')
        window = mc.window('BlendShapeUIRecorderMouth', title='Record BlendShape Mouth Position for:', resizeToFitChildren=True, fw=1, mxb=False, w=345, h=200)
        mc.frameLayout(labelVisible=0)
        mc.text(l='Select each curve you want to record', fn='boldLabelFont')
        mc.text(l='Available curves to Record')
        mc.rowLayout(nc=7)
        mc.separator(w=10, style='none')
        mc.columnLayout()
        mc.text(l='Left Side:', fn='boldLabelFont')
        mc.textScrollList('LeftRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Center Side:', fn='boldLabelFont')
        mc.textScrollList('CenterRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Right Side:', fn='boldLabelFont')
        mc.textScrollList('RightRecordCrvsList', ams=True, w=100, h=70)
        mc.setParent('..')
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.separator(style='double')
        mc.rowLayout(nc=5)
        mc.separator(style='none', w=28)
        mc.button(l='Record with this selection', w=135, c=recordWithSelectionMouth)
        mc.separator(w=15, style='none')
        mc.button(l='Record with all curves', w=135, c=recordWithAllCurvesMouth)
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(window)

class HelpToFixBldUI():
    def __init__(self):
        if mc.window('HelpToFixMouthUI', exists=True):
            mc.deleteUI('HelpToFixMouthUI')
        window = mc.window('HelpToFixMouthUI', title='Help To Fix your symetrical blendshape on the rotation:', resizeToFitChildren=True, fw=1, mxb=False, w=345, h=200)
        mc.frameLayout(labelVisible=0)
        mc.separator(style='double')
        mc.rowLayout(nc=5)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Available Type:')
        mc.textScrollList('TypeMouth', w=120, h=80, sc=loadMouthBldCrv)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Available Curves:')
        mc.textScrollList('CrvOfTypeMouth', w=180, h=80, sc=loadLocRecorderSelInHelpToFixMouthUI)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.setParent('..')
        mc.separator(style='double')
        mc.text(l='Choose your axis to Repair:', fn='boldLabelFont')
        mc.rowLayout(nc=2)
        mc.separator(w=40, style='none')
        mc.radioButtonGrp('AxisToRepair', label='', labelArray3=['X', 'Y', 'Z'], numberOfRadioButtons=3, cw4=[20, 70, 70, 70], sl=1)
        mc.setParent('..')
        mc.text(l='You can fix the axis for each controller or for all')
        mc.separator(style='in')
        mc.text(l='Recorder locator list:')
        mc.rowLayout(nc=3)
        mc.separator(w=20, style='none')
        mc.textScrollList('RecLocList', w=280, h=80, ams=True)
        mc.separator(w=20, style='none')
        mc.setParent('..')
        mc.rowLayout(nc=5)
        mc.separator(w=35, style='none')
        mc.button(l='Fix For Selected', w=120, c=fixBldLocSelected)
        mc.separator(w=5, style='none')
        mc.button(l='Fix For All', w=120, c=fixBldLocAll)
        mc.setParent('..')
        mc.separator(h=10, style='none')
        mc.setParent('..')
        mc.showWindow(window)

def launchRecorderExpressionMouthUI(*args):
    recordExpressionsUIMouth()

def getBldCrvValue(*args):
    crv = mc.textScrollList('listBldCrv', q=1, si=1)
    if len(crv) > 0:
        mc.select(crv, r=True)
        crv = mc.ls(sl=1)[0]
        info = crv.split('_')
        bld = '%s_%s_bldExp' % (info[0], info[1])
        if info[2] == 'Open':
            mc.warning('you cannot test your Open blendshape with Test It slider, please use the open mouth attribute into your head controller')
        getValue = mc.getAttr('%s.%s' % (bld, crv))
        mc.floatSliderGrp('testIt', e=1, v=getValue)

def HideUIMouthOption(*args):
    sel = mc.radioButtonGrp('nameAttr', q=1, sl=1)
    if sel == 4:
        mc.radioButtonGrp('axisRot2', e=1, en=0)
        mc.floatField('MaxValueActivation', e=1, en=0)
    else:
        mc.radioButtonGrp('axisRot2', e=1, en=1)
        mc.floatField('MaxValueActivation', e=1, en=1)

def searchByName(*args):
    mc.textScrollList('listBldCrv', e=True, da=True)
    bldList = mc.textScrollList('listBldCrv', q=True, ai=True)
    searchName = mc.textField('searchByName', q=True, tx=True)
    mc.select(cl=1)
    mc.select('*%s*_bld_crv' % searchName, r=True)
    try:
        mc.select('*%s*bldExp*bld_crv' % searchName, d=True)
    except:
        pass

    try:
        mc.select('*%s*bld*bld_crv' % searchName, d=True)
    except:
        pass

    listCrv = mc.ls(sl=1)
    for crv in listCrv:
        for bldCrv in bldList:
            if crv == bldCrv:
                mc.textScrollList('listBldCrv', e=True, ams=True, si=crv)
                break

def helpBarAbout(*args):
    launchAboutMenu()

def launchRecorderMouthUI(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvListOK = []
            jawJnt = ''
            jawCtrl = ''
            try:
                jawJnt = mc.textScrollList('jawJntList2', q=True, ai=True)[0]
            except:
                pass

            try:
                jawCtrl = mc.textScrollList('jawCtrlList', q=True, ai=True)[0]
            except:
                pass

            if jawCtrl != '' and jawJnt != '':
                attr = mc.radioButtonGrp('nameAttr', q=True, sl=True)
                if attr == 1:
                    attr = 'Open'
                else:
                    if attr == 2:
                        attr = 'Side'
                    elif attr == 3:
                        attr = 'Twist'
                    else:
                        attrNb = mc.radioButtonGrp('nameAttrJaw', q=True, sl=True)
                        if attrNb == 1:
                            attr = 'jaw'
                        elif attrNb == 2:
                            attr = 'jawNeg'
                        else:
                            attr = 'jawDown'
                    testExists = []
                    try:
                        testExists = mc.ls('*%s*_bld_crv' % attr)
                    except:
                        pass

                if len(testExists) == 0:
                    mc.select('*crv', r=True)
                    mc.select('*crvShape', d=True)
                    try:
                        mc.select('*_bld_crv', d=True)
                    except:
                        pass

                    crvList = mc.ls(sl=1)
                    for crv in crvList:
                        name = crv.split('crv')[0]
                        if mc.objExists(name + 'ctrlGrp'):
                            if mc.objExists(name + 'grpOff'):
                                if mc.objExists(name + '1_jnt'):
                                    crvListOK.append(crv)

                    if len(crvListOK) > 0:
                        launchRecorderExpressionMouthUI()
                        for crv in crvListOK:
                            side = crv.split('_')[0]
                            if side == 'L':
                                mc.textScrollList('LeftRecordCrvsList', e=1, a=crv)
                            elif side == 'R':
                                mc.textScrollList('RightRecordCrvsList', e=1, a=crv)
                            else:
                                mc.textScrollList('CenterRecordCrvsList', e=1, a=crv)

                        return crvListOK
                else:
                    mc.error('one or many expression was already recorded for the %s attribute, please delete them before to create a new one' % attr)
            else:
                mc.error('please add the jaw ctrl and the jawJnt before trying to create a new expression')
        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')

def launchRecorderUI(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                goToEditMode()
            crvListOK = []
            try:
                mc.select('*crv', r=True)
                mc.select('*crvShape', d=True)
                try:
                    mc.select('*_bld_crv', d=True)
                except:
                    pass

                crvList = mc.ls(sl=1)
                for crv in crvList:
                    name = crv.split('crv')[0]
                    if mc.objExists(name + 'ctrlGrp'):
                        if mc.objExists(name + 'grpOff'):
                            if mc.objExists(name + '1_jnt'):
                                crvListOK.append(crv)

                recordExpressionsUI()
                for crv in crvListOK:
                    side = crv.split('_')[0]
                    if side == 'L':
                        mc.textScrollList('LeftRecordCrvsList', e=1, a=crv)
                    elif side == 'R':
                        mc.textScrollList('RightRecordCrvsList', e=1, a=crv)
                    else:
                        mc.textScrollList('CenterRecordCrvsList', e=1, a=crv)

                return crvListOK
            except:
                raise mc.error('no system found')

        else:
            mc.error('you cannot create a new blendshape expression if you have use the optimize mode')
    else:
        mc.error('you need to create the facial controller')

def helpToFixBldSymMenu(*args):
    elts = []
    try:
        elts = mc.textScrollList('listBldCrv', q=True, si=True, ams=True)
    except:
        pass

    if len(elts) > 0:
        HelpToFixBldUI()
        listOfType = []
        for sel in elts:
            type = sel.split('_')[2]
            test = 'yes'
            lenght = len(listOfType)
            if lenght > 0:
                for elt in listOfType:
                    if elt == type:
                        test = 'no'
                        break
                    else:
                        test = 'yes'

                if test == 'yes':
                    listOfType.append(type)
            else:
                listOfType.append(type)

        for typ in listOfType:
            mc.textScrollList('TypeMouth', e=True, a=typ)

def helpToFixBldSymMenuMouth(*args):
    elts = []
    try:
        elts = mc.textScrollList('listBldCrvMouth', q=True, ams=True, si=True)
    except:
        pass

    if len(elts) > 0:
        HelpToFixBldUI()
        for sel in elts:
            mc.textScrollList('TypeMouth', e=True, a=sel)

def loadMouthBldCrv(*args):
    mc.textScrollList('RecLocList', e=True, ra=True)
    type = mc.textScrollList('TypeMouth', q=True, si=True)[0]
    mc.textScrollList('CrvOfTypeMouth', e=True, ra=True)
    mc.select('*%s_bld_crv' % type, r=True)
    try:
        mc.select('*bld_*%s*_bld_crv' % type, d=True)
    except:
        pass

    try:
        mc.select('*bldExp_*%s*_bld_crv' % type, d=True)
    except:
        pass

    sel = mc.ls(sl=1)
    for elt in sel:
        mc.textScrollList('CrvOfTypeMouth', e=True, a=elt)

def loadLocRecorderSelInHelpToFixMouthUI(*args):
    mc.textScrollList('RecLocList', e=True, ra=True)
    sel = mc.textScrollList('CrvOfTypeMouth', q=True, si=True)[0]
    info = sel.split('_')
    mc.select('%s_%s_*_%s_bld_recorder' % (info[0], info[1], info[2]), r=True)
    locList = mc.ls(sl=1)
    for loc in locList:
        mc.textScrollList('RecLocList', e=True, a=loc)

def lauchMarcoUI(*args):
    UKDP_AER.autoEyelidsRig.UI()

UI()
