---
name: character-show
description: Cenas com MAIS DE UM personagem e regras de jogo na Character Factory — invocador + invocados ensaiados, arena (magias e golpes num boneco de treino), rodada com vida (patrulha, o alvo morre e tomba, um invocado nasce do corpo, alvo novo sobe) — simuladas por regras no Blender ao vivo (o usuário filma) e espelhadas na Unity (CFTraining, CFWobble, CFSummoner, CFPath, CFRoundProbe). Use SEMPRE que o usuário pedir personagens contracenando ("ele invoca e os esqueletos atacam", "ataca o boneco", "anda de um lado para o outro e depois ataca", "quando o boneco morre nasce outro", "cena de treino", "mostra os dois juntos", "show", "rodada"), quando os personagens SUMIREM do show, quando o pé patinar numa curva ou numa chegada, ou ao levar uma dessas cenas para a Unity — inclusive uma BATALHA num cenário (dois personagens + invocados lutando com todas as animações e skills, rodadas que alternam o vencedor: CFBattleBuilder / CFBattle / CFUnit, Battle_Meadow). Inclui o LABORATÓRIO de teste da arena 1x1 (CFDuelLab, tecla L): Raio da Morte, botões de atacar / dano / andar / invocar, câmera lenta e quadro a quadro, vista do jogo 1:1 com silhueta e afinar as transições do Animator — use quando o usuário pedir "testar as animações", "raio da morte", "botões para disparar", "ver no tamanho do jogo".
---

# Shows e rodadas: personagens juntos, regras de jogo

Um show não anima nada novo: toda pose vem de um clipe aprovado. O que ele faz é ENSAIAR o contrato da engine no
viewport (quem dispara o quê, onde, em que quadro) para que o defeito apareça no Blender antes de aparecer no jogo.
Regras de operação: skill `character-factory`. Clipes de cada personagem: `character-clips`. Export/import:
`character-engine`. Exemplos: `characters/ocaso` (invocador), `characters/ossinho` (invocado), `characters/toco` (alvo).

| Script (`blender/`) | O que encena | Espelho na Unity |
|---|---|---|
| `summon_show.py --arg host=<HOST>` | o `summon` do hospedeiro + o `spawn` de cada unidade nos `landmarks.summon.points`, strips NLA | `CFSummoner` + `CFImporter.BuildShowcase` |
| `arena_show.py` | invoca, lança no alvo, unidades andam até o alvo e golpeiam — plano ESCRITO (`host_plan`, `walk_start`) | `CFImporter.BuildTraining` (versão sem vida) |
| `training_show.py` | rodada SIMULADA por regras: patrulha → invocação → magias/golpes → vida → morte → erguer → alvo novo | `CFTraining` (atual) |

Base comum: `showlib.py` (`stop`, `play`, `reveal`, `drop_show`, `compose`, `fillet_path`, `path_at`, `pin_root`,
`heading`). Leia o cabeçalho do script antes de passar argumentos — os padrões já são os aprovados.

## 1. Operar a cena `CF_Show`

- Tudo vive na cena `CF_Show` (coleções `CF_Show_Host` / `_Units` / `_Stage` / `_Target` / `_UI`); o personagem em
  trabalho fica intocado na cena principal. Modos: `build` (padrão; já toca) · `play` · `stop` · `off` · `remove`.
- **`--arg mode=off` antes de qualquer script da esteira** (`clip.sh`, sondas, renders): eles agem na cena do contexto.
- **`--arg mode=remove [--arg host_too=true]` antes de salvar o `.blend`**, senão o show (e o hospedeiro anexado)
  vai junto para o arquivo do personagem.
- **"Sumiram da tela"** → `--arg mode=play`. Ele chama `showlib.reveal`: o olho de uma coleção no Outliner
  (`layer_collection.hide_viewport` / `exclude`) esconde tudo dentro dela enquanto `obj.hide_get()` continua dizendo
  "visível" (2026-11-12: 7 de 34 objetos à vista, o show inteiro sumiu). Diagnóstico: `o.visible_get()` × `hide_get()`
  e as flags da coleção na view layer. Confira com `python3 cf/bl.py shot <png>` antes de dizer que voltou.
- Uma cena de show por vez: o `build` de qualquer um dos três apaga a `CF_Show` anterior e as coleções dela
  (`drop_show`; o `summon_show` também leva `_Target` / `_UI`), guardando só o hospedeiro anexado.
