---
name: character-rig
description: Do GLB gerado ao personagem rigado e sem deformação na Character Factory — import no Blender ao vivo, malha de jogo (60k + bake), landmarks, PORTÕES DO MODELO antes do rig, alongar/inclinar no modelo, Rigify + pesos por região, props em osso próprio, teste de pose e caça às deformações. Use quando houver um modelo novo para rigar, quando o usuário disser "rig", "pesos", "skinning", "ainda tem deformação", "o braço entra no corpo", "rasgo na axila", ou depois de qualquer mudança em rig/landmarks.json. Inclui o orçamento de ossos de mobile (base 30, dedos ≤ 8, osso extra só onde há personagem: orelha, cauda, capa, barba, corrente).
---

# Rig e deformação

Entrada: `characters/<id>/model/*.glb` (corpo em T-pose + um GLB por prop). Saída: `<NAME>` + `<NAME>_rig` na cena,
`rig/landmarks.json`, teste de pose limpo. Regras de operação e do Blender ao vivo: skill `character-factory`.
Comandos completos: `factory/README.md` ("Passo a passo", passos 4–5). Exemplo: `characters/brasa/rig/landmarks.json`
(as chaves `_doc*` explicam cada bloco).

## 0. Rig simples e de mobile: orçamento de ossos (princípio de jogo 7)

Um esqueleto limpo, com poucos ossos; osso extra SÓ onde ele acrescenta personagem (orelha, cauda, capa, capuz, barba,
arma com corrente). Rigify é a ferramenta (o Auto-Rig Pro não está instalado e não é preciso: o export leva só os ossos
DEF com nomes Mixamo). Contagem medida nos prefabs da Unity (ossos usados pelos `SkinnedMeshRenderer`, 2026-11-14):

| Unidade | Total | Base | Dedos | Props | Extras (personagem) | Efeito (`Fx*`) |
|---|---|---|---|---|---|---|
| BRASA | 49 | 30 | 8 | 1 | 10: Beard ×3, Tabard ×4, LeftPauldron, Backpack, Chimney | 0 |
| GRANIZO | 46 | 30 | 8 | 1 | 7: Hair ×3, Tabard ×4 | 0 |
| OSSINHO | 47 | 30 | 12 | 1 | 4: Tabard ×4 | 0 |
| ALVOR | 64 | 30 | **20** | 2 | 4: Tabard ×4 | 8 (aura) |
| OCASO | 90 | 30 | **20** | 1 | 3: Hair ×3 | **36** (raio, hex, colunas) |
| FERRUGEM | **143** | 28 | 12 | 0 | 0 | **103** (explosão em pedaços) |

Base = root, Hips, Spine/1/2, Neck/1, Head, ombro + deltoide + braço + torção + antebraço + torção + mão por lado,
coxa + perna + pé + dedo do pé por lado (30; o FERRUGEM não tem deltoide: 28).

Regras (orçamento por unidade de jogo; o número vale para o PRÓXIMO personagem):
- **Deformação ≤ 50 ossos** (sem contar `Fx*`): base 30 + dedos ≤ 8 + personagem ≤ 10 + 1 por prop rígido. Quatro
  influências por vértice (já é o contrato do export).
- **Dedos ≤ 8** (polegar 2 + bloco dos outros 2, por mão): a 64 px um dedo tem menos de 1 px. Dedos separados (20) só
  se um close (Retrato, desbloqueio) mostra a mão fechando — senão é custo de CPU por unidade sem ganho de leitura.
  ALVOR e OCASO estão acima disso por causa da pegada de uma mão (decisão daquele estágio); não copie.
- **Osso de personagem precisa se mexer na tela**: cada osso extra tem de andar ≥ 2 px (≈ 5 cm na ponta) em algum
  clipe — leia o deslocamento da cauda do osso no `motion_table.py`. Não andou: funda com o pai ou tire. Corrente de
  molas: 2–3 ossos (barba, rabo de cavalo, tabardo), nunca 6.
- **Rosto para os closes** (skill `character-design` §0d): mandíbula 1 + pálpebra/sobrancelha 1–2 por lado, só quando
  o brief pede expressão; contam no orçamento de personagem.
- **Efeito não mora no esqueleto da unidade se ele é de UMA vez**: osso `Fx*` animado por escala é barato no clipe que
  o usa, mas é pago em todo quadro de toda unidade viva. O FERRUGEM carrega 103 ossos de pedaços só para a morte —
  limite conhecido; o próximo personagem que explode leva os pedaços num prefab próprio, instanciado no evento da morte
  (o `CFExplosion` já recebe o evento), e o esqueleto vivo volta ao orçamento.
