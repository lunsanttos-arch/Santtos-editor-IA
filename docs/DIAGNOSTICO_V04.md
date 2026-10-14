# Diagnóstico v0.4 e direção da v0.5.0-alpha

## Evidência disponível

Código importado do ZIP v0.4, schemas, scripts, prompts e composição Remotion
inspecionados. TypeScript e render sintético de 150 frames passaram na instalação.
Não há bruto de benchmark nem plano editorial real no pacote; não é possível
afirmar que a qualidade visual ou o posicionamento por gesto foram validados.

## Preservar

- Whisper/PyAV e timestamps de palavras (`transcribe.py`).
- Visual Director, extração de frames, placements e índices locais de assets.
- JSON como contrato entre Director/Editor/Reviewer e Remotion.
- Composição `SanttosReel`, render draft e revisão antes do final.
- Scripts Windows e pedidos visuais explícitos como requisito obrigatório.

## Refatorar incrementalmente

- `validate_visual_coverage.py` aceita qualquer motion perto do cue: um headline
  irrelevante pode satisfazer um pedido de logo. É necessário conferir o assunto
  e o asset esperado, inclusive em trechos repetidos do bruto.
- `validate_plan.py` verifica parte dos campos, mas não executa o JSON Schema;
  tempos não finitos e terminações além da timeline precisam reprovar.
- `SanttosReel.tsx` concentra componentes, tipografia e animações fixas. Separar
  estilo e componentes permite evolução sem trocar o plano v0.4.
- Zoom é interpolado linearmente. Aplicar easing e limites do preset.
- O render final não exige cobertura visual; toda saída deve passar pelo gate.
- O pipeline automatizado completo é `.bat`. Não afirmar suporte Linux integral.

## Novos módulos

Perfis/presets versionados, formatos escritos e seleção persistida; componentes
de captions/câmera/som; um gate de qualidade com testes de reprovação; workflow
de preview e exportação; registro da análise de referências com proveniência.

## Referência enviada

`Download.mp4`: 147,97 s, 576 × 1024. Leitura visual por quadros amostrados em
todo o intervalo; áudio não transcrito. A apresentação divide o fluxo em:

1. Formatos escritos uma vez (falado, mudo, narrado).
2. Roteiro convertido em plano JSON.
3. Remotion Studio para verificar e ajustar antes de exportar.
4. Um teste que reprova quebra de regras.

A referência mostra também verificações de ausência de imagens e de áudio.
São exemplos do vídeo, não medições comprovadas de eficácia nem regras que
devem ser impostas automaticamente a todo material SanTTos.

## Riscos e sequência

Manter o schema v0.4 e acrescentar a seleção de estilo fora do plano evita
invalidar respostas do Codex e projetos antigos. Presets precisam mudar o render,
não apenas o prompt. Gates não substituem revisão humana de estética ou gesto.
Evitar inferir rosto/caption/B-roll automaticamente a partir de medidas de corte.

Sequência: contratos e testes → perfis → componentes/câmera/som → prompts e
preview/render com gates → render comparativo. A aprovação estética com o bruto
original permanece pendente; a referência é um tutorial, não esse benchmark.

## Validação desta alpha

- 12 testes Python do gate e 3 testes da heurística de captions passaram.
- TypeScript passou; schema dos cinco presets verificado.
- Render sintético com logo, caption, callout, zoom e sound cue: 150 frames,
  540 × 960, áudio presente e decodificação completa sem erro.
- Um frame de cada um dos cinco presets renderizado; frame clean inspecionado.
- Render sem Visual Director reprovou antes de iniciar exportação.
- Planos e transcrição originais restaurados após o smoke.

Não foram executados o `.bat` no Windows, o agente autenticado sobre um bruto
real, o tracking de rosto/gesto ou uma comparação estética v0.4/v0.5. O pipeline
Whisper requer baixar um modelo na primeira transcrição; importar a biblioteca
não comprova que esse download ou a transcrição real funcionaram.