- O hospedeiro é ANEXADO do `.blend` dele, sem o `<HOST>_skeleton` de export nem o que ele deforma (um segundo cajado
  deitado no palco foi isso). A unidade é COPIADA por ponto: `obj.copy()` de um rig re-aponta o que é interno (IK,
  drivers); o que aponta de FORA (modificador de armadura, pai das malhas) se troca à mão (`showlib.remap`).
- Script que executa outro dentro dele (o `training_show` roda o `wobble.py`) lê o resultado em `cflib.last_out` e
  passa `"scene": show.name` — o filho tem de trabalhar na cena do show, não na do contexto.

## 2. Compor, não animar (`showlib.compose`)

- UMA ação assada por personagem, montada de itens `(ação, início, fase)`: loop dá a volta pelo período (n − 1), one-shot
  segura o último quadro, clipes consecutivos CRUZAM em `xf` = 5 quadros (quatérnios por nlerp). Corte seco estala: o
  1º quadro do andar está a 31 cm da pose-base na mão livre. Faixas NLA com `blend_in` misturam com a pose de REPOUSO
  na trilha de baixo — por isso uma ação composta, não strips (só o `summon_show` usa strips, sem mistura).
- **Depois de todo one-shot, ponha um item de idle**: sem isso a ação segura o último quadro congelado até o próximo
  clipe.
- `override(out, frames, plan)` é o gancho para editar quadro a quadro depois de compor (mover a coluna de runas).
- Plano escrito à mão (`arena_show`) serve para um ensaio de 10 s. Com regra de jogo (vida, morte, quem ataca quando),
  SIMULE (`training_show`): quadro a quadro, as mesmas regras do `CFTraining.cs`, e só então asse. Leia o JSON do
  resultado (`patrol`, `units`, `deaths`, `raises`, `life`, `wasted`, `target_falls`) — ele é o roteiro que a Unity
  tem de repetir.

## 3. Andar pelo chão sem patinar

- Andar no lugar + raiz arrastada só funciona em reta. Em curva o pé de apoio patina (0,7 cm/quadro num arco de 0,3 m)
  e uma unidade que chega e gira no lugar patina muito mais (65° em 6 quadros = 4,4 cm/quadro).
- **`pin_root(rig, scene, design, fa, fb, toes)`**: a cada quadro o pé plantado fica onde estava e a raiz vai aonde isso
  a põe (raiz = posição anterior − R(yaw)·dedo_local); o erro final (13,9 cm numa patrulha de 2,58 m) é espalhado pela
  caminhada → 0,03–0,07 cm/quadro em retas, curvas e paradas.
  - Pé plantado = o que MENOS anda no mundo sob a raiz planejada, NÃO o mais baixo: o manto arrasta os dois pés baixos,
    o pino pegou o pé em balanço e a raiz andou para trás (erro final 56 cm).
  - Leia a pose pelo depsgraph da cena do show: `rig.evaluated_get(scene.view_layers[0].depsgraph)`. `pose_bones` só
    atualiza na cena ATIVA do contexto — com a cena trocada no mesmo script as amostras congelaram (erro 85 cm). Objeto
    recém-posicionado: `matrix_basis` (sem pai), não `matrix_world` (espera o depsgraph).
- **Caminho** = `fillet_path(pontos, raio)`: retas + arcos de um raio só (a mesma construção do `CFPath.Fillet`).
  Estique-o para durar ciclos INTEIROS do andar e comece o andar na fase que o termina no quadro de saída que menos
  escorrega (`walk->idle best_frame` do manifesto de export; OCASO quadro 21): fase = (h_saída − 1 − n_andar) % período.
- **Chegada**: a última perna do caminho já aponta para o alvo (`fillet_path([P0, S − d·0,3, S], 0,25)`; na Unity o
  ponto intermediário `unitLead` 0,3) e a unidade NASCE virada para onde vai andar. Nada de girar no lugar.
- Unity: `CFCharacter.WalkPinStep` (ligado por padrão, `pinWhileWalking`, teto `walkPinMaxStep` 0,03 m) faz o mesmo
  pino em tempo real; `stopLead` 0,18 m porque o passo termina e o cruzamento carrega (sem ele a unidade parava
  0,16–0,24 m além e o cutelo entrava 17 cm no saco; com ele, 0,699 / 0,763 m do eixo para 0,70 pedidos).

## 4. O alvo: posição, molas, vida, queda

