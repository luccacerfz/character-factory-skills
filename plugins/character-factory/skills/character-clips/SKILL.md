---
name: character-clips
description: Author the clips of a Character Factory character — base pose, attack, idle, walk, taking a hit and death, plus the special clips (ranged spell with a projectile, summon, a unit that rises out of the ground / spawn, planted staff) — with a two-handed weapon, a one-handed weapon + shield or NO weapon (claws, fists — the unarmed freehands route), follow-through springs, effects (aura, bolt, orb), measured mesh×mesh and floor contact, and the 12 Disney principles checked at game size (64 px). Use when the user asks for an animation ("make the idle", "attack", "walk", "hit", "death", "spell", "summon", "all the animations"), complains about one ("the arm disappears", "it has no weight", "the foot slides", "the weapon goes through"), or after changing the rig. Includes the Seedance video reference of the character itself with colored limbs. Characters ACTING TOGETHER (summoner + summoned units, training target, round) belong to the character-show skill. Includes the game principles in the clip: poses that read at 64 px, a short strike with clear contact and hit-stop, walk variations for packs, and the victory/close-up clip.
---

# Clips

Everything authored in a clip lives in `characters/<id>/anim/<clip>.clip.json`; `./clip.sh <id> <NAME> <clip>` builds it
(~7–20 s) and writes each stage's report to `anim/<clip>.build.log`. The full key contract is in
`factory/README.md` (sections "Clipes" and "Além do ataque"); BRASA's and GRANIZO's recipes are the examples. Operating
rules: skill `character-factory`.

Stage order (do not change it): retarget (if there is a take) → polish → floor | bodyfloor (+plant, +limbfloor) → weapon OR
onehand → freehands (if the prop was released, two hands) → hubpin → secondary → keepclear → **stance** → fx.

## 0. New character: start by PORTING the recipes of an approved one

```
python3 cf/port_clip.py <src_id> <SRC> <dst_id> <DST> [clip ...] [--force]   # angles copied; meters scaled
bl.py run blender/limb_radii.py --arg name=<DST> --arg landmarks=<json>      # REAL arm radii -> landmarks "limbs"
./build.sh <id> <NAME> attack            # clip.sh + short report + seam/base  (then idle walk hit death)
./look.sh <id> <NAME> <clip> a '[[62,8],[0,6],[90,6]]' 3 2.1 '[0.1,-0.3,0.95]'   # contact sheets from fixed cameras
./contacts.sh <id> <NAME> <clip>...      # contact_probe on each clip, one line per pair
```

The port scales each number by what it is: angles stay equal; chest-space meters × the arm ratio; floor meters
× the leg ratio; solver radii = the ones MEASURED on the new body. On GRANIZO all five clips built on the first
try; what the port does NOT know and had to be fixed by hand:
- **shoulder width**: scaling by the arm ratio leaves the pommel hand inside the shoulder on a wider body
  (shoulders ×1.6, arms ×1.44) → +0.07 m on "esq" (left) in the low-carry keys, +0.04 at impact;
- **radii**: the recipe carried a 0.11 m forearm; the bracer measures 0.164 → the solver saw a pommel 35 mm inside as free;
- **where the twist shows**: with a rigid bracer on the non-twist bone, the forearm twist twists nothing and what
  shows is the wrist DEVIATION (handle lying on the bracer) → `forearm_twist_free_deg 110`, `wrist_ulnar_max_deg 45`,
  `twist_side` only on the arm that needs it; `weapon.grip` with the pommel hand at the END of the handle (≤ 2–3 cm spare);
- **video reference**: it is of the character itself — the port deletes `reference`; film a new one (section 7);
- **weight class**: the port copies the TIMINGS. A 390 kg ogre with a dwarf's timings got 7.46 from the critics
  ("a dwarf's timing on an ogre's mass"). Before the first review, re-time for the mass: a walk with a longer period
  (24 → 30 frames = 120 steps/min; keys at f' = 1 + (f−1)·k), smaller `bob` and weapon sway (hips
  ≤ 4.5 cm, weapon head ≤ 15 cm), dips over 8–10 frames, the hit's recoil and the death's leg kick halved;
- **leg reach**: torso meters × the leg ratio can ask for a crouch the short leg does not have
  (−14.4 cm on 43 cm legs): `polish.py` gives the hips back (`leg_reach.hips_raised_max_cm`) and the body hits
  that limit like a wall. Read `hips` in `motion_table.py` and key up to the limit, not beyond it.

`weapon.debug_arm: ["L", 17]` prints in the log the cost of each elbow swivel of that arm on that frame (deviation,
twist, flexion, handle clearance): read it before touching the solver weights.

## 1. The base pose decides the five clips

- Base pose = frame 1 of the attack (two-handed weapon carry). Idle, walk, hit and death use
  `recipe.pose_from: "<NAME>_attack"`; without a mocap take, `source: "hold"` + `layers` / `gait`.
- Before animating, choose the base pose by looking at three numbers from `weapon.py`: forearm twist (target < 90° from
  bind), wrist bend (< 60°) and the `contact_probe` of frame 1. A defect here is inherited by every clip.
- A base-pose parameter (`weapon.grip`, `grip.*`, `phi_ready` / `psi_ready`) is not changed because of one frame:
  if it changed, rebuild all five (attack first) and probe all five.
- Every clip is authored **square** and rotated in the last stage (`stance_yaw_deg`: attack / idle / hit / death +30°,
  walk 0°). The solvers are not rotation-invariant.

## 2. Arms on a handle

`weapon.py` solves each arm with two free variables (elbow swivel × wrist roll on the handle).
- `weapon.keys` = prop angles `[quadro, phi, psi, sep, ease]` (quadro = frame); `weapon.hands` = grip center in chest
  space `[quadro, esq, frente, cima, peso]` (frame, left, forward, up, weight; weight 2 = locked key).
- If `twist_jumps` / `seam_crossings` do not come back empty or the wrist goes past ~60°, the error is in the prop's or the
  hands' trajectory, not in the solver: `./wtable.sh <id> <NAME> <clip> [f0 f1]` (per-frame table; it RE-RUNS weapon.py →
  rebuild with `clip.sh` afterwards) and `cf/armlab.py` to test a new rule offline.
- Where the grip fits: `blender/reach_map.py` (one wrist, with the REAL forearm radius) and `blender/grip_fit.py` (the grip
  center at which both arms stay outside the body → ready-made keys). Pommel hand in front of its own shoulder, never on the
  body's axis; with the hands high the elbows go forward/up and the head is a forbidden zone.
- Prop with inertia (`drag`): the real handle lags 25–40° behind the keyed angle → key the hands against the real angle.
- `twist_side` fixes the twist branch; measure the other branch too before choosing. A critic's hypothesis is tested and
  measured: freeing the branch of GRANIZO's right arm ("the twist parks at 155°") gave 178°, wrist deviation ±90° and
  a seam crossing → reverted. On a rigid bracer that twist does not even show; the wrist deviation does.
- `handle_weight` / `handle_cost_cap` (default 4 / 8): raising them to 20 / 45 in the attack took handle × right forearm
  from 23 mm to 12.5 mm with no jumps; check `twist_jumps`, the wrist bend and the `contact_probe` afterwards.
- The forearm must not lie along the handle: pommel rule (lower hand) + handle rule (both hands, `handle_weight`),
  both with a cost that saturates. They choose the elbow; what really solves it is the grip position and the design of the
  bracer (skill `character-design`). Known remainder on GRANIZO: pommel × bracer 34 mm in 7 frames of the attack.

## 2b. ONE-handed weapon, held shield, effect (ALVOR is the example: `characters/alvor/anim/*.clip.json`)

When `rig/landmarks.json` has `onehand`, `clip.sh` runs `onehand.py` instead of `weapon.py`. Read its header.
- You key what reads at 64 px: `weapon.wrist` `[quadro, esq, frente, cima]` (wrist in CHEST space) and `weapon.aim`
  `[quadro, phi, psi]` (where the blade points). The solver owns the elbow, the wrist roll and the limits.
  `"ready"` = the character's carry pose (`landmarks.onehand`).
