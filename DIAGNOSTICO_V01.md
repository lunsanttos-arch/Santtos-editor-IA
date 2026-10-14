# Diagnostico da v0.1 a partir do primeiro render

O primeiro render provou que o pipeline funciona, mas tambem revelou que a logica editorial estava errada.

## Problemas encontrados

- `build_basic_plan.py` criava um corte sempre que encontrava silencio maior que 0.55 s.
- O mesmo script aplicava zoom 1.06 em todo terceiro segmento, independentemente da fala.
- As captions eram quebradas por quantidade fixa de 4 palavras, nao por unidade de sentido.
- Nao havia analise de gancho, repeticao, intencao, enfase ou narrativa.
- `overlays` estava vazio, portanto a edicao era praticamente corte + caption + zoom.

## Consequencia visual

O resultado parece automatizado: cortes e reenquadramentos entram por regra numerica, captions quebram frases em lugares ruins e nenhum elemento visual responde ao conteudo.

## Mudanca na v0.2

A logica mecanica deixa de comandar a montagem. O agente le a transcricao, decide a estrutura editorial e grava um plano que o Remotion apenas executa.
