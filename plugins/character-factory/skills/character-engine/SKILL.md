---
name: character-engine
description: Take a Character Factory character into the engine — FBX export with Mixamo names, LODs and a contract manifest, copy to Unity, automatic import (materials, clips with events, additive effects, Animator, prefab), summoner with the units' prefab (CFSummoner), ranged attack (projectiles and the land event), a prop that wobbles and dies (training dummy — CFWobble, topple table), measurement inside Unity and transitions without foot sliding (PinStep, WalkPinStep). Use when the user asks to "export", "send it to Unity", "FBX", "import into the engine", "the foot slides in the transition", when closing out a character's clips, or when taking a training target / summoner into the engine. Includes the "feel" in the engine: hit-stop, camera shake on the strike, squad variation and Animator transitions tuned in the engine and saved per character (blend_tune.json).
---

# Engine: export + Unity

Operating rules: skill `character-factory`. Contract details: `factory/README.md` ("Engine (Unity)").

## 1. Export

```
python3 cf/bl.py run blender/lod_show.py --arg name=<NAME> --arg mode=hero     # always export with the hero mesh showing
python3 cf/bl.py run blender/lit_gain.py --arg name=<NAME>                      # if it has smoke/dust/steam: the brightness the light gives it
python3 cf/bl.py run blender/export.py --arg name=<NAME> --arg 'clips=["idle","walk","attack","hit","death"]' \
        --arg out=$PWD/characters/<id>/export/<NAME>.fbx                         # `clips` and `out` are required
python3 cf/to_unity.py characters/<id>/export ../Assets                      # creates Assets/Characters/<NAME>
```

Output: `characters/<id>/export/<NAME>.fbx` + `<NAME>.json` (manifest): clean skeleton with Mixamo names, at most 4
influences, body LOD0/LOD1, each prop as its own mesh on one bone, clips as NLA strips, events, cycle convention
(period + 1 frames), `ground_speed_m_s`, `enter_phase` / `leave_phase`, `stance_yaw_deg`.

The manifest also carries: `fx` (effect meshes, material `"blend": "additive"` + `strength` = the emission approved in
Blender; the importer uses the additive particle shader and multiplies the tint), `matte` per material (`to_unity.py`
bakes it into metallic/smoothness) and, for a one-handed weapon, `hand_prop`. The effect bones (`Fx*`) sit under the root
and animate by scale: the importer turns on `updateWhenOffscreen` and turns off shadows on those renderers.