- **O alvo nasce do projétil**: eixo = alvo do projétil + a profundidade do disco pintado (TOCO a 2,79 m = 2,60 + 0,19).
  Um raio mirando o vazio a 3,2 m foi o que mostrou isso. O dano entra no quadro em que o projétil POUSA (o voo está na
  ação: `cf_fx_<fx>`; evento `land` no export), não no `hit` (no `hit` ele SAI).
- Molas que leem a 64 px: 2 Hz, amortecimento 0,13, teto 22° → magia 13,6° (o topo anda ~26 cm), raio ~8°, cutelo ~7°.
  O primeiro ajuste (pico 12, teto 16, 0,15) dava 8,5° = 2 px: "não foi atingido". Rig e molas: skill `character-rig` §4d.
- **Vida**: hp 16; magia 5, raio 3, cutelo 1 (padrões do `training_show` e do `CFTraining`). Com hp ≤ 0 nenhuma magia
  ou golpe NOVO começa (um golpe já no ar é contado em `wasted`).
- **Morte = corpo rígido tombando pela borda do pé** (`wobble.py` `life`, `CFWobble.Fall`): tabela por direção do
  `topple_fit.py` (rig §4d), φ'' = g L sen φ / (k² + L²), chute = 1,3 × o mínimo que passa da borda → TOCO: 25 quadros até o
  chão, 2 quiques (restituição 0,22). Portão: `lowest_mm_after_impact` ≤ 5 mm (deu 0,6).
- **Faixa de queda livre**: o alvo cai para longe de quem o matou; o invocador mata de frente, então o corpo cai ATRÁS
  (180°). Vagas `[65, −65, 125, −125]`. Com alguém em 180° o 2º corpo caiu em cima do esqueleto e o 3º nasceu 3 cm
  dentro dele (Unity, 3 mortes em 36 s).
- Barra de vida é UI, não personagem: dois quads, escala e cor de emissão chaveadas (verde ≥ 0,67, amarelo, vermelho
  < 0,34), escondida enquanto o alvo está caído, virada para a câmera (na Unity, para `Camera.main`).

## 4b. Corpo a corpo e explosão de morte (`melee_show.py`, FERRUGEM × TOCO)

- Onde a unidade PARA é medido: pontos da garra (grupos da mão/dedos) de cada evento contra o `collider` do alvo
  (`landmarks.collider`: raio por altura + caixas); grade distância × giro, mordida ≤ 45 mm. O teste de normal mais
  próxima do BVH deu profundidades absurdas (40 cm) em tábuas finas.
- Morte com bloco `"explosion"` no `death.clip.json` (raio, dano, `push_deg`, `squash`, `stun_s`): no evento, o alvo dentro
  do raio (medido do CENTROIDE do corpo no quadro anterior) toma dano, é empurrado para longe e fica ATORDOADO = o efeito
  `shock` do próprio alvo (seus landmarks, construído na cópia do show pelo `fx.py` com `scene=` e `frames=`) + trancos
  aleatórios de 3° a cada 2–3 quadros nas molas. `attacks_after 1` para ele sobreviver (4/16) e o stun aparecer.
- Um canal que UM clipe chaveia (a escala do `root` que esconde o corpo explodido), TODOS chaveiam: sem isso o show
  herdou o corpo sumido e não achou contato nenhum.
- Fora da cena do contexto, objeto E osso se leem pelo depsgraph da cena (`evaluated_get`): `matrix_world` do original
  ficou na origem e o centro da explosão saiu 0,8 m errado.
- Unity: `CFImporter.BuildMelee(hostDir, targetDir, standDistance, standTurnDeg, walkMeters)` → `<HOST>_Melee.unity` com
  `CFMelee` (anda no próprio rumo até o stand MEDIDO no Blender — FERRUGEM 1,17 m, giro 0 —, golpes nos eventos `hit` /
  `rake2`, alvo novo, `attacksAfter`, final dano + morte). A explosão é `CFExplosion` no prefab (do manifesto); o stun é
  `CFWobble.Stun` + `CFStunFx` (arcos procedurais aditivos sobre a superfície, mesma curva de nível do show).

## 5. Erguer um invocado do corpo (lê como necromancia)

1. O invocador toca a PRÓPRIA invocação de novo (`raise_delay` 18 quadros depois da queda).
2. A coluna de runas do 1º ponto vai para o corpo: offset de localização nos ossos `DEF-fx_rise_l_*`
   (+= R_repouso⁻¹·Δ, pelo `override`); a outra coluna fica em escala 0,001. Mova-a para onde a unidade SAI (`rises_at`
   = o corpo), não para a vaga final — a primeira versão errou isso.
