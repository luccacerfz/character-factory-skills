---
name: character-design
description: Desenhar um personagem da Character Factory de modo que ele CAIBA na animação, e gerá-lo no Tripo web — brief de uma página, regras de desenho que vêm dos portões do modelo (braço, corredor da cabeça, cabo), concept em T-pose com GPT Image 2.5, vistas ortogonais, modelo 3D multivista H3.1 Ultra e props como objetos separados. Use quando o usuário pedir um personagem novo, um concept, uma arma/acessório novo, "gera no Tripo", ou quando um portão do modelo reprovar e a saída for redesenhar. Inclui as regras de LEITURA no jogo: silhueta a 64 px na câmera de jogo (não em close), essência em 1–2 traços amplificados, estilo boneco de ação em miniatura e o rosto para os closes (vitória, desbloqueio).
---

# Desenho e geração (brief → concept → GLB)

O que se decide aqui custa minutos; o mesmo erro descoberto depois dos clipes custa rodadas inteiras. O primeiro
personagem (BRASA) ficou com três limites que nenhuma animação tirou — todos eram do desenho. Por isso o brief já nasce
com as regras abaixo, e o `model_gates.py` (skill `character-rig`) confere no modelo gerado.

## 0. Leitura, essência e escala — decida ANTES do brief (princípios de jogo 1–4, 7)

Uma unidade de jogo mobile é vista a ~64 px de altura, de cima (câmera de jogo 55°, fov 38), durante 1–3 s por vez. Tudo
nesta seção existe porque o jogador decide "quem é e o que está fazendo" num relance. A régua é a do laboratório da
arena (skill `character-show` §9d, tecla G): a câmera do jogo num telefone de 360 × 640 px, colocada para que uma
unidade de 1,4 m em pé no centro tenha 64 px. Nessa escala **1 px ≈ 2,2 cm**: o que tem menos de 4–5 cm (2 px) não
existe, o que mexe menos de 2 px não mexeu.

### 0a. Leitura primeiro (um relance = quem é + o que faz)

- **Julgue sempre na câmera de jogo, no tamanho de jogo**, nunca num close do Blender. O close engana: o OCASO é um
  necromante de rosto de caveira em close; no laboratório, de cima, a 1:1, ele é um DOMO roxo (o manto) com o gancho
  do cajado saindo — 97 × 88 px na tela; o crânio e o capuz não se separam da massa. O ALVOR lê pela lâmina diagonal
  que sai da silhueta (113 × 123 px); escudo + elmo viram um bloco só. O FERRUGEM lê como caixa com garras (72 px).
  Esses números e silhuetas estão em `env/duel/shots/lab/` — compare o seu personagem com eles.
- **A câmera de jogo vê o TOPO**: topo da cabeça, ombros, costas, o prop. Ponha a identidade onde ela vê: forma do
  chapéu / capuz / chifres, o prop por cima do ombro ou para fora do corpo, uma cor de destaque no topo. O rosto é para
  os momentos de close (0d), não para a leitura em jogo.
- **Teste de silhueta antes de gastar crédito**: concept em T-pose E um esboço 3/4 de cima reduzidos a 64 px de altura,
  preenchidos de preto (limiar no PNG: `python3 -c` com PIL, `img.convert('L').point(lambda v: 0 if v < 200 else 255)`),
  ao lado das silhuetas dos aprovados (`env/duel/shots/lab/inset_pair.png`). Portão: nomeie a unidade só pela mancha —
  se ela confunde com outra, mude a FORMA (não a cor).
- **Linguagem de forma por papel** (uma por unidade, legível de longe): bruto = bloco/quadrado (FERRUGEM, GRANIZO),
  conjurador = triângulo/domo com uma vertical (OCASO + cajado), herói = V largo em cima com uma diagonal (ALVOR +
  espada), invocado = pequeno, magro, repetido (OSSINHO). Duas unidades do mesmo elenco não dividem a mesma forma.
- **O prop-assinatura sai da silhueta**: ≥ 1/3 da altura, e para FORA do contorno do corpo na pose de idle vista de
  cima (lâmina diagonal, cajado vertical com gancho, martelo maior que a cabeça). Prop colado no corpo some no domo.
