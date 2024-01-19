# -*- coding: utf-8 -*-

import sys
import os


K_MAYA_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\maya.exe'
K_MAYA_BATCH_EXE = r'C:\Program Files\Autodesk\Maya2020\bin\mayabatch.exe'


def main():
    source_directory = sys.argv[1]
    file_list = _get_list_directory_files(source_directory)

    path = os.getcwd()
    cmd = 'SET MAYA_UI_LANGUAGE=ja_JP' + '\n'
    #cmd += 'SET MAYA_PLUG_IN_PATH=C:dir'+'\n'
    #cmd += 'SET MAYA_MODULE_PATH=C:dir'+'\n'
    #cmd += 'SET MAYA_SCRIPT_PATH=C:dir'+'\n'
    cmd += 'SET PYTHONPATH=%s' % path + '\n'

    # logを入れるフォルダを作成
    _check_directory(os.path.join(source_directory, 'Log'))

    for file in file_list:
        replace_path = os.path.join(source_directory, file).replace('\\', '/')
        root, ext = os.path.splitext(replace_path)
        log_path = os.path.join(source_directory, 'Log', file).replace(ext, '.log')
        cmd += '\n'
        cmd += 'SET MAYA_CMD_FILE_OUTPUT={0}'.format(log_path) + '\n'
        cmd += '"{0}"'.format(K_MAYA_BATCH_EXE) + ' -command'
        cmd += ' "python(\\"import Batch_Exporter;Batch_Exporter.run(\'{}\')\\")"'.format(replace_path)

    dirPath, curPathName = os.path.split(source_directory)
    path = os.path.join(dirPath, 'batch_exporter_run.bat')
    save_bat_file(path, cmd)


def save_bat_file(path, cmd):
    with open(path, "w") as file:
        file.write(cmd)

def _check_directory(path):
    if os.path.isdir(path) is False:
        os.makedirs(path)

def _get_list_directory_files(directory_path):
    file_list = []
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        if os.path.isfile(file_path):
            file_list.append(file_name)
    return file_list


if __name__ == '__main__':
    main()