3. UMA unidade sai do centro de massa do corpo (C = T + d·(r + (−r cos θ + h sen θ))), 3 cm dele no OCASO, e anda até
   a vaga livre mais próxima (0,85 m), com o caminho do §3.
4. O corpo afunda dentro da coluna (u^1,7 em 28 quadros, 1,25 m); o alvo novo sobe ((1 − u)^2,2 em 10 quadros, esticado 7 %
   na subida, squash 0,08 + aceno de 5° para a frente no pouso) com a vida cheia.
5. Anel cheio (4 vagas; só na Unity por enquanto): o invocado mais antigo desmorona (`CFSummoner.Dismiss`, clipe de morte)
   e o novo toma a vaga. Toda morte continua gerando um invocado.
- `after_respawn` 120: quadros mostrados com o alvo novo de pé — com menos, uma segunda morte começava antes do fim.

## 6. Câmera

- Rodada com patrulha lateral: **az 135°, el 32°** (alta, atrás do ombro esquerdo do hospedeiro, à la Clash Royale),
  distância = diagonal da caixa × 1,42, `view_shift` (−0,12, −0,12, −0,25): a patrulha atravessa a tela, o disco pintado
  olha para a câmera, o corpo caído e o esqueleto novo atrás do alvo ficam no quadro. De lado (az 88°) a patrulha vira
  profundidade — esse ângulo serve para o arco de um lob (`arena_show`).
- Título girado para a câmera (o `cflib.label` olha para −Y). Câmera atrás do alvo mostra o disco de costas.
- Unity (`BuildTraining`): centro = Lerp(hospedeiro, alvo, 0,62), atrás = (−frente − direita), distância 2,75 × vão,
  elevação 32°. A janela Game pode estar em retrato: capture por `RenderTexture` 1280×720.

## 7. Unity: a mesma rodada

`CFImporter.BuildTraining(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Training.unity` (objeto Training só com
Transform + `CFTraining`). Importe a unidade e o alvo ANTES do hospedeiro.
- `CFTraining` ([DefaultExecutionOrder(50)]): hospedeiro 0 parado → 1 perseguição pura no `CFPath` → 2 parando →
  3 vira para o alvo → 4 invoca → 5 luta/ergue; unidades 0 nascendo → 1 via e depois vaga → 2 parando → 3 golpeia enquanto
  `target.IsUp`. Contadores `Kills`, `Raised`, `Dismissed`, `UnitCount`.
- `CFWobble`: `Hit(push, pico, squash, dano)` devolve se morreu; `Fall`, `Sink`, `Rise`; eventos `Died(pos)`, `Landed`,
  `Risen`; a tabela de queda vem do manifesto (`wobble.topple`; o importador soma 180° ao ângulo do Blender).
- `CFSummoner.RaiseAt(pos, rot, fxSegundos)`: o PRÓXIMO evento de invocação ergue UMA unidade ali e leva a coluna do
  1º ponto (ossos `Fx*` agrupados por efeito e casados ao ponto pela posição de repouso). Nomes com serial (`R1`, `R2`…:
  todos saíam `R3`).
- **Prova = `CFRoundProbe`** (no objeto Training antes do Play, retire depois e salve a cena sem ele): eventos,
  escorregamento do pé de apoio em cm por 1/30 s por personagem, caminho do hospedeiro, capturas nos tempos pedidos →
  `characters/<id>/review/unity/round_probe.json`. OCASO, 48 s: 5 mortes, 4 erguidos, 61 acertos, para a 7 cm do ponto;
  pé de apoio 0,009 (hospedeiro) / ≤ 0,05 (unidades) cm por quadro, picos de 1–2,7 só em quadros isolados de transição.
- O Play avançou sem foco nesta máquina; se `Time.frameCount` não andar, `Application.runInBackground`. O `execute_code`
  compila C# 6.

## 8. Portões antes de mostrar ao usuário

