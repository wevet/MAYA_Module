# -*- coding: utf-8 -*-

import os
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm


class Poly_Reduction:
    def __init__(self):
        self.clean_path = None
        self.original_path = None

    def apply_reduction(self):
        self.clean_path = ""
        self.original_path = cmds.fileDialog2(cap="Choose Folder to Reduce", ds=1, fm=3)

        if self.original_path is not None:
            self.clean_path = str(self.original_path[0])

        for root, dirs, files in os.walk(self.clean_path):
            print("root => {}, dirs => {}, files => {}".format(root, dirs, files))

            for file_name in files:
                if file_name.endswith(".fbx"):
                    print("file_name => {}".format(file_name))
                    file_path = root + "/" + file_name
                    cmds.file(file_path, open=True, force=True)

                    obj = cmds.ls(geometry=True)
                    for item in obj:
                        try:
                            cmds.polyReduce(p=50, n=cmds.select(item))
                        except:
                            pass
                        #pm.mel.FBXExport(f=file_path)
                        self._export_fbx(file_path)

    def _export_fbx(self, file_path):
        """
        # @TODO
        #  1の場合はOSネイティブ
        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            mel.eval('savePrefsChanges;')
        """

        if mel.eval('optionVar -q "FileDialogStyle"') == 1:
            self.has_native_os = True
            mel.eval('optionVar -iv FileDialogStyle 2 ;')
            print("modify FileDialogStyle")

        if not cmds.pluginInfo('fbxmaya', q=True, loaded=True):
            cmds.loadPlugin('fbxmaya')

        mel.eval('FBXResetExport')
        mel.eval('FBXExportBakeComplexAnimation -v 1')
        mel.eval('FBXExportInAscii -v 1')
        mel.eval('FBXExport -f "' + file_path + '" -s')


if __name__ == "__main__":
    reduction = Poly_Reduction()
    reduction.apply_reduction()
    pass



