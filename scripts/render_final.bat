@echo off
setlocal
cd /d "%~dp0.."
call npm run check:edit || goto :error
call npm run typecheck || goto :error
call npm run render || goto :error
echo.
echo Render concluido: output\final.mp4
pause
exit /b 0
:error
echo.
echo Render falhou. Copie o erro e me mande.
pause
exit /b 1
