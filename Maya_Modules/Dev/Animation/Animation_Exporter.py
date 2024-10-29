# -*- coding: utf-8 -*-

import sys
import os
from PySide2.QtWidgets import QVBoxLayout, QPushButton, QLabel, QComboBox, QLineEdit, QSpinBox, QFileDialog, QDialog, QCheckBox
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

        # キャラクターごとにエクスポート
        for character in self.characters:
            cmds.select(character)
            if self.frame_split:
                file_path = os.path.join(self.directory, f"{self.filename}_{character}_frames_{self.start_frame}-{self.end_frame}.fbx")
                self._export_fbx(file_path, self.start_frame, self.end_frame)
            else:
                file_path = os.path.join(self.directory, f"{self.filename}_{character}.fbx")
                self._export_fbx(file_path, self.start_frame, self.end_frame)


    def _export_fbx(self, file_path, start_frame, end_frame):
        """
        Export selected character to an FBX file.
        """
        cmds.playbackOptions(min=start_frame, max=end_frame)
        self._prepare_fbx_export()
        mel.eval(f'FBXExport -f "{file_path}" -s')
        print(f"Exported {file_path} from frames {start_frame} to {end_frame}")



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
        self.characters = []  # キャラクターリストのデフォルト

        # キャラクターリスト
        self.character_label = QLabel("Choose Target")
        self.character_list = QComboBox()
        self.character_list.addItems(self.characters)
        layout.addWidget(self.character_label)
        layout.addWidget(self.character_list)

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


    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "出力先ディレクトリを選択")
        if self.directory:
            self.dir_label.setText(f"出力先: {self.directory}")


    def export_animation(self):
        character = self.character_list.currentText()
        filename = self.filename_edit.text()
        start_frame = self.start_frame.value()
        end_frame = self.end_frame.value()
        directory = self.directory
        frame_split = self.frame_split_checkbox.isChecked()

        # AnimationExporterクラスを利用してエクスポート処理を実行
        exporter = AnimationExporter(
            characters=[character],
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




