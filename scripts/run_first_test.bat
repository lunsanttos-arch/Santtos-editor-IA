@echo off
setlocal
cd /d "%~dp0.."

if "%~1"=="" (
  echo.
  echo Arraste um MP4 para cima deste arquivo .BAT
  echo ou execute: scripts\run_first_test.bat "C:\caminho\video.mp4"
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo Ambiente Python nao encontrado. Rode SETUP_WINDOWS.bat primeiro.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat
python scripts\transcribe.py "%~1" --model small --device cpu || goto :error
python scripts\build_basic_plan.py || goto :error
npm run studio
exit /b 0

:error
echo.
echo O teste falhou. Copie o erro e me mande.
pause
exit /b 1
