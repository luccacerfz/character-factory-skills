---
name: character-clips
description: Autorar os clipes de um personagem da Character Factory — pose-base, ataque, idle, andar, tomar dano e morte, e os clipes especiais (magia à distância com projétil, invocação, unidade que sai do chão / spawn, cajado plantado) — com arma de duas mãos, de uma mão + escudo ou SEM arma (garras, punhos — rota desarmada do freehands), molas de follow-through, efeitos (aura, raio, orbe), contato malha×malha e chão medidos e os 12 princípios da Disney conferidos no tamanho de jogo (64 px). Use quando o usuário pedir uma animação ("faz o idle", "ataque", "andar", "dano", "morte", "magia", "invocação", "todas as animações"), reclamar de uma ("o braço some", "está sem peso", "o pé patina", "a arma atravessa") ou depois de mudar o rig. Inclui a referência em vídeo Seedance do próprio personagem com membros coloridos. Personagens CONTRACENANDO (invocador + invocados, alvo de treino, rodada) são da skill character-show. Inclui os princípios de jogo no clipe: poses que leem a 64 px, golpe curto com contato claro e hit-stop, variações de andar para bando e o clipe de vitória/close.
---

# Clipes

Tudo que é autoral de um clipe mora em `characters/<id>/anim/<clip>.clip.json`; `./clip.sh <id> <NAME> <clip>` constrói
(~7–20 s) e escreve o relatório de cada estágio em `anim/<clip>.build.log`. O contrato completo das chaves está em
`factory/README.md` ("Clipes" e "Além do ataque"); as receitas do BRASA e do GRANIZO são os exemplos. Regras de
operação: skill `character-factory`.

Ordem dos estágios (não mude): retarget (se houver take) → polish → floor | bodyfloor (+plant, +limbfloor) → weapon OU
onehand → freehands (se soltou o prop, duas mãos) → hubpin → secondary → keepclear → **stance** → fx.

## 0. Personagem novo: comece PORTANDO as receitas de um aprovado

```
python3 cf/port_clip.py <src_id> <SRC> <dst_id> <DST> [clip ...] [--force]   # ângulos copiados; metros escalados
bl.py run blender/limb_radii.py --arg name=<DST> --arg landmarks=<json>      # raios REAIS do braço -> landmarks "limbs"
./build.sh <id> <NAME> attack            # clip.sh + relatório curto + emenda/base  (depois idle walk hit death)
./look.sh <id> <NAME> <clip> a '[[62,8],[0,6],[90,6]]' 3 2.1 '[0.1,-0.3,0.95]'   # folhas de contato de câmeras fixas
./contacts.sh <id> <NAME> <clip>...      # contact_probe em cada clipe, uma linha por par
```

O porte escala cada número pelo que ele é: ângulos iguais; metros no espaço do peito × razão dos braços; metros no chão
× razão das pernas; raios do solver = os MEDIDOS no corpo novo. No GRANIZO os cinco clipes construíram na primeira
tentativa; o que o porte NÃO sabe e teve de ser corrigido à mão:
- **largura dos ombros**: escalar pela razão dos braços deixa a mão do pomo por dentro do ombro num corpo mais largo
  (ombros ×1,6, braços ×1,44) → +0,07 m em "esq" nas chaves de porte baixo, +0,04 no impacto;
- **raios**: a receita trazia antebraço 0,11 m; o bracelete mede 0,164 → o solver achava livre um pomo 35 mm dentro;
- **onde a torção aparece**: com bracelete rígido no osso sem torção, a torção do antebraço não torce nada e o que
  aparece é o DESVIO do punho (cabo deitado no bracelete) → `forearm_twist_free_deg 110`, `wrist_ulnar_max_deg 45`,
  `twist_side` só no braço que precisa; `weapon.grip` com a mão do pomo na PONTA do cabo (sobra ≤ 2–3 cm);
- **referência em vídeo**: é do próprio personagem — o porte apaga `reference`; filme outra (seção 7);
- **classe de peso**: o porte copia os TEMPOS. Um ogro de 390 kg com os tempos de um anão levou 7,46 dos críticos
  ("a dwarf's timing on an ogre's mass"). Antes da primeira revisão, re-tempore para a massa: andar com período mais
  longo (24 → 30 quadros = 120 passos/min; chaves em f' = 1 + (f−1)·k), `bob` e balanço da arma menores (quadril
  ≤ 4,5 cm, cabeça da arma ≤ 15 cm), mergulhos em 8–10 quadros, recuo do dano e chute das pernas na morte pela metade;
- **alcance das pernas**: metros de tronco × razão das pernas pode pedir um agachamento que a perna curta não tem
  (−14,4 cm em pernas de 43 cm): o `polish.py` devolve o quadril (`leg_reach.hips_raised_max_cm`) e o corpo bate
  nesse limite como numa parede. Leia `hips` em `motion_table.py` e chaveie até o limite, não além.

`weapon.debug_arm: ["L", 17]` imprime no log o custo de cada giro de cotovelo daquele braço naquele quadro (desvio,
torção, flexão, folga do cabo): leia isso antes de mexer em pesos do solver.

## 1. A pose-base decide os cinco clipes

- Pose-base = quadro 1 do ataque (porte da arma a duas mãos). Idle, andar, dano e morte usam
  `recipe.pose_from: "<NAME>_attack"`; sem take de mocap, `source: "hold"` + `layers` / `gait`.
- Antes de animar, escolha a pose-base olhando três números do `weapon.py`: torção dos antebraços (meta < 90° do bind),
  dobra dos punhos (< 60°) e `contact_probe` do quadro 1. Um defeito aqui é herdado por todo clipe.
- Parâmetro da pose-base (`weapon.grip`, `grip.*`, `phi_ready` / `psi_ready`) não se mexe por causa de um quadro:
  mudou, reconstrua os cinco (ataque primeiro) e sonde os cinco.
- Todo clipe é autorado **quadrado** e girado no último estágio (`stance_yaw_deg`: ataque / idle / dano / morte +30°,
  andar 0°). Os solvers não são invariantes a rotação.

## 2. Braços num cabo

`weapon.py` resolve cada braço com duas variáveis livres (giro do cotovelo × rolagem do punho no cabo).
- `weapon.keys` = ângulos do prop `[quadro, phi, psi, sep, ease]`; `weapon.hands` = centro da pegada no espaço do
  peito `[quadro, esq, frente, cima, peso]` (peso 2 = chave travada).
- Se `twist_jumps` / `seam_crossings` não vierem vazios ou o punho passar de ~60°, o erro é da trajetória do prop ou das
  mãos, não do solver: `./wtable.sh <id> <NAME> <clip> [f0 f1]` (tabela por quadro; ele RE-EXECUTA o weapon.py →
  reconstrua com `clip.sh` depois) e `cf/armlab.py` para testar regra nova offline.
- Onde a pegada cabe: `blender/reach_map.py` (um punho, com o raio REAL do antebraço) e `blender/grip_fit.py` (centro da
  pegada em que os dois braços ficam fora do corpo → chaves prontas). Mão do pomo à frente do próprio ombro, nunca no
  eixo do corpo; com as mãos altas os cotovelos vão para frente/cima e a cabeça é zona proibida.
- Prop com inércia (`drag`): o cabo real atrasa 25–40° do ângulo chaveado → chaveie as mãos contra o ângulo real.
- `twist_side` fixa o ramo da torção; o outro ramo também se mede antes de escolher. Hipótese de crítico se testa e
  se mede: soltar o ramo do braço direito do GRANIZO ("a torção estaciona em 155°") deu 178°, desvio de punho ±90° e
  um cruzamento de costura → revertido. Num bracelete rígido essa torção nem aparece; o desvio do punho aparece.
- `handle_weight` / `handle_cost_cap` (padrão 4 / 8): subir para 20 / 45 no ataque levou cabo × antebraço direito de
  23 mm para 12,5 mm sem saltos; confira `twist_jumps`, a dobra do punho e o `contact_probe` depois.
- O antebraço não pode deitar no cabo: regra do pomo (mão de baixo) + regra do cabo (as duas mãos, `handle_weight`),
  ambas com custo que satura. Elas escolhem o cotovelo; quem resolve de verdade é a posição da pegada e o desenho do
  bracelete (skill `character-design`). Resto conhecido no GRANIZO: pomo × bracelete 34 mm em 7 quadros do ataque.

## 2b. Arma de UMA mão, escudo segurado, efeito (ALVOR é o exemplo: `characters/alvor/anim/*.clip.json`)

