---
name: character-factory
description: Esteira completa da Character Factory — do personagem que o artista imaginou até o personagem rigado, animado (idle, andar, ataque, dano, morte) e importado na Unity, com tudo acontecendo ao vivo no Blender. Use SEMPRE que o usuário pedir um personagem novo ("cria outro personagem", "novo personagem na fábrica", "roda a esteira"), quiser retomar um personagem, ou pedir uma etapa sem dizer qual. Esta skill decide a ordem, os portões de cada estágio e manda para as outras (character-design, character-rig, character-clips, character-review, character-engine, character-show — personagens contracenando, invocador + invocados, alvo de treino, rodada com vida). Leia-a antes de qualquer trabalho em factory/. Também resume os 8 princípios de JOGO (leitura na câmera de jogo, essência, estilo × escala, close, variação de bando, timing do golpe, rig simples, bancada de teste com Raio da Morte) e manda para onde cada um está detalhado.
---

# Character Factory — a esteira

O artista descreve um personagem; a fábrica entrega o personagem rigado, com cinco clipes, medido e dentro da engine.
Tudo passa pelo Blender aberto (o usuário **filma** a tela), então cada estágio precisa aparecer no viewport.

- Código e manual: `factory/README.md` (tabela de ferramentas + contrato do `clip.json`), `factory/docs/TECHNIQUES.md`
  (cada lição com o número que a provou). Leia o trecho do estágio em que você está — não o arquivo todo.
- Um personagem = `factory/characters/<id>/` com `brief.md`, `refs/`, `model/`, `rig/landmarks.json`, `anim/*.clip.json`,
  `mocap/`, `review/`, `export/`, `state.json`. `<id>` minúsculo, `<NAME>` = o mesmo em maiúsculas (nome dos objetos).
- Exemplos completos para copiar: `characters/brasa/` (anão, martelo), `characters/granizo/` (ogro, marreta de gelo) e
  `characters/alvor/` (paladino: espada de UMA mão, escudo segurado, aura de cura, todos os clipes autorais + Mixamo
  lido como referência),
  `characters/ocaso/` + `characters/ossinho/` (necromante de manto que NÃO é humanoide + o esqueleto que ele invoca:
  cajado plantado, unidade que sai do chão, magia com projétil) e `characters/toco/` (boneco de treino: prop que
  balança, morre tombando e renasce — não é personagem, não tem Rigify) e `characters/uivo/` (o primeiro QUADRÚPEDE: lobo, rig de lobo do Rigify enxuto, meio-galope e dash no tempo do vídeo do usuário, galope, bote com sacudida, uivo sentado; `quad_build.sh`).

## A ordem, e o portão de saída de cada estágio

Só passe adiante com o portão medido. Quase todo retrabalho do primeiro personagem veio de descobrir no estágio 6 um
problema que o estágio 1 ou 3 mostrava em segundos.

| # | Estágio | Skill | Portão de saída (número, não impressão) |
|---|---|---|---|
| 1 | Brief + desenho que cabe na animação E lê no jogo | `character-design` | brief de uma página com Essência (1–2 traços), Leitura e Close; silhueta a 64 px conferida; regras de geração; marcador esquerda/direita |
| 2 | Concept em T-pose (BOCA ABERTA) + modelo 3D + **Remesh 60k → Smart UV → Textura** no Tripo + props separados | `character-design` §3 6b–6c | T-pose real, mãos vazias, mandíbula aberta, props fora do corpo; `model/<id>_hi.glb` + `model/<id>_game.glb` (UV limpo); até 5.000 créditos Tripo por personagem |
| 3 | Import, malha de jogo, landmarks, **portões do modelo** | `character-rig` | `model_gates.py`: `overhead`, `corridor` ≥ 1 (e `wrap` depois do rig) |
| 4 | Rig (Rigify), pesos, props, teste de pose | `character-rig` | `pose_test.py` + close-ups de ombro/punho/quadril limpos; `fist_fit` lido; com dedos separados, `hand_test.py` olhado de perto |
| 5 | Pose-base + ataque | `character-clips` | ataque fecha sem `twist_jumps`; `contact_probe` sem penetração |
| 6 | Idle, andar, dano, morte sobre a pose-base | `character-clips` | cinco clipes começam na mesma pose (≤ 1 mm); `./contacts.sh`: contato E chão limpos nos cinco |
| 7 | Pacote de evidências + críticos | `character-review` | nota ponderada e lista de correções; ou o "está bom" do usuário |
| 8 | Export + Unity | `character-engine` | ida e volta do FBX ≤ 0,05 cm; import `ok=True problems=[]`; transições medidas |
| 9 | (se houver) personagens juntos: invocação, alvo, rodada | `character-show` | show tocando no viewport; pé de apoio ≤ 0,1 cm/quadro em curva; alvo ≤ 5 mm no chão; o mesmo roteiro medido na Unity (`CFRoundProbe`) |
| 10 | Laboratório na Unity: a unidade no tamanho e na câmera de jogo, contra os outros | `character-show` §9d | roteiro do `CFDuelLab` rodado: quadro do hit-stop = contato, morte limpa de 3 estados, altura na tela + silhueta 1:1, Retrato; blends salvos em `<NAME>.blend_tune.json` se mudaram |