| O quê | Número | Onde |
|---|---|---|
| pé de apoio enquanto anda (Blender) | ≤ 0,1 cm/quadro (0,03–0,07) | resultado do `pin_root` / do `training_show` |
| pé de apoio (Unity) | média ≤ 0,1 cm por 1/30 s; pico só em quadro de transição | `round_probe.json → slide_cm` |
| alvo depois do impacto | ≤ 5 mm abaixo do piso | `life.lowest_mm_after_impact` |
| ninguém na faixa de queda | 0 unidades a ±30° de 180° | vagas usadas |
| roteiro | mortes, erguidos, alvo de pé de novo antes do fim | JSON do resultado / eventos do probe |
| olho | folha de ~15 quadros da rodada + o viewport tocando | `review/work/training_round_sheet.jpg`, `bl.py shot` |

Feche com `state.json` do hospedeiro (`training_round`, com o que NÃO foi feito), uma linha no `docs/TECHNIQUES.md` por
lição nova, o show TOCANDO na tela e, se o arquivo vai ser salvo, `mode=remove` antes.

## 9. Batalha num cenário (Unity): dois personagens e o que um deles invoca

`CharacterFactory.EditorTools.CFBattleBuilder.Build("<PRIMEIRO>", "<SEGUNDO>")` (menu *Character Factory ▸ Build Battle
Meadow*) → `Assets/Scenes/Battle_Meadow.unity`: prado ORIGINAL pintado (textura procedural + arbustos, canteiro, pedras,
árvores em malhas geradas, shader `CharacterFactory/Foliage`), sol quente + ambiente trilight, câmera alta (52°, 10 m,
FOV 30) seguindo o centro da luta, e o objeto `Battle` com o `CFBattle`. Importe os três personagens antes (o invocado
antes do invocador).
- **Nada é digitado por personagem**: altura e raio saem do idle assado; o alcance do golpe é o ponto mais à frente de
  corpo + props em cada evento de acerto do clipe (o menor dá o alcance, a média dos ângulos dá o rumo); projéteis e
  invocação vêm do manifesto. O que é REGRA (vida, dano, cooldown) mora em `Tune` — balanço, não medida.
- **Regras** (`CFBattle`): alvo = inimigo mais perto a cada 0,5 s, mas quem está golpeando não larga o alvo; invocador
  avança 0,7 m, invoca sem invocados vivos, cooldown 11 s, inimigo a ≥ 1,5 m; dano ≥ `bigHit` interrompe ataque;
  invocados desmoronam com o mestre; explosão = dano + `Stun` + reação + empurrão no raio; corpos se afastam.
- **Rodadas que contam a história**: o vetor de vida do primeiro lado decide quem vence (`firstHealthByRound` 60 / 19:
  o brutamontes mata o invocador; enfraquecido, morre e explode). Confira que o efeito que você quer MOSTRAR acha o
  alvo vivo: com 26 a explosão matava o OCASO e o stun nunca aparecia.
- **Prova**: grave em Play com `Time.captureFramerate = 30` e um `EditorApplication.update` que renderiza `CFBattle.cam`
  numa RT 1280×720 por `Time.frameCount` novo, com um log a cada 15 quadros (vida, clipe, `IsStunned`, posição) e o
  `CFBattle.Log`. O Play recarrega o domínio: arme DEPOIS do Play e reinicie a rodada por reflexão (`_round = 0`,
  `NewRound`). Monte a folha dos momentos (entrada, invocação, golpes, morte, explosão, stun) e o mp4.
- Armadilhas desta cena (números em `docs/TECHNIQUES.md`): cor de vértice em projeto Linear (`.linear`); `Mathf.SmoothStep`
  não é borda; preenchimento de sombra só na passada base (luz pontual = quadrado); `Pow` de seno negativo = NaN.

### 9b. Times e cenário de kit (masmorra: ALVOR + FERRUGEM × OCASO + OSSINHOs + BRASA + GRANIZO)

`CFDungeonBuilder.Build()` (menu *Character Factory ▸ Build Battle Dungeon*) → `Assets/Scenes/Battle_Dungeon.unity`.
Tudo vem de `factory/env/dungeon/layout.json` (piso, poços, cada prop com posição / giro / escala / luz, paredes,
tipos de luz, nascimentos) e `pools.json` (contorno dos poços, escrito pelo `env/tools/dungeon_floor.py`). Mudou o layout?
Rode o gerador do piso ANTES do builder (o piso pinta os poços que o builder afunda).
- **Times** (`CFBattle.firstTeam` / `secondTeam`, `Entry` = prefab + perfil + nascimento + avanço): cada unidade nasce
  virada para o centro do outro time; por rodada, `first/secondTeamHealthScale` (vida) e `first/secondTeamDamageScale`
  (dano E cura); os invocados seguem a escala do lado deles. Com cura no time, escalar VIDA não alterna: a aura do ALVOR
  repunha ~18 de vida em 30 s e humanos ×0,45 contra mortos-vivos ×1,6 ainda deu "blue wins". Vida ×0,5 / ×1,3 + dano
  ×0,55 / ×1,5 alterna: rodada 1 azul em 31,4 s, rodada 2 vermelho em 25,2 s (o FERRUGEM explode no fim).