- **Valor antes de cor**: as 2–3 massas grandes vizinhas com ≥ 20 % de diferença de luminância (o interior da silhueta
  lê a 64 px), e o corpo contrastando com o chão: a grama renderizada da arena é (99, 168, 75) — nada de verde médio
  como cor dominante de unidade.

### 0b. Ache a essência e AMPLIFIQUE (1–2 traços, não um catálogo)

- Pesquise o arquétipo (quem é, de onde vem, como se move) e escreva no brief uma seção **Essência**: no máximo DOIS
  traços, cada um com um adjetivo e um verbo ("teimoso — investe de cabeça"; "frio — nunca se apressa"). Mais que dois
  e nenhum lê a 64 px.
- Cada traço vira uma decisão de FORMA e uma de MOVIMENTO por clipe, numa tabela no brief:

  | Traço | Forma (o que a silhueta mostra) | idle | andar | ataque | dano | morte | close (vitória) |
  |---|---|---|---|---|---|---|---|

  Exemplo (leitura do que as unidades aprovadas já fazem): GRANIZO "lento e inevitável" → maior do elenco (1,55 m),
  marreta enorme; andar de 30 quadros (120 passos/min), ataque com preparo longo (evento a 1,30 s) e golpe curto;
  OCASO "frio, manipulador" → domo + cajado plantado; nunca corre (0,32 m/s), o momento-herói é a invocação.
- **Empurre até ler**: cada traço precisa de UMA coisa grande e específica (um gesto de 20°+ de cabeça, um prop que
  pesa, uma postura curvada de 15°+), não de cinco sutis. Regra: no máximo 3 ideias de desenho por unidade (forma,
  prop, cor de destaque); detalhe que não lê a 64 px sai ou cresce 1,5–2×.
- O crítico de princípios (skill `character-review`) recebe a seção Essência e responde por clipe: "o traço X aparece?".

### 0c. Estilo na escala: "boneco de ação em miniatura"

Estilo detalhado não traduz para mobile. A casa usa o boneco colecionável atarracado (Clash Royale / Warcraft Rumble),
com regras que se medem no concept:
- **Cabeça** 1/4–1/3 da altura (OSSINHO 0,67 m ≈ 1/3; heróis ≈ 1/4); **mãos** ≥ 1,3× a proporção real; **prop** ≥ 0,6×
  a altura do corpo; pés/base largos (a unidade não pode parecer na ponta dos pés vista de cima).
- **Formas grossas e chanfradas**: nenhuma peça com menos de 4–5 cm de espessura (2 px); alças, correntes, dedos
  separados e franjas finas não leem — viram uma massa (mão em placa, cinto largo, franja em 3 pontas grossas).
- **Poucos blocos de cor**: 3–4 cores principais + 1 destaque; a textura PBR pintada à mão REFORÇA a forma (luz no
  topo, oclusão nas dobras), nunca carrega a identidade sozinha.
- **Proporção ousada > anatomia correta** (§4b): o portão do modelo pode reprovar por escolha (OCASO `overhead` 0,66) —
  isso se declara no brief com o gesto que cabe no lugar.

### 0d. Momentos de close (desbloqueio, vitória, menu) = onde mora o charme

- Em jogo a unidade é uma silhueta; o rosto aparece nos closes. A arena já tem o take **Retrato** (tecla 9; automático
  depois de um nocaute): o vencedor vira para a câmera e **inclina ~7° para trás** em torno dos pés, câmera à altura do
  rosto, fov 28, rosto no terço superior, cartão de vitória no terço inferior (`env/duel/shots/lab/retrato_alvor_s.jpg`).
- Desenhe o rosto PARA esse take: feições grandes e de alto contraste (sobrancelha, olho, boca — ou o "rosto" de uma
  máquina: a escotilha do FERRUGEM lê no Retrato), linha dos olhos visível com a cabeça erguida 5–10°, nada na frente
  do rosto no idle (mão, prop, aba do capuz).
