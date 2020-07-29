@echo off
if NOT exist requirements.txt (
 echo No Requirements.txt found.
 EXIT /b 0
)
if NOT exist "$(PYTHON_EXT)/python.exe" (
 echo Python extension is not available. >&2
 EXIT /b 1
)
echo Installing dependencies
call "$(PYTHON_EXT)/python.exe" -m pip install -U pip
call "$(PYTHON_EXT)/python.exe" -m pip install wheel
call "$(PYTHON_EXT)/python.exe" -m pip install -U setuptools
if %errorlevel% NEQ 0 (
 echo Failed to install setuptools >&2
 EXIT /b 1
)
call "$(PYTHON_EXT)/python.exe" -m pip install -r requirements.txt
if %errorlevel% NEQ 0 (
 echo Failed to install dependencies>&2
 EXIT /b 1
)