Quando `rig/landmarks.json` tem `onehand`, o `clip.sh` roda `onehand.py` no lugar do `weapon.py`. Leia o cabeçalho dele.
- Você chaveia o que lê a 64 px: `weapon.wrist` `[quadro, esq, frente, cima]` (pulso no espaço do PEITO) e `weapon.aim`
  `[quadro, phi, psi]` (para onde a lâmina aponta). O solver é dono do cotovelo, do giro do punho e dos limites.
  `"ready"` = a pose de porte do personagem (`landmarks.onehand`).
- **A chave não é o contato.** `drag` é uma mola na direção da lâmina (0,35 ≈ 1,3 quadro de atraso). Meça a lâmina
  (rumo/elevação do osso da arma) no quadro do evento `hit` e adiante as chaves — no ALVOR ela apontava −81° do alvo
  no quadro do evento antes do ajuste.
- **Escudo**: segurado pela alça na mão (`props[].seat`), apontado por `off.face` `[quadro, rumo, elevação, giro]` —
  a FACE do escudo; a mão toma a orientação que isso pede. Na guarda ele fica na FRENTE do corpo (punho na linha do
  centro), nunca ao lado do ombro; o braço do escudo fica à frente no preparo e abre como contrapeso no corte.
- **Escudo em repouso (morte, queda)**: o eixo do punho fica a ~40° da normal do escudo (a alça é inclinada). Um
  escudo deitado de face para cima AO LADO de um antebraço deitado obriga o punho a apontar para o céu — pulso a 114°
  por 23 quadros no ALVOR. Pouse o escudo SOBRE o corpo (peito), por último, e gire-o no próprio plano (`roll`) até o
  pulso descansar (32°). Leia `wrist_bend` da mão do escudo no último quadro, não só no golpe.
- **Mira que o pulso não dá não é alcançada — e ninguém avisa.** Os limites (`wrist_flex_max` 60, `wrist_dev_max`
  38) cortam a mira em silêncio: um follow-through com psi +33 parou 12 cm antes. Confira `aim_off_deg` do build e
  a posição da ponta; termine o golpe numa mira que o braço alcança.
- **Espaçamento se mede na PONTA**: velocidade da ponta quadro a quadro (`motion_table` → `speed.sword_head`). O corte
  do ALVOR tinha 8,9 → 7,7 → 16,7 m/s (um tranco e um salto) que nenhuma folha de câmera mostrava; redistribuindo
  as chaves de punho/mira/tronco ficou 5,4 8,7 12,1 13,7 9,3 6,5 (acelera até o contato, desacelera depois).
- **Arma solta** (`weapon.release`): o `onehand.py` deita o prop pelo casco inferior da PRÓPRIA malha (apoia nos dois
  pontos mais baixos em volta do centro de massa — na espada, guarda + ponta) e levanta um prop em voo que tocaria o
  piso. Leia `prop_lies` no log do build. O evento de som (`sword_ground`) vai no quadro do primeiro toque.
- **Prop solto herda DUAS velocidades**: a linear (abaixo) e a ANGULAR — `release.ballistic.turn: 1.0` = gira a taxa
  constante durante o voo. Sem isso a rotação entra em ease-in até a pose deitada e a arma "paira em pé ao lado da mão
  e depois tomba" (ALVOR rodada 3: 4,5 → 13,2°/quadro; virou o defeito mais visível da morte). Confira o passo angular
  por quadro, não só a posição; aço que chega a ~4 m/s quica (`bounce` ≈ 0,12).
- **Queda obedece a g**: com apoio no chão o centro de massa não acelera para baixo mais que 1,09 cm/quadro² (30 fps), e
  não desce a velocidade constante (lê como agachar). Cair = o centro de massa SAI do apoio (margem cruza zero) antes de
  o quadril descer. Em loop, camadas com a mesma fase param juntas em algum quadro: defase-as (peito 6–8 quadros depois
  do tronco) e confira que quadril, cabeça e ponta nunca ficam os três abaixo de 0,03 m/s.
- **Soltura balística** (`release.ballistic`): o prop sai com a velocidade da MÃO e cai por gravidade; onde e quando
  pousa é calculado (`release_land_left_m / _fwd_m`, `release_flight_frames` no log). Para mudar o pouso, mude o gesto:
  `Δpouso = Δv × quadros de voo` (1 cm/quadro ≈ 19 cm) — mova a chave do pulso do quadro anterior ao último segurado,
  convertendo de mundo para o espaço do peito com os eixos do peito daquele quadro. Guarda de lado = o braço da arma é
  o de TRÁS: no recuo ele viaja para trás e a arma pousa atrás da cabeça se ninguém chavear o contrário. Chaves até 3
  quadros DEPOIS da soltura também mexem no voo: meça de novo.
- **A arma sai pela palma**: sonde a posição do cabo no espaço do osso da mão nos 5 quadros depois da soltura; se ela
  anda contra a palma (ou o tombo leva o pomo para o antebraço), `contacts.sh` acusa arma × antebraço/mão. Conserto:
  a mão recua pela normal da palma e o `yaw` do pouso inverte o tombo (o pomo sai para onde a palma olha).
- **Prop segurado que é solto** (`off.release`, exige `own_bone` no rig): `{frame, blend, wrist, hand, curl}`. Dali em
  diante `off.wrist` / `off.face` são o caminho do PROP; a mão segue `release.wrist` e deita com `hand: [0, 0]`
  (`hand` é [torção, flexão] — torção alta deixa a mão de quilha: `free_hand_wrist_lift_cm` alto no repouso).
  **Repouso do prop sobre o corpo**: não ajuste no olho. `blender/settle_dump.py` (corpo + prop em triângulos no quadro
  final) → `cf/settle_solve.py <npz> '<off.face final>' '<off.wrist final>'` devolve a pose de menor centro de massa em
  contato (apoios, margem do centro de massa) já como chaves; aplique a mesma diferença às chaves do pouso/quique e
  confira no `contacts.sh` (toque ≤ 6 mm, nenhuma penetração).
- **Soltura da planta numa queda**: se o pé autoral do repouso fica longe do pé plantado (o corpo ROLA depois do impacto
  e leva o quadril), voltar às curvas com a ponta no chão ARRASTA o pé (FERRUGEM: 99 mm/quadro, 20 cm em 3 quadros, que
  nenhuma folha mostrava — só `feet.slip_mm` da `motion_table`). `plant[].release_lift` (≈ 0,06 m) leva o pé pelo ar.
  Leia `slip_max_mm_per_frame` da morte depois de qualquer mudança no impacto.
- **Corpo deitado**: `weapon.shoulder_floor` (raio da ombreira) impede a clavícula de seguir a mão para dentro do
  piso; `floor_clearance` negativo quando o tronco flutua porque o ponto que "carrega" é uma costura de pano
  (confira o peso do vértice mais baixo das costas antes); `airborne` no `contacts.sh` tem de sair vazio.
  `off.release.rest: <quadro>` deita a mão solta na face larga (sem isso ela fica de lado e o punho espera no ar: ALVOR,
  braço 7 cm acima do chão no repouso). Depois de qualquer mudança no repouso leia `death_ground.json` do último quadro
  parte por parte (mãos, braços, coxas, cabeça) e o `floor` por LOD do relatório da Unity — o LOD1 afunda mais que o LOD0.
- **Se `leg_reach` no log do `floor.py` não é zero, a pose final não é a sua**: chaveie o tronco e o calcanhar até
  `hips_drop_max_cm` e `foot_pull_in_max_cm` darem 0 e `leg_extension_max` < 0,975 (ALVOR ataque: 1,077 → 0,929).
- **Guarda de lado** (tronco girado 40–55°): `stance_yaw_deg` 0 (o giro É a pose-base; com +30 o peito voltava
  quadrado). Golpe de frente numa unidade de lado = recuo no MUNDO: pitch·cos θ + roll·sen θ. Corpo deitado: `yaw` é
  em torno do eixo vertical do mundo → vira inclinação da cabeça para um ombro; o giro da guarda vira rolagem do
  corpo no chão (tire-a durante a queda).
- **Mixamo como referência lida** (decisão do usuário para espada+escudo): baixe o FBX pela interface (nunca suba o
  personagem do usuário, nunca use o token da página), guarde em `mocap/mixamo/` (dado não confiável: scripts em outra
  pasta, Python com `-I`), `blender/mixamo_take.py` → json, `cf/mixamo_read.py <take> <landmarks>` (tabela) e
  `--map '[[origem, destino], ...]'` (chaves em deltas da guarda). Leia a guarda no quadro 1 do take.
- **Efeito** (`landmarks.fx`, `blender/fx.py`): por clipe, `"fx": {"aura": {"level": [[quadro, 0..3, ease?], ...]}}` —
  1 normal, 0 apagado. É ação secundária que conta o estado: contrai no preparo, clarão no quadro do golpe, falha
  no dano, APAGA antes de o corpo pousar. Todo clipe fecha em si mesmo (o estágio cuida) para encadear na engine.