- Conferir no fim do rig e de novo no export: a chave `bones` do manifesto (`characters/<id>/export/<NAME>.json`) e,
  na Unity, o mesmo trecho que fez a tabela acima (união dos `r.bones` dos `SkinnedMeshRenderer` do prefab, separada
  por nome: `Fx*`, dedos, base, props, o resto = personagem). Passou do orçamento: escreva no `state.json` por quê.

## 1. Entrar na cena

```
bl.py run blender/reset_character.py                       # só se a cena tem outro personagem; salve o .blend dele antes
bl.py run blender/stage.py --arg character=<id> --arg concept=<refs/tpose_front.png>
bl.py run blender/import_model.py --arg glb=<glb> --arg name=<NAME> --arg height=<m> --arg review=<dir>
bl.py run blender/gameready.py --arg name=<NAME> --arg tris=60000 --arg outdir=<model/textures> --arg review=<dir>
bl.py run blender/ortho.py --arg name=<NAME> --arg outdir=characters/<id>/rig ; .venv/bin/python cf/grid.py characters/<id>/rig
```

Um arquivo `.blend` por personagem (`characters/<id>/<id>.blend`). Prop decimado sem soldar racha em cacos: `open_edges`
do relatório tem de ser 0.

## 2. Landmarks: ler das pranchas, nunca chutar

`ortho_front_grid.jpg` / `ortho_side_grid.jpg` têm grade métrica. Escreva `rig/landmarks.json`:
- `joints` em metros no repouso. Junta com `y: null` é centrada na malha **de repouso** (um default silencioso já pôs
  ossos fora do braço). O ombro é o centro do deltoide, não a axila; o pulso é onde a mão dobra, não a borda da braçadeira.
- `regions` (caixas/cores de peso), `props` (caixa-alvo + osso + rotação de cada prop), `keepout` (cápsulas de pontas
  rígidas da cabeça: chifres, presas largas), `secondary.chains` (teto de balanço das massas soltas), `weapon`, `grip`.
- Confira esquerda/direita pelo marcador assimétrico do brief antes de qualquer outra coisa.
- **Meça a malha antes de escrever um número**: fatias por altura/eixo (onde começa e acaba cada peça, a seção do braço,
  o raio do bracelete), cores médias por faixa (HSV) e close-ups em pontos do MUNDO sem rig:
  `bl.py run blender/look_at.py --arg out=<dir> --arg 'spots={"mao":[x,y,z,raio]}'`. No segundo personagem todos os
  landmarks saíram de medida e o rig passou nos portões na primeira montagem.
- Vocabulário que o segundo personagem acrescentou (tudo opcional, dirigido por dados):
  - `extras`: `[{"chain": "hair", "joints": [...], "parent": "spine.006"}, {"bone": "backpack", "joints": [a, b], "parent": ...}]`
    — sem a chave, vale a lista do BRASA. Nomes da casa: `hair*` / `beard*` (correntes macias que colidem com o prop),
    `tabard_f` / `tabard_b` (abas do cinto), `backpack`. O prop da mão é sempre `<NAME>_hammer`.
  - `colors`: classes HSV por personagem (`{"ivory": [{"h": [12, 48], "s": [0, .25], "v": [.72, 1]}]}`), usadas em `regions[].color`.
  - `regions[]`: `fade_x: [x0, x1]` (a região some para os lados: aba soldada na coxa) e `soft_passes` (borda de cor macia).
  - `limit[]`: teto de peso com `ramp [z_livre, z_teto]` nos DOIS sentidos (para cima ou para baixo).
  - `limbs`: raios medidos do braço — `bl.py run blender/limb_radii.py --arg name=<NAME> --arg landmarks=<json>`.

## 3. Portões do modelo — antes do rig

```
bl.py run blender/model_gates.py --arg name=<NAME> --arg landmarks=<json>
```

