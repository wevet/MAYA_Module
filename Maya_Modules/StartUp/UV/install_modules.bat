@echo off
REM MayaのPythonパスを設定
set MAYA_PYTHON="C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe"

REM pipがインストールされているか確認し、なければインストール
echo Checking pip installation...
%MAYA_PYTHON% -m ensurepip --upgrade
if %ERRORLEVEL% neq 0 (
    echo Failed to install or upgrade pip.
    pause
    exit /b
)

REM pipを最新バージョンにアップグレード
echo Upgrading pip...
%MAYA_PYTHON% -m pip install --upgrade pip
if %ERRORLEVEL% neq 0 (
    echo Failed to upgrade pip.
    pause
    exit /b
)

REM numpy、Pillowをインストール
echo Installing required packages...
%MAYA_PYTHON% -m pip install numpy pillow
if %ERRORLEVEL% neq 0 (
    echo Failed to install required packages.
    pause
    exit /b
)

echo All packages installed successfully.
pause

