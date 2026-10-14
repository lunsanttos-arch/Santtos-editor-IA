# Teste de posicionamento

`placement-only.mp4`: 4,8 segundos, sem áudio e sem captions.
Teste visual do logo acima da palma, sobre o bruto enviado pelo usuário.
Não é a edição final e não valida sincronismo com a fala.
Publicação autorizada pelo usuário para permitir visualização e download.

## Teste com tracking

`hand-tracking.mp4`: mesmo trecho (18,1–22,9 s do bruto), agora com trajetória
medida da palma. Sem áudio/captions. O logo acompanha a mão com suavização;
perdas curtas usam fluxo óptico e, quando não há alvo seguro, um fade.
A trajetória e o plano usados estão em `hand-motion-tracks.json` e
`hand-tracking-plan.json`. O formato desta comparação é `mudo`, preset
`santtos-clean`. O bruto completo não foi publicado.

Verificação: 144 frames H.264, 540×960, 4,8 s; decode integral sem erro. Foram
medidas 129 amostras na janela do logo: 101 por landmarks; 117 amostras ficaram
visíveis após fluxo óptico, suavização e margens de segurança. Esse índice mede
disponibilidade, não precisão contra anotação humana. Frames em todo o trecho
foram inspecionados. A perda breve no movimento mais próximo da borda permanece
uma limitação declarada, não um trecho com posição inventada.
