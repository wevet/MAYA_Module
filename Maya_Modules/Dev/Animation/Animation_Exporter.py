# -*- coding: utf-8 -*-

import sys
import os
from PySide2.QtWidgets import QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QSpinBox, QFileDialog, QDialog, QCheckBox, QListWidget, QListWidgetItem
from PySide2 import QtCore, QtWidgets
import maya.cmds as cmds
import maya.OpenMayaUI as omui
from shiboken2 import wrapInstance
from functools import partial
import maya.mel as mel


def maya_main_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QMainWindow)


class AnimationExporter:
    def __init__(self, characters, filename, directory, start_frame, end_frame, frame_split=False):
        """
        :param characters: List of character names to export
        :param filename: Base filename for exported files
        :param directory: Directory to export files to
        :param start_frame: Start frame for export
        :param end_frame: End frame for export
        :param frame_split: Boolean indicating if frames should be split into multiple files
        """
        self.characters = characters
        self.filename = filename
        self.directory = directory
        self.start_frame = int(start_frame)
        self.end_frame = int(end_frame)
        self.frame_split = frame_split

        # プラグインのロード
        if not cmds.pluginInfo('fbxmaya', query=True, loaded=True):
            cmds.loadPlugin('fbxmaya')


    @staticmethod
    def get_related_joints(meshes):
        """
        選択されたメッシュに影響を与えているジョイントを取得します。
        """
        joints = set()
        for mesh in meshes:
            skin_cluster = cmds.ls(cmds.listHistory(mesh), type='skinCluster')
            if skin_cluster:
                influences = cmds.skinCluster(skin_cluster[0], query=True, influence=True)
                joints.update(influences)
        return list(joints)


    @staticmethod
    def _get_bake_attributes(objects):
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


    def bake_animation(self, objects):
        bake_attributes = self._get_bake_attributes(objects)
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
                preserveOutsideKeys=False,
                sparseAnimCurveBake=False,
                disableImplicitControl=True,
                removeBakedAttributeFromLayer=False,
            )
        else:
            print("Cannot find any connection to bake!")


    @staticmethod
    def _prepare_fbx_export():
        """
        Set up FBX export options.
        """
        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
        mel.eval('FBXResetExport')
        mel.eval('FBXExportBakeComplexAnimation -v 1')
        mel.eval('FBXExportInAscii -v 1')


    def export(self):
        """
        Export each character as specified in the class parameters.
        """
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        print(f"self.characters => {self.characters}")

        # キャラクターごとにエクスポート
        for character in self.characters:
            # キャラクター名のコロンをアンダースコアに置換
            sanitized_character = character.replace(":", "_")

            cmds.select(character)

            # メッシュに関連するジョイントを取得してアニメーションをベイク
            meshes = cmds.ls(selection=True, dag=True, type='mesh')
            joints = self.get_related_joints(meshes)

            print(f"joints => {joints}")
            #self.bake_animation(joints)

            file_path = os.path.join(self.directory, f"{self.filename}_{sanitized_character}.fbx")
            if self.frame_split:
                file_path = os.path.join(self.directory, f"{self.filename}_{sanitized_character}_frames_{self.start_frame}-{self.end_frame}.fbx")
            self._export_fbx(file_path, self.start_frame, self.end_frame)


    def _export_fbx(self, file_path, start_frame, end_frame):
        """
        Export selected character to an FBX file.
        """
        cmds.playbackOptions(min=start_frame, max=end_frame)
        self._prepare_fbx_export()
        encoded_path = file_path.replace("\\", "/")
        mel.eval(f'FBXExport -f "{encoded_path}" -s')
        print(f"Exported {encoded_path} from frames {start_frame} to {end_frame}")



