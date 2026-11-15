---
name: character-rig
description: From the generated GLB to a rigged character with no deformation in the Character Factory — import into live Blender, game mesh (60k + bake), landmarks, MODEL GATES before the rig, lengthen/tilt in the model, Rigify + weights by region, props on their own bone, pose test and hunting down deformations. Use when there is a new model to rig, when the user says "rig", "weights", "skinning", "there is still deformation", "the arm goes into the body", "armpit tear", or after any change to rig/landmarks.json. Includes the mobile bone budget (base 30, fingers ≤ 8, extra bone only where there is character: ear, tail, cape, beard, chain).
---

# Rig and deformation

Input: `characters/<id>/model/*.glb` (body in T-pose + one GLB per prop). Output: `<NAME>` + `<NAME>_rig` in the scene,
`rig/landmarks.json`, a clean pose test. Operating rules and live Blender rules: skill `character-factory`.
Full commands: `factory/README.md` ("Step by step", steps 4–5). Example: `characters/brasa/rig/landmarks.json`
(the `_doc*` keys explain each block).

## 0. Simple mobile rig: bone budget (game principle 7)

A clean skeleton with few bones; an extra bone ONLY where it adds character (ear, tail, cape, hood, beard,
chained weapon). Rigify is the tool (Auto-Rig Pro is not installed and is not needed: the export takes only the DEF
bones with Mixamo names). Count measured on the Unity prefabs (bones used by the `SkinnedMeshRenderer`s, 2026-11-14):

| Unit | Total | Base | Fingers | Props | Extras (character) | Effect (`Fx*`) |
|---|---|---|---|---|---|---|
| BRASA | 49 | 30 | 8 | 1 | 10: Beard ×3, Tabard ×4, LeftPauldron, Backpack, Chimney | 0 |
| GRANIZO | 46 | 30 | 8 | 1 | 7: Hair ×3, Tabard ×4 | 0 |
| OSSINHO | 47 | 30 | 12 | 1 | 4: Tabard ×4 | 0 |
| ALVOR | 64 | 30 | **20** | 2 | 4: Tabard ×4 | 8 (aura) |
| OCASO | 90 | 30 | **20** | 1 | 3: Hair ×3 | **36** (beam, hex, columns) |
| FERRUGEM | **143** | 28 | 12 | 0 | 0 | **103** (explosion into pieces) |

Base = root, Hips, Spine/1/2, Neck/1, Head, shoulder + deltoid + arm + twist + forearm + twist + hand per side,
thigh + leg + foot + toe per side (30; FERRUGEM has no deltoid: 28).

Rules (budget per game unit; the number applies to the NEXT character):
- **Deformation ≤ 50 bones** (not counting `Fx*`): base 30 + fingers ≤ 8 + character ≤ 10 + 1 per rigid prop. Four
  influences per vertex (already the export contract).
- **Fingers ≤ 8** (thumb 2 + a block of the others 2, per hand): at 64 px a finger is less than 1 px. Separate fingers
  (20) only if a close-up (Retrato portrait, unlock) shows the hand closing — otherwise it is per-unit CPU cost with no
  readability gain. ALVOR and OCASO are above that because of a one-handed grip (a decision from that stage); do not copy.
- **A character bone has to move on screen**: every extra bone has to travel ≥ 2 px (≈ 5 cm at the tip) in some
  clip — read the displacement of the bone's tail in `motion_table.py`. It did not move: merge it with its parent or
  remove it. Spring chain: 2–3 bones (beard, ponytail, tabard), never 6.
- **Face for the close-ups** (skill `character-design` §0d): jaw 1 + eyelid/eyebrow 1–2 per side, only when
  the brief asks for expression; they count toward the character budget.
- **An effect does not live in the unit's skeleton if it happens ONCE**: an `Fx*` bone animated by scale is cheap in
  the clip that uses it, but it is paid for in every frame of every living unit. FERRUGEM carries 103 piece bones just
  for its death — a known limit; the next character that explodes carries the pieces in a prefab of its own,
  instantiated on the death event (`CFExplosion` already receives the event), and the living skeleton returns to budget.
