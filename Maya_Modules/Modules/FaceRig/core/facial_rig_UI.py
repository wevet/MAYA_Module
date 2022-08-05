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

mayaVersion = ['2018', '2019', '2020', '2022', '2023']
num = int(num)
numNb = num
for v in mayaVersion:
    if num >= 2018:
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
import xtrasUI
import func_recorder
import UKDP_AER
from cleaner import correct_custom_name
from func_creation import *
from func_animEditMode import *
from xtrasUI import *
from func_recorder import *

importlib.reload(cleaner)
importlib.reload(func_creation)
importlib.reload(func_animEditMode)
importlib.reload(xtrasUI)
importlib.reload(func_recorder)
importlib.reload(UKDP_AER)

class FaceRigMainUI:
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

    def show_ui(self):
        window = mc.window('RIG', title='Custom Facial Rig v 1.0', resizeToFitChildren=False, h=900, sizeable=True, w=395)
        mc.columnLayout(adj=True)
        self.menu_bar_ui()
        self.entry()
        self.tab_layout_ui()
        mc.setParent('..')
        mc.frameLayout(labelVisible=0)
        mc.button(l='Menu (各要素のリサイズや置き換えをサポート、表情付けの前に使用します）', c=launch_XTRAS_menu_ui)
        mc.textScrollList('HiddenTMPNodeList', vis=0, h=30)
        mc.textScrollList('RecordPosCtrl', vis=0, h=30)
        mc.setParent('..')
        mc.showWindow(window)

    def menu_bar_ui(self):
        menuBarLayout = mc.menuBarLayout(menuBarVisible=True, po=True)
        mc.menu(label='File Mode')
        mc.menuItem(label='Edit Mode', c=go_to_edit_mode)
        mc.menuItem(label='Anim Mode', c=go_to_anim_mode)
        mc.separator(w=5, style='in')
        mc.menu(label='Help')
        mc.menuItem(label='About / Contact', c=help_bar_about)

    def entry(self):
        mc.columnLayout()
        mc.rowLayout(nc=2)
        mc.separator(w=90, style='none')
        mc.separator(w=210, h=20, style='in')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=35, style='none')
        mc.text(fn='boldLabelFont', w=320, l='FACIAL RIG')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=90, style='none')
        mc.separator(w=210, h=20, style='in')
        mc.setParent('..')
        mc.setParent('..')

    def tab_layout_ui(self):
        mc.tabLayout(tv=0)
        tabs = mc.tabLayout(innerMarginWidth=1, innerMarginHeight=1, cr=20, h=700, w=385, scr=1)
        child1 = mc.frameLayout(labelVisible=0)
        self.creation_placement()
        self.user_replace_ui()
        self.attach_new_system()
        mc.setParent('..')
        child2 = mc.frameLayout(labelVisible=0)
        self.add_to_current_skin_ui(version)
        self.add_new_part_on_your_rig()
        mc.setParent('..')
        child3 = mc.frameLayout(labelVisible=0)
        self.make_the_facial_controller_ui()
        self.mouth_blend_shape_menu_ui()
        self.blend_shape_menu_ui()
        self.attach_to_facial_controller()
        mc.setParent('..')
        child4 = mc.frameLayout(labelVisible=0)
        self.other_menu_ui()
        mc.setParent('..')
        mc.tabLayout(tabs, edit=True, tabLabel=((child1, 'Setup And Creation'), (child2, 'Make Skin'), (child3, 'Make Blend shape'), (child4, 'Others')))
        mc.setParent('..')

    def creation_placement(self):
        mc.frameLayout(l='I - Creation and Placement', collapsable=1, collapse=0, labelVisible=1)
        mc.text(l='Curveを選択し、Side. Typeを定義します。', fn='boldLabelFont')
        self.curve_select()
        self.side_creation_ui()
        self.type_creation_ui()
        self.select_shape_control_creation_ui()

    def curve_select(self):
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Curve select:', fn='boldLabelFont')
        mc.separator(w=25, style='none')
        mc.textScrollList('curveSelList', w=170, h=20)
        mc.separator(w=5, style='none')
        mc.button(l='Add', w=80, c=func_creation.add_sel_curve_creation)
        mc.setParent('..')
        mc.separator(style='double')

    def side_creation_ui(self):
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

    def type_creation_ui(self):
        mc.rowLayout(nc=2)
        mc.separator(w=170, style='none')
        mc.text(l='Type: ', fn='boldLabelFont')
        mc.setParent('..')
        mc.radioCollection('typeRadioGrp')
        mc.rowLayout(nc=9)
        mc.separator(w=16, style='none')
        rb1 = mc.radioButton('eyeBrow', l='EyeBrow')
        mc.separator(w=1, style='none')
        rb2 = mc.radioButton('upperLid', l='UpperLid')
        mc.separator(w=1, style='none')
        rb3 = mc.radioButton('lowerLid', l='LowerLid')
        mc.separator(w=1, style='none')
        rb4 = mc.radioButton('upperCheeks', l='UpperCheeks')
        mc.separator(w=1, style='none')
        mc.setParent('..')
        mc.rowLayout(nc=9)
        mc.separator(w=15, style='none')
        rb5 = mc.radioButton('cheeks', l='Cheeks')
        mc.separator(w=5, style='none')
        rb6 = mc.radioButton('nose', l='Nose')
        mc.separator(w=10, style='none')
        rb7 = mc.radioButton('crease', l='Crease')
        mc.separator(w=7, style='none')
        rb8 = mc.radioButton('upperLip', l='UpperLip')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        rb9 = mc.radioButton('lowerLip', l='LowerLip')
        mc.separator(w=2, style='none')
        rb10 = mc.radioButton('custom', l='Custom')
        mc.setParent('..')
        mc.radioCollection('typeRadioGrp', edit=True, select=rb1)
        mc.rowLayout(nc=2)
        mc.separator(w=40, style='none')
        mc.text(l='Custom Nameは、この命名規則に従ってください。:', fn='boldLabelFont')
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
            mc.textField('otherNameList', w=150, h=20, tcc=cleaner.correct_custom_name)
        else:
            mc.textField('otherNameList', w=150, h=20)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='double')

    def select_shape_control_creation_ui(self):
        mc.text('シェイプコントローラーの種類を選択します。', fn='boldLabelFont')
        mc.iconTextRadioCollection('ctrlShapeGrp')
        mc.rowLayout(nc=8)
        mc.separator(w=20, style='none')
        rbc1 = mc.iconTextRadioButton('sphere', l='Sphere', i='../icons/sphereF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc2 = mc.iconTextRadioButton('circle', l='Circle', i='../icons/circleF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc3 = mc.iconTextRadioButton('triangle', l='Triangle', i='../icons/triangleF.png', st='iconAndTextHorizontal')
        mc.separator(w=5, style='none')
        rbc4 = mc.iconTextRadioButton('custom', l='Custom', i='../icons/interrogationPoint.png', st='iconAndTextHorizontal')
        mc.setParent('..')
        mc.iconTextRadioCollection('ctrlShapeGrp', edit=True, select=rbc1)
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Custom Control:', fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.textScrollList('otherCtrlShapeList', w=150, h=20)
        mc.separator(w=5, style='none')
        mc.button(l='Add', w=80, c=func_creation.add_control_to_curve_creation)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='Enter the number of controller:', fn='boldLabelFont')
        mc.separator(w=20, style='none')
        mc.intField('range', min=3, max=99, v=3, w=30)
        mc.separator(w=18, style='none')
        mc.button(l='Create system', w=100, c=func_creation.create_system_on_curve_selected)
        mc.setParent('..')
        mc.setParent('..')

    def user_replace_ui(self):
        mc.frameLayout('II - User Replace Position Controller System', collapsable=1, collapse=1)
        mc.frameLayout('How To:', collapsable=1, collapse=1)
        mc.text(l='作成したコントローラを選択し、textFieldに入力します。')
        mc.text(l='and tweak his position with the slider \n make the same thing for others if you need it \n after that, you need to click on rebuild EP position curve \n doing the same thing for each curves even \n if you do not move controllers')
        mc.separator(style='in')
        mc.setParent('..')
        mc.separator(style='none')
        mc.text('フェイシャルで作られたコントローラーを選択し、"Get All Controller"をクリックします。')
        mc.button(l='Get All Controller', c=get_all_controllers_on_curves)
        mc.separator(style='double')
        mc.rowLayout(nc=2)
        mc.separator(w=20, style='none')
        mc.text(l='Controllers available for this curve:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        mc.textScrollList('CtrlOnCurve', h=90, w=150, sc=send_UValue_to_slider_replace_controller)
        mc.separator(w=20, style='none')
        mc.columnLayout()
        mc.floatSliderGrp('replaceCtrlSys', w=150, min=0.0, max=1, v=0, field=1, cw2=(40, 300), pre=3, cc=change_UValue_of_controller, dc=change_UValue_of_controller)
        mc.rowLayout(nc=2)
        mc.text(l='Active Symmetry:', en=1)
        mc.checkBox('CheckBox Symmetry OnRebuildEP', l='', en=1)
        mc.setParent('..')
        mc.button('rebuildCrvBtn', l='rebuild EP position curve', w=150, c=rebuild_EP_position_curve)
        mc.button('restoreCrvBtn', l='Restore To Original Curve', w=150, en=0, c=restore_to_original_curve)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')

    def attach_new_system(self):
        mc.frameLayout(l='III - Attach the new system on your model', collapsable=1, collapse=1, w=330)
        mc.rowLayout(nc=2)
        mc.separator(w=60, style='none')
        mc.text(l='異なる要素を追加して、実行します')
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Head joint:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        mc.textScrollList('headSelList', w=150, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=add_head_joint)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Head Ctrl:', fn='boldLabelFont')
        mc.separator(w=21, style='none')
        mc.textScrollList('headCtrlList', w=150, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=add_head_controller)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=20, style='none')
        mc.text(l='Custom Ctrl:', fn='boldLabelFont')
        mc.separator(w=8, style='none')
        mc.textScrollList('CustomCtrlList', w=150, h=50)
        mc.separator(w=10, style='none')
        mc.columnLayout()
        mc.button(l='Add', w=80, c=add_control_list)
        mc.button(l='Remove', w=80, c=remove_control_list)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='double', h=5)
        mc.rowLayout(nc=2)
        mc.separator(w=35, style='none')
        mc.button(l='Validate The Head Part Settings', w=300, c=execute_head)
        mc.setParent('..')
        mc.setParent('..')

    def add_to_current_skin_ui(self, version: int):
        mc.frameLayout(l='Skin method')
        if num == 'yes':
            mc.frameLayout(l='Reminder:', collapsable=1, collapse=1)
            mc.text(l='Reminder:', fn='boldLabelFont')
            mc.text(l='Bind SkinでGeodesic Voxelを使用した場合、スキンを削除する必要があります。')
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
        mc.button(l='Add', w=80, c=add_head_geometry)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text(l='New joint:', fn='boldLabelFont')
        mc.separator(w=28, style='none')
        mc.textScrollList('jntListScript', w=150, h=80)
        mc.separator(w=10, style='none')
        mc.button(l='Refresh', w=80, c=refresh_joint)
        mc.setParent('..')
        if num == 'yes':
            mc.rowLayout(nc=4)
            mc.separator(w=15, style='none')
            mc.button(l='Delete And Make a New Skin', w=160, c=delete_skin_and_make_skin)
            mc.separator(w=10, style='none')
            mc.button(l='Add To Current Skin', w=160, c=add_to_current_skin)
            mc.setParent('..')
        else:
            mc.button(l='Add To Current Skin', c=add_to_current_skin)

    def add_new_part_on_your_rig(self):
        mc.frameLayout(l='Only If you have already use add to current', collapsable=1, collapse=0)
        mc.text(l='追加Partが必要な場合のみ必要です。')
        mc.text(l='注意事項 Head Geometry FieldにHead Geometry を追加してください。')
        mc.rowLayout(nc=6)
        mc.separator(w=5, style='none')
        mc.text(l='Additionnal Part:', fn='boldLabelFont')
        mc.separator(w=1, style='none')
        mc.textScrollList('addAdditionnalCtrl', w=150, h=60)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.button(l='Add', w=80, c=add_button_of_additional_part)
        mc.button(l='Remove', w=80, c=remove_button_of_additional_part)
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='in')
        mc.button(l='Validate Additionnal Part', c=validate_additional_part)
        mc.separator(style='double')
        mc.setParent('..')
        mc.button(l='Skin Tool', c=skin_tool)
        mc.setParent('..')

    def make_the_facial_controller_ui(self):
        mc.frameLayout(l='I - Make The Facial Controller', collapsable=1, collapse=0)
        mc.frameLayout(l='How To:', collapsable=1, collapse=1)
        mc.text(l='すべてのブレンドシェイプが接続されたフェイシャル・コントローラーを用意します。')
        mc.separator(style='in')
        mc.text(l='To Do this:', fn='boldLabelFont')
        mc.text(l='Head Controllerを選択し、"Head Ctrl "Fieldに入力します。\n その後、"Make Facial Controller "をクリックします。\n それを移動して、"Confirm Position" をクリックします。', fn='boldLabelFont')
        mc.separator(style='in')
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(style='none', w=5)
        mc.text(l='Head Controller:', fn='boldLabelFont')
        mc.separator(style='none', w=10)
        mc.textScrollList('headCtrlBlendShape', w=155, h=20)
        mc.separator(style='none', w=5)
        mc.button(l='Add', w=80, c=add_head_controller_to_ui_blend_shape)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=4)
        mc.separator(style='none', w=30)
        mc.button(l='Make Facial Controller', w=150, c=facial_controller_expression)
        mc.separator(style='none', w=5)
        mc.button(l='Confirm Position', w=150, c=valid_position_of_facial_controller_expression)
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='使用する前に、各Ctrlの回転と並進に値がないことを確認してください。', fn='boldLabelFont')
        mc.button(l='各ControllerとJointの間にScale Constraintを追加します。', c=add_scale_constraint_on_each_controller)
        mc.setParent('..')

    def mouth_blend_shape_menu_ui(self):
        mc.frameLayout(l='II - BlendShape For Improve Mouth Mouvement', collapsable=1, collapse=1)
        mc.separator(h=5, style='none')
        self.mouth_blend_shape_general_list()
        mc.separator(style='double')
        self.mouth_blend_shape_creation_ui()
        mc.setParent('..')

    def mouth_blend_shape_general_list(self):
        mc.frameLayout(l='A - List Of Existing Blend Shape Mouth and Edit', collapsable=1, collapse=0)
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
        mc.button(l='Refresh', w=80, c=refresh_build_mouth_Crv_list)
        mc.button(l='Delete', w=80, c=delete_build_mouth_selected)
        mc.setParent('..')
        mc.setParent('..')
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='If you need to fix a Blend Shape orient after the symmetry, \n select it in text scroll list and click "Help To Fix"', fn='boldLabelFont')
        mc.button(l='Help To Fix', c=help_to_fix_build_Sym_menu_mouth)
        mc.setParent('..')

    def mouth_blend_shape_creation_ui(self):
        mc.text('Add your Jaw joint:', fn='boldLabelFont')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text('Jaw Joint:', fn='boldLabelFont')
        mc.separator(w=10, style='none')
        mc.textScrollList('jawJntList2', w=170, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=add_jaw_joint_lip2)
        mc.setParent('..')
        mc.rowLayout(nc=6)
        mc.separator(w=15, style='none')
        mc.text('Jaw Ctrl:', fn='boldLabelFont')
        mc.separator(w=17, style='none')
        mc.textScrollList('jawCtrlList', w=170, h=20)
        mc.separator(w=10, style='none')
        mc.button(l='Add', w=80, c=add_jaw_control_for_record)
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=2)
        mc.separator(w=15, style='none')
        mc.text(l='Select the type:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=70, style='none')
        mc.radioButtonGrp('nameAttr', label='', labelArray3=['Open', 'Side', 'Twist'], numberOfRadioButtons=3, cw4=[10, 60, 60, 60], sl=1, cc=hide_ui_mouth_option)
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
        mc.button('recordMouthExpUIBtn', l='Record This Mouth Expression', c=launch_recorder_mouth_ui)

    def blend_shape_menu_ui(self):
        mc.frameLayout(l='III - Make BlendShape', collapsable=1, collapse=1)
        self.make_general_blend_shape_ui()
        mc.separator(style='double')
        self.blend_shape_general_list()
        mc.setParent('..')

    def blend_shape_general_list(self):
        mc.frameLayout(l='B - List Of ReExisting Blend Shape:', collapsable=1, collapse=0)
        mc.rowLayout(nc=2)
        mc.separator(w=20, style='none')
        mc.text('List of Blend Shape Curve:', fn='boldLabelFont')
        mc.setParent('..')
        mc.rowLayout(nc=4)
        mc.separator(w=5, style='none')
        mc.textScrollList('listBldCrv', w=165, h=150, ams=True, sc=get_blend_curve_value)
        mc.separator(w=5, style='none')
        mc.rowLayout(nc=3)
        mc.columnLayout()
        mc.button(l='Refresh', w=80, c=refresh_build_Crv_list)
        mc.button(l='Select', w=80, c=select_build_Crv_list)
        mc.button(l='Delete', w=80, c=delete_select_build_Crv_list)
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
        mc.button(l='Search', w=80, c=search_by_name)
        mc.setParent('..')
        mc.rowLayout(nc=2)
        mc.separator(w=5, style='none')
        mc.text(l='Blend ShapeをBlend Shape List Curveで選択し、テストします。')
        mc.setParent('..')
        mc.separator(style='in')
        mc.rowLayout(nc=4)
        mc.separator(w=15, style='none')
        mc.text(l='Test it:', fn='boldLabelFont')
        mc.separator(w=15, style='none')
        mc.floatSliderGrp('testIt', w=250, min=0.0, max=1, v=0, field=1, cw2=(40, 300), pre=3, cc=test_blend_shape)
        mc.setParent('..')
        mc.separator(style='in')
        mc.text(l='If you need to fix a Blend Shape orient after the symmetry, \n select it in text scroll list and click "Help To Fix"', fn='boldLabelFont')
        mc.button(l='Help To Fix', c=help_to_fix_build_symmetry_menu)
        mc.setParent('..')

    def make_general_blend_shape_ui(self):
        mc.frameLayout(l='A - Make Blend Shape (Record Your actual Expression)', collapsable=1, collapse=0)
        mc.button('recorderBldExp', l='Record This Expression', c=launch_recorder_ui)
        mc.separator(style='double')
        mc.button('ValidateExpButton', l='Validate your expression', w=150, en=0, c=validate_recorder)
        mc.separator(style='double')
        mc.setParent('..')

    def attach_to_facial_controller(self):
        mc.frameLayout(labelVisible=0)
        mc.separator(style='in')
        mc.text(l='When you have make some Blend Shape click on:', fn='boldLabelFont')
        mc.rowLayout(nc=2)
        mc.separator(style='none', w=33)
        mc.button(l='Connect / Reload Blend Shape To Facial Controller', w=300, c=attach_and_organize_cc_facial)
        mc.setParent('..')
        mc.separator(style='none')
        mc.setParent('..')

    def other_menu_ui(self):
        mc.text(l='Eye Section:', fn='boldLabelFont')
        self.realistic_eyelid_ui()

    def realistic_eyelid_ui(self):
        mc.frameLayout(l='Make Realistic Eye Rig', collapsable=1, collapse=0)
        mc.text(l='This part use the script of UKDP based on Marco Giordano tutorial')
        mc.button(l='Launch The script', c=launch_marco_ui)
        mc.setParent('..')

class RecordExpressionsUI:
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
        mc.button(l='Record with this selection', w=135, c=record_with_selection)
        mc.separator(w=15, style='none')
        mc.button(l='Record with all curves', w=135, c=record_with_all_curves)
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(window)

class RecordExpressionsUIMouth:
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
        mc.button(l='Record with this selection', w=135, c=record_with_selection_mouth)
        mc.separator(w=15, style='none')
        mc.button(l='Record with all curves', w=135, c=record_with_all_curves_mouth)
        mc.separator(w=10, style='none')
        mc.setParent('..')
        mc.setParent('..')
        mc.showWindow(window)

class HelpToFixBuildUI:
    def __init__(self):
        if mc.window('HelpToFixMouthUI', exists=True):
            mc.deleteUI('HelpToFixMouthUI')
        window = mc.window('HelpToFixMouthUI', title='Help To Fix your Symmetrical Blend Shape on the rotation:', resizeToFitChildren=True, fw=1, mxb=False, w=345, h=200)
        mc.frameLayout(labelVisible=0)
        mc.separator(style='double')
        mc.rowLayout(nc=5)
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Available Type:')
        mc.textScrollList('TypeMouth', w=120, h=80, sc=load_mouth_build_curve)
        mc.setParent('..')
        mc.separator(w=5, style='none')
        mc.columnLayout()
        mc.text(l='Available Curves:')
        mc.textScrollList('CrvOfTypeMouth', w=180, h=80, sc=load_locator_recorder_select_in_help_to_fix_mouth_ui)
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
        mc.button(l='Fix For Selected', w=120, c=fix_build_locator_selected)
        mc.separator(w=5, style='none')
        mc.button(l='Fix For All', w=120, c=fix_build_locator_all)
        mc.setParent('..')
        mc.separator(h=10, style='none')
        mc.setParent('..')
        mc.showWindow(window)

def launch_recorder_expression_mouth_ui(*args):
    RecordExpressionsUIMouth()

def get_blend_curve_value(*args):
    crv = mc.textScrollList('listBldCrv', q=1, si=1)
    if len(crv) > 0:
        mc.select(crv, r=True)
        crv = mc.ls(sl=1)[0]
        info = crv.split('_')
        bld = '%s_%s_bldExp' % (info[0], info[1])
        if info[2] == 'Open':
            mc.warning('Open Blend ShapeをTestスライダーでテストすることはできませんので、Head ControllerのOpenMouthアトリビュートを使用してください。')
        getValue = mc.getAttr('%s.%s' % (bld, crv))
        mc.floatSliderGrp('testIt', e=1, v=getValue)

def hide_ui_mouth_option(*args):
    sel = mc.radioButtonGrp('nameAttr', q=1, sl=1)
    if sel == 4:
        mc.radioButtonGrp('axisRot2', e=1, en=0)
        mc.floatField('MaxValueActivation', e=1, en=0)
    else:
        mc.radioButtonGrp('axisRot2', e=1, en=1)
        mc.floatField('MaxValueActivation', e=1, en=1)

def search_by_name(*args):
    mc.textScrollList('listBldCrv', e=True, da=True)
    bldList = mc.textScrollList('listBldCrv', q=True, ai=True)
    searchName = mc.textField('searchByName', q=True, tx=True)
    mc.select(cl=1)
    mc.select('*%s*_bld_crv' % searchName, r=True)
    try:
        mc.select('*%s*bldExp*bld_crv' % searchName, d=True)
    except ZeroDivisionError:
        pass
    try:
        mc.select('*%s*bld*bld_crv' % searchName, d=True)
    except ZeroDivisionError:
        pass

    listCrv = mc.ls(sl=1)
    for crv in listCrv:
        for bldCrv in bldList:
            if crv == bldCrv:
                mc.textScrollList('listBldCrv', e=True, ams=True, si=crv)
                break

def help_bar_about(*args):
    #launchAboutMenu()
    pass

def launch_recorder_mouth_ui(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                go_to_edit_mode()
            crvListOK = []
            jawJnt = ''
            jawCtrl = ''
            try:
                jawJnt = mc.textScrollList('jawJntList2', q=True, ai=True)[0]
            except ZeroDivisionError:
                pass

            try:
                jawCtrl = mc.textScrollList('jawCtrlList', q=True, ai=True)[0]
            except ZeroDivisionError:
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
                    except ZeroDivisionError:
                        pass

                if len(testExists) == 0:
                    mc.select('*crv', r=True)
                    mc.select('*crvShape', d=True)
                    try:
                        mc.select('*_bld_crv', d=True)
                    except ZeroDivisionError:
                        pass

                    crvList = mc.ls(sl=1)
                    for crv in crvList:
                        name = crv.split('crv')[0]
                        if mc.objExists(name + 'ctrlGrp'):
                            if mc.objExists(name + 'grpOff'):
                                if mc.objExists(name + '1_jnt'):
                                    crvListOK.append(crv)

                    if len(crvListOK) > 0:
                        launch_recorder_expression_mouth_ui()
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
                    mc.error('その属性には、すでに1つまたは複数の式が記録されています。%s, 新しいものを作成する前にそれらを削除してください。' % attr)
            else:
                mc.error('新しいエクスプレッションを作成する前に、jaw CtrlとjawJntを追加してください。')
        else:
            mc.error('最適化モードを使用している場合、新しいブレンドシェイプ・エクスプレッションを作成することはできません。')
    else:
        mc.error('フェイシャルコントローラーを作成する必要があります。')

def launch_recorder_ui(*args):
    ctrlFacial = 'Facial_Rig_ctrl'
    if mc.objExists(ctrlFacial):
        checkMode = mc.getAttr('%s.mode' % ctrlFacial)
        if checkMode != 2:
            if checkMode == 1:
                go_to_edit_mode()
            crvListOK = []
            try:
                mc.select('*crv', r=True)
                mc.select('*crvShape', d=True)
                try:
                    mc.select('*_bld_crv', d=True)
                except ZeroDivisionError:
                    pass

                crvList = mc.ls(sl=1)
                for crv in crvList:
                    name = crv.split('crv')[0]
                    if mc.objExists(name + 'ctrlGrp'):
                        if mc.objExists(name + 'grpOff'):
                            if mc.objExists(name + '1_jnt'):
                                crvListOK.append(crv)

                record_expressions = RecordExpressionsUI()
                print("show record_expressions")
                for crv in crvListOK:
                    side = crv.split('_')[0]
                    if side == 'L':
                        mc.textScrollList('LeftRecordCrvsList', e=1, a=crv)
                    elif side == 'R':
                        mc.textScrollList('RightRecordCrvsList', e=1, a=crv)
                    else:
                        mc.textScrollList('CenterRecordCrvsList', e=1, a=crv)
                return crvListOK
            except ZeroDivisionError:
                raise mc.error('no system found')
        else:
            mc.error('最適化モードを使用している場合、新しいブレンドシェイプ・エクスプレッションを作成することはできません。')
    else:
        mc.error('フェイシャルコントローラーを作成する必要があります。')

def help_to_fix_build_symmetry_menu(*args):
    elts = []
    try:
        elts = mc.textScrollList('listBldCrv', q=True, si=True, ams=True)
    except ZeroDivisionError:
        pass

    if len(elts) > 0:
        HelpToFixBuildUI()
        listOfType = []
        for sel in elts:
            type = sel.split('_')[2]
            test = 'yes'
            length = len(listOfType)
            if length > 0:
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

def help_to_fix_build_symmetry_menu_mouth(*args):
    elts = []
    try:
        elts = mc.textScrollList('listBldCrvMouth', q=True, ams=True, si=True)
    except ZeroDivisionError:
        pass

    if len(elts) > 0:
        HelpToFixBuildUI()
        for sel in elts:
            mc.textScrollList('TypeMouth', e=True, a=sel)

def load_mouth_build_curve(*args):
    mc.textScrollList('RecLocList', e=True, ra=True)
    type = mc.textScrollList('TypeMouth', q=True, si=True)[0]
    mc.textScrollList('CrvOfTypeMouth', e=True, ra=True)
    mc.select('*%s_bld_crv' % type, r=True)
    try:
        mc.select('*bld_*%s*_bld_crv' % type, d=True)
    except ZeroDivisionError:
        pass
    try:
        mc.select('*bldExp_*%s*_bld_crv' % type, d=True)
    except ZeroDivisionError:
        pass

    sel = mc.ls(sl=1)
    for elt in sel:
        mc.textScrollList('CrvOfTypeMouth', e=True, a=elt)

def load_locator_recorder_select_in_help_to_fix_mouth_ui(*args):
    mc.textScrollList('RecLocList', e=True, ra=True)
    sel = mc.textScrollList('CrvOfTypeMouth', q=True, si=True)[0]
    info = sel.split('_')
    mc.select('%s_%s_*_%s_bld_recorder' % (info[0], info[1], info[2]), r=True)
    locList = mc.ls(sl=1)
    for loc in locList:
        mc.textScrollList('RecLocList', e=True, a=loc)

def launch_marco_ui(*args):
    UKDP_AER.autoEyelidsRig.show_ui()

"""
face_rig = FaceRigMainUI()
face_rig.show_ui()
"""


