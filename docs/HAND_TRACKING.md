# Tracking da palma no Remotion

O logo pode acompanhar uma mão medida ao longo do vídeo, em vez de ficar preso
ao x/y do primeiro frame. O schema do edit-plan v0.4 permanece inalterado.
`data/motion-tracks.json` é um sidecar opcional; vazio, preserva o render antigo.

## Gerar a trajetória

Use Python 3.12 para as dependências opcionais. MediaPipe 0.10.21 inclui os
modelos necessários e roda em CPU, sem baixar pesos do Hugging Face.

```sh
python -m pip install --only-binary=:all: -r requirements-tracking.txt
python scripts/track_hand.py --visual-at 18.4 --asset chatgpt-mark.svg
npm run check:edit
npm run typecheck
npm run render:review
```

`--visual-at` e `--asset` precisam identificar um item existente em `visuals`.
O tempo é da timeline final, não do bruto. Para a mão correta, ajuste
`--seed-x`/`--seed-y` (porcentagem do vídeo original). `--offset-y -19` mantém o
centro do logo acima da palma. `--input`, `--plan`, `--workflow` e `--output`
permitem trabalhar num benchmark separado sem substituir o projeto ativo.

O script mede landmarks da palma (0/5/9/13/17), associa a mão mais próxima da
anterior e usa fluxo óptico com checagem ida/volta e RANSAC para perdas curtas.
A suavização é simétrica em cinco frames; não acumula atraso. O tracker aplica
a mesma curva e limites de zoom do renderer, e mede o rosto para evitar sua
região. Quando perde o alvo, faz fade curto em vez de inventar uma trajetória.
Considera a área das captions conforme o formato selecionado.

O gate verifica hash do bruto, cortes, formato, intensidade da câmera, tempos,
visibilidade e vínculo com o visual. Mudar bruto, cortes, formato ou câmera exige
regenerar o tracking. Não reaproveite um arquivo de trajetória de outro vídeo.
O renderer interpola os pontos por frame. Sem trajetória para o item, mantém seu
x/y estático; com trajetória, esconde o item fora do intervalo medido.

## Benchmark real

Trecho do bruto enviado: 18,1–22,9 s (4,8 s), mesmo trecho do teste estático.
129 amostras na janela do logo: 101 detecções de landmarks; o restante utiliza
fluxo óptico curto ou perda declarada. O relatório gerado registra a cobertura
visível. Isso é uma medida de disponibilidade, não uma precisão comprovada por
anotação humana. O vídeo de entrega é `benchmarks/previews/hand-tracking.mp4`.
É um teste de movimento sem áudio/captions; não é a edição editorial completa.

## Limites

Mãos cortadas pelo quadro, oclusões longas e cruzamento de mãos ainda podem
causar perda. Nessas situações o logo desaparece gradualmente. Este módulo
rastreia a palma selecionada; não reconhece automaticamente qual dedo está
apontando nem a intenção de todos os gestos. A caixa de rosto é aproximada;
revisão dos frames renderizados continua necessária. O pipeline `.bat` não
escolhe automaticamente o alvo: gere o tracking depois do plano aprovado.

Os dados reais do benchmark ficam junto ao preview. Os planos ativos na raiz
continuam com os exemplos originais, e a trajetória ativa permanece vazia para
não aplicar movimentos de uma pessoa a outro projeto.