| Portão | Mede | Se < 1 |
|---|---|---|
| `overhead` | braço ÷ distância do ombro a 6 cm acima do topo do crânio | `proportions.py --arg factor=<n>` alonga o braço NO MODELO (só a pele lisa; malha, high-poly, LOD e landmarks pelo mesmo mapa; reversível) |
| `corridor` | (largura dos ombros − espessura do braço) ÷ envergadura de tudo acima da cabeça | `part_tilt.py` (inclina chifres/cristas no modelo, `dry=true` primeiro) ou gerar de novo; nenhuma pose resolve |
| `wrap` | quanto os dedos fecham antes de tocar o cabo (só depois do `fist_fit.py`) | cabo mais fino, dedos mais longos, ou punho estilizado **declarado** em `grip._fit` |
| `cuff` | meia largura dos dedos ÷ raio do que veste os últimos 12 cm do antebraço (bracelete, aba da manopla) | gerar de novo com bracelete que afina até o pulso / acaba 3–4 cm antes; senão `wrist_ulnar_max_deg` nos clipes e limite declarado (GRANIZO: 0,925 → pomo 34 mm no bracelete) |

O relatório traz também `shoulder_half_over_arm` (fato, ainda não portão: 0,56 no BRASA carregou bem um prop de duas
mãos; 0,63 no GRANIZO deixou a mão do pomo por dentro do ombro).

Por que antes: no primeiro personagem os três reprovavam e só apareceram depois de cinco clipes prontos (chifre 34 mm
dentro do braço em 15 quadros; 17 tentativas de pose só trocaram o lado do contato). A espessura do braço é a **medida
na malha**: a "impressão" dizia 15 cm, a malha 20–22 cm.

## 4. Rig, pesos, props

```
./rebuild_rig.sh <id> <NAME>     # rig_build → prop → recap_island → rig_bind → split_plates → rig_extras → attach_prop → fist_fit → pose_test
```

Rode depois de QUALQUER mudança nos landmarks (~40 s). Auto-Rig Pro não está instalado: Rigify. Regras que já estão no
código e que você precisa alimentar pelos landmarks:
- Todo acessório rígido é objeto separado em osso próprio (`props` + `attach_prop.py`); `prop_bones` não seguram pele.
- Placas rígidas que se movem uma contra a outra (braçadeira | mão) não compartilham pele (`split_plates.py`).
- Transição de peso nunca em cima de borda pintada: a região rígida engole a borda, a rampa fica na pele lisa.
- Antebraço: osso de meia-torção carrega a braçadeira; a torção se distribui (cotovelo / punho / mão).
- Massa soldada que dobra (barba, rabo de cavalo) = ilha + verso em tiras (`split_props.py`, `recap_island.py`).
- Peso automático falhou (< 90 % dos vértices)? `rig_bind.py` cai sozinho no proxy voxel.
- Rasgo = (degrau de peso) × (quanto aquele osso viaja). Receitas que o GRANIZO precisou:
  - cabeça sem pescoço: `limit` `neck_not_chest` (ossos do pescoço com teto 0 abaixo do queixo, rampa para o peito) +
    `feather` largo na mandíbula (0,07) — o pescoço segurava pele 20 cm à frente do próprio pivô (69 arestas 13→47 mm);
  - bota/perneira rígida: `limit` `boot_is_foot` (canela com teto 0 na bota, rampa longa);
  - aba de tecido soldada na coxa: corrente `tabard_*` com `fade_x` + `soft_passes 4` e rampa do quadril larga
    (arestas > 30 mm no joelho levantado: 83 → 33);
  - bracelete rígido: região no osso SEM torção (`DEF-forearm.L/R`), punho girando no corte bracelete|mão
    (`hands.cuff_pin`); aí a torção do antebraço deixa de aparecer (ver skill `character-clips`).

## 4b. Consertos do gerador, look e props segurados (ALVOR)

- **Dedo a mais / protuberância**: `blender/remove_stub.py` (corta e fecha a pele) → `blender/skin_patch.py` (repinta a
  sombra e o vinco que o gerador pintou na raiz; `dry=true` primeiro, leia `other_paint_by_5mm` para escolher `force`).
  Aplique também na high-poly se ela ainda for usada para bake.
- **Look fosco** ("a luz que vem do Tripo"): `blender/matte.py` — metal escalado, piso de rugosidade, sem especular;
  os números ficam no material (`cf_matte`) e o export os leva para a engine. Nada de repintar textura.
- **Mão com dedos separados**: `hand_fingers.py` propõe as juntas (`landmarks.fingers`), `hand_test.py` fecha o punho e
  mede. Dobradiça do dedo = eixo lido do osso, não um eixo fixo do mundo.
