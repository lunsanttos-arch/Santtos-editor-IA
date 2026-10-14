@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   SANTTOS AI EDITOR v0.4 - SETUP WINDOWS
 echo ========================================
echo.

where node >nul 2>nul || (
  echo ERRO: Node.js nao encontrado. Instale Node.js LTS e execute novamente.
  pause
  exit /b 1
)

where py >nul 2>nul || (
  echo ERRO: Python Launcher nao encontrado. Instale Python 3.14 x64.
  pause
  exit /b 1
)

py -3.14 --version >nul 2>nul || (
  echo ERRO: Python 3.14 nao encontrado.
  echo Instale Python 3.14 x64 e execute novamente.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/5] Criando ambiente Python 3.14...
  py -3.14 -m venv .venv
)
call .venv\Scripts\activate.bat

echo [2/5] Atualizando pip...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/5] Instalando dependencias Python compativeis...
python -m pip install --upgrade --force-reinstall -r requirements.txt
if errorlevel 1 goto :error

python -c "import av, faster_whisper; print('PyAV:', av.__version__); print('faster-whisper:', faster_whisper.__version__)"
if errorlevel 1 goto :error

echo [4/5] Instalando dependencias Remotion...
call npm ci
if errorlevel 1 goto :error

echo [5/5] Instalando skills oficiais do Remotion para agentes...
call npx -y skills@latest add remotion-dev/skills -g -y

echo.
echo ========================================
echo SETUP CONCLUIDO
 echo ========================================
echo Agora arraste um MP4 para scripts\run_ai_edit.bat
pause
exit /b 0

:error
echo.
echo A instalacao falhou. Copie o erro e me mande.
pause
exit /b 1
