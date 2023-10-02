# -*- coding: utf-8 -*-

"""
supported version MAYA 2019, 2020, 2022
Auther : Shunji_Nagasawa
"""

from collections import OrderedDict
import os
import sys
import json
import maya.mel as mel
import pymel.core as pm
import maya.cmds as cmds
from functools import partial
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtCore import *
import time

def maya_main_window():

    main_window = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window), QtWidgets.QDialog)
    else:
        return wrapInstance(long(main_window), QtWidgets.QDialog) # type: ignore


class RetargetingTool(QtWidgets.QDialog):

    WINDOW_TITLE = "Animation Retarget"
    PROJECT_PATH = "json/Projects/"
    IMPORT_NS = "RTG"
    MODULE_VERSION = "1.0.3"

    SOURCE_TRANSFORM_ATTRIBUTE = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]

    def __init__(self, parent=None, *args, **kwargs):
        super(RetargetingTool, self).__init__(maya_main_window())

        self.refresh_button = None
        self.simple_conn_button = None
        self.ik_conn_button = None
        self.bake_button = None
        self.batch_bake_button = None
        self.rot_checkbox = None
        self.pos_checkbox = None
        #self.mo_checkbox = None
        self.snap_checkbox = None
        self.connection_layout = None

        # start --------------------- Automation
        self.project_names = []
        self.auto_connection_button = None

        self.source_model_text_name = None
        self.source_model_text = None
        self.source_joints = []
        self.target_model_text_name = None
        self.target_model_text = None
        self.target_joints = []

        # prefix
        self.source_reference_prefix = None
        self.target_reference_prefix = None
        # end

        # start ------------------- reset pose
        self.reset_initial_pose_button = None
        #end

        self.custom_import_button = None

        # start ------------------- initial pose
        self.copy_initial_pose_button = None
        self.controller_data = []
        #end

        file_path = cmds.file(q=True, sn=True)
        file_name = os.path.basename(file_path)
        raw_name, extension = os.path.splitext(file_name)
        self.scene_name = raw_name
        print("Here is the name of the file that is currently open => {0}".format(self.scene_name))

        self.script_job_ids = []
        self.connection_ui_widgets = []
        self.color_counter = 0
        self.setStyleSheet('background-color:#262f38;')
        self.maya_color_index = OrderedDict([(13, "red"), (18, "cyan"), (14, "lime"), (17, "yellow")])
        self.cached_connect_nodes = []
        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 520)
        self.create_ui_widgets()
        self.create_ui_layout()
        self._create_ui_connections()
        self._create_script_jobs()

    def create_ui_widgets(self):
        self.refresh_button = QtWidgets.QPushButton(QtGui.QIcon(":refresh.png"), "")
        self.simple_conn_button = QtWidgets.QPushButton("Create Connection")
        self.ik_conn_button = QtWidgets.QPushButton("Create IK Connection")

        # automation retarget function
        self.auto_connection_button = QtWidgets.QPushButton("Create Auto Connect")
        self.auto_connection_button.setStyleSheet("background-color: #34d8ed; color: black")

        # reset pose function
        self.copy_initial_pose_button = QtWidgets.QPushButton("Copy Init Pose (Experimental)")
        self.copy_initial_pose_button.setStyleSheet("background-color: #c4221a; color: white")
        self.reset_initial_pose_button = QtWidgets.QPushButton("Reset Pose")
        self.reset_initial_pose_button.setStyleSheet("background-color: #34d8ed; color: black")

        self.custom_import_button = QtWidgets.QPushButton("Import With NS")
        self.custom_import_button.setStyleSheet("background-color: #34d8ed; color: black")

        # bake animation function
        self.bake_button = QtWidgets.QPushButton("Bake Animation")
        self.bake_button.setStyleSheet("background-color: lightgreen; color: black")
        #self.batch_bake_button = QtWidgets.QPushButton("Batch Bake And Export ...")

        self.rot_checkbox = QtWidgets.QCheckBox("Rotation")
        self.pos_checkbox = QtWidgets.QCheckBox("Translation")
        self.snap_checkbox = QtWidgets.QCheckBox("Align To Position")

    def create_ui_layout(self):
        horizontal_layout_checkbox = QtWidgets.QHBoxLayout()
        horizontal_layout_checkbox.addWidget(self.pos_checkbox)
        horizontal_layout_checkbox.addWidget(self.rot_checkbox)
        horizontal_layout_checkbox.addWidget(self.snap_checkbox)
        horizontal_layout_checkbox.addStretch()

        dir_name = os.path.dirname(__file__)
        file_name = os.path.join(dir_name, 'json/Project.json')
        with open(file_name) as f:
            data = json.load(f)
            for name in data['name']:
                self.project_names.append(name)

        X = 200
        Y = 40
        # select source model
        horizontal_layout_1 = QtWidgets.QHBoxLayout()
        source_menu_list = QtWidgets.QMenu(self)
        for item in self.project_names:
            select_action = QtWidgets.QAction(item, self)
            select_action.triggered.connect(partial(self._apply_source_model_name, item))
            source_menu_list.addAction(select_action)
        source_menu_button = QtWidgets.QPushButton("Source", self)
        source_menu_button.setMenu(source_menu_list)
        self.source_model_text = QtWidgets.QTextEdit(self)
        self.source_model_text.setReadOnly(True)
        self.source_model_text.setFixedSize(X, Y)
        horizontal_layout_1.addWidget(source_menu_button)
        horizontal_layout_1.addWidget(self.source_model_text)

        # select target model
        horizontal_layout_1_1 = QtWidgets.QHBoxLayout()
        target_menu_list = QtWidgets.QMenu(self)
        for item in self.project_names:
            select_action = QtWidgets.QAction(item, self)
            select_action.triggered.connect(partial(self._apply_target_model_name, item))
            target_menu_list.addAction(select_action)
        target_menu_button = QtWidgets.QPushButton("Target", self)
        target_menu_button.setMenu(target_menu_list)
        self.target_model_text = QtWidgets.QTextEdit(self)
        self.target_model_text.setReadOnly(True)
        self.target_model_text.setFixedSize(X, Y)
        horizontal_layout_1_1.addWidget(target_menu_button)
        horizontal_layout_1_1.addWidget(self.target_model_text)

        # button layout
        horizontal_layout_2 = QtWidgets.QHBoxLayout()
        horizontal_layout_2.addWidget(self.simple_conn_button)
        horizontal_layout_2.addWidget(self.ik_conn_button)

        # automation layout
        horizontal_layout_3 = QtWidgets.QHBoxLayout()
        horizontal_layout_3.addWidget(self.reset_initial_pose_button)
        horizontal_layout_3.addWidget(self.auto_connection_button)

        # copy pose layout
        horizontal_layout_4 = QtWidgets.QHBoxLayout()
        horizontal_layout_4.addWidget(self.custom_import_button)

        # custom import and more..
        horizontal_layout_5 = QtWidgets.QHBoxLayout()
        horizontal_layout_5.addWidget(self.bake_button)

        # main layout
        connection_list_widget = QtWidgets.QWidget()
        self.connection_layout = QtWidgets.QVBoxLayout(connection_list_widget)
        self.connection_layout.setContentsMargins(2, 2, 2, 2)
        self.connection_layout.setSpacing(3)
        self.connection_layout.setAlignment(QtCore.Qt.AlignTop)
        list_scroll_area = QtWidgets.QScrollArea()
        list_scroll_area.setWidgetResizable(True)
        list_scroll_area.setWidget(connection_list_widget)

        separator_line_1 = QtWidgets.QFrame(parent=None)
        separator_line_1.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_1_1 = QtWidgets.QFrame(parent=None)
        separator_line_1_1.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_1_1.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_2 = QtWidgets.QFrame(parent=None)
        separator_line_2.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_3 = QtWidgets.QFrame(parent=None)
        separator_line_3.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_4 = QtWidgets.QFrame(parent=None)
        separator_line_4.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_5 = QtWidgets.QFrame(parent=None)
        separator_line_5.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        separator_line_6 = QtWidgets.QFrame(parent=None)
        separator_line_6.setFrameShape(QtWidgets.QFrame.HLine)
        separator_line_6.setFrameShadow(QtWidgets.QFrame.Sunken)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addWidget(list_scroll_area)
        main_layout.addLayout(horizontal_layout_checkbox)
        main_layout.addWidget(separator_line_1)
        main_layout.addLayout(horizontal_layout_1)
        main_layout.addWidget(separator_line_1_1)
        main_layout.addLayout(horizontal_layout_1_1)
        main_layout.addWidget(separator_line_2)
        main_layout.addLayout(horizontal_layout_2)
        main_layout.addWidget(separator_line_3)
        main_layout.addLayout(horizontal_layout_3)
        main_layout.addWidget(separator_line_4)
        main_layout.addLayout(horizontal_layout_4)
        main_layout.addWidget(separator_line_5)
        main_layout.addLayout(horizontal_layout_5)

    def _create_ui_connections(self):
        self.simple_conn_button.clicked.connect(self.create_connection_node)
        self.ik_conn_button.clicked.connect(self.create_ik_connection_node)
        self.refresh_button.clicked.connect(self.refresh_ui_list)
        self.bake_button.clicked.connect(self.bake_animation_confirm)
        #self.batch_bake_button.clicked.connect(self.open_batch_window)

        self.auto_connection_button.clicked.connect(self.automation_create_connection_node)
        self.copy_initial_pose_button.clicked.connect(self._copy_initial_pose_function)
        self.reset_initial_pose_button.clicked.connect(self._reset_pose_function)

        self.custom_import_button.clicked.connect(self._handle_import)
        self.rot_checkbox.setChecked(True)
        self.pos_checkbox.setChecked(True)
        self.snap_checkbox.setChecked(False)

    def _apply_source_model_name(self, project_name):
        if self.source_model_text_name is not None:
            self.source_model_text.clear()
        self.source_model_text_name = project_name
        self.source_model_text.append("Selected Source : " + self.source_model_text_name)

    def _apply_target_model_name(self, project_name):
        if self.target_model_text_name is not None:
            self.target_model_text.clear()
        self.target_model_text_name = project_name
        self.target_model_text.append("Selected Target : " + self.target_model_text_name)

    def _create_script_jobs(self):
        self.script_job_ids.append(cmds.scriptJob(event=["SelectionChanged", partial(self.refresh_ui_list)]))
        self.script_job_ids.append(cmds.scriptJob(event=["NameChanged", partial(self.refresh_ui_list)]))

    def kill_script_jobs(self):
        for job_id in self.script_job_ids:
            if cmds.scriptJob(exists=job_id):
                cmds.scriptJob(kill=job_id)
            else:
                pass

    def refresh_ui_list(self):
        self.clear_list()
        connect_nodes_in_scene = RetargetingTool.get_connect_nodes()
        self.cached_connect_nodes = connect_nodes_in_scene
        for node in connect_nodes_in_scene:
            connection_ui_item = ListItemWidget(parent_instance=self, connection_node=node)
            self.connection_layout.addWidget(connection_ui_item)
            self.connection_ui_widgets.append(connection_ui_item)


    def clear_list(self):
        self.connection_ui_widgets = []
        while self.connection_layout.count() > 0:
            connection_ui_item = self.connection_layout.takeAt(0)
            if connection_ui_item.widget():
                connection_ui_item.widget().deleteLater()


    def showEvent(self, event):
        self.refresh_ui_list()


    def closeEvent(self, event):
        self.kill_script_jobs()
        self.clear_list()

    def _handle_import(self):
        self._fbx_import_to_namespace(ns=self.IMPORT_NS)

    def _get_target_group_root(self):
        if self.target_model_text_name == "YY36":
            return "AllRig_GRP"
        elif self.target_model_text_name == "X21" or self.target_model_text_name == "X22":
            return "Group"
        return None

    # Import処理
    # 自動でnamespaceを付与
    def _fbx_import_to_namespace(self, ns='target_namespace'):
        current_namespace = cmds.namespaceInfo(cur=True)
        if not cmds.namespace(ex=':%s' % ns):
            cmds.namespace(add=':%s' % ns)
        cmds.namespace(set=':%s' % ns)

        path_list = cmds.fileDialog2(fm=1, ds=2, ff=('FBX(*.fbx)'))
        if not path_list:
            return
        mel.eval('FBXImportSetLockedAttribute -v false')
        cmds.file(path_list[0], i=True, gr=True, mergeNamespacesOnClash=True, namespace=current_namespace, importTimeRange = "override")
        print("import path => {0}".format(path_list[0]))
        cmds.namespace(set=current_namespace)

        cmds.currentUnit(time='60fps')
        fps = mel.eval('currentTimeUnitToFPS')
        print(fps)

    # TODO
    # This function is under development and not available !!
    def _copy_initial_pose_function(self):
        cmds.warning("This function is under development and not available !!")
        pass

    def _copy_transform(self, source, target):
        print("copy transform. source => {0}, target => {1}".format(source, target))
        for attr in self.SOURCE_TRANSFORM_ATTRIBUTE:
            lock_check = cmds.getAttr(target + "." + attr, lock=True)
            if lock_check is False:
                attribute_value = cmds.getAttr(source + "." + attr)
                # cmds.setAttr(target + "." + attr, attribute_value)
                print("set pose {0}, value {1}".format(target + "." + attr, attribute_value))
            else:
                print("can't modify lock attribute => {0}".format(target + "." + attr))

    # Restore Pose to pre-edit state.
    def _reset_pose_function(self):
        if len(self.target_joints) <= 0:
            self._find_target_curves()

        for source in self.target_joints:
            # poseの初期値にresetする
            for attr in self.SOURCE_TRANSFORM_ATTRIBUTE:
                lock_check = cmds.getAttr(source + "." + attr, lock=True)
                if lock_check is False:
                    if attr in ["sx", "sy", "sz"]:
                        continue
                    cmds.setAttr(source + "." + attr, 0)
                    #print("reset attribute {0}".format(target + "." + attr))
                else:
                    print("can't modify lock attribute => {0}".format(source + "." + attr))

    # Retrieve the retarget original joint
    def _find_source_joints(self):
        self.source_joints = []
        self.source_reference_prefix = None
        cmds.select(self.IMPORT_NS + ":group")
        joints = cmds.ls(selection=True, dag=True, type="joint")

        for joint in joints:
            # 編集可能にする
            for attr in self.SOURCE_TRANSFORM_ATTRIBUTE:
                lock_check = cmds.getAttr(joint + "." + attr, lock=True)
                if lock_check is True:
                    cmds.setAttr(joint, lock=0)

            # @MEMO
            # 文字列を一文字ずる書き出しprefixを調べる
            # 例　RTG:NC003_Rig_Final:root => RTG:NC003_Rig_Final:
            if self.source_reference_prefix is None:
                """
                string_array = []
                for str in list(joint):
                    if str == ":":
                        break
                    string_array.append(str)
                self.source_reference_prefix = "".join(string_array)
                """
                names = joint.split(":")
                length = len(names) - 1
                name= ""
                for idx in range(length):
                    name += names[idx] + ":"
                self.source_reference_prefix = name
                print("source_reference_prefix => {0}".format(self.source_reference_prefix))

            # json dataを基にmappingを行う
            source_joint_data = self._get_project_json_data(self.source_model_text_name)
            source_joints = source_joint_data['joint']
            for key, value in source_joints.items():
                #real_joint_name = self.source_reference_prefix + ":" + value
                real_joint_name = self.source_reference_prefix + value
                if real_joint_name == joint:
                    self.source_joints.append(joint)
                    print("added joint => {0}".format(joint))
        print("found joint count => {0}".format(len(self.source_joints)))

    # Retrieve the nurbs curve of the retarget destination
    def _find_target_curves(self):
        self.target_joints = []
        self.target_reference_prefix = None
        root_object = self._get_target_group_root()
        if root_object:
            cmds.select("*:" + root_object)
        curves = cmds.ls(selection=True, dag=True, type="transform")
        for curve in curves:
            if cmds.nodeType(curve) == "transform" :
                # @MEMO
                # 文字列を一文字ずる書き出しprefixを調べる
                # 例　XXX_P001_Rig_20220905:Group => XXX_P001_Rig_20220905
                if self.target_reference_prefix is None:
                    """
                    string_array = []
                    for str in list(curve):
                        if str == ":":
                            break
                        string_array.append(str)
                    self.target_reference_prefix = "".join(string_array)
                    """
                    names = curve.split(":")
                    length = len(names) - 1
                    name = ""
                    for idx in range(length):
                        name += names[idx] + ":"
                    self.target_reference_prefix = name
                    print("target_reference_prefix => {0}".format(self.target_reference_prefix))

                target_joint_data = self._get_project_json_data(self.target_model_text_name)
                target_curves = target_joint_data['ctrl']
                for key, value in target_curves.items():
                    real_curve_name = self.target_reference_prefix + value
                    if real_curve_name == curve:
                        self.target_joints.append(curve)
                        print("added curve => {0}".format(curve))

                """
                has_fk = curve.find("FK") > -1 or curve.find("fk") > -1
                has_ik = curve.find("IK") > -1 or curve.find("ik") > -1
                if has_fk or has_ik:
                    self.target_joints.append(curve)
                """

        """
        for source in self.target_joints:
            for attr in self.SOURCE_TRANSFORM_ATTRIBUTE:
                attribute_value = cmds.getAttr(source + "." + attr)
                print("cur pose {0}, value {1}".format(source + "." + attr, attribute_value))
        """
        print("found object count => {0}".format(len(self.target_joints)))


    def _get_animated_attributes(self, node):
        keyable_attributes = cmds.listAttr(node, keyable=True)
        animated_attributes = []
        if not keyable_attributes:
            return animated_attributes
        for attr in keyable_attributes:
            isTL = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTL')
            isTA = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTA')
            isTU = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTU')
            isTT = cmds.listConnections('%s.%s' % (node, attr), type='animCurveTT')
            if isTL is not None or isTA is not None or isTU is not None or isTT is not None:
                animated_attributes.append(attr)
        return animated_attributes


    def _get_project_json_data(self, path_name):
        dir_name = os.path.dirname(__file__)
        file_name = os.path.join(dir_name, self.PROJECT_PATH + path_name + '.json')
        with open(file_name) as f:
            return json.load(f)


    # Calculate BoneMapping load json file
    def _get_bone_mapping_dict(self):
        if len(self.source_joints) <= 0 or len(self.target_joints) <= 0:
            #cmds.warning("source joints is empty or target joints is empty !")
            cmds.confirmDialog(title='Failed', message='source joints is empty or target joints is empty !', button=['Ok'], defaultButton='Ok')
            return

        source_joint_data = self._get_project_json_data(self.source_model_text_name)
        target_joint_data = self._get_project_json_data(self.target_model_text_name)
        source_joints = source_joint_data['joint']
        target_joints = target_joint_data['joint']
        source_curves = source_joint_data['ctrl']
        target_curves = target_joint_data['ctrl']

        # TODO
        # Retarget先のjsonファイルを読み込み、Bone Mappingを行う。
        # 1. source元のmappingを作成
        # 2. keyを元にtargetのjointを検索
        # 3. source dictのvalueをkeyにしvalueをtargetのjointにmapping
        # 4. reference rigの場合は文字が含まれているか確認
        source_dict = {}
        for key, value in source_joints.items():
            for source in self.source_joints:
                # remove prefix import group
                # RTG:NC003_Rig_Final:pelvis => pelvis
                names = source.split(":")
                length = len(names) - 1
                source_name = names[length]
                joint_name = source_name
                if joint_name == value:
                    source_dict[key] = source

        retarget_dict = {}
        for key, value in source_dict.items():
            # jsonにjoint名とctrl名が両方ある
            if key in source_joints and key in target_curves:
                target = self._find_curve_object(target_curves[key])
                if target is not None:
                    retarget_dict[value] = target
                else:
                    print("target is None => {0}".format(target_curves[key]))
            else:
                print("json data doesn't have this key => {0}".format(key))

        for key, value in retarget_dict.items():
            print("retarget_dict => {0} : {1}".format(key, value))
        return retarget_dict

    def _load_joint_and_control(self):
        pass

    def automation_create_connection_node(self):
        self._find_source_joints()
        self._find_target_curves()
        if self.target_reference_prefix is None:
            cmds.warning("Mapping cannot be performed . information in the reference file could not be obtained. !")
            return
        retarget_dict = self._get_bone_mapping_dict()
        self._automation_create_connection_node(retarget_dict)

    def _find_curve_object(self, curve_name):
        real_joint_name = self.target_reference_prefix + curve_name
        for source in self.target_joints:
            if source == real_joint_name:
                return source
        return None

    def _automation_create_connection_node(self, joint_dict):
        # key => joint_name
        # value => controller_name
        for key, value in joint_dict.items():
            try:
                has_fk = value.find("FK") > -1
                has_ik = value.find("IK") > -1
                """
                if has_fk:
                    self._create_connection_node(key, value)
                """
                if has_ik:
                    self._create_ik_connection_node(key, value)
                else:
                    self._create_connection_node(key, value)
                    pass
            except:
                pass

    def create_connection_node(self):
        try:
            selected_joint = cmds.ls(sl=True)[0]
            selected_ctrl = cmds.ls(sl=True)[1]
            self._create_connection_node(selected_joint, selected_ctrl)
        except:
            cmds.warning("create_connection_node No selections!")
            cmds.confirmDialog(title='Warning', message='create_connection_node No selections!', button=['Ok'], defaultButton='Ok')

    def create_ik_connection_node(self):
        try:
            selected_joint = cmds.ls(selection=True)[0]
            selected_ctrl = cmds.ls(selection=True)[1]
            self._create_ik_connection_node(selected_joint, selected_ctrl)
        except:
            cmds.warning("create_ik_connection_node No selections!")
            cmds.confirmDialog(title='Warning', message='create_ik_connection_node No selections!', button=['Ok'], defaultButton='Ok')

    def _create_connection_node(self, selected_joint, selected_ctrl):
        print("source => {0}, target => {1}".format(selected_joint, selected_ctrl))
        if self.snap_checkbox.isChecked() is True:
            cmds.matchTransform(selected_ctrl, selected_joint, pos=True)
        else:
            pass
        if self.rot_checkbox.isChecked() is True and self.pos_checkbox.isChecked() is False:
            suffix = "_ROT"
        elif self.pos_checkbox.isChecked() is True and self.rot_checkbox.isChecked() is False:
            suffix = "_TRAN"
        else:
            suffix = "_TRAN_ROT"

        try:
            # Add message attr
            locator = self._create_control_sphere(selected_ctrl + suffix)
            cmds.addAttr(locator, longName="ConnectNode", attributeType="message")

            # attributeがあった場合は削除
            if cmds.attributeQuery("ConnectedCtrl", node=selected_ctrl, exists=True):
                cmds.deleteAttr("ConnectedCtrl", node=selected_ctrl)
                print("Delete ConnectedCtrl since it already exists.")
            else:
                pass

            cmds.addAttr(selected_ctrl, longName="ConnectedCtrl", attributeType="message")
            cmds.connectAttr(locator + ".ConnectNode", selected_ctrl + ".ConnectedCtrl")
            cmds.parent(locator, selected_joint)

            position = cmds.xform(selected_joint, q=True, t=True, ws=True)
            print("position => {0}".format(position))

            cmds.xform(locator, rotation=(0, 0, 0))
            cmds.xform(locator, translation=(0, 0, 0))

            # uiのチェックボックスに基づいて制約のタイプを選択する
            if self.rot_checkbox.isChecked() is True and self.pos_checkbox.isChecked() is True:
                cmds.parentConstraint(locator, selected_ctrl, maintainOffset=True)
            elif self.rot_checkbox.isChecked() is True and self.pos_checkbox.isChecked() is False:
                cmds.orientConstraint(locator, selected_ctrl, maintainOffset=True)
            elif self.pos_checkbox.isChecked() is True and self.rot_checkbox.isChecked() is False:
                cmds.pointConstraint(locator, selected_ctrl, maintainOffset=True)
            else:
                cmds.warning("Select translation and/or rotation!")
                cmds.delete(locator)
                cmds.deleteAttr(selected_ctrl, at="ConnectedCtrl")
            self.refresh_ui_list()
        except:
            pass

    def _create_ik_connection_node(self, selected_joint, selected_ctrl):
        self.rot_checkbox.setChecked(True)
        self.pos_checkbox.setChecked(True)

        if self.snap_checkbox.isChecked() is True:
            cmds.matchTransform(selected_ctrl, selected_joint, pos=True)
        else:
            pass

        try:
            tran_locator = self._create_control_sphere(selected_ctrl + "_TRAN")
            cmds.parent(tran_locator, selected_joint)
            cmds.xform(tran_locator, rotation=(0, 0, 0))
            cmds.xform(tran_locator, translation=(0, 0, 0))
            rot_locator = self._create_control_locator(selected_ctrl + "_ROT")
            # メッセージ属性を追加し、それらを接続する
            cmds.addAttr(tran_locator, longName="ConnectNode", attributeType="message")
            cmds.addAttr(rot_locator, longName="ConnectNode", attributeType="message")
            cmds.addAttr(selected_ctrl, longName="ConnectedCtrl", attributeType="message")
            cmds.connectAttr(tran_locator + ".ConnectNode", selected_ctrl + ".ConnectedCtrl")
            cmds.parent(rot_locator, tran_locator)
            cmds.xform(rot_locator, rotation=(0, 0, 0))
            cmds.xform(rot_locator, translation=(0, 0, 0))
            joint_parent = cmds.listRelatives(selected_joint, parent=True)[0]
            cmds.parent(tran_locator, joint_parent)
            cmds.makeIdentity(tran_locator, apply=True, translate=True)
            cmds.orientConstraint(selected_joint, tran_locator, maintainOffset=False)
            cmds.parentConstraint(rot_locator, selected_ctrl, maintainOffset=True)
            # Lock and hide attributes
            cmds.setAttr(rot_locator + ".tx", lock=True, keyable=False)
            cmds.setAttr(rot_locator + ".ty", lock=True, keyable=False)
            cmds.setAttr(rot_locator + ".tz", lock=True, keyable=False)
            cmds.setAttr(tran_locator + ".rx", lock=True, keyable=False)
            cmds.setAttr(tran_locator + ".ry", lock=True, keyable=False)
            cmds.setAttr(tran_locator + ".rz", lock=True, keyable=False)
            self.refresh_ui_list()
        except:
            pass

    def _scale_control_shape(self, controller, size):
        cmds.select(self.get_curves(controller), replace=True)
        cmds.scale(size, size, size)
        cmds.select(clear=True)

    def get_curves(self, object):
        children = cmds.listRelatives(object, type="shape", children=True)
        ctrl_vertices = []
        for c in children:
            spans = int(cmds.getAttr(c + ".spans")) + 1
            vertices = "{shape}.cv[0:{count}]".format(shape=c, count=spans)
            ctrl_vertices.append(vertices)
        return ctrl_vertices

    def _create_control_locator(self, ctrl_shape_name):
        curves = []
        curves.append(cmds.curve(degree=1, p=[(0, 0, 1), (0, 0, -1)], k=[0, 1]))
        curves.append(cmds.curve(degree=1, p=[(1, 0, 0), (-1, 0, 0)], k=[0, 1]))
        curves.append(cmds.curve(degree=1, p=[(0, 1, 0), (0, -1, 0)], k=[0, 1]))

        locator = self.combine_shapes(curves, ctrl_shape_name)
        cmds.setAttr(locator + ".overrideEnabled", 1)
        cmds.setAttr(locator + ".overrideColor", list(self.maya_color_index.keys())[self.color_counter])
        return locator

    def _create_control_sphere(self, ctrl_shape_name):
        circles = []
        for n in range(0, 5):
            circles.append(cmds.circle(normal=(0, 0, 0), center=(0, 0, 0))[0])

        cmds.rotate(0, 45, 0, circles[0])
        cmds.rotate(0, -45, 0, circles[1])
        cmds.rotate(0, -90, 0, circles[2])
        cmds.rotate(90, 0, 0, circles[3])
        sphere = self.combine_shapes(circles, ctrl_shape_name)
        cmds.setAttr(sphere + ".overrideEnabled", 1)
        cmds.setAttr(sphere + ".overrideColor", list(self.maya_color_index.keys())[self.color_counter])
        #self._scale_control_shape(sphere, 0.5)
        self._scale_control_shape(sphere, 1)
        return sphere

    def combine_shapes(self, shapes, ctrl_shape_name):
        shape_nodes = cmds.listRelatives(shapes, shapes=True)
        output_node = cmds.group(empty=True, name=ctrl_shape_name)
        cmds.makeIdentity(shapes, apply=True, translate=True, rotate=True, scale=True)
        cmds.parent(shape_nodes, output_node, shape=True, relative=True)
        cmds.delete(shape_nodes, constructionHistory=True)
        cmds.delete(shapes)
        return output_node

    def bake_animation_confirm(self):
        confirm = cmds.confirmDialog(title="Confirm",
                                     message="Animation Bake will delete all connected nodes. Do you want to continue?",
                                     button=["Yes", "No"], defaultButton="Yes", cancelButton="No")
        if confirm == "Yes":
            progress_dialog = QtWidgets.QProgressDialog("Bake animation", None, 0, -1, self)
            progress_dialog.setWindowFlags(progress_dialog.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
            progress_dialog.setWindowFlags(progress_dialog.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
            progress_dialog.setWindowTitle("Progress...")
            progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
            progress_dialog.show()
            QtCore.QCoreApplication.processEvents()
            # Bake animation

            # constraintを削除する
            # undo処理を監視
            self.bake_animation()
            cmds.undo()

            progress_dialog.close()
        if confirm == "No":
            pass
        self.refresh_ui_list()

    def open_batch_window(self):
        try:
            self.settings_window.close()
            self.settings_window.deleteLater()
        except:
            pass
        self.settings_window = BatchExport()
        self.settings_window.show()

    @classmethod
    def bake_animation(cls):
        if len(cls.get_connected_ctrls()) == 0:
            cmds.warning("No connections found in scene!")
        if len(cls.get_connected_ctrls()) != 0:
            time_min = cmds.playbackOptions(query=True, min=True)
            time_max = cmds.playbackOptions(query=True, max=True)

            # Bake the animation
            cmds.refresh(suspend=True)
            cmds.bakeResults(cls.get_connected_ctrls(), t=(time_min, time_max), sb=1, at=["rx", "ry", "rz", "tx", "ty", "tz"], hi="none")
            cmds.refresh(suspend=False)

            # Delete the connect nodes
            for node in cls.get_connect_nodes():
                try:
                    print("delete connect node")
                    cmds.delete(node)
                except:
                    pass

            # Remove the message attribute from the controllers
            for ctrl in cls.get_connected_ctrls():
                try:
                    print("delete connect controller")
                    cmds.deleteAttr(ctrl, attribute="ConnectedCtrl")
                except:
                    pass
            pass

    @classmethod
    def get_connect_nodes(cls):
        connect_nodes_in_scene = []
        for i in cmds.ls():
            if cmds.attributeQuery("ConnectNode", node=i, exists=True) is True:
                connect_nodes_in_scene.append(i)
            else:
                pass
        return connect_nodes_in_scene

    @classmethod
    def get_connected_ctrls(cls):
        connected_ctrls_in_scene = []
        for i in cmds.ls():
            if cmds.attributeQuery("ConnectedCtrl", node=i, exists=True) is True:
                connected_ctrls_in_scene.append(i)
            else:
                pass
        return connected_ctrls_in_scene


class InitialCtrlData:
    # TODO
    # this class delete later
    def __init__(self, source_name):
        self.controller_name = source_name
        self.tx = cmds.getAttr(source_name + ".tx")
        self.ty = cmds.getAttr(source_name + ".ty")
        self.tz = cmds.getAttr(source_name + ".tz")
        self.rx = cmds.getAttr(source_name + ".rx")
        self.ry = cmds.getAttr(source_name + ".ry")
        self.rz = cmds.getAttr(source_name + ".rz")
        self.sx = cmds.getAttr(source_name + ".sx")
        self.sy = cmds.getAttr(source_name + ".sy")
        self.sz = cmds.getAttr(source_name + ".sz")
        print("cache transform {0}".format(self.controller_name))

    def reset_pose(self):
        if self.controller_name is not None:
            cmds.setAttr( self.controller_name + ".tx", self.tx)
            cmds.setAttr( self.controller_name + ".ty", self.ty)
            cmds.setAttr( self.controller_name + ".tz", self.tz)
            cmds.setAttr( self.controller_name + ".rx", self.rz)
            cmds.setAttr( self.controller_name + ".ry", self.ry)
            cmds.setAttr( self.controller_name + ".rz", self.rz)
            cmds.setAttr( self.controller_name + ".sx", self.sx)
            cmds.setAttr( self.controller_name + ".sy", self.sy)
            cmds.setAttr( self.controller_name + ".sz", self.sz)

class ListItemWidget(QtWidgets.QWidget):
    """
    UI list item class.
    新しいリスト・アイテムが作成されると、それはRetargetingToolクラスのconnection_list_widgetに追加されます。
    """

    def __init__(self, connection_node, parent_instance):
        super(ListItemWidget, self).__init__()
        self.connection_node = connection_node
        self.main = parent_instance

        self.color_button = None
        self.sel_button = None
        self.del_button = None
        self.transform_name_label = None

        self.setFixedHeight(26)
        self.create_ui_widgets()
        self.create_ui_layout()
        self.create_ui_connections()

        # If there is already connection nodes in the scene update the color counter
        try:
            current_override = cmds.getAttr(self.connection_node + ".overrideColor")
            self.main.color_counter = self.main.maya_color_index.keys().index(current_override)
        except:
            pass

    def create_ui_widgets(self):
        self.color_button = QtWidgets.QPushButton()
        self.color_button.setFixedSize(20, 20)
        self.color_button.setStyleSheet("background-color:" + self.get_current_color())

        self.sel_button = QtWidgets.QPushButton()
        self.sel_button.setStyleSheet("background-color: #707070")
        self.sel_button.setText("Select")
        self.sel_button.setFixedWidth(80)

        self.del_button = QtWidgets.QPushButton()
        self.del_button.setStyleSheet("background-color: #707070")
        self.del_button.setText("Delete")
        self.del_button.setFixedWidth(80)

        self.transform_name_label = QtWidgets.QLabel(self.connection_node)
        self.transform_name_label.setAlignment(QtCore.Qt.AlignCenter)
        self.transform_name_label.setStyleSheet("color: darkgray")
        for selected in cmds.ls(selection=True):
            if selected == self.connection_node:
                self.transform_name_label.setStyleSheet("color: white")

    def create_ui_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(5, 5, 20, 0)
        main_layout.addWidget(self.color_button)
        main_layout.addWidget(self.transform_name_label)
        main_layout.addWidget(self.sel_button)
        main_layout.addWidget(self.del_button)

    def create_ui_connections(self):
        self.sel_button.clicked.connect(self.select_connection_node)
        self.del_button.clicked.connect(self.delete_connection_node)
        self.color_button.clicked.connect(self.set_color)

    def select_connection_node(self):
        cmds.select(self.connection_node)
        for widget in self.main.connection_ui_widgets:
            widget.transform_name_label.setStyleSheet("color: darkgray")
        self.transform_name_label.setStyleSheet("color: white")

    def delete_connection_node(self):
        try:
            for attr in cmds.listConnections(self.connection_node, destination=True):
                if cmds.attributeQuery("ConnectedCtrl", node=attr, exists=True):
                    cmds.deleteAttr(attr, at="ConnectedCtrl")
        except:
            pass

        cmds.delete(self.connection_node)
        self.main.refresh_ui_list()

    def set_color(self):
        # Set the color on the connection node and button
        connection_nodes = self.main.cached_connect_nodes
        color = list(self.main.maya_color_index.keys())
        length = len(self.main.maya_color_index)
        if self.main.color_counter >= length - 1:
            self.main.color_counter = 0
        else:
            self.main.color_counter += 1

        for node in connection_nodes:
            cmds.setAttr(node + ".overrideEnabled", 1)
            cmds.setAttr(node + ".overrideColor", color[self.main.color_counter])

        for widget in self.main.connection_ui_widgets:
            widget.color_button.setStyleSheet("background-color:" + self.get_current_color())

    def get_current_color(self):
        current_color_index = cmds.getAttr(self.connection_node + ".overrideColor")
        color_name = self.main.maya_color_index.get(current_color_index, "grey")
        return color_name

class BatchExport(QtWidgets.QDialog):
    """
    Batch exporter class
    """
    WINDOW_TITLE = "Batch Exporter"

    def __init__(self):
        super(BatchExport, self).__init__(maya_main_window())
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(400, 250)
        self.animation_clip_paths = []
        self.output_folder = ""

        self.file_list_widget = None
        self.remove_selected_button = None
        self.load_anim_button = None
        self.export_button = None

        self.connection_file_line = None
        self.connection_filepath_button = None
        self.export_selected_label = None
        self.export_selected_line = None
        self.export_selected_button = None
        self.output_filepath_button = None
        self.file_type_combo = None

        self.create_ui()
        self.create_connections()

    def create_ui(self):
        self.file_list_widget = QtWidgets.QListWidget()
        self.remove_selected_button = QtWidgets.QPushButton("Remove Selected")
        self.remove_selected_button.setFixedHeight(24)
        self.load_anim_button = QtWidgets.QPushButton("Load Animations")
        self.load_anim_button.setFixedHeight(24)
        self.export_button = QtWidgets.QPushButton("Batch Export Animations")
        self.export_button.setStyleSheet("background-color: lightgreen; color: black")
        self.connection_file_line = QtWidgets.QLineEdit()
        # 接続リグファイルのファイルパスを入力します。
        self.connection_file_line.setToolTip("Enter the file path of the connection rig file.")
        self.connection_filepath_button = QtWidgets.QPushButton()
        self.connection_filepath_button.setIcon(QtGui.QIcon(":fileOpen.png"))
        self.connection_filepath_button.setFixedSize(24, 24)

        self.export_selected_label = QtWidgets.QLabel("Export Selected (Optional):")
        self.export_selected_line = QtWidgets.QLineEdit()
        # エクスポートするノードの名前を入力します。すべてエクスポートする場合は空白のままにします。
        self.export_selected_line.setToolTip("Enter the name of the node to be exported. Leave blank if you want to export all.")
        self.export_selected_button = QtWidgets.QPushButton()
        self.export_selected_button.setIcon(QtGui.QIcon(":addClip.png"))
        self.export_selected_button.setFixedSize(24, 24)

        self.output_filepath_button = QtWidgets.QPushButton()
        self.output_filepath_button.setIcon(QtGui.QIcon(":fileOpen.png"))

        self.file_type_combo = QtWidgets.QComboBox()
        self.file_type_combo.addItems([".fbx", ".ma"])

        horizontal_layout_1 = QtWidgets.QHBoxLayout()
        horizontal_layout_1.addWidget(QtWidgets.QLabel("Connection Rig File:"))
        horizontal_layout_1.addWidget(self.connection_file_line)
        horizontal_layout_1.addWidget(self.connection_filepath_button)

        horizontal_layout_2 = QtWidgets.QHBoxLayout()
        horizontal_layout_2.addWidget(self.load_anim_button)
        horizontal_layout_2.addWidget(self.remove_selected_button)

        horizontal_layout_3 = QtWidgets.QHBoxLayout()
        horizontal_layout_3.addWidget(QtWidgets.QLabel("Output File Type:"))
        horizontal_layout_3.addWidget(self.file_type_combo)
        horizontal_layout_3.addWidget(self.export_button)

        horizontal_layout_4 = QtWidgets.QHBoxLayout()
        horizontal_layout_4.addWidget(self.export_selected_label)
        horizontal_layout_4.addWidget(self.export_selected_line)
        horizontal_layout_4.addWidget(self.export_selected_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.file_list_widget)
        main_layout.addLayout(horizontal_layout_2)
        main_layout.addLayout(horizontal_layout_1)
        main_layout.addLayout(horizontal_layout_4)
        main_layout.addLayout(horizontal_layout_3)

    def create_connections(self):
        self.connection_filepath_button.clicked.connect(self.connection_filepath_dialog)
        self.load_anim_button.clicked.connect(self.animation_filepath_dialog)
        self.export_button.clicked.connect(self.batch_action)
        self.export_selected_button.clicked.connect(self.add_selected_action)
        self.remove_selected_button.clicked.connect(self.remove_selected_item)

    def connection_filepath_dialog(self):
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select Connection Rig File", "", "Maya ACSII (*.ma);;All files (*.*)")
        if file_path[0]:
            self.connection_file_line.setText(file_path[0])

    def output_filepath_dialog(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select export folder path", "")
        if folder_path:
            self.output_folder = folder_path
            return True
        else:
            return False

    def animation_filepath_dialog(self):
        file_paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select Animation Clips", "", "FBX (*.fbx);;All files (*.*)")
        file_path_list = file_paths[0]

        if file_path_list[0]:
            for i in file_path_list:
                self.file_list_widget.addItem(i)

        for i in range(0, self.file_list_widget.count()):
            self.file_list_widget.item(i).setTextColor(QtGui.QColor("white"))

    def add_selected_action(self):
        selection = cmds.ls(selection=True)
        text_string = ""
        if len(selection) > 1:
            text_string = "["
            for i in selection:
                text_string += '"{}", '.format(i)
            text_string = text_string[:-2]
            text_string += "]"
        elif selection[0]:
            text_string = "{}".format(selection[0])
        else:
            pass

        self.export_selected_line.setText(text_string)

    def remove_selected_item(self):
        try:
            selected_items = self.file_list_widget.selectedItems()
            for item in selected_items:
                self.file_list_widget.takeItem(self.file_list_widget.row(item))
        except:
            pass

    def batch_action(self):
        if self.connection_file_line.text() == "":
            # 接続ファイルのテキストフィールドが空です。エクスポートできるように、接続リグファイルを追加します。このファイルには、リグとスケルトンへの接続が含まれている必要があります。
            cmds.warning("The text field in the connection file is empty. Add a connection rig file so that it can be exported. This file must contain the connections to the rig and skeleton.")
        elif self.file_list_widget.count() == 0:
            # アニメーションクリップのリストが空です。エクスポートできるようにアニメーションクリップをリストに追加してください！
            cmds.warning("The list of animation clips is empty. Please add animation clips to the list so that they can be exported!")
        else:
            confirm_dialog = self.output_filepath_dialog()
            if confirm_dialog is True:
                self.bake_export()
            else:
                pass

    def bake_export(self):
        self.animation_clip_paths = []
        for i in range(self.file_list_widget.count()):
            self.animation_clip_paths.append(self.file_list_widget.item(i).text())

        number_of_operations = len(self.animation_clip_paths) * 3
        current_operation = 0
        progress_dialog = QtWidgets.QProgressDialog("Preparing", "Cancel", 0, number_of_operations, self)
        progress_dialog.setWindowFlags(progress_dialog.windowFlags() ^ QtCore.Qt.WindowCloseButtonHint)
        progress_dialog.setWindowFlags(progress_dialog.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        progress_dialog.setValue(0)
        progress_dialog.setWindowTitle("Progress...")
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.show()
        QtCore.QCoreApplication.processEvents()
        export_result = []

        for i, path in enumerate(self.animation_clip_paths):
            # Import connection file and animation clip
            progress_dialog.setLabelText("Baking and exporting {} of {}".format(i + 1, len(self.animation_clip_paths)))
            self.file_list_widget.item(i).setTextColor(QtGui.QColor("yellow"))
            cmds.file(new=True, force=True)
            cmds.file(self.connection_file_line.text(), open=True)
            mel.eval('FBXImportMode -v "exmerge";')
            mel.eval('FBXImport -file "{}";'.format(path))
            current_operation += 1
            progress_dialog.setValue(current_operation)

            # Bake animation
            RetargetingTool.bake_animation()
            current_operation += 1
            progress_dialog.setValue(current_operation)

            # Export animation
            output_path = self.output_folder + "/" + os.path.splitext(os.path.basename(path))[0]
            if self.file_type_combo.currentText() == ".fbx":
                output_path += ".fbx"
                cmds.file(rename=output_path)
                if self.export_selected_line.text() != "":
                    cmds.select(self.export_selected_line.text(), replace=True)
                    mel.eval('FBXExport -f "{}" -s'.format(output_path))
                else:
                    mel.eval('FBXExport -f "{}"'.format(output_path))
            elif self.file_type_combo.currentText() == ".ma":
                output_path += ".ma"
                cmds.file(rename=output_path)
                if self.export_selected_line.text() != "":
                    cmds.select(self.export_selected_line.text(), replace=True)
                    cmds.file(exportSelected=True, type="mayaAscii")
                else:
                    cmds.file(exportAll=True, type="mayaAscii")

            current_operation += 1
            progress_dialog.setValue(current_operation)

            if os.path.exists(output_path):
                self.file_list_widget.item(i).setTextColor(QtGui.QColor("lime"))
                export_result.append("Sucessfully exported: " + output_path)

            else:
                self.file_list_widget.item(i).setTextColor(QtGui.QColor("red"))
                export_result.append("Failed exporting: " + output_path)

        print("------")
        for i in export_result:
            print(i)
        print("------")

        progress_dialog.setValue(number_of_operations)
        progress_dialog.close()

def show_main_window():
    global retarget_tool_ui
    try:
        retarget_tool_ui.close()
        retarget_tool_ui.deleteLater()
    except:
        pass
    retarget_tool_ui = RetargetingTool()
    retarget_tool_ui.show()