- Escreva no brief UMA expressão por momento (vitória, derrota, desbloqueio) e COMO ela é feita: pose de corpo + cabeça
  (sempre), mandíbula / pálpebra / sobrancelha (2–4 ossos, skill `character-rig` §0) ou troca de textura / emissão do
  olho. Hoje nenhum aprovado tem osso de rosto: é a primeira coisa a pedir no próximo brief.

### 0e. Onde o personagem vive (decide os ossos extras)

No brief, nomeie as 1–3 partes que carregam personalidade e balançam (orelha, cauda, capa, ponta do capuz, barba,
chaminé, corrente da arma). Desenhe cada uma como UMA massa grossa com raiz à vista (regra da §2) — vira corrente de
molas no rig. Todo o resto é rígido. Parte que não balança ≥ 2 px (≈ 5 cm) em nenhum clipe não ganha osso.

## 1. Brief (`characters/<id>/brief.md`, uma página)

Copie a estrutura de `characters/granizo/brief.md`: Pitch · **Essência (1–2 traços + a tabela traço × clipe, §0b)** ·
Look (trava de estilo) · **Leitura (forma por papel, prop que sai da silhueta, topo visto de cima, §0a)** · Objetos
separados · Regras de geração · Personalidade → notas de animação · **Close (expressão por momento, §0d)** · Clipes. O estilo da casa: miniatura colecionável atarracada (Clash Royale /
Warcraft Rumble), PBR pintado à mão, formas grossas, silhueta legível a 64 px, nada fino ou solto.

## 2. Regras de desenho (cada uma tem um número por trás)

| Regra | Por quê (medido no BRASA) |
|---|---|
| **T-pose**: braços retos para os lados, palmas para baixo, dedos juntos, **mãos vazias**, pernas levemente afastadas | A-pose a 35° fundiu axila e manopla no tronco de um personagem atarracado: rasgo em close |
| Braço (ombro→pulso) ≥ 1,1 × distância do ombro a um ponto logo acima do topo do crânio | portão `overhead`: com braço curto a arma de duas mãos não passa por cima da cabeça; foi preciso alongar 20 % no modelo |
| Nada na cabeça mais largo que a cabeça: envergadura (chifres, cristas, orelhas) ≤ largura dos ombros − espessura do braço | portão `corridor` 0,70: chifre 34 mm dentro do braço em 15 quadros; 17 poses tentadas, nenhuma resolveu |
| Cabo fino na pegada (mais fino que o pulso), mãos grandes com dedos tão longos quanto a palma | portão `wrap` 0,31: os dedos fechavam 34° antes de tocar um cabo de 10–12 cm → punho estilizado |
| Braçadeiras/manoplas retas, sem aba alargada, **mais finas que o punho fechado no lado do pulso** e começando 3–4 cm antes dele | a aba raspava no pomo sempre que o pulso dobrava; no GRANIZO o bracelete (13–16 cm de raio, punho 12,5) começa NO pulso: todo cabo a menos de ~50° do antebraço atravessa a borda (35 mm, 7–24 quadros por clipe) |
| Polegar AO LADO da palma (aberto para a frente), nunca dobrado sob ela | GRANIZO veio com o polegar apontando para baixo sob a palma: `fist_fit.py` não acha envolvimento em nenhuma estação do cabo → punho estilizado declarado |
| Braço (ombro→pulso) ≥ quanto o tronco projeta à frente da linha dos ombros + 10 cm | FERRUGEM: caldeira 0,44 × braço 0,41 — o punho nunca passa na frente do corpo; o golpe sai nas laterais e só a mão + garras atravessam |
| Peças redondas nos ombros (tambores, ombreiras altas) contam como envergadura da cabeça | FERRUGEM: corredor 0,926 e overhead 0,665 por causa dos tambores — sem arma, declarado como limite |
| Ombros largos pedem braço proporcional: (meia largura dos ombros) ÷ (ombro→pulso) ≤ ~0,6 | GRANIZO 0,40 ÷ 0,64: a mão do pomo cai 13–17 cm por dentro do próprio ombro e o antebraço deita no cabo; as chaves portadas precisaram de +7 cm para o lado |
| Cabeça afundada entre os ombros (sem pescoço) é permitida, mas então a cabeça quase não gira: o tronco vira | queixo e presas entram até 62 mm no peito/ombros quando a cabeça inclina; os ossos do pescoço não podem segurar pele do peito (regra `neck_not_chest`) |
| Nada rígido na linha dos ombros/cabeça (ombreira alta, chaminé); prop de costas BAIXO, mais estreito que o tronco | ombreira 22–63 mm dentro do capacete; mochila batendo na cabeça no recuo |
| Todo acessório rígido (arma, mochila, escudo) é **objeto separado**, gerado sozinho | soldado no corpo rasga igual à arma |
| Pele lisa nas dobras (ombro, cotovelo, quadril); cinto alto e simples | fivela e cinto esmagavam no impacto; pele lisa é onde o peso distribui bem e onde dá para alongar no modelo |
| Detalhes rígidos da cabeça (presas, sobrancelhas) NÃO da cor da massa mole | presas marfim = cor do cabelo: a classe de cor pegou as presas; foi preciso caixa + cor |
| Massa mole (barba, rabo de cavalo) = UMA massa grossa, de cor distinta, com raiz à vista | vira ilha + corrente de molas; raiz enterrada sob casca rígida é sobreposição permanente |
| Um marcador assimétrico (alça num ombro, presa quebrada) | é assim que se confere esquerda/direita em cada vista e no modelo |
| Dedos separados e ABERTOS na T-pose, e CONTE-os na imagem e no modelo | ALVOR veio com seis dedos na mão direita: `remove_stub.py` + `skin_patch.py` consertam, mas custa uma rodada |
| Escudo: gerado sozinho, com ALÇA visível nas costas, e grande o bastante para o antebraço caber atrás da placa com o punho na alça (≈ 0,3 × 0,5 da altura do personagem) | ALVOR: escudo do tamanho gerado deixava a mão fora da alça; 1,3× (0,47 × 0,73 m para 1,5 m) resolveu. Ele é SEGURADO na mão, na frente do corpo |
| Sem brilho pintado: peça "matte, no painted highlights, no glow" e ligue "remover iluminação" | "a luz que vem do Tripo" = metal 1,0 + brilho na textura; `matte.py` tira o metal, não o brilho pintado |
| Pense na pegada ao escolher a pose das mãos | bind de palmas para baixo + mão de cima pegando por baixo = meia-volta de torção no antebraço (107–145°) |

