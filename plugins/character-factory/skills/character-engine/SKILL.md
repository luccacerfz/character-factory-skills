---
name: character-engine
description: Levar um personagem da Character Factory para a engine — export FBX com nomes Mixamo, LODs e manifesto de contrato, cópia para a Unity, import automático (materiais, clipes com eventos, efeitos aditivos, Animator, prefab), invocador com o prefab das unidades (CFSummoner), ataque à distância (projéteis e evento land), prop que balança e morre (boneco de treino — CFWobble, tabela de queda), medição dentro da Unity e transições sem pé patinando (PinStep, WalkPinStep). Use quando o usuário pedir "exporta", "manda para a Unity", "FBX", "importa na engine", "o pé escorrega na transição", ao fechar os clipes de um personagem, ou ao levar um alvo de treino / invocador para a engine. Inclui o "sentir" na engine: hit-stop, tremor de câmera no golpe, variação de bando e transições do Animator afinadas no motor e salvas por personagem (blend_tune.json).
---

# Engine: export + Unity

Regras de operação: skill `character-factory`. Detalhes do contrato: `factory/README.md` ("Engine (Unity)").

## 1. Export

```
python3 cf/bl.py run blender/lod_show.py --arg name=<NAME> --arg mode=hero     # exportar sempre com a malha hero à mostra
python3 cf/bl.py run blender/lit_gain.py --arg name=<NAME>                      # se tem fumaça/poeira/vapor: o brilho que a luz dá a ela
python3 cf/bl.py run blender/export.py --arg name=<NAME> --arg 'clips=["idle","walk","attack","hit","death"]' \
        --arg out=$PWD/characters/<id>/export/<NAME>.fbx                         # `clips` e `out` são obrigatórios
python3 cf/to_unity.py characters/<id>/export ../Assets                      # cria Assets/Characters/<NAME>
```

Saída: `characters/<id>/export/<NAME>.fbx` + `<NAME>.json` (manifesto): esqueleto limpo com nomes Mixamo, no máximo 4
influências, corpo LOD0/LOD1, cada prop como malha própria em um osso, clipes como strips NLA, eventos, convenção de
ciclo (período + 1 quadros), `ground_speed_m_s`, `enter_phase` / `leave_phase`, `stance_yaw_deg`.

O manifesto também leva: `fx` (malhas de efeito, material `"blend": "additive"` + `strength` = a emissão aprovada no
Blender; o importador usa o shader aditivo de partícula e multiplica a tinta), `matte` por material (o `to_unity.py`
assa no metal/suavidade) e, para arma de uma mão, `hand_prop`. Os ossos de efeito (`Fx*`) ficam sob a raiz e animam
por escala: o importador liga `updateWhenOffscreen` e tira sombra desses renderers.

Conferir no relatório do export:
- `round_trip.meshes_missing_in_file` vazio (um objeto com `hide_select` era pulado sem aviso pelo exportador por
  seleção: a aura do ALVOR ficou fora do FBX e a Unity recusou o import);
- ida e volta do FBX ≤ 0,05 cm em todo osso e todo quadro (o bake decompõe cada osso contra o pai reconstruído; sem
  isso a escala não uniforme do Rigify cisalha 6–8 mm nos dedos);
- **ida e volta da PELE** (`round_trip.skin_round_trip`, por clipe): `max_cm` ≤ 0,5 e `file_lowest_cm` ≥ −0,3. A junta
  exata não diz nada de uma bota 20 cm abaixo dela: o FERRUGEM passou na ida e volta das juntas (0,021 cm) e na sonda
  de chão do Blender, e a Unity mostrou a bota 1,16 cm DENTRO do piso. Causa: pai com escala não uniforme (o estica do
  IK do Rigify) + filho girado = cisalhamento, que TRS não guarda. O bake agora faz os PAIS semelhança no mundo (ou
  (a, b, a) quando os filhos só torcem — decidido por clipe) e só as folhas guardam escala por eixo
  (`skin_fit.parents_axial`, `parent_anisotropy_dropped`, `parent_skin_worst_cm` no relatório). Um squash por ESCALA
  chaveado de propósito num osso com filhos apareceria em `parent_anisotropy_dropped` — chaveie-o numa folha;
- personagem com rig ANTERIOR à regra "sem B-bones" do `rig_build.py` (GRANIZO): conte os ossos de deformação com
  `bbone_segments > 1` ANTES do export e zere para 1 — a ida e volta das juntas passa (0,004 cm) e a da pele falha
  por 9,6–15,9 cm (torção ao longo do osso não move cabeça nem ponta); depois disso, re-meça `./contacts.sh`;
- efeito de CHÃO não é projétil: só `cf_fx_*` com `lands` (bolt / hex) vira `projectiles` (que o
  `CFProjectileRetarget` puxa para a linha do alvo). Os `spikes` do GRANIZO v3 (rachadura + cristais) vão para
  `ground_fx` + evento `<fx>_arrive` (ataque 29 = `hit`); antes o export quebrava com `KeyError: 'lands'`;