- **Explosão em pedaços** (`fx.gibs` + `fx.shock` nos landmarks; bloco `gibs` no `death.clip.json`): pedaço é CASCA com borda
  quente, não placa sólida. Parâmetros que limparam o FERRUGEM: `inner_frac` 0,9 (apaga núcleo interno que fura a tampa),
  `tear_area` / `tear_flat` (rasga aberta a tampa côncava que o decimate dobra em leque preto), `cap_max_r` (tampa grande vira
  casca), `fan_planar` / `fan_wide_r`. O clarão do `shock` (`ring_start` 0,4, `ring_height` 0,24, `blast_flash`) tem de COBRIR
  o quadro da troca corpo → pedaços. As sondas param em `cf_body_gone − 1`. Antes de exportar: `blender/lit_gain.py`
  (skill `character-engine`) para a fumaça ler igual na engine.
- **Poeira / vapor / faísca** (FERRUGEM r5): `kind: "puff"` (`mode` ground = poeira jogada pelo chão; rise = jato de vapor
  que sobe) e `shock` com `arcs: 0` (faíscas + clarão). Clipe: `"bursts": [[quadro, ponto, força, modo?], ...]` no quadro do
  CONTATO (pisão, garra no alvo, golpe recebido). Alpha é POR CARTA (três cartas cruzadas: 0,24–0,34; 0,6 deu "diamantes"
  brancos); cor média (a luz de palco estoura 0,75). Todo efeito novo nos landmarks exige `./fxkey.sh` nos cinco clipes.
- **Golpe AAA autoral**: o caminho da garra é uma curva (pontos de passagem), cada passo maior que o anterior até o contato;
  hit-stop = chave de parada em TODAS as camadas do corpo e na janela da garra no mundo nos 2 quadros do contato;
  corrente de força quadril → caldeira (+1 quadro) → garra. Meça: cantos (ângulo entre passos) e passos por quadro.
- `python3 cf/clipfmt.py <clip.json>` mantém o arquivo legível (uma trilha por linha) depois de editar por script.

## 2c. Prop plantado, unidade que SAI DO CHÃO, invocador (exemplos: `characters/ocaso`, `characters/ossinho`)

- **Clipe autoral de ataque** (sem take de ator) é `"kind": "oneshot"` + `recipe.returns_hub: true`. `"kind": "attack"`
  é o caminho de mocap: o `polish.py` procura `<NAME>_attack_mocap`, falha, e os estágios seguintes do `clip.sh` rodam
  sobre a ação que estava no rig e a CORROMPEM (o andar do OSSINHO teve de ser reconstruído). Build que falhou no
  polish = reconstrua também o clipe que estava na tela.
- **Cajado plantado**: `weapon.wrist_frame` / `aim_frame: "root"` (chaves no espaço da unidade, não do peito) e
  `weapon.foot` (o pé do prop é quem manda; `blender/prop_foot.py` mede, a build reporta `foot_off_mm`). Cuidado:
  com `aim_frame: "root"` a palavra `"ready"` é outra pose — numa unidade de prop carregado o quadro 1 saiu 59 mm da
  pose-base.
- **Unidade que nasce do chão = elevador** (`"sink": [[quadro, metros, ease], ...]` → `blender/sink.py`, depois do
  stance). Todo estágio trabalha com o piso em z = 0; então o clipe é autorado com a unidade EM PÉ no próprio piso e o
  `sink` baixa a raiz. Mão na borda do buraco = mão chaveada ALTA no espaço da unidade
  (`weapon.off.wrist_frame: "root"`, altura = −sink + 2 cm, uma chave por quadro). Gere o `sink` e essas chaves
  JUNTOS, de uma curva física só: velocidade de saída e `g` (9,81 / 900 m por quadro²) dão o ápice e o quadro do pouso
  (OSSINHO: solta a 1,94 m/s, 7 cm acima do chão no ápice, pousa 10 quadros depois; `sink` > 0 = no ar).
  `floor_probe.py` julga contra o piso DELE (`cf_sink` fica na ação). O clipe não começa na pose-base (quadro 1 =
  enterrado) e termina nela.
  - A ordem em que as coisas saem se MEDE: altura de cada ponta (mão, topo do crânio, ponta da lâmina) contra −sink,
    quadro a quadro. Lâmina a 40° "boiava" deitada na superfície; 52° ainda enterrada e 80° dois quadros depois: fura
    de ponta.
  - Corpo sem alcance por cima da cabeça (`overhead` 0,72): role o tronco 20° para o ombro que sobe ficar alto e o
    crânio sair do caminho — 12 cm de janela em que só a mão aparece.
- **Morte de unidade leve**: arremessada, não tombada — `root pitch` que só acelera (6 → 14°/quadro), `floor_hop` no
  voo, sem `plant`. No chão, tire TUDO o que a guarda tem de torto: o giro vira `roll` (seção 7, ALVOR), a inclinação
  para a frente vira um abdominal (ombros 4 cm no ar), e a cabeça inclinada para trás segura o corpo inteiro na nuca
  quando o crânio é mais grosso que as costelas (quadril 3,4 cm acima do chão): cabeça em linha com a coluna e raiz
  2–3° antes de −90.
- **Invocador**: `landmarks.summon {unit, event, points [[esq, frente], ...]}`; os efeitos de coluna do invocador
  (`fx` com `anchor: [esq, frente]`) ficam nesses pontos. O `spawn` da unidade tem de caber entre o evento do
  invocador e o fim da invocação (OCASO `summon` 23 → `summon_end` 58; OSSINHO `ready` no quadro 34 → 57).
  `blender/summon_show.py --arg host=<HOST>` ensaia o contrato da engine no viewport (skill `character-show`: cena
  `CF_Show`, strips NLA, a unidade enterrada até o evento). **`--arg mode=off` antes de voltar ao pipeline.**

## 2d. Magia à distância: projétil juntado na mão, lob, alvo (OCASO `spell`)

- Segunda habilidade à distância de um personagem: troque QUEM trabalha e a TRAJETÓRIA (ataque = cajado chicoteado, raio reto
  em 4 quadros; magia = cajado plantado, a mão de osso junta o orbe e o lança por baixo, arco balístico de 19 quadros).
- `landmarks.fx.<x>` kind bolt com `"bone": "DEF-hand.L"` e `"at"` sob a palma (no repouso as palmas olham para baixo: o
  lado da palma é −Z); no clipe `{"charge": f, "fire": f}`: o orbe nasce na mão e cresce, tremendo, até soltar. `"arc"` +
  `"ballistic": true` = parábola cronometrada por g; `"burst_frames"` / `"burst_scale"` a explosão. Um aura com `anchor` no
  ponto de impacto (`hexmark`) faz a marca no chão; chaveie o clarão no `lands_frame` que o build imprime.
- **Soltura = a mão anda para onde o orbe vai.** Meça o portador (osso do efeito) nos 3 quadros antes da soltura: a mão tem
  de acelerar (1,7 → 3,1 → 4,2 m/s) e sair na direção e na velocidade do orbe (4,6 m/s, 6°). Com o giro do tronco a mão varre
  para DENTRO: solte à frente do ombro do braço que lança, não cruzando o corpo (35° de diferença na v1).
- Corpo de manto/capuz: depois da soltura, pouco giro e pouca inclinação do tronco e a cabeça sem giro residual — o capuz
  afundava 50 mm na gola; `head_limits` ligados pioraram (67 mm: contra-giram a cabeça para trás).
- Todo clipe do personagem precisa chavear o efeito novo apagado: re-chaveie só os efeitos (assign + `fx.py --arg fx=<bloco>`)
  em vez de reconstruir os corpos.

## 2e. O que um show / rodada pede dos clipes

Cenas com vários personagens (invocação, arena, rodada com patrulha, vida e erguer) são da skill `character-show` — ela
COMPÕE os clipes daqui, não anima nada novo. O que ela precisa que cada clipe já traga:
- **Andar** com `walk->idle best_frame` no manifesto de export (o show começa a patrulha na fase que termina nesse
  quadro) e `ground_speed_m_s` medido (é a velocidade com que a raiz anda no show e na Unity).
- **One-shots que voltam à pose-base** (ataque, magia, invocação): o show cruza 5 quadros para o próximo clipe; um
  one-shot que termina longe da base estala mesmo cruzado.
- **Projétil assado** (`fx.py` grava `cf_fx_<fx>` na ação): o show e a engine tiram dele o quadro em que o alvo é
  atingido. Re-chaveou o efeito? Reconstrua a ação, senão o alvo apanha no quadro antigo.