## 3. Tripo web (Chrome já logado; use as ferramentas `claude-in-chrome`)

Gerar no Tripo com GPT Image 2.5 é decisão do usuário (o gerador da Runware não obedecia à T-pose).

1. **Imagem** (ícone no topo da barra esquerda) → modelo **GPT Image 2.5**. Prompt em inglês com: estilo, descrição,
   POSE em maiúsculas (T-pose, palmas para baixo, mãos vazias), "no weapon, nothing on the back", fundo branco, luz
   uniforme, câmera frontal sem perspectiva. Para manter o estilo da casa, anexe como referência o
   `refs/tpose_front.png` de um personagem aprovado e escreva "same art style … but a COMPLETELY DIFFERENT character".
   Proporção 4:3 (T-pose é larga), 2 imagens (8 créditos).
2. Confira na imagem, antes de gastar no 3D: T-pose de verdade, mãos vazias e abertas, marcador assimétrico no lado
   certo (o lado ESQUERDO dele fica à DIREITA de quem olha), braço/cabeça dentro das regras (meça em pixels).
3. **Vistas**: o botão "Gerar multivisões" da imagem (ícone de cubo ao passar o mouse) às vezes devolve vistas oblíquas
   (aconteceu duas vezes seguidas no GRANIZO). Se as quatro não forem frente / perfil esquerdo / perfil direito / costas
   retos, gere cada vista com GPT Image 2.5 usando a frente como referência e um prompt explícito ("strict 90-degree
   profile, he faces the LEFT edge of the image, his left arm points straight at the camera…", "seen from DIRECTLY
   BEHIND…"). Perfil esquerdo = câmera à esquerda dele = ele olha para a esquerda da imagem.
4. Baixe cada imagem (seta ao passar o mouse). **Confira para onde o Chrome do perfil baixa** (`chrome://settings/downloads`:
   nem sempre é `~/Downloads`); os nomes se repetem
   (`image_0.png`), então mova uma de cada vez para `characters/<id>/refs/view_{front,left,right,back}.png`.
5. **Modelo** (segundo ícone) → aba de multivista (ícone de cubo) → suba Frente / Esquerda / Direita / Verso →
   "Geometria e textura": malha Ultra, textura 4K, remover iluminação, PBR, triângulos, 2.000.000 → **H3.1 – Máx.
   qualidade** → Gerar (55 créditos, alguns minutos).
6. Exportar → GLB → mover para `characters/<id>/model/<id>_hi.glb` (a versão de 2 M de triângulos: referência de
   forma e fonte de bake).
6b. **Sempre Remesh → Smart UV → Textura** (regra do usuário, 2026-11-14, UIVO): o UV que o Tripo gera com a malha
   é picado em centenas de ilhas (58 % de ocupação no UIVO) — ninguém repinta isso depois. O Smart UV (barra esquerda)
   só aceita ≤ 80.000 triângulos, então: **Remesh** → Triângulo, "Malha Smart" DESLIGADA (com ela o teto é 20.000 e
   custa 35; sem ela vai até 150.000 e custa 5) → **60.000** (o orçamento de jogo) → Retopologia; depois **Smart UV**
   no resultado (20 créditos); depois **Textura** (4K, PBR, sem iluminação). Exportar → GLB →
   `model/<id>_game.glb`. Essa é a malha de jogo: UV limpo, textura repintável; o `gameready.py` só reassa se precisar.
   Orçamento: o usuário autoriza **até 5.000 créditos do Tripo** por personagem para este fluxo (remesh, Smart UV,
   textura e as repetições que a qualidade pedir) — não economize nele; anote cada gasto no `state.json → tripo`.
6c. **Mandíbula SEMPRE aberta** no concept deste estilo (regra do usuário): "mouth open ~25 deg, upper and lower teeth
   apart, tongue inside" no prompt de TODA vista, e confira na imagem antes do 3D — boca soldada não ganha osso de
   mandíbula, e a mordida, o rugido, o uivo e o ofegar da corrida vivem nela (UIVO: `DEF-jaw` + regras de peso
   `lower_jaw` / `upper_muzzle` / `throat` em `characters/uivo/rig/landmarks.json`).
7. **Cada prop é outra geração**: imagem isolada (objeto inteiro, vertical, fundo branco, com o concept do personagem
   como referência de estilo) → "Gerar 3D" de imagem única → GLB em `model/<id>_<prop>_hi.glb`. Meça o cabo na imagem
   (largura ÷ comprimento) antes de gerar.

Gerações consomem créditos da conta do usuário: gere 2 opções, escolha, e não repita sem motivo. Anote no `state.json`
o que foi gerado e o que foi descartado.

## 4. Depois do GLB

O juiz é o `model_gates.py` (skill `character-rig`). Reprovou? Em ordem de custo: alongar/inclinar no modelo
(`proportions.py`, `part_tilt.py`, reversíveis) → regenerar a imagem com a regra explícita → aceitar como limite
declarado (e dizer isso ao usuário com o número).

## 4b. Silhueta primeiro — não um humanoide fantasiado (usuário, 2026-11-11, OCASO v1 → v2)

"nao quero os personagens sempre em humanoides perfeitos... tem que ter mais estilo da foto clash royale." O v1 do
necromante era um homem de proporção normal com casaco, calça e bota: lia como genérico e foi refeito.

- Comece o brief pela FORMA, não por um corpo: cabeça ≈ 1/3 da altura, mãos e prop enormes, manto até o chão / sino /
  corcunda / pernas escondidas quando couber, assimetria, atitude. Uma referência dá a LINGUAGEM, nunca o personagem
  (nada de elmo, barba, cajado ou paleta copiados): o desenho é original.
- Um mini assim reprova `overhead` / `corridor` por desenho (OCASO 0,66 / 0,70; OSSINHO 0,72). Isso é escolha, não
  defeito: escreva no brief o que ele NUNCA faz (levantar o braço ao lado do capuz, golpe por cima da cabeça) e dê a
  ele um gesto que cabe (cajado plantado, garra baixa à frente, corte diagonal).
- Sem pernas à vista o manto é a base: ele não cambaleia, TOMBA (morte = pêndulo invertido sobre a borda da barra).
- Unidade invocada = outro personagem (brief, modelo, rig e clipes próprios), menor e mais simples, com o `spawn` no
  lugar do `hit` se o orçamento for de cinco clipes.
- **Alvo de treino / prop que apanha** (TOCO) não é personagem: uma imagem só no Tripo (GPT Image 2.5, 2 opções com o
  prop de um aprovado como referência de estilo) → "Gerar 3D" de imagem única. O que o desenho precisa: um LADO
  pintado que diga "acerte aqui" (disco de alvo) e que vai olhar para a câmera; massas grossas empilhadas (sacos amarrados,
  não palha solta — a opção com saia de palha foi descartada); pé LARGO em cruz (é a borda pela qual ele tomba, 0,22–0,27 m
  num boneco de 1,15 m) com o poste saindo do centro; cabeça separada por um pescoço estreito (vira o 2º pivô das molas).
  Um marcador esquerda/direita também (remendo num lado do saco).

## 5. O que o segundo personagem (GRANIZO) ensinou sobre o brief

- Escreva no brief só o que a silhueta precisa. O bloco de gelo nas costas saiu: ficava no caminho do martelo atrás da
  cabeça (a regra "nada rígido na linha dos ombros" vale também para o que o próprio brief inventa).
- Pele muito clara estoura para branco nas luzes do palco: `stage.py --arg exposure=-0.9` (ou
  `scene.view_settings.exposure`) antes de julgar qualquer imagem.
- O Tripo solda o rabo de cavalo na nuca e funde os dedos: aceite (corrente macia por cor, mão em placa única) em vez de
  gastar créditos tentando separar.
- Gere e MEÇA antes de gostar: `model_gates.py` (overhead / corridor / wrap / **cuff**) + `limb_radii.py` + fatias (seção 2 da skill `character-rig`) dizem em
  minutos se braço, corredor, bracelete e pegada passam. Refazer o concept custa 55 créditos; descobrir no clipe custa o dia.

## 5b. Uma ideia, amplificada em OBJETOS (GRANIZO v3, 2026-11-14 — "melhorou bastante mas pode melhorar mais ainda seguindo os princípios de originalidade")

O v2 lia como "ogro com machado". O v3 começa de UMA frase — *ele É a geleira* (a geleira cresceu sobre ele) — e cada
asset nasce dela:

- A ideia vira **assimetria de objetos separados**, cada um gerado SOZINHO no Tripo (2 opções de cada): o lado ESQUERDO
  glaciado (punho = bloco de gelo de 0,61 m na mão, crosta de gelo na metade esquerda da corcunda), o lado DIREITO ainda
  ogro (picareta "Quebra-Geleira" de uma mão). 276 créditos no total (conceitos 32, vistas 24, corpo multivista + 3
  props 220). Um prop por traço lê a 64 px; o mesmo traço pintado no corpo não lê.
- Dois traços amplificados e só dois: o punho de geleira (assimetria) e a RACHADURA (todo golpe abre o chão). Cada clipe
  conta uma história com um deles (idle: o gelo sobe pelo braço e ele sacode; morte: a geleira fecha sobre ele).
- **Corcunda que sobe atrás do crânio** prende a cabeça: o osso da cabeça do Rigify é isolado e a corcunda está logo
  atrás — inclinar a cabeça para trás passa de −10° e entra (−20° = 26 mm). Se o desenho tem corcunda até a coroa,
  escreva no brief: olha PARA CIMA com os olhos e o tronco, nunca jogando a cabeça.
- Braço curto para o tronco (meia largura dos ombros ÷ braço 0,97, regra ≤ 0,6) e corcunda = `overhead` 0,70,
  `corridor` 0,90, `cuff` 0,93 por desenho: o preparo vai por cima do ombro DIREITO, o punho trabalha do lado dele.