- `height_m` igual à altura da malha de bind (lida de `mesh.vertices`; `bound_box` é a malha posada);
- o prop exportado está onde o `weapon.grip` diz.

## 2. Unity

Instância: Unity 6 + MCP for Unity (ver memória `characterfactory-unity-mcp`). Depois do `to_unity.py`:
`refresh_unity` (mode force, scope assets) → `execute_code`:
`return CharacterFactory.EditorTools.CFImporter.Import("Assets/Characters/<NAME>");` (o nome completo do namespace é
obrigatório no compilador C# 6 do MCP; menu equivalente: *Character Factory ▸ Import All Characters*). Para capturar:
`CFImporter.BuildShowcase(dir)` primeiro (cria `Assets/Scenes/<NAME>_Showcase.unity` e ABRE essa cena no lugar da
atual), depois `CFImporter.Capture(dir, clip, t, "Captures/x.png", w, h, camPos, lookAt, fov, -1)`.

- **Antes do `refresh_unity`, leia `mcpforunity://editor/state`**: se `play_mode.is_playing` (sessão do usuário, ex.
  `Duel_Arena`), NÃO importe — o refresh reimporta o FBX e regenera prefab/Animator de um personagem que está em cena.
  Rode só o `to_unity.py` (copia os arquivos) e deixe `Import` + `MeasureTransitions` como pendência no `state.json`
  (GRANIZO v3, 2026-11-14).
- Rig **Generic**: o Humanoid mapeia sozinho com nomes Mixamo, mas a reprodução em músculos desvia centímetros e solta
  a pegada de duas mãos; o importador mede e decide.
- Animator: repouso = estado padrão; marcha = bool com `offset = enterPhase`; one-shots = triggers; duração da
  transição pela ORIGEM (repouso 0,06 s, marcha 0,15 s, one-shot 0,08 s — padrões; afináveis por personagem no
  laboratório, `<NAME>.blend_tune.json`, §2e); prioridade morte → dano → ataque → marcha;
  a morte segura o último quadro.
- Saída da marcha: `CFCharacter.PinStep` prende o pé de apoio e move a unidade no lugar dele, com teto
  (`pinMaxCarry` = velocidade × 0,18 s). No toque do calcanhar a bola do pé ainda está no ar: teste o tornozelo; com
  os dois no chão vale o pé da frente. Sem teto a unidade dá um bote de até 31 cm.
- Parar no pé certo: rode `CFImporter.MeasureTransitions(dir)` DEPOIS de cada `Import` — ele mede a patinação por
  fase, grava a janela de saída no prefab (`leaveFrom/leaveTo/maxPhaseWait`) e mede de novo com a parada esperando
  (`CFCharacter.SetMoving(false)` + `StopStep`). O jogo move a unidade enquanto `IsMoving` e pode pedir a parada quando
  faltar `StopDistance` até o destino. ALVOR: 13,6 / 36,6 cm (média / pior) → 0,9 / 4,7 cm; espera até 0,72 s.
  Personagens importados antes (janela 0/0) não esperam: comportamento antigo.
- **Atacar no pé certo**: `CFCharacter.PlayWhenPlanted("attack")` espera a mesma janela (a unidade segue andando
  enquanto `IsMoving`), depois dispara o gatilho e prende o pé de apoio. ALVOR, 28 fases: andar→ataque 12,2 / 36,0 cm
  (média / pior) → 2,4 / 4,0 cm; espera até 0,68 s (média 0,26 s). `Play` continua sendo o disparo imediato — use-o
  para reações (dano, morte). Quem avança o Animator à mão chama `PlayStep(dt)` depois de cada `Animator.Update`.
  `Play` também CANCELA um golpe pendente (um dano durante a espera disparava o ataque por cima da reação — achado
  por um crítico lendo o C#): toda ação adiada precisa de quem a cancele, e de uma linha no `MeasureTransitions`.
  O histórico do `execute_code` some a cada recompilação. Capturas do pacote (ALVOR, 560×460, fov 34): câmera de jogo
  `camPos (1.3, 3.1, 2.6)` → `lookAt (-0.15, 0.45, -0.35)`; lateral baixa `(-3.6, 0.75, -0.3)` → `(0, 0.5, -0.45)`;
  tempos idle 2,05 · walk 0,3 · attack 0,5 / 0,8 · hit 0,2 · death 0,25 / 0,6 / 1,2 / 1,45 / 1,95 s; repita com
  `forceLod` 1 para a linha de LOD1.
- O `execute_code` do MCP compila C# 6 (sem funções locais nem tuplas). O Play mode não avança com a Unity em segundo
  plano: avance `Animator.Update` à mão para medir.

Segundo personagem (GRANIZO): export + cópia + import + showcase + capturas rodaram sem tocar em código — o contrato
é o manifesto, não o personagem.

Leia `bodyMinYCm` do relatório da Unity (o ponto mais baixo do corpo em todos os clipes): abaixo de −0,5 cm há algo
dentro do chão — volte ao `./contacts.sh` (linha `floor`). No ALVOR esse número (−6,0) achou o que nenhum render mostrava.
`bodyMinYCm` lê só o corpo, nos quadros de sonda. O relatório também traz `floor[]` — o ponto mais baixo de CADA
renderer (corpo, LOD1, arma, escudo; efeito não) em TODOS os quadros de todos os clipes, com clipe e quadro — e
`floorMinYCm` / `floorWorst`; abaixo de −1 cm vira `problems`. Foi o que faltava quando a espada solta do ALVOR
ficou 1,7 cm dentro do piso por 49 quadros da morte: o corpo estava limpo, a arma ninguém media.

Portão: `import ok=True problems=[]`, `bodyMinYCm` ≥ −0,5, sequência do controlador correta (morte ignora gatilhos seguintes), e a tabela
de pé plantado por transição gravada (`unity_transitions*.json`). Capture a câmera de jogo para o pacote de revisão.

## 2b. Unidade que sai do chão, invocador, ataque à distância (OCASO + OSSINHO)

Tudo isto é dado do manifesto — nenhum nome de personagem no C#:

- **`sink` por clipe** (`export.py` lê `cf_sink` da action; `to_unity.py` → `clips[].sink`): o piso DA unidade, por quadro
  (−0,74 m no 1º quadro do `spawn`). O portão de chão e o `bodyMinYCm` descontam esse piso — sem isso um esqueleto
  enterrado de propósito reprova por 74 cm. A raiz já desce no clipe; o `sink` é só o gabarito do juiz.
- **`hold_last_frame` = "não termina na pose-base"** (`last_frame_vs_home_cm` ≥ 1), não "último ≠ primeiro": o `spawn`
  começa enterrado e termina em pé — tem de entregar para o idle. A comparação com a pose-base **ignora ossos de efeito**
  (`DEF-fx_*`): o raio parado a 3 m no fim do ataque dizia "não voltou" e o ataque congelava (297,9 cm → 0,65 cm).
- **`summon`** (`rig/landmarks.json → summon` → manifesto → `CFSummoner` no prefab): prefab da unidade
  (`Assets/Characters/<UNIT>/<UNIT>.prefab` — **importe a unidade ANTES do invocador**, senão vira `problems`), evento do
  clipe, clipe de `spawn`, pontos `[esq, frente]` → local `(−esq, 0, frente)` (a unidade olha +Z). No evento, uma unidade
  por ponto, a segunda `stagger` depois, viradas `turnOutDeg` para fora; `maxAlive` dispensa as antigas (`dismissClip`).
  Confira três coisas: ponto = osso da coluna de efeito (`FxRise*Ring`, erro 0 no OCASO); no quadro em que a unidade
  passa a existir o corpo inteiro está abaixo do chão (topo −15 cm); do `ready` em diante o ponto mais baixo ≥ −0,5 cm.
- **Animator que acabou de nascer não escreve pose**: com `CullUpdateTransforms` um renderer nunca desenhado conta como
  invisível — `Play(spawn); Update(0)` andava a máquina de estados e deixava a unidade EM PÉ por um quadro (topo +67 cm
  medido). O `CFSummoner.SpawnAt` troca para `AlwaysAnimate` só nessa avaliação. Vale para qualquer coisa instanciada
  já em pose.
- **`ranged`** (efeito `kind: "bolt"` com `target` nos landmarks): no evento `hit` o projétil SAI; `impactPointLocal`
  vira o alvo e `projectileSpeed` a velocidade (OCASO: (0, 0,55, 3,2) m a 16,5 m/s; o osso do raio chega 5 quadros
  depois). O showcase não solta poeira no chão e treme a câmera na chegada.
- **"Pé no chão" sai dos pés do personagem**: `plantedBallHeight / plantedAnkleHeight` = altura em repouso + 1/5 do que
  o andar levanta o pé (6–15 mm), com os 4,5 / 10,5 cm antigos como TETO. Num mini de 0,70 m o tornozelo nunca passa
  de 8,7 cm: os dois pés liam como plantados o ciclo todo, o pino segurava o pé que balança e a tabela "media"
  15,8 / 22,2 cm de patinação (real: 3,4 / 4,1). Se a tabela de transições de um personagem pequeno vier absurda, leia
  `plantedBallCm / plantedAnkleCm / footLiftCm` no relatório antes de mexer no clipe.
- `BuildShowcase` de um invocador: sequência `summon` → ataque, câmera afastada pelo alcance dos pontos, `maxAlive` =
  nº de pontos. Para conferir o gatilho real entre em Play (`manage_editor play`) e leia `Time.frameCount`,
  `CFSummoner.Units` e os estados por `execute_code`: nesta máquina o Play avançou sem foco (1.610 quadros em 9 s);
  se `frameCount` não andar, ligue `Application.runInBackground` e, em último caso, avance `Animator.Update` à mão.

## 2c. Alvo que balança e o treino (TOCO + OCASO + OSSINHO)

- Prop que é atingido (boneco de treino, totem, estandarte) NÃO é personagem: `blender/wobble_rig.py` (ossos em pé, pesos por
  altura) → `blender/export_prop.py` (FBX sem clipes + manifesto `kind: wobble`, molas, `target`) → `cf/to_unity.py` →
  `CFImporter.Import(dir)` desvia para `ImportWobble`: rig Generic SEM Animator (com "None" a Unity importa a malha rígida:
  0 triângulos skinados), `CFWobble` no root com as MESMAS molas do `wobble.py`. Relatório: altura, tris, piso, `targetLocal`
  (+Z = o lado pintado; o importador reprova se não for).
- Projétil assado na animação (bolt / hex do `fx.py`): o `export.py` transforma o voo gravado na ação (`cf_fx_<fx>`) em evento
  `land` no quadro do estouro e o manifesto ganha `projectiles` (clipe, fx, quadro de saída e de pouso, alvo, arco). O jogo
  chuta o alvo no `land`, não no `hit` (no `hit` o projétil SAI). O alvo fica onde o projétil estoura: eixo = alvo do
  projétil + a profundidade do disco (`BuildTraining` lê os dois).
- `CFImporter.BuildTraining(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Training.unity` com `CFTraining` (patrulha,
  invocação, magias, golpes, vida do alvo, erguer um invocado do corpo). As REGRAS da rodada (vagas, faixa de queda,
  `stopLead`, `unitLead`, vida, anel cheio), a câmera e a prova com `CFRoundProbe` estão na skill `character-show` §7 — ela
  é o espelho do `blender/training_show.py`.
- O que é contrato de import (e mora aqui): `wobble.topple` no manifesto (o `to_unity.py` achata `dirs` em colunas
  `deg / r / k2 / rest`: o `JsonUtility` não lê array aninhado) e o importador soma 180° ao ângulo (Blender XY → Unity XZ;
  local (x, y, z) → (−x, z, −y)); o alvo sem a tabela vira `problems`.
- **`CFCharacter.WalkPinStep` vale para TODO personagem** (ligado por padrão, `pinWhileWalking`): enquanto o andar toca,
  o pé que menos andou desde o quadro anterior fica onde estava e a unidade é carregada por ele (teto
  `walkPinMaxStep` 0,03 m). Curva e chegada sem patinar (0,009 cm por 1/30 s no OCASO). Roda depois do `PinStep` e só
  quando ele não está prendendo; desliga-se por personagem em `pinWhileWalking`.
- A janela Game pode estar em retrato: capture pela câmera numa `RenderTexture` 1280×720 (`cam.Render` + `ReadPixels`).
- **Vídeo em fps alto**: `CFFrameRecorder` (dir, fps, seconds; `Stop()`) fixa `Time.captureFramerate` e grava o Game view
  no fim de cada quadro (pós-FX e HUD OnGUI juntos) → `ffmpeg -framerate 60 -i f_%05d.jpg`; `frames.txt` dá o tempo de
  jogo por quadro (corte no `battle.Log`). Vitrine de um personagem: cena com `CFReel` (todos os clipes, título por
  clipe, andares em arco, ataque em câmera lenta, morte → `Rebind` → vitória) — GRANIZO: `Assets/Scenes/GRANIZO_Reel.unity`.
  `Screen.width` lido pelo `execute_code` é a janela do editor, não o Game view. Peça antes de assumir o Play: o
  usuário pode estar no laboratório.

## 2d. Efeitos por tipo, explosão e stun (FERRUGEM)

- `blend` do material de efeito vem do TIPO: `additive` (raio, faísca, chama, aura: luz, sem sombra), `alpha` (poeira,
  vapor, fumaça da explosão: partícula Alpha Blended UNLIT e de dois lados, tinta 0,5 = a cor do mapa — o Standard Fade
  iluminado desenhava as cartas PRETAS vistas por trás), `""` (os pedaços da explosão: o corpo, opaco, COM sombra). Malha com vários materiais (gibs: corpo / borda / fumaça) = uma entrada por slot usado (`slot`, `color`
  para material sem textura); o export remove slots vazios para slot i = submalha i. O importador reprova se o número de
  materiais não bater com `subMeshCount`.
- Bloco `explosion` do `death.clip.json` → manifesto (`to_unity.py`) → `CFExplosion` no prefab: no evento (`explode`), todo
  `CFWobble` em pé no raio toma dano + empurrão para longe do coração e, se sobreviver, `Stun`. O coração é a média dos
  ossos no último quadro com o corpo inteiro (no evento a escala do `root` já o escondeu). Jogo: `Exploded(centro, raio)`.
  "Inteiro" = nem o `rootBone` nem os ossos logo abaixo dele com `lossyScale` < 0,95 (o export põe o colapso no quadril, não
  no `root`: testar só o `root` amostrava o coração a 1 cm do chão acima de 30 fps).
- Alvo importado (`ImportWobble`) ganha `CFStunFx` com `CF_StunArc.mat` (aditivo) e `CF_StunRim.mat` (shader
  `CharacterFactory/StunRim`; só pipeline embutido). O stun é o `shock` do Blender camada por camada, desenhado pela engine:
  arcos com a imagem do `fx.py` (núcleo quente + brilho), garfo, arco para o chão, faíscas balísticas, estrela no pouso do
  salto, luz que pisca e um FRESNEL azul sobre o corpo — é o fresnel que lê na câmera do jogo (aditivo sobre albedo claro só
  clareia). Arcos só na CASCA externa (célula de 2 cm × 22,5°, raio ≥ 85 % do máximo da célula, normal para fora) e com
  `cameraBias` (o lado que a câmera vê).
- **Pedaços (gibs) na engine**: o manifesto `gibs` → `CFExplosion` troca os renderers SÓ em Play e no evento (pedaços ligados,
  corpo desligado; volta quando o corpo está inteiro de novo depois de `restoreAfter`); a borda quente brilha por
  `MaterialPropertyBlock` = cor × força × escala do osso `FxGibsHeat` (no Blender um driver). Slot 0 dos pedaços = o material do
  corpo (`share`: sem segunda cópia dos mapas); as LOD1 dos efeitos entram nos `LODGroup`.
- **Nunca "slot i = submalha i"**: o importador do FBX triangula n-gons côncavas sozinho, perdeu 420 triângulos das tampas e
  TROCOU as submalhas da LOD0 (interior inteiro amarelo, borda preta; a LOD1 vinha certa). O `export.py` exporta com
  `use_triangles=True` e grava `submeshes` (triângulos e área por slot); `CFImporter.MatchSlots` casa pela melhor permutação
  (reprova > 5 %) e `CFExplosion.hotSlots` guarda onde o material quente caiu em CADA renderer.
- **Fumaça iluminada desenhada sem luz**: rode `blender/lit_gain.py --arg name=<NAME>` antes do export (mede quanto a luz do
  viewport aprovado clareia cada material de fumaça → `cf_lit_gain` → `tint` no manifesto). O importador converte para o espaço
  de cor do projeto: o shader de partícula legado faz 2 × tinta × mapa no espaço de TRABALHO e, num projeto Linear, a tinta
  0,5 mostrava a fumaça a 0,43× do mapa (FERRUGEM: fuligem preta).
- **Gravar um evento quadro a quadro em Play**: no evento ponha `Time.captureDeltaTime = 1/30` e capture num
  `EditorApplication.update` quando `Time.frameCount − f0` alcançar cada deslocamento (`Camera.main.Render` numa RT);
  `Application.onBeforeRender` não dispara com a janela Game escondida. Log por `AppDomain.SetData`; salve em
  `review/unity/unity_melee_r<N>.log` + `review/unity/blast/`.
- **Capturar LineRenderer / efeito de câmera**: mova a câmera numa chamada, capture na SEGUINTE. A fita `View` é montada para a
  câmera do quadro: mover e renderizar na mesma chamada desenhou os arcos de lado, dentro do saco (58 % dos pixels sumiram).
  Para segurar um instante: inscreva-se no evento (`Exploded += ... Time.timeScale = 0.04f`) e capture em seguida.

## 2e. Sentir na engine: hit-stop, tremor, bando variado, transições afinadas no motor

O que o clipe promete (contato claro, segurar no impacto, bando que não anda em passo — skill `character-clips` §6b) a
engine entrega assim. Tudo em `Runtime/CFBattle.cs`, `CFDuelDirector.cs`, `CFDuelLab.cs`, `CFBlendTune.cs`.

**Hit-stop** (`CFBattle.hitStop` 0,06 s, `killStop` 0,13 s):
- No evento de acerto (corpo a corpo: `hitEvents`; magia: `landEvent`) o `Animator.speed` do atacante E da vítima vai a
  0 por esse tempo (magia: só o alvo — o lançador soltou o projétil há muito). O `Freeze` soma ao `until` e ao
  `nextAttack` da unidade só o tempo NOVO congelado (dois golpes seguidos não somam duas vezes), o `Think` retorna
  enquanto congelado (nem o empurrão anda) e o `Thaw` devolve a velocidade PRÓPRIA da unidade (`animSpeed`, ver bando).
- Prova por conta, não por foto (o congelamento dura 2 quadros): a 0,1× o FERRUGEM avançou 9 quadros do ataque em
  0,416 s de jogo em vez de 12,5 — os 3,6 que faltam são os dois hit-stops de 0,06 s dos eventos `hit` e `rake2`. O
  leitor do laboratório mostra `[HIT-STOP]` e o quadro congelado.
- O gatilho da reação (`hit`) é dado ANTES do congelamento: a transição começa e fica parada, a vítima segura a pose de
  contato e a reação estala quando solta — é o efeito que se quer.

**Sinal para a câmera** (`CFBattle.Struck(ponto, dano / vida máxima, matou)`, no mesmo quadro da faísca):
- `CFDuelDirector.OnStruck`: tremor ANGULAR (a vista gira, a câmera fica; Perlin a 38 Hz, decai e^(−9t)) de
  `shakeHit` 0,35–0,9° (pela fração de dano) e `shakeKill` 1,5°, metade no Retrato e no Livre; soco de FOV `punchHit`
  0,9° / `punchKill` 2,2° (decai e^(−11t)). Tudo em tempo NÃO escalado: o tremor é o mesmo na câmera lenta do nocaute.
- Qualquer outro diretor (o `CFDemoDirector` da masmorra) assina o mesmo evento — nada de olhar a vida por quadro.

**Bando variado** (`CFBattle.varySquad`, `squadSpeed` (0,92, 1,08), `squadScale` (0,95, 1,05)):
- Só invocados (o herói é sempre igual). `Vary` no `OnSummoned`: velocidade do Animator e escala do transform, raio do
  corpo × escala, `walkSpeed` × velocidade × escala (o pé não patina: a velocidade de chão do clipe escala com o
  playback E com o tamanho). Os tempos de clipe da batalha passam por `Len(u, clip)` = duração ÷ velocidade.
- Determinístico pela chave da unidade com sequência de razão áurea (h = frac(k·0,618 + 0,17)): o primeiro hash
  (seno de vizinhos) deu ×0,93 aos dois esqueletos de uma invocação.

**Transições afinadas NO MOTOR** (`CFBlendTune`, JSON por personagem):
- Categorias do controlador que o importador monta: `walkIn` (repouso → andar, 0,20), `walkOut` (andar → repouso,
  0,20), `fromHome` (repouso → one-shot, 0,06), `fromLoop` (andar → one-shot, 0,15), `fromOneShot` (one-shot → one-shot,
  0,08), `back` (one-shot → repouso no fim, 0,10; `exitTime` = 1 − back / duração). A categoria se LÊ do controlador
  (repouso = estado padrão; laço = estado com parâmetro Bool do mesmo nome), então serve para qualquer personagem.
- No laboratório (painel Transições, só no editor): edite, **Aplicar** escreve no `.controller` e o Animator em Play
  usa na hora (medido: a transição repouso → dano passou a durar 0,250 s sem reiniciar o estado); **Salvar JSON**
  grava `Assets/Characters/<NAME>/<NAME>.blend_tune.json`. O `CFImporter.Import` lê esse arquivo (sem ele, os padrões
  acima) — reimportar não perde o que foi afinado a olho.
- Atenção: Aplicar muda o asset no disco também fora do Play. Para desfazer um teste: `TuneApply(lado, new CFBlendTune())`
  (os padrões) ou reimporte.
- Afinar por olho tem limite: blend curto demais estala onde as poses diferem (a regra dos cinco clipes começarem na
  mesma pose ≤ 1 mm é o que permite 0,06 s); blend do andar longo demais patina — confira com `MeasureTransitions`
  depois de salvar e reimportar.

**Visualizar outra câmera dentro do jogo** (o inset do laboratório): RenderTexture desenhada pelo IMGUI num projeto
Linear sai com uma codificação de gama A MAIS (chão 0,40 desenhado como 0,66 = 0,40^(1/2,2)), com RT sRGB ou linear.
Desenhe direto na tela por viewport (`camera.pixelRect`, `depth` acima da principal) e copie o `CFPostFX` da câmera
principal para a de pré-visualização (sem ele a vista fica pálida ao lado do jogo); medições continuam num RT próprio
com `RenderWithShader`.

## 2f. Quadrúpede (UIVO)

- `export.py` lê `rig["cf_quad"]`: mapa de nomes próprio (Hips/Spine/Spine1/Spine2/Chest/Neck/Neck1/Head, Tail1–4,
  Left/RightScapula, Left/RightFrontUpLeg/FrontLeg/FrontFoot/FrontToeBase, Left/RightUpLeg/Leg/Foot/ToeBase, Jaw,
  Left/RightEar1–2) — o mapa Mixamo chamaria a ponta do rabo de "Hips". `FEET` = as quatro patas; `rig_bones` ganha
  `frontFoot*/frontToe*` e o manifesto `quadruped: true`. Rig Generic (sem Humanoid para quatro patas).
- O `CFImporter` escolhe a marcha pelo nome `walk` ou, na falta, o primeiro loop com velocidade: ponha `run` antes de
  `sprint_loop` na lista de clipes. O `sprint` é um DASH (`gait.dash`: distância, quadros, perfil) — o jogo move a unidade
  por esse perfil, não por uma velocidade constante.
- C# com QUATRO pés (feito 2026-11-14): `CFCharacter.quadruped` + `frontLeft/RightBall`, `FootCount` / `GetFoot(i)`
  (tornozelo nulo no quadrúpede), `QuadWalkPin` (só patas plantadas, a que menos andou, teto `walkPinMaxStep`).
  Planted = `ballRest + margem` (7,5 cm no UIVO). Import: `ok=True problems=[]`, −0,449 cm.
- **Pino de quadrúpede = MÉDIA das patas plantadas** (`PinStep` / `Carry`): prender só a pata que lidera a deixava parada
  e fazia as outras plantadas deslizarem o que ela não deslizava (UIVO run→attack com janela 29,5 / 37,7 cm → 6,2 / 9,6).
- **O `PinStep` começa no quadro ANTES da mistura e termina o último pedaço dela**: o 1º quadro da mistura já moveu o pé
  pelo peso desse quadro, e uma mistura de 0,08 s que acaba entre dois quadros perdia o resto (o pino do bote carregou
  0,12 m de 0,28 num quadro longo do editor e a mordida caiu 14 cm antes do alvo). `ResetPins()` depois de teletransportar
  a unidade (reinício de rodada); um apoio gravado a mais de um `pinMaxCarry` de distância é descartado.
- **`QuadWalkPin` relia a pata DEPOIS de mover a unidade e somava a correção de novo**: virou integrador, −3 cm por quadro
  (o teto) para TRÁS, e a corrida de 2,18 m/s andava 1,24 m/s no Play. A tabela mostrava: com o pino (15,7 cm) pior que
  sem ele (5,8). Regra: se o modo de jogo (com pino) mede PIOR que o sem pino, o pino está errado — não o clipe.
- **Dash conduzido pelo personagem**: `PlayDash(distância)` dispara o clipe, larga a marcha e grava origem/direção;
  `DashStep()` move a unidade pelo perfil no `LateUpdate` ANTES dos pinos (movido depois, o pino gravava a pata antes do
  último empurrão — ~10 cm — e puxava o lobo para trás); `IsDashing` até pousar. Entrar num dash é um CORTE
  (`CFBlendTune.toDash` 0,03 s) e nada é preso; sair de um dash que já pousou prende as patas plantadas e o corpo assenta
  sobre elas (0,28 m no UIVO): sprint → ataque / dano / morte / vitória / idle = 9,8 / 5,4 / 4,0 / 3,9 / 3,4 cm.
- **Como um one-shot termina** (`end` no clip.json → `cf_end` → manifesto → `CFClip.end`): `home` (padrão: entrega para o
  idle), `hold` (morte, vitória), `chain` (o dash termina NO alvo e o golpe segue no evento `land`; nunca segura —
  um estado que segura não tem saída, o ataque não conseguiria seguir; sem golpe, segura 0,1 s e volta sozinho,
  `exitTime = 1 + 0,1/len`, interrompível pelos gatilhos da origem). O `export.py` reporta `end_problem` quando um `home`
  não volta. UIVO r1: o rabo ainda balançando 4,46 cm no fim do ataque e o deslize do dano (6 cm) viraram HOLD —
  o lobo congelaria depois de cada mordida e de cada dano. Confira `hold` por clipe no relatório da Unity.
- **Marcha → marcha direto** no controlador (`UseGait` troca os bools no mesmo quadro): pela pose-base a corrida parava
  quase toda antes do galope. A transição de troca fica ANTES da volta para casa na lista do estado.
- **Fase de ENTRADA medida no motor**: `MeasureTransitions` varre todas as fases de entrada da marcha (rampa + `WalkPinStep`,
  como no Play), grava a melhor no controlador se ganhar 0,5 cm da do export e põe a linha `entry phase swept`. UIVO
  0,80 → 0,60: idle→run 43,3 → 1,4 cm; GRANIZO 0,0 cm. Rode `MeasureTransitions` depois de TODO `Import`.
- **Janela de saída CONJUNTA** (parar E golpear: o `PlayWhenPlanted` espera a mesma janela): escolhida pelo pior dos dois
  por fase. Só pela parada, UIVO tinha duas fases em que o ataque deslizava 18–19 cm. UIVO 0,76–0,96: run→idle 3,0 / 9,9,
  run→attack 6,2 / 9,6 (espera ≤ 0,65 s); GRANIZO walk→idle 1,1 / 3,9, walk→attack 1,3 / 1,8.
- Medir um loop à mão exige `SetMoving(true)` / o bool da marcha: sem ele o controlador volta ao idle em 7 quadros e a
  "patinação" medida (146 cm) era o idle sendo carregado. E o `MeasureTransitions` roda o que o `LateUpdate` roda
  (`DashStep` → `PinStep`, inclusive no último quadro da marcha) — senão mede outro motor.
- Limites declarados (UIVO): idle→sprint 44 cm (o dash nasce da fase estendida da corrida — o jogo entra nele pela
  corrida); idle→attack 7,2 cm = interpolação a 60 Hz das patas traseiras entre chaves a 30 fps (0 no Blender).
- **Caça contra o boneco** (`CFImporter.BuildHunt(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Hunt.unity`, `CFHunt`):
  todos os clipes de um caçador com dash, em rodadas alternadas (vitória / dano + morte), legenda do clipe na tela, câmera
  que acompanha, barra de vida. Onde o alvo fica é MEDIDO: alcance da mordida (pele mais à frente acima das patas no 1º
  `hit` do ataque: 1,016 m), o carregamento da saída do dash (0,28 m) e a face do alvo na altura da mordida (0,184 m) →
  a mordida entra 2–4 cm na face. A mordida do próprio dash (0,797 m) fecha no ar ~0,5 m antes (`dashBites` false).
  Vídeo: `CFFrameRecorder` (60 fps fixos) + `CFHunt.RestartFromTop()`.
  Contra o "robótico" na engine (r2): mordidas ENCADEADAS no evento `interrupt` do ataque (`chainEvent`), cada uma com
  velocidade própria (0,93–1,07, sequência de razão áurea: `BiteSpeed`) — ataque → idle → ataque era um reset; a morte
  começa na metade do dano (`deathAt` 0,5) em vez de depois da recuperação inteira. Câmera (`cameraMode`, tecla C):
  `Top` = a do jogo (elevação 56°, fov 38), `Side` = a antiga, `TopAndSide` (padrão) = de cima + a lateral num inset
  (`insetRect`, câmera "Side Inset Camera" copiada da principal, profundidade +1).
- **Efeito de vento** (`fx.py` tipo `wind`, landmarks `fx.wind`): arcos no focinho + riscos que ficam no MUNDO; entram
  no FBX como qualquer efeito (ossos `Fx*` por escala, material aditivo). O clipe é no lugar, então riscos e poeira já
  andam PARA TRÁS no clipe pelo quanto o chão andou (`ground_travel`): quando a engine leva a unidade para a frente na
  velocidade do clipe, eles ficam parados no mundo. Só vale se a unidade andar na `ground_speed_m_s` do manifesto.
- **Primeira mordida = `dash_bite`** (r3): `CFHunt.dashBiteClip` toca no fim do dash quando o controlador tem o clipe
  (`HasClip`); as mordidas seguintes encadeiam no ataque. O `BuildHunt` mede onde o alvo fica pelo `hit` do clipe da
  PRIMEIRA mordida (`first_bite` no JSON; carregamento 0,0 m). Unity: sprint → dash_bite 2,1 cm × sprint → attack 10,3.
- **Unidade sem arma não tem prop de mão**: o `export.py` punha `UIVO_Hammer` no manifesto porque `cf_weapon_prop` tinha
  "hammer" como padrão. Agora: sem chave no rig e sem objeto `<NAME>_<prop>` → sem prop (`prop`/`hand_prop` = "").
- Abertos depois do r3: idle → attack 8,4 cm e idle → hit 9,9 cm (bola da pata; o `PinStep` em pé → em pé cancelaria o
  deslize planejado do dano), run → attack espera a janela, o renderer do vento não é desligado fora das marchas, linhas
  do `sprint_loop` no `MeasureTransitions`, teto do `maxPhaseWait`.
- **Pose-base nova muda a tabela inteira** (UIVO r4, agachado com as patas abertas): a média melhora (run → idle 5,5 → 4,3,
  run → attack 8,8 → 6,8 cm), mas o que sai de uma pose de patas JUNTAS para a casa piora — dash interrompido por morte /
  dano / vitória 4–9 → 8,5–11,3 cm (o pouso do dash × as patas abertas da casa). O caminho da caçada (sprint → dash_bite)
  ficou em 2,1 cm porque o `dash_bite` traz a pose nova só na recuperação, com cada pata no ar. Rode `MeasureTransitions`
  e compare com a tabela anterior a cada mudança de pose-base.

## 3. O que a engine não conserta

Gatilho no pé errado ainda arrasta 23–30 cm sem clipe de transição: é limite declarado, não bug do importador. Se o
jogo exigir menos, a saída é autorar o clipe de transição ou esperar a fase (`leave_phase`).