- **`spawn` que cabe na invocação** (evento → `summon_end`) e começa enterrado (`sink`): o mesmo clipe serve para erguer
  um invocado de um corpo.

## 2f. Unidade SEM arma — as garras são a arma (FERRUGEM: `characters/ferrugem/anim/*.clip.json`)

`rig/landmarks.json` sem `weapon` / `onehand` → o `clip.sh` roda `freehands.py release=1 blend=0`: ele é dono dos dois
braços do quadro 1 ao fim. Tudo mora no bloco `free_hands` do clipe (cabeçalho do `freehands.py`):
- pose-base própria: `hub.clip.json` (`source: "hold"`, `pose_from: <NAME>_rest`, 3 quadros); todo clipe usa
  `pose_from: <NAME>_hub`. O `hubcheck.sh` compara com a ação de `pose_from`.
- `hands` = punho no espaço do PEITO `[quadro, esq, frente, cima, ease]`; `pole` = cotovelo preferido; `claws` =
  `[quadro, graus .01, graus .02, ease]` (curvar traz as pontas para a frente; o polegar acompanha).
- `swivel_samples: 180, swivel_hold: 2` em TODOS os clipes do personagem (a pose-base também): com o padrão 36 / 6 o
  cotovelo fica preso 20° fora depois de um arco grande (156 mm no fim do rastelo).
- `hand_length` = mão + garra MEDIDA (fatias do braço; 0,45 no FERRUGEM, padrão 0,15) e `tip_floor` em todo clipe que
  chega perto do chão — com o padrão as garras entraram 21 mm no piso na morte.
- **Chaves de punho param em toda chave** (ease por trecho, sem spline): para pêndulo / ciclo gere UMA chave linear por
  quadro de uma função (cosseno com atraso: braço de gorila 3 quadros atrás das pernas, arco +cos²); para golpe gere por
  slerp de DIREÇÕES na esfera do braço com o alcance à parte (antebraço curto: alcance = cotovelo; d 0,375 ≈ 60°).
  Geradores de exemplo no `_doc` / `free_hands._` dos clipes do FERRUGEM.
- Antes de chavear, MEÇA quanto o tronco projeta à frente da linha dos ombros contra o comprimento do braço (caldeira
  0,44 × braço 0,41: o punho nunca passa na frente; o golpe é nas laterais e a mão + garras viram para dentro).
- Idle com pêndulo + `hub_pin: ["all", 0]`: o pin tira o valor do quadro 1 de TODO quadro. Se as mãos não estão na
  pose-base no quadro 1 (atraso do pêndulo), elas ficam deslocadas o loop inteiro (29 mm). Faça a emenda num
  assentamento: tronco parado no centro 6–8 quadros, braços chegando — o quadro 1 é a pose-base de verdade.
- Morte de corpo largo à frente (barril): cai sobre o corpo, a cabeça fica livre; braços mantêm a direção do MUNDO durante
  o tombo (giram ~90° para a frente no espaço do peito) e pousam depois; pé redondo pousa pela borda (pitch −40° depois
  do tombo: o canto sola+frente para baixo). `boots_low_last_mm` no log do `limbfloor` tem de dar ~0.
- **Ciclo que é dono dos braços** (andar): `free_hands.cyclic: true`. O cotovelo lembra o quadro anterior; começando
  frio ele termina o ciclo noutro giro (FERRUGEM: chaves idênticas, emenda de 10,5 mm na mão e 36 mm nas garras → 0,0).
- **Golpe sem arma: meça a velocidade de MUNDO** (`motion_table.py` → `speed.hand_l / head / hips`), não a do gerador. O
  pulso no mundo é corpo + braço: chaves de golpe do tronco com `out` fazem o corpo saltar no início e FREAR até o
  contato (cabeça 29 cm num quadro). Golpe do corpo com `in` em 4 quadros, quadril 1 quadro à frente do braço: o pulso
  acelera até o contato (0,4 → 1,3 → 5,5 → 11,2 → 15,9 → 12,0 no hit) e a cabeça fica em ~6 m/s.
- **Braço de gorila no andar** (o que o vídeo mostrou): além do pêndulo para a frente, os dois braços ABREM para os
  lados em cada fase de balanço (3 quadros depois do pé) e o corpo rola sobre o pé de apoio (9°, 7 cm). 34° leu como
  "bater asa" (críticos, rodada 1): ~21° com PAUSA no topo (sobe 40 %, segura 15 %, desce 45 %, mais devagar que g),
  pulso ≤ 75 cm. Braço jogado para TRÁS passa na coxa: abdução mínima 0,5 × o balanço para trás (polegar 11 mm na perna).
  Mais rolagem custa perna: abaixe o andar até `hips_drop_max_cm` 0.
- **Pé de máquina CAI**: `gait.land: "drop"` (polish.py) — depois do topo do arco z = lift·(1 − s²), 0,5 → 2,5 cm/quadro
  até o chão; o seno chega PLANO (1,9–2,0) e lê como pé colocado. Pisão: tronco −2,4 cm em 2 quadros (`out`), peito
  +3° um quadro depois, cabeça +4° mais um; `heel_strike` 0 num pedestal.
- **Braço pendurado atrasa o giro do peito** (idle, estalos de yaw): seguidor amortecido do yaw (ω 0,55, ζ 0,75) e a mão
  girada de volta por (seguidor − peito) no espaço do peito. CONFIRA O SINAL pela velocidade da mão: errado ela adianta
  (0,45 → 0,86 m/s); certo, 0,38. Yaw + = para a esquerda dele: (esq, frente) → (esq + θ·frente, frente − θ·esq).
- **Barriga grande e pêndulo lateral**: a mão que balança PARA o corpo bate nele (33 mm dentro). Ela fica com ~20 % do
  balanço e escorrega pela FRENTE da barriga com o resto.
- **Garras apontando para o corpo** (mão ao lado da barriga depois do golpe): `free_hands.twist` aceita CHAVES
  `{"L": [[quadro, graus, ease?], ...]}` — gira a mão no antebraço (FERRUGEM: −45° tirou 97 mm do polegar; +45° piorou;
  meça os dois sinais e o chão, −45 no braço direito pôs o indicador 17 mm no piso → −25).
- **Morte com braços no mundo**: interpole o deslocamento ombro→punho por DIREÇÃO (slerp) + COMPRIMENTO; a reta corta a
  corda e o cotovelo fecha no meio (mão 32 mm no próprio braço). Repouso com alcance ≥ ~0,93 do braço no plano do chão
  (0,337 m deixou a mão 75 mm dentro do úmero). Garras de mão deitada: meça o sinal da curva contra o chão (neste rig
  curvar levantou as pontas: −6 → 57 mm no piso, +18 → limpo).
- **Contato com as peças rígidas que a unidade tem**: `landmarks.contact.things` (palmas, lâminas). Só com a cabeça os
  cinco clipes do FERRUGEM passavam "limpos" com garras 150 mm dentro do corpo. Não liste um osso cujas faces também
  seguem outros (o tambor no `spine.003`: falso 10 cm). Lâmina com casca aberta cruza a própria dobradiça desde o
  quadro 1: declare `contact.lap` com o motivo depois de olhar o close-up.
- **Gerador de caminho: nada de `max()` / `min()` duros entre curvas.** O valor fica contínuo, a derivada salta onde
  elas se cruzam: no andar do FERRUGEM (flare de um passo × abertura do balanço para trás) isso pôs 33 m/s² num quadro
  nas chaves do punho, que nenhuma folha mostrava. Use max arredondado `½(a+b+√((a−b)²+k²))` e rampa arredondada no
  lugar de `max(0, x)`, e meça a 2ª diferença das CHAVES (antes do build) e do punho no mundo (`motion_table`) depois.
- **Graus de giro do cotovelo enganam**: `swivel_jumps` = ângulo entre dois vetores de giro no mundo; com o punho
  andando 17 cm num quadro o eixo ombro→punho gira e o "salto" sobe sem o cotovelo saltar. Leia a corda em mm (3º número)
  e o `swivel_jump_chest_max_deg` (o giro no espaço do PEITO: o corpo carregando o braço não conta). Dano do FERRUGEM:
  13,8° no mundo, 1,5–6,2° no peito.
- **Número de mão é no MUNDO.** O README r2 do FERRUGEM disse "o punho cai 17 cm no recuo" (espaço do peito, com o
  corpo girando ao contrário); no mundo eram 46,9 cm num quadro, mais rápido que o golpe — os três críticos pegaram.
  Garra que bateu fica no lugar: escreva o punho no mundo depois do contato (base do peito gravada de um build, `BASIS=`).
