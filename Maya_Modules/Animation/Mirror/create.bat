
@echo off

echo +===================================
echo select a mirror mode
echo 1 left to right mirror
echo 2 right to left mirror
echo 3 flip to frame
echo +===================================

set input_str=
set /p input_str=

IF "%input_str%"=="" goto :input_start

:input_conf
echo +-------------------------------------------------------+
echo  selected mode [%input_str%] right?
echo  y / n
echo +-------------------------------------------------------+
set conf_select=
set /p conf_select=

if "%conf_select%"== set conf_select=y
if /i not "%conf_select%"=="y"  goto :input_start

:input_end
echo +-------------------------------------------------------+
echo done Press any key.
echo +-------------------------------------------------------+

pause

rem echo %input_str%

set PYPATH=%~d0%~p0Animation_Mirror_Caller.py
echo %PYPATH%

"C:\Program Files\Autodesk\Maya2020\bin\mayapy.exe" %PYPATH% %1 %input_str%

pause

