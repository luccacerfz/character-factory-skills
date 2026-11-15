---
name: character-design
description: Design a Character Factory character so that it FITS the animation, and generate it on Tripo web — a one-page brief, drawing rules that come from the model gates (arm, head corridor, handle), a T-pose concept with GPT Image 2.5, orthographic views, a multiview H3.1 Ultra 3D model and props as separate objects. Use when the user asks for a new character, a concept, a new weapon/accessory, "generate it on Tripo", or when a model gate fails and the way out is to redraw. Includes the in-game READABILITY rules: silhouette at 64 px in the game camera (not in close-up), essence in 1–2 amplified traits, a miniature action-figure style and the face for the close-ups (victory, unlock).
---

# Design and generation (brief → concept → GLB)

What is decided here costs minutes; the same mistake found after the clips costs whole rounds. The first character
(BRASA) ended up with three limits that no animation could remove — all of them came from the drawing. That is why the
brief is born with the rules below, and `model_gates.py` (skill `character-rig`) checks them on the generated model.

## 0. Readability, essence and scale — decide BEFORE the brief (game principles 1–4, 7)

A mobile game unit is seen at ~64 px tall, from above (game camera 55°, fov 38), for 1–3 s at a time. Everything in
this section exists because the player decides "who is it and what is it doing" at a glance. The yardstick is the one
from the arena lab (skill `character-show` §9d, key G): the game camera on a 360 × 640 px phone, placed so that a
1.4 m unit standing in the center is 64 px tall. At that scale **1 px ≈ 2.2 cm**: anything under 4–5 cm (2 px) does
not exist, anything that moves less than 2 px did not move.

### 0a. Readability first (one glance = who it is + what it does)

- **Always judge in the game camera, at game size**, never in a Blender close-up. The close-up lies: OCASO is a
  skull-faced necromancer in close-up; in the lab, from above, at 1:1, he is a purple DOME (the cloak) with the hook
  of the staff sticking out — 97 × 88 px on screen; the skull and the hood do not separate from the mass. ALVOR reads
  by the diagonal blade that leaves the silhouette (113 × 123 px); shield + helm become a single block. FERRUGEM reads
  as a box with claws (72 px). Those numbers and silhouettes are in `env/duel/shots/lab/` — compare your character with them.
- **The game camera sees the TOP**: top of the head, shoulders, back, the prop. Put the identity where it looks: the
  shape of the hat / hood / horns, the prop over the shoulder or sticking out of the body, an accent color on top. The
  face is for the close-up moments (0d), not for in-game reading.
- **Silhouette test before spending credits**: the T-pose concept AND a 3/4 sketch from above, scaled down to 64 px tall,
  filled black (threshold on the PNG: `python3 -c` with PIL, `img.convert('L').point(lambda v: 0 if v < 200 else 255)`),
  next to the silhouettes of the approved ones (`env/duel/shots/lab/inset_pair.png`). Gate: name the unit from the blob
  alone — if it gets confused with another one, change the SHAPE (not the color).
- **Shape language by role** (one per unit, readable from afar): brute = block/square (FERRUGEM, GRANIZO),
  caster = triangle/dome with a vertical (OCASO + staff), hero = wide V on top with a diagonal (ALVOR +
  sword), summon = small, thin, repeated (OSSINHO). Two units in the same cast do not share the same shape.
- **The signature prop leaves the silhouette**: ≥ 1/3 of the height, and OUTSIDE the body outline in the idle pose
  seen from above (diagonal blade, vertical staff with a hook, hammer bigger than the head). A prop glued to the body
  vanishes into the dome.
- **Value before color**: the 2–3 large neighboring masses with ≥ 20 % luminance difference (the inside of the silhouette
  reads at 64 px), and the body contrasting with the ground: the arena's rendered grass is (99, 168, 75) — no mid green
  as a unit's dominant color.

### 0b. Find the essence and AMPLIFY it (1–2 traits, not a catalog)

- Research the archetype (who it is, where it comes from, how it moves) and write an **Essence** section in the brief: at
  most TWO traits, each with an adjective and a verb ("stubborn — charges head first"; "cold — never hurries"). More
  than two and none of them reads at 64 px.