- **The key is not the contact.** `drag` is a spring along the blade direction (0.35 ≈ 1.3 frames of lag). Measure the
  blade (heading/elevation of the weapon bone) on the `hit` event frame and move the keys earlier — on ALVOR it pointed −81°
  away from the target on the event frame before the fix.
- **Shield**: held by the strap in the hand (`props[].seat`), aimed by `off.face` `[quadro, rumo, elevação, giro]`
  (frame, heading, elevation, roll) — the shield's FACE; the hand takes the orientation that this asks for. In guard it
  sits in FRONT of the body (wrist on the center line), never beside the shoulder; the shield arm is forward in the
  wind-up and opens as a counterweight in the cut.
- **Shield at rest (death, fall)**: the wrist axis sits ~40° from the shield's normal (the strap is slanted). A
  shield lying face up NEXT TO a lying forearm forces the wrist to point at the sky — wrist at 114°
  for 23 frames on ALVOR. Lay the shield ON the body (chest), last, and turn it in its own plane (`roll`) until the
  wrist rests (32°). Read the shield hand's `wrist_bend` on the last frame, not only in the strike.
- **An aim the wrist cannot give is not reached — and nobody warns you.** The limits (`wrist_flex_max` 60, `wrist_dev_max`
  38) clip the aim silently: a follow-through with psi +33 stopped 12 cm short. Check the build's `aim_off_deg` and
  the tip position; end the strike on an aim the arm can reach.
- **Spacing is measured at the TIP**: tip speed frame by frame (`motion_table` → `speed.sword_head`). ALVOR's cut
  had 8.9 → 7.7 → 16.7 m/s (a jerk and a jump) that no camera sheet showed; after redistributing
  the wrist/aim/torso keys it became 5.4 8.7 12.1 13.7 9.3 6.5 (accelerates up to the contact, decelerates after).
- **Released weapon** (`weapon.release`): `onehand.py` lays the prop down on the lower hull of its OWN mesh (it rests on
  the two lowest points around the center of mass — on the sword, guard + tip) and lifts an in-flight prop that would touch
  the floor. Read `prop_lies` in the build log. The sound event (`sword_ground`) goes on the frame of the first touch.
- **A released prop inherits TWO velocities**: the linear one (below) and the ANGULAR one — `release.ballistic.turn: 1.0`
  = it spins at a constant rate during the flight. Without it the rotation eases in toward the lying pose and the weapon
  "hovers upright next to the hand and then topples" (ALVOR round 3: 4.5 → 13.2°/frame; it became the most visible defect
  of the death). Check the angular step per frame, not only the position; steel arriving at ~4 m/s bounces (`bounce` ≈ 0.12).
- **A fall obeys g**: with support on the floor the center of mass does not accelerate downward faster than 1.09
  cm/frame² (30 fps), and does not descend at constant speed (that reads as crouching). Falling = the center of mass
  LEAVES the support (the margin crosses zero) before the hips drop. In a loop, layers with the same phase stop together
  on some frame: offset them (chest 6–8 frames after the torso) and check that hips, head and tip are never all three
  below 0.03 m/s.
- **Ballistic release** (`release.ballistic`): the prop leaves with the HAND's velocity and falls under gravity; where and
  when it lands is computed (`release_land_left_m / _fwd_m`, `release_flight_frames` in the log). To change the landing,
  change the gesture: `Δpouso = Δv × quadros de voo` (landing shift = velocity change × flight frames; 1 cm/frame
  ≈ 19 cm) — move the wrist key of the frame before the last held one, converting from world to chest space with that
  frame's chest axes. Side guard = the weapon arm is the REAR one: in the recoil it travels backward and the weapon lands
  behind the head unless someone keys the opposite. Keys up to 3 frames AFTER the release also change the flight:
  measure again.
- **The weapon leaves through the palm**: probe the handle position in the hand bone's space for the 5 frames after the
  release; if it moves against the palm (or the tumble carries the pommel into the forearm), `contacts.sh` flags weapon ×
  forearm/hand. Fix: the hand backs off along the palm normal and the landing `yaw` reverses the tumble (the pommel leaves
  toward where the palm faces).
- **A held prop that is released** (`off.release`, requires `own_bone` in the rig): `{frame, blend, wrist, hand, curl}`.
  From then on `off.wrist` / `off.face` are the PROP's path; the hand follows `release.wrist` and lies down with
  `hand: [0, 0]` (`hand` is [twist, flexion] — a high twist leaves the hand on edge: a high `free_hand_wrist_lift_cm` at
  rest).
  **Prop resting on the body**: do not adjust it by eye. `blender/settle_dump.py` (body + prop as triangles on the final
  frame) → `cf/settle_solve.py <npz> '<off.face final>' '<off.wrist final>'` returns the lowest-center-of-mass pose in
  contact (supports, center-of-mass margin) already as keys; apply the same difference to the landing/bounce keys and
  check with `contacts.sh` (touch ≤ 6 mm, no penetration).
