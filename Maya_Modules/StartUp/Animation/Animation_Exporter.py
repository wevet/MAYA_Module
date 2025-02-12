# -*- coding: utf-8 -*-

import sys
import os
from PySide2.QtWidgets import QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QSpinBox, QFileDialog, QDialog, QCheckBox, QListWidget, QListWidgetItem, QGridLayout, QHBoxLayout, QMessageBox
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from functools import partial
import maya.mel as mel
import logging
import subprocess
import Animation_Util as Util

import importlib
importlib.reload(Util)


logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QMainWindow)

g_is_strip_name_space = True

class AnimationExporter:
    def __init__(self, characters, filename, directory, start_frame, end_frame,
                 bake_keyframes=True, joints=None, controllers=None, prefix=None, multiple_export=False):
        """
        :param characters: List of character names to export
        :param filename: Base filename for exported files
        :param directory: Directory to export files to
        :param start_frame: Start frame for export
        :param end_frame: End frame for export
        :param bake_keyframes: Whether to bake keyframes for Animator export
        :param joints: List of joint nodes to be exported
        :param controllers: List of animation controller nodes (e.g., nurbs curves)
        :param prefix namespace prefix
        :param multiple_export animation export many files
        """
        self.characters = characters
        self.filename = filename
        self.directory = directory
        self.start_frame = int(start_frame)
        self.end_frame = int(end_frame)
        self.bake_keyframes = bake_keyframes
        self.joints = joints or []  # Default to empty list if None
        self.controllers = controllers or []  # Default to empty list if None
        self.prefix = prefix or None
        self.multiple_export = multiple_export
        self.original_names = {}  # To store original names for restoring

        self.K_PRESET_FILE_NAME = "C:/Program Files/Autodesk/Maya2023/plug-ins/fbx/plug-ins/FBX/Presets/export/L5LT1.fbxexportpreset"


    @staticmethod
    def get_related_joints(meshes):
        """
        選択されたメッシュに影響を与えているジョイントを取得
        """
        local_joints = set()
        for mesh in meshes:
            skin_cluster = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
            if skin_cluster:
                influences = cmds.skinCluster(skin_cluster[0], query=True, influence=True)
                local_joints.update(influences)
        return list(local_joints)


    @staticmethod
    def get_bake_attributes(objects):
        result = []
        if not objects:
            raise ValueError("No objects specified")
        connections = cmds.listConnections(
            objects,
            plugs=True,
            source=True,
            connections=True,
            destination=False
        ) or []

        for dst_obj, src_obj in zip(connections[::2], connections[1::2]):
            nodeType = cmds.nodeType(src_obj)
            if not nodeType.startswith("animCurve"):
                result.append(dst_obj)
        return result


    def _bake_animation(self, objects):

        bake_attributes = self.get_bake_attributes(objects)
        if not bake_attributes:
            print("No attributes found to bake!")
            return

        #print(f"Baking attributes: {bake_attributes}")

        if bake_attributes:
            cmds.bakeResults(
                bake_attributes,
                time=(self.start_frame, self.end_frame),
                shape=True,
                simulation=True,
                sampleBy=1,
                controlPoints=False,
                minimizeRotation=True,
                bakeOnOverrideLayer=False,
                preserveOutsideKeys=True, # ベイク時に範囲外のキーを削除しない
                sparseAnimCurveBake=False,
                disableImplicitControl=True,
                removeBakedAttributeFromLayer=False)
        else:
            print("Cannot find any connection to bake!")


    def _export_fbx(self, file_path):
        """
        Set up FBX export options.
        """
        encoded_path = file_path.replace("\\", "/")

        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            print("modify FileDialogStyle")

        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        # reset export
        mel.eval('FBXResetExport')
        # Enable skeleton definitions and skin export
        mel.eval('FBXExportSkeletonDefinitions -v 1')
        mel.eval('FBXExportSkins -v 1')
        if self.bake_keyframes:
            mel.eval('FBXExportAnimationOnly -v 0;')
            mel.eval('FBXExportBakeComplexAnimation -v 1;')
            mel.eval('FBXExportSkeletonDefinitions -v 1;')
        else:
            mel.eval('FBXExportBakeComplexAnimation -v 0')
            mel.eval('FBXExportAnimationOnly -v 0')
        mel.eval('FBXExportInAscii -v 1')
        mel.eval(f'FBXExport -f "{encoded_path}" -s')


    def _select_with_prefix(self):
        """
        指定されたprefixを使用してノードを選択します。
        """
        if not self.prefix.endswith(":"):
            self.prefix += ":"
        prefixed_nodes = [f"{self.prefix}{node}" for node in self.joints]
        return prefixed_nodes


    """
    bake animation export
    """
    def animation_export(self):

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        cmds.currentTime(self.start_frame)

        # **root ノードの直下にある output ノードを検索**
        output_nodes = cmds.listRelatives("root", children=True, type="transform", fullPath=True) or []
        output_nodes = [node for node in output_nodes if "output" in node]

        if not output_nodes:
            raise RuntimeError("No 'output' node found under 'root'. Ensure that the hierarchy is correct.")

        output_node = output_nodes[0]
        output_joints = cmds.listRelatives(output_node, allDescendents=True, type="joint", fullPath=True) or []

        if not output_joints:
            raise RuntimeError("No joints found under 'output'. Ensure that the output node exists and has children.")

        self.joints = output_joints
        cmds.select(clear=True)
        cmds.select(self.joints, replace=True)

        # **アニメーションをベイク**
        self._bake_animation(self.joints)

        # **ベイク後に connector、model を削除**
        if cmds.objExists("connector"):
            cmds.delete("connector")
            print("Connector node deleted before export.")

        if cmds.objExists("model"):
            cmds.delete("model")
            print("Model node deleted before export.")

        # output 自身をワールドに移動
        try:
            cmds.parent(output_node, world=True)
            print(f"Moved '{output_node}' to world.")
        except RuntimeError:
            print(f"⚠ Warning: Could not move '{output_node}' to world. Possible constraint or reference issue.")

        file_path = os.path.join(self.directory, f"{self.filename}.fbx")
        self._export_fbx(file_path)


    @staticmethod
    def clean_scene_for_export():
        """
        エクスポート前に不要なデータを削除。
        1. `line` 以外の頂点カラーセットを削除。
        2. `uvSet`, `hatching`, `sdf` 以外のUVセットを削除。
        3. L5リグツールを使用してリグを削除（コンストレインノードを残さない）。
        """
        # **① line 以外の頂点カラーを削除**
        meshes = cmds.ls(type="mesh")  # メッシュを取得
        for mesh in meshes:
            color_sets = cmds.polyColorSet(mesh, query=True, allColorSets=True) or []
            for color_set in color_sets:
                if color_set != "line":
                    try:
                        cmds.polyColorSet(mesh, delete=True, colorSet=color_set)
                        print(f"Deleted color set: {color_set} on {mesh}")
                    except RuntimeError:
                        print(f"Warning: Could not delete color set {color_set} on {mesh}")

        # **② 不要なUVセットを削除**
        keep_uv_sets = {"map1", "hatching", "sdf"}
        for mesh in meshes:
            uv_sets = cmds.polyUVSet(mesh, query=True, allUVSets=True) or []
            for uv_set in uv_sets:
                # 既定のUVセットは削除しない
                if uv_set not in keep_uv_sets:
                    try:
                        cmds.polyUVSet(mesh, delete=True, uvSet=uv_set)
                        print(f"Deleted UV Set: {uv_set} on {mesh}")
                    except RuntimeError:
                        print(f"Warning: Could not delete UV Set: {uv_set} on {mesh}")

        # **③ L5リグツールを使用してリグを削除**
        if cmds.pluginInfo("L5RigTool", query=True, loaded=True):
            cmds.unloadPlugin (rm=True)
            print("L5リグを削除しました。")
        else:
            print("Warning: L5リグツールが見つかりませんでした。")
        print("Scene cleanup completed.")


    """
    no animation export
    """
    def model_export(self):

        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        if not self.characters:
            print("No characters provided for export. Aborting.")
            return

        print(f"self.characters => {self.characters}")

        # **"connector" を削除**
        if cmds.objExists("connector"):
            cmds.delete("connector")
            print("Deleted 'connector' node.")

        # エクスポート前に不要なデータをクリーンアップ
        self.clean_scene_for_export()

        # **rootの子ノードをすべて取得し、ワールドへ移動**
        if cmds.objExists("root"):
            root_children = cmds.listRelatives("root", children=True, fullPath=True) or []
            for child in root_children:
                if cmds.objExists(child):
                    try:
                        cmds.parent(child, world=True)
                        print(f"Moved {child} to world.")
                    except RuntimeError:
                        print(f"Warning: Could not move {child} to world. Possible constraint or reference issue.")

        if os.path.exists(self.K_PRESET_FILE_NAME) is False:
            print(f"Warning: FBX preset not found at {self.K_PRESET_FILE_NAME}")
            return

        all_meshes = []
        all_joints = []

        # meshごとにエクスポート
        for character in self.characters:
            sanitized_character = character.replace(":", "_")
            cmds.select(character)
            meshes = cmds.ls(selection=True, dag=True, type='mesh')

            local_joints = self.get_related_joints(meshes)
            print(f"joints => {local_joints}")

            # **リファレンスオブジェクトの変換（リファレンス解除）**
            local_transforms = [character]

            try:
                # **トランスフォームをワールドへ移動**
                cmds.parent(local_transforms, world=True)
                print(f"Moved {character} to world.")
            except RuntimeError:
                print(f"Warning: Could not move {character} to world. Possible constraint or reference issue.")


            all_meshes.extend(meshes)
            all_joints.extend(local_joints)


        cmds.select(clear=True)
        cmds.select(all_meshes, add=True)
        cmds.select(all_joints, add=True)

        mel.eval('FBXLoadExportPresetFile -f "' + self.K_PRESET_FILE_NAME + '"')
        print(f"Loaded FBX preset: {self.K_PRESET_FILE_NAME}")

        file_path = os.path.join(self.directory, f"{self.filename}.fbx")

        encoded_path = file_path.replace("\\", "/")

        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        # reset export
        mel.eval('FBXResetExport')
        # Enable skeleton definitions and skin export
        mel.eval('FBXExportSkeletonDefinitions -v 1')
        mel.eval('FBXExportSkins -v 1')
        mel.eval('FBXExportBakeComplexAnimation -v 0')
        mel.eval('FBXExportAnimationOnly -v 0')
        # バイナリ形式でエクスポート
        mel.eval('FBXExportInAscii -v 0')
        mel.eval(f'FBXExport -f "{encoded_path}" -s')




