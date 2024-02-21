
rem choose folder
@echo off
set "RootFolder="
set "Title=Please select a folder"

set dialog="about:<script language=vbscript>resizeTo 0,0:Sub window_onload():
set dialog=%dialog%Set Shell=CreateObject("Shell.Application"):
set dialog=%dialog%Set Env=CreateObject("WScript.Shell").Environment("Process"):
set dialog=%dialog%Set Folder=Shell.BrowseForFolder(0, Env("Title"), 1, Env("RootFolder")):
set dialog=%dialog%If Folder Is Nothing Then ret="" Else ret=Folder.Items.Item.Path End If:
set dialog=%dialog%CreateObject("Scripting.FileSystemObject").GetStandardStream(1).Write ret:
set dialog=%dialog%Close:End Sub</script><hta:application caption=no showintaskbar=no />"

set folder=
for /f "delims=" %%p in ('MSHTA.EXE %dialog%') do  set "folder=%%p"

echo +-------------------------------------------------------+
echo selected  folder is : "%folder%"

if "%folder%"=="" (
    echo +-------------------------------------------------------+
    echo folder is empty
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

set input_str=
set /p input_str=

pause

if "%input_str%"=="" (
    echo +-------------------------------------------------------+
    echo not selected mirror mode
    echo +-------------------------------------------------------+
) else (
    echo +-------------------------------------------------------+
    echo selected mirror_mode %input_str%
    call :finalize
)


:finalize
set PYPATH=%~d0%~p0Animation_Mirror_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1 %folder% %input_str%

pause
exit