- **Releasing the plant in a fall**: if the authored rest foot is far from the planted foot (the body ROLLS after the
  impact and takes the hips with it), going back to the curves with the toe on the floor DRAGS the foot (FERRUGEM: 99
  mm/frame, 20 cm in 3 frames, which no sheet showed — only the `motion_table`'s `feet.slip_mm`). `plant[].release_lift`
  (≈ 0.06 m) carries the foot through the air. Read the death's `slip_max_mm_per_frame` after any change to the impact.
- **Lying body**: `weapon.shoulder_floor` (pauldron radius) stops the clavicle from following the hand into the
  floor; a negative `floor_clearance` when the torso floats because the point that "carries" it is a cloth seam
  (check the weight of the lowest back vertex first); `airborne` in `contacts.sh` must come out empty.
  `off.release.rest: <quadro>` (a frame) lays the free hand on its broad face (without it the hand stays on edge and the
  wrist waits in the air: ALVOR, arm 7 cm above the floor at rest). After any change to the rest pose, read the last
  frame's `death_ground.json` part by part (hands, arms, thighs, head) and the per-LOD `floor` in the Unity report — LOD1
  sinks more than LOD0.
- **A lying body that floats after the springs** (CENTELHA death r4): measured stage by stage, polish / bodyfloor /
  limbfloor / onehand / hubpin left the thigh 0 mm from the floor and `secondary.py` lifted it to 41–51 mm. The seat
  vertices share weight with the back tabard; with `floor_over_limit` the cloth is held above the floor and the seat
  rises with it. A `floor_clearance` of 0.05–0.065 on the springs made it worse (it holds the tips 5–6.5 cm up). The
  tool: `"floor_resettle": true` in the clip (`clip.sh`) settles the torso again AFTER the springs, with the arms and the
  cloth carried along, and `bodyfloor.py keep/keep_from` keeps an already released prop in place in the world (without
  it the staff went 39 mm into the floor along with the root).
- **If `leg_reach` in the `floor.py` log is not zero, the final pose is not yours**: key the torso and the heel until
  `hips_drop_max_cm` and `foot_pull_in_max_cm` give 0 and `leg_extension_max` < 0.975 (ALVOR attack: 1.077 → 0.929).
- **Side guard** (torso turned 40–55°): `stance_yaw_deg` 0 (the turn IS the base pose; with +30 the chest came back
  square). A frontal hit on a side-on unit = recoil in the WORLD: pitch·cos θ + roll·sin θ. Lying body: `yaw` is
  around the world's vertical axis → it becomes a head tilt toward one shoulder; the guard's turn becomes a roll of the
  body on the floor (remove it during the fall).
- **Mixamo as a reference that is read** (the user's decision for sword+shield): download the FBX through the web
  interface (never upload the user's character, never use the page's token), store it in `mocap/mixamo/` (untrusted data:
  scripts in another folder, Python with `-I`), `blender/mixamo_take.py` → json, `cf/mixamo_read.py <take> <landmarks>`
  (table) and `--map '[[origem, destino], ...]'` (source, target; keys as deltas from the guard). Read the guard on frame
  1 of the take.
- **Effect** (`landmarks.fx`, `blender/fx.py`): per clip, `"fx": {"aura": {"level": [[quadro, 0..3, ease?], ...]}}` —
  1 normal, 0 off. It is secondary action that tells the state: it contracts in the wind-up, flashes on the strike frame,
  flickers on the hit, goes OUT before the body lands. Every clip closes on itself (the stage handles it) so it chains in
  the engine.
- **Explosion into pieces** (`fx.gibs` + `fx.shock` in the landmarks; a `gibs` block in `death.clip.json`): a piece is a
  SHELL with a hot rim, not a solid plate. Parameters that cleaned up FERRUGEM: `inner_frac` 0.9 (deletes the inner core
  that pokes through the cap), `tear_area` / `tear_flat` (tears open the concave cap that decimate folds into a black fan),
  `cap_max_r` (a big cap becomes a shell), `fan_planar` / `fan_wide_r`. The `shock` flash (`ring_start` 0.4, `ring_height`
  0.24, `blast_flash`) must COVER the frame of the body → pieces swap. The probes stop at `cf_body_gone − 1`. Before
  exporting: `blender/lit_gain.py` (skill `character-engine`) so the smoke reads the same in the engine.
- **Dust / steam / spark** (FERRUGEM r5): `kind: "puff"` (`mode` ground = dust thrown along the floor; rise = a jet of
  steam going up) and `shock` with `arcs: 0` (sparks + flash). Clip: `"bursts": [[quadro, ponto, força, modo?], ...]`
  (frame, point, strength, mode) on the CONTACT frame (stomp, claw on the target, strike received). Alpha is PER CARD
  (three crossed cards: 0.24–0.34; 0.6 gave white "diamonds"); a medium color (the stage light blows out 0.75). Every new
  effect in the landmarks requires `./fxkey.sh` on all five clips.
- **Authored AAA strike**: the claw path is a curve (waypoints), each step larger than the previous one until the contact;
  hit-stop = a stop key on ALL the body layers and on the claw's world window during the 2 contact frames;
  chain of force hips → boiler (+1 frame) → claw. Measure: corners (angle between steps) and steps per frame.
- `python3 cf/clipfmt.py <clip.json>` keeps the file readable (one track per line) after editing it by script.

## 2c. Planted prop, a unit that RISES OUT OF THE GROUND, summoner (examples: `characters/ocaso`, `characters/ossinho`)

- **An authored attack clip** (no actor take) is `"kind": "oneshot"` + `recipe.returns_hub: true`. `"kind": "attack"`
  is the mocap path: `polish.py` looks for `<NAME>_attack_mocap`, fails, and the following stages of `clip.sh` run
  on the action that was on the rig and CORRUPT it (OSSINHO's walk had to be rebuilt). A build that failed in
  polish = rebuild the clip that was on screen too.
- **Planted staff**: `weapon.wrist_frame` / `aim_frame: "root"` (keys in the unit's space, not the chest's) and
  `weapon.foot` (the prop's foot is in charge; `blender/prop_foot.py` measures it, the build reports `foot_off_mm`).
  Careful: with `aim_frame: "root"` the word `"ready"` is a different pose — on a unit carrying a prop, frame 1 came out
  59 mm away from the base pose.
- **A unit born from the ground = an elevator** (`"sink": [[quadro, metros, ease], ...]` (frame, meters, ease) →
  `blender/sink.py`, after stance). Every stage works with the floor at z = 0; so the clip is authored with the unit
  STANDING on its own floor and `sink` lowers the root. Hand on the edge of the hole = hand keyed HIGH in unit space
  (`weapon.off.wrist_frame: "root"`, height = −sink + 2 cm, one key per frame). Generate the `sink` and those keys
  TOGETHER, from a single physical curve: exit velocity and `g` (9.81 / 900 m per frame²) give the apex and the landing
  frame (OSSINHO: leaves at 1.94 m/s, 7 cm above the floor at the apex, lands 10 frames later; `sink` > 0 = in the air).
  `floor_probe.py` judges against ITS floor (`cf_sink` stays in the action). The clip does not start in the base pose
  (frame 1 = buried) and ends in it.
  - The order in which things come out is MEASURED: height of each tip (hand, top of the skull, blade tip) against −sink,
    frame by frame. A blade at 40° "floated" lying on the surface; at 52° it was still buried and at 80° two frames later:
    it pierces point first.
  - A body with no reach over the head (`overhead` 0.72): roll the torso 20° so the rising shoulder goes high and the
    skull gets out of the way — a 12 cm window in which only the hand shows.
- **Death of a light unit**: thrown, not toppled — a `root pitch` that only accelerates (6 → 14°/frame), `floor_hop` in
  flight, no `plant`. On the floor, remove EVERYTHING crooked the guard has: the turn becomes `roll` (section 7, ALVOR),
  the forward lean becomes a sit-up (shoulders 4 cm in the air), and a head tilted back holds the whole body up on the
  nape when the skull is thicker than the ribs (hips 3.4 cm above the floor): head in line with the spine and the root
  2–3° short of −90.
- **Summoner**: `landmarks.summon {unit, event, points [[esq, frente], ...]}` (points as [left, forward]); the summoner's
  column effects (`fx` with `anchor: [esq, frente]`) sit at those points. The unit's `spawn` must fit between the
  summoner's event and the end of the summon (OCASO `summon` 23 → `summon_end` 58; OSSINHO `ready` on frame 34 → 57).
  `blender/summon_show.py --arg host=<HOST>` rehearses the engine contract in the viewport (skill `character-show`: scene
  `CF_Show`, NLA strips, the unit buried until the event). **`--arg mode=off` before going back to the pipeline.**

## 2d. Ranged spell: a projectile gathered in the hand, lob, target (OCASO `spell`)

- A character's second ranged ability: change WHO does the work and the TRAJECTORY (attack = whipped staff, straight bolt
  in 4 frames; spell = planted staff, the bone hand gathers the orb and throws it underhand, a 19-frame ballistic arc).
- `landmarks.fx.<x>` kind bolt with `"bone": "DEF-hand.L"` and `"at"` under the palm (at rest the palms face down: the
  palm side is −Z); in the clip `{"charge": f, "fire": f}`: the orb is born in the hand and grows, trembling, until it is
  released. `"arc"` + `"ballistic": true` = a parabola timed by g; `"burst_frames"` / `"burst_scale"` the explosion. An
  aura with an `anchor` at the impact point (`hexmark`) makes the mark on the floor; key the flash on the `lands_frame`
  the build prints.
- **Release = the hand moves where the orb goes.** Measure the carrier (the effect's bone) in the 3 frames before the
  release: the hand must accelerate (1.7 → 3.1 → 4.2 m/s) and leave in the orb's direction and at its speed (4.6 m/s,
  6°). With the torso turn the hand sweeps INWARD: release in front of the throwing arm's shoulder, not across the body
  (35° of difference in v1).
- Cloak/hood body: after the release, little torso turn and lean and no residual turn on the head — the hood
  sank 50 mm into the collar; turning `head_limits` on made it worse (67 mm: they counter-turn the head backward).
- Every clip of the character must key the new effect as off: re-key only the effects (assign + `fx.py --arg fx=<bloco>`)
  instead of rebuilding the bodies.

## 2e. What a show / round asks of the clips

Scenes with several characters (summon, arena, a round with patrol, health and raising) belong to the `character-show`
skill — it COMPOSES the clips from here and animates nothing new. What it needs each clip to already bring:
- **Walk** with `walk->idle best_frame` in the export manifest (the show starts the patrol at the phase that ends on that
  frame) and a measured `ground_speed_m_s` (it is the speed at which the root moves in the show and in Unity).
- **One-shots that return to the base pose** (attack, spell, summon): the show crossfades 5 frames into the next clip; a
  one-shot that ends far from the base pops even when crossfaded.
- **Baked projectile** (`fx.py` writes `cf_fx_<fx>` into the action): the show and the engine take from it the frame on
  which the target is hit. Re-keyed the effect? Rebuild the action, otherwise the target is hit on the old frame.
- **A `spawn` that fits inside the summon** (event → `summon_end`) and starts buried (`sink`): the same clip serves to
  raise a summoned unit from a body.

## 2f. A unit WITHOUT a weapon — the claws are the weapon (FERRUGEM: `characters/ferrugem/anim/*.clip.json`)

`rig/landmarks.json` without `weapon` / `onehand` → `clip.sh` runs `freehands.py release=1 blend=0`: it owns both
arms from frame 1 to the end. Everything lives in the clip's `free_hands` block (header of `freehands.py`):
- its own base pose: `hub.clip.json` (`source: "hold"`, `pose_from: <NAME>_rest`, 3 frames); every clip uses
  `pose_from: <NAME>_hub`. `hubcheck.sh` compares against the `pose_from` action.
- `hands` = wrist in CHEST space `[quadro, esq, frente, cima, ease]`; `pole` = preferred elbow; `claws` =
  `[quadro, graus .01, graus .02, ease]` (frame, degrees for .01, degrees for .02, ease; curling brings the tips
  forward; the thumb follows).
- `swivel_samples: 180, swivel_hold: 2` on ALL the character's clips (the base pose too): with the default 36 / 6 the
  elbow stays stuck 20° out after a big arc (156 mm at the end of the rake).
- `hand_length` = hand + claw MEASURED (arm slices; 0.45 on FERRUGEM, default 0.15) and `tip_floor` on every clip that
  comes close to the floor — with the default the claws went 21 mm into the floor in the death.
- **Wrist keys stop at every key** (ease per segment, no spline): for a pendulum / cycle generate ONE linear key per
  frame from a function (lagged cosine: gorilla arm 3 frames behind the legs, arc +cos²); for a strike generate it by
  slerp of DIRECTIONS on the arm's sphere with the reach handled separately (short forearm: reach = elbow; d 0.375 ≈
  60°). Example generators in the `_doc` / `free_hands._` of FERRUGEM's clips.
- Before keying, MEASURE how far the torso projects in front of the shoulder line against the arm length (boiler
  0.44 × arm 0.41: the wrist never gets in front of it; the strike is at the sides and the hand + claws turn inward).
- Idle with a pendulum + `hub_pin: ["all", 0]`: the pin subtracts the frame-1 value from EVERY frame. If the hands are
  not in the base pose on frame 1 (pendulum lag), they stay offset for the whole loop (29 mm). Put the seam in a
  settle: torso still at the center for 6–8 frames, arms arriving — frame 1 is the real base pose.
- Death of a body that is wide at the front (barrel): it falls onto the body, the head stays free; the arms keep their
  WORLD direction during the topple (they turn ~90° forward in chest space) and land afterwards; a round foot lands on
  its edge (pitch −40° after the topple: the sole+front corner down). `boots_low_last_mm` in the `limbfloor` log must
  come out ~0.
- **A cycle that owns the arms** (walk): `free_hands.cyclic: true`. The elbow remembers the previous frame; starting
  cold it ends the cycle on another swivel (FERRUGEM: identical keys, a 10.5 mm seam at the hand and 36 mm at the claws →
  0.0).
- **Unarmed strike: measure the WORLD speed** (`motion_table.py` → `speed.hand_l / head / hips`), not the generator's.
  The wrist in the world is body + arm: torso strike keys with `out` make the body jump at the start and BRAKE until the
  contact (head 29 cm in one frame). A body strike with `in` over 4 frames, hips 1 frame ahead of the arm: the wrist
  accelerates up to the contact (0.4 → 1.3 → 5.5 → 11.2 → 15.9 → 12.0 on the hit) and the head stays at ~6 m/s.
- **Gorilla arm in the walk** (what the video showed): besides the forward pendulum, both arms OPEN to the
  sides in each swing phase (3 frames after the foot) and the body rolls over the planted foot (9°, 7 cm). 34° read as
  "flapping wings" (critics, round 1): ~21° with a PAUSE at the top (rise 40 %, hold 15 %, fall 45 %, slower than g),
  wrist ≤ 75 cm. An arm thrown BACK passes through the thigh: minimum abduction 0.5 × the backward swing (thumb 11 mm
  into the leg). More roll costs leg: lower the walk until `hips_drop_max_cm` is 0.
- **A machine foot DROPS**: `gait.land: "drop"` (polish.py) — after the top of the arc z = lift·(1 − s²), 0.5 → 2.5
  cm/frame down to the floor; the sine arrives FLAT (1.9–2.0) and reads as a placed foot. Stomp: torso −2.4 cm over 2
  frames (`out`), chest +3° one frame later, head +4° one more; `heel_strike` 0 on a pedestal.
- **A hanging arm lags behind the chest turn** (idle, yaw snaps): a damped follower of the yaw (ω 0.55, ζ 0.75) and the
  hand turned back by (follower − chest) in chest space. CHECK THE SIGN through the hand's speed: wrong, it leads
  (0.45 → 0.86 m/s); right, 0.38. Yaw + = to his left: (left, fwd) → (left + θ·fwd, fwd − θ·left).
- **Big belly and a lateral pendulum**: the hand that swings TOWARD the body hits it (33 mm inside). It keeps ~20 % of
  the swing and slides across the FRONT of the belly with the rest.
- **Claws pointing at the body** (hand beside the belly after the strike): `free_hands.twist` accepts KEYS
  `{"L": [[quadro, graus, ease?], ...]}` (frame, degrees, ease) — it turns the hand on the forearm (FERRUGEM: −45° took
  97 mm off the thumb; +45° made it worse; measure both signs and the floor, −45 on the right arm put the index finger
  17 mm into the floor → −25).
- **Death with the arms in the world**: interpolate the shoulder→wrist offset by DIRECTION (slerp) + LENGTH; the straight
  line cuts the chord and the elbow closes in the middle (hand 32 mm into its own arm). A rest pose with reach ≥ ~0.93 of
  the arm in the floor plane (0.337 m left the hand 75 mm inside the humerus). Claws of a lying hand: measure the sign of
  the curl against the floor (on this rig curling lifted the tips: −6 → 57 mm into the floor, +18 → clean).
- **Contact with the rigid parts the unit has**: `landmarks.contact.things` (palms, blades). With only the head, the
  five FERRUGEM clips passed as "clean" with claws 150 mm inside the body. Do not list a bone whose faces also
  follow other bones (the drum on `spine.003`: a false 10 cm). A blade with an open shell crosses its own hinge from
  frame 1: declare `contact.lap` with the reason after looking at the close-up.
- **Path generator: no hard `max()` / `min()` between curves.** The value stays continuous, but the derivative jumps where
  they cross: in FERRUGEM's walk (one step's flare × the backward-swing opening) this put 33 m/s² in one frame
  into the wrist keys, which no sheet showed. Use a smooth max `½(a+b+√((a−b)²+k²))` and a smooth ramp in place of
  `max(0, x)`, and measure the 2nd difference of the KEYS (before the build) and of the wrist in the world
  (`motion_table`) afterwards.
- **Elbow swivel degrees deceive**: `swivel_jumps` = the angle between two swivel vectors in the world; with the wrist
  moving 17 cm in one frame the shoulder→wrist axis turns and the "jump" grows without the elbow jumping. Read the chord
  in mm (3rd number) and `swivel_jump_chest_max_deg` (the swivel in CHEST space: the body carrying the arm does not
  count). FERRUGEM's hit: 13.8° in the world, 1.5–6.2° in the chest.
- **A hand number is in the WORLD.** FERRUGEM's r2 README said "the wrist drops 17 cm in the recoil" (chest space, with
  the body turning the other way); in the world it was 46.9 cm in one frame, faster than the strike — all three critics
  caught it. A claw that hit stays in place: write the wrist in the world after the contact (chest basis recorded from
  a build, `BASIS=`).
