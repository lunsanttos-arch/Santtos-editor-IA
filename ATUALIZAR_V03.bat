@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  SANTTOS AI EDITOR - ATUALIZAR PARA v0.3
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
  echo Ambiente .venv nao encontrado.
  echo Se esta e uma pasta nova, rode SETUP_WINDOWS.bat em vez deste atualizador.
  pause
  exit /b 1
)

call .venv\Scripts\activate.bat

echo [1/3] Instalando suporte aos frames de revisao...
python -m pip install "Pillow>=11.0.0,<13"
if errorlevel 1 goto :error

echo [2/3] Conferindo B-roll e scripts Python...
python scripts\index_broll.py
if errorlevel 1 goto :error
python -m py_compile scripts\apply_agent_plan.py scripts\extract_review_frames.py scripts\index_broll.py scripts\init_ai_plan.py scripts\transcribe.py scripts\validate_plan.py
if errorlevel 1 goto :error

echo [3/3] Conferindo dependencias do Remotion...
call npm install
if errorlevel 1 goto :error

echo.
echo ========================================
echo ATUALIZACAO v0.3 CONCLUIDA
echo ========================================
echo Agora arraste o bruto para scripts\run_ai_edit.bat
pause
exit /b 0

:error
echo.
echo A atualizacao falhou. Copie o erro e me mande.
pause
exit /b 1
