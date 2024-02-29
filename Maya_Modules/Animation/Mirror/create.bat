
rem choose folder
@echo off
rem set "RootFolder="
rem set "Title=Please select a folder"
rem set dialog="about:<script language=vbscript>resizeTo 0,0:Sub window_onload():
rem set dialog=%dialog%Set Shell=CreateObject("Shell.Application"):
rem set dialog=%dialog%Set Env=CreateObject("WScript.Shell").Environment("Process"):
rem set dialog=%dialog%Set Folder=Shell.BrowseForFolder(0, Env("Title"), 1, Env("RootFolder")):
rem set dialog=%dialog%If Folder Is Nothing Then ret="" Else ret=Folder.Items.Item.Path End If:
rem set dialog=%dialog%CreateObject("Scripting.FileSystemObject").GetStandardStream(1).Write ret:
rem set dialog=%dialog%Close:End Sub</script><hta:application caption=no showintaskbar=no />"

rem set folder=
rem for /f "delims=" %%p in ('MSHTA.EXE %dialog%') do  set "folder=%%p"

rem set folder=
rem set "psCommand="(new-object -COM 'Shell.Application').BrowseForFolder(0,'Please choose your SOURCE folder.',0x010,17).self.path""
rem for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I


echo +-------------------------------------------------------+
echo please input directory
echo +-------------------------------------------------------+

set folder=
set /p folder=
pause

if "%folder%"=="" (
    echo +-------------------------------------------------------+
    echo not input directory
    echo +-------------------------------------------------------+
    exit

) else (
    call :select_mirror_mode
)

:select_mirror_mode
echo +-------------------------------------------------------+
echo select a mirror mode
echo 1 left to right mirror
echo 2 right to left mirror
echo 3 flip to frame
echo +-------------------------------------------------------+
set input_mirror_mode=
set /p input_mirror_mode=
pause

if "%input_mirror_mode%"=="" (
    echo +-------------------------------------------------------+
    echo not selected mirror mode
    echo +-------------------------------------------------------+
    exit
) else (
    echo +-------------------------------------------------------+
    echo selected mirror_mode %input_mirror_mode%
    call :select_mirror_axis
)

:select_mirror_axis
echo +-------------------------------------------------------+
echo select a mirror axis
echo 1 X
echo 2 Y
echo 3 Z
echo +-------------------------------------------------------+
set input_mirror_axis=
set /p input_mirror_axis=
pause

if "%input_mirror_axis%"=="" (
    echo +-------------------------------------------------------+
    echo not selected mirror axis
    echo +-------------------------------------------------------+
    exit
) else (
    echo +-------------------------------------------------------+
    echo selected mirror_axis %input_mirror_axis%
    call :finalize
)


:finalize
echo +-------------------------------------------------------+
set PYPATH=%~d0%~p0Animation_Mirror_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1 %folder% %input_mirror_mode% %input_mirror_axis%

pause
exit

