@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo  SANTTOS AI EDITOR - ATUALIZACAO v0.4
echo ==========================================
echo.
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente existente nao encontrado. Use o pacote completo e rode SETUP_WINDOWS.bat.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade "Pillow>=11" || goto :error
python scripts\index_brands.py || goto :error
call npm run typecheck
if errorlevel 1 goto :error
echo.
echo Atualizacao v0.4 concluida.
echo Agora arraste o bruto em scripts\run_ai_edit.bat
pause
exit /b 0
:error
echo.
echo Falha na atualizacao. Copie o erro e me mande.
pause
exit /b 1