class Animation_ExporterGUI(QDialog):

    WINDOW_TITLE = "Animation Exporter"
    MODULE_VERSION = "1.0"

    def __init__(self, parent=None, *args, **kwargs):
        super(Animation_ExporterGUI, self).__init__(maya_main_window())

        self.setWindowTitle(self.WINDOW_TITLE + " v" + self.MODULE_VERSION)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.resize(420, 420)
        self.default_style = "background-color: #34d8ed; color: black"
        self.setStyleSheet('background-color:#262f38;')

        layout = QVBoxLayout()

        self.directory = None

        # キャラクターリスト
        self.character_label = QLabel("Character Selection (multiple selections allowed)")
        self.character_list = QListWidget()
        self.character_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.character_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.character_label)
        layout.addWidget(self.character_list)

        # キャラクターリスト更新ボタン
        self.update_button = QPushButton("Update Character List")
        self.update_button.setStyleSheet(self.default_style)
        self.update_button.clicked.connect(self.update_character_list)
        layout.addWidget(self.update_button)

        # リストクリアボタン
        self.clear_button = QPushButton("Clear Character List")
        self.clear_button.setStyleSheet(self.default_style)
        self.clear_button.clicked.connect(self.clear_character_list)
        layout.addWidget(self.clear_button)

        # 出力ファイル名
        self.filename_label = QLabel("Export FileName")
        self.filename_edit = QLineEdit()
        layout.addWidget(self.filename_label)
        layout.addWidget(self.filename_edit)

        # 出力ディレクトリ選択
        self.dir_label = QLabel("Export Directory")
        self.dir_button = QPushButton("Choose Directory")
        self.dir_button.setStyleSheet(self.default_style)
        self.dir_button.clicked.connect(self.select_directory)
        layout.addWidget(self.dir_label)
        layout.addWidget(self.dir_button)

        # フレームレンジ指定
        self.start_label = QLabel("Start Frame")
        self.start_frame = QSpinBox()
        self.start_frame.setMinimum(1)
        # 開いているシーンのStart Frame
        self.start_frame.setValue(int(cmds.playbackOptions(query=True, min=True)))
        self.end_label = QLabel("End Frame")
        self.end_frame = QSpinBox()
        self.end_frame.setMinimum(1)
        # 開いているシーンのEnd Frame
        self.end_frame.setValue(int(cmds.playbackOptions(query=True, max=True)))
        layout.addWidget(self.start_label)
        layout.addWidget(self.start_frame)
        layout.addWidget(self.end_label)
        layout.addWidget(self.end_frame)

        # フレーム分割オプションのチェックボックス
        self.frame_split_checkbox = QCheckBox("Output by specifying frames")
        layout.addWidget(self.frame_split_checkbox)

        # エクスポートボタン
        self.export_button = QPushButton("Export Animation")
        self.export_button.setStyleSheet(self.default_style)
        self.export_button.clicked.connect(self.export_animation)
        layout.addWidget(self.export_button)
        self.setLayout(layout)

        """
        以下のformatに沿った形式でfbx exportできるといい？
        [
            {
                "mesh_name" : "mGear:m_med_nrw_body_lod0_mesh",
                "time_range" : [0, 100], [200, 500],
                "file_name" : ["A", "B"]
            },
            {
                "mesh_name" : "mGear:m_med_nrw_body_lod1_mesh",
                "time_range" : [0, 100], [200, 500],
                "file_name" : ["A", "B"]            
            },
            {
                "mesh_name" : "mGear:m_med_nrw_body_lod0_mesh",
                "time_range" : [0, 100],
                "file_name" : "Sample"
            },
        ]

        """


    def update_character_list(self):
        selected_meshes = cmds.ls(selection=True, type='transform')
        self.character_list.clear()  # リストをクリア
        for mesh in selected_meshes:
            item = QListWidgetItem(mesh)
            self.character_list.addItem(item)
            print(f"mesh => {mesh}")


    def clear_character_list(self):
        """
        キャラクターリストをクリアします。
        """
        self.character_list.clear()


    def on_selection_changed(self):
        selected_items = self.character_list.selectedItems()
        print(f"Currently selected items: {[item.text() for item in selected_items]}")  # 選択状態をデバッグ出力


    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Choose Export Dir")
        if self.directory:
            self.dir_label.setText(f"Directory: {self.directory}")


    def export_animation(self):
        selected_items = self.character_list.selectedItems()
        print(f"Selected items: {[item.text() for item in selected_items]}")  # デバッグ
        characters = [item.text() for item in selected_items]
        filename = self.filename_edit.text()
        directory = self.directory
        frame_split = self.frame_split_checkbox.isChecked()

        # frame_splitがFalseの場合、Mayaファイルのデフォルトフレーム範囲を使用
        if frame_split:
            start_frame = self.start_frame.value()
            end_frame = self.end_frame.value()
        else:
            start_frame = int(cmds.playbackOptions(query=True, min=True))
            end_frame = int(cmds.playbackOptions(query=True, max=True))

        print(f"export_animation")

        # AnimationExporterクラスを利用してエクスポート処理を実行
        exporter = AnimationExporter(
            characters=characters,
            filename=filename,
            directory=directory,
            start_frame=start_frame,
            end_frame=end_frame,
            frame_split=frame_split
        )
        exporter.export()



def show_main_window():
    global animation_exporter
    try:
        animation_exporter.close()  # type: ignore
        animation_exporter.deleteLater()  # type: ignore
    except:
        pass
    animation_exporter = Animation_ExporterGUI()
    animation_exporter.show()




