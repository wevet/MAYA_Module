
@echo off
set PYPATH=%~d0%~p0Batch_Exporter_Caller.py
echo %PYPATH%
 
"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1
 
pause

