@echo off
REM MayaのPythonパスを設定
set MAYA_PYTHON="C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe"

REM pipがインストールされているか確認し、なければインストール
%MAYA_PYTHON% -m ensurepip --upgrade

REM numpyをインストール
%MAYA_PYTHON% -m pip install numpy

echo numpy installation completed.
pause