- **Teto de altura que ACOMPANHA o ombro**: um teto fixo no mundo segura o punho enquanto o pisão baixa o ombro e a mão
  abre para fora (emenda 78,8 mm). `zcap + 0,8 × (z_ombro − z_ombro_topo)`: pulso ≤ 68,4 cm (era 75), emenda 46,4.
- **Passo em apoio simples**: margem negativa no passo de volta do dano (−2,8 cm, 5 quadros) se resolve rolando o
  tronco ~6° PARA o pé de apoio durante o passo (+0,7..+1,2), não alongando o passo.

## 2g. Prop GIGANTE na mão livre e o que foi medido no GRANIZO v3 (`characters/granizo/anim/*.clip.json`)

- **Sinais, medidos (não suponha)**: roll + em peito / tronco / cabeça BAIXA o ombro DIREITO (o hub v3 caiu para o lado
  da picareta uma rodada inteira com +6; −7 deu shL 0,987 / shR 1,088); loc `side` + é para a ESQUERDA dele; yaw − do
  tronco leva o ombro direito para trás; pitch − da cabeça = para cima/trás; no `onehand`, `aim` [elevação, rumo] com
  rumo + para a esquerda.
- **Cabeça isolada do Rigify + corcunda**: a cabeça não segue o peito. Toda dobra e todo roll do tronco levam a cabeça
  junto (chaves de `head roll` espelhando o `chest roll` no idle); para trás, no máximo ~−10°.
- **Segurar no spline pede chave duplicada**: a tangente vem dos vizinhos, duas chaves iguais (28, 60) ainda escorregam.
  Pose congelada = 28 `"in"`, 30, 60.
- **`still` não trava no mundo e `drag` continua depois da última chave**: com o tronco andando o prop `still` anda
  junto; a picareta com `drag` 0,2 seguiu balançando na vitória. Parada seca = `drag` 0.
- **Punho pendurado amplifica**: `up` do pulso livre em espaço do peito → altura do punho com ganho 1,3–1,8 (o braço
  dobra no balanço). Correção por quadro com ganho 1 passou do ponto; 0,55 convergiu (walk_b arrastando 0–1,6 cm).
- **Arrastar no andar no lugar é de graça**: o prop fica parado em relação ao corpo e o chão desliza por baixo. Onde o
  pé que balança cruza o punho (61 mm), o desvio de 20 cm por cima da bota virou uma batida do clipe.
- **O que um prop gigante NÃO faz** (meça antes de autorar): picareta plantada em pé na vitória (a mão pega a 21–37 % do
  cabo: o pomo só chega ao chão agachado); batida no peito com um punho de 0,6 m (todo caminho 13–46 mm dentro do peito).
- **Efeito de chão `spikes`** (`fx.py`): `layout: line` = rachadura até o alvo + 7 cristais em sequência (o último estoura
  no `hit`); `layout: cluster` = cristais crescendo em volta (morte-iceberg, coroa da vitória). `lean` [22, 14] escondeu as
  pontas DENTRO do corpo curvado; [6, 8–14] faz a jaula. Coroa ATRÁS dele: `radius` < recuo do centro (0,58 < 0,78).
  Aditivo sobre chão claro estoura para branco: cor [0,16, 0,55, 1,0] / núcleo [0,62, 0,9, 1,0] / força 1,15.
- **Veias de gelo** = `shock` com `links` em ordem (punho → cotovelo → ombro → crosta) + `zones` limitando o clipe a esses
  links (nada arcando para o chão).
- `step_out_of_first` de 367–381 mm num hit/morte pode ser osso de EFEITO (faísca nascendo de escala 0 no ponto do
  estouro): liste os ossos antes de caçar o "pulo".

## 3. Os cinco clipes

| Clipe | `kind` | Como nasce | O que conferir |
|---|---|---|---|
| attack | `attack` | take de ator retargetado + `layers`; perfil da arma autoral | antecipação com slow-in, golpe que só acelera, 3 quadros de hit-stop, assentamento VISÍVEL, saída num arco só |
| idle | `loop` | hold na base + respiração, troca de peso, olhar, um "heft" | o CORPO respira (≥ 2 px a 64 px), não a arma; nada parado; reversões desencontradas |
| walk | `loop` | `recipe.gait` paramétrico no lugar | `travel_render.py`: pé fica no disco (≤ 1 cm por contato); arma não balança mais que o corpo |
| hit | `oneshot` | camadas autorais base → base | recuo no 1º quadro, rosto livre, recuperação mais longa que o golpe, último quadro = base |
| death | `oneshot` | camadas + `floor: "body"` + `weapon.release` + `free_hands` | o golpe fatal é MAIOR que o dano comum; queda monótona; `ground_table.py`; prop solto sai pela FRENTE da queda |

**Toda chave é uma parada.** Uma camada interpola com ease ATÉ cada chave (velocidade zero em toda chave): certo
para extremos, gagueira para chaves de passagem a 1–2 quadros (cabeça a 2,0 / 1,5 / 2,2 / 1,4 / 3,1 m/s). Em camadas
de corpo (torso, peito, cabeça) use `"interp": "spline"`: UMA curva monótona por todas as chaves — plana nos extremos,
andando nas passagens, nunca além de uma chave; um ease escrito na chave (`"in"` do golpe, `"hold"`) continua valendo
no trecho dela. E menos chaves: um mergulho é início, fundo e volta.

Ciclo é anel: último quadro == primeiro, filtros periódicos, molas herdam a volta anterior. Os braços fecham em
ângulo FÍSICO (o `weapon.py` reporta `cycle_closed_deg`): a referência transportada quadro a quadro volta girada pelo
que o caminho encerrou (holonomia) — quanto mais o corpo mexe num idle, maior a emenda que isso abriria (6,4 mm). `hub_pin` prende as pontas
na base (`"all"` num hold; não em ciclo de marcha; nunca prender barba/tecido).

## 4. Massas soltas e props vestidos

Correntes novas entram por `landmarks.extras` + `secondary.chains`; `secondary.collide_prefix` (ex.: `["hair"]`) diz
quais colidem com o prop. Um rabo de cavalo que já nasce encostado nas costas marca contato de 2–6 cm quando a cabeça
joga para trás (dano, morte): olhe de costas antes de tratar como defeito.

- `secondary.py` escreve SÓ rotação (nunca `bone.matrix`: a escala de pose acumula); `clip.sh` reprova se
  `pose_scale_off` ≠ vazio. Teto de balanço por personagem em `landmarks.json → secondary.chains`.
- Prop vestido que entra na cabeça: regra em `landmarks.json → keepclear` (eixo fixo do personagem, teto em graus).
- Sobreposição que é do traje, não do movimento, é DECLARADA (`contact.lap`) com tolerância própria — nunca subir o
  portão geral.

## 5. Medir (depois de qualquer mudança)

```
./clip.sh <id> <NAME> <clip>
python3 cf/bl.py run blender/contact_probe.py --arg name=<NAME> --arg action=<NAME>_<clip> --arg out=<json>   # 6 mm; sem "penetrations"
python3 cf/bl.py run blender/motion_table.py  --arg name=<NAME> --arg action=<NAME>_<clip> --arg out=<json>
.venv/bin/python cf/path_plot.py <clip>_motion.json out.jpg [--window f0 f1]   # o ARCO da cabeça da arma, 1 ponto por quadro
```

`./contacts.sh <id> <NAME> <clip>...` roda as duas sondas e imprime uma linha por par: contato malha×malha (6 mm) e
**chão** (`floor_probe.py`, 5 mm: nada da unidade dentro do piso em nenhum quadro — corpo, props de `cf_props` E a arma
de `cf_weapon_prop`; `airborne` = quadros em que nada do corpo nem do que ele ainda segura toca o chão). O chão precisa de juiz próprio: nenhum render mostra o que está sob o piso — a morte do ALVOR passou em
tudo com a bota 6 cm enterrada, e quem achou foi a `bodyMinYCm` da Unity. Em clipe com `floor: "body"`: as chaves dos
pés estão no espaço da RAIZ (depois de tombar 90°, "atrás" é "embaixo" e `fwd` é "para cima"); chaveie as pernas
pousando 1 cm DENTRO do chão e o `limbfloor.py` faz disso um contato; cotovelos respeitam `weapon.floor_radius`.

Os cinco clipes têm de começar na mesma pose (≤ 1 mm) e os ciclos fechar (emenda ≤ 2 mm, correntes < 0,5°):
`./hubcheck.sh <id> <NAME> <clip>` (ataque primeiro) dá os três números e o maior passo por quadro de cada osso.

