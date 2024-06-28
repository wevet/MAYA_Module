
rem choose directory command
@echo off

rem set folder=
rem set "psCommand="(new-object -COM 'Shell.Application').BrowseForFolder(0,'Please choose your SOURCE folder.',0x010,17).self.path""
rem for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I

rem echo selected  folder is : "%folder%"
rem pause


echo +-------------------------------------------------------+
echo please input directory
echo +-------------------------------------------------------+

set input_str=
set /p input_str=
pause


if "%input_str%"=="" (
    echo +-------------------------------------------------------+
    echo not input directory
    echo +-------------------------------------------------------+
    exit
) else (
    echo +-------------------------------------------------------+
    echo input directory %input_str%
    echo +-------------------------------------------------------+
    call :finalize
)

:finalize
@echo off
set PYPATH=%~d0%~p0HIK_Automation_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" %PYPATH% %1 %input_str%
 
pause
exit

