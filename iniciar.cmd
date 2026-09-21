@echo off
setlocal
cd /d "%~dp0"
rem Ejecutar una comprobacion real: where tambien encuentra el alias de Microsoft Store.
py -3 -c "import sys, sqlite3; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 goto usar_py
python -c "import sys, sqlite3; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if not errorlevel 1 goto usar_python
set "RECURSO_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if not exist "%RECURSO_PYTHON%" goto sin_python
"%RECURSO_PYTHON%" -c "import sys, sqlite3; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>nul
if errorlevel 1 goto sin_python
echo Usando Python incluido en Codex.
echo Abre http://127.0.0.1:8000 y deja esta ventana abierta.
"%RECURSO_PYTHON%" server.py %*
goto fin
:usar_py
echo Abre http://127.0.0.1:8000 y deja esta ventana abierta.
py -3 server.py %*
goto fin
:usar_python
echo Abre http://127.0.0.1:8000 y deja esta ventana abierta.
python server.py %*
goto fin
:sin_python
echo No se encontro Python. Instala Python 3.10 o posterior y vuelve a iniciar.
:fin
pause