Leia a `motion_table` como o crítico lê: velocidade da cabeça quadro a quadro (serrilhado = chaves demais), altura do
quadril (platô = limite das pernas), faixa de altura da cabeça da arma contra a do quadril, `slip` e `under_floor`.
Sinal de build contaminado: pose-base agachada, `lean_in_out.torso.fwd` perto de 90°, `foot_pull_in` de dezenas de
cm — o clipe herdou a pose do que estava na tela (corrigido: `retarget.py` e `polish.py` partem de pose limpa; se
voltar, alguém atribuiu uma action sem `cflib.assign_action`).

## 6. Os 12 princípios, conferidos no tamanho de jogo

A unidade tem ~64 px na tela: 1 px ≈ 2 cm. O que não mexe 2 px não existe. Do veredito de princípios da rodada 9:

- **Antecipação**: o mergulho não pode ser o movimento mais rápido do clipe (era 3,8 m/s contra 3,4 do golpe). Entre com
  slow-in e troque espera por percurso.
- **Follow-through**: depois do hit-stop o corpo assenta de forma visível (squash do tronco, cabeça acena, prop quica
  6–9°) e a saída começa cedo; 17 quadros parados leem como quadro congelado.
- **Arcos**: desenhe o caminho da cabeça da arma (`path_plot.py`). Um chute lateral de 20 cm na saída do golpe não
  aparecia em nenhuma das seis câmeras.
- **Peso consistente**: a arma não pode subir mais rápido do que desce, nem balançar 3× o corpo no andar; quem paga
  cada movimento da cabeça da arma é o tronco.
- **Ação secundária**: respiração no peito/ombros; olhar ≥ 20° de cabeça (8° = 1 px); o gesto de personagem tem de
  aparecer na câmera de jogo.
- **Exagero em escada**: morte > dano > idle. Compare o deslocamento do primeiro quadro entre os clipes.
- **Sobreposição**: quadris arrancam 2–3 quadros antes dos braços; mãos não pousam no mesmo quadro; reversões não caem
  todas na emenda do ciclo.
- **Afirmação escrita tem de bater com a imagem**: se a receita diz "o rosto fica legível" ou "a cabeça do martelo
  desliza", meça. Três afirmações do primeiro personagem perderam para as fotos.

## 6b. Os princípios de JOGO no clipe: leitura, essência, golpe, bando, close

Os 12 princípios (§6) dizem se o movimento é bom; estes dizem se ele FUNCIONA num jogo mobile visto de cima a 64 px.
Cada item tem o número e onde conferir. O juiz final é o laboratório da arena na Unity (skill `character-show` §9d),
com os blends da engine — não o viewport.

### Leitura das poses (um relance)

- Cada clipe tem 1–2 **poses-chave** que contam a ação sozinhas, como silhueta, na câmera de jogo (55° de cima):
  ataque = preparo (extremo da antecipação) + contato; dano = recuo do 1º quadro; morte = o corpo no chão; invocação = o
  gesto-assinatura. Confira essas poses no laboratório (tecla V: silhueta 1:1, `+1 quadro` para parar nelas) e no
  pacote de revisão (silhueta 64 px). Pose que vira mancha = refaça a pose, não o tempo.
- **Movimentos largos**: o preparo leva a cabeça da arma a ≥ 0,35 × a altura da unidade do repouso (≥ 22 px a 64 px);
  o tronco inclina ≥ 10–15° para dentro do golpe no contato; olhar de cabeça ≥ 20° (8° = 1 px, §6). Vista de cima, a
  extensão PARA A FRENTE e PARA O LADO lê; para cima/baixo encurta (cos 55° ≈ 0,57): exagere o que vai na direção da
  câmera de jogo.
- A pose de contato aponta o prop/membro TODO para o alvo, fora do contorno do corpo — é o quadro que o jogador vê
  congelado pelo hit-stop.

### Essência no movimento

- Leia a tabela traço × clipe do brief (skill `character-design` §0b) antes de autorar cada clipe e escreva, no topo do
  `clip.json` (`_doc`), qual traço o clipe amplifica e COMO (um número: graus, quadros, cm). Um clipe que não mostra
  nenhum dos 1–2 traços é genérico — o crítico de princípios recebe a pergunta "o traço X aparece aqui?".
- Ritmo é personalidade: o pesado demora no preparo e é curto no golpe; o ágil tem preparo curto e mais quadros de
  assentamento; o frio não tem movimento secundário rápido (OCASO anda a 0,32 m/s e o momento dele é a invocação).

### O tempo vende o golpe (contato claro + segurar o impacto + efeito + tela)

Tempos atuais (30 fps, `export/<NAME>.json → clips.attack.events`):

| Unidade | Ápice do preparo | Contato (`hit`) | Assenta | Total | Contato em s |
|---|---|---|---|---|---|
| OSSINHO | 8 | 12 | 22 | 28 | 0,37 |
| FERRUGEM | 16 | 23 (+ `rake2` 28) | 33 | 54 | 0,73 |
| OCASO (cajado) | 16 | 24 (`land` 28) | 47 | 54 | 0,77 |
| ALVOR | 16 | 25 | 40 | 58 | 0,80 |
| BRASA / GRANIZO | 17 | **40** | — | **85** | **1,30** |

Regras:
- **Golpe curto**: do ápice do preparo ao contato ≤ 4 quadros no leve (OSSINHO 4), ≤ 9 no pesado (ALVOR 9); nos 3
  quadros antes do contato a ponta percorre ≥ 50 % do arco (o "estalo": velocidade da ponta crescendo até o contato,
  `motion_table → speed.<arma>_head`, §2b "espaçamento"). O contato de um corpo a corpo cai até ~0,8 s do início do
  clipe. BRASA e GRANIZO (23 quadros do ápice ao contato, contato a 1,30 s) estão FORA desta regra: limite conhecido
  dos martelos, a refazer quando forem retemporados.
- **Quadro de contato claro**: o evento `hit` cai EXATAMENTE no quadro de extensão máxima (a ponta no alvo). `drag` na
  arma atrasa o contato 1 quadro: golpe que tem de acertar no evento leva `drag 0` (TECHNIQUES, "Hold on impact"). No
  laboratório: velocidade 1/10, Encostar, Atacar, e `+1 quadro` até o leitor mostrar `[HIT-STOP]` — o quadro mostrado
  ali (`attack 25/58`) é a pose congelada que o jogador vê. Se não é a pose de contato, o evento está errado.
- **Segurar no impacto**: o clipe segura 2–3 quadros no contato (assentamento visível depois, §6); a engine soma
  `hitStop` 0,06 s (≈ 2 quadros) congelando atacante E vítima, e `killStop` 0,13 s no golpe que mata. Total parado no
  contato: 4–6 quadros num golpe comum, 6–8 na morte. Ajuste no laboratório (hit-stop −/+, 20 ms por clique) e
  registre o valor no `state.json` do personagem se ele pedir outro.
- **Efeito e tela no mesmo quadro**: no evento `hit` a engine solta a faísca (`CFBattleFx.Spark`), congela os dois e
  manda o `Struck` → a câmera da arena treme (0,35–0,9° pelo dano, 1,5° na morte, decai em ~0,1 s) e dá um soco de
  FOV (0,9° / 2,2°). Clipe de magia: o dano e o tremor são no `land` (o projétil pousa), o lançador NÃO congela.
- **Escada de exagero na engine também**: dano comum < golpe que mata (killStop > hitStop, tremor 1,5° > 0,9°, faísca
  1,8× no raio da morte).

### Pequenas variações num bando (truque barato, efeito grande)

- Unidade que vem em grupo (OSSINHO, toda invocação, todo esquadrão) não pode andar em passo: duas cópias iguais lado a
  lado leem como clones.
- **Piso, já na engine** (`CFBattle.varySquad`): cada invocado ganha velocidade de Animator ×0,92–1,08 e tamanho
  ×0,95–1,05, determinísticos pela chave da unidade (sequência de razão áurea — um hash de vizinhos deu ×0,93 aos dois
  esqueletos de uma mesma invocação); a velocidade de chão do andar segue velocidade × tamanho, então o pé não patina.
  Medido: OSSINHO_A ×1,04 / 0,97, OSSINHO_B ×0,98 / 1,05.
- **O truque inteiro (próximo passo)**: 2–3 andares por unidade de bando (`walk`, `walk_b`, `walk_c`) — mesmo período
  ±2 quadros, mesma pose do quadro 1 e mesmo `enter_phase`/`leave_phase` (contrato da engine), mas balanço do quadril
  ±20 %, braço da arma em outra altura, cabeça inclinada para um lado, um passo mancando. Cada variante tem seu
  `ground_speed_m_s` no manifesto; a engine escolhe pela chave. Comece pelo OSSINHO (é o único bando hoje).