O olho do usuário é o portão final: quando ele disser que o personagem está aprovado, pare de iterar com críticos e
registre isso no `state.json`. A nota dos críticos serve para achar defeitos, não para discutir com quem aprovou.

## Os 8 princípios de JOGO (o que o jogador vê — valem em todo estágio)

Os portões acima dizem que o personagem está CERTO; estes dizem que ele FUNCIONA num jogo mobile visto de cima a ~64 px.
São do usuário ("hyper importantes", 2026-11-14) e cada um tem regra com número na skill do estágio:

| # | Princípio | A regra, curta | Onde está detalhado | Como se prova |
|---|---|---|---|---|
| 1 | **Leitura primeiro** | um relance = quem é + o que faz; silhueta clara, poses exageradas, movimentos largos; julgar SEMPRE na câmera de jogo no tamanho de jogo (1,4 m = 64 px, 1 px ≈ 2,2 cm), nunca num close do Blender | `character-design` §0a · `character-clips` §6b · `character-review` §0 | laboratório G + V (altura na tela medida, silhueta 1:1); relance cego dos críticos |
| 2 | **Essência amplificada** | pesquisar quem é, reduzir a 1–2 traços (adjetivo + verbo), empurrar até lerem; uma ideia forte > muitos detalhes | `character-design` §0b · `character-clips` §6b | seção Essência + tabela traço × clipe no brief; crítico responde "o traço aparece?" por clipe |
| 3 | **Estilo na escala** | boneco de ação em miniatura: formas simples e grossas, proporção ousada, 3–4 cores + 1 destaque, nada < 2 px (≈ 4–5 cm) carregando identidade | `character-design` §0c | silhueta e valores no concept a 64 px antes do Tripo |
| 4 | **Close = personalidade** | desbloqueio, vitória, menu: a unidade vira para a câmera e inclina ~7° para cima/trás; rosto grande e livre; expressão por momento | `character-design` §0d · `character-clips` §6b (`victory`) · `character-show` §9c (take Retrato) | Retrato depois de um nocaute (`env/duel/shots/lab/retrato_alvor_s.jpg`) |
| 5 | **Pequenas variações** | bando não anda em passo: a engine varia ritmo ×0,92–1,08 e tamanho ×0,95–1,05 por unidade; o truque inteiro são 2–3 andares por unidade de bando | `character-clips` §6b · `character-engine` §2e | laboratório: Invocar 2–3× + Andar; fases diferentes em 2 s |
| 6 | **O tempo vende o golpe** | golpe curto, quadro de contato claro, segurar no impacto (clipe 2–3 quadros + engine 0,06 s / 0,13 s na morte), faísca + tremor + soco de FOV no mesmo quadro | `character-clips` §6b · `character-engine` §2e | laboratório 1/10 + `+1 quadro`: o quadro do `[HIT-STOP]` é a pose de contato |
| 7 | **Rig simples, de mobile** | esqueleto limpo: base 30, dedos ≤ 8, ≤ 10 ossos de personagem (orelha, cauda, capa, barba, corrente), deformação ≤ 50; efeito de uma vez não mora no esqueleto | `character-rig` §0 | chave `bones` do manifesto + contagem no prefab da Unity |
| 8 | **Bancada de teste rápida** | um mapa com "Raio da Morte" e botões para nascer, atacar, tomar dano e morrer; blends do Animator afinados NO MOTOR e salvos por personagem | `character-show` §9d (`CFDuelLab`) · `character-engine` §2e (`CFBlendTune`) | roteiro de 8 passos do laboratório rodado, capturas no pacote |

Personagem novo: o brief já sai com Essência, Leitura e Close (estágio 1); o estágio 10 abaixo fecha com o
laboratório. Personagem aprovado antes destes princípios não se refaz por conta própria: o que ele não cumpre vira
item no `state.json` (`game_principles`), dito ao usuário com o número (ex.: BRASA / GRANIZO acertam a 1,30 s, 23
quadros do ápice ao contato; FERRUGEM carrega 103 ossos de efeito).

## Regras de operação (valem em todas as skills)

- **Sempre `cd factory` antes de um comando** — o diretório de trabalho escorrega entre chamadas.
- **Blender**: 4.5 LTS aberto com o addon *MCP for Blender* (socket 127.0.0.1:9876). Tudo vai por
  `python3 cf/bl.py run blender/<script>.py --arg k=v` (ou `bl.py code "<py>"`). Se o Blender cair:
  `open -a ~/Applications/Blender-4.5.12-LTS.app <arquivo.blend>`; o socket volta sozinho em ~3 s.
