
rem choose directory command
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

set folder=
set "psCommand="(new-object -COM 'Shell.Application').BrowseForFolder(0,'Please choose your SOURCE folder.',0x010,17).self.path""
for /f "usebackq delims=" %%I in (`powershell %psCommand%`) do set "folder=%%I
rem for /f "delims=" %%p in ('MSHTA.EXE %dialog%') do  set "folder=%%p"

echo selected  folder is : "%folder%"
pause


rem apply python
@echo off
set PYPATH=%~d0%~p0Batch_Exporter_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1 %folder%
 
pause