- Each trait becomes one SHAPE decision and one MOTION decision per clip, in a table in the brief:

  | Trait | Shape (what the silhouette shows) | idle | walk | attack | hit | death | close-up (victory) |
  |---|---|---|---|---|---|---|---|

  Example (a reading of what the approved units already do): GRANIZO "slow and inevitable" → biggest of the cast (1.55 m),
  a huge sledgehammer; a 30-frame walk (120 steps/min), an attack with a long wind-up (event at 1.30 s) and a short strike;
  OCASO "cold, manipulative" → dome + planted staff; never runs (0.32 m/s), his hero moment is the summon.
- **Push until it reads**: each trait needs ONE big, specific thing (a head gesture of 20°+, a prop with real
  weight, a hunched posture of 15°+), not five subtle ones. Rule: at most 3 design ideas per unit (shape,
  prop, accent color); a detail that does not read at 64 px goes, or grows 1.5–2×.
- The principles critic (skill `character-review`) receives the Essence section and answers per clip: "does trait X show?".

### 0c. Style at scale: "miniature action figure"

Detailed style does not translate to mobile. The house uses the stocky collectible figure (Clash Royale / Warcraft Rumble),
with rules you can measure on the concept:
- **Head** 1/4–1/3 of the height (OSSINHO 0.67 m ≈ 1/3; heroes ≈ 1/4); **hands** ≥ 1.3× real proportion; **prop** ≥ 0.6×
  the body height; wide feet/base (seen from above, the unit must not look like it is standing on tiptoe).
- **Thick, chamfered shapes**: no piece thinner than 4–5 cm (2 px); straps, chains, separate fingers
  and thin fringes do not read — they turn into one mass (plate hand, wide belt, fringe as 3 thick points).
- **Few color blocks**: 3–4 main colors + 1 accent; the hand-painted PBR texture REINFORCES the shape (light on
  top, occlusion in the folds), it never carries the identity on its own.
- **Bold proportion > correct anatomy** (§4b): the model gate may fail by choice (OCASO `overhead` 0.66) —
  that is declared in the brief together with the gesture that fits instead.

### 0d. Close-up moments (unlock, victory, menu) = where the charm lives

- In game the unit is a silhouette; the face shows up in the close-ups. The arena already has the **Portrait** take
  ("Retrato", key 9; automatic after a knockout): the winner turns to the camera and **leans back ~7°** around the
  feet, camera at face height, fov 28, face in the upper third, victory card in the lower third
  (`env/duel/shots/lab/retrato_alvor_s.jpg`).
