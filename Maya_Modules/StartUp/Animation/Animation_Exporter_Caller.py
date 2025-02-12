# -*- coding: utf-8 -*-

import sys
import os

K_MAYA_EXE = r'C:\Program Files\Autodesk\Maya2023\bin\maya.exe'
K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2023\bin\mayabatch.exe'

class Animation_Job_Caller:

    def __init__(self):
        self.source_directory = None
        self.file_list = []


    def main(self, new_source_directory):
        self.source_directory = new_source_directory
        self.file_list = self._get_list_directory_files()

        path = os.getcwd()
        cmd = self._generate_env_settings()
        cmd += 'set PYTHONPATH=%s' % path + '\n'

        # 統一したスクリプト呼び出し形式を設定
        ma_files = [os.path.join(self.source_directory, file).replace('\\', '/') for file in self.file_list if file.endswith(".ma")]
        if not ma_files:
            print("No .ma files found in the specified directory.")
            return

        # ファイルリストをそのまま渡すように変更
        file_list_string = ", ".join([f"'{file}'" for file in ma_files])
        cmd += f'"{K_MAYA_BATCH_EXE}" -command '
        cmd += f'"python(\\"import Animation_Exporter; '
        cmd += f'Animation_Exporter.run_outer([{file_list_string}])\\")"\n'

        cmd += 'pause\n'
        cmd += 'exit'

        dir_path, current_path_name = os.path.split(__file__)
        batch_file_path = os.path.join(dir_path, 'animation_exporter_run.bat')
        self._save_bat_file(batch_file_path, cmd)
        print(f"Batch file created at: {batch_file_path}")


    @staticmethod
    def _generate_env_settings():
        """
        バッチファイル用の環境変数設定を生成
        """
        env_settings = (
            ":: ENV\n"
            "set MGEAR_MODULE_PATH=C:/Users/waltz/Documents/Maya_Project/Scripts/mgear_4.2.2\n"
            "set MAYA_MODULE_PATH=%MGEAR_MODULE_PATH%;\n\n"            


            ":: SCRIPTS & PYTHONPATH\n"
            "set PYTHONPATH=C:/Users/waltz/Documents/MAYA_Module/Maya_Modules/StartUp\n"
            "set MAYA_SCRIPT_PATH=C:/Users/waltz/Documents/MAYA_Module/Maya_Modules/StartUp\n\n"
            
            ":: ENV\n"
            "set MAYA_UI_LANGUAGE=ja_JP\n\n"
        )
        return env_settings


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

