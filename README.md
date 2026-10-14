# SanTTos AI Editor v0.4 — Visual Director

A v0.4 adiciona uma camada de direcao visual antes da edicao.

## O que mudou
1. O agente le a transcricao e cria `data/visual-cues.json`.
2. Cues explicitos como "aparece aqui", "mostra" e pedidos de logo recebem prioridade alta.
3. O sistema extrai frames do bruto nesses momentos.
4. Um segundo agente visual escolhe x/y/scale, inclusive para gesto `aqui/ali`.
5. O editor monta o Reel usando `visuals` alem de cuts, captions, motions e B-roll.
6. `validate_visual_coverage.py` reprova uma montagem que manteve um pedido visual HIGH sem mostrar nada.
7. Se isso acontecer, uma passada de reparo visual roda automaticamente.
8. A revisao final confere novamente a cobertura.

## Atualizando a partir da v0.3
Copie o conteudo do pacote update-only sobre sua pasta atual, substitua os arquivos e execute:

`ATUALIZAR_V04.bat`

Depois arraste o bruto para:

`scripts\run_ai_edit.bat`

## Benchmark do nosso teste
Quando a fala mantida disser algo equivalente a "quero que apareca aqui o logo do ChatGPT", a edicao deve inserir um elemento `visuals` type `brand` usando `chatgpt.svg`, idealmente proximo da regiao indicada pela mao.

## Assets
- B-roll: `public/broll`
- Marcas: `public/brands`

Os SVGs ChatGPT/OpenAI incluidos sao fallbacks locais do projeto e podem ser substituidos pelos assets oficiais usados na sua producao.

## Remotion: instalacao, preview e render

Veja [docs/REMOTION.md](docs/REMOTION.md) para executar o Studio, validar o plano e renderizar no Windows ou Linux. Use `npm ci` para instalar as versoes registradas em `package-lock.json`.