- **A height ceiling that FOLLOWS the shoulder**: a ceiling fixed in the world holds the wrist while the stomp lowers the
  shoulder and the hand opens outward (78.8 mm seam). `zcap + 0,8 × (z_ombro − z_ombro_topo)` (z_ombro = shoulder
  height, z_ombro_topo = its top): wrist ≤ 68.4 cm (was 75), seam 46.4.
- **A step on single support**: a negative margin on the hit's step back (−2.8 cm, 5 frames) is solved by rolling the
  torso ~6° TOWARD the planted foot during the step (+0.7..+1.2), not by lengthening the step.

## 2g. A GIANT prop in the free hand and what was measured on GRANIZO v3 (`characters/granizo/anim/*.clip.json`)

- **Signs, measured (do not assume them)**: roll + on chest / torso / head LOWERS the RIGHT shoulder (the v3 hub leaned
  toward the pickaxe side for a whole round with +6; −7 gave shL 0.987 / shR 1.088); loc `side` + is to HIS LEFT; yaw −
  of the torso takes the right shoulder back; pitch − of the head = up/back; in `onehand`, `aim` [elevation, heading] with
  heading + to the left.
- **Rigify's isolated head + a hunchback**: the head does not follow the chest. Every bend and every roll of the torso
  takes the head along (`head roll` keys mirroring the `chest roll` in the idle); backward, at most ~−10°.