- Invocação em andamento quando o invocador morre: o 2º invocado chegava 0,03 s DEPOIS da morte e ficava vivo; agora
  desmorona em 0,45 s (`OnSummoned` confere o mestre).
- **Aura de cura** (`Profile.auraHeal / auraRadius / auraPeriod / auraColor`): cura aliados feridos no raio (anel + faíscas
  subindo, `CFBattleFx.HealRing / HealMotes`); sem ninguém ferido tenta de novo em 0,5 s.
- **Ritmo**: times a 11,7 m (FERRUGEM anda 0,26 m/s) gastavam 10 s só de caminhada e a rodada levava ~50 s; a 6,5 m e
  esqueletos de 5 de vida (com 8 o brutamontes ficava preso nas ondas de invocação), ~26 s.
- **Câmera da referência** (retrato, quase de cima): 68°, FOV 32, 44 m, `camFollowX` 0,2 (fica na linha da pista).
  Grave 720×1560 (`RenderTexture` retrato), não 1280×720.
- **Desníveis e ponte** (`layout.json → terrain`): fosso de gosma de parede a parede cruzado por uma raiz do Tripo, bordas
  e platôs elevados com escadas. O builder lê o topo da raiz pela PRÓPRIA malha (raycast) e monta o `CFGround` (grade de
  20 cm: altura + caminhável; A* de 8 vizinhos, sem cortar quina, degrau máx. 0,22 m; puxa o fio pelo `Line`). O `CFBattle`
  usa reta quando dá e `Steer` quando não dá; `Keep` desliza na borda; `Height` só soma células caminháveis.
- **5 heróis, 3 × 2**: BRASA e GRANIZO entram no lado da cripta (`TuneHammers`). Com `Time.captureFramerate = 30` a
  rodada é DETERMINÍSTICA (a rodada 3 repetiu a 1 quadro a quadro): calibre no editor e confie. Vida ×0,8 / dano ×0,85
  na cripta → azul vence a 1 em 46,9 s (ALVOR com 10/40); humanos ×0,85 / ×0,85 → vermelho vence a 2 em 38,5 s.
- **Batalha limpa** (pedido "muita cor chamativa"): o cenário é o palco, as minis são o show. Gosma escura com veio
  sutil (o brilho do veio era 0,43 linear no azul = manchas lilás em sRGB 0,68: emissão > albedo × luz numa cena escura);
  bloom só no que é quente (limiar 1,3, intensidade 0,3: as barras de vida estouravam); brilho dos props ÷ 3; luzes do
  fosso 1,7 → 0,55; cores de time azul × VERMELHO (magenta = a cor da gosma). Nada disso toca nos personagens.
- **Demo como jogo**: `CFDemoDirector` (intro, 5 câmeras, corte automático, HUD) + `CFDemoBuild.Build()` →
  `Builds/MasmorraDemo.app` (janela retrato 540×960 redimensionável, Retina, 14 s de build). O build falha em Play.
  Gravar COM o HUD: o app com `-cfrecord <dir> -cfseconds N` (`CFDemoRecorder`: `ScreenCapture` no fim do quadro pega
  o OnGUI; `Camera.Render` numa RenderTexture não pega).

### 9c. Arena de teste 1x1 (todos contra todos, em takes)

`CFDuelBuilder.Build()` (menu *Character Factory ▸ Build Duel Arena (1x1)*) → `Assets/Scenes/Duel_Arena.unity`: campo
verde plano (quadrado pintado de 40 m, anel gasto a 4,6 m, marcas de largada em ±2,6 m; mato só depois de 7,5 m, árvores
a 21–43 m), céu procedural, névoa linear. `CFBattle` em modo time com UMA entrada por lado + `CFDuelDirector`:
- roster e pares no componente (vazio = todos os pares); a fila põe o próximo par logo no `RoundOver` (o `NewTeamRound`
  lê `firstTeam/secondTeam` só quando a rodada começa); placar V/D, nocaute = câmera lenta 0,3 por 1,2 s + take Perto;
