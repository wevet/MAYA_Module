# -*- coding: utf-8 -*-

import sys
import os


K_MAYA_EXE = r'C:\Program Files\Autodesk\Maya2023\bin\maya.exe'
K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe'

class HIK_Automation_Caller:

    def __init__(self):
        self.source_directory = None
        self.file_list = []
        pass

    def main(self, new_source_directory):
        self.source_directory = new_source_directory
        self.file_list = self._get_list_directory_files()

        path = os.getcwd()
        cmd = 'SET MAYA_UI_LANGUAGE=ja_JP' + '\n'
        #cmd += 'SET MAYA_PLUG_IN_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_MODULE_PATH=C:dir'+'\n'
        #cmd += 'SET MAYA_SCRIPT_PATH=C:dir'+'\n'
        cmd += 'SET PYTHONPATH=%s' % path + '\n'

        # create log directory
        self._check_directory()

        for file in self.file_list:

            # ignore ma mb files
            prefix = os.path.splitext(file)
            if ".FBX" == prefix[1]:

                print("Execute the following fbx file. => {}".format(file))
                replace_path = os.path.join(self.source_directory, file).replace('\\', '/')
                root, ext = os.path.splitext(replace_path)
                log_path = os.path.join(self.source_directory, 'Log', file).replace(ext, '.log')
                cmd += '\n'
                cmd += 'SET MAYA_CMD_FILE_OUTPUT={0}'.format(log_path) + '\n'
                cmd += '"{0}"'.format(K_MAYA_BATCH_EXE) + ' -command'
                cmd += ' "python(\\"import HIK_Automation;HIK_Automation.run(\'{}\')\\")"'.format(replace_path)

        dir_path, current_path_name = os.path.split(__file__)
        path = os.path.join(dir_path, 'hik_automation_run.bat')
        self._save_bat_file(path, cmd)

    @staticmethod
    def _save_bat_file(path, cmd):
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
    # args 2 select folder directory
    params = sys.argv
    for param in params:
        print("parameters => {}".format(param))

    caller = HIK_Automation_Caller()
    caller.main(params[1])