- Check at the end of the rig and again at export: the `bones` key of the manifest (`characters/<id>/export/<NAME>.json`)
  and, in Unity, the same snippet that produced the table above (union of the `r.bones` of the prefab's
  `SkinnedMeshRenderer`s, split by name: `Fx*`, fingers, base, props, the rest = character). Over budget: write down why
  in `state.json`.

## 1. Entering the scene

```
bl.py run blender/reset_character.py                       # only if the scene holds another character; save its .blend first
bl.py run blender/stage.py --arg character=<id> --arg concept=<refs/tpose_front.png>
bl.py run blender/import_model.py --arg glb=<glb> --arg name=<NAME> --arg height=<m> --arg review=<dir>
bl.py run blender/gameready.py --arg name=<NAME> --arg tris=60000 --arg outdir=<model/textures> --arg review=<dir>
bl.py run blender/ortho.py --arg name=<NAME> --arg outdir=characters/<id>/rig ; .venv/bin/python cf/grid.py characters/<id>/rig
```

One `.blend` file per character (`characters/<id>/<id>.blend`). A prop decimated without welding cracks into shards:
`open_edges` in the report has to be 0.

## 2. Landmarks: read them from the sheets, never guess

`ortho_front_grid.jpg` / `ortho_side_grid.jpg` have a metric grid. Write `rig/landmarks.json`:
- `joints` in meters at rest. A joint with `y: null` is centered on the **rest** mesh (a silent default once put
  bones outside the arm). The shoulder is the center of the deltoid, not the armpit; the wrist is where the hand bends,
  not the edge of the vambrace.
- `regions` (weight boxes/colors), `props` (target box + bone + rotation of each prop), `keepout` (capsules for rigid
  head tips: horns, wide tusks), `secondary.chains` (sway ceiling of the loose masses), `weapon`, `grip`.