- takes 1 Jogo · 2 Lateral · 3/4 Ombro A/B · 5 Órbita · 6 Topo · 7 Perto · 8 Livre · 9 Retrato; teclas C, A (auto), N, R, Espaço, H, F, L (lab);
  `Cut(t)` / `TakeName` públicos para ferramentas; o eixo do duelo gira devagar e nunca vira mais de 110°;
- captura: `cam.Render` num RT de 1000 × 1000/aspect e `cam.ResetAspect()` depois; HUD só por `ScreenCapture`.
- Grama: meça o pixel renderizado (alvo ~ (99, 168, 75), sat 0,55) — luz + pós sobem R/G ×1,3 sobre o albedo.
- **Sentir o golpe** (2026-11-14): todo acerto congela atacante e vítima (`hitStop` 0,06 s; `killStop` 0,13 s na morte;
  magia só o alvo) e manda `CFBattle.Struck` → tremor angular 0,35–0,9° (1,5° na morte) + soco de FOV. Detalhes e a
  prova por conta na skill `character-engine` §2e.
- **Take 9 Retrato** (o close de personalidade): depois da câmera lenta do nocaute o diretor corta para o vencedor, que
  vira para a câmera e inclina `portraitTilt` 7° para trás em torno dos pés (fov 28, pitch 10, rosto no terço superior,
  barra de vida dele escondida); toca `victory` / `celebrate` / `cheer` se o personagem tiver. O cartão VITÓRIA desceu
  para o terço inferior (faixa central de 56 % da largura, filete na cor do vencedor) — nunca cobre o rosto.
  Captura de referência: `env/duel/shots/lab/retrato_alvor_s.jpg`.
- Invocados variam (`varySquad`): os OSSINHOs de uma invocação nascem com ritmo e tamanho próprios (×1,04 / 0,97 e
  ×0,98 / 1,05).

### 9d. Laboratório de teste (`CFDuelLab`, tecla L) — o "Raio da Morte" e cada animação num botão

O teste rápido na engine: as regras do duelo param (`CFBattle.hold`: sem IA, sem fim de rodada; os relógios das ações
continuam) e o par da arena vira bancada. Mesmo objeto `Duels` da cena (o `CFDuelBuilder` já põe o componente).
Fora do lab há um botão "LAB (L)" no canto inferior direito.

| Onde | Botão / tecla | O que faz |
|---|---|---|
| painel A / B | **Atacar** (T = A, Y = B) | o próximo clipe de ataque do herói, virado pelo rumo do golpe medido, no outro herói (fora do alcance o corpo a corpo erra, como no jogo) |
| | **Dano** | o herói leva um golpe sem dano: faísca, hit-stop, clipe `hit`, tremor da câmera |
| | **RAIO DA MORTE** (K = no B) | feixe do céu + anel no chão + faísca 1,8×; morre NA HORA, de qualquer estado (em pé, andando, no meio do ataque) — a morte de qualquer clipe sem precisar de uma luta. O corpo fica 2,5 s na pose final antes de afundar |
| | **Andar / Parar** | o andar NO LUGAR (esteira: o pino do pé é desligado para ninguém sair da marca), o herói e os invocados dele juntos — onde a variação do bando aparece; Parar usa a parada no pé certo |
| | **Invocar** | o clipe de invocação (só quem tem `summonClip`) |
| barra | **< Par / Par >**, **Reviver** | troca de par / renasce o par atual nas marcas |
| | **Encostar / Afastar** | à distância de golpe (o MENOR alcance de corpo a corpo do par: os dois golpes acertam) / às marcas (±2,6 m) |
| | **Lateral / Jogo / Retrato** | takes do diretor (Lateral é o padrão do lab) |
| | **G Jogo 1:1** | a vista do JOGO num telefone 360 × 640 px desenhada em pixels reais à direita: câmera 55°, fov 38, distância resolvida para 1,4 m = 64 px no centro (12,1 m), régua de 64 px, e a altura na tela de cada herói MEDIDA (render de silhueta só dele, caixa dos pixels escuros) |
| | **V Silhueta** | a mesma vista em silhuetas chapadas (efeitos e UI fora: shader de substituição `CharacterFactory/Silhouette`, unidades na camada 30) |
| | **Transicoes** (editor) | os 6 tempos de blend do Animator do herói A ou B, Aplicar ao vivo / Salvar JSON (skill `character-engine` §2e) |
| | **tempo** 1x · 1/2 · 1/4 · 1/10 · Pausa (Espaço) · **+1 quadro** (.) | +1 quadro = 1/30 s de jogo e pausa de novo |
| | **hit-stop −/+**, **morte −/+** | 20 ms por clique |