class Animation_ExporterGUI(QDialog):

    WINDOW_TITLE = "Character ToolKit"
    MODULE_VERSION = "1.3"

    def __init__(self, parent=None, *args, **kwargs):
        super(Animation_ExporterGUI, self).__init__(maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 420)
        self.default_style = "background-color: #34d8ed; color: black"
        self.model_style = "background-color: #ff8080; color: black;"
        self.setStyleSheet('background-color:#262f38;')

        self.export_configs = []

        main_layout = QtWidgets.QVBoxLayout()

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { /* タブ全体の背景 */
                border: 1px solid #2c3e50; background: #2c3e50;
            }
            QTabBar::tab { /* 通常 */
                background: #34495e; color: white; padding: 10px;
                border: 1px solid #2c3e50; border-bottom: none;
            }
            QTabBar::tab:selected { /* 選択中 */
                background: #1abc9c; color: white;
            }
            QTabBar::tab:hover { /* ホバー時 */
                background: #16a085; }
        """)

        main_layout.addWidget(self.tabs)
        self.model_directory = None
        self.model_directory_label  = None
        self.model_directory_button = None

        self.animation_directory = None
        self.animator_directory_label = None
        self.animator_directory_button = None

        self.character_label = None
        self.character_list = None
        self.update_button = None
        self.clear_button = None
        self.filename_label = None
        self.filename_edit = None

        self.start_label = None
        self.start_frame = None
        self.end_label = None
        self.end_frame = None

        self.export_button = None
        self.export_without_bake_button = None
        self.create_model_scene_button = None
        self.create_animation_scene_button = None

        # エクスポート設定リスト
        self.export_config_list = None

        self.animator_tab = self._create_animator_tab()
        self.tabs.addTab(self.animator_tab, "Animator")
        self.modeler_tab = self._create_modeler_tab()
        self.tabs.addTab(self.modeler_tab, "Modeler")
        self.setLayout(main_layout)


    def _create_animator_tab(self):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        """
        export_directory : "your/path",
        export_setting :
        [
            {
                "root_node": LTN:root,
                "prefix" : LTN,
                "file_name": foo,
                "joints": rig["joints"],
                "controllers": rig["controllers"],
                "start_frame": 0,
                "end_frame": 100
            },
            {
                "root_node": LUK:root,
                "prefix" : LUK,
                "file_name": bar,
                "joints": rig["joints"],
                "controllers": rig["controllers"],
                "start_frame": 0,
                "end_frame": 120            
            }
        ]
        """

        self.export_config_list = QListWidget()
        self.export_config_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        layout.addWidget(self.export_config_list)

        # ボタン用のグリッドレイアウト
        button_layout = QtWidgets.QGridLayout()

        add_config_button = QPushButton("Add Config")
        add_config_button.setStyleSheet(self.default_style)
        add_config_button.clicked.connect(self._add_config)
        button_layout.addWidget(add_config_button, 0, 0)

        edit_config_button = QPushButton("Edit Config")
        edit_config_button.setStyleSheet(self.default_style)
        edit_config_button.clicked.connect(self._edit_config)
        button_layout.addWidget(edit_config_button, 0, 1)

        remove_config_button = QPushButton("Remove Config")
        remove_config_button.setStyleSheet(self.default_style)
        remove_config_button.clicked.connect(self._remove_config)
        button_layout.addWidget(remove_config_button, 1, 0)

        find_references_button = QPushButton("Find Rig")
        find_references_button.setStyleSheet(self.default_style)
        find_references_button.clicked.connect(self._find_and_add_reference_rigs)
        button_layout.addWidget(find_references_button, 1, 1)

        layout.addLayout(button_layout)

        # エクスポートディレクトリ選択
        self.animator_directory_label = QLabel("Animator Export Directory:")
        self.animator_directory_button = QPushButton("Choose Directory")
        self.animator_directory_button.setStyleSheet(self.default_style)
        self.animator_directory_button.clicked.connect(self._select_animator_export_directory)
        layout.addWidget(self.animator_directory_label)
        layout.addWidget(self.animator_directory_button)

        # エクスポート実行ボタン
        export_button = QPushButton("Export Animation")
        export_button.setStyleSheet(self.model_style)
        export_button.clicked.connect(self._export_configurations)
        layout.addWidget(export_button)

        tab.setLayout(layout)
        return tab


    @staticmethod
    def get_joints_and_controls_under_root(root_node):
        """
        Retrieve all joints and animation controls under the specified root node.
        """
        if not cmds.objExists(root_node):
            print(f"Root node '{root_node}' does not exist in the scene.")
            return {"joints": [], "controls": []}

        # 再帰的に全ての子孫ノードを取得
        descendants = cmds.listRelatives(root_node, allDescendents=True, fullPath=True) or []

        if g_is_strip_name_space:
            joints = [
                node.split("|")[-1].split(":")[-1]
                for node in descendants if cmds.nodeType(node) == "joint"
            ]

            controls = [
                cmds.listRelatives(node, parent=True, fullPath=False)[0].split(":")[-1]
                for node in descendants if cmds.nodeType(node) == "nurbsCurve"
            ]
        else:
            joints = [
                node.split("|")[-1]
                for node in descendants if cmds.nodeType(node) == "joint"
            ]

            controls = [
                cmds.listRelatives(node, parent=True, fullPath=False)[0]
                for node in descendants if cmds.nodeType(node) == "nurbsCurve"
            ]

        return joints, controls


    @staticmethod
    def find_reference_rigs():
        """
        シーン内のリファレンスリグを検索し、ジョイントまたはAnimation Controllerがある場合のみ結果に含める。
        top nodeは "root" から取得
        """
        references = cmds.file(query=True, reference=True)
        if not references:
            print("No reference nodes found in the scene.")
            return []

        reference_rigs = []
        for ref in references:
            try:
                # リファレンスファイルから名前空間を取得
                namespace = cmds.file(ref, query=True, namespace=True)
                prefix = namespace.split(":")[0] if ":" in namespace else namespace

                # 名前空間が有効かを確認（空でない、または ":" を含む場合に有効とみなす）
                if not namespace or namespace == ":":
                    print(f"Skipped namespace: {namespace} (Invalid or empty)")
                    continue

                # 名前空間以下のトップノードを取得
                top_nodes = cmds.ls(f"{namespace}:*", assemblies=True)
                print(f"namespace found => {namespace}")
                print(f"top_nodes found => {top_nodes}")

                for top_node in top_nodes:
                    if "root" not in top_node:
                        continue

                    joints, controllers = Animation_ExporterGUI.get_joints_and_controls_under_root(top_node)

                    if not joints and not controllers:
                        print(f"Skipped {top_node}: No joints or animation controllers found.")
                        continue

                    file_name = top_node.replace(":", "_")

                    reference_rigs.append({
                        "reference_node": ref,
                        "root_node": top_node,
                        "prefix": prefix,
                        "file_name": file_name,
                        "joints": joints,
                        "controllers": controllers
                    })
                    print(f"Found rig: {top_node}, Prefix:{prefix}, Joints: {len(joints)}, Controllers: {len(controllers)}")

            except RuntimeError as e:
                print(f"Error processing reference node {ref}: {e}")
        return reference_rigs


    def _find_and_add_reference_rigs(self):
        """
        Find reference rigs in the current Maya scene and add them to the export configurations.
        Automatically sets start and end frames to the scene's playback range.
        """
        reference_rigs = Animation_ExporterGUI.find_reference_rigs()
        if not reference_rigs:
            print("No reference rigs found in the current scene.")
            return

        start_frame = int(cmds.playbackOptions(query=True, min=True))
        end_frame = int(cmds.playbackOptions(query=True, max=True))

        for rig in reference_rigs:
            root_node = rig["root_node"]
            file_name = rig["file_name"]
            prefix = rig["prefix"]

            if any(config["root_node"] == root_node for config in self.export_configs):
                print(f"Skipped duplicate configuration for top node: {root_node}")
                continue

            config = {
                "root_node": root_node,
                "file_name": file_name,
                "prefix": prefix,
                "joints": rig["joints"],
                "controllers": rig["controllers"],
                "start_frame": start_frame,
                "end_frame": end_frame
            }
            self.export_configs.append(config)
            self.export_config_list.addItem(f"{prefix} | {root_node} | {config['start_frame']}-{config['end_frame']} | {file_name}")


    def _edit_config(self):
        """
        Edit the configuration of the selected export setting.
        """
        selected_items = self.export_config_list.selectedItems()
        if not selected_items:
            print("No configuration selected!")
            return

        selected_index = self.export_config_list.row(selected_items[0])
        if selected_index < 0 or selected_index >= len(self.export_configs):
            print(f"Error: Selected index {selected_index} is out of range.")
            return

        selected_config = self.export_configs[selected_index]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Export Configuration")
        layout = QVBoxLayout(dialog)

        root_node_label = QLabel("RootNode:")
        root_node_edit = QLineEdit(selected_config.get("root_node", ""))
        layout.addWidget(root_node_label)
        layout.addWidget(root_node_edit)

        prefix_label = QLabel("Prefix:")
        prefix_edit = QLineEdit(selected_config.get("prefix", ""))
        layout.addWidget(prefix_label)
        layout.addWidget(prefix_edit)

        start_frame_label = QLabel("Start Frame:")
        start_frame_spinbox = QSpinBox()
        start_frame_spinbox.setRange(0, 10000)
        start_frame_spinbox.setValue(selected_config.get("start_frame", 0))
        layout.addWidget(start_frame_label)
        layout.addWidget(start_frame_spinbox)

        end_frame_label = QLabel("End Frame:")
        end_frame_spinbox = QSpinBox()
        end_frame_spinbox.setRange(1, 10000)
        end_frame_spinbox.setValue(selected_config.get("end_frame", 1000))
        layout.addWidget(end_frame_label)
        layout.addWidget(end_frame_spinbox)

        file_name_label = QLabel("Input File Name:")
        file_name_edit = QLineEdit(selected_config.get("file_name", ""))
        layout.addWidget(file_name_label)
        layout.addWidget(file_name_edit)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def edit_config_internal():
            selected_config: dict = self.export_configs[selected_index]
            root_node_name = root_node_edit.text().strip()
            selected_config["root_node"] = root_node_name
            selected_config["prefix"] = prefix_edit.text().strip()
            selected_config["start_frame"] = start_frame_spinbox.value()
            selected_config["end_frame"] = end_frame_spinbox.value()
            selected_config["file_name"] = file_name_edit.text().strip()

            if not selected_config["joints"] or not selected_config["controllers"]:
                joints, controllers = self.get_joints_and_controls_under_root(root_node_name)
                selected_config["joints"] = joints
                selected_config["controllers"] = controllers
                print(f"Updated joints and controllers for root node '{root_node_name}':")
                print(f"Joints: {joints}")
                print(f"Controllers: {controllers}")

            self.export_config_list.item(selected_index).setText(f"{selected_config['prefix']} | {selected_config['root_node']} | " f"{selected_config['start_frame']}-{selected_config['end_frame']} | {selected_config['file_name']}")
            dialog.accept()

        ok_button.clicked.connect(edit_config_internal)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()


    def _add_config(self):
        """
        設定を追加
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Export Config")
        layout = QVBoxLayout(dialog)

        root_node_label = QLabel("RootNode:")
        root_node_edit = QLineEdit()
        layout.addWidget(root_node_label)
        layout.addWidget(root_node_edit)

        prefix_label = QLabel("Prefix:")
        prefix_edit = QLineEdit()
        layout.addWidget(prefix_label)
        layout.addWidget(prefix_edit)

        start_frame_label = QLabel("Start Frame:")
        start_frame_spinbox = QSpinBox()
        start_frame_spinbox.setRange(0, 10000)
        layout.addWidget(start_frame_label)
        layout.addWidget(start_frame_spinbox)

        end_frame_label = QLabel("End Frame:")
        end_frame_spinbox = QSpinBox()
        end_frame_spinbox.setRange(1, 10000)
        layout.addWidget(end_frame_label)
        layout.addWidget(end_frame_spinbox)

        file_name_label = QLabel("Input File Name:")
        file_name_edit = QLineEdit()
        layout.addWidget(file_name_label)
        layout.addWidget(file_name_edit)

        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        def add_config_internal():
            prefix = prefix_edit.text().strip()
            root_node = root_node_edit.text().strip()
            file_name = file_name_edit.text().strip()
            if root_node:
                joints, controllers = self.get_joints_and_controls_under_root(root_node)
                config = {
                    "root_node": root_node,
                    "prefix": prefix,
                    "file_name": file_name,
                    "joints": joints,
                    "controllers": controllers,
                    "start_frame": start_frame_spinbox.value(),
                    "end_frame": end_frame_spinbox.value(),
                }
                self.export_configs.append(config)
                self.export_config_list.addItem(f"{prefix} | {root_node} | {config['start_frame']}-{config['end_frame']} | {file_name}")
                dialog.accept()

        ok_button.clicked.connect(add_config_internal)
        cancel_button.clicked.connect(dialog.reject)
        dialog.exec_()


    def _remove_config(self):
        """
        選択したconfigを削除
        """
        selected_items = self.export_config_list.selectedItems()
        if not selected_items:
            print("No configuration selected!")
            return

        selected_index = self.export_config_list.row(selected_items[0])
        if selected_index < 0 or selected_index >= len(self.export_configs):
            print(f"Error: Selected index {selected_index} is invalid.")
            return

        print(f"Removing config at index: {selected_index}, Config: {self.export_configs[selected_index]}")

        del self.export_configs[selected_index]
        self.export_config_list.takeItem(selected_index)
        print("Configuration removed successfully.")


    def _show_progress_bar(self, max_value, title="Processing", label="Processing files..."):
        progress_dialog = QtWidgets.QProgressDialog(label, None, 0, max_value, self)
        progress_dialog.setWindowTitle(title)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModal)
        progress_dialog.show()
        QtCore.QCoreApplication.processEvents()
        return progress_dialog


    # Animation Exporter Single and Multiple
    def _export_configurations(self):
        """
        保存された設定に基づいてエクスポートを実行
        """
        if not self.export_configs:
            print("No export configurations to process!")
            return

        directory = self.animation_directory

        if not directory:
            print("Export directory is not set!")
            return

        total_configs = len(self.export_configs)
        progress_dialog = self._show_progress_bar(total_configs, title="Exporting...", label="Exporting rigs...")

        is_multiple_export = len(self.export_configs) > 1

        if g_is_strip_name_space is True:
            Util.AnimationUtil.toggle_plugin_scanner(False)
        else:
            if is_multiple_export:
                Util.AnimationUtil.toggle_plugin_scanner(False)
            Util.AnimationUtil.all_import_reference()
            if not is_multiple_export:
                Util.AnimationUtil.remove_namespace()

        successful_exports = 0

        for index, config in enumerate(self.export_configs):
            try:
                root_node = config["root_node"]
                file_name = config["file_name"]
                prefix = config["prefix"]
                start_frame = config["start_frame"]
                end_frame = config["end_frame"]
                joints = config["joints"]
                controllers = config["controllers"]
                progress_dialog.setLabelText(f"Exporting {file_name}...")

                print(f"prefix => {prefix}")
                Util.AnimationUtil.all_import_reference()
                restore_data = Util.AnimationUtil.remove_namespace_prefix(prefix=prefix)

                exporter = AnimationExporter(characters=root_node, filename=file_name, directory=directory,
                                             start_frame=start_frame, end_frame=end_frame, bake_keyframes=True,
                                             joints=joints, controllers=controllers, prefix=prefix,
                                             multiple_export=is_multiple_export)

                exporter.animation_export()
                successful_exports += 1

                if g_is_strip_name_space is True:
                    Util.AnimationUtil.restore_namespace(restore_data=restore_data)
                    Util.AnimationUtil.reload_current_scene_without_saving()

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Export Error", f"Error exporting {config['file_name']}: {str(e)}")
                progress_dialog.close()
                Util.AnimationUtil.toggle_plugin_scanner(True)
                return

            progress_dialog.setValue(index + 1)
            QtCore.QCoreApplication.processEvents()
            if progress_dialog.wasCanceled():
                print(f"Export canceled. {index} of {total_configs} files were processed.")
                break

        progress_dialog.close()
        Util.AnimationUtil.reload_current_scene_without_saving()
        Util.AnimationUtil.toggle_plugin_scanner(True)
        if successful_exports == total_configs:
            QtWidgets.QMessageBox.information(self, "Export Complete", "All files have been successfully exported.")
        else:
            QtWidgets.QMessageBox.warning(self, "Partial Export", f"{successful_exports} of {total_configs} files were successfully exported.")


    def _select_animator_export_directory(self):
        self.animation_directory = QFileDialog.getExistingDirectory(self, "Choose Export Dir")
        if self.animation_directory:
            self.animator_directory_label.setText(f"Directory: {self.animation_directory}")


    # @TODO
    # Wip
    def _create_modeler_tab(self):
        tab = QtWidgets.QWidget()
        layout = QVBoxLayout()
        # キャラクターリスト
        self.character_label = QLabel("Mesh Selection (multiple selections allowed)")
        self.character_list = QListWidget()
        self.character_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.character_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.character_label)
        layout.addWidget(self.character_list)

        character_list_layout = QGridLayout()
        # キャラクターリスト更新ボタン
        self.update_button = QPushButton("Add Mesh List")
        self.update_button.setStyleSheet(self.default_style)
        self.update_button.clicked.connect(self._update_character_list)
        character_list_layout.addWidget(self.update_button, 0, 0)

        # リストクリアボタン
        self.clear_button = QPushButton("Clear Mesh List")
        self.clear_button.setStyleSheet(self.default_style)
        self.clear_button.clicked.connect(self._clear_character_list)
        character_list_layout.addWidget(self.clear_button, 0, 1)
        layout.addLayout(character_list_layout)

        # 出力ファイル名
        self.filename_label = QLabel("Export FileName")
        self.filename_edit = QLineEdit()
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_edit)

        # 出力ディレクトリ選択
        self.model_directory_label = QLabel("Export Directory")
        self.model_directory_button = QPushButton("Choose Directory")
        self.model_directory_button.setStyleSheet(self.default_style)
        self.model_directory_button.clicked.connect(self._select_model_directory)
        layout.addWidget(self.model_directory_label)
        layout.addWidget(self.model_directory_button)

        button_layout = QGridLayout()
        # エクスポートボタン（アニメーションベイクなし）
        self.export_without_bake_button = QPushButton("Export Model")
        self.export_without_bake_button.setStyleSheet(self.model_style)
        self.export_without_bake_button.clicked.connect(self._export_model)
        button_layout.addWidget(self.export_without_bake_button, 0, 0)

        # モデル用シーン作成ボタン
        self.create_model_scene_button = QPushButton("Create Model Scene")
        self.create_model_scene_button.setStyleSheet(self.model_style)
        self.create_model_scene_button.clicked.connect(self.create_modeler_scene_with_dialog)
        button_layout.addWidget(self.create_model_scene_button, 0, 1)

        # Animation用シーン作成ボタン
        self.create_animation_scene_button = QPushButton("Create Animation Scene")
        self.create_animation_scene_button.setStyleSheet(self.model_style)
        self.create_animation_scene_button.clicked.connect(self.create_animation_scene_with_dialog)
        button_layout.addWidget(self.create_animation_scene_button, 0, 2)

        layout.addLayout(button_layout)
        tab.setLayout(layout)
        return tab


    @staticmethod
    def create_modeler_scene_with_dialog():
        """
        Create a Modeler-specific MA file from the current Animator MA file with user-defined save path.
        Steps:
        1. Hide the 'rig' node.
        2. Show a dialog for the user to specify the save location.
        3. Save the file as <chosen_path>_work.ma.
        """
        # Step 1: Get the current scene name
        current_scene = cmds.file(query=True, sceneName=True)
        if not current_scene:
            print("Error: No scene is currently open.")
            return

        Util.AnimationUtil.find_rig_root_node(index=0)

        # Step 2: Open a dialog for saving the new file
        save_path = QFileDialog.getSaveFileName(None, "Save Modeler Scene", os.path.splitext(current_scene)[0] + "_work.ma", "Maya ASCII Files (*.ma)")[0]

        if not save_path:
            Util.AnimationUtil.find_rig_root_node(index=1)
            print("Save operation canceled.")
            return

        # Step 3: Save the scene as <chosen_path>_work.ma
        cmds.file(rename=save_path)
        cmds.file(save=True, type='mayaAscii')  # Save as .ma file
        print(f"Scene saved as: {save_path}")


    @staticmethod
    def create_animation_scene_with_dialog():
        """
        Create an animation scene by removing unnecessary nodes and saving the clean scene.
        Steps:
        1. Delete unnecessary nodes (`etc`, `guide_root`, `set1_fc`, `set1_hizi`, `set1_mata`).
        2. Keep the structure under `root` unchanged.
        3. Save the new scene as `scenes/キャラ名.ma`.
        """

        # **現在のシーン名を取得**
        current_scene = cmds.file(query=True, sceneName=True)
        if not current_scene:
            print("Error: No scene is currently open.")
            return

        # **シーンのディレクトリを取得**
        current_dir = os.path.dirname(current_scene)
        parent_dir = os.path.dirname(current_dir)  # 上の階層を取得
        scenes_dir = os.path.join(parent_dir, "scenes")  # `scenes/` フォルダに保存
        os.makedirs(scenes_dir, exist_ok=True)  # フォルダがなければ作成

        # **キャラクター名を取得（シーン名のベース部分を使用）**
        filename = os.path.basename(current_scene)
        character_name = os.path.splitext(filename)[0].replace("_rig", "")
        save_path = os.path.join(scenes_dir, f"{character_name}.ma")

        # **Step 1: 保存ダイアログを開く**
        save_path, _ = QFileDialog.getSaveFileName(None, "Save Animation Scene", save_path, "Maya ASCII Files (*.ma)")

        # **Step 2: キャンセルされた場合、何もせず終了**
        if not save_path:
            print("Save operation canceled. No changes were made.")
            return

        # **Step 3: 削除するノード一覧**
        nodes_to_delete = ["etc", "guide_root", "set1_fc", "set1_hizi", "set1_mata"]
        for node in nodes_to_delete:
            if cmds.objExists(node):
                cmds.delete(node)
                print(f"Deleted {node}")

        # **Step 4: シーンを保存**
        cmds.file(rename=save_path)
        cmds.file(save=True, type='mayaAscii')  # `.ma` として保存
        print(f"Animation scene saved at: {save_path}")
        QMessageBox.information(None, "Success", f"Scene saved successfully at:\n{save_path}")


    def _update_character_list(self):
        selected_meshes = cmds.ls(selection=True, type='transform')
        self.character_list.clear()  # リストをクリア
        for mesh in selected_meshes:
            item = QListWidgetItem(mesh)
            self.character_list.addItem(item)
            print(f"mesh => {mesh}")


    def _clear_character_list(self):
        """
        キャラクターリストをクリアします。
        """
        self.character_list.clear()


    def _on_selection_changed(self):
        selected_items = self.character_list.selectedItems()
        print(f"Currently selected items: {[item.text() for item in selected_items]}")  # 選択状態をデバッグ出力


    def _select_model_directory(self):
        self.model_directory = QFileDialog.getExistingDirectory(self, "Choose Export Dir")
        if self.model_directory:
            self.model_directory_label.setText(f"Directory: {self.model_directory}")


    @staticmethod
    def get_output_meshes():
        """
        Export meshes under 'root/output' without baking keyframes.
        """
        # Get all meshes under 'root/output'
        root_node = "root"
        output_node = f"{root_node}|output"  # Assuming "output" is directly under "root"
        if not cmds.objExists(output_node):
            print(f"Error: {output_node} does not exist.")
            return []

        # Get all meshes under 'output'
        meshes = cmds.listRelatives(output_node, allDescendents=True, type="mesh", fullPath=True)
        if not meshes:
            print(f"No meshes found under {output_node}")
            return []

        transforms = list(set(cmds.listRelatives(meshes, parent=True, fullPath=True)))
        sanitized_transforms = [transform.split("|")[-1] for transform in transforms]
        print(f"Sanitized Transforms: {sanitized_transforms}")
        return sanitized_transforms


    # @TODO
    # 自動取得は要望があれば対応
    def _export_model(self):
        """
        #自動で取得する場合の処理
        meshes = self._get_output_meshes()
        if not meshes:
            print("No meshes found to export.")
            return
        characters = meshes
        """
        """
        選択されたリストではなく、character_listに含まれる全ての要素をエクスポート
        """

        characters = [self.character_list.item(i).text() for i in range(self.character_list.count())]

        filename = self.filename_edit.text()
        directory = self.model_directory
        start_frame = int(cmds.playbackOptions(query=True, min=True))
        end_frame = int(cmds.playbackOptions(query=True, max=True))

        if not directory:
            print("Export directory is not set!")
            return

        # **名前空間の削除（エクスポート前）**
        Util.AnimationUtil.all_import_reference()
        prefix = characters[0].split(":")[0] if ":" in characters[0] else None
        restore_data = Util.AnimationUtil.remove_namespace_prefix(prefix=prefix)
        exporter = AnimationExporter(characters=characters, filename=filename, directory=directory, start_frame=start_frame, end_frame=end_frame, bake_keyframes=False)
        exporter.model_export()
        Util.AnimationUtil.restore_namespace(restore_data=restore_data)
        Util.AnimationUtil.reload_current_scene_without_saving()
        print("Model export completed.")


