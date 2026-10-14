@echo off
setlocal
cd /d "%~dp0.."

if "%~1"=="" (
  echo.
  echo Arraste o VIDEO BRUTO para cima deste arquivo:
  echo scripts\run_ai_edit.bat
  echo.
  pause
  exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente Python nao encontrado. Rode SETUP_WINDOWS.bat primeiro.
  pause
  exit /b 1
)
where codex >nul 2>nul || (
  echo Codex CLI nao encontrado. Rode INSTALAR_CODEX.bat e faca login primeiro.
  pause
  exit /b 1
)
call .venv\Scripts\activate.bat

echo ==============================================
echo  SANTTOS AI EDITOR v0.4 - VISUAL DIRECTOR
echo ==============================================
echo.

echo [1/14] Transcrevendo o bruto...
python scripts\transcribe.py "%~1" --model small --device cpu || goto :error

echo.
echo [2/14] Indexando assets locais...
python scripts\index_broll.py || goto :error
python scripts\index_brands.py || goto :error

echo.
echo [3/14] Visual Director: procurando oportunidades visuais...
if exist "data\visual-cues.raw.json" del /q "data\visual-cues.raw.json"
type prompts\visual_director.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\visual-cues.schema.json --output-last-message data\visual-cues.raw.json -
if errorlevel 1 goto :error
python scripts\apply_json_object.py --input data\visual-cues.raw.json --output data\visual-cues.json || goto :error

echo.
echo [4/14] Extraindo frames dos momentos visuais...
python scripts\extract_cue_frames.py || goto :error

echo.
echo [5/14] Visual Director: analisando gesto e posicao na tela...
if exist "data\visual-placements.raw.json" del /q "data\visual-placements.raw.json"
set /p CUE_IMAGES=<data\cue-images.txt
if not "%CUE_IMAGES%"=="" (
  type prompts\place_visuals.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\visual-placement.schema.json --output-last-message data\visual-placements.raw.json --image="%CUE_IMAGES%" -
  if errorlevel 1 (
    echo Posicionamento visual por imagem falhou. Usando posicoes seguras automaticas.
    echo {"placements":[]} > data\visual-placements.raw.json
  )
) else (
  echo {"placements":[]} > data\visual-placements.raw.json
)
python scripts\apply_json_object.py --input data\visual-placements.raw.json --output data\visual-placements.json || goto :error
python scripts\merge_visual_director.py || goto :error

echo.
echo [6/14] Criando plano neutro...
python scripts\init_ai_plan.py || goto :error

echo.
echo [7/14] Codex: primeira montagem editorial + visual...
if exist "data\agent-plan.json" del /q "data\agent-plan.json"
type prompts\edit_video.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\edit-plan.schema.json --output-last-message data\agent-plan.json -
if errorlevel 1 goto :error
python scripts\apply_agent_plan.py --input data\agent-plan.json || goto :error
python scripts\validate_plan.py || goto :error
call npm run typecheck || goto :error
copy /y data\edit-plan.json data\edit-plan.first-pass.json >nul

echo.
echo [8/14] Conferindo cobertura dos pedidos visuais...
python scripts\validate_visual_coverage.py
if errorlevel 2 (
  echo Tentando correcao automatica de cobertura visual...
  type prompts\repair_visuals.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\edit-plan.schema.json --output-last-message data\visual-repair-plan.json -
  if not errorlevel 1 (
    python scripts\apply_agent_plan.py --input data\visual-repair-plan.json || goto :error
    python scripts\validate_plan.py || goto :error
    python scripts\validate_visual_coverage.py || goto :error
    copy /y data\edit-plan.json data\edit-plan.first-pass.json >nul
  ) else (
    goto :error
  )
)

echo.
echo [9/14] Renderizando draft leve...
if not exist "output\review" mkdir "output\review"
call npm run render:review || goto :error

echo.
echo [10/14] Extraindo frames do draft...
python scripts\extract_review_frames.py --count 6 || goto :error

echo.
echo [11/14] Codex: revisao editorial + visual...
if exist "data\review-plan.json" del /q "data\review-plan.json"
set /p REVIEW_IMAGES=<data\review-images.txt
type prompts\review_video.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\edit-plan.schema.json --output-last-message data\review-plan.json --image="%REVIEW_IMAGES%" -
if errorlevel 1 (
  echo Revisao com imagens falhou. Tentando revisao textual...
  type prompts\review_video.txt | codex exec --skip-git-repo-check --sandbox read-only --output-schema schemas\edit-plan.schema.json --output-last-message data\review-plan.json -
  if errorlevel 1 goto :openpreview
)

echo.
echo [12/14] Aplicando e validando revisao...
python scripts\apply_agent_plan.py --input data\review-plan.json
if errorlevel 1 (
  copy /y data\edit-plan.first-pass.json data\edit-plan.json >nul
  goto :openpreview
)
python scripts\validate_plan.py
if errorlevel 1 (
  copy /y data\edit-plan.first-pass.json data\edit-plan.json >nul
  goto :openpreview
)
call npm run typecheck
if errorlevel 1 (
  copy /y data\edit-plan.first-pass.json data\edit-plan.json >nul
  goto :openpreview
)

echo.
echo [13/14] Auditoria final dos visual cues...
python scripts\validate_visual_coverage.py
if errorlevel 2 (
  echo Revisao removeu um visual obrigatorio. Restaurando primeira montagem validada.
  copy /y data\edit-plan.first-pass.json data\edit-plan.json >nul
)

:openpreview
echo.
echo [14/14] Abrindo preview final no Remotion Studio...
echo.
echo Teste-chave v0.4: pedidos como "aparece aqui o logo do ChatGPT" devem virar elemento visual real no ponto indicado.
call npm run studio
exit /b 0

:error
echo.
echo A execucao falhou. Copie o erro e me mande.
pause
exit /b 1
