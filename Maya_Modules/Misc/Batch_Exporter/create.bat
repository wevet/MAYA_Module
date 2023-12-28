
@echo off
set PYPATH=%~d0%~p0Create_Batch_Exporter.py
echo %PYPATH%
 
"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1
 
pause

