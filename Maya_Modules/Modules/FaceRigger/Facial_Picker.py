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

        self.BROW_ALL_GROUP_NAME = "Brow_All_Ctrl_grp"
        self.NOSE_ALL_GROUP_NAME = "Nose_All_Ctrl_grp"
        self.CHEEK_ALL_GROUP_NAME = "Cheek_All_Ctrl_grp"
        self.EYE_ALL_GROUP_NAME = "Eye_All_Ctrl_grp"
        self.LIP_ALL_GROUP_NAME = "Lip_All_Ctrl_grp"
        self.EYE_TARGET_ALL_GROUP_NAME = "Eye_target_All_Ctrl_grp"
        self.ORAL_CAVITY_ALL_GROUP_NAME = "Oral_Cavity_All_Ctrl_grp"

        self.K_TRANSLATION_ROTATION_ATTR = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        self.K_ROTATION_ATTR = ["rotateX", "rotateY", "rotateZ"]
        self.K_SCALE_ATTR = ["scaleX", "scaleY", "scaleX.Z"]

        self.JAW_MASTER_CONTROLLER_NAME = "Jaw_Master_Ctrl"
        self.LOWER_TEETH_CONTROLLER_NAME = "Lower_teeth_ctrl"
        self.UPPER_TEETH_CONTROLLER_NAME = "Upper_teeth_ctrl"

        self.setWindowTitle('FaceRig Picker')
        self.setFixedSize(705, 611)
        self.styles = 'Plastique'
        self._initialize_ui()
        self._create_layout()
        self._create_connections()
        self.green = 'background-color: rgb(051,153,102)'
        self.red = 'background-color: rgb(255,0,051)'
        self.gray = [0.15, 0.15, 0.15]
        self.blue = 'background-color: rgb(0,102,153)'
        self.magenta = 'background-color: rgb(204,0,102)'
        self.yellow = 'background-color: rgb(255,255,0)'
        self.white = 'background-color: rgb(255,255,255)'
        self.prefix = ''
        self.shift = 0
        self._name_space_combo_update()
        self._update_CV_command()

    def _initialize_ui(self):
        self.current_dir = os.path.dirname(__file__)
        f = QtCore.QFile(self.current_dir + '/ui/Facial_Picker.ui')
        f.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=None)
        self.setCentralWidget(self.ui)
        f.close()
        image_path = self.current_dir + '/icon/Facial_image.png'
        self.ui.Label_image.setPixmap(image_path)

    def _create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)
        self.ui.BtnGrp.setStyle(QtWidgets.QStyleFactory.create(self.styles))

    def _create_connections(self):
        self.ui.P_L_brow_Btn.clicked.connect(self._left_brow_command)
        self.ui.P_L_brow_02_Btn.clicked.connect(self._left_brow_02_command)
        self.ui.P_L_brow_03_Btn.clicked.connect(self._left_brow_03_command)
        self.ui.P_L_medial_fibers_brow_Btn.clicked.connect(self._left_medial_fibers_brow_command)
        self.ui.P_L_lateral_fibers_brow_Btn.clicked.connect(self._left_lateral_fibers_brow_command)
        self.ui.P_L_procerus_brow_Btn.clicked.connect(self._left_procerus_brow_command)

        self.ui.P_R_brow_Btn.clicked.connect(self._right_brow_command)
        self.ui.P_R_brow_02_Btn.clicked.connect(self._right_brow_02_command)
        self.ui.P_R_brow_03_Btn.clicked.connect(self._right_brow_03_command)
        self.ui.P_R_medial_fibers_brow_Btn.clicked.connect(self._right_medial_fibers_brow_command)
        self.ui.P_R_lateral_fibers_brow_Btn.clicked.connect(self._right_lateral_fibers_brow_command)
        self.ui.P_R_procerus_brow_Btn.clicked.connect(self._right_procerus_brow_command)

        self.ui.P_Center_brow_Btn.clicked.connect(self._center_brow_command)

        self.ui.P_L_brow_master_Btn.clicked.connect(self._left_brow_master_command)
        self.ui.P_L_eye_blink_Btn.clicked.connect(self._left_eye_blink_command)
        self.ui.P_L_eye_lower_Btn.clicked.connect(self._left_eye_lower_command)
        self.ui.P_L_eye_lacrimal_Btn.clicked.connect(self._left_eye_lacrimal_command)
        self.ui.P_L_eye_lacrimal_upper_Btn.clicked.connect(self._left_eye_lacrimal_upper_command)
        self.ui.P_L_eye_lacrimal_lower_Btn.clicked.connect(self._left_eye_lacrimal_lower_command)
        self.ui.P_L_eye_back_Btn.clicked.connect(self._left_eye_back_command)
        self.ui.P_L_eye_back_upper_Btn.clicked.connect(self._left_eye_back_upper_command)
        self.ui.P_L_eye_back_lower_Btn.clicked.connect(self._left_eye_back_lower_command)
        self.ui.P_L_eye_double_Btn.clicked.connect(self._left_eye_double_command)
        self.ui.P_L_eye_target_Btn.clicked.connect(self._left_eye_target_command)

        self.ui.P_R_brow_master_Btn.clicked.connect(self._right_brow_master_command)
        self.ui.P_R_eye_blink_Btn.clicked.connect(self._right_eye_blink_command)
        self.ui.P_R_eye_lower_Btn.clicked.connect(self._right_eye_lower_command)
        self.ui.P_R_eye_lacrimal_Btn.clicked.connect(self._right_eye_lacrimal_command)
        self.ui.P_R_eye_lacrimal_upper_Btn.clicked.connect(self._right_eye_lacrimal_upper_command)
        self.ui.P_R_eye_lacrimal_lower_Btn.clicked.connect(self._right_eye_lacrimal_lower_command)
        self.ui.P_R_eye_back_Btn.clicked.connect(self._right_eye_back_command)
        self.ui.P_R_eye_back_upper_Btn.clicked.connect(self._right_eye_back_upper_command)
        self.ui.P_R_eye_back_lower_Btn.clicked.connect(self._right_eye_back_lower_command)
        self.ui.P_R_eye_double_Btn.clicked.connect(self._right_eye_double_command)
        self.ui.P_R_eye_target_Btn.clicked.connect(self._right_eye_target_command)

        self.ui.P_Eye_target_Master_Btn.clicked.connect(self._eye_target_master_command)
        self.ui.P_Eye_World_point_Btn.clicked.connect(self._eye_world_point_command)

        self.ui.P_L_Eye_World_point_Btn.clicked.connect(self._left_eye_world_point_command)
        self.ui.P_L_nose_Btn.clicked.connect(self._left_nose_command)
        self.ui.P_L_nasalis_transverse_nose_Btn.clicked.connect(self._left_nasalis_transverse_nose_command)
        self.ui.P_L_procerus_nose_Btn.clicked.connect(self._left_procerus_nose_command)
        self.ui.P_L_nasolabial_fold_nose_Btn.clicked.connect(self._left_nasolabial_fold_nose_command)

        self.ui.P_R_Eye_World_point_Btn.clicked.connect(self._right_eye_world_point_command)
        self.ui.P_R_nasalis_transverse_nose_Btn.clicked.connect(self._right_nasalis_transverse_nose_command)
        self.ui.P_R_procerus_nose_Btn.clicked.connect(self._right_procerus_nose_command)
        self.ui.P_R_nasolabial_fold_nose_Btn.clicked.connect(self._right_nasolabial_fold_nose_command)
        self.ui.P_R_nose_Btn.clicked.connect(self._right_nose_command)

        self.ui.P_Nose_Btn.clicked.connect(self._nose_command)
        self.ui.P_Lower_nose_Btn.clicked.connect(self._lower_nose_command)
        self.ui.P_depressor_septi_nose_Btn.clicked.connect(self._depressor_septi_nose_command)

        self.ui.P_L_cheek_Btn.clicked.connect(self._left_cheek_command)
        self.ui.P_L_upper_cheek_Btn.clicked.connect(self._left_upper_cheek_command)
        self.ui.P_L_outer_orbicularis_cheek_Btn.clicked.connect(self._left_outer_orbicularis_cheek_command)
        self.ui.P_L_inner_orbicularis_cheek_Btn.clicked.connect(self._left_inner_orbicularis_cheek_command)
        self.ui.P_L_lower_cheek_Btn.clicked.connect(self._left_lower_cheek_command)
        self.ui.P_L_lower_liplid_Btn.clicked.connect(self._left_lower_liplid_command)
        self.ui.P_L_lip_corner_Btn.clicked.connect(self._left_lip_corner_command)
        self.ui.P_L_lip_corner_up_Btn.clicked.connect(self._left_lip_corner_up_command)
        self.ui.P_L_lip_corner_up_FK_Btn.clicked.connect(self._left_lip_corner_up_FK_command)
        self.ui.P_L_lip_corner_down_Btn.clicked.connect(self._left_lip_corner_down_command)
        self.ui.P_L_lip_corner_down_FK_Btn.clicked.connect(self._left_lip_corner_down_FK_command)

        self.ui.P_R_cheek_Btn.clicked.connect(self._right_cheek_command)
        self.ui.P_R_upper_cheek_Btn.clicked.connect(self._right_upper_cheek_command)
        self.ui.P_R_outer_orbicularis_cheek_Btn.clicked.connect(self._right_outer_orbicularis_cheek_command)
        self.ui.P_R_inner_orbicularis_cheek_Btn.clicked.connect(self._right_inner_orbicularis_cheek_command)
        self.ui.P_R_lower_cheek_Btn.clicked.connect(self._right_lower_cheek_command)
        self.ui.P_R_lower_liplid_Btn.clicked.connect(self._right_lower_liplid_command)
        self.ui.P_R_lip_corner_Btn.clicked.connect(self._right_lip_corner_command)
        self.ui.P_R_lip_corner_up_Btn.clicked.connect(self._right_lip_corner_up_command)
        self.ui.P_R_lip_corner_up_FK_Btn.clicked.connect(self._right_lip_corner_up_FK_command)
        self.ui.P_R_lip_corner_down_Btn.clicked.connect(self._right_lip_corner_down_command)
        self.ui.P_R_lip_corner_down_FK_Btn.clicked.connect(self._right_lip_corner_down_FK_command)

        self.ui.P_Upper_lip_Master_Btn.clicked.connect(self._upper_lip_Master_command)
        self.ui.P_Upper_lip_Btn.clicked.connect(self._upper_lip_command)
        self.ui.P_Upper_lip_FK_Btn.clicked.connect(self._upper_lip_FK_command)

        self.ui.P_Lower_lip_Master_Btn.clicked.connect(self._lower_lip_Master_command)
        self.ui.P_Lower_lip_Btn.clicked.connect(self._lower_lip_command)
        self.ui.P_Lower_lip_FK_Btn.clicked.connect(self._lower_lip_FK_command)

        self.ui.P_Lower_lip_outer_Btn.clicked.connect(self._lower_lip_outer_command)

        self.ui.P_L_lip_upper_side_Btn.clicked.connect(self._left_lip_upper_side_command)
        self.ui.P_L_lip_upper_side_FK_Btn.clicked.connect(self._left_lip_upper_side_FK_command)
        self.ui.P_L_lip_upper_side_02_FK_Btn.clicked.connect(self._left_lip_upper_side_02_FK_command)
        self.ui.P_L_lip_upper_outer_Btn.clicked.connect(self._left_lip_upper_outer_command)
        self.ui.P_L_lip_lower_side_Btn.clicked.connect(self._left_lip_lower_side_command)
        self.ui.P_L_lip_lower_side_FK_Btn.clicked.connect(self._left_lip_lower_side_FK_command)
        self.ui.P_L_lip_lower_side_02_FK_Btn.clicked.connect(self._left_lip_lower_side_02_FK_command)
        self.ui.P_L_lip_lower_outer_Btn.clicked.connect(self._left_lip_lower_outer_command)

        self.ui.P_R_lip_upper_side_Btn.clicked.connect(self._right_lip_upper_side_command)
        self.ui.P_R_lip_upper_side_FK_Btn.clicked.connect(self._right_lip_upper_side_FK_command)
        self.ui.P_R_lip_upper_side_02_FK_Btn.clicked.connect(self._right_lip_upper_side_02_FK_command)
        self.ui.P_R_lip_upper_outer_Btn.clicked.connect(self._right_lip_upper_outer_command)
        self.ui.P_R_lip_lower_side_Btn.clicked.connect(self._right_lip_lower_side_command)
        self.ui.P_R_lip_lower_side_FK_Btn.clicked.connect(self._right_lip_lower_side_FK_command)
        self.ui.P_R_lip_lower_side_02_FK_Btn.clicked.connect(self._right_lip_lower_side_02_FK_command)
        self.ui.P_R_lip_lower_outer_Btn.clicked.connect(self._right_lip_lower_outer_command)

        self.ui.P_Lip_Master_Btn.clicked.connect(self._lip_master_command)
        self.ui.P_Jaw_Master_Btn.clicked.connect(self._jaw_master_command)
        self.ui.P_Lip_FACS_Btn.clicked.connect(self._lip_FACS_command)
        self.ui.P_Lip_FACS_bar_Btn.clicked.connect(self._lip_FACS_bar_command)
        self.ui.P_Lip_FACS_L_bar_Btn.clicked.connect(self._lip_FACS_left_bar_command)
        self.ui.P_Lip_FACS_R_bar_Btn.clicked.connect(self._lip_FACS_right_bar_command)
        self.ui.P_Lip_FACS_upper_bar_Btn.clicked.connect(self._lip_FACS_upper_bar_command)
        self.ui.P_Lip_FACS_lower_bar_Btn.clicked.connect(self._lip_FACS_lower_bar_command)
        self.ui.P_Upper_teeth_Btn.clicked.connect(self._upper_teeth_command)
        self.ui.P_Lower_teeth_Btn.clicked.connect(self._lower_teeth_command)
        self.ui.P_Tongue_Btn.clicked.connect(self._tongue_command)
        self.ui.P_Tongue_02_Btn.clicked.connect(self._tongue_02_command)
        self.ui.P_Tongue_03_Btn.clicked.connect(self._tongue_03_command)
        self.ui.P_Facial_Master_Btn.clicked.connect(self._facial_master_command)

        self.ui.UpdateCVBtn.clicked.connect(self._name_space_combo_update)
        self.ui.UpdateCVBtn.clicked.connect(self._update_CV_command)
        self.ui.PrimaryCheckBox.stateChanged.connect(self._check_box_state_command)
        self.ui.SecondaryCheckBox.stateChanged.connect(self._check_box_state_command)
        self.ui.MasterCheckBox.stateChanged.connect(self._check_box_state_command)
        self.ui.FKCheckBox.stateChanged.connect(self._check_box_state_command)
        self.ui.OralCavityCheckBox.stateChanged.connect(self._check_box_state_command)
        self.ui.Reset_CtrlBtn.clicked.connect(self._reset_control_command)
        self.ui.SelAll_CtrlBtn.clicked.connect(self._select_all_control_command)
        self.ui.Reset_BrowBtn.clicked.connect(self._reset_brow_command)
        self.ui.Select_BrowBtn.clicked.connect(self._select_brow_command)
        self.ui.Reset_EyeBtn.clicked.connect(self._reset_eye_command)
        self.ui.Select_EyeBtn.clicked.connect(self._select_eye_command)
        self.ui.Reset_EyeTargetBtn.clicked.connect(self._reset_eye_target_command)
        self.ui.Select_EyeTargetBtn.clicked.connect(self._select_eye_target_command)
        self.ui.Reset_NoseBtn.clicked.connect(self._reset_nose_command)
        self.ui.Select_NoseBtn.clicked.connect(self._select_nose_command)
        self.ui.Reset_CheekBtn.clicked.connect(self._reset_cheek_command)
        self.ui.Select_CheekBtn.clicked.connect(self._select_cheek_command)
        self.ui.Reset_LipBtn.clicked.connect(self._reset_lip_command)
        self.ui.Select_LipBtn.clicked.connect(self._select_lip_command)
        self.ui.Reset_OralBtn.clicked.connect(self._reset_oral_command)
        self.ui.Select_OralBtn.clicked.connect(self._select_oral_command)
        self.ui.Reset_LipFollowBtn.clicked.connect(self._reset_lip_follow_command)
        self.ui.Reset_Lip_FACSBtn.clicked.connect(self._reset_lip_FACS_command)
        self.ui.Reset_NoseFollowBtn.clicked.connect(self._reset_nose_follow_command)
        self.ui.Reset_CheekFollowBtn.clicked.connect(self._reset_cheek_follow_command)
        self.ui.Reset_EyeLowerFollowBtn.clicked.connect(self._reset_eye_lower_follow_command)
        self.ui.Reset_BrowFollowBtn.clicked.connect(self._reset_brow_follow_command)
        self.ui.Reset_EyeFollowBtn.clicked.connect(self._reset_eye_follow_command)
        self.ui.NameSpace_Combo.currentTextChanged.connect(self._update_CV_command)

    def _name_space_combo_update(self):
        self.ui.NameSpace_Combo.clear()
        self.ui.NameSpace_Combo.addItem('')
        all_nameSpace_list = self._find_all_name_space()
        if all_nameSpace_list:
            for each in all_nameSpace_list:
                self.ui.NameSpace_Combo.addItem(each)
        print("_name_space_combo_update")

    def _find_all_name_space(self):
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
        print("_find_all_name_space => {}".format(all_nameSpace_list))
        return all_nameSpace_list

    def _do_something(self):
        any_sel = cmds.ls(sl=True)
        for each in any_sel:
            print(each)
            self.another_dialog.textEdit.setText(each)
            self.ui.lineEdit.setText(each)

    def _reset_control_command(self, *args):
        with UndoContext():
            self._reset_lip_command()
            self._reset_lip_follow_command()
            self._reset_lip_FACS_command()
            self._reset_nose_follow_command()
            self._reset_cheek_follow_command()
            self._reset_cheek_command()
            self._reset_eye_lower_follow_command()
            self._reset_nose_command()
            self._reset_brow_command()
            self._reset_eye_command()
            self._reset_brow_follow_command()
            self._reset_eye_target_command()
            self._reset_eye_follow_command()
            self._reset_oral_command()
            if cmds.objExists(self.prefix + 'Facial_Master_Ctrl'):
                self._reset_joint_transform('Facial_Master_Ctrl')
        print("_reset_control_command")

    # select all controllers
    def _select_all_control_command(self, *args):
        with UndoContext():
            self._select_brow_command()
            brow_sel_all = cmds.ls(sl=True)
            self._select_eye_command()
            eye_sel_all = cmds.ls(sl=True)
            self._select_eye_target_command()
            eye_target_sel_all = cmds.ls(sl=True)
            self._select_nose_command()
            nose_sel_all = cmds.ls(sl=True)
            self._select_cheek_command()
            cheek_sel_all = cmds.ls(sl=True)
            self._select_lip_command()
            lip_sel_all = cmds.ls(sl=True)
            self._select_oral_command()
            oral_sel_all = cmds.ls(sl=True)
            cmds.select(brow_sel_all, eye_sel_all, eye_target_sel_all, nose_sel_all, cheek_sel_all, lip_sel_all, oral_sel_all)
        print("_select_all_control_command")

    def _reset_brow_command(self, *args):
        if cmds.objExists(self.prefix + self.BROW_ALL_GROUP_NAME):
            self._brow_all_control_reset()
            print('_reset_brow_command')

    def _select_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.BROW_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + '*brow*ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + '*brow*ctrl')
        print('_select_brow_command')

    def _reset_eye_command(self, *args):
        if cmds.objExists(self.prefix + self.EYE_ALL_GROUP_NAME):
            self._eye_all_control_reset()
            print('_reset_eye_command')

    def _select_eye_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.EYE_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + '*eye_blink*ctrl', tgl=True)
                    if cmds.objExists(self.prefix + '*eye_lower*ctrl'):
                        cmds.select(self.prefix + '*eye_lower*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*lacrimal*ctrl') and cmds.objExists(self.prefix + '*back*ctrl'):
                        cmds.select(self.prefix + '*back*ctrl', self.prefix + '*lacrimal*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*double*ctrl'):
                        cmds.select(self.prefix + '*double*ctrl', add=True)
                else:
                    cmds.select(self.prefix + '*eye_blink*ctrl')
                    if cmds.objExists(self.prefix + '*eye_lower*ctrl'):
                        cmds.select(self.prefix + '*eye_lower*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*lacrimal*ctrl') and cmds.objExists(self.prefix + '*back*ctrl'):
                        cmds.select(self.prefix + '*back*ctrl', self.prefix + '*lacrimal*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*double*ctrl'):
                        cmds.select(self.prefix + '*double*ctrl', add=True)
        print("_select_eye_command")

    def _reset_eye_target_command(self, *args):
        if cmds.objExists(self.prefix + self.EYE_TARGET_ALL_GROUP_NAME):
            self._eye_target_all_control_reset()
            print("_reset_eye_target_command")

    def _select_eye_target_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.EYE_TARGET_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + '*target*ctrl', tgl=True)
                    cmds.select(self.prefix + 'Eye_World_point_loc', add=True)
                    cmds.select(self.prefix + 'L_Eye_World_point_ctrl', add=True)
                    cmds.select(self.prefix + 'R_Eye_World_point_ctrl', add=True)
                else:
                    cmds.select(self.prefix + '*target*ctrl')
                    cmds.select(self.prefix + 'Eye_World_point_loc', add=True)
                    cmds.select(self.prefix + 'L_Eye_World_point_ctrl', add=True)
                    cmds.select(self.prefix + 'R_Eye_World_point_ctrl', add=True)
        print("_select_eye_target_command")

    def _reset_nose_command(self, *args):
        if cmds.objExists(self.prefix + self.NOSE_ALL_GROUP_NAME):
            self._nose_all_control_reset()
            print("_reset_nose_command")

    def _select_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.NOSE_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    if cmds.objExists(self.prefix + '*nose*ctrl'):
                        cmds.select(self.prefix + '*nose*ctrl', tgl=True)
                    if cmds.objExists(self.prefix + 'Nose_ctrl'):
                        cmds.select(self.prefix + 'Nose_ctrl', add=True)
                else:
                    if cmds.objExists(self.prefix + '*nose*ctrl'):
                        cmds.select(self.prefix + '*nose*ctrl')
                    if cmds.objExists(self.prefix + 'Nose_ctrl'):
                        cmds.select(self.prefix + 'Nose_ctrl', add=True)
        print("_select_nose_command")

    def _reset_cheek_command(self, *args):
        if cmds.objExists(self.prefix + self.CHEEK_ALL_GROUP_NAME):
            self._cheek_all_control_reset()
            print("_reset_cheek_command")

    def _select_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.CHEEK_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + '*cheek*ctrl', tgl=True)
                    if cmds.objExists(self.prefix + '*_lower_liplid_ctrl'):
                        cmds.select(self.prefix + '*_lower_liplid_ctrl', add=True)
                else:
                    cmds.select(self.prefix + '*cheek*ctrl')
                    if cmds.objExists(self.prefix + '*_lower_liplid_ctrl'):
                        cmds.select(self.prefix + '*_lower_liplid_ctrl', add=True)
        print("_select_cheek_command")

    def _reset_lip_command(self, *args):
        if cmds.objExists(self.prefix + self.LIP_ALL_GROUP_NAME):
            self._lip_all_control_reset()
            print("_reset_lip_command")

    def _select_lip_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.LIP_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + self.JAW_MASTER_CONTROLLER_NAME, tgl=True)
                    if cmds.objExists(self.prefix + '*lip*Ctrl'):
                        cmds.select(self.prefix + '*lip*Ctrl', add=True)
                    if cmds.objExists(self.prefix + '*lip*side*ctrl'):
                        cmds.select(self.prefix + '*lip*side*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_ctrl'):
                        cmds.select(self.prefix + '*_lip_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_FK_ctrl'):
                        cmds.select(self.prefix + '*_lip_FK_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_*outer_ctrl'):
                        cmds.select(self.prefix + '*_lip_*outer_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_Master_ctrl'):
                        cmds.select(self.prefix + '*_lip_Master_ctrl', add=True)
                    if cmds.objExists(self.prefix + 'Lip_Master_ctrl'):
                        cmds.select(self.prefix + 'Lip_Master_ctrl', add=True)
                    if cmds.objExists(self.prefix + 'Lip_FACS_*bar_ctrl'):
                        cmds.select(self.prefix + 'Lip_FACS_*bar_ctrl', add=True)
                else:
                    cmds.select(self.prefix + self.JAW_MASTER_CONTROLLER_NAME)
                    if cmds.objExists(self.prefix + '*lip*Ctrl'):
                        cmds.select(self.prefix + '*lip*Ctrl', add=True)
                    if cmds.objExists(self.prefix + '*lip*side*ctrl'):
                        cmds.select(self.prefix + '*lip*side*ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_ctrl'):
                        cmds.select(self.prefix + '*_lip_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_FK_ctrl'):
                        cmds.select(self.prefix + '*_lip_FK_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_*outer_ctrl'):
                        cmds.select(self.prefix + '*_lip_*outer_ctrl', add=True)
                    if cmds.objExists(self.prefix + '*_lip_Master_ctrl'):
                        cmds.select(self.prefix + '*_lip_Master_ctrl', add=True)
                    if cmds.objExists(self.prefix + 'Lip_Master_ctrl'):
                        cmds.select(self.prefix + 'Lip_Master_ctrl', add=True)
                    if cmds.objExists(self.prefix + 'Lip_FACS_*bar_ctrl'):
                        cmds.select(self.prefix + 'Lip_FACS_*bar_ctrl', add=True)
        print("_select_lip_command")

    def _reset_oral_command(self, *args):
        if cmds.objExists(self.prefix + self.ORAL_CAVITY_ALL_GROUP_NAME):
            self._oral_cavity_all_control_reset()
            print("_reset_oral_command")

    def _select_oral_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.ORAL_CAVITY_ALL_GROUP_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + '*teeth*ctrl', tgl=True)
                    if cmds.objExists(self.prefix + 'Tongue_*ctrl'):
                        cmds.select(self.prefix + 'Tongue_*ctrl', add=True)
                else:
                    cmds.select(self.prefix + '*teeth*ctrl')
                    if cmds.objExists(self.prefix + 'Tongue_*ctrl'):
                        cmds.select(self.prefix + 'Tongue_*ctrl', add=True)
        print("_select_oral_command")

    def _reset_lip_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.LIP_ALL_GROUP_NAME):
            self._lip_connect_control_reset()
            print("_reset_lip_follow_command")

    def _reset_lip_FACS_command(self, *args):
        if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl'):
            self._lip_FACS_control_reset()
            print("_reset_lip_FACS_command")

    def _reset_nose_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.LIP_ALL_GROUP_NAME) and cmds.objExists(self.prefix + self.NOSE_ALL_GROUP_NAME):
            self._lip_nose_connect_control_reset()
            print("_reset_nose_follow_command")

    def _reset_cheek_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.LIP_ALL_GROUP_NAME) and cmds.objExists(self.prefix + self.CHEEK_ALL_GROUP_NAME):
            self._lip_cheek_connect_control_reset()
            print("_reset_cheek_follow_command")

    def _reset_eye_lower_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.CHEEK_ALL_GROUP_NAME) and cmds.objExists(self.prefix + self.EYE_ALL_GROUP_NAME):
            self._cheek_eye_connect_control_reset()
            print("_reset_eye_lower_follow_command")

    def _reset_brow_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.EYE_ALL_GROUP_NAME) and cmds.objExists(self.prefix + self.BROW_ALL_GROUP_NAME):
            self._eye_brow_connect_control_reset()
            print("_reset_brow_follow_command")

    def _reset_eye_follow_command(self, *args):
        if cmds.objExists(self.prefix + self.EYE_TARGET_ALL_GROUP_NAME) and cmds.objExists(self.prefix + self.EYE_ALL_GROUP_NAME):
            self._eye_target_eye_connect_control_reset()
            print("_reset_eye_follow_command")

    def _check_box_state_command(self, *args):
        self._update_CV_command()
        print("_check_box_state_command")

    # @TODO
    # Refactoring
    def _update_CV_command(self, *args):
        self.prefix = self.ui.NameSpace_Combo.currentText()
        print("current name space => {}".format(self.prefix))

        if cmds.objExists(self.prefix + 'L_brow_ctrl'):
            if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'L_brow_02_ctrl'):
            if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'L_brow_03_ctrl'):
            if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl') is False and cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_procerus_brow_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_brow_ctrl'):
            if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'R_brow_02_ctrl'):
            if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'R_brow_03_ctrl'):
            if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl') is False and cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl') is False:
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

        if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_procerus_brow_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'Center_brow_ctrl'):
            if cmds.objExists(self.prefix + 'L_brow_ctrl') is True or cmds.objExists(self.prefix + 'R_brow_ctrl') is True:
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

        if cmds.objExists(self.prefix + 'L_brow_master_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_brow_master_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_blink_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_blink_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_lower_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_lower_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_lacrimal_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_lacrimal_upper_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_lacrimal_lower_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_back_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_back_upper_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_back_lower_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_double_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_lacrimal_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_lacrimal_upper_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_lacrimal_lower_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_back_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_back_upper_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_back_lower_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_eye_double_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_eye_target_ctrl'):
            self.ui.P_L_eye_target_Btn.setStyleSheet(self.green)
            self.ui.P_L_eye_target_Btn.setEnabled(True)
        else:
            self.ui.P_L_eye_target_Btn.setEnabled(False)
            self.ui.P_L_eye_target_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'R_eye_target_ctrl'):
            self.ui.P_R_eye_target_Btn.setStyleSheet(self.blue)
            self.ui.P_R_eye_target_Btn.setEnabled(True)
        else:
            self.ui.P_R_eye_target_Btn.setEnabled(False)
            self.ui.P_R_eye_target_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Eye_target_Master_ctrl'):
            self.ui.P_Eye_target_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Eye_target_Master_Btn.setEnabled(True)
        else:
            self.ui.P_Eye_target_Master_Btn.setEnabled(False)
            self.ui.P_Eye_target_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Eye_World_point_loc'):
            self.ui.P_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'L_Eye_World_point_ctrl'):
            self.ui.P_L_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_L_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_L_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_L_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'R_Eye_World_point_ctrl'):
            self.ui.P_R_Eye_World_point_Btn.setStyleSheet(self.yellow)
            self.ui.P_R_Eye_World_point_Btn.setEnabled(True)
        else:
            self.ui.P_R_Eye_World_point_Btn.setEnabled(False)
            self.ui.P_R_Eye_World_point_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'L_nose_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_nasalis_transverse_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_procerus_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_nose_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_nasalis_transverse_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_procerus_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'Nose_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lower_nose_ctrl'):
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

        if cmds.objExists(self.prefix + 'depressor_septi_nose_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_upper_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_upper_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lower_liplid_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lower_liplid_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_corner_up_FK_Ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_corner_up_FK_Ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_corner_down_FK_Ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_corner_down_FK_Ctrl'):
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

        if cmds.objExists(self.prefix + 'Upper_lip_Master_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lower_lip_Master_ctrl'):
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

        if cmds.objExists(self.prefix + 'Upper_lip_ctrl'):
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

        if cmds.objExists(self.prefix + 'Upper_lip_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lower_lip_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lower_lip_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lower_lip_outer_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_upper_side_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_upper_outer_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_upper_side_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_upper_outer_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_lower_side_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_lower_side_02_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'L_lip_lower_outer_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_lower_side_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_lower_side_02_FK_ctrl'):
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

        if cmds.objExists(self.prefix + 'R_lip_lower_outer_ctrl'):
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

        if cmds.objExists(self.prefix + 'Lip_Master_ctrl'):
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

        if cmds.objExists(self.prefix + self.JAW_MASTER_CONTROLLER_NAME):
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

        if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl'):
            self.ui.P_Lip_FACS_Btn.setStyleSheet(self.red)
            self.ui.P_Lip_FACS_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Lip_FACS_bar_ctrl'):
            self.ui.P_Lip_FACS_bar_Btn.setStyleSheet(self.white)
            self.ui.P_Lip_FACS_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Lip_FACS_L_bar_ctrl'):
            self.ui.P_Lip_FACS_L_bar_Btn.setStyleSheet(self.green)
            self.ui.P_Lip_FACS_L_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_L_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_L_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Lip_FACS_R_bar_ctrl'):
            self.ui.P_Lip_FACS_R_bar_Btn.setStyleSheet(self.blue)
            self.ui.P_Lip_FACS_R_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_R_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_R_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Lip_FACS_upper_bar_ctrl'):
            self.ui.P_Lip_FACS_upper_bar_Btn.setStyleSheet(self.yellow)
            self.ui.P_Lip_FACS_upper_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_upper_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_upper_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Lip_FACS_lower_bar_ctrl'):
            self.ui.P_Lip_FACS_lower_bar_Btn.setStyleSheet(self.yellow)
            self.ui.P_Lip_FACS_lower_bar_Btn.setEnabled(True)
        else:
            self.ui.P_Lip_FACS_lower_bar_Btn.setEnabled(False)
            self.ui.P_Lip_FACS_lower_bar_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + self.UPPER_TEETH_CONTROLLER_NAME):
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

        if cmds.objExists(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME):
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

        if cmds.objExists(self.prefix + 'Tongue_ctrl'):
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

        if cmds.objExists(self.prefix + 'Tongue_02_ctrl'):
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

        if cmds.objExists(self.prefix + 'Tongue_03_ctrl'):
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

        if cmds.objExists(self.prefix + 'Facial_Master_Ctrl'):
            self.ui.P_Facial_Master_Btn.setStyleSheet(self.magenta)
            self.ui.P_Facial_Master_Btn.setEnabled(True)
        else:
            self.ui.P_Facial_Master_Btn.setEnabled(False)
            self.ui.P_Facial_Master_Btn.setStyleSheet(None)

        if cmds.objExists(self.prefix + 'Facial_Set_Ctrl.Primary_Ctrl'):
            if self.ui.PrimaryCheckBox.isChecked() is True:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Primary_Ctrl', 1)
            else:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Primary_Ctrl', 0)
        if cmds.objExists(self.prefix + 'Facial_Set_Ctrl.Secondary_Ctrl'):
            if self.ui.SecondaryCheckBox.isChecked() is True:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Secondary_Ctrl', 1)
            else:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Secondary_Ctrl', 0)
        if cmds.objExists(self.prefix + 'Facial_Set_Ctrl.Master_Ctrl'):
            if self.ui.MasterCheckBox.isChecked() is True:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Master_Ctrl', 1)
            else:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Master_Ctrl', 0)
        if cmds.objExists(self.prefix + 'Facial_Set_Ctrl.FK_Ctrl'):
            if self.ui.FKCheckBox.isChecked() is True:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.FK_Ctrl', 1)
            else:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.FK_Ctrl', 0)
        if cmds.objExists(self.prefix + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl'):
            if self.ui.OralCavityCheckBox.isChecked() is True:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl', 1)
            else:
                cmds.setAttr(self.prefix + 'Facial_Set_Ctrl.Oral_Cavity_Ctrl', 0)
        print("_update_CV_command")
        return

    # brow command
    def _left_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_brow_ctrl')
            else:
                print('no existing object!!')
        print("_left_brow_command")

    def _left_brow_02_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_brow_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_brow_02_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_brow_02_ctrl')
            else:
                print('no existing object!!')
        print("_left_brow_02_command")

    def _left_brow_03_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_brow_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_brow_03_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_brow_03_ctrl')
            else:
                print('no existing object!!')
        print("_left_brow_03_command")

    def _left_medial_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_medial_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_medial_fibers_brow_ctrl')
            else:
                print('no existing object!!')
        print("_left_medial_fibers_brow_command")

    def _left_lateral_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lateral_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lateral_fibers_brow_ctrl')
            else:
                print('no existing object!!')
        print("_left_lateral_fibers_brow_command")

    def _left_procerus_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_procerus_brow_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_procerus_brow_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_procerus_brow_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_procerus_brow_command")

    def _right_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_brow_ctrl')
            else:
                print('no existing object!!')
        print("_right_brow_command")

    def _right_brow_02_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_brow_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_brow_02_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_brow_02_ctrl')
            else:
                print('no existing object!!')
        print("_right_brow_02_command")

    def _right_brow_03_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_brow_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_brow_03_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_brow_03_ctrl')
            else:
                print('no existing object!!')
        print("_right_brow_03_command")

    def _right_medial_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_medial_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_medial_fibers_brow_ctrl')
            else:
                print('no existing object!!')
        print("_right_medial_fibers_brow_command")

    def _right_lateral_fibers_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lateral_fibers_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lateral_fibers_brow_ctrl')
            else:
                print('no existing object!!')
        print("_right_lateral_fibers_brow_command")

    def _right_procerus_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_procerus_brow_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_procerus_brow_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_procerus_brow_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_procerus_brow_command")

    def _center_brow_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Center_brow_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Center_brow_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Center_brow_ctrl')
            else:
                print('no existing object!!')
        print("_center_brow_command")

    def _left_brow_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_brow_master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_brow_master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_brow_master_ctrl')
            else:
                print('no existing object!!')
        print("_left_brow_master_command")

    def _right_brow_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_brow_master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_brow_master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_brow_master_ctrl')
            else:
                print('no existing object!!')
        print("_right_brow_master_command")

    # eye command
    def _left_eye_blink_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_blink_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_blink_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_blink_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_blink_command")

    def _right_eye_blink_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_blink_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_blink_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_blink_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_blink_command")

    def _left_eye_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_lower_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_lower_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_lower_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_lower_command")

    def _right_eye_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_lower_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_lower_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_lower_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_lower_command")

    def _left_eye_lacrimal_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_lacrimal_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_lacrimal_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_lacrimal_command")

    def _left_eye_lacrimal_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_lacrimal_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_lacrimal_upper_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_lacrimal_upper_command")

    def _left_eye_lacrimal_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_lacrimal_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_lacrimal_lower_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_lacrimal_lower_command")

    def _left_eye_back_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_back_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_back_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_back_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_back_command")

    def _left_eye_back_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_back_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_back_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_back_upper_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_back_upper_command")

    def _left_eye_back_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_back_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_back_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_back_lower_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_back_lower_command")

    def _left_eye_double_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_double_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_double_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_double_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_double_command")

    def _right_eye_lacrimal_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_lacrimal_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_lacrimal_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_lacrimal_command")

    def _right_eye_lacrimal_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_lacrimal_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_lacrimal_upper_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_lacrimal_upper_command")

    def _right_eye_lacrimal_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_lacrimal_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_lacrimal_lower_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_lacrimal_lower_command")

    def _right_eye_back_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_back_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_back_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_back_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_back_command")

    def _right_eye_back_upper_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_back_upper_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_back_upper_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_back_upper_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_back_upper_command")

    def _right_eye_back_lower_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_back_lower_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_back_lower_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_back_lower_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_back_lower_command")

    def _right_eye_double_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_double_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_double_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_double_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_double_command")

    def _left_eye_target_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_target_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_eye_target_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_eye_target_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_target_command")

    def _right_eye_target_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_eye_target_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_eye_target_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_eye_target_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_target_command")

    def _eye_target_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Eye_target_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Eye_target_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Eye_target_Master_ctrl')
            else:
                print('no existing object!!')
        print("_eye_target_master_command")

    def _eye_world_point_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Eye_World_point_loc'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Eye_World_point_loc', tgl=True)
                else:
                    cmds.select(self.prefix + 'Eye_World_point_loc')
            else:
                print('no existing object!!')
        print("_eye_world_point_command")

    def _left_eye_world_point_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_Eye_World_point_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_Eye_World_point_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_Eye_World_point_ctrl')
            else:
                print('no existing object!!')
        print("_left_eye_world_point_command")

    def _right_eye_world_point_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_Eye_World_point_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_Eye_World_point_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_Eye_World_point_ctrl')
            else:
                print('no existing object!!')
        print("_right_eye_world_point_command")

    # nose command
    def _left_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_nose_ctrl')
            else:
                print('no existing object!!')
        print("_left_nose_command")

    def _left_nasalis_transverse_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_nasalis_transverse_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_nasalis_transverse_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_nasalis_transverse_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_nasalis_transverse_nose_command")

    def _left_procerus_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_procerus_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_procerus_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_procerus_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_procerus_nose_command")

    def _left_nasolabial_fold_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_nasolabial_fold_nose_command")

    def _right_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_nose_ctrl')
            else:
                print('no existing object!!')
        print("_right_nose_command")

    def _right_nasalis_transverse_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_nasalis_transverse_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_nasalis_transverse_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_nasalis_transverse_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_nasalis_transverse_nose_command")

    def _right_procerus_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_procerus_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_procerus_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_procerus_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_procerus_nose_command")

    def _right_nasolabial_fold_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_nasolabial_fold_nose_command")

    def _nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Nose_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Nose_ctrl')
            else:
                print('no existing object!!')
        print("_nose_command")

    def _lower_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lower_nose_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lower_nose_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lower_nose_ctrl')
            else:
                print('no existing object!!')
        print("_lower_nose_command")

    def _depressor_septi_nose_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'depressor_septi_nose_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'depressor_septi_nose_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'depressor_septi_nose_FK_ctrl')
            else:
                print('no existing object!!')
        print("_depressor_septi_nose_command")

    # cheek command
    def _left_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_left_cheek_command")

    def _right_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_right_cheek_command")

    def _left_upper_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_upper_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_upper_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_upper_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_left_upper_cheek_command")

    def _left_outer_orbicularis_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_outer_orbicularis_cheek_command")

    def _left_inner_orbicularis_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_inner_orbicularis_cheek_command")

    def _right_upper_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_upper_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_upper_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_upper_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_right_upper_cheek_command")

    def _right_outer_orbicularis_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_outer_orbicularis_cheek_command")

    def _right_inner_orbicularis_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_inner_orbicularis_cheek_command")

    def _left_lower_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lower_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lower_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_left_lower_cheek_command")

    def _right_lower_cheek_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lower_cheek_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lower_cheek_ctrl')
            else:
                print('no existing object!!')
        print("_right_lower_cheek_command")

    # lip command
    def _left_lower_liplid_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lower_liplid_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lower_liplid_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lower_liplid_ctrl')
            else:
                print('no existing object!!')
        print("_left_lower_liplid_command")

    def _right_lower_liplid_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lower_liplid_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lower_liplid_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lower_liplid_ctrl')
            else:
                print('no existing object!!')
        print("_right_lower_liplid_command")

    def _left_lip_corner_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_corner_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_corner_Ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_corner_command")

    def _right_lip_corner_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_corner_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_corner_Ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_corner_command")

    def _left_lip_corner_up_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_corner_up_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_corner_up_Ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_corner_up_command")

    def _left_lip_corner_up_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_up_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_corner_up_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_corner_up_FK_Ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_corner_up_FK_command")

    def _right_lip_corner_up_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_corner_up_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_corner_up_Ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_corner_up_command")

    def _right_lip_corner_up_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_corner_up_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_corner_up_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_corner_up_FK_Ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_corner_up_FK_command")

    def _left_lip_corner_down_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_corner_down_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_corner_down_Ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_corner_down_command")

    def _left_lip_corner_down_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_down_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_corner_down_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_corner_down_FK_Ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_corner_down_FK_command")

    def _right_lip_corner_down_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_corner_down_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_corner_down_Ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_corner_down_command")

    def _right_lip_corner_down_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_corner_down_FK_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_corner_down_FK_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_corner_down_FK_Ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_corner_down_FK_command")

    def _upper_lip_Master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Upper_lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Upper_lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Upper_lip_Master_ctrl')
            else:
                print('no existing object!!')
        print("_upper_lip_Master_command")

    def _lower_lip_Master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lower_lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lower_lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lower_lip_Master_ctrl')
            else:
                print('no existing object!!')
        print("_lower_lip_Master_command")

    def _upper_lip_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Upper_lip_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Upper_lip_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Upper_lip_ctrl')
            else:
                print('no existing object!!')
        print("_upper_lip_command")

    def _upper_lip_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Upper_lip_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Upper_lip_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Upper_lip_FK_ctrl')
            else:
                print('no existing object!!')
        print("_upper_lip_FK_command")

    def _lower_lip_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lower_lip_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lower_lip_ctrl')
            else:
                print('no existing object!!')
        print("_lower_lip_command")

    def _lower_lip_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lower_lip_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lower_lip_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lower_lip_FK_ctrl')
            else:
                print('no existing object!!')
        print("_lower_lip_FK_command")

    def _lower_lip_outer_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lower_lip_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lower_lip_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lower_lip_outer_ctrl')
            else:
                print('no existing object!!')
        print("_lower_lip_outer_command")

    def _left_lip_upper_side_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_upper_side_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_upper_side_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_upper_side_command")

    def _left_lip_upper_side_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_upper_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_upper_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_upper_side_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_upper_side_FK_command")

    def _left_lip_upper_side_02_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_upper_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_upper_side_02_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_upper_side_02_FK_command")

    def _left_lip_upper_outer_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_upper_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_upper_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_upper_outer_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_upper_outer_command")

    def _right_lip_upper_side_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_upper_side_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_upper_side_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_upper_side_command")

    def _right_lip_upper_side_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_upper_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_upper_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_upper_side_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_upper_side_FK_command")

    def _right_lip_upper_side_02_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_upper_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_upper_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_upper_side_02_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_upper_side_02_FK_command")

    def _right_lip_upper_outer_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_upper_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_upper_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_upper_outer_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_upper_outer_command")

    def _left_lip_lower_side_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_lower_side_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_lower_side_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_lower_side_command")

    def _left_lip_lower_side_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_lower_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_lower_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_lower_side_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_lower_side_FK_command")

    def _left_lip_lower_side_02_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_lower_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_lower_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_lower_side_02_FK_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_lower_side_02_FK_command")

    def _left_lip_lower_outer_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_lower_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'L_lip_lower_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'L_lip_lower_outer_ctrl')
            else:
                print('no existing object!!')
        print("_left_lip_lower_outer_command")

    def _right_lip_lower_side_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_lower_side_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_lower_side_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_lower_side_command")

    def _right_lip_lower_side_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_lower_side_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_lower_side_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_lower_side_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_lower_side_FK_command")

    def _right_lip_lower_side_02_FK_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_lower_side_02_FK_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_lower_side_02_FK_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_lower_side_02_FK_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_lower_side_02_FK_command")

    def _right_lip_lower_outer_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'R_lip_lower_outer_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'R_lip_lower_outer_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'R_lip_lower_outer_ctrl')
            else:
                print('no existing object!!')
        print("_right_lip_lower_outer_command")

    def _lip_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_Master_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_Master_ctrl')
            else:
                print('no existing object!!')
        print("_lip_master_command")

    def _lip_FACS_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_Ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_command")

    def _lip_FACS_bar_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_bar_ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_bar_command")

    def _lip_FACS_left_bar_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_L_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_L_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_L_bar_ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_left_bar_command")

    def _lip_FACS_right_bar_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_R_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_R_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_R_bar_ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_right_bar_command")

    def _lip_FACS_upper_bar_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_upper_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_upper_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_upper_bar_ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_upper_bar_command")

    def _lip_FACS_lower_bar_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_lower_bar_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Lip_FACS_lower_bar_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Lip_FACS_lower_bar_ctrl')
            else:
                print('no existing object!!')
        print("_lip_FACS_lower_bar_command")

    # jaw command
    def _jaw_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.JAW_MASTER_CONTROLLER_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + self.JAW_MASTER_CONTROLLER_NAME, tgl=True)
                else:
                    cmds.select(self.prefix + self.JAW_MASTER_CONTROLLER_NAME)
            else:
                print('no existing object!!')
        print("_jaw_master_command")

    # teeth command
    def _upper_teeth_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.UPPER_TEETH_CONTROLLER_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + self.UPPER_TEETH_CONTROLLER_NAME, tgl=True)
                else:
                    cmds.select(self.prefix + self.UPPER_TEETH_CONTROLLER_NAME)
            else:
                print('no existing object!!')
        print("_upper_teeth_command")

    def _lower_teeth_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME, tgl=True)
                else:
                    cmds.select(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME)
            else:
                print('no existing object!!')
        print("_lower_teeth_command")

    def _tongue_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Tongue_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Tongue_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Tongue_ctrl')
            else:
                print('no existing object!!')
        print("_tongue_command")

    def _tongue_02_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Tongue_02_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Tongue_02_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Tongue_02_ctrl')
            else:
                print('no existing object!!')
        print("_tongue_02_command")

    def _tongue_03_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Tongue_03_ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Tongue_03_ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Tongue_03_ctrl')
            else:
                print('no existing object!!')
        print("_tongue_03_command")

    def _facial_master_command(self, *args):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Facial_Master_Ctrl'):
                mods = cmds.getModifiers()
                if mods & 1 > 0 or mods & 4 > 0:
                    cmds.select(self.prefix + 'Facial_Master_Ctrl', tgl=True)
                else:
                    cmds.select(self.prefix + 'Facial_Master_Ctrl')
            else:
                print('no existing object!!')
        print("_facial_master_command")

    # controller transformをリセットする
    def _reset_joint_transform(self, joint_name):
        for attr in self.K_TRANSLATION_ROTATION_ATTR:
            attr_obj = joint_name + ".{}".format(attr)
            cmds.setAttr(self.prefix + attr_obj, 0)
        for attr in self.K_SCALE_ATTR:
            attr_obj = joint_name + ".{}".format(attr)
            cmds.setAttr(self.prefix + attr_obj, 1)
        print("_reset_joint_transform => {}".format(joint_name))
        pass

    def _lip_all_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Upper_lip_ctrl'):
                self._reset_joint_transform('Upper_lip_ctrl')
            if cmds.objExists(self.prefix + 'Upper_lip_FK_ctrl'):
                self._reset_joint_transform('Upper_lip_FK_ctrl')
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl'):
                self._reset_joint_transform('Lower_lip_ctrl')
            if cmds.objExists(self.prefix + 'Lower_lip_FK_ctrl'):
                self._reset_joint_transform('Lower_lip_FK_ctrl')
            if cmds.objExists(self.prefix + 'Lower_lip_outer_ctrl'):
                self._reset_joint_transform('Lower_lip_outer_ctrl')

            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl'):
                self._reset_joint_transform('L_lip_upper_side_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_upper_side_FK_ctrl'):
                self._reset_joint_transform('L_lip_upper_side_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl'):
                self._reset_joint_transform('L_lip_upper_side_02_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_upper_outer_ctrl'):
                self._reset_joint_transform('L_lip_upper_outer_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl'):
                self._reset_joint_transform('L_lip_lower_side_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_lower_side_FK_ctrl'):
                self._reset_joint_transform('L_lip_lower_side_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_lower_side_02_FK_ctrl'):
                self._reset_joint_transform('L_lip_lower_side_02_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_lip_lower_outer_ctrl'):
                self._reset_joint_transform('L_lip_lower_outer_ctrl')

            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl'):
                self._reset_joint_transform('R_lip_upper_side_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_upper_side_FK_ctrl'):
                self._reset_joint_transform('R_lip_upper_side_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_upper_side_02_FK_ctrl'):
                self._reset_joint_transform('R_lip_upper_side_02_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_upper_outer_ctrl'):
                self._reset_joint_transform('R_lip_upper_outer_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl'):
                self._reset_joint_transform('R_lip_lower_side_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_lower_side_FK_ctrl'):
                self._reset_joint_transform('R_lip_lower_side_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_lower_side_02_FK_ctrl'):
                self._reset_joint_transform('R_lip_lower_side_02_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_lip_lower_outer_ctrl'):
                self._reset_joint_transform('R_lip_lower_outer_ctrl')

            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl'):
                self._reset_joint_transform('L_lip_corner_up_Ctrl')
            if cmds.objExists(self.prefix + 'L_lip_corner_up_FK_Ctrl'):
                self._reset_joint_transform('L_lip_corner_up_FK_Ctrl')
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl'):
                self._reset_joint_transform('L_lip_corner_down_Ctrl')
            if cmds.objExists(self.prefix + 'L_lip_corner_down_FK_Ctrl'):
                self._reset_joint_transform('L_lip_corner_down_FK_Ctrl')
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl'):
                self._reset_joint_transform('L_lip_corner_Ctrl')
                if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl.Zip'):
                    cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Zip', 0)

            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl'):
                self._reset_joint_transform('R_lip_corner_up_Ctrl')
            if cmds.objExists(self.prefix + 'R_lip_corner_up_FK_Ctrl'):
                self._reset_joint_transform('R_lip_corner_up_FK_Ctrl')
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl'):
                self._reset_joint_transform('R_lip_corner_down_Ctrl')
            if cmds.objExists(self.prefix + 'R_lip_corner_down_FK_Ctrl'):
                self._reset_joint_transform('R_lip_corner_down_FK_Ctrl')
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl'):
                self._reset_joint_transform('R_lip_corner_Ctrl')
                if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl.Zip'):
                    cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Zip', 0)

            if cmds.objExists(self.prefix + 'Upper_lip_Master_ctrl'):
                self._reset_joint_transform('Upper_lip_Master_ctrl')
            if cmds.objExists(self.prefix + 'Lower_lip_Master_ctrl'):
                self._reset_joint_transform('Lower_lip_Master_ctrl')
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl'):
                self._reset_joint_transform('Lip_Master_ctrl')
            if cmds.objExists(self.prefix + self.JAW_MASTER_CONTROLLER_NAME):
                self._reset_joint_transform(self.JAW_MASTER_CONTROLLER_NAME)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl'):
                self._reset_joint_transform('Lip_FACS_Ctrl')
            if cmds.objExists(self.prefix + 'Lip_FACS_bar_ctrl'):
                self._reset_joint_transform('Lip_FACS_bar_ctrl')

            if cmds.objExists(self.prefix + 'Lip_FACS_L_bar_ctrl'):
                self._reset_joint_transform('Lip_FACS_L_bar_ctrl')
            if cmds.objExists(self.prefix + 'Lip_FACS_R_bar_ctrl'):
                self._reset_joint_transform('Lip_FACS_R_bar_ctrl')
            if cmds.objExists(self.prefix + 'Lip_FACS_upper_bar_ctrl'):
                self._reset_joint_transform('Lip_FACS_upper_bar_ctrl')
            if cmds.objExists(self.prefix + 'Lip_FACS_lower_bar_ctrl'):
                self._reset_joint_transform('Lip_FACS_lower_bar_ctrl')
        print("_lip_all_control_reset")

    def _lip_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl.Zip_val'):
                cmds.setAttr(self.prefix + 'Lip_Master_ctrl.Zip_val', 3)
            if cmds.objExists(self.prefix + 'Upper_lip_ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl'):
                cmds.setAttr(self.prefix + 'Upper_lip_ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'Upper_lip_ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'Upper_lip_ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl'):
                cmds.setAttr(self.prefix + 'Lower_lip_ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_side_02_FK_ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'Lower_lip_ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.lip_upper_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.lip_upper_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.lip_lower_side_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_side_02_FK_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.lip_lower_side_02_rotate_follow', 1)
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl') and cmds.objExists(self.prefix + 'Lower_lip_outer_ctrl'):
                cmds.setAttr(self.prefix + 'Lower_lip_ctrl.lip_lower_outer_follow', 0.3)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_outer_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'L_lip_upper_outer_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_outer_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_lower_side_ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'L_lip_lower_outer_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_outer_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'R_lip_upper_outer_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.lip_upper_outer_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_outer_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_lower_side_ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'R_lip_lower_outer_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.lip_lower_outer_follow', 1)
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'Lip_Master_ctrl.scale_val', 0.8)
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl.scale_min_val'):
                cmds.setAttr(self.prefix + 'Lip_Master_ctrl.scale_min_val', 0.4)
            if cmds.objExists(self.prefix + 'Lip_Master_ctrl.scale_max_val'):
                cmds.setAttr(self.prefix + 'Lip_Master_ctrl.scale_max_val', 1.3)
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'Lower_lip_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'Lower_lip_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'Lower_lip_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl.scale_val_02'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl.scale_val_02'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'L_lip_lower_side_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'L_lip_lower_side_ctrl.scale_val_02'):
                cmds.setAttr(self.prefix + 'L_lip_lower_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'R_lip_lower_side_ctrl.scale_val', 1)
            if cmds.objExists(self.prefix + 'R_lip_lower_side_ctrl.scale_val_02'):
                cmds.setAttr(self.prefix + 'R_lip_lower_side_ctrl.scale_val_02', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl.scale_val'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.scale_val', 1)
        print("_lip_connect_control_reset")

    def _lip_FACS_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Open_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Open_Follow', 1)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Up_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Up_Follow', 1)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Down_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Down_Follow', 1)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Side_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Side_Follow', 1)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Inside_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Inside_Follow', 1)
            if cmds.objExists(self.prefix + 'Lip_FACS_Ctrl.Outside_Follow'):
                cmds.setAttr(self.prefix + 'Lip_FACS_Ctrl.Outside_Follow', 1)
        print("_lip_FACS_control_reset")

    def _lip_nose_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'Upper_lip_ctrl') and cmds.objExists(self.prefix + 'Lower_nose_ctrl'):
                cmds.setAttr(self.prefix + 'Upper_lip_ctrl.Lower_Nose_follow', 0.5)
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'L_nose_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Nose_follow', 0.3)
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'R_nose_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Nose_follow', 0.3)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'L_nose_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.Nose_follow', 0.5)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'R_nose_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.Nose_follow', 0.5)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.nasolabial_fold', 1)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.nasolabial_fold', 1)
        print("_lip_nose_connect_control_reset")

    def _lip_cheek_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'L_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Cheek_follow', 0.6)
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Lower_Cheek_follow', 0.7)
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'L_upper_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Upper_Cheek_follow', 0.7)
            if cmds.objExists(self.prefix + 'L_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'L_lower_liplid_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_Ctrl.Liplid_follow', 0.5)
            if cmds.objExists(self.prefix + 'L_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'L_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_upper_side_ctrl.Cheek_follow', 0.5)
            if cmds.objExists(self.prefix + 'L_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_up_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.prefix + 'L_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'L_lower_liplid_ctrl'):
                cmds.setAttr(self.prefix + 'L_lip_corner_down_Ctrl.Liplid_follow', 0.3)
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'R_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Cheek_follow', 0.6)
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Lower_Cheek_follow', 0.7)
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'R_upper_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Upper_Cheek_follow', 0.7)
            if cmds.objExists(self.prefix + 'R_lip_corner_Ctrl') and cmds.objExists(self.prefix + 'R_lower_liplid_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_Ctrl.Liplid_follow', 0.5)
            if cmds.objExists(self.prefix + 'R_lip_upper_side_ctrl') and cmds.objExists(self.prefix + 'R_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_upper_side_ctrl.Cheek_follow', 0.5)
            if cmds.objExists(self.prefix + 'R_lip_corner_up_Ctrl') and cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_up_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.Lower_Cheek_follow', 0.3)
            if cmds.objExists(self.prefix + 'R_lip_corner_down_Ctrl') and cmds.objExists(self.prefix + 'R_lower_liplid_ctrl'):
                cmds.setAttr(self.prefix + 'R_lip_corner_down_Ctrl.Liplid_follow', 0.3)
        print("_lip_cheek_connect_control_reset")

    def _cheek_all_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_cheek_ctrl'):
                self._reset_joint_transform('L_cheek_ctrl')
            if cmds.objExists(self.prefix + 'L_lower_cheek_ctrl'):
                self._reset_joint_transform('L_lower_cheek_ctrl')
            if cmds.objExists(self.prefix + 'L_upper_cheek_ctrl'):
                self._reset_joint_transform('L_upper_cheek_ctrl')
            if cmds.objExists(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl'):
                self._reset_joint_transform('L_outer_orbicularis_cheek_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl'):
                self._reset_joint_transform('L_inner_orbicularis_cheek_FK_ctrl')
                cmds.setAttr(self.prefix + 'L_upper_cheek_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.prefix + 'L_lower_liplid_ctrl'):
                self._reset_joint_transform('L_lower_liplid_ctrl')

            if cmds.objExists(self.prefix + 'R_cheek_ctrl'):
                self._reset_joint_transform('R_cheek_ctrl')
            if cmds.objExists(self.prefix + 'R_lower_cheek_ctrl'):
                self._reset_joint_transform('R_lower_cheek_ctrl')
            if cmds.objExists(self.prefix + 'R_upper_cheek_ctrl'):
                self._reset_joint_transform('R_upper_cheek_ctrl')
            if cmds.objExists(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl'):
                self._reset_joint_transform('R_outer_orbicularis_cheek_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl'):
                self._reset_joint_transform('R_inner_orbicularis_cheek_FK_ctrl')
                cmds.setAttr(self.prefix + 'R_upper_cheek_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.prefix + 'R_lower_liplid_ctrl'):
                self._reset_joint_transform('R_lower_liplid_ctrl')
        print("_cheek_all_control_reset")

    def _cheek_eye_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_upper_cheek_ctrl') and cmds.objExists(self.prefix + 'L_eye_lower_ctrl'):
                cmds.setAttr(self.prefix + 'L_upper_cheek_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'R_upper_cheek_ctrl') and cmds.objExists(self.prefix + 'R_eye_lower_ctrl'):
                cmds.setAttr(self.prefix + 'R_upper_cheek_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'L_eye_lower_ctrl') and cmds.objExists(self.prefix + 'L_outer_orbicularis_cheek_FK_ctrl') and cmds.objExists(self.prefix + 'L_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.prefix + 'L_eye_lower_ctrl.Orbicularis_cheek_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_lower_ctrl') and cmds.objExists(self.prefix + 'R_outer_orbicularis_cheek_FK_ctrl') and cmds.objExists(self.prefix + 'R_inner_orbicularis_cheek_FK_ctrl'):
                cmds.setAttr(self.prefix + 'R_eye_lower_ctrl.Orbicularis_cheek_follow', 1)
        print("_cheek_eye_connect_control_reset")

    def _nose_all_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_nose_ctrl'):
                self._reset_joint_transform('L_nose_ctrl')
                if cmds.objExists(self.prefix + 'Nose_ctrl'):
                    cmds.setAttr(self.prefix + 'L_nose_ctrl.Center_Nose_follow', 0.2)
            if cmds.objExists(self.prefix + 'L_nasalis_transverse_nose_FK_ctrl'):
                self._reset_joint_transform('L_nasalis_transverse_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'L_nose_ctrl.nasalis_transverse_follow', 1)
            if cmds.objExists(self.prefix + 'L_procerus_nose_FK_ctrl'):
                self._reset_joint_transform('L_procerus_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'L_nose_ctrl.procerus_follow', 1)
            if cmds.objExists(self.prefix + 'L_nasolabial_fold_nose_FK_ctrl'):
                self._reset_joint_transform('L_nasolabial_fold_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'L_nose_ctrl.nasolabial_fold_follow', 2)

            if cmds.objExists(self.prefix + 'R_nose_ctrl'):
                self._reset_joint_transform('R_nose_ctrl')
                if cmds.objExists(self.prefix + 'Nose_ctrl'):
                    cmds.setAttr(self.prefix + 'R_nose_ctrl.Center_Nose_follow', 0.2)
            if cmds.objExists(self.prefix + 'R_nasalis_transverse_nose_FK_ctrl'):
                self._reset_joint_transform('R_nasalis_transverse_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'R_nose_ctrl.nasalis_transverse_follow', 1)
            if cmds.objExists(self.prefix + 'R_procerus_nose_FK_ctrl'):
                self._reset_joint_transform('R_procerus_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'R_nose_ctrl.procerus_follow', 1)
            if cmds.objExists(self.prefix + 'R_nasolabial_fold_nose_FK_ctrl'):
                self._reset_joint_transform('R_nasolabial_fold_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'R_nose_ctrl.nasolabial_fold_follow', 2)

            if cmds.objExists(self.prefix + 'Nose_ctrl'):
                self._reset_joint_transform('Nose_ctrl')
            if cmds.objExists(self.prefix + 'Lower_nose_ctrl'):
                self._reset_joint_transform('Lower_nose_ctrl')
            if cmds.objExists(self.prefix + 'depressor_septi_nose_FK_ctrl'):
                self._reset_joint_transform('depressor_septi_nose_FK_ctrl')
                cmds.setAttr(self.prefix + 'L_nose_ctrl.depressor_septi_follow', 1)
                cmds.setAttr(self.prefix + 'R_nose_ctrl.depressor_septi_follow', 1)
        print("_nose_all_control_reset")

    def _brow_all_control_reset(self):
        with UndoContext():
            # left brow
            if cmds.objExists(self.prefix + 'L_brow_ctrl'):
                self._reset_joint_transform('L_brow_ctrl')
                cmds.setAttr(self.prefix + 'L_brow_ctrl.Brow_02_follow', 1)
                if cmds.objExists(self.prefix + 'Center_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'L_brow_ctrl.Center_Brow_follow', 1)
                if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'L_brow_ctrl.medial_fibers_follow', 1)
            if cmds.objExists(self.prefix + 'L_brow_02_ctrl'):
                self._reset_joint_transform('L_brow_02_ctrl')
                cmds.setAttr(self.prefix + 'L_brow_02_ctrl.Brow_follow', 1)
                if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'L_brow_02_ctrl.lateral_fibers_follow', 1)
            if cmds.objExists(self.prefix + 'L_brow_03_ctrl'):
                self._reset_joint_transform('L_brow_03_ctrl')
                cmds.setAttr(self.prefix + 'L_brow_02_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.prefix + 'L_medial_fibers_brow_ctrl'):
                self._reset_joint_transform('L_medial_fibers_brow_ctrl')
                cmds.setAttr(self.prefix + 'L_medial_fibers_brow_ctrl.Brow_follow', 1)
                if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'L_medial_fibers_brow_ctrl.lateral_fibers_follow', 1)
                if cmds.objExists(self.prefix + 'L_procerus_brow_FK_ctrl'):
                    cmds.setAttr(self.prefix + 'L_medial_fibers_brow_ctrl.procerus_follow', 1)
            if cmds.objExists(self.prefix + 'L_lateral_fibers_brow_ctrl'):
                self._reset_joint_transform('L_lateral_fibers_brow_ctrl')
                cmds.setAttr(self.prefix + 'L_lateral_fibers_brow_ctrl.Brow_follow', 1)
                cmds.setAttr(self.prefix + 'L_lateral_fibers_brow_ctrl.Brow_02_follow', 1)
                cmds.setAttr(self.prefix + 'L_lateral_fibers_brow_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.prefix + 'L_procerus_brow_FK_ctrl'):
                self._reset_joint_transform('L_procerus_brow_FK_ctrl')

            # right brow
            if cmds.objExists(self.prefix + 'R_brow_ctrl'):
                self._reset_joint_transform('R_brow_ctrl')
                cmds.setAttr(self.prefix + 'R_brow_ctrl.Brow_02_follow', 1)
                if cmds.objExists(self.prefix + 'Center_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'R_brow_ctrl.Center_Brow_follow', 1)
                if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'R_brow_ctrl.medial_fibers_follow', 1)
            if cmds.objExists(self.prefix + 'R_brow_02_ctrl'):
                self._reset_joint_transform('R_brow_02_ctrl')
                cmds.setAttr(self.prefix + 'R_brow_02_ctrl.Brow_follow', 1)
                if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'R_brow_02_ctrl.lateral_fibers_follow', 1)
            if cmds.objExists(self.prefix + 'R_brow_03_ctrl'):
                self._reset_joint_transform('R_brow_03_ctrl')
                cmds.setAttr(self.prefix + 'R_brow_02_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.prefix + 'R_medial_fibers_brow_ctrl'):
                self._reset_joint_transform('R_medial_fibers_brow_ctrl')
                cmds.setAttr(self.prefix + 'R_medial_fibers_brow_ctrl.Brow_follow', 1)
                if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl'):
                    cmds.setAttr(self.prefix + 'R_medial_fibers_brow_ctrl.lateral_fibers_follow', 1)
                if cmds.objExists(self.prefix + 'R_procerus_brow_FK_ctrl'):
                    cmds.setAttr(self.prefix + 'R_medial_fibers_brow_ctrl.procerus_follow', 1)
            if cmds.objExists(self.prefix + 'R_lateral_fibers_brow_ctrl'):
                self._reset_joint_transform('R_lateral_fibers_brow_ctrl')
                cmds.setAttr(self.prefix + 'R_lateral_fibers_brow_ctrl.Brow_follow', 1)
                cmds.setAttr(self.prefix + 'R_lateral_fibers_brow_ctrl.Brow_02_follow', 1)
                cmds.setAttr(self.prefix + 'R_lateral_fibers_brow_ctrl.Brow_03_follow', 1)
            if cmds.objExists(self.prefix + 'R_procerus_brow_FK_ctrl'):
                self._reset_joint_transform('R_procerus_brow_FK_ctrl')

            # brow other
            if cmds.objExists(self.prefix + 'Center_brow_ctrl'):
                self._reset_joint_transform('Center_brow_ctrl')
            if cmds.objExists(self.prefix + 'L_brow_master_ctrl'):
                self._reset_joint_transform('L_brow_master_ctrl')
                cmds.setAttr(self.prefix + 'L_brow_master_ctrl.Brow_02_follow', 1)
            if cmds.objExists(self.prefix + 'R_brow_master_ctrl'):
                self._reset_joint_transform('R_brow_master_ctrl')
                cmds.setAttr(self.prefix + 'R_brow_master_ctrl.Brow_02_follow', 1)
            if cmds.objExists(self.prefix + 'R_brow_master_ctrl') and cmds.objExists(self.prefix + 'L_brow_03_ctrl'):
                cmds.setAttr(self.prefix + 'L_brow_master_ctrl.Brow_03_follow', 1)
                cmds.setAttr(self.prefix + 'R_brow_master_ctrl.Brow_03_follow', 1)
        print("_brow_all_control_reset")

    def _eye_all_control_reset(self):
        with UndoContext():
            # left eye
            if cmds.objExists(self.prefix + 'L_eye_blink_ctrl'):
                self._reset_joint_transform('L_eye_blink_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_lower_ctrl'):
                self._reset_joint_transform('L_eye_lower_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_lower_ctrl.lower_FK_follow'):
                cmds.setAttr(self.prefix + 'L_eye_lower_ctrl.lower_FK_follow', 1)
            if cmds.objExists(self.prefix + 'L_eye_lower_ctrl.side_shrink_follow'):
                cmds.setAttr(self.prefix + 'L_eye_lower_ctrl.side_shrink_follow', 1)
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_ctrl'):
                self._reset_joint_transform('L_eye_lacrimal_ctrl')
                cmds.setAttr(self.prefix + 'L_eye_lacrimal_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.prefix + 'L_eye_lacrimal_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_upper_FK_ctrl'):
                self._reset_joint_transform('L_eye_lacrimal_upper_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_lacrimal_lower_FK_ctrl'):
                self._reset_joint_transform('L_eye_lacrimal_lower_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_back_ctrl'):
                self._reset_joint_transform('L_eye_back_ctrl')
                cmds.setAttr(self.prefix + 'L_eye_back_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.prefix + 'L_eye_back_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'L_eye_back_upper_FK_ctrl'):
                self._reset_joint_transform('L_eye_back_upper_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_back_lower_FK_ctrl'):
                self._reset_joint_transform('L_eye_back_lower_FK_ctrl')
            if cmds.objExists(self.prefix + 'L_eye_double_ctrl'):
                self._reset_joint_transform('L_eye_double_ctrl')
                cmds.setAttr(self.prefix + 'L_eye_blink_ctrl.Up_Eye_Double_follow', 1)
                cmds.setAttr(self.prefix + 'L_eye_blink_ctrl.Down_Eye_Double_follow', 1)

            # right eye
            if cmds.objExists(self.prefix + 'R_eye_blink_ctrl'):
                self._reset_joint_transform('R_eye_blink_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_lower_ctrl'):
                self._reset_joint_transform('R_eye_lower_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_lower_ctrl.lower_FK_follow'):
                cmds.setAttr(self.prefix + 'R_eye_lower_ctrl.lower_FK_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_lower_ctrl.side_shrink_follow'):
                cmds.setAttr(self.prefix + 'R_eye_lower_ctrl.side_shrink_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_ctrl'):
                self._reset_joint_transform('R_eye_lacrimal_ctrl')
                cmds.setAttr(self.prefix + 'R_eye_lacrimal_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.prefix + 'R_eye_lacrimal_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_upper_FK_ctrl'):
                self._reset_joint_transform('R_eye_lacrimal_upper_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_lacrimal_lower_FK_ctrl'):
                self._reset_joint_transform('R_eye_lacrimal_lower_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_back_ctrl'):
                self._reset_joint_transform('R_eye_back_ctrl')
                cmds.setAttr(self.prefix + 'R_eye_back_ctrl.Eye_Blink_follow', 1)
                cmds.setAttr(self.prefix + 'R_eye_back_ctrl.Eye_Lower_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_back_upper_FK_ctrl'):
                self._reset_joint_transform('R_eye_back_upper_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_back_lower_FK_ctrl'):
                self._reset_joint_transform('R_eye_back_lower_FK_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_double_ctrl'):
                self._reset_joint_transform('R_eye_double_ctrl')
                cmds.setAttr(self.prefix + 'R_eye_blink_ctrl.Up_Eye_Double_follow', 1)
                cmds.setAttr(self.prefix + 'R_eye_blink_ctrl.Down_Eye_Double_follow', 1)
        print("_eye_all_control_reset")

    def _eye_brow_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_blink_ctrl') and cmds.objExists(self.prefix + 'L_brow_master_ctrl'):
                cmds.setAttr(self.prefix + 'L_eye_blink_ctrl.Up_Brow_Master_follow', 0.5)
                cmds.setAttr(self.prefix + 'L_eye_blink_ctrl.Down_Brow_Master_follow', 0.3)
            if cmds.objExists(self.prefix + 'R_eye_blink_ctrl') and cmds.objExists(self.prefix + 'R_brow_master_ctrl'):
                cmds.setAttr(self.prefix + 'R_eye_blink_ctrl.Up_Brow_Master_follow', 0.5)
                cmds.setAttr(self.prefix + 'R_eye_blink_ctrl.Down_Brow_Master_follow', 0.3)
            if cmds.objExists(self.prefix + 'L_eye_double_ctrl') and cmds.objExists(self.prefix + 'L_brow_02_ctrl'):
                cmds.setAttr(self.prefix + 'L_brow_02_ctrl.Eye_Double_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_double_ctrl') and cmds.objExists(self.prefix + 'R_brow_02_ctrl'):
                cmds.setAttr(self.prefix + 'R_brow_02_ctrl.Eye_Double_follow', 1)
        print("_eye_brow_connect_control_reset")

    def _eye_target_all_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_target_ctrl'):
                self._reset_joint_transform('L_eye_target_ctrl')
            if cmds.objExists(self.prefix + 'R_eye_target_ctrl'):
                self._reset_joint_transform('R_eye_target_ctrl')
            if cmds.objExists(self.prefix + 'Eye_target_Master_ctrl'):
                self._reset_joint_transform('Eye_target_Master_ctrl')

            if cmds.objExists(self.prefix + 'Eye_World_point_loc'):
                for attr in self.K_TRANSLATION_ROTATION_ATTR:
                    attr_obj = "Eye_World_point_loc" + ".{}".format(attr)
                    cmds.setAttr(self.prefix + attr_obj, 0)
                cmds.setAttr(self.prefix + 'Eye_target_Master_ctrl.Target_World', 0)
            if cmds.objExists(self.prefix + 'L_Eye_World_point_ctrl'):
                for attr in self.K_TRANSLATION_ROTATION_ATTR:
                    attr_obj = "L_Eye_World_point_ctrl" + ".{}".format(attr)
                    cmds.setAttr(self.prefix + attr_obj, 0)
            if cmds.objExists(self.prefix + 'R_Eye_World_point_ctrl'):
                for attr in self.K_TRANSLATION_ROTATION_ATTR:
                    attr_obj = "R_Eye_World_point_ctrl" + ".{}".format(attr)
                    cmds.setAttr(self.prefix + attr_obj, 0)
        print("_eye_target_all_control_reset")

    def _eye_target_eye_connect_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + 'L_eye_target_ctrl') and cmds.objExists(self.prefix + 'L_eye_blink_ctrl'):
                cmds.setAttr(self.prefix + 'L_eye_target_ctrl.Blink', 0)
                cmds.setAttr(self.prefix + 'L_eye_target_ctrl.Eyelid_up_follow', 0.4)
            if cmds.objExists(self.prefix + 'R_eye_target_ctrl') and cmds.objExists(self.prefix + 'R_eye_blink_ctrl'):
                cmds.setAttr(self.prefix + 'R_eye_target_ctrl.Blink', 0)
                cmds.setAttr(self.prefix + 'R_eye_target_ctrl.Eyelid_up_follow', 0.4)
            if cmds.objExists(self.prefix + 'L_eye_target_ctrl') and cmds.objExists(self.prefix + 'L_eye_lower_ctrl'):
                cmds.setAttr(self.prefix + 'L_eye_target_ctrl.Blink_Side', 0)
                cmds.setAttr(self.prefix + 'L_eye_target_ctrl.Eyelid_down_follow', 0.4)
                cmds.setAttr(self.prefix + 'L_eye_target_ctrl.Eyelid_side_follow', 1)
            if cmds.objExists(self.prefix + 'R_eye_target_ctrl') and cmds.objExists(self.prefix + 'R_eye_lower_ctrl'):
                cmds.setAttr(self.prefix + 'R_eye_target_ctrl.Blink_Side', 0)
                cmds.setAttr(self.prefix + 'R_eye_target_ctrl.Eyelid_down_follow', 0.4)
                cmds.setAttr(self.prefix + 'R_eye_target_ctrl.Eyelid_side_follow', 1)
        print("_eye_target_eye_connect_control_reset")

    def _oral_cavity_all_control_reset(self):
        with UndoContext():
            if cmds.objExists(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME):
                self._reset_joint_transform(self.LOWER_TEETH_CONTROLLER_NAME)
            if cmds.objExists(self.prefix + self.UPPER_TEETH_CONTROLLER_NAME):
                self._reset_joint_transform(self.UPPER_TEETH_CONTROLLER_NAME)
            if cmds.objExists(self.prefix + 'Tongue_ctrl'):
                self._reset_joint_transform('Tongue_ctrl')
            if cmds.objExists(self.prefix + 'Tongue_02_ctrl'):
                self._reset_joint_transform('Tongue_02_ctrl')
            if cmds.objExists(self.prefix + 'Tongue_03_ctrl'):
                self._reset_joint_transform('Tongue_03_ctrl')

            if cmds.objExists(self.prefix + self.JAW_MASTER_CONTROLLER_NAME) and cmds.objExists(self.prefix + 'Tongue_ctrl'):
                cmds.setAttr(self.prefix + '{}.Tongue_follow'.format(self.JAW_MASTER_CONTROLLER_NAME), 1)
            if cmds.objExists(self.prefix + self.JAW_MASTER_CONTROLLER_NAME) and cmds.objExists(self.prefix + self.LOWER_TEETH_CONTROLLER_NAME):
                cmds.setAttr(self.prefix + '{}.Lower_Teeth_follow'.format(self.JAW_MASTER_CONTROLLER_NAME), 1)
        print("_oral_cavity_all_control_reset")

if __name__ == '__main__':
    Facial_Picker_window.main()