- Primeiro `walk_b` feito: GRANIZO (2026-11-14), o machado APOIADO NO OMBRO (o `walk` balança ao lado), período 30
  (walk 32), 0,742 × 0,756 m/s, silhueta 30–36 % diferente na mesma fase a 64 px. Duas lições: (1) arrastar a arma
  atrás do corpo some da câmera de jogo quando a unidade vem para a câmera (lê desarmado) — a variante tem de mudar
  o que se vê de cima e dos dois lados; (2) um loop cuja pegada é longe da pose-base precisa de `weapon.lock_hub: false`
  (o solver prendia o 1º quadro no cotovelo e giro da pose-base: cabeça do machado 117 mm dentro da cabeça).
- No laboratório: Invocar 2–3 vezes, depois Andar (esteira no lugar) — os esqueletos têm de estar em fases diferentes
  do ciclo depois de 2 s.

### Momentos de close (vitória, desbloqueio, menu) = personalidade

- O take **Retrato** da arena vira o vencedor para a câmera e o inclina ~7° para trás pelos pés; se o personagem tiver
  um clipe `victory` (ou `celebrate` / `cheer`), a arena o toca nesse momento. O primeiro é o do GRANIZO
  (`characters/granizo/anim/victory.clip.json`, 2026-11-14): copie dele.
- O que o GRANIZO ensinou no `victory` de uma mão: (1) o troféu erguido com o braço levantado deixa o cabo em linha com o
  antebraço → bracelete 36,8 mm; antebraço HORIZONTAL e cabo em pé (aim ~110°, cabeça um pouco para trás) = 0;
  (2) parada, a lâmina rola para o conforto do pulso e mostra o FIO à câmera: `weapon.edge` [[f, esq, frente, cima]]
  (espaço da unidade) aponta o fio para o lado e mostra a face larga da cabeça; (3) olhos que acendem = dois `flame`
  pequenos (`size` 0,05, `level` 0 por padrão) no osso da cabeça, na posição dos olhos achada pela cor da textura.
- `victory`: one-shot de 1,5–2,5 s que termina numa pose SEGURADA (`hold_last_frame`), o traço da essência no máximo
  (o teimoso bate o martelo no chão e estufa o peito; o frio só ergue o cajado e inclina a cabeça). A raiz NÃO gira (a
  engine gira e inclina); cabeça erguida 5–10° na pose final; mãos e prop longe do rosto; expressão de rosto se o rig
  tiver os ossos (skill `character-rig` §0).
- Julgue no Retrato (laboratório → botão Retrato, ou depois de um nocaute): rosto no terço superior, nada na frente
  dele, a expressão lê a ~400 px de altura de corpo.

## 7. Referência em vídeo = o próprio personagem, membros coloridos

Decisão do usuário. Por clipe: `blender/limb_paint.py --arg mode=on --arg still=mocap/char_color_still.png` →
`cf/runware.py video --model bytedance:seedance@2.0 --first-frame …` (o prompt repete as cores e trava a câmera) →
`cf/colorpose.py track` / `remap` → `blender/board.py --arg sequence=…` (vídeo ao lado, sincronizado) →
`./refcheck.sh <id> <NAME> <clip> <tag>`. `reference.role: "gate"` (idle, andar: < 0,06 geral, nenhum membro > 0,10)
ou `"beats"` (dano, morte: o vídeo só dá os tempos — não chame o número de aprovado). A métrica de cor de uma vista não
vê profundidade: é portão, não objetivo. Ator humano (Kling) só para o take de mocap do ataque; pose 3D em personagem
estilizado falha. Job Seedance preso em "processing": o cliente desiste em 1500 s SEM cobrança (confira `runware.py balance` antes e
depois). Relance UMA vez (só com `--first-frame`); se prender de novo, reporte — no GRANIZO os dois jobs prenderam e
o personagem ficou sem referência (declarado em `state.json → reference`), não invente o portão.
A referência é do personagem COMO ELE É: se ele ganhar um prop ou mudar de guarda depois dos vídeos (ALVOR ganhou o
escudo), arquive os antigos (`mocap/v1_*`), refaça o still colorido na pose-base nova (esconda a malha de efeito; escolha
a vista em que os quatro membros aparecem — um escudo de frente tapa tudo) e gere de novo. ~US$ 0,80 por vídeo:
confira o saldo, anote em `costs.jsonl` e no `state.json`.

Como LER a comparação (OCASO / OSSINHO, vídeos feitos depois dos clipes — vale também para auditar um clipe pronto):
- A posição absoluta carrega um deslocamento comum quando o rastreador lê brilho do piso como torso (torso 0,44 em
  toda versão): compare o membro RELATIVO À CABEÇA (centro − centro da cabeça) e o EIXO do membro. Foi assim que o andar
  do OSSINHO mostrou o que a nota geral escondia: armR 0,078 / 25,6° → 0,059 / 12,2° com a nota geral parada em 0,19.
- Leia o erro por quadro RELATIVO À CABEÇA (dx, dy, ângulo do eixo de cada membro) antes de mudar chave: no andar do
  FERRUGEM foi isso que mostrou os braços do vídeo abrindo 0,2 da altura para os lados a cada passo. Vídeo assimétrico
  (um passo abre os braços, o outro não) não se copia num ciclo de jogo: fique simétrico e declare o número.
- Varra a fase do `time_map` (`colorpose.py compare --map` com 0..período de deslocamento): se as pernas têm o mínimo
  no deslocamento 0 e um braço não muda com a fase, o erro do braço é de POSE, não de tempo.
- Arma de uma mão no andar: a lâmina ANDA COM O ANTEBRAÇO (em pé quando a mão vem à frente, deitada para a frente
  quando desce ao quadril). Chaveada ao contrário o punho encosta no limite (55,7° de 60) e a lâmina tapa o rosto.
- Emenda de ciclo "assimétrica" em metros de mundo: compare com o OUTRO extremo do ciclo antes de mexer em chave —
  as pontas da spline já têm tangente zero no espaço do peito; o que sobra é o tronco carregando o braço.

### Lições da rodada 2 do ALVOR (pés, queda, mão livre)

- **Pé que gira no chão gira sobre a bola**: `rot yaw` no `foot_ik` gira no TORNOZELO. Junte `loc side/fwd` =
  `v − R(yaw)·v` (v = tornozelo → bola) e, se o calcanhar sobe, `pitch` + `loc up` = braço × sen(pitch). Confira com
  percurso de calcanhar × ponta (o `slip` do `motion_table.py` não vê giro no lugar).
- **Passo de volta**: o tronco muda de pé (chaves `torso fwd/side`) 2–5 quadros ANTES de o pé sair; o pé sobe ≥ 5 cm.
- **Guarda de lado + queda de costas**: o yaw da guarda vira roll no chão. Meça a altura dos dois ombros no último
  quadro e acerte `chest roll` até igualarem; depois confira `ground_table.py` (costas, peito, cabeça, mãos).
- **Mão que soltou a arma**: `weapon.hand_floor` = espessura real do punho; `finger_floor` / `finger_radius` mantêm
  os dedos fora do piso. Prop que repousa sobre o corpo: desça até o portão dizer "touches" com 3–5 mm.
- **Loop com `drag`**: a mola já roda sobre o período; se `last vs first` passar de 1 mm, é chave, não mola.
- Leia a saída INTEIRA do `contacts.sh` (as linhas de penetração vêm primeiro).

## 7b. QUADRÚPEDE: andadura gerada, chaves por cima, solucionadores (UIVO)

- `./quad_build.sh <id> <NAME> <clip>...` = `blender/quad_clip.py` (andadura + chaves + molas + solucionadores, medido) +
  `fx.py` com o bloco `fx` do clipe. Reconstruir joga a action fora: os efeitos SEMPRE são rechaveados junto.
  Cabeçalho do `quad_clip.py` = o contrato (parâmetros em graus/metros: `torso_*`, `hips/chest/neck/head_*`, `head_level`,
  `jaw`, `ear*`, `tail1..4_*`, `scap_*`, `paw_<FL|FR|RL|RR>_x/y/z/curl`, `follow_<pata>`; `torso_pivot`; `solve`).
- Loop com `gait`: touchdown / duty / lift / curl / toeoff / reach / scap / bob / pitch / flex / surge / roll / yaw /
  head_level / tail / ears / jaw por fase. A pata de apoio anda +S/2 → −S/2 (S = v × duty × T): patinação 0 por construção.
  Galope (UIVO 14 f, 4,4 m/s) e meio-galope (25 f, 2,18 m/s) já calibrados em `characters/uivo/anim/`.
