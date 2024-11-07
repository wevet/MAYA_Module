# -*- coding: utf-8 -*-

import sys
import os

K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe'

class Animation_Job_Caller:

    def __init__(self):
        self.source_directory = None
        self.file_list = []

    def main(self, new_source_directory):
        self.source_directory = new_source_directory
        self.file_list = self._get_list_directory_files()

        path = os.getcwd()
        cmd = 'SET MAYA_UI_LANGUAGE=ja_JP' + '\n'
        cmd += 'SET PYTHONPATH=%s' % path + '\n'

        # create log directory
        self._check_directory()

        for file in self.file_list:
            if file.endswith(".ma"):
                print(f"Execute the following ma file => {file}")
                replace_path = os.path.join(self.source_directory, file).replace('\\', '/')
                root, ext = os.path.splitext(replace_path)
                log_path = os.path.join(self.source_directory, 'Log', file).replace(ext, '.log')

                cmd += '\n'
                cmd += f'SET MAYA_CMD_FILE_OUTPUT={log_path}\n'
                cmd += f'"{K_MAYA_BATCH_EXE}" -file "{replace_path}" -command "python(\\"import Animation_Exporter;Animation_Exporter.run(\'{replace_path}\')\\")"'

        dir_path, current_path_name = os.path.split(__file__)
        batch_file_path = os.path.join(dir_path, 'animation_exporter_run.bat')
        self._save_bat_file(batch_file_path, cmd)
        print(f"Batch file created at: {batch_file_path}")

    @staticmethod
    def _save_bat_file(path, cmd):
        with open(path, "w") as file:
            file.write(cmd)

    def _check_directory(self):
        log_dir = os.path.join(self.source_directory, 'Log')
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)

    def _get_list_directory_files(self):
        return [f for f in os.listdir(self.source_directory) if os.path.isfile(os.path.join(self.source_directory, f))]


if __name__ == '__main__':
    # args: 1) Python file name 2) Folder directory
    params = sys.argv
    if len(params) > 1:
        caller = Animation_Job_Caller()
        caller.main(params[1])
    else:
        print("Please specify a directory containing Maya .ma files.")