- **Lâmina**: `prop_blade.py` (eixo, guarda, pomo, meia-espessura, meia-largura) em vez do `prop.py`.
- **Escudo SEGURADO**: `props[]` com `bone: DEF-hand.<lado>` + `seat` (escala, rotação, deslocamento — `hand_seat.py`
  lê a alça e a leva para dentro do punho). Se o punho não alcança a alça com o antebraço atrás da placa, aumente o
  escudo (ALVOR: 1,3×), não estique o braço. A face do escudo fica no objeto (`cf_face`) para o `onehand.py` apontá-la.
  Dê `own_bone` ao prop segurado (`props[].own_bone: "DEF-shield"`; `prop_own_bone.py`, chamado pelo `rebuild_rig.sh`):
  osso filho da mão com o mesmo repouso — nada muda nos clipes, e a morte pode SOLTAR o prop (sem isso o escudo fica
  pesado na mão e um braço morto continua "segurando": dois rounds de crítica no ALVOR). Entra em `prop_bones`.
- **Efeito**: `landmarks.fx` + `fx.py build=true` (o `rebuild_rig.sh` chama): malha em ossos `DEF-fx_*` sem pai.

## 4c. Corpo de peças rígidas e mini de pernas curtas (OSSINHO, 0,70 m)

- **Esqueleto**: cada osso é uma região rígida presa (caixas em `regions`, processadas em ordem — a de baixo vence);
  só os pescoços entre as peças dobram. A solda costela | cabeça do úmero ainda estica até 35 mm nas poses de teste:
  lê como junta de bola com um vinco, foi aceita e DECLARADA (a cura seria um corte genérico entre ossos rígidos).
- `pose_test.py` escala os movimentos pelo comprimento da perna (< 40 cm): 22 cm de pé levantado numa perna de 16 cm
  davam 121 de 136 arestas esticadas — defeito do teste, não do rig.
- `prop_blade.py --arg guard_min=0.85` (ou `weapon.guard_min`): uma lâmina LARGA (cutelo) é lida como guarda com o
  padrão 0,5 (`guard_thick_z` 0,294 — a lâmina inteira).
- `hands.stub` / `stub_taper` / `stub_shade` nos landmarks: o toco do pulso do `split_plates.py` por personagem
  (pulso de osso fino: 0,012 / 0,75 / 0,3 — o padrão saía escuro para fora do punho).
- Gerador assimétrico (4 dedos numa mão, 3 na outra): `remove_stub.py` no dedo a mais, e `fingers` igual dos dois lados.
- Portão `overhead` reprovado por DESENHO (crânio tão alto quanto o braço é longo; mini de manto que nunca levanta
  o braço ao lado do capuz) não se conserta no modelo: declare no `state.json` e autore os clipes dentro dele.

## 4c'. Máquina de peças rígidas (FERRUGEM: `characters/ferrugem/rig/landmarks.json`, chave `_doc_caps`)

- Peça rígida = `regions[]` com `"island": true, "closed": true` + um osso: 100 % rígida, as tampas de corte fechadas
  (`split_props.py`). Pele contínua numa máquina rasgou 166 arestas / 61 mm no teste de pose; ilhas fechadas nas colunas
  das coxas e nos pedestais dos pés resolveram. A dobra fica só nos acoplamentos (pescoço do tornozelo, cotovelo).
- Tambor do ombro no osso da CLAVÍCULA (`DEF-shoulder.X`) com o centro no ombro: o braço gira dentro dele.
- `bisect: [["x", 0.592]]` corta no fim do chanfro MEDIDO na high-poly (um corte 1 cm fora deixou cacos da borda) →
  anel plano. A tampa pega o texel de `cap_from` (um ponto de ferrugem, não cinza) com UV planar mínima e normais
  divididas personalizadas (leque ponderado por área): sem isso a tampa faceta em cata-vento. As normais sobrevivem
  ao `rebuild_rig.sh`.
- Cotovelo de acoplamento curto: encurte o pino rígido do úmero até a zona de dobra ter ~7,5 cm (43 → 33,6 mm só na pose
  extrema) e limite o cotovelo a ~60° nos clipes.

## 4d. Prop que balança quando é atingido (TOCO, boneco de treino)

Não é Rigify: `blender/wobble_rig.py` com `landmarks.wobble` — `bones` (o primeiro é o pé fixo; cada próximo pendura no
anterior, cabeça = pivô), `blends` (faixa de altura onde um osso passa a malha ao seguinte, smoothstep), `spring`. Ache os
pivôs por FATIAS de altura (largura por faixa de 2,5 cm): onde o poste sai do pé, onde a cabeça apoia. A física fica em
`blender/wobble.py` (assa acertos em chaves) e no `CFWobble.cs` (as mesmas equações). Molas moles leem melhor: 8,5° não lê a
64 px; 13–14° na magia sim.

