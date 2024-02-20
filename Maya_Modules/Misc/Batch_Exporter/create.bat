
rem choose directory command
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
echo selected  folder is : "%folder%"
pause


rem apply python
@echo off
set PYPATH=%~d0%~p0Batch_Exporter_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1 %folder%
 
pause