- **Nunca `raise SystemExit` num script que roda no Blender ao vivo**: o addon só captura `Exception` e o Blender
  fecha no meio da filmagem. Termine com `cflib.out(...)` dentro de `if/else`.
- **Mostre o estágio**: `blender/board.py --arg title="..."` troca o letreiro; ao fim de um bloco de trabalho deixe o
  resultado tocando (`blender/play.py --arg name=<NAME> --arg action=<NAME>_<clip> --arg mode=play`, ou o reel).
  Pare a reprodução (`mode=stop`) antes de sondas e renders.
- **Fato do personagem vem do repouso** (`mesh.vertices`), nunca de `bound_box` (é a malha posada no quadro atual).
- **Olhe antes de afirmar**: close-up de vários lados e vários quadros (`blender/closeup.py` + `cf/sheet.py`) antes de
  dizer que algo está limpo. O usuário reclama do que vê no viewport, não do que a métrica diz.
- **Segredos**: `RUNWARE_API_KEY` só em `.env` na raiz (fora do git). Nada de nome, e-mail ou projeto do usuário em
  requisição para serviço externo. Não fazer commit sem pedido.
- **zsh**: um glob sem correspondência aborta o comando inteiro (`rm -f a/*.x b/*.y` pode não rodar nada).
- **Agentes críticos são somente leitura** (não rodam Blender nem scripts da esteira): a sessão está sendo filmada e um
  segundo processo mexendo na cena estraga a tomada.

## Trocar de personagem na sessão viva (o que já deu errado)

- **Script destrutivo não tem ensaio se o cabeçalho não diz**: `reset_character.py --arg dry=true` (flag inventada)
  apagou os 99 objetos da cena. Leia o cabeçalho; use `--arg backup=<arquivo>`.
- **Confira `bpy.data.filepath` depois do reset**: a sessão continuou apontando para o `.blend` do personagem anterior
  com o novo dentro — um Ctrl+S o sobrescreveria. Logo depois do import: `save_as_mainfile(filepath=<novo>, copy=False)`.
- **Abrir o `.blend` de outro personagem na sessão viva** (sem fechar o Blender que está sendo filmado): salve o atual e
  agende `bpy.ops.wm.open_mainfile(filepath=…)` com `bpy.app.timers.register(fn, first_interval=1.0)` dentro de
  `temp_override(window=…)` — nunca direto no `bl.py code` (a resposta do socket morre com o contexto). O servidor do
  addon sobrevive à carga; sonde `bpy.data.filepath` até mudar (< 4 s nos arquivos de 450 MB).
- **Personagens juntos** (invocador + invocados, alvo, rodada) vão para a cena própria `CF_Show` (skill `character-show`):
  enquanto ela está na tela nenhum script da esteira roda (`--arg mode=off` volta para a cena do personagem);
  `--arg mode=remove` antes de salvar o `.blend`; "sumiram da tela" = `--arg mode=play` (religa o olho das coleções).

## Estado e memória da fábrica

- Ao fechar um estágio, atualize `characters/<id>/state.json` (`updated`, o que foi feito, números do portão, `next`).
  É por ele que uma sessão nova retoma o trabalho.
- Lição nova (algo que custou mais de uma tentativa) vai para `docs/TECHNIQUES.md` com o **número medido** e a regra;
  se a lição muda como se desenha, rig-a ou anima o próximo personagem, atualize também a skill do estágio.
- Parâmetro que mora na pose-base ou no rig (`rig/landmarks.json`: `weapon.grip`, `grip`, `keepclear`, proporções)
  se propaga para TODOS os clipes: mudou, reconstrua os cinco (ataque primeiro) e meça os cinco.

## Como reportar

Status curto em pt-BR a cada bloco: o que mudou, o número que prova, o que falta. Limite que é do modelo (não da
animação) é dito como limite, com a medida — e vira regra de desenho para o próximo personagem.

## Segundo personagem em diante

1. Um `.blend` por personagem (`characters/<id>/<id>.blend`); a cena viva guarda só o personagem em trabalho.
2. Brief → Tripo → `import_model.py` → `gameready.py` → **medir** (fatias, cores, `look_at.py`) → `landmarks.json` →
   `model_gates.py` → `proportions.py` se precisar → `./rebuild_rig.sh`.
3. `cf/port_clip.py` de um personagem aprovado → `limb_radii.py` → `./build.sh` / `./look.sh` / `./contacts.sh` por clipe.
4. `reel.py` + `play.py` (o usuário filma) → `lod.py` → `export.py` → `cf/to_unity.py` → importador da Unity.

O segundo personagem (GRANIZO, ogro de gelo com marreta) foi do brief à Unity com os cinco clipes numa sessão. Tudo
que travou virou dado nos landmarks ou argumento de script — nenhum nome de personagem no código. Se um script citar
`beard`, `backpack` ou `BRASA` fora de um comentário, generalize antes de contornar.
