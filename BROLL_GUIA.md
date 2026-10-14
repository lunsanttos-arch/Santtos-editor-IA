# B-roll na v0.3

A pasta `public/broll` funciona como a biblioteca local do Reel.

1. Coloque nela imagens e videos antes de rodar `scripts/run_ai_edit.bat`.
2. A etapa `index_broll.py` cria `data/broll-index.json`.
3. O Codex pode escolher um arquivo somente se ele aparecer nesse indice.
4. Videos de B-roll sao reproduzidos sem audio, mantendo a fala original.
5. Se nao houver asset adequado, o agente pode usar `graphic` (card animado) ou simplesmente nao inserir B-roll.

Dica: nomes descritivos ajudam bastante, por exemplo `premiere_timeline.png`, `porto_alegre_drone.mp4`, `whatsapp_tela.png`.