Alvo que MORRE tomba como corpo rígido pela borda do pé — e isso se MEDE na malha, não se chaveia:
`bl.py run blender/topple_fit.py --arg name=<NAME> --arg write=true` grava `landmarks.wobble.topple` (centro de massa e,
por direção, borda `r`, giro² `k2`, ângulo de repouso `rest`); `export_prop.py` leva para o manifesto, o `wobble.py`
(`life`) e o `CFWobble` usam a mesma tabela. TOCO: centro de massa a 0,51 m, borda 0,22–0,27 m (pé em cruz), repouso
75,9–91,5° (de costas 89,1°). Ângulo de repouso = o MENOR atan2(w, u) sobre todos os vértices, com qualquer u: contar só
os pontos além da borda deixava a queda de costas parada em 90° com o saco flutuando (o pé segura o poste 22 cm acima
do chão). Faça backup do `landmarks.json` antes do `write`. Show e regras da morte: skill `character-show`.

## 4c. Máquina de peças cortadas (FERRUGEM): juntas, tampas e o que fica escondido

- **Bola na junta** (`joint_ball.py`, `landmarks.balls`): membro que gira com o pivô DENTRO da carcaça (ombro no tambor,
  tornozelo no pedestal) mostra a tampa do corte saindo. Esfera centrada no pivô, na malha do corpo, rígida na ilha da
  carcaça. A cor decide: `balls[].uv` com um texel de ferro escuro liso (±8–16 px) — o texel vizinho virou "bola de pele".
- **Tampas com texel explícito** (`cap_texel.py`, `regions[].cap_uv`): o texel mais próximo do corte costuma ser ferrugem
  = ruído espalhado num disco de 20–40 cm.
- **Forro do encaixe** (`socket_liner.py`, `landmarks.liners`): a superfície do corpo que uma ilha ESCONDE no repouso
  (raios: com a ilha bloqueiam, sem ela abrem) — o gerador nunca viu e texturizou como ruído. Pinta (só UV) com o ferro.
  UV guardada em `cf_uv_orig3` (FLOAT_VECTOR; um FLOAT2 de canto vira 2º mapa UV).
- Antes de culpar a malha por "pontilhado" numa fresta: vista sólida (há buraco?) e cor de teste chapada nas faces
  suspeitas. No FERRUGEM os pontos ficaram sobre o amarelo = sombra do EEVEE com 1 raio (o `stage.py` agora usa 4 × 16).
- **Anel de face** (`joint_ball.py` com `"shape": "ring"`): corte que passa por uma ponta abaulada/rebitada deixa um cap de
  borda rasgada (r 0,08–0,17 no tambor). Um anel de latão na face (r_in/r_out, `cone` de ~4 mm, lábios para dentro) e um
  anel escuro de soquete em volta do braço. Texel escolhido NA TEXTURA (PIL: valor, saturação, desvio da vizinhança): o
  vértice mais próximo deu um latão claro que lia como adesivo.
- **Peça que gira por dentro varre uma esfera** (`part_tuck.py`, `landmarks.tuck`): a aba do braço a 13–16 cm do pivô
  com r 0,15–0,18 varria o raio do próprio tambor e saía pelo aro. Puxe o anel para dentro de `r_max` em torno do eixo.
  Script que move vértices de rest pose tem de ser idempotente por MARCA (só o que ele moveu guarda o original): a 1ª
  versão restaurava todos de uma cópia e jogou as bolas do `joint_ball` (recriadas a cada rebuild) na origem.
- `rebuild_rig.sh` roda `joint_ball` → `cap_texel` → `socket_liner` → `part_tuck` quando os landmarks pedem; `lod.py` depois.

## 4e. QUADRÚPEDE (UIVO, lobo): metarig de lobo do Rigify, enxuto

