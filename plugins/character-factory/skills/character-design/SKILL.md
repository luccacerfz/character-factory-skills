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
| A RAISING gesture with the prop above the head: arm (shoulder→wrist) ≥ 0.4 × height | CENTELHA (1.2 m): shoulder at 62 cm and an arm of ~32 cm — the crystal never got above 1.62 m; the three variants that tried it put the staff through the torso (35.5 mm) or the leg (31.2 mm). The "raise" ended up reading through the jump and the downward strike |

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
   quality** → Generate (55 credits, a few minutes). Never 8K (65): it does not reach the game — §3a. This whole
   stretch (5–6b) also runs in the **Agentic Canvas**, with retopology + bake + Smart UV in a single node — §3b.
6. Export → GLB → move to `characters/<id>/model/<id>_hi.glb` (the 2 M triangle version: shape reference
   and bake source).
6b. **Always Remesh → Smart UV → Texture** (the user's rule, 2026-11-14, UIVO): the UV that Tripo generates with the mesh
   is chopped into hundreds of islands (58 % occupancy on UIVO) — nobody repaints that later. Smart UV (left bar)
   only accepts ≤ 80,000 triangles, so:
   - **Remesh** → Triangle, **"Smart Mesh" P1.0 ALWAYS ON** (the user's rule, 2026-11-15: "always use Smart Mesh
     P1"). With it the ceiling is **20,000** polygons and it costs **35**; off, it went up to 150,000 for 5, but do
     NOT turn it off (a body made at 60k without it was discarded and redone).
   - Count: body **20,000** (the ceiling); a prop by its size on screen (fist / hand weapon 6,000, small piece
     2,000–4,000) → Retopology.
   - The Remesh panel remembers the last choice. Before clicking, zoom in and check the switch, the number and the
     price on the button ("Retopology 35" = Smart on; "5" = off, wrong).
   - Then **Smart UV** on the result (20 credits). Measured on a brute's body: on the Smart P1 mesh of 18,907 tris,
     70.8 % occupancy in LARGE islands; on the 60k mesh without Smart, 56.7 % in hundreds of slivers. That is the
     reason for the rule.
   - To redo the remesh of a mesh that was already processed: History (clock icon in the viewer) → the generation's
     version (✦ icon) → **"Save as New Model"**. "Restore This Version" only shows the version and, with it, the
     Retopology button stays disabled.
   - Then **Texture**: the 4 views come in by themselves as reference. The panel opens with **8K** selected and
     **"Remove lighting" OFF**: switch to **4K** (20 credits) and turn remove lighting ON.
   - Export → GLB → `model/<id>_game.glb`. That is the game mesh: clean UV, repaintable texture. After the import, the
     **paint pass** of §3c enriches this albedo with the maps baked from the `_hi.glb`. In Blender:
     `import_model.py` of the `_game.glb` → `gameready.py --arg tris=20000 --arg bake=false` (it only rebakes if needed).
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

## 3a. What resolution buys — NEVER 8K (measured 2026-11-16)

The user's question: "is the best path HD Model 3.1 at 8K → Remesh P1 → Smart UV → Texture → enrich it in Blender?"
The ORDER is that one. 8K has no place anywhere in it.

| Step (Tripo UI on 2026-11-16) | Credits | Note |
|---|---|---|
| HD Model H3.1, geometry only | 15 (up to 1 M) / 30 (Ultra, up to 2 M) | |
| HD Model Ultra + 4K / 8K texture | 55 / 65 | "8K texture" is a subscriber switch |
| Direct Smart Mesh (P2.0, or "P1.0 – Fast") | 100 | 500–25,000 quads, 1/2/4 generations |
| Remesh + Smart Mesh P1.0 | 35 (triangle, up to 20,000) / 40 (quad, up to 10,000) | |
| Smart UV | 20 | it warns: "Smart UV will remove the current texture" |
| Texture 4K / 8K | 20 / 30 | opens at 8K with "remove lighting" OFF |
| PBR generator · Magic Brush (preview) · Upscale 4K/8K · Auto rig | 5 · 5 · 20 · 20 | |
| Export | 0 | USD, FBX, OBJ, STL, GLB, 3MF; texture 512–4k |

- **The HD Model's 8K never reaches the game.** In the workspace, Smart UV erases the texture and it is generated again;
  in the Canvas, the retopology node bakes the HD texture onto the new UV (resampled). Either way the final texture is
  born later.
- **The 8K of the texture step is AI upscaling** (Tripo's help calls it "HD Textures with AI Upscaling"): invented
  realistic micro-detail — the opposite of the target, which is flat colour + painted shading.
- **Measured** on a brute's 4K albedo (shrink it and scale it back up): 2048 → PSNR 49.2 dB, mean error 0.40/255, 0.10 %
  of the texels off by more than 8/255; 1024 → 43.0 dB, 0.74/255, 1.13 %; 512 → 36.9 dB. 68.5 % of the used texels are
  flat colour. Tripo's 4K carries ≤ 2K of information in this style (≈ 1K with no visible loss) and it arrives as a
  JPEG inside the GLB.
- So: **generate at 4K** (a clean source for the paint pass of §3c), **ship 2K** for the close-up and 1K in game
  (shrink it at Unity import). An 8K takes 16× the memory of a 2K and shows nothing the game camera can see. Our
  importer already decides this: `CFImporter.Tex` imports every character map with `maxTextureSize = 2048` + mipmaps
  — nothing above 2K reaches the game today, whether the source is 4K or 8K.
- **Where the "detail" of a collectible mini comes from** (the user's reference: 4 colour blocks + 1 accent, THICK
  tufts of fur and cut cloth, a soft gradient, a light edge, zero texture noise): (1) SHAPE — a tuft, a fringe, a fold,
  a buckle are GEOMETRY; ask for "thick", "chunky", "big", "5 big points" in the concept (not 30 little spikes);
  (2) SHADING PAINTED into the albedo (§3c); (3) the SHADER (rim + wrapped light — skill `character-engine` §2i).
  Texture resolution is not on the list.
- **FPS** is not decided here: what weighs on a phone is 1 material/atlas per character, bones (the budget in
  `character-rig`), LODs (`lod.py`) and the texture IMPORT size. The 2 M HD mesh never goes to the engine — it is a
  bake source.
- **HD Model vs direct Smart Mesh.** Tripo's help positions the HD Model (up to 2 M) for printing and sculpture, and
  Smart Mesh for games. We use both on purpose: the HD is the SOURCE of the bakes (the `_game.glb` already ships a 2K
  normal map truly baked from the HD; the paint pass bakes five more maps from it) and Remesh P1 gives the mesh.
  Direct P2.0 splits the object into PARTS that are not welded (Merge by Distance in Blender), has per-part symmetry
  and only keeps quads in FBX: a candidate for rigid props. It was not tested on a body — without the HD there is no
  bake source.

## 3b. Tripo's Agentic Canvas (studio.tripo3d.ai → Canvas) — a healer built end to end, 2026-11-16

A node graph (Upload, Generate image, Multi-view, HD Model, Smart Mesh, Retopology, Smart UV, Texture generation, PBR,
Rigging, Animation, AI 3D Lab, Export…) with a chat Agent that plans and assembles the nodes. **Control** mode (it
shows the plan and stops at each stage: "Continue") or **Auto**. Planning is free; each node costs the same as in the
workspace. The graph stays saved in the project: swap the input image, run again, and the whole line is redone.

What the Canvas does BETTER than the workspace:
- **Retopology in one node: Bake + "Smart Low Poly v2" + Smart UV = 35 credits**, and the HD texture comes baked onto
  the new UV (in the workspace: Remesh 35 + Smart UV 20, and the texture is lost). The healer: 1,919,842 → 17,208
  triangles / 9,849 vertices.
- **The "T-pose" template of the Generate image node**: chained on an approved image, it redraws the SAME character
  in a T-pose (takes the prop out of the hand, changes the skin colour, fixes the collar) without losing the shape.
  A two-node flow: (1) free shape → (2) T-pose.
- The strip of **"sets"** under the Multi-view group keeps every round of views; a click goes back to an earlier one.
- Rigging with a skeleton preset (Mixamo, ActorCore, UE5 Mannequin, Unity Humanoid Compatible, VRM 1.0) and an "Other"
  tab for what is not a humanoid (the workspace lists Quadruped, Hexapod, Octopod, Bird, Serpentine, Aquatic); image
  generation (GPT Image 2, Nano Banana, Midjourney) cost 0 on this account.
- **Rigging + Animation measured on the healer (20 + 20 credits).** Mixamo rig in ~1 min. The Animation node has a
  Generate tab (text → motion, a duration slider — 5 s — and "Multi-step motion") and a Library tab (ready presets +
  "AI Animation"). The idle asked for in text ("tired old healer, hunched, sways, blows on his hand") came back at
  4.96 s with the right idea in the 3 frames checked: hunched trunk, hand to the mouth, the skirt following the legs
  with no tear. What it does NOT have: a prop, events, measured contact and floor, a checked loop, a bone for the jaw /
  ears / topknot / skirt (it is the plain Mixamo skeleton). It works as a PREVIEW and as a cheap motion reference
  without leaving the Canvas; it replaces neither `character-rig` nor `character-clips`.

What the Agent gets WRONG — check the NODE, not its sentence (click the node after it runs):
- `#` in the chat is a node reference: `#6E6A66` became "I can't find #6 on this canvas". Write colours WITHOUT `#`.
- I asked for a 4K texture on the HD Model: the node ran at **8k** (65 credits instead of 55). The plan does not show
  the parameters.
- I asked for a texture "from the 4 views, remove lighting ON": the node ran on the **Image** tab (the front only)
  with the switch OFF. On the second try it turned the switch on and still used one image ("it was created from a
  single image").
- It planned a separate Smart UV node after a Retopology that already had Smart UV on (20 credits for nothing: tell
  it to skip).
- "I couldn't plan 'Rig … with a biped skeleton'": the Rigging node had to be created by hand (the PBR node's bar →
  the figure icon).
- With a style reference from another character it copied the BODY (a muscular warrior in a short skirt instead of
  the bell-shaped healer). The fix goes in the node's own prompt: SHAPE first, in capitals ("SILHOUETTE = A BELL WITH
  A HUGE HEAD… NOT a warrior, NOT muscular… the skirt HIDES THE LEGS"), and what the reference must NOT give ("a
  COMPLETELY DIFFERENT body").
- **The Multi-view node**: free, no prompt, and a lottery — 3 runs gave 3 napes (bald, a cap of hair, a ponytail) and
  profiles at 3/4. Check the BACK before the 3D; if no set works, item 3 of §3 applies (views by prompt).

Verdict: use the Canvas for the Tripo part of a new character (concept → T-pose → views → HD → retopology with bake →
texture → PBR) with the Agent in Control mode only to ASSEMBLE the nodes, and set each node by hand before generating.
Do not delegate the brief, the choice of views or the parameters to it. Tripo's rig and animation are good for a
preview; the production rig is still Rigify with weights by region (skill `character-rig`) — that is the one that
passes the gates and the 5 measured clips.
Measured cost of the healer's body in the Canvas: HD 65 + retopology 35 + texture 20 (+20 redone) + PBR 5 + rig 20 +
animation 20 = 185 credits.

Not verified in this round (do not treat as a rule): whether the Multi-view tab of the texture node really uses the 4
views (the Agent only ever built it with 1 image); what comes inside the rigged/animated GLB (bone names, fps) —
nothing was exported yet; direct Smart Mesh P2.0 on a body.

## 3c. Enriching the texture in Blender: the PAINT pass (rig-safe, 2026-11-16)

Tripo's albedo with "remove lighting" is flat colour (which is what we want as a base) — and that is why the character
comes out looking like plastic: it lacks the light a miniature painter puts into the paint. The pass bakes from the HD
what the painter needs and paints the albedo on the SAME UV (mesh, weights and normal map untouched; it works on a
character that is already rigged and animated).

```
Blender -b --factory-startup --python blender/paint_bake.py -- model/<id>_hi.glb model/<id>_game.glb model/tex/paint 2048
.venv/bin/python cf/tex_paint.py model/tex/paint/basecolor_orig.png model/tex/paint model/tex/paint/basecolor_painted.png
Blender -b model/tex/paint/game_scratch.blend --python blender/paint_look.py -- <albedo.png> <prefix> mini   # A/B
```

- `paint_bake.py` (BACKGROUND Blender, it does not touch the live session; 58 s including the 2 M import): fine AO (3 %
  of the height) and broad AO (30 %), an OBJECT-space normal, and a map with fine curvature (R), broad curvature (G)
  and height (B) — the curvature is computed with numpy on the HD vertices (position − smoothed position, projected
  on the normal; 24 and 220 Laplacian iterations) and baked as emission. The HD and the game mesh leave Tripo in the
  same space (bounds equal within 1–2 mm): the selected-to-active bake works directly, cage 0.8 % of the height. It also
  writes the GLB's albedo as `basecolor_orig.png` (once; it never overwrites it).
- `tex_paint.py` (numpy, ~5 s, everything in LINEAR light): a fixed key light from above and in front with wrap,
  occlusion, a dark line in the fine cavities, a highlight on the convex edges that face the light, a ground gradient;
  the shadow goes darker, MORE saturated and cooler, the light warmer. `deadzone` separates a drawn line from surface
  grain (without it a skirt turns into speckle). Tune per character: `edge=0.3 cavity=0.5 grad=0.2 'light=[0.2,-0.5,1]'`.
  The maths, for whoever rebuilds it: `v = (key_lo + (key_hi − key_lo)·wrap(N·L)) · occlusion · (1 + form·broad_curv) ·
  (1 − cavity·concave) · ground`, normalised by its median; `colour = albedo·v`, shadow tint `[0.80, 0.86, 1.12]` and
  light tint `[1.07, 1.02, 0.90]`, saturation `1.10 + 0.40·shadow`, a warm highlight on the convex edges × a smoothstep
  of the light. Defaults: wrap 0.55 · key 0.66–1.16 · ao_broad 0.85 · ao_fine 0.55 · floor 0.38 · form 0.10 ·
  cavity 0.42 · edge 0.40 · deadzone 0.15 · smooth 1.8 px · grad 0.14.
- Judge with `paint_look.py`: original vs painted, shader `lit` (Unity's Standard) and `mini` (60 % unlit paint + 40 %
  lit + a cool rim from the GEOMETRY normal), in a close-up, from the back and at the game camera at 64 px. On the
  brute, the painted one gains readability in the face, the cracks and the muscles under both shaders; at 64 px the
  difference is small (contrast) — the gain belongs to the close-up and the portrait, where the charm lives (§0d).
- Texture passes do not stack blindly: this one ALWAYS starts from `basecolor_orig.png`. `ao_bake.py` + `tex_grade.py`
  (AO in the character's .blend + emission of the cracks) is another pass over the same original; pick one as the
  base and apply the other on top only if the A/B asks for it.
- **Where the pass stops today**: proven in a render A/B (scratch copies). The `basecolor_painted.png` has NOT yet
  gone through `export.py` → `to_unity.py` → Unity, and the `mini` shader exists only in `paint_look.py` (in Unity the
  body uses Standard — `character-engine` §2i). Before calling a character "painted", run that trip and judge it in
  the arena.

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


## 5c. An effect that is a light OBJECT (crystal, cage, shards): Tripo vs procedural vs glass (CENTELHA r12–r14)

- Tripo works for an effect asset (a GPT Image 2.5 image with an approved prop as style reference → single-image
  "Generate 3D", 55 credits): ask for "wide clear gaps between them" and the pieces come out separate
  (`blender/fx_asset.py parts=row` groups the loose shells: 110 shells → 5 shards); collapse decimation keeps the UVs
  (1.96 M → 500 triangles).
- But the user asked for "much cleaner and more cartoony" than the scan (blobs with orange veins). A cartoon crystal is
  PROCEDURAL (`cf/fx_crystal.py`): 5–6 FLAT facets, a 3-stage taper to the tip, each face with its own vertices; a
  256 px atlas with 3 tone bands (each facet takes a tone from the direction of a fixed light) + a light stripe on the
  ridge. Same npz + png contract as `fx_asset.py`. Cage 268 triangles (Tripo 1,600), shard 20–44 (Tripo 500).
- "More translucent and cartoony" = cartoon GLASS: translucent facet interior per band (alpha 0.34–0.68), an opaque
  outline on the ridges (0.11 of the canonical tip/foot UV), a white glint; in the engine a two-pass shader (multiply
  the background by a golden transmission, add colour + fresnel) — skill `character-engine` §2g.
- Colour next to another character: cream disappears against the skeleton's BONE (use lemon); gold alpha over grass =
  lime; in linear space a pale gold that is added becomes cream — use a saturated palette. Cage tips 0.20 m from the
  target's axis (at 0.07 m they went through the skull).
- Size on the phone: a 0.75 m cage on a 0.70 m target (tips just above the skull, ring < half the distance between
  neighbours); rain shards of 0.48 m (0.18–0.30 m gave 8–13 px and vanished).
