# Remotion no SanTTos AI Editor

O Remotion já é o motor de composição e render da v0.4. O ponto de entrada é
`src/index.ts`, que registra `src/Root.tsx`; a composição `SanttosReel` usa
`data/edit-plan.json` e `data/transcript.json`.

## Instalar e executar

Na raiz do projeto, com Node.js e npm disponíveis:

```sh
npm ci
npm run typecheck
npm run studio
```

Coloque o bruto em `public/input.mp4` antes do preview/render. O plano deve
referenciar intervalos existentes nesse vídeo. Assets locais ficam em
`public/brands` e `public/broll`.

```sh
python scripts/validate_plan.py
python scripts/validate_visual_coverage.py
npm run render:review
npm run render
```

O draft fica em `output/review/draft.mp4`; o final, em `output/final.mp4`.
O render exige Chrome/Chromium e suas dependências de sistema. Para usar um
Chromium já instalado no Linux:

```sh
npm run render:review -- --browser-executable=/usr/bin/chromium --concurrency=2
```

## Fluxo editorial existente

No Windows, `scripts/run_ai_edit.bat` recebe o caminho do bruto e coordena
Whisper → Visual Director → extração de frames → posicionamento → Editor →
auditoria de cobertura → draft Remotion → Reviewer → auditoria → Studio.
O fluxo completo também exige Python, FFmpeg, Codex CLI autenticado e as
dependências de `requirements.txt`. Os scripts `.bat` são específicos do Windows;
os comandos npm podem ser executados no Linux.

## Referência de fluxo pendente

Referência fornecida: https://vt.tiktok.com/ZSgJj1XYa/

O acesso ao link no ambiente retornou HTTP 403. Seu conteúdo ainda não foi
analisado. É necessário fornecer o MP4 para documentar e implementar o fluxo
mostrado sem inferir etapas a partir do link.