O leitor de cada herói mostra estado, clipe e quadro (`attack 25/58`, 1-based como no Blender), a transição em curso
(`-> hit 63%`), `[HIT-STOP]` enquanto congelado e, com G ligado, `na tela do jogo: L × A px`.

**Roteiro por personagem novo** (o pacote de revisão leva as capturas, skill `character-review` §0):
1. Encostar → velocidade 1/10 → Atacar → `+1 quadro` até `[HIT-STOP]`: o quadro congelado TEM de ser a pose de contato.
   Repita do outro lado (a vítima segura a pose de contato dela também).
2. 1x: Atacar e Dano algumas vezes — o golpe "pesa"? Ajuste hit-stop −/+ e anote se o personagem pede outro valor.
3. Raio da morte em pé, andando (Andar → Raio) e no meio do ataque (Atacar → Raio no quadro do preparo): a morte
   começa limpa dos três estados (a transição de 0,06–0,15 s não pode estalar).
4. Andar / Parar 5× seguidas: para no pé certo, sem deslizar (a esteira não move a unidade; o que andar é patinação).
5. Invocar 2–3× e Andar: os invocados em fases diferentes depois de 2 s.
6. G e V: altura na tela, a silhueta parada e nas poses-chave (pause no preparo, no contato, no chão). Compare com
   ALVOR 113 × 123 px / OCASO 97 × 88 / FERRUGEM 72.
7. Retrato: rosto no terço superior, nada na frente.
8. Transições: só se algo estalou ou arrastou em 3/4 — Aplicar, conferir, Salvar JSON, reimportar, `MeasureTransitions`.

**Por script** (`execute_code`, em Play): `var lab = Object.FindObjectOfType<CharacterFactory.CFDuelLab>();` →
`lab.SetOn(true)`, `Attack(lado)`, `Hit(lado)`, `Ray(lado)`, `Summon(lado)`, `Walk(lado)`, `Close(bool)`, `Revive()`,
`Pair(±1)`, `SetSpeed(v)`, `Pause()`, `Step()`, `SetInset(bool)`, `SetSilhouette(bool)`, `TuneApply(lado, tune)`,
`TuneSave(lado, tune)`; leitura: `lab.battle.LabState(lado)`, `lab.HeroPx[lado]`, `lab.HeroWidthPx[lado]`,
`lab.CamDistance`, `lab.director.PairName`. O `PairName` só atualiza no `Update` seguinte; e o par pode já ter avançado
quando o lab liga (o duelo anterior acabou entre duas chamadas): confira o par antes de agir.
- `Restart()` recomeça a contagem de rodadas em 1: o diretor zera `_seenRound` em `Next/Prev/Repeat`, senão o duelo
  novo não é visto como novo (nomes e placar errados).
- Captura com o painel e o inset: `ScreenCapture.CaptureScreenshot` (o inset é uma câmera com viewport, sai na captura
  de tela; num RT da câmera principal NÃO sai).

## Caçador com dash contra o boneco (UIVO + TOCO)

`CFImporter.BuildHunt("Assets/Characters/<HOST>", "Assets/Characters/TOCO")` → `Assets/Scenes/<HOST>_Hunt.unity` com
`CFHunt`: parado → corrida → galope → DASH (o personagem conduz: `PlayDash` / `DashStep`) que pousa ao alcance → mordidas
(hit-stop 0,06 s) → rodada ímpar: o boneco cai, VITÓRIA, afunda e outro sobe; rodada par: um ataque, DANO e MORTE. Os oito
clipes aparecem em ~19 s, com legenda do clipe na tela (`captions`, pt-BR) e câmera lateral que acompanha. A posição do
boneco é medida (skill `character-engine` §2f). Para gravar: Play → `CFHunt.RestartFromTop()` + `CFFrameRecorder`
(60 fps fixos, captura da janela Game com a legenda) → `ffmpeg`. A cena da usuária aberta antes (se suja) vai para uma
cópia `<cena>_unsaved_<data>.unity` antes do `BuildHunt` — ele abre uma cena nova.
