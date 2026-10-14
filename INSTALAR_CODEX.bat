@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo  INSTALAR / ABRIR CODEX CLI
echo ========================================
echo.

where codex >nul 2>nul && goto :login

echo Instalando Codex CLI pelo instalador oficial...
powershell -ExecutionPolicy ByPass -Command "irm https://chatgpt.com/codex/install.ps1 | iex"
if errorlevel 1 (
  echo.
  echo O instalador oficial falhou.
  echo Alternativa: npm install -g @openai/codex
  pause
  exit /b 1
)

:login
echo.
echo O Codex vai abrir. Escolha Sign in with ChatGPT se ainda nao estiver logado.
echo Depois pode fechar com Ctrl+C e usar scripts\run_ai_edit.bat.
echo.
codex
pause
