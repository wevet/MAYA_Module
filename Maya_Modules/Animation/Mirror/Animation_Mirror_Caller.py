# -*- coding: utf-8 -*-

import sys
import os

"""
Python class to automate Animation Mirror

1.Drag & drop the folder to create.bat file.
2.Select mirror mode.

"""

K_MAYA_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\maya.exe'
K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\mayabatch.exe'

class Animation_Mirror_Caller:

    def __init__(self):
        self.source_directory = sys.argv[1]
        self.file_list = []

        # @TODO
        # Need to pass the result of the bat file.
        self.mirror_mode = 3
        pass

    def main(self, index):
        self.file_list = self._get_list_directory_files()
        self.mirror_mode = int(index)

        path = os.getcwd()
        cmd = 'SET MAYA_UI_LANGUAGE=ja_JP' + '\n'
        #cmd += 'SET MAYA_PLUG_IN_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_MODULE_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_SCRIPT_PATH=C:dir'+'\n'
        cmd += 'SET PYTHONPATH=%s' % path + '\n'

        # logを入れるフォルダを作成
        self._check_directory()

        for file in self.file_list:
            replace_path = os.path.join(self.source_directory, file).replace('\\', '/')
            root, ext = os.path.splitext(replace_path)
            log_path = os.path.join(self.source_directory, 'Log', file).replace(ext, '.log')
            cmd += '\n'
            cmd += 'SET MAYA_CMD_FILE_OUTPUT={0}'.format(log_path) + '\n'
            cmd += '"{0}"'.format(K_MAYA_BATCH_EXE) + ' -command'
            cmd += ' "python(\\"import Animation_Mirror;Animation_Mirror.run(\'{}, {}\')\\")"'.format(replace_path, self.mirror_mode)

        dir_path, current_path_name = os.path.split(self.source_directory)
        path = os.path.join(dir_path, 'animation_mirror_run.bat')
        self._save_bat_file(path, cmd)

    def _save_bat_file(self, path, cmd):
        with open(path, "w") as file:
            file.write(cmd)

    def _check_directory(self):
        if os.path.isdir(os.path.join(self.source_directory, 'Log')) is False:
            os.makedirs(os.path.join(self.source_directory, 'Log'))

    def _get_list_directory_files(self):
        file_list = []
        for file_name in os.listdir(self.source_directory):
            file_path = os.path.join(self.source_directory, file_name)
            if os.path.isfile(file_path):
                file_list.append(file_name)
        return file_list


if __name__ == '__main__':
    # args 1 run python file name
    # args 2 mirror mode index
    params = sys.argv
    for param in params:
        print("parameters => {}".format(param))

    caller = Animation_Mirror_Caller()
    caller.main(params[1])



