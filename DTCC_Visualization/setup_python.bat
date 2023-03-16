@echo off

set PLUGIN_PYTHON=%~dp0\Content\Python
pushd %PLUGIN_PYTHON%
set UNREAL_PATH=C:\Unreal\UE_5.0
set /p "UNREAL_PATH=Enter path to Unreal Engine or press ENTER for default [%UNREAL_PATH%] : "

%UNREAL_PATH%\Engine\Binaries\ThirdParty\Python3\Win64\python.exe -m pip install --target=%PLUGIN_PYTHON%\.thirdparty -r .\requirements.txt

echo Remember to enable the "Python Editor Script Plugin" for the current project.
pause