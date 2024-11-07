@echo off
rem Choose Directory Dialog and Run Animation_Job_Caller.py

rem Set PowerShell command for directory selection
for /f "usebackq delims=" %%I in (`powershell -command "Add-Type -AssemblyName System.windows.forms; $f = New-Object System.Windows.Forms.OpenFileDialog; $f.Filter = 'All Files (*.*)|*.*'; if($f.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK){$f.FileName}"`) do set "selected_file=%%I"

rem Check if a directory was selected
if "%selected_file%"=="" (
    echo +-------------------------------------------------------+
    echo No directory selected. Exiting...
    echo +-------------------------------------------------------+
    pause
    exit /b
) else (
    echo +-------------------------------------------------------+
    echo Selected directory: %selected_file%
    echo +-------------------------------------------------------+
)

rem Set the path to the Python script
set "PYPATH=%~dp0Animation_Job_Caller.py"
echo Running Animation Job Caller with directory: %selected_file%

rem Run the Python script using Maya's mayapy interpreter
"C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe" "%PYPATH%" "%selected_file%"

pause
exit