- `blender/quad_rig.py --arg name=<NAME> --arg landmarks=<json>`: o wolf metarig cortado para mobile (35 ossos de deformação:
  coluna 5 + pescoço 2 + cabeça + rabo 4 + escápulas + 4 patas de 4 ossos + mandíbula + orelhas 2+2). Juntas no
  `landmarks.json` (cabeçalho do script: `hips…chest`, `neck/neck_mid/head/head_tip`, `tail_1…tail_tip`,
  `scapula/shoulder/elbow/wrist/fpaw/ftoe`, `hip/stifle/hock/rpaw/rtoe`, `jaw/chin`, `ear/ear_mid/ear_tip`); grava
  `rig["cf_quad"] = True` (limb_paint, export e clipes leem) e `IK_Stretch = 0` (pata fora do alcance esticava a perna).
- Nomes do metarig NÃO são de bípede: `spine` é a PONTA do rabo, o corpo é spine.004 (garupa) → spine.008, a cabeça spine.011.
- Pesos: `rig_bind.py` + regiões (`mane` por cadeia, `lower_jaw` caixa, `keep_only` focinho/crânio, `limit` bochechas,
  garganta, `chest_ruff` com mandíbula 0, `brisket`): o calor dava a juba aos ombros e a mandíbula levava o peito.
- Malha do Tripo (Remesh → Smart UV → Textura): **solde as costuras de UV antes do bind** (`remove_doubles` 1e-5; 41.752 →
  29.966 vértices) — o glTF duplica o vértice em cada costura e o calor pesa cada lado sozinho (a pele rasga no layout UV).
  Confira o encaixe na malha hi (BVH: mediana 0,03 cm) e troque a malha mantendo o rig; a malha antiga vai escondida.
- `blender/quad_pose_test.py --arg name=<NAME>`: poses A recolhida, B estendida, C mordida, D uivo, E virada → estiramento
  de aresta p99 / máx, vértices > 2,2×, ponto mais baixo (UIVO: p99 1,5–2,1).

## 5. Olhar e medir — só então dizer que está limpo

1. `pose_test.py` (independe da pose de bind) e seus close-ups de ombro. O olho vê COMPRIMENTO: leia
   `edges_over_2.2x_and_15mm` e `max_gain_mm`, não só a razão (uma aresta de 3 mm que triplica não aparece).
   `--arg only=A` deixa uma pose sozinha na tela para o `stretch_why.py` e os close-ups. O `rebuild_rig.sh` imprime
   uma linha por pose; o resto está em `review/build/05_pose_test.json`.
2. Pintura por membro: `blender/limb_paint.py --arg mode=on` — membro sem a cor certa = peso errado; membro que some =
   pose errada. Desligue (`mode=off`) antes de exportar.
3. Close-ups: `blender/closeup.py` (ossos-alvo, raio, vistas, `hide` para esconder props) + `cf/sheet.py`. Vista com
   elevação negativa ou raio pequeno pode cair dentro do corpo: descarte a célula, não interprete.
4. Deformação = (degrau de peso) × (quanto o osso anda em relação aos vizinhos). Laço:
   `stretch_probe.py` (onde) → `stretch_why.py` (qual osso, qual ilha, quantos mm) → regra em `landmarks.json`
   (`limit` com `ramp`, `smooth_zones`, `sharpen`) → `./rebuild_rig.sh` → de novo. Procure degraus PEQUENOS de ossos que
   andam muito.
   **Antes de mexer em peso, prove que é peso**: pegue os vértices da costura e meça o deslocamento deles no espaço do
   osso dominante entre dois quadros. Vértice 100 % num osso que se move em relação a ele NÃO é peso — é B-bone (ou
   shape key/modificador). O FERRUGEM perdeu uma rodada assim: o Rigify gera DEF com B-bones (coluna 8 segmentos,
   membros 10), a pele do tronco curvava 19,9 mm contra a ilha rígida do tambor e a costura rasgava em serrilha. A engine
   não tem B-bones: `rig_build.py` agora força 1 segmento em todo osso que deforma (o que o Blender mostra = o que a
   Unity mostra). Mudou o rig, reconstrua e sonde os cinco clipes (no FERRUGEM a cabeça passou a entrar 25 mm no
   colarinho no ataque, que a coluna curva escondia).
5. Depois dos clipes: `contact_probe.py` (malha contra malha, todo quadro) é o juiz de penetração; ver `character-clips`.

O usuário julga pelo viewport. "Ainda há deformações" significa: ache com close-up, conserte a causa no peso ou no
modelo, mostre o antes/depois — não suba um portão nem esconda com câmera.

## 6. Fechar o estágio

`lod.py` (LOD1 medido contra a hero deformada; refazer depois de qualquer mudança na malha), salvar o `.blend`,
`state.json` com os números dos portões, e o que é limite do modelo escrito como limite.