- Check left/right against the brief's asymmetric marker before anything else.
- **Measure the mesh before writing down a number**: slices by height/axis (where each piece starts and ends, the arm's
  cross-section, the bracer's radius), average colors per band (HSV) and close-ups at WORLD points without the rig:
  `bl.py run blender/look_at.py --arg out=<dir> --arg 'spots={"mao":[x,y,z,raio]}'`. On the second character all the
  landmarks came from measurement and the rig passed the gates on the first build.
- Vocabulary the second character added (all optional, data-driven):
  - `extras`: `[{"chain": "hair", "joints": [...], "parent": "spine.006"}, {"bone": "backpack", "joints": [a, b], "parent": ...}]`
    — without the key, BRASA's list applies. House names: `hair*` / `beard*` (soft chains that collide with the prop),
    `tabard_f` / `tabard_b` (belt flaps), `backpack`. The hand prop is always `<NAME>_hammer`.
  - `colors`: HSV classes per character (`{"ivory": [{"h": [12, 48], "s": [0, .25], "v": [.72, 1]}]}`), used in `regions[].color`.
  - `regions[]`: `fade_x: [x0, x1]` (the region fades out to the sides: a flap welded to the thigh) and `soft_passes`
    (soft color edge).
  - `limit[]`: weight ceiling with `ramp [z_livre, z_teto]` in BOTH directions (upward or downward).
  - `limbs`: measured arm radii — `bl.py run blender/limb_radii.py --arg name=<NAME> --arg landmarks=<json>`.

## 3. Model gates — before the rig

```
bl.py run blender/model_gates.py --arg name=<NAME> --arg landmarks=<json>
```

| Gate | Measures | If < 1 |
|---|---|---|
| `overhead` | arm ÷ distance from the shoulder to 6 cm above the top of the skull | `proportions.py --arg factor=<n>` lengthens the arm IN THE MODEL (only the smooth skin; mesh, high-poly, LOD and landmarks through the same map; reversible) |
| `corridor` | (shoulder width − arm thickness) ÷ span of everything above the head | `part_tilt.py` (tilts horns/crests in the model, `dry=true` first) or generate it again; no pose solves it |
| `wrap` | how far the fingers close before touching the handle (only after `fist_fit.py`) | thinner handle, longer fingers, or a stylized fist **declared** in `grip._fit` |
| `cuff` | half width of the fingers ÷ radius of whatever covers the last 12 cm of the forearm (bracer, gauntlet flap) | generate it again with a bracer that tapers to the wrist / ends 3–4 cm before it; otherwise `wrist_ulnar_max_deg` in the clips and a declared limit (GRANIZO: 0.925 → pommel 34 mm into the bracer) |

The report also includes `shoulder_half_over_arm` (a fact, not yet a gate: 0.56 on BRASA carried a two-handed prop
well; 0.63 on GRANIZO left the pommel hand inside the shoulder).

Why before: on the first character all three failed and only showed up after five finished clips (horn 34 mm
inside the arm over 15 frames; 17 pose attempts only switched the side of the contact). The arm thickness is the
**measurement on the mesh**: the "impression" said 15 cm, the mesh 20–22 cm.

## 4. Rig, weights, props

```
./rebuild_rig.sh <id> <NAME>     # rig_build → prop → recap_island → rig_bind → split_plates → rig_extras → attach_prop → fist_fit → pose_test
```

Run it after ANY change to the landmarks (~40 s). Auto-Rig Pro is not installed: Rigify. Rules that are already in the
code and that you need to feed through the landmarks:
- Every rigid accessory is a separate object on its own bone (`props` + `attach_prop.py`); `prop_bones` do not hold skin.
- Rigid plates that move against each other (vambrace | hand) do not share skin (`split_plates.py`).
- A weight transition never sits on a painted edge: the rigid region swallows the edge, the ramp goes on the smooth skin.
- Forearm: a half-twist bone carries the vambrace; the twist is distributed (elbow / wrist / hand).
- A welded mass that bends (beard, ponytail) = island + back side in strips (`split_props.py`, `recap_island.py`).
- Automatic weights failed (< 90% of the vertices)? `rig_bind.py` falls back to the voxel proxy on its own.
- Tear = (weight step) × (how far that bone travels). Recipes GRANIZO needed:
  - head without a neck: `limit` `neck_not_chest` (neck bones with ceiling 0 below the chin, ramp toward the chest) +
    a wide `feather` on the jaw (0.07) — the neck held skin 20 cm in front of its own pivot (69 edges 13→47 mm);
  - rigid boot/greave: `limit` `boot_is_foot` (shin with ceiling 0 on the boot, long ramp);
  - fabric flap welded to the thigh: `tabard_*` chain with `fade_x` + `soft_passes 4` and a wide hip ramp
    (edges > 30 mm with the knee raised: 83 → 33);
  - rigid bracer: region on the bone WITHOUT twist (`DEF-forearm.L/R`), wrist rotating at the bracer|hand cut
    (`hands.cuff_pin`); then the forearm twist stops showing (see skill `character-clips`).

## 4b. Generator fixes, look and held props (ALVOR)

- **Extra finger / protrusion**: `blender/remove_stub.py` (cuts and closes the skin) → `blender/skin_patch.py` (repaints
  the shadow and the crease the generator painted at the root; `dry=true` first, read `other_paint_by_5mm` to choose
  `force`). Apply it to the high-poly too if it is still used for the bake.
- **Matte look** ("the light that comes from Tripo"): `blender/matte.py` — scaled metal, roughness floor, no specular;
  the numbers live in the material (`cf_matte`) and the export carries them to the engine. No texture repainting.
- **Hand with separate fingers**: `hand_fingers.py` proposes the joints (`landmarks.fingers`), `hand_test.py` closes the
  fist and measures. Finger hinge = axis read from the bone, not a fixed world axis.
- **Blade**: `prop_blade.py` (axis, guard, pommel, half-thickness, half-width) instead of `prop.py`.
- **HELD shield**: `props[]` with `bone: DEF-hand.<lado>` + `seat` (scale, rotation, offset — `hand_seat.py`
  reads the handle and brings it inside the fist). If the fist cannot reach the handle with the forearm behind the plate,
  enlarge the shield (ALVOR: 1.3×), do not stretch the arm. The shield's face lives on the object (`cf_face`) so that
  `onehand.py` can aim it.
  Give the held prop an `own_bone` (`props[].own_bone: "DEF-shield"`; `prop_own_bone.py`, called by `rebuild_rig.sh`):
  a child bone of the hand with the same rest — nothing changes in the clips, and the death can DROP the prop (without it
  the shield stays weighted to the hand and a dead arm keeps "holding": two critique rounds on ALVOR). It goes into
  `prop_bones`.
- **Effect**: `landmarks.fx` + `fx.py build=true` (`rebuild_rig.sh` calls it): mesh on parentless `DEF-fx_*` bones.

## 4c. Body of rigid pieces and a short-legged mini (OSSINHO, 0.70 m)

- **Skeleton**: each bone is a locked rigid region (boxes in `regions`, processed in order — the one further down wins);
  only the necks between the pieces bend. The rib | humerus-head weld still stretches up to 35 mm in the test poses:
  it reads as a ball joint with a crease, was accepted and DECLARED (the cure would be a generic cut between rigid bones).
- `pose_test.py` scales the movements by leg length (< 40 cm): 22 cm of raised foot on a 16 cm leg
  gave 121 of 136 stretched edges — a defect of the test, not of the rig.
- `prop_blade.py --arg guard_min=0.85` (or `weapon.guard_min`): a WIDE blade (cleaver) is read as a guard with the
  default 0.5 (`guard_thick_z` 0.294 — the whole blade).
- `hands.stub` / `stub_taper` / `stub_shade` in the landmarks: the wrist stub of `split_plates.py`, per character
  (thin bony wrist: 0.012 / 0.75 / 0.3 — the default came out dark outside the fist).
- Asymmetric generator (4 fingers on one hand, 3 on the other): `remove_stub.py` on the extra finger, and the same
  `fingers` on both sides.
- An `overhead` gate failed BY DESIGN (skull as tall as the arm is long; a cloaked mini that never raises
  its arm beside the hood) cannot be fixed in the model: declare it in `state.json` and author the clips within it.

## 4c'. Machine of rigid pieces (FERRUGEM: `characters/ferrugem/rig/landmarks.json`, key `_doc_caps`)

- Rigid piece = `regions[]` with `"island": true, "closed": true` + one bone: 100% rigid, with the cut caps closed
  (`split_props.py`). Continuous skin on a machine tore 166 edges / 61 mm in the pose test; closed islands on the thigh
  columns and the foot pedestals solved it. Bending happens only at the couplings (ankle neck, elbow).
- Shoulder drum on the CLAVICLE bone (`DEF-shoulder.X`) with its center at the shoulder: the arm rotates inside it.
- `bisect: [["x", 0.592]]` cuts at the end of the chamfer MEASURED on the high-poly (a cut 1 cm off left shards of the
  edge) → a flat ring. The cap takes the texel from `cap_from` (a rust spot, not gray) with a minimal planar UV and
  custom split normals (area-weighted fan): without them the cap facets like a pinwheel. The normals survive
  `rebuild_rig.sh`.
- Short coupling elbow: shorten the humerus's rigid pin until the bend zone is ~7.5 cm (43 → 33.6 mm, only in the
  extreme pose) and limit the elbow to ~60° in the clips.