Check in the export report:
- `round_trip.meshes_missing_in_file` empty (an object with `hide_select` used to be skipped silently by the
  selection-based exporter: ALVOR's aura was left out of the FBX and Unity refused the import);
- FBX round trip ≤ 0.05 cm on every bone and every frame (the bake decomposes each bone against the rebuilt parent;
  without that, Rigify's non-uniform scale shears the fingers by 6–8 mm);
- **SKIN round trip** (`round_trip.skin_round_trip`, per clip): `max_cm` ≤ 0.5 and `file_lowest_cm` ≥ −0.3. An exact
  joint says nothing about a boot 20 cm below it: FERRUGEM passed the joint round trip (0.021 cm) and Blender's floor
  probe, and Unity showed the boot 1.16 cm INSIDE the floor. Cause: a parent with non-uniform scale (Rigify's IK
  stretch) + a rotated child = shear, which TRS cannot store. The bake now makes the PARENTS similarity transforms in
  world space (or (a, b, a) when the children only twist — decided per clip) and only the leaves keep per-axis scale
  (`skin_fit.parents_axial`, `parent_anisotropy_dropped`, `parent_skin_worst_cm` in the report). A SCALE squash keyed
  on purpose on a bone with children would show up in `parent_anisotropy_dropped` — key it on a leaf;
- a character whose rig PREDATES the "no B-bones" rule of `rig_build.py` (GRANIZO): count the deform bones with
  `bbone_segments > 1` BEFORE the export and set them to 1 — the joint round trip passes (0.004 cm) and the skin one
  fails by 9.6–15.9 cm (twist along the bone moves neither head nor tail); after that, re-measure `./contacts.sh`;
- a FLOOR effect is not a projectile: only `cf_fx_*` with `lands` (bolt / hex) becomes `projectiles` (which
  `CFProjectileRetarget` pulls onto the target line). GRANIZO v3's `spikes` (crack + crystals) go to
  `ground_fx` + the `<fx>_arrive` event (attack 29 = `hit`); before, the export broke with `KeyError: 'lands'`;
- `height_m` equal to the height of the bind mesh (read from `mesh.vertices`; `bound_box` is the posed mesh);
- the exported prop is where `weapon.grip` says.

## 2. Unity

Instance: Unity 6 + MCP for Unity (everything runs in the open editor; `execute_code` compiles C# 6). After `to_unity.py`:
`refresh_unity` (mode force, scope assets) → `execute_code`:
`return CharacterFactory.EditorTools.CFImporter.Import("Assets/Characters/<NAME>");` (the fully qualified namespace is
required by the MCP's C# 6 compiler; equivalent menu: *Character Factory ▸ Import All Characters*). To capture:
`CFImporter.BuildShowcase(dir)` first (creates `Assets/Scenes/<NAME>_Showcase.unity` and OPENS that scene in place of
the current one), then `CFImporter.Capture(dir, clip, t, "Captures/x.png", w, h, camPos, lookAt, fov, -1)`.

- **Before `refresh_unity`, read `mcpforunity://editor/state`**: if `play_mode.is_playing` (the user's session, e.g.
  `Duel_Arena`), do NOT import — the refresh reimports the FBX and regenerates the prefab/Animator of a character that
  is in the scene. Run only `to_unity.py` (copies the files) and leave `Import` + `MeasureTransitions` as pending in
  `state.json` (GRANIZO v3, 2026-11-14).
- **Generic** rig: Humanoid maps on its own with Mixamo names, but muscle-space playback drifts by centimeters and
  loosens the two-handed grip; the importer measures and decides.
- Animator: rest = default state; gait = bool with `offset = enterPhase`; one-shots = triggers; transition duration
  set by the SOURCE (rest 0.06 s, gait 0.15 s, one-shot 0.08 s — defaults; tunable per character in the
  lab, `<NAME>.blend_tune.json`, §2e); priority death → hit → attack → gait;
  death holds the last frame.
- Leaving the gait: `CFCharacter.PinStep` pins the planted foot and moves the unit in its place, with a cap
  (`pinMaxCarry` = speed × 0.18 s). At heel strike the ball of the foot is still in the air: test the ankle; with
  both on the floor, the front foot counts. Without the cap the unit lunges up to 31 cm.
- Stopping on the right foot: run `CFImporter.MeasureTransitions(dir)` AFTER every `Import` — it measures sliding per
  phase, writes the exit window into the prefab (`leaveFrom/leaveTo/maxPhaseWait`) and measures again with the stop
  waiting (`CFCharacter.SetMoving(false)` + `StopStep`). The game moves the unit while `IsMoving` and may request the
  stop when `StopDistance` remains to the destination. ALVOR: 13.6 / 36.6 cm (mean / worst) → 0.9 / 4.7 cm; waits up
  to 0.72 s. Characters imported earlier (window 0/0) don't wait: old behavior.
- **Attacking on the right foot**: `CFCharacter.PlayWhenPlanted("attack")` waits for the same window (the unit keeps
  walking while `IsMoving`), then fires the trigger and pins the planted foot. ALVOR, 28 phases: walk→attack 12.2 /
  36.0 cm (mean / worst) → 2.4 / 4.0 cm; waits up to 0.68 s (mean 0.26 s). `Play` is still the immediate fire — use it
  for reactions (hit, death). Whoever advances the Animator by hand calls `PlayStep(dt)` after each `Animator.Update`.
  `Play` also CANCELS a pending strike (a hit during the wait fired the attack on top of the reaction — found by a
  critic reading the C#): every deferred action needs something that cancels it, and a row in `MeasureTransitions`.
  The `execute_code` history is lost on every recompile. Package captures (ALVOR, 560×460, fov 34): game camera
  `camPos (1.3, 3.1, 2.6)` → `lookAt (-0.15, 0.45, -0.35)`; low side `(-3.6, 0.75, -0.3)` → `(0, 0.5, -0.45)`;
  times idle 2.05 · walk 0.3 · attack 0.5 / 0.8 · hit 0.2 · death 0.25 / 0.6 / 1.2 / 1.45 / 1.95 s; repeat with
  `forceLod` 1 for the LOD1 row.
- The MCP's `execute_code` compiles C# 6 (no local functions or tuples). Play mode doesn't advance with Unity in the
  background: advance `Animator.Update` by hand to measure.

Second character (GRANIZO): export + copy + import + showcase + captures ran without touching code — the contract
is the manifest, not the character.

Read `bodyMinYCm` from the Unity report (the lowest point of the body across all clips): below −0.5 cm something is
inside the floor — go back to `./contacts.sh` (the `floor` row). On ALVOR this number (−6.0) found what no render showed.
`bodyMinYCm` reads only the body, on the probe frames. The report also carries `floor[]` — the lowest point of EACH
renderer (body, LOD1, weapon, shield; not effects) on ALL frames of all clips, with clip and frame — and
`floorMinYCm` / `floorWorst`; below −1 cm it becomes `problems`. That was what was missing when ALVOR's dropped sword
sat 1.7 cm inside the floor for 49 frames of the death: the body was clean, nobody was measuring the weapon.

Gate: `import ok=True problems=[]`, `bodyMinYCm` ≥ −0.5, correct controller sequence (death ignores later triggers), and
the planted-foot-per-transition table saved (`unity_transitions*.json`). Capture the game camera for the review package.

## 2b. Unit that rises out of the ground, summoner, ranged attack (OCASO + OSSINHO)

All of this is manifest data — no character name in the C#:

- **`sink` per clip** (`export.py` reads `cf_sink` from the action; `to_unity.py` → `clips[].sink`): the unit's OWN
  floor, per frame (−0.74 m on the 1st frame of `spawn`). The floor gate and `bodyMinYCm` discount that floor — without
  it, a skeleton buried on purpose fails by 74 cm. The root already descends in the clip; `sink` is only the judge's gauge.
- **`hold_last_frame` = "does not end in the base pose"** (`last_frame_vs_home_cm` ≥ 1), not "last ≠ first": `spawn`
  starts buried and ends standing — it has to hand off to idle. The comparison with the base pose **ignores effect
  bones** (`DEF-fx_*`): the bolt parked 3 m away at the end of the attack said "didn't return" and the attack froze
  (297.9 cm → 0.65 cm).
- **`summon`** (`rig/landmarks.json → summon` → manifest → `CFSummoner` on the prefab): the unit's prefab
  (`Assets/Characters/<UNIT>/<UNIT>.prefab` — **import the unit BEFORE the summoner**, otherwise it becomes `problems`),
  clip event, `spawn` clip, points `[esq, frente]` (left, forward) → local `(−esq, 0, frente)` (the unit faces +Z). On
  the event, one unit per point, the second one `stagger` later, turned `turnOutDeg` outward; `maxAlive` dismisses the
  old ones (`dismissClip`). Check three things: point = effect column bone (`FxRise*Ring`, error 0 on OCASO); on the
  frame the unit comes into existence, the whole body is below the floor (top −15 cm); from `ready` on, the lowest
  point ≥ −0.5 cm.
- **A freshly born Animator doesn't write a pose**: with `CullUpdateTransforms`, a renderer that was never drawn counts
  as invisible — `Play(spawn); Update(0)` advanced the state machine and left the unit STANDING for one frame (top
  +67 cm measured). `CFSummoner.SpawnAt` switches to `AlwaysAnimate` for that one evaluation only. This applies to
  anything instantiated already posed.
- **`ranged`** (effect `kind: "bolt"` with `target` in the landmarks): on the `hit` event the projectile LEAVES;
  `impactPointLocal` becomes the target and `projectileSpeed` the speed (OCASO: (0, 0.55, 3.2) m at 16.5 m/s; the bolt
  bone arrives 5 frames later). The showcase spawns no dust on the floor and shakes the camera on arrival.
- **"Foot on the floor" comes from the character's own feet**: `plantedBallHeight / plantedAnkleHeight` = rest height +
  1/5 of how far the walk lifts the foot (6–15 mm), with the old 4.5 / 10.5 cm as a CAP. On a 0.70 m mini the ankle
  never goes above 8.7 cm: both feet read as planted for the whole cycle, the pin held the swinging foot and the table
  "measured" 15.8 / 22.2 cm of sliding (real: 3.4 / 4.1). If a small character's transition table comes out absurd,
  read `plantedBallCm / plantedAnkleCm / footLiftCm` in the report before touching the clip.
- `BuildShowcase` for a summoner: sequence `summon` → attack, camera pulled back by the reach of the points, `maxAlive`
  = number of points. To check the real trigger, enter Play (`manage_editor play`) and read `Time.frameCount`,
  `CFSummoner.Units` and the states via `execute_code`: on this machine Play advanced without focus (1,610 frames in
  9 s); if `frameCount` doesn't advance, turn on `Application.runInBackground` and, as a last resort, advance
  `Animator.Update` by hand.

## 2c. Target that wobbles, and training (TOCO + OCASO + OSSINHO)

- A prop that gets hit (training dummy, totem, banner) is NOT a character: `blender/wobble_rig.py` (upright bones,
  weights by height) → `blender/export_prop.py` (FBX without clips + manifest `kind: wobble`, springs, `target`) →
  `cf/to_unity.py` → `CFImporter.Import(dir)` branches to `ImportWobble`: Generic rig WITHOUT an Animator (with "None"
  Unity imports a rigid mesh: 0 skinned triangles), `CFWobble` on the root with the SAME springs as `wobble.py`.
  Report: height, tris, floor, `targetLocal` (+Z = the painted side; the importer fails it otherwise).
- Projectile baked into the animation (bolt / hex from `fx.py`): `export.py` turns the flight recorded in the action
  (`cf_fx_<fx>`) into a `land` event on the burst frame, and the manifest gains `projectiles` (clip, fx, launch and
  landing frame, target, arc). The game kicks the target on `land`, not on `hit` (on `hit` the projectile LEAVES). The
  target sits where the projectile bursts: axis = the projectile's target + the disc's depth (`BuildTraining` reads both).
- `CFImporter.BuildTraining(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Training.unity` with `CFTraining` (patrol,
  summoning, spells, strikes, target HP, raising a summon from the body). The round RULES (slots, topple band,
  `stopLead`, `unitLead`, HP, full ring), the camera and the proof with `CFRoundProbe` are in skill `character-show`
  §7 — it is the mirror of `blender/training_show.py`.
- What is import contract (and lives here): `wobble.topple` in the manifest (`to_unity.py` flattens `dirs` into
  columns `deg / r / k2 / rest`: `JsonUtility` doesn't read nested arrays) and the importer adds 180° to the angle
  (Blender XY → Unity XZ; local (x, y, z) → (−x, z, −y)); a target without the table becomes `problems`.
- **`CFCharacter.WalkPinStep` applies to EVERY character** (on by default, `pinWhileWalking`): while the walk plays,
  the foot that moved least since the previous frame stays where it was and the unit is carried by it (cap
  `walkPinMaxStep` 0.03 m). Curves and arrivals without sliding (0.009 cm per 1/30 s on OCASO). It runs after `PinStep`
  and only when that one isn't pinning; turn it off per character with `pinWhileWalking`.
- The Game window may be in portrait: capture through the camera into a 1280×720 `RenderTexture` (`cam.Render` +
  `ReadPixels`).
- **High-fps video**: `CFFrameRecorder` (dir, fps, seconds; `Stop()`) fixes `Time.captureFramerate` and records the Game
  view at the end of each frame (post-FX and OnGUI HUD together) → `ffmpeg -framerate 60 -i f_%05d.jpg`; `frames.txt`
  gives the game time per frame (cut on `battle.Log`). Showcase reel for one character: a scene with `CFReel` (all
  clips, a title per clip, walks in an arc, attack in slow motion, death → `Rebind` → victory) — GRANIZO:
  `Assets/Scenes/GRANIZO_Reel.unity`. `Screen.width` read by `execute_code` is the editor window, not the Game view.
  Ask before taking over Play: the user may be in the lab.
- **Split screen, several characters on the SAME script**: `CFSplitReel` (`Assets/Scenes/Factory_Split.unity`, 6
  panels 3×2 + a step/skill strip between the rows). All of them stand at the ORIGIN, each on its own layer (24+i, the
  summons too, via `UnitSummoned`); each panel is a copy of the main camera that sees only its layer + the scenery and
  renders into its own `RenderTexture` (2× and filtered): with `Camera.rect` the post-FX `OnRenderImage` grabs the whole
  screen. OnGUI assembles the grid, and `ScreenCapture` records everything. Frame by the size of the BODY (`*Body*`
  renderers): with props and effect columns in the bounds, OCASO ended up at half size. After death, `Rebind` doesn't
  restore an exploded body: `CFExplosion.SetBlown(false)` (FERRUGEM vanished in the victory). Fixed-duration steps
  (idle 2.8 · walk 4.6 · attack 3.2 · special 4.4 · hit 1.7 · death 3.1 · victory 2.8 s) = 1,362 frames at 60 fps in
  ~4 min.

## 2d. Effects by type, explosion and stun (FERRUGEM)

- The effect material's `blend` comes from the TYPE: `additive` (bolt, spark, flame, aura: light, no shadow), `alpha`
  (dust, steam, explosion smoke: Alpha Blended UNLIT two-sided particle, tint 0.5 = the map's color — the lit Standard
  Fade drew the cards BLACK when seen from behind), `""` (the explosion chunks: the body, opaque, WITH shadow). A mesh
  with several materials (gibs: body / rim / smoke) = one entry per used slot (`slot`, `color` for a material without
  a texture); the export removes empty slots so that slot i = submesh i. The importer fails it if the number of
  materials doesn't match `subMeshCount`.
- The `explosion` block of `death.clip.json` → manifest (`to_unity.py`) → `CFExplosion` on the prefab: on the event
  (`explode`), every standing `CFWobble` within the radius takes damage + a push away from the heart and, if it
  survives, `Stun`. The heart is the mean of the bones on the last frame with the whole body (at the event the `root`
  scale has already hidden it). Game: `Exploded(centro, raio)` (center, radius).
  "Whole" = neither the `rootBone` nor the bones right below it with `lossyScale` < 0.95 (the export puts the collapse
  on the hips, not on the `root`: testing only the `root` sampled the heart 1 cm above the floor at above 30 fps).
- An imported target (`ImportWobble`) gets `CFStunFx` with `CF_StunArc.mat` (additive) and `CF_StunRim.mat` (shader
  `CharacterFactory/StunRim`; built-in pipeline only). The stun is Blender's `shock`, layer by layer, drawn by the
  engine: arcs with the `fx.py` image (hot core + glow), fork, arc to the floor, ballistic sparks, a star at the jump's
  landing, a flickering light and a blue FRESNEL over the body — the fresnel is what reads on the game camera
  (additive over a light albedo only brightens). Arcs only on the outer SHELL (cell of 2 cm × 22.5°, radius ≥ 85% of
  the cell's maximum, normal facing out) and with `cameraBias` (the side the camera sees).
- **Chunks (gibs) in the engine**: the `gibs` manifest → `CFExplosion` swaps the renderers ONLY in Play and on the
  event (chunks on, body off; it switches back when the body is whole again after `restoreAfter`); the hot rim glows
  via `MaterialPropertyBlock` = color × strength × scale of the `FxGibsHeat` bone (in Blender, a driver). Slot 0 of the
  chunks = the body's material (`share`: no second copy of the maps); the effects' LOD1s go into the `LODGroup`s.
- **Never "slot i = submesh i"**: the FBX importer triangulates concave n-gons on its own, lost 420 triangles of the
  caps and SWAPPED the LOD0 submeshes (whole interior yellow, rim black; LOD1 came out right). `export.py` exports with
  `use_triangles=True` and writes `submeshes` (triangles and area per slot); `CFImporter.MatchSlots` matches by the
  best permutation (fails > 5%) and `CFExplosion.hotSlots` stores where the hot material landed in EACH renderer.
- **Lit smoke drawn without light**: run `blender/lit_gain.py --arg name=<NAME>` before the export (it measures how much
  the approved viewport's light brightens each smoke material → `cf_lit_gain` → `tint` in the manifest). The importer
  converts to the project's color space: the legacy particle shader does 2 × tint × map in WORKING space and, in a
  Linear project, tint 0.5 showed the smoke at 0.43× the map (FERRUGEM: black soot).
- **Recording an event frame by frame in Play**: on the event, set `Time.captureDeltaTime = 1/30` and capture in an
  `EditorApplication.update` when `Time.frameCount − f0` reaches each offset (`Camera.main.Render` into an RT);
  `Application.onBeforeRender` doesn't fire with the Game window hidden. Log via `AppDomain.SetData`; save to
  `review/unity/unity_melee_r<N>.log` + `review/unity/blast/`.
- **Capturing a LineRenderer / camera effect**: move the camera in one call, capture in the NEXT one. The `View` ribbon
  is built for the frame's camera: moving and rendering in the same call drew the arcs sideways, inside the sack (58%
  of the pixels vanished). To hold an instant: subscribe to the event (`Exploded += ... Time.timeScale = 0.04f`) and
  capture right after.

## 2e. Feel in the engine: hit-stop, shake, varied squad, transitions tuned in the engine

What the clip promises (clear contact, a hold on impact, a squad that doesn't walk in step — skill `character-clips`
§6b) the engine delivers like this. All in `Runtime/CFBattle.cs`, `CFDuelDirector.cs`, `CFDuelLab.cs`, `CFBlendTune.cs`.

**Hit-stop** (`CFBattle.hitStop` 0.06 s, `killStop` 0.13 s):
- On the hit event (melee: `hitEvents`; spell: `landEvent`) the `Animator.speed` of the attacker AND the victim goes to
  0 for that time (spell: only the target — the caster released the projectile long ago). `Freeze` adds to the unit's
  `until` and `nextAttack` only the NEW frozen time (two strikes in a row don't add twice), `Think` returns while
  frozen (not even the push moves) and `Thaw` restores the unit's OWN speed (`animSpeed`, see squad).
- Proof by arithmetic, not by screenshot (the freeze lasts 2 frames): at 0.1× FERRUGEM advanced 9 frames of the attack
  in 0.416 s of game time instead of 12.5 — the missing 3.6 are the two 0.06 s hit-stops of the `hit` and `rake2`
  events. The lab's readout shows `[HIT-STOP]` and the frozen frame.
- The reaction trigger (`hit`) is set BEFORE the freeze: the transition starts and stays paused, the victim holds the
  contact pose and the reaction snaps when it is released — that is the effect we want.

**Signal to the camera** (`CFBattle.Struck(ponto, dano / vida máxima, matou)` — point, damage / max HP, killed — on the
same frame as the spark):
- `CFDuelDirector.OnStruck`: ANGULAR shake (the view rotates, the camera stays put; Perlin at 38 Hz, decays e^(−9t)) of
  `shakeHit` 0.35–0.9° (by damage fraction) and `shakeKill` 1.5°, half that in Retrato (Portrait) and Livre (Free); FOV
  punch `punchHit` 0.9° / `punchKill` 2.2° (decays e^(−11t)). All in UNSCALED time: the shake is the same in the
  knockout slow motion.
- Any other director (the dungeon's `CFDemoDirector`) subscribes to the same event — no polling HP every frame.

**Varied squad** (`CFBattle.varySquad`, `squadSpeed` (0.92, 1.08), `squadScale` (0.95, 1.05)):
- Summons only (the hero is always the same). `Vary` in `OnSummoned`: Animator speed and transform scale, body
  radius × scale, `walkSpeed` × speed × scale (the foot doesn't slide: the clip's ground speed scales with playback
  AND with size). The battle's clip times go through `Len(u, clip)` = duration ÷ speed.
- Deterministic by the unit's key, with a golden-ratio sequence (h = frac(k·0.618 + 0.17)): the first hash (sine of
  neighbors) gave ×0.93 to both skeletons of one summon.

**Transitions tuned IN THE ENGINE** (`CFBlendTune`, JSON per character):
- Categories of the controller the importer builds: `walkIn` (rest → walk, 0.20), `walkOut` (walk → rest,
  0.20), `fromHome` (rest → one-shot, 0.06), `fromLoop` (walk → one-shot, 0.15), `fromOneShot` (one-shot → one-shot,
  0.08), `back` (one-shot → rest at the end, 0.10; `exitTime` = 1 − back / duration). The category is READ from the
  controller (rest = default state; loop = a state with a Bool parameter of the same name), so it works for any character.
- In the lab ("Transicoes" (Transitions) panel, editor only): edit; **Aplicar** (Apply) writes to the `.controller` and
  the Animator in Play uses it right away (measured: the rest → hit transition went to 0.250 s without restarting the
  state); **Salvar JSON** (Save JSON) writes `Assets/Characters/<NAME>/<NAME>.blend_tune.json`. `CFImporter.Import`
  reads that file (without it, the defaults above) — reimporting doesn't lose what was tuned by eye.
- Warning: Aplicar changes the asset on disk even outside Play. To undo a test: `TuneApply(lado, new CFBlendTune())`
  (`lado` = side; these are the defaults) or reimport.
- Tuning by eye has a limit: a blend that is too short pops where the poses differ (the rule that the five clips start
  in the same pose ≤ 1 mm is what allows 0.06 s); a walk blend that is too long slides — check with `MeasureTransitions`
  after saving and reimporting.

**Viewing another camera inside the game** (the lab's inset): a RenderTexture drawn by IMGUI in a Linear project comes
out with one EXTRA gamma encoding (floor 0.40 drawn as 0.66 = 0.40^(1/2.2)), whether the RT is sRGB or linear.
Draw directly to the screen per viewport (`camera.pixelRect`, `depth` above the main one) and copy the main camera's
`CFPostFX` to the preview camera (without it the view looks washed out next to the game); measurements still go into
their own RT with `RenderWithShader`.

## 2f. Quadruped (UIVO)

- `export.py` reads `rig["cf_quad"]`: its own name map (Hips/Spine/Spine1/Spine2/Chest/Neck/Neck1/Head, Tail1–4,
  Left/RightScapula, Left/RightFrontUpLeg/FrontLeg/FrontFoot/FrontToeBase, Left/RightUpLeg/Leg/Foot/ToeBase, Jaw,
  Left/RightEar1–2) — the Mixamo map would call the tip of the tail "Hips". `FEET` = the four paws; `rig_bones` gains
  `frontFoot*/frontToe*` and the manifest `quadruped: true`. Generic rig (no Humanoid for four legs).
- `CFImporter` picks the gait by the name `walk` or, failing that, the first loop with a speed: put `run` before
  `sprint_loop` in the clip list. `sprint` is a DASH (`gait.dash`: distance, frames, profile) — the game moves the unit
  along that profile, not at a constant speed.
- C# with FOUR feet (done 2026-11-14): `CFCharacter.quadruped` + `frontLeft/RightBall`, `FootCount` / `GetFoot(i)`
  (null ankle on the quadruped), `QuadWalkPin` (planted paws only, the one that moved least, cap `walkPinMaxStep`).
  Planted = `ballRest + margem` (margin; 7.5 cm on UIVO). Import: `ok=True problems=[]`, −0.449 cm.
- **Quadruped pin = MEAN of the planted paws** (`PinStep` / `Carry`): pinning only the leading paw kept it still and
  made the other planted paws slide by what it didn't (UIVO run→attack with window 29.5 / 37.7 cm → 6.2 / 9.6).
- **`PinStep` starts on the frame BEFORE the blend and finishes the last piece of it**: the blend's 1st frame has
  already moved the foot by that frame's weight, and a 0.08 s blend that ends between two frames lost the rest (the
  lunge's pin carried 0.12 m of 0.28 in one long editor frame and the bite landed 14 cm short of the target).
  `ResetPins()` after teleporting the unit (round restart); a support recorded more than one `pinMaxCarry` away is discarded.
- **`QuadWalkPin` re-read the paw AFTER moving the unit and added the correction again**: it became an integrator,
  −3 cm per frame (the cap) BACKWARD, and the 2.18 m/s run moved at 1.24 m/s in Play. The table showed it: with the pin
  (15.7 cm) worse than without it (5.8). Rule: if the game mode (with the pin) measures WORSE than without the pin, the
  pin is wrong — not the clip.
- **Character-driven dash**: `PlayDash(distância)` (distance) fires the clip, drops the gait and records origin/direction;
  `DashStep()` moves the unit along the profile in `LateUpdate` BEFORE the pins (moved after, the pin recorded the paw
  before the last push — ~10 cm — and pulled the wolf backward); `IsDashing` until it lands. Entering a dash is a CUT
  (`CFBlendTune.toDash` 0.03 s) and nothing is pinned; leaving a dash that has already landed pins the planted paws and
  the body settles onto them (0.28 m on UIVO): sprint → attack / hit / death / victory / idle = 9.8 / 5.4 / 4.0 / 3.9 /
  3.4 cm.
- **How a one-shot ends** (`end` in clip.json → `cf_end` → manifest → `CFClip.end`): `home` (default: hands off to
  idle), `hold` (death, victory), `chain` (the dash ends AT the target and the strike follows on the `land` event; it
  never holds — a state that holds has no exit, so the attack couldn't follow; without a strike, it holds 0.1 s and
  returns on its own, `exitTime = 1 + 0,1/len`, interruptible by the source's triggers). `export.py` reports
  `end_problem` when a `home` doesn't return. UIVO r1: the tail still swinging 4.46 cm at the end of the attack and the
  hit's slide (6 cm) had turned into HOLD — the wolf would freeze after every bite and every hit. Check `hold` per clip
  in the Unity report.
- **Gait → gait directly** in the controller (`UseGait` swaps the bools on the same frame): going through the base pose,
  the run almost came to a full stop before the gallop. The swap transition goes BEFORE the return home in the state's list.
- **ENTRY phase measured in the engine**: `MeasureTransitions` sweeps all of the gait's entry phases (ramp +
  `WalkPinStep`, as in Play), writes the best one into the controller if it beats the export's by 0.5 cm and adds the
  line `entry phase swept`. UIVO 0.80 → 0.60: idle→run 43.3 → 1.4 cm; GRANIZO 0.0 cm. Run `MeasureTransitions` after
  EVERY `Import`.
- **JOINT exit window** (stopping AND striking: `PlayWhenPlanted` waits for the same window): chosen by the worse of the
  two per phase. Going by the stop alone, UIVO had two phases where the attack slid 18–19 cm. UIVO 0.76–0.96: run→idle
  3.0 / 9.9, run→attack 6.2 / 9.6 (wait ≤ 0.65 s); GRANIZO walk→idle 1.1 / 3.9, walk→attack 1.3 / 1.8.
- Measuring a loop by hand requires `SetMoving(true)` / the gait bool: without it the controller goes back to idle in 7
  frames and the measured "sliding" (146 cm) was the idle being carried. And `MeasureTransitions` runs what
  `LateUpdate` runs (`DashStep` → `PinStep`, including on the gait's last frame) — otherwise it measures a different engine.
- Declared limits (UIVO): idle→sprint 44 cm (the dash is born from the run's extended phase — the game enters it from
  the run); idle→attack 7.2 cm = 60 Hz interpolation of the hind paws between keys at 30 fps (0 in Blender).
- **Hunt against the dummy** (`CFImporter.BuildHunt(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Hunt.unity`,
  `CFHunt`): all the clips of a hunter with a dash, in alternating rounds (victory / hit + death), clip caption on
  screen, a camera that follows, health bar. Where the target sits is MEASURED: bite reach (the furthest-forward skin
  above the paws at the attack's 1st `hit`: 1.016 m), the dash exit's carry (0.28 m) and the target's face at bite
  height (0.184 m) → the bite goes 2–4 cm into the face. The dash's own bite (0.797 m) closes in the air ~0.5 m short
  (`dashBites` false). Video: `CFFrameRecorder` (fixed 60 fps) + `CFHunt.RestartFromTop()`.
  Against the "robotic" look in the engine (r2): bites CHAINED on the attack's `interrupt` event (`chainEvent`), each at
  its own speed (0.93–1.07, golden-ratio sequence: `BiteSpeed`) — attack → idle → attack was a reset; death starts
  halfway through the hit (`deathAt` 0.5) instead of after the whole recovery. Camera (`cameraMode`, key C):
  `Top` = the game camera (56° elevation, fov 38), `Side` = the old one, `TopAndSide` (default) = top-down + the side
  view in an inset (`insetRect`, "Side Inset Camera" copied from the main one, depth +1).
- **Wind effect** (`fx.py` type `wind`, landmarks `fx.wind`): arcs at the muzzle + streaks that stay in the WORLD; they
  go into the FBX like any effect (`Fx*` bones by scale, additive material). The clip is in place, so streaks and dust
  already move BACKWARD in the clip by however far the ground moved (`ground_travel`): when the engine carries the unit
  forward at the clip's speed, they stay still in the world. Only valid if the unit moves at the manifest's `ground_speed_m_s`.
- **First bite = `dash_bite`** (r3): `CFHunt.dashBiteClip` plays at the end of the dash when the controller has the clip
  (`HasClip`); the following bites chain in the attack. `BuildHunt` measures where the target sits from the `hit` of
  the FIRST bite's clip (`first_bite` in the JSON; carry 0.0 m). Unity: sprint → dash_bite 2.1 cm vs. sprint → attack 10.3.
- **A unit without a weapon has no hand prop**: `export.py` put `UIVO_Hammer` in the manifest because `cf_weapon_prop`
  had "hammer" as its default. Now: no key in the rig and no `<NAME>_<prop>` object → no prop (`prop`/`hand_prop` = "").
- Open after r3: idle → attack 8.4 cm and idle → hit 9.9 cm (ball of the paw; a standing → standing `PinStep` would
  cancel the planned slide of the hit), run → attack waits for the window, the wind renderer isn't turned off outside
  the gaits, `sprint_loop` rows in `MeasureTransitions`, a cap on `maxPhaseWait`.
- **A new base pose changes the whole table** (UIVO r4, crouched with paws spread): the mean improves (run → idle 5.5 →
  4.3, run → attack 8.8 → 6.8 cm), but whatever goes from a paws-TOGETHER pose to home gets worse — dash interrupted by
  death / hit / victory 4–9 → 8.5–11.3 cm (the dash landing vs. home's spread paws). The hunt path (sprint → dash_bite)
  stayed at 2.1 cm because `dash_bite` brings in the new pose only in the recovery, with each paw in the air. Run
  `MeasureTransitions` and compare with the previous table on every base-pose change.

## 3. What the engine doesn't fix

A trigger on the wrong foot still drags 23–30 cm without a transition clip: that is a declared limit, not an importer
bug. If the game demands less, the way out is to author the transition clip or to wait for the phase (`leave_phase`).