- One-shot: só chaves (geradas por um `make_clips.py` do personagem a partir da pose-base do idle — todo clipe começa nela).
  `follow_<pata>` = a pata vai com o corpo (morte de lado, empinar); `head_level` = a cabeça do caçador fica estável.
- Solucionadores (relatório `solve`): `paw_floor` (almofada de pele abaixo do chão → sobe o alvo), `reach` (vão na cadeia,
  dedo que não chega E o osso DEF que ESTICA — o Rigify esconde a falta de alcance esticando a canela: 3,6 % → pele 0,69 cm
  no FBX; pata plantada de andadura não é puxada, viraria patinação), `body_floor` (morte, sentar: o chão é o alvo).
  Se o `body_floor` precisa erguer muito, a pose está errada (o uivo sentado subiu 7,4 cm e as patas da frente flutuaram 6 cm).
- Portão: `reach` ≤ 0,05 cm, `stretch %` ≤ 2,5, `floor` ≥ −0,5 cm, `slip` 0 (exceto deslize autoral, ex. o dano), e OLHE
  de lado e em 3/4 (`strip`) — a métrica não vê "parece cachorro pedindo".
- Referência Seedance (§7) num quadrúpede: o tempo do usuário manda, o vídeo dá a FORMA. Rode o `refcheck.sh` em todos os
  clipes com bloco `reference`; no UIVO ele mudou dois: ataque (encolher BAIXO e esticar num bote longo) e vitória (uivo SENTADO).
- **`end` de todo one-shot** (`home` padrão / `hold` / `chain`): com `home` as molas assentam nos últimos `settle` quadros
  (8) e o último quadro É a pose-base; o que desloca a pata (empurrão do dano) tem de VOLTAR num passo (sobe, viaja no ar,
  pousa na vertical) — "a próxima transição leva para casa" fez o export marcar o dano como HOLD e a Unity travar o lobo.
  Morte e vitória: `"end": "hold"`; o dash que termina no alvo: `"end": "chain"`.
- **Interpolação padrão = spline** (Hermite monótona, Fritsch–Carlson): o smoothstep antigo PARAVA todo canal em toda
  chave — 60+ canais parando juntos é o "robótico" que o usuário viu em todos os clipes. Ease explícito (`in` / `out` /
  `lin` / `hold`) continua valendo onde se quer parada; loop: tangentes dão a volta na emenda. Andaduras também levam
  molas (`GAIT_SPRINGS` no `make_clips.py` do UIVO: cabeça pelo balanço do tronco, pontas das orelhas, cauda 2–4).
- **Idle de caçador olha em sacadas** (vira em 3 quadros com `out`, segura, vira) — um seno lento na cabeça lê como torreta.
- **Morte com batidas** (UIVO r2, 60 f): impacto (ganido) → cambaleia (uma pata SAI para o lado) → as traseiras cedem →
  a frente dobra → rola de lado com `in` → quica → assenta → membros por molas da rolagem → último suspiro → chute e
  garra. `follow_*` entra durante a queda. O `body_floor` recalcula a elevação NECESSÁRIA a cada passada (somar
  flutuava 6,5–13 cm).
- **Morte de quadrúpede = DE LADO, rolada PASSANDO de 90°** (UIVO r3, 52 f; a de barriga do r2 leu como "agachado vivo"
  nos três críticos, e a de peito com as patas abertas leu como "vai dar o bote"). A parte mais LARGA decide como ele
  deita: a 86° a juba escora a frente (quadril 19 cm, cabeça 10 cm no ar). Role até ~111°: o flanco de trás desce antes
  da juba e as patas de cima caem sobre a barriga. Duas regras da ordem `Rz(yaw) Ry(roll) Rx(pitch)` do `quad_clip`:
  o pitch do tronco num corpo rolado inclina o eixo longo no mundo por `sen(p)·cos(roll)` (p −22 a 111° = traseira 7,7°
  abaixo), e depois de ~90° o YAW relativo de quadril / pescoço / cabeça vira para o chão (yaw + = para a esquerda dele =
  para baixo). Resultado: cabeça no chão (pescoço 1,5 cm), elevação 14,4 → 7,5 cm. As patas-pivô seguram `follow`
  0 → 0,15 até o corpo passar por cima delas. A ALTURA na câmera de jogo quase não muda (67 × 118 px deitado × 71 × 129
  em pé): de 55° de cima a profundidade de um corpo deitado projeta como em pé — julgue a FORMA (patas para fora,
  barriga para cima), não os px.
- **Leia `paw_fix_at`** (quadro da maior correção de cada pata no relatório `solve`): a correção de 8,8 cm da morte era
  no meio do tombo (f19), a da vitória em f35/f52 — não na pose segurada.
- **Cauda que VARRE o chão levanta o lobo inteiro**: atravessando a linha do meio a ponta toca o piso, o `body_floor`
  ergue o corpo 3,8–5,2 cm e as patas da frente (já no alcance máximo sentado) saem 15–21 cm do chão. Varra de UM lado
  (yaw 14 → 28 → 12): elevação 0. E o sentado não inclina mais do que as patas da frente alcançam (21°; 25–32° as
  levantou 9–21 cm) — a altura do uivo vem do pescoço e da cabeça (77–79 px; meta 85 não alcançada, declarado).
- **O passo SOBE antes de viajar**: z da pata adianta y em um quadro. Com o `out` no mesmo quadro da subida, a sonda de
  deslize da engine (bola da pata abaixo de 7,5 cm) contou os primeiros 5 cm do passo como patinação.
- **Peso do pouso é FERRAMENTA, não chave: `gait.land`** `{"F": [queda, a, b], "R": [...], "pitch_F", "pitch_R", "head"}`
  — por pata, depois do toque: queda rápida (seno em `a` quadros) e rebote (cosseno em `b`), focinho para baixo no toque
  da frente, a trava da cabeça cede na queda. Quatro toques = quatro batidas (o bob em cosseno era "uma onda, nada
  pousa"). Meio-galope: frente 2,5 cm / 1,5 + 3,5 f, trás 1,2 cm; galope: frente 3 cm / 1 + 2,5 f.
- **`surge` é de graça se estiver EM FASE com o empurrão**: 0,065 m na fase 0,42 esticou a perna de trás 4,55 %; na fase
  0,3 (corpo mais à frente no toque da frente) 1,34 %, patinação 0. Varra a fase antes de reduzir a amplitude.
- **O bote termina NA mordida**: `dash_bite` = one-shot cujo quadro 1 É o último quadro do dash (lido do
  `sprint.clip.json` pelo `make_clips.py`): o embalo leva o corpo 14 cm, as patas da frente derrapam (planejado), a
  mordida crava no f3 (`hit`), sacode, morde de novo (`hit2` f17). Dash → pousar → encolher → morder era blocker de
  princípios.
- **Vento para a câmera de CIMA** (`fx.wind` nos landmarks): crescentes deitados (`arc_rolls` dentro de ±35°; 55–90°
  ficavam de pé = palitos vistos de cima), raio 0,65, ápice 14 cm à frente do focinho (`arc_lead`), núcleo fino e quente
  (`arc_core` 0,045); riscos ≥ 5 cm de largura (2 px) e ≥ 0,5 m, nascendo atrás dos ombros e FORA da silhueta; o
  meio-galope não tem vento; o dash apaga no último quadro e o `dash_bite` leva o decaimento.
- **Trocar a pose-base = camada ADITIVA, não reescrever chaves** (UIVO r4, agachado de caça da referência): `"layers"` no
  clip.json (cada conjunto de chaves é somado por cima de `keys`). O `make_clips.py` guarda a pose antiga como referencial
  de autoria (`HOME_R3`) e a camada 0 de cada clipe = (pose nova − antiga) × peso por grupo (`body` / `head` / `tail` / cada
  pata, ou um canal só): 1 nos one-shots que saem e voltam à pose, some quando o corpo sai dela (morte, vitória), entra na
  recuperação (`dash_bite`). A parte de uma pata PLANTADA só muda com ela no ar ou num deslize planejado (mantida até o
  tombo, a morte precisou erguer o corpo 17 cm). Pose mais baixa = menos espaço para o agachamento do golpe: peso 0,45–0,5
  em `torso_z` / `torso_pitch` durante a ação (peito −3,9 cm e antebraço −1,7 cm no chão com o deslocamento inteiro).
  Cabeça só para BAIXO some na juba: pescoço para a frente e para baixo (−28) com a cabeça erguida (+21).

## 8. Mostrar

`blender/reel.py` monta idle → andar ×3 → dano → ataque → morte; `blender/play.py --arg name=<NAME>
--arg action=<NAME>_reel --arg 'view=[52,9]' --arg mode=play` deixa tocando para a filmagem.