- **Holding on a spline needs a duplicated key**: the tangent comes from the neighbors, so two equal keys (28, 60) still
  slide. Frozen pose = 28 `"in"`, 30, 60.
- **`still` does not lock in the world and `drag` continues after the last key**: with the torso moving, the `still`
  prop moves along with it; the pickaxe with `drag` 0.2 kept swinging in the victory. Dead stop = `drag` 0.
- **A hanging wrist amplifies**: `up` of the free wrist in chest space → wrist height with a gain of 1.3–1.8 (the arm
  bends in the swing). A per-frame correction with gain 1 overshot; 0.55 converged (walk_b dragging 0–1.6 cm).
- **Dragging in an in-place walk is free**: the prop stays still relative to the body and the floor slides underneath.
  Where the swinging foot crosses the wrist (61 mm), the 20 cm detour over the boot became a beat of the clip.
- **What a giant prop does NOT do** (measure before authoring): a pickaxe planted upright in the victory (the hand grips
  at 21–37 % of the handle: the pommel only reaches the floor while crouching); a chest beat with a 0.6 m fist (every
  path 13–46 mm inside the chest).
- **Floor effect `spikes`** (`fx.py`): `layout: line` = a crack up to the target + 7 crystals in sequence (the last one
  bursts on the `hit`); `layout: cluster` = crystals growing around him (iceberg death, victory crown). `lean` [22, 14]
  hid the tips INSIDE the curved body; [6, 8–14] makes the cage. A crown BEHIND him: `radius` < the center offset
  (0.58 < 0.78). Additive over a light floor blows out to white: color [0.16, 0.55, 1.0] / core [0.62, 0.9, 1.0] /
  strength 1.15.
- **Ice veins** = `shock` with `links` in order (wrist → elbow → shoulder → crust) + `zones` restricting the clip to those
  links (nothing arcing to the floor).
- **Area spell that pins a pack from below** (CENTELHA's "Prison of Light", r5): all of it is `fx.py` (meshes on their
  own bones, keyed by the clip, they travel in the FBX), through three generic extensions with no character name in the
  code:
  - **`shock` with fixed points** (`"fixed"`: left, forward, height in unit space; no bone, no snap) and points on a PROP
    (`"snap": false`, the tips of the staff's fork). A bolt that "rises from the floor" = a link between a point on the
    floor (`g`, z 0.02) and one at the target's knee height (`k`, 0.40 m on a 0.70 m OSSINHO), plus knee↔knee links
    that chain the pack together and arcs from `k` down to the floor around it (`ground`). The clip's `zones` move the
    SAME effect: crest + staff + hand up to frame 65, the targets' zone from 66 on (a single effect = 26 bones, not two
    effects).
  - **`arc_min`**: a short arc (static on the crest, between the fingers: 5–15 cm) was only 5–15 mm wide because the
    width scales with the length. `arc_min` 0.024 m holds the thickness on screen.
  - **`spikes` layout `spots`**: cracks run from the seal's center to each target (0.2 m/frame) and `count / len(spots)`
    crystals grow around each one, leaning INWARD (`lean` [10, 8]°, a 0.21 m ring): the bars of light over the legs.
    One target's crystals break together, one target per frame. Without it the 5 targets became a single iceberg
    (`cluster`).
  - Colors as read on the field: light = white-gold (crystal, sigil, seal, shackles), electricity = blue
    [0.32, 0.58, 1.0] with a gold spark. Measured: [0.45, 0.7, 1] washed out to WHITE over the gold seal (additive);
    shackles [1, 0.9, 0.58] at 1.5 = white glass (ice) → [1, 0.8, 0.38] at 1.15; the seal at 2.4 was a gold PLATE →
    1.7; the staff's crystal in gold read as a TORCH against the copper → cyan-white, and smaller.
- A `step_out_of_first` of 367–381 mm on a hit/death can be an EFFECT bone (a spark born from scale 0 at the burst
  point): list the bones before hunting the "jump".

## 3. The five clips

| Clip | `kind` | How it is born | What to check |
|---|---|---|---|
| attack | `attack` | retargeted actor take + `layers`; authored weapon profile | anticipation with slow-in, a strike that only accelerates, 3 frames of hit-stop, a VISIBLE settle, exit in a single arc |
| idle | `loop` | hold on the base + breathing, weight shift, gaze, one "heft" | the BODY breathes (≥ 2 px at 64 px), not the weapon; nothing still; mismatched reversals |
| walk | `loop` | parametric `recipe.gait` in place | `travel_render.py`: the foot stays on the disc (≤ 1 cm per contact); the weapon does not sway more than the body |
| hit | `oneshot` | authored layers base → base | recoil on the 1st frame, face clear, recovery longer than the strike, last frame = base |
| death | `oneshot` | layers + `floor: "body"` + `weapon.release` + `free_hands` | the fatal strike is BIGGER than a regular hit; a monotonic fall; `ground_table.py`; the released prop leaves to the FRONT of the fall |

