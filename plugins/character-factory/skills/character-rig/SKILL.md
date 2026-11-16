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

- **Eyes on a single textured mesh** (CENTELHA): Tripo gives no eyeball and no eyelid. One LEAF bone per eye (parent
  `spine.006`), pivot 4.7 cm behind the surface, region = the eye's box with `feather` 0.007; blink = vertical scale of
  the bone (0.08 closed, 1.1–1.25 wide open; the feathered skin stretches like an eyelid), look = 8–14° around the pivot
  (above ~15° the whole eye moves). A box top above the brow line drags the eyebrow along. 2 bones. Clip: skill
  `character-clips` §6b ("Eyes").

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

## 4g. A model from the Agentic Canvas, a floor-length skirt, a hanging prop and TWO Blenders (the healer, 2026-11-16)

First character rigged from a GLB made in Tripo's Agentic Canvas (HD model → Retopology with bake, 17,180 tris, ONE
island). Clean in its own poses on the second assembly.

- **Two Blenders, one per character.** The user may have another character open in the live Blender (port 9876) and
  `stage.py` WIPES the scene. Do not swap their scene: open a second Blender with a script that sets
  `scene.blendermcp_port = 9877` and calls `bpy.ops.blendermcp.start_server()` (inside a `bpy.app.timers` callback that
  retries until the addon exists; the addon's auto-start is skipped when 9876 is already taken) and run EVERY factory
  command with `export BLENDER_PORT=9877` (`bl.py` and `rebuild_rig.sh` read the variable). A guard before any
  `stage.py`: `bl.py code "import bpy; assert '<other character>' not in bpy.data.filepath"`. Never use the Blender MCP
  tools meanwhile: they talk to the live instance. At the end, `save_as_mainfile` to `characters/<id>/<id>.blend`.
- **`gameready.py --arg bake=false --arg tris=20000`** on a Canvas model: it arrives retopologised, with UVs and the
  texture on its own UV. `--arg tris` is only a ceiling (17,208 → 17,180, 1 piece of debris removed).
- **The Canvas "T pose" template gives PALMS DOWN** (thumb forward and down). The rig reads the palm from the thumb: only
  the thumb landmarks change. Thumb = PCA of the lobe that hangs (hand vertices below the palm and in front of it):
  base at ⅓ of the axis, middle at the centroid, tip at the far end.
- **Floor-length skirt with no legs inside** (the skin ends at z 0.16; only the feet exist): the legs are HIDDEN chains
  (thigh from the belt to an invented knee, shin to the real ankle). `limit thigh_under_belt` with a long ramp
  (`[0.34, 0.50]`), the sole's `keep_only` restricted to the foot's own FOOTPRINT (the hem points around it stay
  skirt), a short `prune` for `foot` / `toe` (0.15 / 0.12) and NO `prune` for `shin` (the shin must hold a hem 30 cm
  from its axis). The `tabard_f` / `tabard_b` chains take the front and back panels with a wide `fade_x`
  (`[0.04, 0.17]`, `soft_passes 6`). A step 14 cm forward and 7 cm up: 0 stretched edges.
- **A colour class that includes "dark" catches creases.** The collar of black beads was pinned to the chest by colour
  (`v < 0.24` or ivory); the dark CREASE under the chin passed the same test and was pinned to the chest right against
  jaw vertices: 22 edges 23 → 73 mm with the head turned (`stretch_why.py`: pair `DEF-jaw | DEF-spine.003`). Fix: the
  colour region's box ends BEFORE the crease (centre up to z 0.745; the big side beads in boxes of their own) and the
  jaw becomes two boxes (front of the chin all the way down; the sides only from z 0.775 up), so the crease keeps the
  automatic weights + `neck_not_chest`. Pose B: 44 → 7 edges.
- **The head must not hold the trapezius**: the head's lower box starts above the top of the shoulders (0.825 with
  shoulders at 0.80) with a short `feather` (0.012). At 0.81 / 0.025 the head held 0.21–0.27 of the trapezius tops.
- **A staff with a hook: `long_axis`.** A "?" hook pulls the SVD axis off the shaft and the staff's foot reads 17–21 cm
  of radius. `prop_blade.py --arg profile=staff --arg 'long_axis=[0,0,1]'` (and the key `weapon.long_axis` in the
  landmarks). A generated shaft 10 cm thick → `thin [0.62, 0.66, 0.74]` (radius at the fist 57.7 → 33.6 mm; whatever is
  below 0.66 of the length thins with it, the knob at the foot included).
- **A HANGING prop with a pivot of its own** (a censer under the hook): an entry in `props` on the bone that carries it
  (`DEF-weapon`) + `"own_bone": "DEF-censer"` + **`"own_bone_rest": {"head": [hook], "tail": [below]}`**.
  `prop_own_bone.py` takes optional `head` / `tail`: the own bone is born a child of the carrier but with its head at
  the point the prop swings about. The prop is skinned 100 % to that bone, so moving the bone's REST moves nothing on
  screen; with no keys it follows the staff. Test: 28° on the bone and the top link stays on the hook. List the bone in
  `prop_bones`. Measure the hook on the mesh AFTER the first `rebuild_rig.sh` (that is when the staff gets its rest
  place) and only then write the box.