## 4d. Prop that wobbles when it is hit (TOCO, training dummy)

Not Rigify: `blender/wobble_rig.py` with `landmarks.wobble` — `bones` (the first is the fixed foot; each next one hangs
from the previous one, head = pivot), `blends` (height band where one bone hands the mesh over to the next, smoothstep),
`spring`. Find the pivots by height SLICES (width per 2.5 cm band): where the post leaves the foot, where the head rests.
The physics lives in `blender/wobble.py` (bakes hits into keys) and in `CFWobble.cs` (the same equations). Soft springs
read better: 8.5° does not read at 64 px; 13–14° on the spell does.

A target that DIES topples as a rigid body over the edge of its foot — and that is MEASURED on the mesh, not keyed:
`bl.py run blender/topple_fit.py --arg name=<NAME> --arg write=true` writes `landmarks.wobble.topple` (center of mass
and, per direction, edge `r`, gyration² `k2`, rest angle `rest`); `export_prop.py` carries it to the manifest, and
`wobble.py` (`life`) and `CFWobble` use the same table. TOCO: center of mass at 0.51 m, edge 0.22–0.27 m (cross-shaped
foot), rest 75.9–91.5° (backward 89.1°). Rest angle = the SMALLEST atan2(w, u) over all vertices, with any u: counting
only the points beyond the edge left the backward fall stuck at 90° with the bag floating (the foot holds the post
22 cm above the ground). Back up `landmarks.json` before the `write`. Show and death rules: skill `character-show`.

