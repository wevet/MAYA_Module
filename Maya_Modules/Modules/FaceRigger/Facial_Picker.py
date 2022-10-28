# -*- coding: utf-8 -*-

import os
import maya.cmds as cmds
import maya.mel as mel
import sys
from shiboken2 import wrapInstance
from PySide2 import QtCore
from PySide2 import QtUiTools
from PySide2 import QtWidgets
import maya.OpenMayaUI as omui

class UndoContext(object):

    def __enter__(self):
        cmds.undoInfo(openChunk=True)

    def __exit__(self, *exc_info):
        cmds.undoInfo(closeChunk=True)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class Facial_Picker_window(QtWidgets.QMainWindow):

    @classmethod
    def main(cls):
        global picker_ui
        try:
            picker_ui.close()
            picker_ui.deleteLater()
        except:
            pass

        picker_ui = Facial_Picker_window()
        picker_ui.show()

    def __init__(self, parent=maya_main_window()):
        super(Facial_Picker_window, self).__init__(parent)
        self.setWindowTitle('FaceRig Picker')
        self.setFixedSize(705, 611)
        self.styles = 'Plastique'
        self.init_ui()
        self.create_layout()
        self.create_connections()
        self.green = 'background-color: rgb(051,153,102)'
        self.red = 'background-color: rgb(255,0,051)'
        self.gray = [0.15, 0.15, 0.15]
        self.blue = 'background-color: rgb(0,102,153)'
        self.magenta = 'background-color: rgb(204,0,102)'
        self.yellow = 'background-color: rgb(255,255,0)'
        self.white = 'background-color: rgb(255,255,255)'
        self.np = ''
        self.shift = 0
        self.name_space_combo_update()
        self.update_CV_command()

    def init_ui(self):
        self.current_dir = os.path.dirname(__file__)
        f = QtCore.QFile(self.current_dir + '/ui/Facial_Picker.ui')
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        self.setCentralWidget(self.ui)
        f.close()
        image_path = self.current_dir + '/icon/Facial_image.png'
        self.ui.Label_image.setPixmap(image_path)
        return

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)
        self.ui.BtnGrp.setStyle(QtWidgets.QStyleFactory.create(self.styles))

    def create_connections(self):
        self.ui.P_L_brow_Btn.clicked.connect(self.left_brow_command)
        self.ui.P_L_brow_02_Btn.clicked.connect(self.left_brow_02_command)
        self.ui.P_L_brow_03_Btn.clicked.connect(self.left_brow_03_command)
        self.ui.P_L_medial_fibers_brow_Btn.clicked.connect(self.left_medial_fibers_brow_command)
        self.ui.P_L_lateral_fibers_brow_Btn.clicked.connect(self.left_lateral_fibers_brow_command)
        self.ui.P_L_procerus_brow_Btn.clicked.connect(self.left_procerus_brow_command)
        self.ui.P_R_brow_Btn.clicked.connect(self.right_brow_command)
        self.ui.P_R_brow_02_Btn.clicked.connect(self.right_brow_02_command)
        self.ui.P_R_brow_03_Btn.clicked.connect(self.right_brow_03_command)
        self.ui.P_R_medial_fibers_brow_Btn.clicked.connect(self.right_medial_fibers_brow_command)
        self.ui.P_R_lateral_fibers_brow_Btn.clicked.connect(self.right_lateral_fibers_brow_command)
        self.ui.P_R_procerus_brow_Btn.clicked.connect(self.right_procerus_brow_command)
        self.ui.P_Center_brow_Btn.clicked.connect(self.center_brow_command)
        self.ui.P_L_brow_master_Btn.clicked.connect(self.left_brow_master_command)
        self.ui.P_R_brow_master_Btn.clicked.connect(self.right_brow_master_command)
        self.ui.P_L_eye_blink_Btn.clicked.connect(self.left_eye_blink_command)
        self.ui.P_R_eye_blink_Btn.clicked.connect(self.right_eye_blink_command)
        self.ui.P_L_eye_lower_Btn.clicked.connect(self.left_eye_lower_command)
        self.ui.P_R_eye_lower_Btn.clicked.connect(self.right_eye_lower_command)
        self.ui.P_L_eye_lacrimal_Btn.clicked.connect(self.left_eye_lacrimal_command)
        self.ui.P_L_eye_lacrimal_upper_Btn.clicked.connect(self.left_eye_lacrimal_upper_command)
        self.ui.P_L_eye_lacrimal_lower_Btn.clicked.connect(self.left_eye_lacrimal_lower_command)
        self.ui.P_L_eye_back_Btn.clicked.connect(self.left_eye_back_command)
        self.ui.P_L_eye_back_upper_Btn.clicked.connect(self.left_eye_back_upper_command)
        self.ui.P_L_eye_back_lower_Btn.clicked.connect(self.left_eye_back_lower_command)
        self.ui.P_L_eye_double_Btn.clicked.connect(self.left_eye_double_command)
        self.ui.P_R_eye_lacrimal_Btn.clicked.connect(self.right_eye_lacrimal_command)
        self.ui.P_R_eye_lacrimal_upper_Btn.clicked.connect(self.right_eye_lacrimal_upper_command)
        self.ui.P_R_eye_lacrimal_lower_Btn.clicked.connect(self.right_eye_lacrimal_lower_command)
        self.ui.P_R_eye_back_Btn.clicked.connect(self.right_eye_back_command)
        self.ui.P_R_eye_back_upper_Btn.clicked.connect(self.right_eye_back_upper_command)
        self.ui.P_R_eye_back_lower_Btn.clicked.connect(self.right_eye_back_lower_command)
        self.ui.P_R_eye_double_Btn.clicked.connect(self.R_eye_double_BtnCmd)
        self.ui.P_L_eye_target_Btn.clicked.connect(self.L_eye_target_BtnCmd)
        self.ui.P_R_eye_target_Btn.clicked.connect(self.R_eye_target_BtnCmd)
        self.ui.P_Eye_target_Master_Btn.clicked.connect(self.Eye_target_Master_BtnCmd)
        self.ui.P_Eye_World_point_Btn.clicked.connect(self.Eye_World_point_BtnCmd)
        self.ui.P_L_Eye_World_point_Btn.clicked.connect(self.L_Eye_World_point_BtnCmd)
        self.ui.P_R_Eye_World_point_Btn.clicked.connect(self.R_Eye_World_point_BtnCmd)
        self.ui.P_L_nose_Btn.clicked.connect(self.L_nose_BtnCmd)
        self.ui.P_L_nasalis_transverse_nose_Btn.clicked.connect(self.L_nasalis_transverse_nose_BtnCmd)
        self.ui.P_L_procerus_nose_Btn.clicked.connect(self.L_procerus_nose_BtnCmd)
        self.ui.P_L_nasolabial_fold_nose_Btn.clicked.connect(self.L_nasolabial_fold_nose_BtnCmd)
        self.ui.P_R_nasalis_transverse_nose_Btn.clicked.connect(self.R_nasalis_transverse_nose_BtnCmd)
        self.ui.P_R_procerus_nose_Btn.clicked.connect(self.R_procerus_nose_BtnCmd)
        self.ui.P_R_nasolabial_fold_nose_Btn.clicked.connect(self.R_nasolabial_fold_nose_BtnCmd)
        self.ui.P_R_nose_Btn.clicked.connect(self.R_nose_BtnCmd)
        self.ui.P_Nose_Btn.clicked.connect(self.Nose_BtnCmd)
        self.ui.P_Lower_nose_Btn.clicked.connect(self.Lower_nose_BtnCmd)
        self.ui.P_depressor_septi_nose_Btn.clicked.connect(self.depressor_septi_nose_BtnCmd)
        self.ui.P_L_cheek_Btn.clicked.connect(self.L_cheek_BtnCmd)
        self.ui.P_R_cheek_Btn.clicked.connect(self.R_cheek_BtnCmd)
        self.ui.P_L_upper_cheek_Btn.clicked.connect(self.L_upper_cheek_BtnCmd)
        self.ui.P_R_upper_cheek_Btn.clicked.connect(self.R_upper_cheek_BtnCmd)
        self.ui.P_L_outer_orbicularis_cheek_Btn.clicked.connect(self.L_outer_orbicularis_cheek_BtnCmd)
        self.ui.P_R_outer_orbicularis_cheek_Btn.clicked.connect(self.R_outer_orbicularis_cheek_BtnCmd)
        self.ui.P_L_inner_orbicularis_cheek_Btn.clicked.connect(self.L_inner_orbicularis_cheek_BtnCmd)
        self.ui.P_R_inner_orbicularis_cheek_Btn.clicked.connect(self.R_inner_orbicularis_cheek_BtnCmd)
        self.ui.P_L_lower_cheek_Btn.clicked.connect(self.L_lower_cheek_BtnCmd)
        self.ui.P_R_lower_cheek_Btn.clicked.connect(self.R_lower_cheek_BtnCmd)
        self.ui.P_L_lower_liplid_Btn.clicked.connect(self.L_lower_liplid_BtnCmd)
        self.ui.P_R_lower_liplid_Btn.clicked.connect(self.R_lower_liplid_BtnCmd)
        self.ui.P_L_lip_corner_Btn.clicked.connect(self.L_lip_corner_BtnCmd)
        self.ui.P_R_lip_corner_Btn.clicked.connect(self.R_lip_corner_BtnCmd)
        self.ui.P_L_lip_corner_up_Btn.clicked.connect(self.L_lip_corner_up_BtnCmd)
        self.ui.P_R_lip_corner_up_Btn.clicked.connect(self.R_lip_corner_up_BtnCmd)
        self.ui.P_L_lip_corner_up_FK_Btn.clicked.connect(self.L_lip_corner_up_FK_BtnCmd)
        self.ui.P_R_lip_corner_up_FK_Btn.clicked.connect(self.R_lip_corner_up_FK_BtnCmd)
        self.ui.P_L_lip_corner_down_Btn.clicked.connect(self.L_lip_corner_down_BtnCmd)
        self.ui.P_R_lip_corner_down_Btn.clicked.connect(self.R_lip_corner_down_BtnCmd)
        self.ui.P_L_lip_corner_down_FK_Btn.clicked.connect(self.L_lip_corner_down_FK_BtnCmd)
        self.ui.P_R_lip_corner_down_FK_Btn.clicked.connect(self.R_lip_corner_down_FK_BtnCmd)
        self.ui.P_Upper_lip_Master_Btn.clicked.connect(self.Upper_lip_Master_BtnCmd)
        self.ui.P_Lower_lip_Master_Btn.clicked.connect(self.Lower_lip_Master_BtnCmd)
        self.ui.P_Upper_lip_Btn.clicked.connect(self.Upper_lip_BtnCmd)
        self.ui.P_Lower_lip_Btn.clicked.connect(self.Lower_lip_BtnCmd)
        self.ui.P_Upper_lip_FK_Btn.clicked.connect(self.Upper_lip_FK_BtnCmd)
        self.ui.P_Lower_lip_FK_Btn.clicked.connect(self.Lower_lip_FK_BtnCmd)
        self.ui.P_Lower_lip_outer_Btn.clicked.connect(self.Lower_lip_outer_BtnCmd)
        self.ui.P_L_lip_upper_side_Btn.clicked.connect(self.L_lip_upper_side_BtnCmd)
        self.ui.P_L_lip_upper_side_FK_Btn.clicked.connect(self.L_lip_upper_side_FK_BtnCmd)
        self.ui.P_L_lip_upper_side_02_FK_Btn.clicked.connect(self.L_lip_upper_side_02_FK_BtnCmd)
        self.ui.P_L_lip_upper_outer_Btn.clicked.connect(self.L_lip_upper_outer_BtnCmd)
        self.ui.P_R_lip_upper_side_Btn.clicked.connect(self.R_lip_upper_side_BtnCmd)
        self.ui.P_R_lip_upper_side_FK_Btn.clicked.connect(self.R_lip_upper_side_FK_BtnCmd)
        self.ui.P_R_lip_upper_side_02_FK_Btn.clicked.connect(self.R_lip_upper_side_02_FK_BtnCmd)
        self.ui.P_R_lip_upper_outer_Btn.clicked.connect(self.R_lip_upper_outer_BtnCmd)
        self.ui.P_L_lip_lower_side_Btn.clicked.connect(self.L_lip_lower_side_BtnCmd)
        self.ui.P_L_lip_lower_side_FK_Btn.clicked.connect(self.L_lip_lower_side_FK_BtnCmd)
        self.ui.P_L_lip_lower_side_02_FK_Btn.clicked.connect(self.L_lip_lower_side_02_FK_BtnCmd)
        self.ui.P_L_lip_lower_outer_Btn.clicked.connect(self.L_lip_lower_outer_BtnCmd)
        self.ui.P_R_lip_lower_side_Btn.clicked.connect(self.R_lip_lower_side_BtnCmd)
        self.ui.P_R_lip_lower_side_FK_Btn.clicked.connect(self.R_lip_lower_side_FK_BtnCmd)
        self.ui.P_R_lip_lower_side_02_FK_Btn.clicked.connect(self.R_lip_lower_side_02_FK_BtnCmd)
        self.ui.P_R_lip_lower_outer_Btn.clicked.connect(self.R_lip_lower_outer_BtnCmd)
        self.ui.P_Lip_Master_Btn.clicked.connect(self.Lip_Master_BtnCmd)
        self.ui.P_Jaw_Master_Btn.clicked.connect(self.Jaw_Master_BtnCmd)
        self.ui.P_Lip_FACS_Btn.clicked.connect(self.Lip_FACS_BtnCmd)
        self.ui.P_Lip_FACS_bar_Btn.clicked.connect(self.Lip_FACS_bar_BtnCmd)
        self.ui.P_Lip_FACS_L_bar_Btn.clicked.connect(self.Lip_FACS_L_bar_BtnCmd)
        self.ui.P_Lip_FACS_R_bar_Btn.clicked.connect(self.Lip_FACS_R_bar_BtnCmd)
        self.ui.P_Lip_FACS_upper_bar_Btn.clicked.connect(self.Lip_FACS_upper_bar_BtnCmd)
        self.ui.P_Lip_FACS_lower_bar_Btn.clicked.connect(self.Lip_FACS_lower_bar_BtnCmd)
        self.ui.P_Upper_teeth_Btn.clicked.connect(self.Upper_teeth_BtnCmd)
        self.ui.P_Lower_teeth_Btn.clicked.connect(self.Lower_teeth_BtnCmd)
        self.ui.P_Tongue_Btn.clicked.connect(self.Tongue_BtnCmd)
        self.ui.P_Tongue_02_Btn.clicked.connect(self.Tongue_02_BtnCmd)
        self.ui.P_Tongue_03_Btn.clicked.connect(self.Tongue_03_BtnCmd)
        self.ui.P_Facial_Master_Btn.clicked.connect(self.Facial_Master_BtnCmd)
        self.ui.UpdateCVBtn.clicked.connect(self.name_space_combo_update)
        self.ui.UpdateCVBtn.clicked.connect(self.update_CV_command)
        self.ui.PrimaryCheckBox.stateChanged.connect(self.check_box_state_command)
        self.ui.SecondaryCheckBox.stateChanged.connect(self.check_box_state_command)
        self.ui.MasterCheckBox.stateChanged.connect(self.check_box_state_command)
        self.ui.FKCheckBox.stateChanged.connect(self.check_box_state_command)
        self.ui.OralCavityCheckBox.stateChanged.connect(self.check_box_state_command)
        self.ui.Reset_CtrlBtn.clicked.connect(self.reset_control_command)
        self.ui.SelAll_CtrlBtn.clicked.connect(self.select_all_control_command)
        self.ui.Reset_BrowBtn.clicked.connect(self.reset_brow_command)
        self.ui.Select_BrowBtn.clicked.connect(self.select_brow_command)
        self.ui.Reset_EyeBtn.clicked.connect(self.reset_eye_command)
        self.ui.Select_EyeBtn.clicked.connect(self.select_eye_command)
        self.ui.Reset_EyeTargetBtn.clicked.connect(self.reset_eye_target_command)
        self.ui.Select_EyeTargetBtn.clicked.connect(self.select_eye_target_command)
        self.ui.Reset_NoseBtn.clicked.connect(self.reset_nose_command)
        self.ui.Select_NoseBtn.clicked.connect(self.select_nose_command)
        self.ui.Reset_CheekBtn.clicked.connect(self.reset_cheek_command)
        self.ui.Select_CheekBtn.clicked.connect(self.select_cheek_command)
        self.ui.Reset_LipBtn.clicked.connect(self.reset_lip_command)
        self.ui.Select_LipBtn.clicked.connect(self.select_lip_command)
        self.ui.Reset_OralBtn.clicked.connect(self.reset_oral_command)
        self.ui.Select_OralBtn.clicked.connect(self.select_oral_command)
        self.ui.Reset_LipFollowBtn.clicked.connect(self.reset_lip_follow_command)
        self.ui.Reset_Lip_FACSBtn.clicked.connect(self.reset_lip_FACS_command)
        self.ui.Reset_NoseFollowBtn.clicked.connect(self.reset_nose_follow_command)
        self.ui.Reset_CheekFollowBtn.clicked.connect(self.reset_cheek_follow_command)
        self.ui.Reset_EyeLowerFollowBtn.clicked.connect(self.reset_eye_lower_follow_command)
        self.ui.Reset_BrowFollowBtn.clicked.connect(self.reset_brow_follow_command)
        self.ui.Reset_EyeFollowBtn.clicked.connect(self.reset_eye_follow_command)
        self.ui.NameSpace_Combo.currentTextChanged.connect(self.update_CV_command)

    def name_space_combo_update(self):
        self.ui.NameSpace_Combo.clear()
        self.ui.NameSpace_Combo.addItem('')
        all_nameSpace_list = self.find_all_name_space()
        if all_nameSpace_list:
            for each in all_nameSpace_list:
                self.ui.NameSpace_Combo.addItem(each)

    def find_all_name_space(self):
        all_nameSpace_list = list()
        all_objects = cmds.ls(tr=True)
        if all_objects:
            for each in all_objects:
                if ':' in each:
                    nameSpace_count = each.count(':')
                    full_nameSpace = ''
                    for count in range(nameSpace_count):
                        full_nameSpace = full_nameSpace + each.split(':')[count] + ':'

                    all_nameSpace_list.append(full_nameSpace)

        all_nameSpace_list = list(set(all_nameSpace_list))
        print(all_nameSpace_list)
        return all_nameSpace_list

    def do_something(self):
        any_sel = cmds.ls(sl=True)
        for each in any_sel:
            print(each)
            self.another_dialog.textEdit.setText(each)
            self.ui.lineEdit.setText(each)

    def reset_control_command(self, *args):
        with UndoContext():
            self.reset_lip_command()
            self.reset_lip_follow_command()
            self.reset_lip_FACS_command()
            self.reset_nose_follow_command()
            self.reset_cheek_follow_command()
            self.reset_cheek_command()
            self.reset_eye_lower_follow_command()
            self.reset_nose_command()
            self.reset_brow_command()
            self.reset_eye_command()
            self.reset_brow_follow_command()
            self.reset_eye_target_command()
            self.reset_eye_follow_command()
            self.reset_oral_command()
            if cmds.objExists(self.np + 'Facial_Master_Ctrl'):
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Facial_Master_Ctrl.scaleZ', 1)
            print('All ctrl reset')

    def select_all_control_command(self, *args):
        with UndoContext():
            self.select_brow_command()
            brow_sel_all = cmds.ls(sl=True)
            self.select_eye_command()
            eye_sel_all = cmds.ls(sl=True)
            self.select_eye_target_command()
            eyetarget_sel_all = cmds.ls(sl=True)
            self.select_nose_command()
            nose_sel_all = cmds.ls(sl=True)
            self.select_cheek_command()
            cheek_sel_all = cmds.ls(sl=True)
            self.select_lip_command()
            lip_sel_all = cmds.ls(sl=True)
            self.select_oral_command()
            oral_sel_all = cmds.ls(sl=True)
            cmds.select(brow_sel_all, eye_sel_all, eyetarget_sel_all, nose_sel_all, cheek_sel_all, lip_sel_all, oral_sel_all)

    def reset_brow_command(self, *args):
        if cmds.objExists(self.np + 'Brow_All_Ctrl_grp'):
            self.Brow_All_Ctrl_reset()
            print('Brow ctrl reset')

    def select_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Brow_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + '*brow*ctrl', tgl=True)
                else:
                    cmds.select(self.np + '*brow*ctrl')

    def reset_eye_command(self, *args):
        if cmds.objExists(self.np + 'Eye_All_Ctrl_grp'):
            self.Eye_All_Ctrl_reset()
            print('Eye ctrl reset')

    def select_eye_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Eye_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + '*eye_blink*ctrl', tgl=True)
                    if cmds.objExists(self.np + '*eye_lower*ctrl'):
                        cmds.select(self.np + '*eye_lower*ctrl', add=True)
                    if cmds.objExists(self.np + '*lacrimal*ctrl') and cmds.objExists(self.np + '*back*ctrl'):
                        cmds.select(self.np + '*back*ctrl', self.np + '*lacrimal*ctrl', add=True)
                    if cmds.objExists(self.np + '*double*ctrl'):
                        cmds.select(self.np + '*double*ctrl', add=True)
                else:
                    cmds.select(self.np + '*eye_blink*ctrl')
                    if cmds.objExists(self.np + '*eye_lower*ctrl'):
                        cmds.select(self.np + '*eye_lower*ctrl', add=True)
                    if cmds.objExists(self.np + '*lacrimal*ctrl') and cmds.objExists(self.np + '*back*ctrl'):
                        cmds.select(self.np + '*back*ctrl', self.np + '*lacrimal*ctrl', add=True)
                    if cmds.objExists(self.np + '*double*ctrl'):
                        cmds.select(self.np + '*double*ctrl', add=True)

    def reset_eye_target_command(self, *args):
        if cmds.objExists(self.np + 'Eye_target_All_Ctrl_grp'):
            self.Eye_Target_All_Ctrl_reset()
            print('EyeTarget ctrl reset')

    def select_eye_target_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Eye_target_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + '*target*ctrl', tgl=True)
                    cmds.select(self.np + 'Eye_World_point_loc', add=True)
                    cmds.select(self.np + 'L_Eye_World_point_ctrl', add=True)
                    cmds.select(self.np + 'R_Eye_World_point_ctrl', add=True)
                else:
                    cmds.select(self.np + '*target*ctrl')
                    cmds.select(self.np + 'Eye_World_point_loc', add=True)
                    cmds.select(self.np + 'L_Eye_World_point_ctrl', add=True)
                    cmds.select(self.np + 'R_Eye_World_point_ctrl', add=True)

    def reset_nose_command(self, *args):
        if cmds.objExists(self.np + 'Nose_All_Ctrl_grp'):
            self.Nose_All_Ctrl_reset()
            print('Nose ctrl reset')

    def select_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Nose_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    if cmds.objExists(self.np + '*nose*ctrl'):
                        cmds.select(self.np + '*nose*ctrl', tgl=True)
                    if cmds.objExists(self.np + 'Nose_ctrl'):
                        cmds.select(self.np + 'Nose_ctrl', add=True)
                else:
                    if cmds.objExists(self.np + '*nose*ctrl'):
                        cmds.select(self.np + '*nose*ctrl')
                    if cmds.objExists(self.np + 'Nose_ctrl'):
                        cmds.select(self.np + 'Nose_ctrl', add=True)

    def reset_cheek_command(self, *args):
        if cmds.objExists(self.np + 'Cheek_All_Ctrl_grp'):
            self.Cheek_All_Ctrl_reset()
            print('Cheek ctrl reset')

    def select_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Cheek_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + '*cheek*ctrl', tgl=True)
                    if cmds.objExists(self.np + '*_lower_liplid_ctrl'):
                        cmds.select(self.np + '*_lower_liplid_ctrl', add=True)
                else:
                    cmds.select(self.np + '*cheek*ctrl')
                    if cmds.objExists(self.np + '*_lower_liplid_ctrl'):
                        cmds.select(self.np + '*_lower_liplid_ctrl', add=True)

    def reset_lip_command(self, *args):
        if cmds.objExists(self.np + 'Lip_All_Ctrl_grp'):
            self.Lip_All_Ctrl_reset()
            print('Lip ctrl reset')

    def select_lip_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Jaw_Master_Ctrl', tgl=True)
                    if cmds.objExists(self.np + '*lip*Ctrl'):
                        cmds.select(self.np + '*lip*Ctrl', add=True)
                    if cmds.objExists(self.np + '*lip*side*ctrl'):
                        cmds.select(self.np + '*lip*side*ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_ctrl'):
                        cmds.select(self.np + '*_lip_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_FK_ctrl'):
                        cmds.select(self.np + '*_lip_FK_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_*outer_ctrl'):
                        cmds.select(self.np + '*_lip_*outer_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_Master_ctrl'):
                        cmds.select(self.np + '*_lip_Master_ctrl', add=True)
                    if cmds.objExists(self.np + 'Lip_Master_ctrl'):
                        cmds.select(self.np + 'Lip_Master_ctrl', add=True)
                    if cmds.objExists(self.np + 'Lip_FACS_*bar_ctrl'):
                        cmds.select(self.np + 'Lip_FACS_*bar_ctrl', add=True)
                else:
                    cmds.select(self.np + 'Jaw_Master_Ctrl')
                    if cmds.objExists(self.np + '*lip*Ctrl'):
                        cmds.select(self.np + '*lip*Ctrl', add=True)
                    if cmds.objExists(self.np + '*lip*side*ctrl'):
                        cmds.select(self.np + '*lip*side*ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_ctrl'):
                        cmds.select(self.np + '*_lip_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_FK_ctrl'):
                        cmds.select(self.np + '*_lip_FK_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_*outer_ctrl'):
                        cmds.select(self.np + '*_lip_*outer_ctrl', add=True)
                    if cmds.objExists(self.np + '*_lip_Master_ctrl'):
                        cmds.select(self.np + '*_lip_Master_ctrl', add=True)
                    if cmds.objExists(self.np + 'Lip_Master_ctrl'):
                        cmds.select(self.np + 'Lip_Master_ctrl', add=True)
                    if cmds.objExists(self.np + 'Lip_FACS_*bar_ctrl'):
                        cmds.select(self.np + 'Lip_FACS_*bar_ctrl', add=True)

    def reset_oral_command(self, *args):
        if cmds.objExists(self.np + 'Oral_Cavity_All_Ctrl_grp'):
            self.Oral_Cavity_All_Ctrl_reset()
            print('Oral Cavity ctrl reset')

    def select_oral_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Oral_Cavity_All_Ctrl_grp'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + '*teeth*ctrl', tgl=True)
                    if cmds.objExists(self.np + 'Tongue_*ctrl'):
                        cmds.select(self.np + 'Tongue_*ctrl', add=True)
                else:
                    cmds.select(self.np + '*teeth*ctrl')
                    if cmds.objExists(self.np + 'Tongue_*ctrl'):
                        cmds.select(self.np + 'Tongue_*ctrl', add=True)

    def reset_lip_follow_command(self, *args):
        if cmds.objExists(self.np + 'Lip_All_Ctrl_grp'):
            self.Lip_Connect_Ctrl_reset()
            print('Lip Follow Attribute reset')

    def reset_lip_FACS_command(self, *args):
        if cmds.objExists(self.np + 'Lip_FACS_Ctrl'):
            self.Lip_FACS_Ctrl_reset()
            print('Lip FACS Attribute reset')

    def reset_nose_follow_command(self, *args):
        if cmds.objExists(self.np + 'Lip_All_Ctrl_grp') and cmds.objExists(self.np + 'Nose_All_Ctrl_grp'):
            self.Lip_Nose_Connect_Ctrl_reset()
            print('Lip Nose Follow Attribute reset')

    def reset_cheek_follow_command(self, *args):
        if cmds.objExists(self.np + 'Lip_All_Ctrl_grp') and cmds.objExists(self.np + 'Cheek_All_Ctrl_grp'):
            self.Lip_Cheek_Connect_Ctrl_reset()
            print('Lip Cheek Follow Attribute reset')

    def reset_eye_lower_follow_command(self, *args):
        if cmds.objExists(self.np + 'Cheek_All_Ctrl_grp') and cmds.objExists(self.np + 'Eye_All_Ctrl_grp'):
            self.Cheek_Eye_Connect_Ctrl_reset()
            print('Upper Cheek Eye Lower Follow Attribute reset')

    def reset_brow_follow_command(self, *args):
        if cmds.objExists(self.np + 'Eye_All_Ctrl_grp') and cmds.objExists(self.np + 'Brow_All_Ctrl_grp'):
            self.Eye_Brow_Connect_Ctrl_reset()
            print('Eye Brow Follow Attribute reset')

    def reset_eye_follow_command(self, *args):
        if cmds.objExists(self.np + 'Eye_target_All_Ctrl_grp') and cmds.objExists(self.np + 'Eye_All_Ctrl_grp'):
            self.Eye_Target_Eye_Connect_Ctrl_reset()
            print('EyeTarget Eye Follow Attribute reset')

    def check_box_state_command(self, *args):
        self.update_CV_command()

    def update_CV_command(self, *args):
        self.np = self.ui.NameSpace_Combo.currentText()
        if cmds.objExists(self.np + 'L_brow_ctrl'):
            if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl') is False:
                self.ui.P_L_brow_Btn.setStyleSheet(self.green)
                self.ui.P_L_brow_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_Btn.setStyleSheet(self.green)
                    self.ui.P_L_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_Btn.setEnabled(False)
                    self.ui.P_L_brow_Btn.setStyleSheet(None)
            else:
                self.ui.P_L_brow_Btn.setStyleSheet(self.red)
                self.ui.P_L_brow_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_Btn.setStyleSheet(self.red)
                    self.ui.P_L_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_Btn.setEnabled(False)
                    self.ui.P_L_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_brow_Btn.setEnabled(False)
            self.ui.P_L_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_brow_02_ctrl'):
            if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl') is False:
                self.ui.P_L_brow_02_Btn.setStyleSheet(self.green)
                self.ui.P_L_brow_02_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_02_Btn.setStyleSheet(self.green)
                    self.ui.P_L_brow_02_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_02_Btn.setEnabled(False)
                    self.ui.P_L_brow_02_Btn.setStyleSheet(None)
            else:
                self.ui.P_L_brow_02_Btn.setStyleSheet(self.red)
                self.ui.P_L_brow_02_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_02_Btn.setStyleSheet(self.red)
                    self.ui.P_L_brow_02_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_02_Btn.setEnabled(False)
                    self.ui.P_L_brow_02_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_brow_02_Btn.setEnabled(False)
            self.ui.P_L_brow_02_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_brow_03_ctrl'):
            if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl') is False and cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl') is False:
                self.ui.P_L_brow_03_Btn.setStyleSheet(self.green)
                self.ui.P_L_brow_03_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_03_Btn.setStyleSheet(self.green)
                    self.ui.P_L_brow_03_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_03_Btn.setEnabled(False)
                    self.ui.P_L_brow_03_Btn.setStyleSheet(None)
            else:
                self.ui.P_L_brow_03_Btn.setStyleSheet(self.red)
                self.ui.P_L_brow_03_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_L_brow_03_Btn.setStyleSheet(self.red)
                    self.ui.P_L_brow_03_Btn.setEnabled(True)
                else:
                    self.ui.P_L_brow_03_Btn.setEnabled(False)
                    self.ui.P_L_brow_03_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_brow_03_Btn.setEnabled(False)
            self.ui.P_L_brow_03_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl'):
            self.ui.P_L_medial_fibers_brow_Btn.setStyleSheet(self.green)
            self.ui.P_L_medial_fibers_brow_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_medial_fibers_brow_Btn.setStyleSheet(self.green)
                self.ui.P_L_medial_fibers_brow_Btn.setEnabled(True)
            else:
                self.ui.P_L_medial_fibers_brow_Btn.setEnabled(False)
                self.ui.P_L_medial_fibers_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_medial_fibers_brow_Btn.setEnabled(False)
            self.ui.P_L_medial_fibers_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl'):
            self.ui.P_L_lateral_fibers_brow_Btn.setStyleSheet(self.green)
            self.ui.P_L_lateral_fibers_brow_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_lateral_fibers_brow_Btn.setStyleSheet(self.green)
                self.ui.P_L_lateral_fibers_brow_Btn.setEnabled(True)
            else:
                self.ui.P_L_lateral_fibers_brow_Btn.setEnabled(False)
                self.ui.P_L_lateral_fibers_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lateral_fibers_brow_Btn.setEnabled(False)
            self.ui.P_L_lateral_fibers_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_procerus_brow_FK_ctrl'):
            self.ui.P_L_procerus_brow_Btn.setStyleSheet(self.white)
            self.ui.P_L_procerus_brow_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_procerus_brow_Btn.setStyleSheet(self.white)
                self.ui.P_L_procerus_brow_Btn.setEnabled(True)
            else:
                self.ui.P_L_procerus_brow_Btn.setEnabled(False)
                self.ui.P_L_procerus_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_procerus_brow_Btn.setEnabled(False)
            self.ui.P_L_procerus_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_brow_ctrl'):
            if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl') is False:
                self.ui.P_R_brow_Btn.setStyleSheet(self.blue)
                self.ui.P_R_brow_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_Btn.setStyleSheet(self.blue)
                    self.ui.P_R_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_Btn.setEnabled(False)
                    self.ui.P_R_brow_Btn.setStyleSheet(None)
            else:
                self.ui.P_R_brow_Btn.setStyleSheet(self.red)
                self.ui.P_R_brow_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_Btn.setStyleSheet(self.red)
                    self.ui.P_R_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_Btn.setEnabled(False)
                    self.ui.P_R_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_brow_Btn.setEnabled(False)
            self.ui.P_R_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_brow_02_ctrl'):
            if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl') is False:
                self.ui.P_R_brow_02_Btn.setStyleSheet(self.blue)
                self.ui.P_R_brow_02_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_02_Btn.setStyleSheet(self.blue)
                    self.ui.P_R_brow_02_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_02_Btn.setEnabled(False)
                    self.ui.P_R_brow_02_Btn.setStyleSheet(None)
            else:
                self.ui.P_R_brow_02_Btn.setStyleSheet(self.red)
                self.ui.P_R_brow_02_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_02_Btn.setStyleSheet(self.red)
                    self.ui.P_R_brow_02_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_02_Btn.setEnabled(False)
                    self.ui.P_R_brow_02_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_brow_02_Btn.setEnabled(False)
            self.ui.P_R_brow_02_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_brow_03_ctrl'):
            if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl') is False and cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl') is False:
                self.ui.P_R_brow_03_Btn.setStyleSheet(self.blue)
                self.ui.P_R_brow_03_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_03_Btn.setStyleSheet(self.blue)
                    self.ui.P_R_brow_03_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_03_Btn.setEnabled(False)
                    self.ui.P_R_brow_03_Btn.setStyleSheet(None)
            else:
                self.ui.P_R_brow_03_Btn.setStyleSheet(self.red)
                self.ui.P_R_brow_03_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_R_brow_03_Btn.setStyleSheet(self.red)
                    self.ui.P_R_brow_03_Btn.setEnabled(True)
                else:
                    self.ui.P_R_brow_03_Btn.setEnabled(False)
                    self.ui.P_R_brow_03_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_brow_03_Btn.setEnabled(False)
            self.ui.P_R_brow_03_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl'):
            self.ui.P_R_medial_fibers_brow_Btn.setStyleSheet(self.blue)
            self.ui.P_R_medial_fibers_brow_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_medial_fibers_brow_Btn.setStyleSheet(self.blue)
                self.ui.P_R_medial_fibers_brow_Btn.setEnabled(True)
            else:
                self.ui.P_R_medial_fibers_brow_Btn.setEnabled(False)
                self.ui.P_R_medial_fibers_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_medial_fibers_brow_Btn.setEnabled(False)
            self.ui.P_R_medial_fibers_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl'):
            self.ui.P_R_lateral_fibers_brow_Btn.setStyleSheet(self.blue)
            self.ui.P_R_lateral_fibers_brow_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_lateral_fibers_brow_Btn.setStyleSheet(self.blue)
                self.ui.P_R_lateral_fibers_brow_Btn.setEnabled(True)
            else:
                self.ui.P_R_lateral_fibers_brow_Btn.setEnabled(False)
                self.ui.P_R_lateral_fibers_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lateral_fibers_brow_Btn.setEnabled(False)
            self.ui.P_R_lateral_fibers_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_procerus_brow_FK_ctrl'):
            self.ui.P_R_procerus_brow_Btn.setStyleSheet(self.white)
            self.ui.P_R_procerus_brow_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_procerus_brow_Btn.setStyleSheet(self.white)
                self.ui.P_R_procerus_brow_Btn.setEnabled(True)
            else:
                self.ui.P_R_procerus_brow_Btn.setEnabled(False)
                self.ui.P_R_procerus_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_procerus_brow_Btn.setEnabled(False)
            self.ui.P_R_procerus_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Center_brow_ctrl'):
            if cmds.objExists(self.np + 'L_brow_ctrl') is True or cmds.objExists(self.np + 'R_brow_ctrl') is True:
                self.ui.P_Center_brow_Btn.setStyleSheet(self.red)
                self.ui.P_Center_brow_Btn.setEnabled(True)
                if self.ui.SecondaryCheckBox.isChecked() is True:
                    self.ui.P_Center_brow_Btn.setStyleSheet(self.red)
                    self.ui.P_Center_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_Center_brow_Btn.setEnabled(False)
                    self.ui.P_Center_brow_Btn.setStyleSheet(None)
            else:
                self.ui.P_Center_brow_Btn.setStyleSheet(self.yellow)
                self.ui.P_Center_brow_Btn.setEnabled(True)
                if self.ui.PrimaryCheckBox.isChecked() is True:
                    self.ui.P_Center_brow_Btn.setStyleSheet(self.yellow)
                    self.ui.P_Center_brow_Btn.setEnabled(True)
                else:
                    self.ui.P_Center_brow_Btn.setEnabled(False)
                    self.ui.P_Center_brow_Btn.setStyleSheet(None)
        else:
            self.ui.P_Center_brow_Btn.setEnabled(False)
            self.ui.P_Center_brow_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_brow_master_ctrl'):
            self.ui.P_L_brow_master_Btn.setStyleSheet(self.magenta)
            self.ui.P_L_brow_master_Btn.setEnabled(True)
            if self.ui.MasterCheckBox.isChecked() is True:
                self.ui.P_L_brow_master_Btn.setStyleSheet(self.magenta)
                self.ui.P_L_brow_master_Btn.setEnabled(True)
            else:
                self.ui.P_L_brow_master_Btn.setEnabled(False)
                self.ui.P_L_brow_master_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_brow_master_Btn.setEnabled(False)
            self.ui.P_L_brow_master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_brow_master_ctrl'):
            self.ui.P_R_brow_master_Btn.setStyleSheet(self.magenta)
            self.ui.P_R_brow_master_Btn.setEnabled(True)
            if self.ui.MasterCheckBox.isChecked() is True:
                self.ui.P_R_brow_master_Btn.setStyleSheet(self.magenta)
                self.ui.P_R_brow_master_Btn.setEnabled(True)
            else:
                self.ui.P_R_brow_master_Btn.setEnabled(False)
                self.ui.P_R_brow_master_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_brow_master_Btn.setEnabled(False)
            self.ui.P_R_brow_master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_blink_ctrl'):
            self.ui.P_L_eye_blink_Btn.setStyleSheet(self.green)
            self.ui.P_L_eye_blink_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_eye_blink_Btn.setStyleSheet(self.green)
                self.ui.P_L_eye_blink_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_blink_Btn.setEnabled(False)
                self.ui.P_L_eye_blink_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_blink_Btn.setEnabled(False)
            self.ui.P_L_eye_blink_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_blink_ctrl'):
            self.ui.P_R_eye_blink_Btn.setStyleSheet(self.blue)
            self.ui.P_R_eye_blink_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_eye_blink_Btn.setStyleSheet(self.blue)
                self.ui.P_R_eye_blink_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_blink_Btn.setEnabled(False)
                self.ui.P_R_eye_blink_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_blink_Btn.setEnabled(False)
            self.ui.P_R_eye_blink_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_lower_ctrl'):
            self.ui.P_L_eye_lower_Btn.setStyleSheet(self.green)
            self.ui.P_L_eye_lower_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_eye_lower_Btn.setStyleSheet(self.green)
                self.ui.P_L_eye_lower_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_lower_Btn.setEnabled(False)
                self.ui.P_L_eye_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_lower_Btn.setEnabled(False)
            self.ui.P_L_eye_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_lower_ctrl'):
            self.ui.P_R_eye_lower_Btn.setStyleSheet(self.blue)
            self.ui.P_R_eye_lower_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_eye_lower_Btn.setStyleSheet(self.blue)
                self.ui.P_R_eye_lower_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_lower_Btn.setEnabled(False)
                self.ui.P_R_eye_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_lower_Btn.setEnabled(False)
            self.ui.P_R_eye_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_lacrimal_ctrl'):
            self.ui.P_L_eye_lacrimal_Btn.setStyleSheet(self.red)
            self.ui.P_L_eye_lacrimal_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_eye_lacrimal_Btn.setStyleSheet(self.red)
                self.ui.P_L_eye_lacrimal_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_lacrimal_Btn.setEnabled(False)
                self.ui.P_L_eye_lacrimal_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_lacrimal_Btn.setEnabled(False)
            self.ui.P_L_eye_lacrimal_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_lacrimal_upper_FK_ctrl'):
            self.ui.P_L_eye_lacrimal_upper_Btn.setStyleSheet(self.white)
            self.ui.P_L_eye_lacrimal_upper_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_eye_lacrimal_upper_Btn.setStyleSheet(self.white)
                self.ui.P_L_eye_lacrimal_upper_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_lacrimal_upper_Btn.setEnabled(False)
                self.ui.P_L_eye_lacrimal_upper_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_lacrimal_upper_Btn.setEnabled(False)
            self.ui.P_L_eye_lacrimal_upper_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_lacrimal_lower_FK_ctrl'):
            self.ui.P_L_eye_lacrimal_lower_Btn.setStyleSheet(self.white)
            self.ui.P_L_eye_lacrimal_lower_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_eye_lacrimal_lower_Btn.setStyleSheet(self.white)
                self.ui.P_L_eye_lacrimal_lower_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_lacrimal_lower_Btn.setEnabled(False)
                self.ui.P_L_eye_lacrimal_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_lacrimal_lower_Btn.setEnabled(False)
            self.ui.P_L_eye_lacrimal_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_back_ctrl'):
            self.ui.P_L_eye_back_Btn.setStyleSheet(self.red)
            self.ui.P_L_eye_back_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_eye_back_Btn.setStyleSheet(self.red)
                self.ui.P_L_eye_back_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_back_Btn.setEnabled(False)
                self.ui.P_L_eye_back_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_back_Btn.setEnabled(False)
            self.ui.P_L_eye_back_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_back_upper_FK_ctrl'):
            self.ui.P_L_eye_back_upper_Btn.setStyleSheet(self.white)
            self.ui.P_L_eye_back_upper_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_eye_back_upper_Btn.setStyleSheet(self.white)
                self.ui.P_L_eye_back_upper_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_back_upper_Btn.setEnabled(False)
                self.ui.P_L_eye_back_upper_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_back_upper_Btn.setEnabled(False)
            self.ui.P_L_eye_back_upper_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_back_lower_FK_ctrl'):
            self.ui.P_L_eye_back_lower_Btn.setStyleSheet(self.white)
            self.ui.P_L_eye_back_lower_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_eye_back_lower_Btn.setStyleSheet(self.white)
                self.ui.P_L_eye_back_lower_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_back_lower_Btn.setEnabled(False)
                self.ui.P_L_eye_back_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_back_lower_Btn.setEnabled(False)
            self.ui.P_L_eye_back_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_double_ctrl'):
            self.ui.P_L_eye_double_Btn.setStyleSheet(self.red)
            self.ui.P_L_eye_double_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_eye_double_Btn.setStyleSheet(self.red)
                self.ui.P_L_eye_double_Btn.setEnabled(True)
            else:
                self.ui.P_L_eye_double_Btn.setEnabled(False)
                self.ui.P_L_eye_double_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_eye_double_Btn.setEnabled(False)
            self.ui.P_L_eye_double_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_lacrimal_ctrl'):
            self.ui.P_R_eye_lacrimal_Btn.setStyleSheet(self.red)
            self.ui.P_R_eye_lacrimal_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_eye_lacrimal_Btn.setStyleSheet(self.red)
                self.ui.P_R_eye_lacrimal_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_lacrimal_Btn.setEnabled(False)
                self.ui.P_R_eye_lacrimal_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_lacrimal_Btn.setEnabled(False)
            self.ui.P_R_eye_lacrimal_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_lacrimal_upper_FK_ctrl'):
            self.ui.P_R_eye_lacrimal_upper_Btn.setStyleSheet(self.white)
            self.ui.P_R_eye_lacrimal_upper_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_eye_lacrimal_upper_Btn.setStyleSheet(self.white)
                self.ui.P_R_eye_lacrimal_upper_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_lacrimal_upper_Btn.setEnabled(False)
                self.ui.P_R_eye_lacrimal_upper_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_lacrimal_upper_Btn.setEnabled(False)
            self.ui.P_R_eye_lacrimal_upper_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_lacrimal_lower_FK_ctrl'):
            self.ui.P_R_eye_lacrimal_lower_Btn.setStyleSheet(self.white)
            self.ui.P_R_eye_lacrimal_lower_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_eye_lacrimal_lower_Btn.setStyleSheet(self.white)
                self.ui.P_R_eye_lacrimal_lower_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_lacrimal_lower_Btn.setEnabled(False)
                self.ui.P_R_eye_lacrimal_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_lacrimal_lower_Btn.setEnabled(False)
            self.ui.P_R_eye_lacrimal_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_back_ctrl'):
            self.ui.P_R_eye_back_Btn.setStyleSheet(self.red)
            self.ui.P_R_eye_back_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_eye_back_Btn.setStyleSheet(self.red)
                self.ui.P_R_eye_back_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_back_Btn.setEnabled(False)
                self.ui.P_R_eye_back_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_back_Btn.setEnabled(False)
            self.ui.P_R_eye_back_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_back_upper_FK_ctrl'):
            self.ui.P_R_eye_back_upper_Btn.setStyleSheet(self.white)
            self.ui.P_R_eye_back_upper_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_eye_back_upper_Btn.setStyleSheet(self.white)
                self.ui.P_R_eye_back_upper_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_back_upper_Btn.setEnabled(False)
                self.ui.P_R_eye_back_upper_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_back_upper_Btn.setEnabled(False)
            self.ui.P_R_eye_back_upper_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_back_lower_FK_ctrl'):
            self.ui.P_R_eye_back_lower_Btn.setStyleSheet(self.white)
            self.ui.P_R_eye_back_lower_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_eye_back_lower_Btn.setStyleSheet(self.white)
                self.ui.P_R_eye_back_lower_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_back_lower_Btn.setEnabled(False)
                self.ui.P_R_eye_back_lower_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_back_lower_Btn.setEnabled(False)
            self.ui.P_R_eye_back_lower_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_double_ctrl'):
            self.ui.P_R_eye_double_Btn.setStyleSheet(self.red)
            self.ui.P_R_eye_double_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_eye_double_Btn.setStyleSheet(self.red)
                self.ui.P_R_eye_double_Btn.setEnabled(True)
            else:
                self.ui.P_R_eye_double_Btn.setEnabled(False)
                self.ui.P_R_eye_double_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_eye_double_Btn.setEnabled(False)
            self.ui.P_R_eye_double_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_eye_target_ctrl'):
            self.ui.P_L_eye_target_Btn.setStyleSheet(self.green)
            self.ui.P_L_eye_target_Btn.setEnabled(True)
        else:
            self.ui.P_L_eye_target_Btn.setEnabled(False)
            self.ui.P_L_eye_target_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_eye_target_ctrl'):
            self.ui.P_R_eye_target_Btn.setStyleSheet(self.blue)
            self.ui.P_R_eye_target_Btn.setEnabled(True)
        else:
            self.ui.P_R_eye_target_Btn.setEnabled(False)
            self.ui.P_R_eye_target_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Eye_target_Master_ctrl'):
            self.ui.P_Eye_target_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Eye_target_Master_Btn.setEnabled(True)
        else:
            self.ui.P_Eye_target_Master_Btn.setEnabled(False)
            self.ui.P_Eye_target_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Eye_World_point_loc'):
            self.ui.P_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_Eye_World_point_ctrl'):
            self.ui.P_L_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_L_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_L_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_L_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_Eye_World_point_ctrl'):
            self.ui.P_R_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_R_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_R_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_R_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_nose_ctrl'):
            self.ui.P_L_nose_Btn.setStyleSheet(self.green)
            self.ui.P_L_nose_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_nose_Btn.setStyleSheet(self.green)
                self.ui.P_L_nose_Btn.setEnabled(True)
            else:
                self.ui.P_L_nose_Btn.setEnabled(False)
                self.ui.P_L_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_nose_Btn.setEnabled(False)
            self.ui.P_L_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_nasalis_transverse_nose_FK_ctrl'):
            self.ui.P_L_nasalis_transverse_nose_Btn.setStyleSheet(self.white)
            self.ui.P_L_nasalis_transverse_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_nasalis_transverse_nose_Btn.setStyleSheet(self.white)
                self.ui.P_L_nasalis_transverse_nose_Btn.setEnabled(True)
            else:
                self.ui.P_L_nasalis_transverse_nose_Btn.setEnabled(False)
                self.ui.P_L_nasalis_transverse_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_nasalis_transverse_nose_Btn.setEnabled(False)
            self.ui.P_L_nasalis_transverse_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_procerus_nose_FK_ctrl'):
            self.ui.P_L_procerus_nose_Btn.setStyleSheet(self.white)
            self.ui.P_L_procerus_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_procerus_nose_Btn.setStyleSheet(self.white)
                self.ui.P_L_procerus_nose_Btn.setEnabled(True)
            else:
                self.ui.P_L_procerus_nose_Btn.setEnabled(False)
                self.ui.P_L_procerus_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_procerus_nose_Btn.setEnabled(False)
            self.ui.P_L_procerus_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_nasolabial_fold_nose_FK_ctrl'):
            self.ui.P_L_nasolabial_fold_nose_Btn.setStyleSheet(self.white)
            self.ui.P_L_nasolabial_fold_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_nasolabial_fold_nose_Btn.setStyleSheet(self.white)
                self.ui.P_L_nasolabial_fold_nose_Btn.setEnabled(True)
            else:
                self.ui.P_L_nasolabial_fold_nose_Btn.setEnabled(False)
                self.ui.P_L_nasolabial_fold_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_nasolabial_fold_nose_Btn.setEnabled(False)
            self.ui.P_L_nasolabial_fold_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_nose_ctrl'):
            self.ui.P_R_nose_Btn.setStyleSheet(self.blue)
            self.ui.P_R_nose_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_nose_Btn.setStyleSheet(self.blue)
                self.ui.P_R_nose_Btn.setEnabled(True)
            else:
                self.ui.P_R_nose_Btn.setEnabled(False)
                self.ui.P_R_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_nose_Btn.setEnabled(False)
            self.ui.P_R_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_nasalis_transverse_nose_FK_ctrl'):
            self.ui.P_R_nasalis_transverse_nose_Btn.setStyleSheet(self.white)
            self.ui.P_R_nasalis_transverse_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_nasalis_transverse_nose_Btn.setStyleSheet(self.white)
                self.ui.P_R_nasalis_transverse_nose_Btn.setEnabled(True)
            else:
                self.ui.P_R_nasalis_transverse_nose_Btn.setEnabled(False)
                self.ui.P_R_nasalis_transverse_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_nasalis_transverse_nose_Btn.setEnabled(False)
            self.ui.P_R_nasalis_transverse_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_procerus_nose_FK_ctrl'):
            self.ui.P_R_procerus_nose_Btn.setStyleSheet(self.white)
            self.ui.P_R_procerus_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_procerus_nose_Btn.setStyleSheet(self.white)
                self.ui.P_R_procerus_nose_Btn.setEnabled(True)
            else:
                self.ui.P_R_procerus_nose_Btn.setEnabled(False)
                self.ui.P_R_procerus_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_procerus_nose_Btn.setEnabled(False)
            self.ui.P_R_procerus_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_nasolabial_fold_nose_FK_ctrl'):
            self.ui.P_R_nasolabial_fold_nose_Btn.setStyleSheet(self.white)
            self.ui.P_R_nasolabial_fold_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_nasolabial_fold_nose_Btn.setStyleSheet(self.white)
                self.ui.P_R_nasolabial_fold_nose_Btn.setEnabled(True)
            else:
                self.ui.P_R_nasolabial_fold_nose_Btn.setEnabled(False)
                self.ui.P_R_nasolabial_fold_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_nasolabial_fold_nose_Btn.setEnabled(False)
            self.ui.P_R_nasolabial_fold_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Nose_ctrl'):
            self.ui.P_Nose_Btn.setStyleSheet(self.red)
            self.ui.P_Nose_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_Nose_Btn.setStyleSheet(self.red)
                self.ui.P_Nose_Btn.setEnabled(True)
            else:
                self.ui.P_Nose_Btn.setEnabled(False)
                self.ui.P_Nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_Nose_Btn.setEnabled(False)
            self.ui.P_Nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_nose_ctrl'):
            self.ui.P_Lower_nose_Btn.setStyleSheet(self.red)
            self.ui.P_Lower_nose_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_Lower_nose_Btn.setStyleSheet(self.red)
                self.ui.P_Lower_nose_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_nose_Btn.setEnabled(False)
                self.ui.P_Lower_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_nose_Btn.setEnabled(False)
            self.ui.P_Lower_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'depressor_septi_nose_FK_ctrl'):
            self.ui.P_depressor_septi_nose_Btn.setStyleSheet(self.white)
            self.ui.P_depressor_septi_nose_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_depressor_septi_nose_Btn.setStyleSheet(self.white)
                self.ui.P_depressor_septi_nose_Btn.setEnabled(True)
            else:
                self.ui.P_depressor_septi_nose_Btn.setEnabled(False)
                self.ui.P_depressor_septi_nose_Btn.setStyleSheet(None)
        else:
            self.ui.P_depressor_septi_nose_Btn.setEnabled(False)
            self.ui.P_depressor_septi_nose_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_cheek_ctrl'):
            self.ui.P_L_cheek_Btn.setStyleSheet(self.green)
            self.ui.P_L_cheek_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_cheek_Btn.setStyleSheet(self.green)
                self.ui.P_L_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_L_cheek_Btn.setEnabled(False)
                self.ui.P_L_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_cheek_Btn.setEnabled(False)
            self.ui.P_L_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_cheek_ctrl'):
            self.ui.P_R_cheek_Btn.setStyleSheet(self.blue)
            self.ui.P_R_cheek_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_cheek_Btn.setStyleSheet(self.blue)
                self.ui.P_R_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_R_cheek_Btn.setEnabled(False)
                self.ui.P_R_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_cheek_Btn.setEnabled(False)
            self.ui.P_R_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_upper_cheek_ctrl'):
            self.ui.P_L_upper_cheek_Btn.setStyleSheet(self.red)
            self.ui.P_L_upper_cheek_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_upper_cheek_Btn.setStyleSheet(self.red)
                self.ui.P_L_upper_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_L_upper_cheek_Btn.setEnabled(False)
                self.ui.P_L_upper_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_upper_cheek_Btn.setEnabled(False)
            self.ui.P_L_upper_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_outer_orbicularis_cheek_FK_ctrl'):
            self.ui.P_L_outer_orbicularis_cheek_Btn.setStyleSheet(self.white)
            self.ui.P_L_outer_orbicularis_cheek_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_outer_orbicularis_cheek_Btn.setStyleSheet(self.white)
                self.ui.P_L_outer_orbicularis_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_L_outer_orbicularis_cheek_Btn.setEnabled(False)
                self.ui.P_L_outer_orbicularis_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_outer_orbicularis_cheek_Btn.setEnabled(False)
            self.ui.P_L_outer_orbicularis_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_inner_orbicularis_cheek_FK_ctrl'):
            self.ui.P_L_inner_orbicularis_cheek_Btn.setStyleSheet(self.white)
            self.ui.P_L_inner_orbicularis_cheek_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_inner_orbicularis_cheek_Btn.setStyleSheet(self.white)
                self.ui.P_L_inner_orbicularis_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_L_inner_orbicularis_cheek_Btn.setEnabled(False)
                self.ui.P_L_inner_orbicularis_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_inner_orbicularis_cheek_Btn.setEnabled(False)
            self.ui.P_L_inner_orbicularis_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_upper_cheek_ctrl'):
            self.ui.P_R_upper_cheek_Btn.setStyleSheet(self.red)
            self.ui.P_R_upper_cheek_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_upper_cheek_Btn.setStyleSheet(self.red)
                self.ui.P_R_upper_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_R_upper_cheek_Btn.setEnabled(False)
                self.ui.P_R_upper_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_upper_cheek_Btn.setEnabled(False)
            self.ui.P_R_upper_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_outer_orbicularis_cheek_FK_ctrl'):
            self.ui.P_R_outer_orbicularis_cheek_Btn.setStyleSheet(self.white)
            self.ui.P_R_outer_orbicularis_cheek_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_outer_orbicularis_cheek_Btn.setStyleSheet(self.white)
                self.ui.P_R_outer_orbicularis_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_R_outer_orbicularis_cheek_Btn.setEnabled(False)
                self.ui.P_R_outer_orbicularis_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_outer_orbicularis_cheek_Btn.setEnabled(False)
            self.ui.P_R_outer_orbicularis_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_inner_orbicularis_cheek_FK_ctrl'):
            self.ui.P_R_inner_orbicularis_cheek_Btn.setStyleSheet(self.white)
            self.ui.P_R_inner_orbicularis_cheek_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_inner_orbicularis_cheek_Btn.setStyleSheet(self.white)
                self.ui.P_R_inner_orbicularis_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_R_inner_orbicularis_cheek_Btn.setEnabled(False)
                self.ui.P_R_inner_orbicularis_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_inner_orbicularis_cheek_Btn.setEnabled(False)
            self.ui.P_R_inner_orbicularis_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
            self.ui.P_L_lower_cheek_Btn.setStyleSheet(self.red)
            self.ui.P_L_lower_cheek_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lower_cheek_Btn.setStyleSheet(self.red)
                self.ui.P_L_lower_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_L_lower_cheek_Btn.setEnabled(False)
                self.ui.P_L_lower_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lower_cheek_Btn.setEnabled(False)
            self.ui.P_L_lower_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
            self.ui.P_R_lower_cheek_Btn.setStyleSheet(self.red)
            self.ui.P_R_lower_cheek_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lower_cheek_Btn.setStyleSheet(self.red)
                self.ui.P_R_lower_cheek_Btn.setEnabled(True)
            else:
                self.ui.P_R_lower_cheek_Btn.setEnabled(False)
                self.ui.P_R_lower_cheek_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lower_cheek_Btn.setEnabled(False)
            self.ui.P_R_lower_cheek_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lower_liplid_ctrl'):
            self.ui.P_L_lower_liplid_Btn.setStyleSheet(self.red)
            self.ui.P_L_lower_liplid_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lower_liplid_Btn.setStyleSheet(self.red)
                self.ui.P_L_lower_liplid_Btn.setEnabled(True)
            else:
                self.ui.P_L_lower_liplid_Btn.setEnabled(False)
                self.ui.P_L_lower_liplid_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lower_liplid_Btn.setEnabled(False)
            self.ui.P_L_lower_liplid_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lower_liplid_ctrl'):
            self.ui.P_R_lower_liplid_Btn.setStyleSheet(self.red)
            self.ui.P_R_lower_liplid_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lower_liplid_Btn.setStyleSheet(self.red)
                self.ui.P_R_lower_liplid_Btn.setEnabled(True)
            else:
                self.ui.P_R_lower_liplid_Btn.setEnabled(False)
                self.ui.P_R_lower_liplid_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lower_liplid_Btn.setEnabled(False)
            self.ui.P_R_lower_liplid_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_corner_Ctrl'):
            self.ui.P_L_lip_corner_Btn.setStyleSheet(self.green)
            self.ui.P_L_lip_corner_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_corner_Btn.setStyleSheet(self.green)
                self.ui.P_L_lip_corner_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_corner_Btn.setEnabled(False)
                self.ui.P_L_lip_corner_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_corner_Btn.setEnabled(False)
            self.ui.P_L_lip_corner_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_corner_Ctrl'):
            self.ui.P_R_lip_corner_Btn.setStyleSheet(self.blue)
            self.ui.P_R_lip_corner_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_corner_Btn.setStyleSheet(self.blue)
                self.ui.P_R_lip_corner_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_corner_Btn.setEnabled(False)
                self.ui.P_R_lip_corner_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_corner_Btn.setEnabled(False)
            self.ui.P_R_lip_corner_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl'):
            self.ui.P_L_lip_corner_up_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_corner_up_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_corner_up_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_corner_up_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_corner_up_Btn.setEnabled(False)
                self.ui.P_L_lip_corner_up_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_corner_up_Btn.setEnabled(False)
            self.ui.P_L_lip_corner_up_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_corner_up_FK_Ctrl'):
            self.ui.P_L_lip_corner_up_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_corner_up_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_corner_up_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_corner_up_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_corner_up_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_corner_up_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_corner_up_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_corner_up_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl'):
            self.ui.P_R_lip_corner_up_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_corner_up_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_corner_up_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_corner_up_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_corner_up_Btn.setEnabled(False)
                self.ui.P_R_lip_corner_up_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_corner_up_Btn.setEnabled(False)
            self.ui.P_R_lip_corner_up_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_corner_up_FK_Ctrl'):
            self.ui.P_R_lip_corner_up_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_corner_up_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_corner_up_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_corner_up_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_corner_up_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_corner_up_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_corner_up_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_corner_up_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl'):
            self.ui.P_L_lip_corner_down_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_corner_down_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_corner_down_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_corner_down_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_corner_down_Btn.setEnabled(False)
                self.ui.P_L_lip_corner_down_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_corner_down_Btn.setEnabled(False)
            self.ui.P_L_lip_corner_down_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_corner_down_FK_Ctrl'):
            self.ui.P_L_lip_corner_down_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_corner_down_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_corner_down_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_corner_down_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_corner_down_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_corner_down_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_corner_down_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_corner_down_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl'):
            self.ui.P_R_lip_corner_down_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_corner_down_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_corner_down_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_corner_down_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_corner_down_Btn.setEnabled(False)
                self.ui.P_R_lip_corner_down_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_corner_down_Btn.setEnabled(False)
            self.ui.P_R_lip_corner_down_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_corner_down_FK_Ctrl'):
            self.ui.P_R_lip_corner_down_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_corner_down_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_corner_down_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_corner_down_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_corner_down_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_corner_down_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_corner_down_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_corner_down_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Upper_lip_Master_ctrl'):
            self.ui.P_Upper_lip_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Upper_lip_Master_Btn.setEnabled(True)
            if self.ui.MasterCheckBox.isChecked() is True:
                self.ui.P_Upper_lip_Master_Btn.setStyleSheet(self.magenta)
                self.ui.P_Upper_lip_Master_Btn.setEnabled(True)
            else:
                self.ui.P_Upper_lip_Master_Btn.setEnabled(False)
                self.ui.P_Upper_lip_Master_Btn.setStyleSheet(None)
        else:
            self.ui.P_Upper_lip_Master_Btn.setEnabled(False)
            self.ui.P_Upper_lip_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_lip_Master_ctrl'):
            self.ui.P_Lower_lip_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Lower_lip_Master_Btn.setEnabled(True)
            if self.ui.MasterCheckBox.isChecked() is True:
                self.ui.P_Lower_lip_Master_Btn.setStyleSheet(self.magenta)
                self.ui.P_Lower_lip_Master_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_lip_Master_Btn.setEnabled(False)
                self.ui.P_Lower_lip_Master_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_lip_Master_Btn.setEnabled(False)
            self.ui.P_Lower_lip_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Upper_lip_ctrl'):
            self.ui.P_Upper_lip_Btn.setStyleSheet(self.yellow)
            self.ui.P_Upper_lip_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_Upper_lip_Btn.setStyleSheet(self.yellow)
                self.ui.P_Upper_lip_Btn.setEnabled(True)
            else:
                self.ui.P_Upper_lip_Btn.setEnabled(False)
                self.ui.P_Upper_lip_Btn.setStyleSheet(None)
        else:
            self.ui.P_Upper_lip_Btn.setEnabled(False)
            self.ui.P_Upper_lip_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Upper_lip_FK_ctrl'):
            self.ui.P_Upper_lip_FK_Btn.setStyleSheet(self.white)
            self.ui.P_Upper_lip_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_Upper_lip_FK_Btn.setStyleSheet(self.white)
                self.ui.P_Upper_lip_FK_Btn.setEnabled(True)
            else:
                self.ui.P_Upper_lip_FK_Btn.setEnabled(False)
                self.ui.P_Upper_lip_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_Upper_lip_FK_Btn.setEnabled(False)
            self.ui.P_Upper_lip_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_lip_ctrl'):
            self.ui.P_Lower_lip_Btn.setStyleSheet(self.yellow)
            self.ui.P_Lower_lip_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_Lower_lip_Btn.setStyleSheet(self.yellow)
                self.ui.P_Lower_lip_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_lip_Btn.setEnabled(False)
                self.ui.P_Lower_lip_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_lip_Btn.setEnabled(False)
            self.ui.P_Lower_lip_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_lip_FK_ctrl'):
            self.ui.P_Lower_lip_FK_Btn.setStyleSheet(self.white)
            self.ui.P_Lower_lip_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_Lower_lip_FK_Btn.setStyleSheet(self.white)
                self.ui.P_Lower_lip_FK_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_lip_FK_Btn.setEnabled(False)
                self.ui.P_Lower_lip_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_lip_FK_Btn.setEnabled(False)
            self.ui.P_Lower_lip_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_lip_outer_ctrl'):
            self.ui.P_Lower_lip_outer_Btn.setStyleSheet(self.red)
            self.ui.P_Lower_lip_outer_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_Lower_lip_outer_Btn.setStyleSheet(self.red)
                self.ui.P_Lower_lip_outer_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_lip_outer_Btn.setEnabled(False)
                self.ui.P_Lower_lip_outer_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_lip_outer_Btn.setEnabled(False)
            self.ui.P_Lower_lip_outer_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_upper_side_ctrl'):
            self.ui.P_L_lip_upper_side_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_upper_side_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_upper_side_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_upper_side_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_upper_side_Btn.setEnabled(False)
                self.ui.P_L_lip_upper_side_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_upper_side_Btn.setEnabled(False)
            self.ui.P_L_lip_upper_side_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_upper_side_FK_ctrl'):
            self.ui.P_L_lip_upper_side_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_upper_side_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_upper_side_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_upper_side_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_upper_side_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_upper_side_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_upper_side_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_upper_side_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl'):
            self.ui.P_L_lip_upper_side_02_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_upper_side_02_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_upper_side_02_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_upper_side_02_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_upper_side_02_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_upper_side_02_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_upper_side_02_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_upper_side_02_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_upper_outer_ctrl'):
            self.ui.P_L_lip_upper_outer_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_upper_outer_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_upper_outer_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_upper_outer_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_upper_outer_Btn.setEnabled(False)
                self.ui.P_L_lip_upper_outer_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_upper_outer_Btn.setEnabled(False)
            self.ui.P_L_lip_upper_outer_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_upper_side_ctrl'):
            self.ui.P_R_lip_upper_side_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_upper_side_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_upper_side_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_upper_side_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_upper_side_Btn.setEnabled(False)
                self.ui.P_R_lip_upper_side_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_upper_side_Btn.setEnabled(False)
            self.ui.P_R_lip_upper_side_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_upper_side_FK_ctrl'):
            self.ui.P_R_lip_upper_side_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_upper_side_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_upper_side_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_upper_side_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_upper_side_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_upper_side_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_upper_side_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_upper_side_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl'):
            self.ui.P_R_lip_upper_side_02_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_upper_side_02_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_upper_side_02_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_upper_side_02_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_upper_side_02_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_upper_side_02_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_upper_side_02_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_upper_side_02_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_upper_outer_ctrl'):
            self.ui.P_R_lip_upper_outer_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_upper_outer_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_upper_outer_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_upper_outer_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_upper_outer_Btn.setEnabled(False)
                self.ui.P_R_lip_upper_outer_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_upper_outer_Btn.setEnabled(False)
            self.ui.P_R_lip_upper_outer_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_lower_side_ctrl'):
            self.ui.P_L_lip_lower_side_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_lower_side_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_lower_side_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_lower_side_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_lower_side_Btn.setEnabled(False)
                self.ui.P_L_lip_lower_side_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_lower_side_Btn.setEnabled(False)
            self.ui.P_L_lip_lower_side_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_lower_side_FK_ctrl'):
            self.ui.P_L_lip_lower_side_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_lower_side_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_lower_side_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_lower_side_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_lower_side_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_lower_side_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_lower_side_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_lower_side_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_lower_side_02_FK_ctrl'):
            self.ui.P_L_lip_lower_side_02_FK_Btn.setStyleSheet(self.white)
            self.ui.P_L_lip_lower_side_02_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_L_lip_lower_side_02_FK_Btn.setStyleSheet(self.white)
                self.ui.P_L_lip_lower_side_02_FK_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_lower_side_02_FK_Btn.setEnabled(False)
                self.ui.P_L_lip_lower_side_02_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_lower_side_02_FK_Btn.setEnabled(False)
            self.ui.P_L_lip_lower_side_02_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'L_lip_lower_outer_ctrl'):
            self.ui.P_L_lip_lower_outer_Btn.setStyleSheet(self.red)
            self.ui.P_L_lip_lower_outer_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_L_lip_lower_outer_Btn.setStyleSheet(self.red)
                self.ui.P_L_lip_lower_outer_Btn.setEnabled(True)
            else:
                self.ui.P_L_lip_lower_outer_Btn.setEnabled(False)
                self.ui.P_L_lip_lower_outer_Btn.setStyleSheet(None)
        else:
            self.ui.P_L_lip_lower_outer_Btn.setEnabled(False)
            self.ui.P_L_lip_lower_outer_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_lower_side_ctrl'):
            self.ui.P_R_lip_lower_side_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_lower_side_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_lower_side_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_lower_side_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_lower_side_Btn.setEnabled(False)
                self.ui.P_R_lip_lower_side_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_lower_side_Btn.setEnabled(False)
            self.ui.P_R_lip_lower_side_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_lower_side_FK_ctrl'):
            self.ui.P_R_lip_lower_side_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_lower_side_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_lower_side_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_lower_side_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_lower_side_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_lower_side_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_lower_side_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_lower_side_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_lower_side_02_FK_ctrl'):
            self.ui.P_R_lip_lower_side_02_FK_Btn.setStyleSheet(self.white)
            self.ui.P_R_lip_lower_side_02_FK_Btn.setEnabled(True)
            if self.ui.FKCheckBox.isChecked() is True:
                self.ui.P_R_lip_lower_side_02_FK_Btn.setStyleSheet(self.white)
                self.ui.P_R_lip_lower_side_02_FK_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_lower_side_02_FK_Btn.setEnabled(False)
                self.ui.P_R_lip_lower_side_02_FK_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_lower_side_02_FK_Btn.setEnabled(False)
            self.ui.P_R_lip_lower_side_02_FK_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'R_lip_lower_outer_ctrl'):
            self.ui.P_R_lip_lower_outer_Btn.setStyleSheet(self.red)
            self.ui.P_R_lip_lower_outer_Btn.setEnabled(True)
            if self.ui.SecondaryCheckBox.isChecked() is True:
                self.ui.P_R_lip_lower_outer_Btn.setStyleSheet(self.red)
                self.ui.P_R_lip_lower_outer_Btn.setEnabled(True)
            else:
                self.ui.P_R_lip_lower_outer_Btn.setEnabled(False)
                self.ui.P_R_lip_lower_outer_Btn.setStyleSheet(None)
        else:
            self.ui.P_R_lip_lower_outer_Btn.setEnabled(False)
            self.ui.P_R_lip_lower_outer_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_Master_ctrl'):
            self.ui.P_Lip_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Lip_Master_Btn.setEnabled(True)
            if self.ui.MasterCheckBox.isChecked() is True:
                self.ui.P_Lip_Master_Btn.setStyleSheet(self.magenta)
                self.ui.P_Lip_Master_Btn.setEnabled(True)
            else:
                self.ui.P_Lip_Master_Btn.setEnabled(False)
                self.ui.P_Lip_Master_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lip_Master_Btn.setEnabled(False)
            self.ui.P_Lip_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Jaw_Master_Ctrl'):
            self.ui.P_Jaw_Master_Btn.setStyleSheet(self.yellow)
            self.ui.P_Jaw_Master_Btn.setEnabled(True)
            if self.ui.PrimaryCheckBox.isChecked() is True:
                self.ui.P_Jaw_Master_Btn.setStyleSheet(self.yellow)
                self.ui.P_Jaw_Master_Btn.setEnabled(True)
            else:
                self.ui.P_Jaw_Master_Btn.setEnabled(False)
                self.ui.P_Jaw_Master_Btn.setStyleSheet(None)
        else:
            self.ui.P_Jaw_Master_Btn.setEnabled(False)
            self.ui.P_Jaw_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_Ctrl'):
            self.ui.P_Lip_FACS_Btn.setStyleSheet(self.red)
            self.ui.P_Lip_FACS_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_bar_ctrl'):
            self.ui.P_Lip_FACS_bar_Btn.setStyleSheet(self.white)
            self.ui.P_Lip_FACS_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_L_bar_ctrl'):
            self.ui.P_Lip_FACS_L_bar_Btn.setStyleSheet(self.green)
            self.ui.P_Lip_FACS_L_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_L_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_L_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_R_bar_ctrl'):
            self.ui.P_Lip_FACS_R_bar_Btn.setStyleSheet(self.blue)
            self.ui.P_Lip_FACS_R_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_R_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_R_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_upper_bar_ctrl'):
            self.ui.P_Lip_FACS_upper_bar_Btn.setStyleSheet(self.yellow)
            self.ui.P_Lip_FACS_upper_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_upper_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_upper_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lip_FACS_lower_bar_ctrl'):
            self.ui.P_Lip_FACS_lower_bar_Btn.setStyleSheet(self.yellow)
            self.ui.P_Lip_FACS_lower_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_lower_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_lower_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Upper_teeth_ctrl'):
            self.ui.P_Upper_teeth_Btn.setStyleSheet(self.red)
            self.ui.P_Upper_teeth_Btn.setEnabled(True)
            if self.ui.OralCavityCheckBox.isChecked() is True:
                self.ui.P_Upper_teeth_Btn.setStyleSheet(self.red)
                self.ui.P_Upper_teeth_Btn.setEnabled(True)
            else:
                self.ui.P_Upper_teeth_Btn.setEnabled(False)
                self.ui.P_Upper_teeth_Btn.setStyleSheet(None)
        else:
            self.ui.P_Upper_teeth_Btn.setEnabled(False)
            self.ui.P_Upper_teeth_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Lower_teeth_ctrl'):
            self.ui.P_Lower_teeth_Btn.setStyleSheet(self.red)
            self.ui.P_Lower_teeth_Btn.setEnabled(True)
            if self.ui.OralCavityCheckBox.isChecked() is True:
                self.ui.P_Lower_teeth_Btn.setStyleSheet(self.red)
                self.ui.P_Lower_teeth_Btn.setEnabled(True)
            else:
                self.ui.P_Lower_teeth_Btn.setEnabled(False)
                self.ui.P_Lower_teeth_Btn.setStyleSheet(None)
        else:
            self.ui.P_Lower_teeth_Btn.setEnabled(False)
            self.ui.P_Lower_teeth_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Tongue_ctrl'):
            self.ui.P_Tongue_Btn.setStyleSheet(self.red)
            self.ui.P_Tongue_Btn.setEnabled(True)
            if self.ui.OralCavityCheckBox.isChecked() is True:
                self.ui.P_Tongue_Btn.setStyleSheet(self.red)
                self.ui.P_Tongue_Btn.setEnabled(True)
            else:
                self.ui.P_Tongue_Btn.setEnabled(False)
                self.ui.P_Tongue_Btn.setStyleSheet(None)
        else:
            self.ui.P_Tongue_Btn.setEnabled(False)
            self.ui.P_Tongue_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Tongue_02_ctrl'):
            self.ui.P_Tongue_02_Btn.setStyleSheet(self.red)
            self.ui.P_Tongue_02_Btn.setEnabled(True)
            if self.ui.OralCavityCheckBox.isChecked() is True:
                self.ui.P_Tongue_02_Btn.setStyleSheet(self.red)
                self.ui.P_Tongue_02_Btn.setEnabled(True)
            else:
                self.ui.P_Tongue_02_Btn.setEnabled(False)
                self.ui.P_Tongue_02_Btn.setStyleSheet(None)
        else:
            self.ui.P_Tongue_02_Btn.setEnabled(False)
            self.ui.P_Tongue_02_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Tongue_03_ctrl'):
            self.ui.P_Tongue_03_Btn.setStyleSheet(self.red)
            self.ui.P_Tongue_03_Btn.setEnabled(True)
            if self.ui.OralCavityCheckBox.isChecked() is True:
                self.ui.P_Tongue_03_Btn.setStyleSheet(self.red)
                self.ui.P_Tongue_03_Btn.setEnabled(True)
            else:
                self.ui.P_Tongue_03_Btn.setEnabled(False)
                self.ui.P_Tongue_03_Btn.setStyleSheet(None)
        else:
            self.ui.P_Tongue_03_Btn.setEnabled(False)
            self.ui.P_Tongue_03_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Facial_Master_Ctrl'):
            self.ui.P_Facial_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Facial_Master_Btn.setEnabled(True)
        else:
            self.ui.P_Facial_Master_Btn.setEnabled(False)
            self.ui.P_Facial_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.np + 'Facial_Set_Ctrl.Primary_Ctrl'):
            if self.ui.PrimaryCheckBox.isChecked() is True:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Primary_Ctrl', 1)
            else:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Primary_Ctrl', 0)
        if cmds.objExists(self.np + 'Facial_Set_Ctrl.Secondary_Ctrl'):
            if self.ui.SecondaryCheckBox.isChecked() is True:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Secondary_Ctrl', 1)
            else:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Secondary_Ctrl', 0)
        if cmds.objExists(self.np + 'Facial_Set_Ctrl.Master_Ctrl'):
            if self.ui.MasterCheckBox.isChecked() is True:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Master_Ctrl', 1)
            else:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Master_Ctrl', 0)
        if cmds.objExists(self.np + 'Facial_Set_Ctrl.FK_Ctrl'):
            if self.ui.FKCheckBox.isChecked() is True:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.FK_Ctrl', 1)
            else:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.FK_Ctrl', 0)
        if cmds.objExists(self.np + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl'):
            if self.ui.OralCavityCheckBox.isChecked() is True:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl', 1)
            else:
                cmds.setAttr(self.np + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl', 0)
        return

    def left_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_brow_ctrl')
            else:
                print('no existing object!!')

    def left_brow_02_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_brow_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_brow_02_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_brow_02_ctrl')
            else:
                print('no existing object!!')

    def left_brow_03_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_brow_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_brow_03_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_brow_03_ctrl')
            else:
                print('no existing object!!')

    def left_medial_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_medial_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_medial_fibers_brow_ctrl')
            else:
                print('no existing object!!')

    def left_lateral_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lateral_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lateral_fibers_brow_ctrl')
            else:
                print('no existing object!!')

    def left_procerus_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_procerus_brow_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_procerus_brow_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_procerus_brow_FK_ctrl')
            else:
                print('no existing object!!')

    def right_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_brow_ctrl')
            else:
                print('no existing object!!')

    def right_brow_02_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_brow_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_brow_02_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_brow_02_ctrl')
            else:
                print('no existing object!!')

    def right_brow_03_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_brow_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_brow_03_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_brow_03_ctrl')
            else:
                print('no existing object!!')

    def right_medial_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_medial_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_medial_fibers_brow_ctrl')
            else:
                print('no existing object!!')

    def right_lateral_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lateral_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lateral_fibers_brow_ctrl')
            else:
                print('no existing object!!')

    def right_procerus_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_procerus_brow_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_procerus_brow_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_procerus_brow_FK_ctrl')
            else:
                print('no existing object!!')

    def center_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Center_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Center_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Center_brow_ctrl')
            else:
                print('no existing object!!')

    def left_brow_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_brow_master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_brow_master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_brow_master_ctrl')
            else:
                print('no existing object!!')

    def right_brow_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_brow_master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_brow_master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_brow_master_ctrl')
            else:
                print('no existing object!!')

    def left_eye_blink_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_blink_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_blink_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_blink_ctrl')
            else:
                print('no existing object!!')

    def right_eye_blink_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_blink_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_blink_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_blink_ctrl')
            else:
                print('no existing object!!')

    def left_eye_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_lower_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_lower_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_lower_ctrl')
            else:
                print('no existing object!!')

    def right_eye_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_lower_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_lower_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_lower_ctrl')
            else:
                print('no existing object!!')

    def left_eye_lacrimal_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_lacrimal_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_lacrimal_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_lacrimal_ctrl')
            else:
                print('no existing object!!')

    def left_eye_lacrimal_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_lacrimal_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_lacrimal_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_lacrimal_upper_FK_ctrl')
            else:
                print('no existing object!!')

    def left_eye_lacrimal_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_lacrimal_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_lacrimal_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_lacrimal_lower_FK_ctrl')
            else:
                print('no existing object!!')

    def left_eye_back_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_back_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_back_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_back_ctrl')
            else:
                print('no existing object!!')

    def left_eye_back_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_back_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_back_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_back_upper_FK_ctrl')
            else:
                print('no existing object!!')

    def left_eye_back_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_back_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_back_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_back_lower_FK_ctrl')
            else:
                print('no existing object!!')

    def left_eye_double_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_double_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_double_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_double_ctrl')
            else:
                print('no existing object!!')

    def right_eye_lacrimal_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_lacrimal_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_lacrimal_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_lacrimal_ctrl')
            else:
                print('no existing object!!')

    def right_eye_lacrimal_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_lacrimal_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_lacrimal_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_lacrimal_upper_FK_ctrl')
            else:
                print('no existing object!!')

    def right_eye_lacrimal_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_lacrimal_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_lacrimal_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_lacrimal_lower_FK_ctrl')
            else:
                print('no existing object!!')

    def right_eye_back_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_back_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_back_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_back_ctrl')
            else:
                print('no existing object!!')

    def right_eye_back_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_back_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_back_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_back_upper_FK_ctrl')
            else:
                print('no existing object!!')

    def right_eye_back_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_back_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_back_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_back_lower_FK_ctrl')
            else:
                print('no existing object!!')

    def R_eye_double_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_double_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_double_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_double_ctrl')
            else:
                print('no existing object!!')

    def L_eye_target_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_target_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_eye_target_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_eye_target_ctrl')
            else:
                print('no existing object!!')

    def R_eye_target_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_eye_target_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_eye_target_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_eye_target_ctrl')
            else:
                print('no existing object!!')

    def Eye_target_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Eye_target_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Eye_target_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Eye_target_Master_ctrl')
            else:
                print('no existing object!!')

    def Eye_World_point_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Eye_World_point_loc'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Eye_World_point_loc', tgl=True)
                else:
                    cmds.select(self.np + 'Eye_World_point_loc')
            else:
                print('no existing object!!')

    def L_Eye_World_point_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_Eye_World_point_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_Eye_World_point_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_Eye_World_point_ctrl')
            else:
                print('no existing object!!')

    def R_Eye_World_point_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_Eye_World_point_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_Eye_World_point_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_Eye_World_point_ctrl')
            else:
                print('no existing object!!')

    def L_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_nose_ctrl')
            else:
                print('no existing object!!')

    def L_nasalis_transverse_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_nasalis_transverse_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_nasalis_transverse_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_nasalis_transverse_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def L_procerus_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_procerus_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_procerus_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_procerus_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def L_nasolabial_fold_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_nasolabial_fold_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_nasolabial_fold_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_nasolabial_fold_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def R_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_nose_ctrl')
            else:
                print('no existing object!!')

    def R_nasalis_transverse_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_nasalis_transverse_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_nasalis_transverse_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_nasalis_transverse_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def R_procerus_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_procerus_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_procerus_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_procerus_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def R_nasolabial_fold_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_nasolabial_fold_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_nasolabial_fold_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_nasolabial_fold_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def Nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Nose_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Nose_ctrl')
            else:
                print('no existing object!!')

    def Lower_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_nose_ctrl')
            else:
                print('no existing object!!')

    def depressor_septi_nose_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'depressor_septi_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'depressor_septi_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'depressor_septi_nose_FK_ctrl')
            else:
                print('no existing object!!')

    def L_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_cheek_ctrl')
            else:
                print('no existing object!!')

    def R_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_cheek_ctrl')
            else:
                print('no existing object!!')

    def L_upper_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_upper_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_upper_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_upper_cheek_ctrl')
            else:
                print('no existing object!!')

    def L_outer_orbicularis_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_outer_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_outer_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_outer_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')

    def L_inner_orbicularis_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_inner_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_inner_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_inner_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')

    def R_upper_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_upper_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_upper_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_upper_cheek_ctrl')
            else:
                print('no existing object!!')

    def R_outer_orbicularis_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_outer_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_outer_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_outer_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')

    def R_inner_orbicularis_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_inner_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_inner_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_inner_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')

    def L_lower_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lower_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lower_cheek_ctrl')
            else:
                print('no existing object!!')

    def R_lower_cheek_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lower_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lower_cheek_ctrl')
            else:
                print('no existing object!!')

    def L_lower_liplid_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lower_liplid_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lower_liplid_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lower_liplid_ctrl')
            else:
                print('no existing object!!')

    def R_lower_liplid_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lower_liplid_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lower_liplid_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lower_liplid_ctrl')
            else:
                print('no existing object!!')

    def L_lip_corner_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_corner_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_corner_Ctrl')
            else:
                print('no existing object!!')

    def R_lip_corner_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_corner_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_corner_Ctrl')
            else:
                print('no existing object!!')

    def L_lip_corner_up_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_corner_up_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_corner_up_Ctrl')
            else:
                print('no existing object!!')

    def L_lip_corner_up_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_up_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_corner_up_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_corner_up_FK_Ctrl')
            else:
                print('no existing object!!')

    def R_lip_corner_up_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_corner_up_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_corner_up_Ctrl')
            else:
                print('no existing object!!')

    def R_lip_corner_up_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_corner_up_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_corner_up_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_corner_up_FK_Ctrl')
            else:
                print('no existing object!!')

    def L_lip_corner_down_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_corner_down_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_corner_down_Ctrl')
            else:
                print('no existing object!!')

    def L_lip_corner_down_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_down_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_corner_down_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_corner_down_FK_Ctrl')
            else:
                print('no existing object!!')

    def R_lip_corner_down_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_corner_down_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_corner_down_Ctrl')
            else:
                print('no existing object!!')

    def R_lip_corner_down_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_corner_down_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_corner_down_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_corner_down_FK_Ctrl')
            else:
                print('no existing object!!')

    def Upper_lip_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Upper_lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Upper_lip_Master_ctrl')
            else:
                print('no existing object!!')

    def Lower_lip_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_lip_Master_ctrl')
            else:
                print('no existing object!!')

    def Upper_lip_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_lip_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Upper_lip_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Upper_lip_ctrl')
            else:
                print('no existing object!!')

    def Upper_lip_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_lip_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Upper_lip_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Upper_lip_FK_ctrl')
            else:
                print('no existing object!!')

    def Lower_lip_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_lip_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_lip_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_lip_ctrl')
            else:
                print('no existing object!!')

    def Lower_lip_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_lip_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_lip_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_lip_FK_ctrl')
            else:
                print('no existing object!!')

    def Lower_lip_outer_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_lip_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_lip_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_lip_outer_ctrl')
            else:
                print('no existing object!!')

    def L_lip_upper_side_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_upper_side_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_upper_side_ctrl')
            else:
                print('no existing object!!')

    def L_lip_upper_side_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_upper_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_upper_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_upper_side_FK_ctrl')
            else:
                print('no existing object!!')

    def L_lip_upper_side_02_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_upper_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_upper_side_02_FK_ctrl')
            else:
                print('no existing object!!')

    def L_lip_upper_outer_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_upper_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_upper_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_upper_outer_ctrl')
            else:
                print('no existing object!!')

    def R_lip_upper_side_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_upper_side_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_upper_side_ctrl')
            else:
                print('no existing object!!')

    def R_lip_upper_side_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_upper_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_upper_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_upper_side_FK_ctrl')
            else:
                print('no existing object!!')

    def R_lip_upper_side_02_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_upper_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_upper_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_upper_side_02_FK_ctrl')
            else:
                print('no existing object!!')

    def R_lip_upper_outer_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_upper_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_upper_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_upper_outer_ctrl')
            else:
                print('no existing object!!')

    def L_lip_lower_side_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_lower_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_lower_side_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_lower_side_ctrl')
            else:
                print('no existing object!!')

    def L_lip_lower_side_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_lower_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_lower_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_lower_side_FK_ctrl')
            else:
                print('no existing object!!')

    def L_lip_lower_side_02_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_lower_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_lower_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_lower_side_02_FK_ctrl')
            else:
                print('no existing object!!')

    def L_lip_lower_outer_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_lower_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'L_lip_lower_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'L_lip_lower_outer_ctrl')
            else:
                print('no existing object!!')

    def R_lip_lower_side_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_lower_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_lower_side_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_lower_side_ctrl')
            else:
                print('no existing object!!')

    def R_lip_lower_side_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_lower_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_lower_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_lower_side_FK_ctrl')
            else:
                print('no existing object!!')

    def R_lip_lower_side_02_FK_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_lower_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_lower_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_lower_side_02_FK_ctrl')
            else:
                print('no existing object!!')

    def R_lip_lower_outer_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'R_lip_lower_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'R_lip_lower_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'R_lip_lower_outer_ctrl')
            else:
                print('no existing object!!')

    def Lip_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_Master_ctrl')
            else:
                print('no existing object!!')

    def Jaw_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Jaw_Master_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Jaw_Master_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Jaw_Master_Ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_Ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_bar_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_bar_ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_L_bar_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_L_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_L_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_L_bar_ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_R_bar_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_R_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_R_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_R_bar_ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_upper_bar_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_upper_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_upper_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_upper_bar_ctrl')
            else:
                print('no existing object!!')

    def Lip_FACS_lower_bar_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_lower_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lip_FACS_lower_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lip_FACS_lower_bar_ctrl')
            else:
                print('no existing object!!')

    def Upper_teeth_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_teeth_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Upper_teeth_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Upper_teeth_ctrl')
            else:
                print('no existing object!!')

    def Lower_teeth_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_teeth_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Lower_teeth_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Lower_teeth_ctrl')
            else:
                print('no existing object!!')

    def Tongue_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Tongue_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Tongue_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Tongue_ctrl')
            else:
                print('no existing object!!')

    def Tongue_02_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Tongue_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Tongue_02_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Tongue_02_ctrl')
            else:
                print('no existing object!!')

    def Tongue_03_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Tongue_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Tongue_03_ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Tongue_03_ctrl')
            else:
                print('no existing object!!')

    def Facial_Master_BtnCmd(self, *args):
        with UndoContext():
            if cmds.objExists(self.np + 'Facial_Master_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.np + 'Facial_Master_Ctrl', tgl=True)
                else:
                    cmds.select(self.np + 'Facial_Master_Ctrl')
            else:
                print('no existing object!!')

    def Lip_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_lip_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Upper_lip_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Upper_lip_FK_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Upper_lip_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lower_lip_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_lip_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lower_lip_FK_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_lip_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lower_lip_outer_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_lip_outer_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_upper_side_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_upper_side_02_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_upper_outer_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_ctrl'):
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_lower_side_02_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_lower_outer_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_upper_side_02_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_upper_outer_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_ctrl'):
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_lower_side_02_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_lower_outer_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_FK_Ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_corner_up_FK_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_FK_Ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_corner_down_FK_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.scaleZ', 1)
                if cmds.objExists(self.np + 'L_lip_corner_Ctrl.Zip'):
                    cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Zip', 0)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_FK_Ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_corner_up_FK_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_FK_Ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_corner_down_FK_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.scaleZ', 1)
                if cmds.objExists(self.np + 'R_lip_corner_Ctrl.Zip'):
                    cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Zip', 0)
            if cmds.objExists(self.np + 'Upper_lip_Master_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Upper_lip_Master_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lower_lip_Master_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_lip_Master_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_Master_ctrl'):
                cmds.setAttr(self.np + 'Lip_Master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Jaw_Master_Ctrl'):
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_bar_ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_bar_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_L_bar_ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_L_bar_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_R_bar_ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_R_bar_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_upper_bar_ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_upper_bar_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lip_FACS_lower_bar_ctrl'):
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lip_FACS_lower_bar_ctrl.scaleZ', 1)

    def Lip_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_Master_ctrl.Zip_val'):
                cmds.setAttr(self.np + 'Lip_Master_ctrl.Zip_val', 3)
            if cmds.objExists(self.np + 'Upper_lip_ctrl') and cmds.objExists(self.np + 'L_lip_upper_side_ctrl') and cmds.objExists(self.np + 'R_lip_upper_side_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'Upper_lip_ctrl') and cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl') and cmds.objExists(self.np + 'R_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'Lower_lip_ctrl') and cmds.objExists(self.np + 'L_lip_lower_side_ctrl') and cmds.objExists(self.np + 'R_lip_lower_side_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'Lower_lip_ctrl') and cmds.objExists(self.np + 'L_lip_lower_side_02_FK_ctrl') and cmds.objExists(self.np + 'R_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'L_lip_upper_side_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'L_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'R_lip_upper_side_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'R_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'L_lip_lower_side_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'L_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'R_lip_lower_side_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'R_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.np + 'Lower_lip_ctrl') and cmds.objExists(self.np + 'Lower_lip_outer_ctrl'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.lip_lower_outer_follow', 0.3)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl') and cmds.objExists(self.np + 'L_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'L_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_ctrl') and cmds.objExists(self.np + 'L_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'L_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl') and cmds.objExists(self.np + 'R_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'R_lip_upper_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_ctrl') and cmds.objExists(self.np + 'R_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'R_lip_lower_outer_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.np + 'Lip_Master_ctrl.scale_val'):
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scale_val', 0.8)
            if cmds.objExists(self.np + 'Lip_Master_ctrl.scale_min_val'):
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scale_min_val', 0.4)
            if cmds.objExists(self.np + 'Lip_Master_ctrl.scale_max_val'):
                cmds.setAttr(self.np + 'Lip_Master_ctrl.scale_max_val', 1.3)
            if cmds.objExists(self.np + 'Lower_lip_ctrl.scale_val'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'Lower_lip_ctrl.scale_val'):
                cmds.setAttr(self.np + 'Lower_lip_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl.scale_val'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl.scale_val_02'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl.scale_val'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl.scale_val'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl.scale_val_02'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl.scale_val'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_ctrl.scale_val'):
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'L_lip_lower_side_ctrl.scale_val_02'):
                cmds.setAttr(self.np + 'L_lip_lower_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl.scale_val'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_ctrl.scale_val'):
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.scale_val', 1)
            if cmds.objExists(self.np + 'R_lip_lower_side_ctrl.scale_val_02'):
                cmds.setAttr(self.np + 'R_lip_lower_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl.scale_val'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.scale_val', 1)

    def Lip_FACS_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Open_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Open_Follow', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Up_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Up_Follow', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Down_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Down_Follow', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Side_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Side_Follow', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Inside_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Inside_Follow', 1)
            if cmds.objExists(self.np + 'Lip_FACS_Ctrl.Outside_Follow'):
                cmds.setAttr(self.np + 'Lip_FACS_Ctrl.Outside_Follow', 1)

    def Lip_Nose_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'Upper_lip_ctrl') and cmds.objExists(self.np + 'Lower_nose_ctrl'):
                cmds.setAttr(self.np + 'Upper_lip_ctrl.Lower_Nose_follow', 0.5)
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl') and cmds.objExists(self.np + 'L_nose_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Nose_follow', 0.3)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl') and cmds.objExists(self.np + 'R_nose_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Nose_follow', 0.3)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl') and cmds.objExists(self.np + 'L_nose_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.Nose_follow', 0.5)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl') and cmds.objExists(self.np + 'R_nose_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.Nose_follow', 0.5)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl') and cmds.objExists(self.np + 'L_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl') and cmds.objExists(self.np + 'R_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'L_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'R_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.nasolabial_fold', 1)

    def Lip_Cheek_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl') and cmds.objExists(self.np + 'L_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Cheek_follow', 0.6)
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl') and cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Lower_Cheek_follow', 0.7)
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl') and cmds.objExists(self.np + 'L_upper_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Upper_Cheek_follow', 0.7)
            if cmds.objExists(self.np + 'L_lip_corner_Ctrl') and cmds.objExists(self.np + 'L_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_Ctrl.Liplid_follow', 0.5)
            if cmds.objExists(self.np + 'L_lip_upper_side_ctrl') and cmds.objExists(self.np + 'L_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_upper_side_ctrl.Cheek_follow', 0.5)
            if cmds.objExists(self.np + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_up_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.np + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'L_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'L_lip_corner_down_Ctrl.Liplid_follow', 0.3)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl') and cmds.objExists(self.np + 'R_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Cheek_follow', 0.6)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl') and cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Lower_Cheek_follow', 0.7)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl') and cmds.objExists(self.np + 'R_upper_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Upper_Cheek_follow', 0.7)
            if cmds.objExists(self.np + 'R_lip_corner_Ctrl') and cmds.objExists(self.np + 'R_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_Ctrl.Liplid_follow', 0.5)
            if cmds.objExists(self.np + 'R_lip_upper_side_ctrl') and cmds.objExists(self.np + 'R_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_upper_side_ctrl.Cheek_follow', 0.5)
            if cmds.objExists(self.np + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_up_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.np + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.np + 'R_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'R_lip_corner_down_Ctrl.Liplid_follow', 0.3)

    def Cheek_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lower_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_upper_cheek_ctrl'):
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_outer_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_outer_orbicularis_cheek_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_inner_orbicularis_cheek_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.np + 'L_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lower_liplid_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lower_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_upper_cheek_ctrl'):
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_outer_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_outer_orbicularis_cheek_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_inner_orbicularis_cheek_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.np + 'R_lower_liplid_ctrl'):
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lower_liplid_ctrl.scaleZ', 1)

    def Cheek_Eye_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_upper_cheek_ctrl') and cmds.objExists(self.np + 'L_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'L_upper_cheek_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'R_upper_cheek_ctrl') and cmds.objExists(self.np + 'R_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'R_upper_cheek_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'L_eye_lower_ctrl') and cmds.objExists(self.np + 'L_outer_orbicularis_cheek_FK_ctrl') and cmds.objExists(self.np + 'L_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.np + 'R_eye_lower_ctrl') and cmds.objExists(self.np + 'R_outer_orbicularis_cheek_FK_ctrl') and cmds.objExists(self.np + 'R_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.Orbicularis_cheek_follow', 1)

    def Nose_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_nose_ctrl'):
                cmds.setAttr(self.np + 'L_nose_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_nose_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.scaleZ', 1)
                if cmds.objExists(self.np + 'Nose_ctrl'):
                    cmds.setAttr(self.np + 'L_nose_ctrl.Center_Nose_follow', 0.2)
            if cmds.objExists(self.np + 'L_nasalis_transverse_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_nasalis_transverse_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.nasalis_transverse_follow', 1)
            if cmds.objExists(self.np + 'L_procerus_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_procerus_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.procerus_follow', 1)
            if cmds.objExists(self.np + 'L_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_nasolabial_fold_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.nasolabial_fold_follow', 2)
            if cmds.objExists(self.np + 'R_nose_ctrl'):
                cmds.setAttr(self.np + 'R_nose_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_nose_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.scaleZ', 1)
                if cmds.objExists(self.np + 'Nose_ctrl'):
                    cmds.setAttr(self.np + 'R_nose_ctrl.Center_Nose_follow', 0.2)
            if cmds.objExists(self.np + 'R_nasalis_transverse_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_nasalis_transverse_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.nasalis_transverse_follow', 1)
            if cmds.objExists(self.np + 'R_procerus_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_procerus_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.procerus_follow', 1)
            if cmds.objExists(self.np + 'R_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_nasolabial_fold_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.nasolabial_fold_follow', 2)
            if cmds.objExists(self.np + 'Nose_ctrl'):
                cmds.setAttr(self.np + 'Nose_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Nose_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Nose_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Nose_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Lower_nose_ctrl'):
                cmds.setAttr(self.np + 'Lower_nose_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_nose_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'depressor_septi_nose_FK_ctrl'):
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'depressor_septi_nose_FK_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_nose_ctrl.depressor_septi_follow', 1)
                cmds.setAttr(self.np + 'R_nose_ctrl.depressor_septi_follow', 1)

    def Brow_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_brow_ctrl'):
                cmds.setAttr(self.np + 'L_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_brow_ctrl.Brow_02_follow', 1)
                if cmds.objExists(self.np + 'Center_brow_ctrl'):
                    cmds.setAttr(self.np + 'L_brow_ctrl.Center_Brow_follow', 1)
                if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'L_brow_ctrl.medial_fibers_follow', 1)
            if cmds.objExists(self.np + 'L_brow_02_ctrl'):
                cmds.setAttr(self.np + 'L_brow_02_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.Brow_follow', 1)
                if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'L_brow_02_ctrl.lateral_fibers_follow', 1)
            if cmds.objExists(self.np + 'L_brow_03_ctrl'):
                cmds.setAttr(self.np + 'L_brow_03_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_brow_03_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_brow_02_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.np + 'L_medial_fibers_brow_ctrl'):
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.Brow_follow', 1)
                if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.lateral_fibers_follow', 1)
                if cmds.objExists(self.np + 'L_procerus_brow_FK_ctrl'):
                    cmds.setAttr(self.np + 'L_medial_fibers_brow_ctrl.procerus_follow', 1)
            if cmds.objExists(self.np + 'L_lateral_fibers_brow_ctrl'):
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.Brow_follow', 1)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.Brow_02_follow', 1)
                cmds.setAttr(self.np + 'L_lateral_fibers_brow_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.np + 'L_procerus_brow_FK_ctrl'):
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_procerus_brow_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_brow_ctrl'):
                cmds.setAttr(self.np + 'R_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_brow_ctrl.Brow_02_follow', 1)
                if cmds.objExists(self.np + 'Center_brow_ctrl'):
                    cmds.setAttr(self.np + 'R_brow_ctrl.Center_Brow_follow', 1)
                if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'R_brow_ctrl.medial_fibers_follow', 1)
            if cmds.objExists(self.np + 'R_brow_02_ctrl'):
                cmds.setAttr(self.np + 'R_brow_02_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.Brow_follow', 1)
                if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'R_brow_02_ctrl.lateral_fibers_follow', 1)
            if cmds.objExists(self.np + 'R_brow_03_ctrl'):
                cmds.setAttr(self.np + 'R_brow_03_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_brow_03_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_brow_02_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.np + 'R_medial_fibers_brow_ctrl'):
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.Brow_follow', 1)
                if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.lateral_fibers_follow', 1)
                if cmds.objExists(self.np + 'R_procerus_brow_FK_ctrl'):
                    cmds.setAttr(self.np + 'R_medial_fibers_brow_ctrl.procerus_follow', 1)
            if cmds.objExists(self.np + 'R_lateral_fibers_brow_ctrl'):
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.Brow_follow', 1)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.Brow_02_follow', 1)
                cmds.setAttr(self.np + 'R_lateral_fibers_brow_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.np + 'R_procerus_brow_FK_ctrl'):
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_procerus_brow_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Center_brow_ctrl'):
                cmds.setAttr(self.np + 'Center_brow_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Center_brow_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Center_brow_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Center_brow_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_brow_master_ctrl'):
                cmds.setAttr(self.np + 'L_brow_master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_brow_master_ctrl.Brow_02_follow', 1)
            if cmds.objExists(self.np + 'R_brow_master_ctrl'):
                cmds.setAttr(self.np + 'R_brow_master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.Brow_02_follow', 1)
            if cmds.objExists(self.np + 'R_brow_master_ctrl') and cmds.objExists(self.np + 'L_brow_03_ctrl'):
                cmds.setAttr(self.np + 'L_brow_master_ctrl.Brow_03_follow', 1)
                cmds.setAttr(self.np + 'R_brow_master_ctrl.Brow_03_follow', 1)

    def Eye_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_blink_ctrl'):
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_lower_ctrl.lower_FK_follow'):
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.lower_FK_follow', 1)
            if cmds.objExists(self.np + 'L_eye_lower_ctrl.side_shrink_follow'):
                cmds.setAttr(self.np + 'L_eye_lower_ctrl.side_shrink_follow', 1)
            if cmds.objExists(self.np + 'L_eye_lacrimal_ctrl'):
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'L_eye_lacrimal_upper_FK_ctrl'):
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_upper_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_lacrimal_lower_FK_ctrl'):
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_lacrimal_lower_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_back_ctrl'):
                cmds.setAttr(self.np + 'L_eye_back_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.np + 'L_eye_back_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'L_eye_back_upper_FK_ctrl'):
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_back_upper_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_back_lower_FK_ctrl'):
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_back_lower_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'L_eye_double_ctrl'):
                cmds.setAttr(self.np + 'L_eye_double_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_double_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.Up_Eye_Double_follow', 1)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.Down_Eye_Double_follow', 1)
            if cmds.objExists(self.np + 'R_eye_blink_ctrl'):
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_lower_ctrl.lower_FK_follow'):
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.lower_FK_follow', 1)
            if cmds.objExists(self.np + 'R_eye_lower_ctrl.side_shrink_follow'):
                cmds.setAttr(self.np + 'R_eye_lower_ctrl.side_shrink_follow', 1)
            if cmds.objExists(self.np + 'R_eye_lacrimal_ctrl'):
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'R_eye_lacrimal_upper_FK_ctrl'):
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_upper_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_lacrimal_lower_FK_ctrl'):
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_lacrimal_lower_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_back_ctrl'):
                cmds.setAttr(self.np + 'R_eye_back_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.np + 'R_eye_back_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.np + 'R_eye_back_upper_FK_ctrl'):
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_back_upper_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_back_lower_FK_ctrl'):
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_back_lower_FK_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_double_ctrl'):
                cmds.setAttr(self.np + 'R_eye_double_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_double_ctrl.scaleZ', 1)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.Up_Eye_Double_follow', 1)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.Down_Eye_Double_follow', 1)

    def Eye_Brow_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_blink_ctrl') and cmds.objExists(self.np + 'L_brow_master_ctrl'):
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.Up_Brow_Master_follow', 0.5)
                cmds.setAttr(self.np + 'L_eye_blink_ctrl.Down_Brow_Master_follow', 0.3)
            if cmds.objExists(self.np + 'R_eye_blink_ctrl') and cmds.objExists(self.np + 'R_brow_master_ctrl'):
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.Up_Brow_Master_follow', 0.5)
                cmds.setAttr(self.np + 'R_eye_blink_ctrl.Down_Brow_Master_follow', 0.3)
            if cmds.objExists(self.np + 'L_eye_double_ctrl') and cmds.objExists(self.np + 'L_brow_02_ctrl'):
                cmds.setAttr(self.np + 'L_brow_02_ctrl.Eye_Double_follow', 1)
            if cmds.objExists(self.np + 'R_eye_double_ctrl') and cmds.objExists(self.np + 'R_brow_02_ctrl'):
                cmds.setAttr(self.np + 'R_brow_02_ctrl.Eye_Double_follow', 1)

    def Eye_Target_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_target_ctrl'):
                cmds.setAttr(self.np + 'L_eye_target_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'R_eye_target_ctrl'):
                cmds.setAttr(self.np + 'R_eye_target_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Eye_target_Master_ctrl'):
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Eye_World_point_loc'):
                cmds.setAttr(self.np + 'Eye_World_point_loc.translateX', 0)
                cmds.setAttr(self.np + 'Eye_World_point_loc.translateY', 0)
                cmds.setAttr(self.np + 'Eye_World_point_loc.translateZ', 0)
                cmds.setAttr(self.np + 'Eye_World_point_loc.rotateX', 0)
                cmds.setAttr(self.np + 'Eye_World_point_loc.rotateY', 0)
                cmds.setAttr(self.np + 'Eye_World_point_loc.rotateZ', 0)
                cmds.setAttr(self.np + 'Eye_target_Master_ctrl.Target_World', 0)
            if cmds.objExists(self.np + 'L_Eye_World_point_ctrl'):
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'L_Eye_World_point_ctrl.rotateZ', 0)
            if cmds.objExists(self.np + 'R_Eye_World_point_ctrl'):
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'R_Eye_World_point_ctrl.rotateZ', 0)

    def Eye_Target_Eye_Connect_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'L_eye_target_ctrl') and cmds.objExists(self.np + 'L_eye_blink_ctrl'):
                cmds.setAttr(self.np + 'L_eye_target_ctrl.Blink', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.Eyelid_up_follow', 0.4)
            if cmds.objExists(self.np + 'R_eye_target_ctrl') and cmds.objExists(self.np + 'R_eye_blink_ctrl'):
                cmds.setAttr(self.np + 'R_eye_target_ctrl.Blink', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.Eyelid_up_follow', 0.4)
            if cmds.objExists(self.np + 'L_eye_target_ctrl') and cmds.objExists(self.np + 'L_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'L_eye_target_ctrl.Blink_Side', 0)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.Eyelid_down_follow', 0.4)
                cmds.setAttr(self.np + 'L_eye_target_ctrl.Eyelid_side_follow', 1)
            if cmds.objExists(self.np + 'R_eye_target_ctrl') and cmds.objExists(self.np + 'R_eye_lower_ctrl'):
                cmds.setAttr(self.np + 'R_eye_target_ctrl.Blink_Side', 0)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.Eyelid_down_follow', 0.4)
                cmds.setAttr(self.np + 'R_eye_target_ctrl.Eyelid_side_follow', 1)

    def Oral_Cavity_All_Ctrl_reset(self):
        with UndoContext():
            if cmds.objExists(self.np + 'Lower_teeth_ctrl'):
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Lower_teeth_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Upper_teeth_ctrl'):
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Upper_teeth_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Tongue_ctrl'):
                cmds.setAttr(self.np + 'Tongue_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Tongue_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Tongue_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Tongue_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Tongue_02_ctrl'):
                cmds.setAttr(self.np + 'Tongue_02_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Tongue_02_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Tongue_03_ctrl'):
                cmds.setAttr(self.np + 'Tongue_03_ctrl.translateX', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.translateY', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.translateZ', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.rotateX', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.rotateY', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.rotateZ', 0)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.scaleX', 1)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.scaleY', 1)
                cmds.setAttr(self.np + 'Tongue_03_ctrl.scaleZ', 1)
            if cmds.objExists(self.np + 'Jaw_Master_Ctrl') and cmds.objExists(self.np + 'Tongue_ctrl'):
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.Tongue_follow', 1)
            if cmds.objExists(self.np + 'Jaw_Master_Ctrl') and cmds.objExists(self.np + 'Lower_teeth_ctrl'):
                cmds.setAttr(self.np + 'Jaw_Master_Ctrl.Lower_Teeth_follow', 1)

if __name__ == '__main__':
    Facial_Picker_window.main()