def show_main_window():
    global animation_exporter
    try:
        animation_exporter.close()  # type: ignore
        animation_exporter.deleteLater()  # type: ignore
    except:
        pass
    animation_exporter = Animation_ExporterGUI()
    animation_exporter.show()


# 外部からの呼び出し
def run_outer(file_paths):
    for path in file_paths:
        run_internal(path)

    # finish job
    if cmds.about(batch=True):
        logger.info("+-------------------------------------------------------+")
        logger.info("All Export complete. Exiting Maya Batch.")
        logger.info("+-------------------------------------------------------+")
        try:
            cmds.evalDeferred('cmds.quit(force=True)')
            cmds.quit(force=True)
            subprocess.run("taskkill /F /IM cmd.exe", shell=True)

        except Exception as e:
            logger.error(f"Failed to quit Maya: {e}")
    else:
        logger.info("Batch mode detected but '--no-exit' flag is present. Keeping Maya open.")


def run_internal(file_path):
    logger.info(f'Scene File Open >> {file_path}')
    cmds.file(file_path, o=True, force=True)
    asset_file_path = cmds.file(q=True, sn=True)

    if not asset_file_path:
        raise ValueError("No scene file is currently open in Maya.")

    filename = os.path.basename(asset_file_path)
    scene_name = os.path.splitext(filename)[0]

    base_directory = os.path.dirname(asset_file_path)
    output_directory = os.path.join(base_directory, "Exported")
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    start_frame = int(cmds.playbackOptions(query=True, min=True))
    end_frame = int(cmds.playbackOptions(query=True, max=True))
    logger.info(f"Start Frame: {start_frame}, End Frame: {end_frame}")
    # root ノードのみを検出する
    reference_rigs = Animation_ExporterGUI.find_reference_rigs()

    if not reference_rigs:
        logger.error("No output rigs found in the scene.")
        return

    logger.info(f"Start Export => {scene_name}")

    is_multiple_export = len(reference_rigs) > 1
    if g_is_strip_name_space is True:
        Util.AnimationUtil.toggle_plugin_scanner(False)
    else:
        if is_multiple_export:
            Util.AnimationUtil.toggle_plugin_scanner(False)
        Util.AnimationUtil.all_import_reference()
        if not is_multiple_export:
            Util.AnimationUtil.remove_namespace()

    for rig in reference_rigs:
        root_node = rig["root_node"]
        joints = rig["joints"]
        controllers = rig["controllers"]
        file_name = rig["file_name"]
        prefix = rig["prefix"]
        convert_file_name= scene_name + "_{}".format(file_name)
        logger.info(f"convert_file_name => {convert_file_name}")

        print(f"prefix => {prefix}")
        Util.AnimationUtil.all_import_reference()
        restore_data = Util.AnimationUtil.remove_namespace_prefix(prefix=prefix)

        exporter = AnimationExporter(
            characters=root_node, filename=convert_file_name, directory=output_directory,
            start_frame=start_frame, end_frame=end_frame, bake_keyframes=True, joints=joints, controllers=controllers,
            prefix=prefix,
            multiple_export=is_multiple_export)
        exporter.animation_export()

        if g_is_strip_name_space is True:
            Util.AnimationUtil.restore_namespace(restore_data=restore_data)
            Util.AnimationUtil.reload_current_scene_without_saving()

    Util.AnimationUtil.toggle_plugin_scanner(True)
    logger.info(f"Export => {scene_name} complete")