- **A gate that fails on purpose is declared**: `overhead` 0.724 (arm 0.40 m, head ⅓ of the height). It goes in the
  landmarks' `_doc`, poses A and D of the test are read as "outside the design", and the character gets ITS poses in
  `pose_test.poses` (staff planted + healing hand, bow, step) with `follow: 1.0`.
- **Budget closed at 48**: base 29 + mitten 8 + topknot 2 + jaw 1 + flaps 4 + eyes 2 + staff 1 + censer 1. The ears
  stayed rigid on the head: no room for them, and at 64 px they do not read.
- **Not verified on this character**: the fist on the handle (`grip` copied, no `fist_fit` — the blade route does not
  run it), the carry pose (`onehand` is a guess), springs, `contact_probe` / `skin_fold`, and the painted texture
  (skill `character-design` §3c) is not on the scene's materials yet.

## 4h. Separate garments dressed on the body: `garment.py` (the healer v2, 2026-11-16)

House rule: body in underwear + every garment its own object (`character-design` §3d). Stage 5e of `rebuild_rig.sh`
runs `blender/garment.py` for each item of `landmarks.garments[]`, AFTER the body's weights and the props. Idempotent:
the piece is rebuilt from the GLB on every rebuild.

- **Fit `fit.box`**: the piece's bounding box is STRETCHED per axis onto a box in rest-pose metres. Size it so the skin
  lies INSIDE the piece's wall (belt: a waist of rx 0.255 / ry 0.236 inside a stretched belt of inner radius 0.235).
  `clear` (3–4 mm) pushes out, along the skin's normal, every vertex that ended up inside it.
- **Fit `fit.ring`** (bead collar, a closed loop): the loop is re-laid on an ellipse (`rx`, `ry`) on the plane through
  `z_front` and `z_back`; with `drape` every stretch the plane would bury is LIFTED until a ball of the bead's radius
  rests on the skin (the sides climb onto the shoulders); `cross` scales the section, and each bead TURNS with the line
  (it is not sheared).
- **Skin**: `{"bone": ...}` = rigid (collar on the chest, bracer on the forearm); or `transfer` (weights copied from the
  body's skin, closest point) with:
  - `keep` — only bones with these prefixes survive (`DEF-spine`, `DEF-thigh`);
  - `fold` — shin / foot / toe fold into the thigh FIRST (a hem is closest to the ANKLE and would follow the foot);
  - `toward` — every vertex gives 0.45 to the pelvis: a skirt hangs from the belt, the legs push it, they do not carry it;
  - `bands` — the belt is rigid above `z_rigid`, with a ramp down to `z_soft`;
  - `chains` — the springs of the loose cloth: a sector about an azimuth (−90 = front), from nothing at z0 to the
    maximum at z1, and below `split` the weight passes to the next bone (two 2-bone chains, front and back = 4 bones);
  - `smooth` — smoothing passes over the piece's own edges.
- **The piece travels as a worn prop**: it enters `rig["cf_props"]` (a json STRING) and `rig["cf_garments"]`; the
  export takes each one as a skinned mesh with its own LOD1. The LOD1 budget is shared between the pieces — the first
  try gave 15,974 of 10,000; with `{"body": 4600, "skirt": 1500, "collar": 900, "bracer_l": 340, "bracer_r": 340,
  "staff": 1400, "censer": 920}` it closed at 9,994 (shape ≤ 1.3 px at 160 px).
- **An underwear body simplifies the rig**: real legs (no hidden legs under a skirt, §4g) and `hands.split: false`
  (bare wrist — the bracer is an object, `split_plates` cuts nothing). 48 deform bones.
- **Hem above the insteps** (z 0.14, was 0.06): floor and feet clean in every clip; chain joints, ramps and bands
  rescaled with the box.
- **Stiff petals = a spring without gravity**: `secondary.chains` `tabard_f.01 [90, 8, 0, 12, 1]`, `.02 [70, 6.5, 0,
  16, 1]` (with the default gravity they hung 29° / 22° at rest). The floor rule of `secondary.py` keeps the tip at
  `floor_clearance + 0.07`: a hem that is too low becomes 15.8° of swing while standing still.
- **Part names in the contact probe follow the bone group across ALL meshes**: "thigh.R × staff" may be the SKIRT's hip
  (weighted to the thigh), not leg skin. Read the mesh before touching the pose.
- **To render a pose**: hide the effects (`hide_viewport` on the `<NAME>_bless/coal/ember/...` meshes — the aura's
  dome covers the sheet) and show them again before clips and export. `pose_test.py` does not run alone after
  `restpose` (arms in FK): run `rebuild_rig.sh`.
- Open on v2: pose test with E 8/5, F 12/10, G 11/9 edges over 2.2× / > 15 mm (the close-ups show no tear; cause not
  isolated).

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