**Every key is a stop.** A layer interpolates with an ease UP TO each key (zero velocity at every key): right
for extremes, a stutter for passing keys 1–2 frames apart (head at 2.0 / 1.5 / 2.2 / 1.4 / 3.1 m/s). On body
layers (torso, chest, head) use `"interp": "spline"`: ONE monotonic curve through all the keys — flat at the extremes,
moving through the passing keys, never overshooting a key; an ease written on a key (the strike's `"in"`, `"hold"`) still
applies to its segment. And fewer keys: a dip is start, bottom and return.

A cycle is a ring: last frame == first, periodic filters, springs inherit the previous lap. The arms close at a
PHYSICAL angle (`weapon.py` reports `cycle_closed_deg`): a reference transported frame by frame comes back rotated by
what the path enclosed (holonomy) — the more the body moves in an idle, the bigger the seam this would open (6.4 mm).
`hub_pin` pins the ends to the base (`"all"` on a hold; not on a gait cycle; never pin beard/cloth).

## 4. Loose masses and worn props

New chains come in through `landmarks.extras` + `secondary.chains`; `secondary.collide_prefix` (e.g. `["hair"]`) says
which of them collide with the prop. A ponytail that is born already touching the back marks 2–6 cm of contact when the
head throws back (hit, death): look from behind before treating it as a defect.

- `secondary.py` writes ONLY rotation (never `bone.matrix`: the pose scale accumulates); `clip.sh` fails if
  `pose_scale_off` ≠ empty. Per-character swing ceiling in `landmarks.json → secondary.chains`.
- A worn prop that goes into the head: a rule in `landmarks.json → keepclear` (a fixed character axis, ceiling in degrees).
- Overlap that belongs to the costume, not to the motion, is DECLARED (`contact.lap`) with its own tolerance — never
  raise the general gate.

## 5. Measure (after any change)

```
./clip.sh <id> <NAME> <clip>
python3 cf/bl.py run blender/contact_probe.py --arg name=<NAME> --arg action=<NAME>_<clip> --arg out=<json>   # 6 mm; no "penetrations"
python3 cf/bl.py run blender/motion_table.py  --arg name=<NAME> --arg action=<NAME>_<clip> --arg out=<json>
.venv/bin/python cf/path_plot.py <clip>_motion.json out.jpg [--window f0 f1]   # the ARC of the weapon head, 1 point per frame
```

`./contacts.sh <id> <NAME> <clip>...` runs both probes and prints one line per pair: mesh×mesh contact (6 mm) and
**floor** (`floor_probe.py`, 5 mm: nothing of the unit inside the floor on any frame — body, props from `cf_props` AND
the weapon from `cf_weapon_prop`; `airborne` = frames in which nothing of the body nor of what it still holds touches
the floor). The floor needs its own judge: no render shows what is under the floor — ALVOR's death passed
everything with the boot 6 cm buried, and what caught it was Unity's `bodyMinYCm`. In a clip with `floor: "body"`: the
foot keys are in ROOT space (after toppling 90°, "behind" is "below" and `fwd` is "up"); key the legs
landing 1 cm INSIDE the floor and `limbfloor.py` turns that into a contact; elbows respect `weapon.floor_radius`.

The five clips must start in the same pose (≤ 1 mm) and the cycles must close (seam ≤ 2 mm, chains < 0.5°):
`./hubcheck.sh <id> <NAME> <clip>` (attack first) gives the three numbers and the largest per-frame step of each bone.

Read the `motion_table` the way the critic reads it: head speed frame by frame (jagged = too many keys), hip
height (plateau = leg limit), the weapon head's height range against the hips', `slip` and `under_floor`.
Sign of a contaminated build: a crouched base pose, `lean_in_out.torso.fwd` near 90°, a `foot_pull_in` of tens of
cm — the clip inherited the pose of whatever was on screen (fixed: `retarget.py` and `polish.py` start from a clean pose;
if it comes back, someone assigned an action without `cflib.assign_action`).

## 6. The 12 principles, checked at game size

The unit is ~64 px tall on screen: 1 px ≈ 2 cm. What does not move 2 px does not exist. From the round-9 principles
verdict:

- **Anticipation**: the dip cannot be the fastest movement of the clip (it was 3.8 m/s against the strike's 3.4). Go in
  with slow-in and trade waiting for travel.
- **Follow-through**: after the hit-stop the body settles visibly (torso squash, the head nods, the prop bounces
  6–9°) and the exit starts early; 17 still frames read as a frozen frame.
- **Arcs**: draw the path of the weapon head (`path_plot.py`). A 20 cm sideways kick at the exit of the strike did not
  show in any of the six cameras.
- **Consistent weight**: the weapon cannot rise faster than it falls, nor sway 3× as much as the body in the walk; the
  torso is what pays for each movement of the weapon head.
- **Secondary action**: breathing in the chest/shoulders; head gaze ≥ 20° (8° = 1 px); the character's gesture must
  show up in the game camera.
- **Exaggeration as a ladder**: death > hit > idle. Compare the first-frame displacement across the clips.
- **Overlap**: the hips start 2–3 frames before the arms; the hands do not land on the same frame; reversals do not all
  fall on the cycle seam.
- **A written claim must match the image**: if the recipe says "the face stays readable" or "the hammer head
  slides", measure it. Three claims about the first character lost to the pictures.

## 6b. The GAME principles in the clip: reading, essence, strike, pack, close-up

The 12 principles (§6) say whether the movement is good; these say whether it WORKS in a mobile game seen from above at
64 px. Each item has the number and where to check it. The final judge is the arena lab in Unity (skill `character-show`
§9d), with the engine's blends — not the viewport.

### Reading the poses (one glance)

- Each clip has 1–2 **key poses** that tell the action on their own, as a silhouette, in the game camera (55° from
  above): attack = wind-up (the extreme of the anticipation) + contact; hit = the recoil of the 1st frame; death = the
  body on the floor; summon = the signature gesture. Check those poses in the lab (key V: 1:1 silhouette, the
  `+1 quadro` button (step one frame) to stop on them) and in the review package (64 px silhouette). A pose that turns
  into a blob = redo the pose, not the timing.
- **Broad movements**: the wind-up takes the weapon head ≥ 0.35 × the unit's height away from rest (≥ 22 px at 64 px);
  the torso leans ≥ 10–15° into the strike at the contact; head gaze ≥ 20° (8° = 1 px, §6). Seen from above, extension
  FORWARD and SIDEWAYS reads; up/down foreshortens (cos 55° ≈ 0.57): exaggerate what goes in the direction of the game
  camera.
- The contact pose points the WHOLE prop/limb at the target, outside the body's outline — it is the frame the player
  sees frozen by the hit-stop.

### Essence in motion

- Read the brief's trait × clip table (skill `character-design` §0b) before authoring each clip and write, at the top of
  the `clip.json` (`_doc`), which trait the clip amplifies and HOW (one number: degrees, frames, cm). A clip that shows
  neither of the 1–2 traits is generic — the principles critic gets the question "does trait X show here?".
- Rhythm is personality: the heavy one lingers in the wind-up and is short in the strike; the agile one has a short
  wind-up and more settle frames; the cold one has no fast secondary motion (OCASO walks at 0.32 m/s and his moment is
  the summon).

### Timing sells the strike (clear contact + holding the impact + effect + screen)

Current timings (30 fps, `export/<NAME>.json → clips.attack.events`):

| Unit | Wind-up apex | Contact (`hit`) | Settles | Total | Contact in s |
|---|---|---|---|---|---|
| OSSINHO | 8 | 12 | 22 | 28 | 0.37 |
| FERRUGEM | 16 | 23 (+ `rake2` 28) | 33 | 54 | 0.73 |
| OCASO (staff) | 16 | 24 (`land` 28) | 47 | 54 | 0.77 |
| ALVOR | 16 | 25 | 40 | 58 | 0.80 |
| BRASA / GRANIZO | 17 | **40** | — | **85** | **1.30** |

Rules:
- **Short strike**: from the wind-up apex to the contact ≤ 4 frames on a light unit (OSSINHO 4), ≤ 9 on a heavy one
  (ALVOR 9); in the 3 frames before the contact the tip covers ≥ 50 % of the arc (the "snap": tip speed growing up to the
  contact, `motion_table → speed.<arma>_head` (`<arma>` = the weapon), §2b "spacing"). A melee contact falls within ~0.8 s
  of the start of the clip. BRASA and GRANIZO (23 frames from apex to contact, contact at 1.30 s) are OUTSIDE this rule: a
  known limit of the hammers, to be redone when they are re-timed.
- **A clear contact frame**: the `hit` event falls EXACTLY on the frame of maximum extension (the tip on the target).
  `drag` on the weapon delays the contact by 1 frame: a strike that must land on the event takes `drag 0` (TECHNIQUES,
  "Hold on impact"). In the lab: speed 1/10, "Encostar" (close in), "Atacar" (attack), and `+1 quadro` until the readout
  shows `[HIT-STOP]` — the frame shown there (`attack 25/58`) is the frozen pose the player sees. If it is not the
  contact pose, the event is wrong.
- **Hold on impact**: the clip holds 2–3 frames at the contact (a visible settle afterwards, §6); the engine adds
  `hitStop` 0.06 s (≈ 2 frames) freezing attacker AND victim, and `killStop` 0.13 s on the killing strike. Total stillness
  at the contact: 4–6 frames on a regular strike, 6–8 on the death. Tune it in the lab (hit-stop −/+, 20 ms per click)
  and record the value in the character's `state.json` if it asks for a different one.
- **Effect and screen on the same frame**: on the `hit` event the engine fires the spark (`CFBattleFx.Spark`), freezes
  both and sends `Struck` → the arena camera shakes (0.35–0.9° by damage, 1.5° on the death, decaying in ~0.1 s) and
  gives a FOV punch (0.9° / 2.2°). Spell clip: the damage and the shake happen on `land` (the projectile lands); the
  caster does NOT freeze.
- **The exaggeration ladder in the engine too**: regular hit < killing strike (killStop > hitStop, shake 1.5° > 0.9°,
  spark 1.8× on the Death Ray).

### Small variations in a pack (a cheap trick, a big effect)

- A unit that comes in a group (OSSINHO, every summon, every squad) cannot walk in step: two identical copies side by
  side read as clones.
- **Baseline, already in the engine** (`CFBattle.varySquad`): each summoned unit gets an Animator speed of ×0.92–1.08 and
  a size of ×0.95–1.05, deterministic by the unit's key (golden-ratio sequence — a hash of neighboring keys gave ×0.93 to
  both skeletons of the same summon); the walk's ground speed follows speed × size, so the foot does not slide.
  Measured: OSSINHO_A ×1.04 / 0.97, OSSINHO_B ×0.98 / 1.05.
- **The full trick (next step)**: 2–3 walks per pack unit (`walk`, `walk_b`, `walk_c`) — same period
  ±2 frames, same frame-1 pose and same `enter_phase`/`leave_phase` (engine contract), but hip sway
  ±20 %, the weapon arm at another height, the head tilted to one side, a limping step. Each variant has its own
  `ground_speed_m_s` in the manifest; the engine picks one by the key. Start with OSSINHO (it is the only pack today).
- First `walk_b` made: GRANIZO (2026-11-14), the axe RESTING ON THE SHOULDER (the `walk` swings it at his side), period 30
  (walk 32), 0.742 × 0.756 m/s, silhouette 30–36 % different at the same phase at 64 px. Two lessons: (1) dragging the
  weapon behind the body vanishes from the game camera when the unit comes toward the camera (it reads as unarmed) — the
  variant must change what is seen from above and from both sides; (2) a loop whose grip is far from the base pose needs
  `weapon.lock_hub: false` (the solver pinned frame 1 to the base pose's elbow and swivel: axe head 117 mm inside the
  head).
- In the lab: "Invocar" (summon) 2–3 times, then "Andar" (walk; treadmill in place) — the skeletons must be in different
  phases of the cycle after 2 s.

### Eyes (rig with `eye.L` / `eye.R`, CENTELHA 2026-11-14)

An `eyes` block in the clip.json → `blender/eyes.py` (runs after the hub pin). `open` [[f, opening]], `look`
[[f, yaw, pitch]] (+ = her left / up), `blinks` [f of the closed eye], `side` {"L": {"open": ...}} (wink), `loop`.
Acting rules: the eyes anticipate the head by 2–3 frames; a blink at every head turn and every 2–4 s, irregular
(sometimes a double one); no blinking while concentrating; squint at the flash; widen in a fright; close slowly in the
death; wink in the victory close-up. Frame 1 = neutral (the pin applies to the eyes too); a cyclic walk may start off
neutral (`pin_first: false`). Details and numbers: `docs/TECHNIQUES.md` ("Olhos vivos", living eyes).

### Close-up moments (victory, unlock, menu) = personality

- The arena's **Retrato** (portrait) take turns the winner toward the camera and tilts him ~7° back from the feet; if
  the character has a `victory` clip (or `celebrate` / `cheer`), the arena plays it at that moment. The first one is
  GRANIZO's (`characters/granizo/anim/victory.clip.json`, 2026-11-14): copy from it.
- What GRANIZO taught in a one-handed `victory`: (1) the trophy raised with the arm up leaves the handle in line with
  the forearm → bracer 36.8 mm; a HORIZONTAL forearm and an upright handle (aim ~110°, head a little back) = 0;
  (2) at rest, the blade rolls toward the wrist's comfort and shows its EDGE to the camera: `weapon.edge`
  [[f, left, forward, up]] (unit space) points the edge to the side and shows the broad face of the head; (3) eyes
  that light up = two small `flame` effects (`size` 0.05, `level` 0 by default) on the head bone, at the eye position
  found by the texture color.
- `victory`: a one-shot of 1.5–2.5 s that ends in a HELD pose (`hold_last_frame`), with the essence trait at its maximum
  (the stubborn one slams the hammer on the floor and puffs out his chest; the cold one only raises the staff and tilts
  his head). The root does NOT turn (the engine turns and tilts it); head raised 5–10° in the final pose; hands and prop
  away from the face; a facial expression if the rig has the bones (skill `character-rig` §0).
- Judge it in the Retrato (lab → "Retrato" button, or after a knockout): face in the upper third, nothing in front
  of it, the expression reads at ~400 px of body height.

## 7. Video reference = the character itself, with colored limbs

The user's decision. Per clip: `blender/limb_paint.py --arg mode=on --arg still=mocap/char_color_still.png` →
`cf/runware.py video --model bytedance:seedance@2.0 --first-frame …` (the prompt repeats the colors and locks the
camera) → `cf/colorpose.py track` / `remap` → `blender/board.py --arg sequence=…` (the video alongside, synchronized) →
`./refcheck.sh <id> <NAME> <clip> <tag>`. `reference.role: "gate"` (idle, walk: < 0.06 overall, no limb > 0.10)
or `"beats"` (hit, death: the video only gives the timings — do not call the number approved). The color metric of a
single view does not see depth: it is a gate, not a goal. A human actor (Kling) only for the attack's mocap take; a 3D
pose on a stylized character fails. A Seedance job stuck in "processing": the client gives up at 1,500 s WITHOUT being
charged (check `runware.py balance` before and after). Relaunch ONCE (only with `--first-frame`); if it gets stuck again,
report it — on GRANIZO both jobs got stuck and the character was left without a reference (declared in
`state.json → reference`); do not invent the gate.
The reference is of the character AS HE IS: if he gets a prop or changes his guard after the videos (ALVOR got the
shield), archive the old ones (`mocap/v1_*`), redo the colored still in the new base pose (hide the effect mesh; choose
the view in which all four limbs show — a shield seen from the front covers everything) and generate again. ~US$ 0.80 per
video: check the balance, note it in `costs.jsonl` and in `state.json`.

How to READ the comparison (OCASO / OSSINHO, videos made after the clips — this also applies to auditing a finished
clip):
- The absolute position carries a common offset when the tracker reads floor brightness as torso (torso 0.44 in
  every version): compare the limb RELATIVE TO THE HEAD (center − head center) and the limb's AXIS. That is how OSSINHO's
  walk showed what the overall score hid: armR 0.078 / 25.6° → 0.059 / 12.2° with the overall score stuck at 0.19.
- Read the per-frame error RELATIVE TO THE HEAD (dx, dy, axis angle of each limb) before changing a key: in FERRUGEM's
  walk that is what showed the video's arms opening 0.2 of the height to the sides at each step. An asymmetric video
  (one step opens the arms, the other does not) is not copied into a game cycle: stay symmetric and declare the number.
- Sweep the phase of the `time_map` (`colorpose.py compare --map` with offsets 0..period): if the legs have their minimum
  at offset 0 and an arm does not change with the phase, the arm's error is one of POSE, not of timing.
- A one-handed weapon in the walk: the blade MOVES WITH THE FOREARM (upright when the hand comes forward, lying forward
  when it drops to the hip). Keyed the other way, the wrist hits the limit (55.7° of 60) and the blade covers the face.
- An "asymmetric" cycle seam in world meters: compare it with the OTHER extreme of the cycle before touching a key —
  the spline ends already have zero tangent in chest space; what remains is the torso carrying the arm.

### Lessons from ALVOR's round 2 (feet, fall, free hand)

- **A foot that turns on the floor turns on the ball**: `rot yaw` in `foot_ik` turns at the ANKLE. Add `loc side/fwd` =
  `v − R(yaw)·v` (v = ankle → ball) and, if the heel rises, `pitch` + `loc up` = lever × sin(pitch). Check it with the
  heel × toe travel (the `slip` of `motion_table.py` does not see a turn in place).
- **Step back**: the torso shifts onto the other foot (`torso fwd/side` keys) 2–5 frames BEFORE the foot leaves; the foot
  rises ≥ 5 cm.
- **Side guard + falling on the back**: the guard's yaw becomes roll on the floor. Measure the height of both shoulders
  on the last frame and adjust `chest roll` until they match; then check `ground_table.py` (back, chest, head, hands).
- **The hand that released the weapon**: `weapon.hand_floor` = the real thickness of the fist; `finger_floor` /
  `finger_radius` keep the fingers out of the floor. A prop resting on the body: lower it until the gate says "touches"
  with 3–5 mm.
- **Loop with `drag`**: the spring already runs over the period; if `last vs first` goes past 1 mm, it is a key, not the
  spring.
- Read the WHOLE output of `contacts.sh` (the penetration lines come first).

## 7b. QUADRUPED: generated gait, keys on top, solvers (UIVO)

- `./quad_build.sh <id> <NAME> <clip>...` = `blender/quad_clip.py` (gait + keys + springs + solvers, measured) +
  `fx.py` with the clip's `fx` block. Rebuilding throws the action away: the effects are ALWAYS re-keyed along with it.
  The `quad_clip.py` header = the contract (parameters in degrees/meters: `torso_*`, `hips/chest/neck/head_*`,
  `head_level`, `jaw`, `ear*`, `tail1..4_*`, `scap_*`, `paw_<FL|FR|RL|RR>_x/y/z/curl`, `follow_<pata>` (`<pata>` = paw);
  `torso_pivot`; `solve`).
- Loop with `gait`: touchdown / duty / lift / curl / toeoff / reach / scap / bob / pitch / flex / surge / roll / yaw /
  head_level / tail / ears / jaw per phase. The planted paw moves +S/2 → −S/2 (S = v × duty × T): zero sliding by
  construction. Gallop (UIVO 14 f, 4.4 m/s) and canter (25 f, 2.18 m/s) are already calibrated in
  `characters/uivo/anim/`.
- One-shot: keys only (generated by the character's `make_clips.py` from the idle's base pose — every clip starts in
  it). `follow_<pata>` = the paw goes with the body (death on its side, rearing); `head_level` = the hunter's head stays
  stable.
- Solvers (the `solve` report): `paw_floor` (a skin pad below the floor → raises the target), `reach` (a gap in the
  chain, a toe that does not reach AND the DEF bone that STRETCHES — Rigify hides the lack of reach by stretching the shin:
  3.6 % → skin 0.69 cm off in the FBX; a planted gait paw is not pulled, that would become sliding), `body_floor` (death,
  sitting: the floor is the target). If `body_floor` needs to lift a lot, the pose is wrong (the sitting howl rose 7.4 cm
  and the front paws floated 6 cm).
- Gate: `reach` ≤ 0.05 cm, `stretch %` ≤ 2.5, `floor` ≥ −0.5 cm, `slip` 0 (except for authored sliding, e.g. the hit),
  and LOOK from the side and at 3/4 (`strip`) — the metric does not see "looks like a begging dog".
- Seedance reference (§7) on a quadruped: the user's timing rules, the video gives the SHAPE. Run `refcheck.sh` on all
  clips with a `reference` block; on UIVO it changed two: attack (crouch LOW and stretch into a long pounce) and victory
  (a SITTING howl).
- **`end` of every one-shot** (`home` default / `hold` / `chain`): with `home` the springs settle in the last `settle`
  frames (8) and the last frame IS the base pose; whatever displaces a paw (the hit's push) must COME BACK in a step
  (rises, travels in the air, lands vertically) — "the next transition takes it home" made the export mark the hit as
  HOLD and Unity froze the wolf. Death and victory: `"end": "hold"`; the dash that ends at the target: `"end": "chain"`.
- **Default interpolation = spline** (monotonic Hermite, Fritsch–Carlson): the old smoothstep STOPPED every channel at
  every key — 60+ channels stopping together is the "robotic" feel the user saw in every clip. An explicit ease (`in` /
  `out` / `lin` / `hold`) still applies where a stop is wanted; loop: the tangents wrap around the seam. Gaits get
  springs too (`GAIT_SPRINGS` in UIVO's `make_clips.py`: head from the torso's sway, ear tips, tail 2–4).
- **A hunter's idle looks around in saccades** (turns in 3 frames with `out`, holds, turns) — a slow sine on the head
  reads as a turret.
- **Death with beats** (UIVO r2, 60 f): impact (yelp) → staggers (one paw STEPS OUT to the side) → the hind legs give
  way → the front folds → rolls onto its side with `in` → bounces → settles → limbs driven by springs from the roll →
  last breath → kick and claw. `follow_*` comes in during the fall. `body_floor` recomputes the NEEDED elevation on
  every pass (adding the passes up floated it 6.5–13 cm).
- **A quadruped's death = ON ITS SIDE, rolled PAST 90°** (UIVO r3, 52 f; r2's belly-down death read as "crouching,
  alive" to all three critics, and the chest-down one with the paws spread read as "about to pounce"). The WIDEST part
  decides how it lies: at 86° the mane props up the front (hips 19 cm, head 10 cm in the air). Roll to ~111°: the rear
  flank drops before the mane and the upper paws fall over the belly. Two rules of `quad_clip`'s
  `Rz(yaw) Ry(roll) Rx(pitch)` order: torso pitch on a rolled body tilts the long axis in the world by
  `sen(p)·cos(roll)` (p −22 at 111° = rear 7.7° lower), and past ~90° the relative YAW of hips / neck / head turns
  toward the floor (yaw + = to his left = down). Result: head on the floor (neck 1.5 cm), elevation 14.4 → 7.5 cm. The
  pivot paws hold `follow` 0 → 0.15 until the body passes over them. The HEIGHT in the game camera barely changes
  (67 × 118 px lying × 71 × 129 standing): from 55° above, the depth of a lying body projects like a standing one —
  judge the SHAPE (paws out, belly up), not the px.
- **Read `paw_fix_at`** (the frame of each paw's largest correction in the `solve` report): the death's 8.8 cm
  correction was in the middle of the topple (f19), the victory's at f35/f52 — not in the held pose.
- **A tail that SWEEPS the floor lifts the whole wolf**: crossing the midline the tip touches the floor, `body_floor`
  raises the body 3.8–5.2 cm and the front paws (already at maximum reach while sitting) leave the floor by 15–21 cm.
  Sweep to ONE side (yaw 14 → 28 → 12): elevation 0. And the sitting pose does not lean further than the front paws can
  reach (21°; 25–32° lifted them 9–21 cm) — the howl's height comes from the neck and the head (77–79 px; the target of
  85 was not reached, declared).
- **The step RISES before it travels**: the paw's z leads its y by one frame. With the `out` on the same frame as the
  lift, the engine's slide probe (paw ball below 7.5 cm) counted the first 5 cm of the step as sliding.
- **Landing weight is a TOOL, not a key: `gait.land`** `{"F": [queda, a, b], "R": [...], "pitch_F", "pitch_R", "head"}`
  — per paw, after touchdown: a fast drop (`queda`; a sine over `a` frames) and a rebound (a cosine over `b`), muzzle down
  on the front touchdown, the head lock gives way in the drop. Four touchdowns = four beats (the cosine bob was "one
  wave, nothing lands"). Canter: front 2.5 cm / 1.5 + 3.5 f, rear 1.2 cm; gallop: front 3 cm / 1 + 2.5 f.
- **`surge` is free if it is IN PHASE with the push**: 0.065 m at phase 0.42 stretched the hind leg 4.55 %; at phase
  0.3 (body further forward at the front touchdown) 1.34 %, zero sliding. Sweep the phase before reducing the amplitude.
- **The pounce ends ON the bite**: `dash_bite` = a one-shot whose frame 1 IS the last frame of the dash (read from
  `sprint.clip.json` by `make_clips.py`): the momentum carries the body 14 cm, the front paws skid (planned), the
  bite sinks in on f3 (`hit`), shakes, bites again (`hit2` f17). Dash → land → crouch → bite was a principles
  blocker.
- **Wind for the camera from ABOVE** (`fx.wind` in the landmarks): crescents lying flat (`arc_rolls` within ±35°;
  55–90° stood upright = sticks seen from above), radius 0.65, apex 14 cm in front of the muzzle (`arc_lead`), a thin,
  hot core (`arc_core` 0.045); streaks ≥ 5 cm wide (2 px) and ≥ 0.5 m long, born behind the shoulders and OUTSIDE the
  silhouette; the canter has no wind; the dash goes out on the last frame and `dash_bite` carries the decay.
- **Changing the base pose = an ADDITIVE layer, not rewriting keys** (UIVO r4, the reference's hunting crouch):
  `"layers"` in the clip.json (each set of keys is added on top of `keys`). `make_clips.py` keeps the old pose as an
  authoring reference (`HOME_R3`) and layer 0 of each clip = (new pose − old) × a weight per group (`body` / `head` /
  `tail` / each paw, or a single channel): 1 on the one-shots that leave and return to the pose, fading out when the
  body leaves it (death, victory), coming in during the recovery (`dash_bite`). The part of a PLANTED paw only changes
  while it is in the air or in a planned slide (kept through the topple, the death needed to lift the body 17 cm). A
  lower pose = less room for the strike's crouch: weight 0.45–0.5 on `torso_z` / `torso_pitch` during the action
  (chest −3.9 cm and forearm −1.7 cm into the floor with the full offset). A head that only goes DOWN disappears into
  the mane: neck forward and down (−28) with the head raised (+21).

## 8. Show

`blender/reel.py` assembles idle → walk ×3 → hit → attack → death; `blender/play.py --arg name=<NAME>
--arg action=<NAME>_reel --arg 'view=[52,9]' --arg mode=play` leaves it playing for filming.