- Draw the face FOR that take: big, high-contrast features (eyebrow, eye, mouth — or the "face" of a
  machine: FERRUGEM's hatch reads in the Portrait), eye line visible with the head raised 5–10°, nothing in front
  of the face in the idle (hand, prop, hood brim).
- Write in the brief ONE expression per moment (victory, defeat, unlock) and HOW it is made: body + head pose
  (always), jaw / eyelid / eyebrow (2–4 bones, skill `character-rig` §0) or a texture swap / eye
  emission. Today no approved character has a face bone: it is the first thing to ask for in the next brief.

### 0e. Where the character lives (decides the extra bones)

In the brief, name the 1–3 parts that carry personality and swing (ear, tail, cape, hood tip, beard,
chimney, weapon chain). Draw each one as ONE thick mass with a visible root (rule from §2) — it becomes a spring
chain in the rig. Everything else is rigid. A part that does not swing ≥ 2 px (≈ 5 cm) in any clip gets no bone.

## 1. Brief (`characters/<id>/brief.md`, one page)

Copy the structure of `characters/granizo/brief.md`: Pitch · **Essence (1–2 traits + the trait × clip table, §0b)** ·
Look (style lock) · **Readability (shape by role, prop that leaves the silhouette, top seen from above, §0a)** · Separate
objects · Generation rules · Personality → animation notes · **Close-up (expression per moment, §0d)** · Clips. The house style: stocky collectible miniature (Clash Royale /
Warcraft Rumble), hand-painted PBR, thick shapes, silhouette readable at 64 px, nothing thin or loose.

## 2. Drawing rules (each one has a number behind it)

| Rule | Why (measured on BRASA) |
|---|---|
| **T-pose**: arms straight out to the sides, palms down, fingers together, **empty hands**, legs slightly apart | An A-pose at 35° fused armpit and gauntlet into the torso of a stocky character: a tear in close-up |
| Arm (shoulder→wrist) ≥ 1.1 × the distance from the shoulder to a point just above the top of the skull | `overhead` gate: with a short arm the two-handed weapon does not pass over the head; it had to be lengthened 20 % on the model |
| Nothing on the head wider than the head: span (horns, crests, ears) ≤ shoulder width − arm thickness | `corridor` gate 0.70: horn 34 mm inside the arm in 15 frames; 17 poses tried, none solved it |
| Thin handle at the grip (thinner than the wrist), big hands with fingers as long as the palm | `wrap` gate 0.31: the fingers closed 34° before touching a 10–12 cm handle → stylized fist |
| Vambraces/gauntlets straight, with no flared lip, **thinner than the closed fist on the wrist side** and starting 3–4 cm before the wrist | the lip scraped the pommel whenever the wrist bent; on GRANIZO the bracer (13–16 cm radius, fist 12.5) starts AT the wrist: every handle at less than ~50° from the forearm goes through the rim (35 mm, 7–24 frames per clip) |
| Thumb BESIDE the palm (open, pointing forward), never folded under it | GRANIZO came with the thumb pointing down under the palm: `fist_fit.py` finds no wrap at any station along the handle → declared stylized fist |
| Arm (shoulder→wrist) ≥ how far the torso projects in front of the shoulder line + 10 cm | FERRUGEM: boiler 0.44 × arm 0.41 — the fist never passes in front of the body; the strike comes out at the sides and only the hand + claws go through |
| Round pieces on the shoulders (drums, tall pauldrons) count as head span | FERRUGEM: corridor 0.926 and overhead 0.665 because of the drums — no weapon, declared as a limit |
| Wide shoulders call for a proportional arm: (half shoulder width) ÷ (shoulder→wrist) ≤ ~0.6 | GRANIZO 0.40 ÷ 0.64: the pommel hand falls 13–17 cm inside its own shoulder and the forearm lies along the handle; the ported keys needed +7 cm to the side |
| A head sunk between the shoulders (no neck) is allowed, but then the head barely turns: the torso turns | chin and tusks go up to 62 mm into the chest/shoulders when the head tilts; the neck bones must not hold chest skin (rule `neck_not_chest`) |
| Nothing rigid on the shoulder/head line (tall pauldron, chimney); a back prop sits LOW, narrower than the torso | pauldron 22–63 mm inside the helmet; backpack hitting the head on the recoil |
| Every rigid accessory (weapon, backpack, shield) is a **separate object**, generated on its own | welded to the body, it tears just like the weapon |
| Smooth skin at the folds (shoulder, elbow, hip); a high, simple belt | buckle and belt got crushed on impact; smooth skin is where the weight distributes well and where it can be lengthened on the model |
| Rigid head details (tusks, eyebrows) NOT the color of the soft mass | ivory tusks = hair color: the color class grabbed the tusks; it took a box + color |
| Soft mass (beard, ponytail) = ONE thick mass, of a distinct color, with a visible root | it becomes an island + spring chain; a root buried under a rigid shell is permanent overlap |
| One asymmetric marker (strap on one shoulder, broken tusk) | that is how left/right gets checked in every view and on the model |
| Fingers separate and OPEN in the T-pose, and COUNT them in the image and on the model | ALVOR came with six fingers on the right hand: `remove_stub.py` + `skin_patch.py` fix it, but it costs a round |
| Shield: generated on its own, with a visible STRAP on the back, and big enough for the forearm to fit behind the plate with the fist in the strap (≈ 0.3 × 0.5 of the character's height) | ALVOR: the shield at its generated size left the hand outside the strap; 1.3× (0.47 × 0.73 m for 1.5 m) solved it. It is HELD in the hand, in front of the body |
| No painted shine: ask for "matte, no painted highlights, no glow" and turn on "remove lighting" | "the light that comes from Tripo" = metal 1.0 + shine in the texture; `matte.py` removes the metal, not the painted shine |
| Think about the grip when choosing the hand pose | palms-down bind + the top hand gripping from below = a half-turn of twist in the forearm (107–145°) |

## 3. Tripo web (Chrome already logged in; use the `claude-in-chrome` tools)

Generating on Tripo with GPT Image 2.5 is the user's decision (the Runware generator did not obey the T-pose).

1. **Image** (icon at the top of the left bar) → model **GPT Image 2.5**. Prompt in English with: style, description,
   POSE in caps (T-pose, palms down, empty hands), "no weapon, nothing on the back", white background, even
   lighting, frontal camera with no perspective. To keep the house style, attach the `refs/tpose_front.png` of an
   approved character as reference and write "same art style … but a COMPLETELY DIFFERENT character".
   Aspect ratio 4:3 (a T-pose is wide), 2 images (8 credits).
2. Check the image before spending on 3D: a real T-pose, hands empty and open, asymmetric marker on the correct
   side (HIS LEFT side is on the viewer's RIGHT), arm/head within the rules (measure in pixels).
3. **Views**: the image's "Generate multiview" button (cube icon on hover) sometimes returns oblique views
   (it happened twice in a row on GRANIZO). If the four are not straight front / left profile / right profile / back,
   generate each view with GPT Image 2.5 using the front as reference and an explicit prompt ("strict 90-degree
   profile, he faces the LEFT edge of the image, his left arm points straight at the camera…", "seen from DIRECTLY
   BEHIND…"). Left profile = camera on his left = he looks toward the left of the image.
4. Download each image (arrow on hover). **Check where this Chrome profile downloads** (`chrome://settings/downloads`:
   not always `~/Downloads`); the names repeat (`image_0.png`), so move one at a time to
   `characters/<id>/refs/view_{front,left,right,back}.png`.
5. **Model** (second icon) → multiview tab (cube icon) → upload Front / Left / Right / Back →
   "Geometry and texture": Ultra mesh, 4K texture, remove lighting, PBR, triangles, 2,000,000 → **H3.1 – Max
   quality** → Generate (55 credits, a few minutes).
6. Export → GLB → move to `characters/<id>/model/<id>_hi.glb` (the 2 M triangle version: shape reference
   and bake source).
6b. **Always Remesh → Smart UV → Texture** (the user's rule, 2026-11-14, UIVO): the UV that Tripo generates with the mesh
   is chopped into hundreds of islands (58 % occupancy on UIVO) — nobody repaints that later. Smart UV (left bar)
   only accepts ≤ 80,000 triangles, so: **Remesh** → Triangle, "Smart Mesh" OFF (with it the ceiling is 20,000 and it
   costs 35; without it it goes up to 150,000 and costs 5) → **60,000** (the game budget) → Retopology; then **Smart UV**
   on the result (20 credits); then **Texture** (4K, PBR, no lighting). Export → GLB →
   `model/<id>_game.glb`. That is the game mesh: clean UV, repaintable texture; `gameready.py` only rebakes if needed.
   Budget: the user authorizes **up to 5,000 Tripo credits** per character for this flow (remesh, Smart UV,
   texture and whatever retries the quality calls for) — do not skimp on it; log every spend in `state.json → tripo`.
6c. **Jaw ALWAYS open** in the concept for this style (the user's rule): "mouth open ~25 deg, upper and lower teeth
   apart, tongue inside" in the prompt of EVERY view, and check it in the image before 3D — a welded mouth gets no jaw
   bone, and the bite, the roar, the howl and the panting while running all live in it (UIVO: `DEF-jaw` + weight rules
   `lower_jaw` / `upper_muzzle` / `throat` in `characters/uivo/rig/landmarks.json`).
7. **Each prop is a separate generation**: isolated image (whole object, vertical, white background, with the character
   concept as style reference) → single-image "Generate 3D" → GLB at `model/<id>_<prop>_hi.glb`. Measure the handle in
   the image (width ÷ length) before generating.

Generations consume credits from the user's account: generate 2 options, pick one, and do not repeat without a reason.
Log in `state.json` what was generated and what was discarded.

## 4. After the GLB

The judge is `model_gates.py` (skill `character-rig`). Failed? In order of cost: lengthen/tilt on the model
(`proportions.py`, `part_tilt.py`, reversible) → regenerate the image with the rule made explicit → accept it as a
declared limit (and tell the user so, with the number).

## 4b. Silhouette first — not a humanoid in costume (user, 2026-11-11, OCASO v1 → v2)

"I don't want the characters always as perfect humanoids... they need more of the style of the clash royale picture." The
v1 necromancer was a man of normal proportions with a coat, pants and boots: he read as generic and was redone.

- Start the brief from the SHAPE, not from a body: head ≈ 1/3 of the height, huge hands and prop, floor-length cloak / bell /
  hunch / hidden legs where it fits, asymmetry, attitude. A reference gives the LANGUAGE, never the character
  (no copied helm, beard, staff or palette): the design is original.
- A mini like that fails `overhead` / `corridor` by design (OCASO 0.66 / 0.70; OSSINHO 0.72). That is a choice, not a
  defect: write in the brief what it NEVER does (raise the arm beside the hood, an overhead strike) and give
  it a gesture that fits (planted staff, low claw in front, diagonal slash).
- With no visible legs the cloak is the base: it does not stagger, it TOPPLES (death = inverted pendulum over the edge of the hem).
- A summoned unit = another character (its own brief, model, rig and clips), smaller and simpler, with `spawn` in
  place of `hit` if the budget is five clips.
- **A training dummy / prop that takes hits** (TOCO) is not a character: a single image on Tripo (GPT Image 2.5, 2 options
  with an approved character's prop as style reference) → single-image "Generate 3D". What the design needs: a painted
  SIDE that says "hit here" (target disc) and that will face the camera; thick stacked masses (tied sacks, not loose
  straw — the option with a straw skirt was discarded); a WIDE cross-shaped foot (it is the edge it topples over,
  0.22–0.27 m on a 1.15 m dummy) with the post rising from the center; a head separated by a narrow neck (it becomes
  the 2nd pivot of the springs).
  A left/right marker as well (a patch on one side of the sack).

## 5. What the second character (GRANIZO) taught about the brief

- Write in the brief only what the silhouette needs. The ice block on the back was cut: it was in the hammer's path behind
  the head (the rule "nothing rigid on the shoulder line" also applies to whatever the brief itself invents).
- Very light skin blows out to white under the stage lights: `stage.py --arg exposure=-0.9` (or
  `scene.view_settings.exposure`) before judging any image.
- Tripo welds the ponytail to the nape and fuses the fingers: accept it (soft chain by color, single plate hand) instead
  of spending credits trying to separate them.
- Generate and MEASURE before you fall for it: `model_gates.py` (overhead / corridor / wrap / **cuff**) + `limb_radii.py` + slices (section 2 of the skill `character-rig`) tell you in
  minutes whether arm, corridor, bracer and grip pass. Redoing the concept costs 55 credits; finding out in the clip costs the day.

## 5b. One idea, amplified into OBJECTS (GRANIZO v3, 2026-11-14 — "it got a lot better but it can get even better by following the principles of originality")

v2 read as "ogre with an axe". v3 starts from ONE sentence — *he IS the glacier* (the glacier grew over him) — and every
asset is born from it:

- The idea becomes **asymmetry of separate objects**, each one generated ON ITS OWN on Tripo (2 options of each): the LEFT
  side glaciated (fist = a 0.61 m ice block on the hand, an ice crust on the left half of the hump), the RIGHT side still
  ogre (the one-handed "Quebra-Geleira" / Glacier-Breaker pick). 276 credits in total (concepts 32, views 24, multiview body + 3
  props 220). One prop per trait reads at 64 px; the same trait painted on the body does not.
- Two amplified traits and only two: the glacier fist (asymmetry) and the CRACK (every strike splits the ground). Each clip
  tells a story with one of them (idle: the ice creeps up the arm and he shakes it off; death: the glacier closes over him).
- **A hump that rises behind the skull** traps the head: the Rigify head bone is isolated and the hump sits right
  behind it — tilting the head back past −10° makes it go in (−20° = 26 mm). If the design has a hump up to the crown,
  write in the brief: he looks UP with the eyes and the torso, never by throwing the head back.
- Arm short for the torso (half shoulder width ÷ arm 0.97, rule ≤ 0.6) and hump = `overhead` 0.70,
  `corridor` 0.90, `cuff` 0.93 by design: the wind-up goes over the RIGHT shoulder, the fist works on its own side.