## 4c. Machine of cut pieces (FERRUGEM): joints, caps and what stays hidden

- **Ball at the joint** (`joint_ball.py`, `landmarks.balls`): a limb that rotates with its pivot INSIDE the casing
  (shoulder in the drum, ankle in the pedestal) shows the cut cap coming out. A sphere centered on the pivot, on the body
  mesh, rigid on the casing island. Color decides: `balls[].uv` with a smooth dark-iron texel (±8–16 px) — the
  neighboring texel turned into a "skin ball".
- **Caps with an explicit texel** (`cap_texel.py`, `regions[].cap_uv`): the texel closest to the cut tends to be rust
  = noise spread over a 20–40 cm disc.
- **Socket liner** (`socket_liner.py`, `landmarks.liners`): the body surface that an island HIDES at rest
  (rays: blocked with the island, open without it) — the generator never saw it and textured it as noise. Paints it
  (UV only) with the iron. UV stored in `cf_uv_orig3` (FLOAT_VECTOR; a corner FLOAT2 becomes a 2nd UV map).
- Before blaming the mesh for "speckling" in a gap: solid view (is there a hole?) and a flat test color on the suspect
  faces. On FERRUGEM the dots sat on the yellow = EEVEE shadow with 1 ray (`stage.py` now uses 4 × 16).
- **Face ring** (`joint_ball.py` with `"shape": "ring"`): a cut through a domed/riveted tip leaves a cap with a
  torn edge (r 0.08–0.17 on the drum). A brass ring on the face (r_in/r_out, `cone` of ~4 mm, lips turned inward) and a
  dark socket ring around the arm. Texel chosen IN THE TEXTURE (PIL: value, saturation, deviation from the
  neighborhood): the nearest vertex gave a light brass that read as a sticker.
- **A piece that rotates inside sweeps a sphere** (`part_tuck.py`, `landmarks.tuck`): the arm flap 13–16 cm from the
  pivot with r 0.15–0.18 swept the drum's own radius and poked out through the rim. Pull the ring inside `r_max` around
  the axis. A script that moves rest-pose vertices has to be idempotent by MARK (only what it moved keeps the original):
  the 1st version restored all of them from a copy and threw the `joint_ball` balls (recreated on every rebuild) to the
  origin.
- `rebuild_rig.sh` runs `joint_ball` → `cap_texel` → `socket_liner` → `part_tuck` when the landmarks ask for it;
  `lod.py` afterwards.

## 4e. QUADRUPED (UIVO, wolf): Rigify's wolf metarig, slimmed down

