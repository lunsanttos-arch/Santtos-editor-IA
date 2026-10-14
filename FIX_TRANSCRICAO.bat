@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  SANTTOS AI EDITOR - CORRECAO PYAV
 echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo ERRO: ambiente .venv nao encontrado.
  echo Rode SETUP_WINDOWS.bat primeiro.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat

echo [1/3] Removendo PyAV incompatível...
python -m pip uninstall -y av
if errorlevel 1 goto :error

echo [2/3] Instalando PyAV 18.0.0...
python -m pip install --no-cache-dir av==18.0.0
if errorlevel 1 goto :error

echo [3/3] Conferindo versoes...
python -c "import av, faster_whisper; print('PyAV:', av.__version__); print('faster-whisper:', faster_whisper.__version__)"
if errorlevel 1 goto :error

echo.
echo ========================================
echo CORRECAO CONCLUIDA
 echo ========================================
echo Agora arraste o mesmo MP4 novamente para scripts\run_first_test.bat
pause
exit /b 0

:error
echo.
echo A correcao falhou. Copie o erro e me mande.
pause
exit /b 1
