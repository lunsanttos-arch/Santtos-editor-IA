@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo  CORRECAO CODEX - SANTTOS AI EDITOR
 echo ========================================
echo.
echo Esta versao nao usa mais --full-auto.
echo Ela usa o Codex em modo READ-ONLY para analisar o projeto
echo e grava apenas a resposta final estruturada em data\agent-plan.json.
echo.
echo Versao do Codex instalada:
codex --version
if errorlevel 1 (
  echo.
  echo Codex nao encontrado. Rode INSTALAR_CODEX.bat.
  pause
  exit /b 1
)
echo.
echo Correcao pronta. Agora arraste o bruto para scripts\run_ai_edit.bat
pause