- `blender/quad_rig.py --arg name=<NAME> --arg landmarks=<json>`: the wolf metarig cut down for mobile (35 deform bones:
  spine 5 + neck 2 + head + tail 4 + scapulae + 4 legs of 4 bones + jaw + ears 2+2). Joints in
  `landmarks.json` (script header: `hips…chest`, `neck/neck_mid/head/head_tip`, `tail_1…tail_tip`,
  `scapula/shoulder/elbow/wrist/fpaw/ftoe`, `hip/stifle/hock/rpaw/rtoe`, `jaw/chin`, `ear/ear_mid/ear_tip`); writes
  `rig["cf_quad"] = True` (limb_paint, the export and the clips read it) and `IK_Stretch = 0` (a paw out of reach
  stretched the leg).
- Metarig names are NOT biped names: `spine` is the TIP of the tail, the body is spine.004 (croup) → spine.008, the head
  spine.011.
- Weights: `rig_bind.py` + regions (`mane` per chain, `lower_jaw` box, `keep_only` muzzle/skull, `limit` cheeks,
  throat, `chest_ruff` with jaw 0, `brisket`): heat weighting gave the mane to the shoulders and the jaw took the chest.
- Tripo mesh (Remesh → Smart UV → Texture): **weld the UV seams before the bind** (`remove_doubles` 1e-5; 41,752 →
  29,966 vertices) — glTF duplicates the vertex at every seam and heat weights each side on its own (the skin tears
  along the UV layout). Check the fit against the hi mesh (BVH: median 0.03 cm) and swap the mesh while keeping the rig;
  the old mesh stays hidden.
- `blender/quad_pose_test.py --arg name=<NAME>`: poses A tucked, B extended, C bite, D howl, E turn → edge stretch
  p99 / max, vertices > 2.2×, lowest point (UIVO: p99 1.5–2.1).

## 5. Look and measure — only then say it is clean

1. `pose_test.py` (independent of the bind pose) and its shoulder close-ups. The eye sees LENGTH: read
   `edges_over_2.2x_and_15mm` and `max_gain_mm`, not just the ratio (a 3 mm edge that triples does not show).
   `--arg only=A` leaves a single pose on screen for `stretch_why.py` and the close-ups. `rebuild_rig.sh` prints
   one line per pose; the rest is in `review/build/05_pose_test.json`.
2. Per-limb paint: `blender/limb_paint.py --arg mode=on` — a limb without the right color = wrong weight; a limb that
   disappears = wrong pose. Turn it off (`mode=off`) before exporting.
3. Close-ups: `blender/closeup.py` (target bones, radius, views, `hide` to hide props) + `cf/sheet.py`. A view with
   negative elevation or a small radius can land inside the body: discard the cell, do not interpret it.
4. Deformation = (weight step) × (how far the bone moves relative to its neighbors). Loop:
   `stretch_probe.py` (where) → `stretch_why.py` (which bone, which island, how many mm) → rule in `landmarks.json`
   (`limit` with `ramp`, `smooth_zones`, `sharpen`) → `./rebuild_rig.sh` → again. Look for SMALL steps on bones that
   move a lot.
   **Before touching weights, prove it is the weights**: take the seam vertices and measure their displacement in the
   space of the dominant bone between two frames. A vertex 100% on a bone that moves relative to it is NOT weights — it
   is B-bones (or a shape key/modifier). FERRUGEM lost a round this way: Rigify generates DEF bones with B-bones (spine
   8 segments, limbs 10), the torso skin curved 19.9 mm against the drum's rigid island and the seam tore in a sawtooth.
   The engine has no B-bones: `rig_build.py` now forces 1 segment on every deforming bone (what Blender shows = what
   Unity shows). Changed the rig? Rebuild and probe the five clips (on FERRUGEM the head started going 25 mm into the
   collar in the attack, which the curved spine had been hiding).
5. After the clips: `contact_probe.py` (mesh against mesh, every frame) is the judge of penetration; see `character-clips`.

The user judges by the viewport. "There are still deformations" means: find it with a close-up, fix the cause in the
weights or in the model, show the before/after — do not lift a gate or hide it with the camera.

## 6. Closing the stage

`lod.py` (LOD1 measured against the deformed hero; redo it after any change to the mesh), save the `.blend`,
`state.json` with the gate numbers, and whatever is a model limit written down as a limit.
