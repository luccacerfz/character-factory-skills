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
- **Additive effect = `CharacterFactory/FxAdditive`** (importer): the legacy `Particles/Additive` has soft particles
  and, at the editor's Ultra quality level, erased everything within ~1 m of depth of a surface — a seal on the floor,
  crystals, arcs on the skin (CENTELHA r6: the whole seal vanished). Same look, without the fade. A character imported
  before this changes on its next import.
- **Area spell with a stun longer than the clip** (`CFSpellBuilder.BuildSpell(host, unit, spots, stun, hold, pinFx,
  casts, killLast)` → `<HOST>_Spell.unity`, `CFSpellShow`): `CFFxHold.Bake(liveOff)` copies seal + shackles into a
  `CFSpellArea` IN THE WORLD (each cast adds an area; none clears another; it outlives the caster; one light per area)
  and turns the live renderers off only for the rest of the clip; `ReleaseOldest` / `Release` let go. The stun belongs
  to the unit: `CFUnit.Stun(s, from, freeze: true)` stops the Animator and restores its speed at the end or on death.
  `casts = 2, killLast`: the 2nd burst kills whoever is inside the seal's radius (`Damage` → `death` → `Vanish`).
  `CFSkyRain` keeps the rain going; `CFFrameRecorder` with `cam/width/height` records the camera into a RenderTexture
  (the Game window was in portrait). Measure the burst's whiteout AT the game camera (CENTELHA r8: > 1,000 px for
  0.10–0.13 s).
- **A one-shot stuck on its last frame**: `export.py` decides `hold_last_frame` by the POSE (body without effects and
  without the `secondary.py` springs); springs away from the base pose show up in `last_frame_springs_vs_home_cm`. If a
  clip that should return to idle comes back `hold: true` in the Unity report, read `last_frame_vs_home_bone` in the
  manifest before touching the clip.
- **A strike not named `attack`**: `MeasureTransitions` also treats as a strike the clip a projectile leaves from
  (`projectiles[].clip`) — a walk→strike row with `PlayWhenPlanted` and a shared exit window.

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

## 2g. An area spell in the engine: what breaks when the game interrupts it (CENTELHA r9–r15)

Scene: `CFSpellBuilder.BuildSpell(host, unit, spots, stun, hold, pinFx, casts, killLast)` → `<HOST>_Spell.unity` with
`CFSpellShow` (schedules the casts), `CFFxHold` / `CFSpellArea` (the area held in the world), `CFSpellAim` (aiming),
`CFSkyRain`, `CFShackleRings`, `CFSpellProbe` (per-frame proof). Order and measurements of the last round:
`characters/centelha/review/round_r15/unity/ENGINE_R15.md`.

- **Whatever replaces a live effect is born at its final colour on the SAME frame** the live one goes out (a copy with
  a 0.12 s fade-in = −76 % gold for 1–2 frames: the "blink"). A recast replaces per PIECE (`replaceOnRecast`: the old
  seal goes, the old shackles keep holding).
- **A single owner of `Animator.speed`** (`CFUnit.SetBaseSpeed / HitStop / Stun`): stun and hit-stop writing the same
  field always end with a unit frozen or sped up.
- **Aiming a spell baked into the skeleton** (`CFSpellAim`): after the Animator, the FLOOR effect bones are carried to
  the target without accumulating (a bone that only animates by scale has its previous offset undone first); bones that
  fly to the area take a fraction; bones used in both places, only on the frames where the clip draws them inside the
  area.
- **Interruption**: a watchdog that only tests "the burst is late" (trigger + event + 0.35 s) left the seal hanging
  1.03 s after a hit. Also test "it left the cast state" (`InCast()`: current state with the clip's name, or a
  transition into it) — the abort lands on the next frame — and skip a caster who is DOWN (`HostDown()`, which has its
  own path). The same for the burst → shackles window (0.233 s, read from the clip by the builder: `holdAfterBurst`).
  Killing counts CASTS (`CastIx = max(casts, bursts)`), not bursts.
- **Stopping a walker = letting the step finish** (`Halt`): zeroing the root at once, with `SetMoving(false)` waiting
  for the exit window, made the legs walk in place and `PinStep` carry the unit 9–10 cm at 0.73–0.79 m/s. Keeping it
  moving while `IsMoving`: 6.1–7.5 cm, 0.58–0.65 m/s (the rest is the `pinMaxCarry` cap = speed × 0.18 s); `walkOut`
  0.32 s in the unit's `blend_tune.json` (0.45 didn't help).
- **A cage only on whoever was caught** (`CFSpellAim.DecideSpots` at the burst): the bone of a spot without a target
  goes to scale 0 in `LateUpdate` (the held copy too, `CFFxHold` bakes with the bones' scale); the next cast's `wind`
  clears the decision. More targets than the clip's spots = a stun without a cage (declare it).
- **Cartoon glass** (`crystal` in the manifest → `CFMat` → shader `CharacterFactory/ToonCrystal`): pass 1 `Blend
  DstColor Zero` multiplies what is behind by lerp(1, transmission, alpha × gain); pass 2 `Blend One One` adds colour ×
  alpha × strength + fresnel; both faces (the far one × 0.45), no ZWrite — multiply and add commute, so there is
  nothing to sort between facets or cages. `glow` (opaque, lit, emission from the atlas) = solid light; additive =
  light (lightning, spark, ring) and it does NOT read over light grass.
- **Capturing in the editor**: `BakeMesh`, never `cam.Render()` after moving bones in the same call (the skin only
  updates in the player loop). Also record at phone size (360 × 640, 30 fps): a flash that blows out at 1280 × 720 may
  not blow out there, and an additive shackle over light bone vanishes (`CFShackleRings`: a DARK band under two light
  rails, ≥ 3.5 px).
- **Proof of the scene**: `CFSpellProbe` (per frame: units, seal, log; a `stop` block per unit: wait, root displacement,
  peak speed, foot drift) + edge takes: caster killed before the burst, caster HIT (alive) before the burst, hit between
  the burst and the shackles, a unit killed by someone else before the burst. Every take newer than every C# file (a
  table of times + md5). After each take: Stop + `OpenScene` of the scene.
- **A line of code swallowed by a comment**: `... // comment ... _light.enabled = false;` on a single line — the
  compiler doesn't complain, and every unit carried a lit light from `Awake` on.

## 2i. Texture, material and the mini look: what weighs and what is missing (2026-11-16)

A study of Tripo + the user's reference (a collectible mini on a card screen). The detail is in `character-design`
§3a–§3c; this is the engine's part.
- **Texture size is already decided at import**: `CFImporter.Tex` sets `maxTextureSize = 2048`, mipmaps and aniso 4 on
  every character map. Generating at 8K in Tripo does not change one pixel of the game. Measured on a brute's 4K
  albedo: 2K loses 0.40/255 on average (PSNR 49.2 dB) and 1K loses 0.74/255 (43.0 dB) — for the game camera (character
  ≈ 64 px) 1K is more than enough; 2K is for the close-up / Portrait. If memory gets tight on a phone, lower
  `maxTextureSize` per platform before touching the mesh.
- **Character FPS** is won with: 1 material per body (Tripo already delivers 1 atlas), bones within the budget
  (`character-rig`), LOD1 for the squad (`lod.py`), additive effects with no shadow. Texture resolution costs MEMORY,
  not frames — and the 2 M HD mesh never enters Unity (it is only a bake source).
- **The body uses Standard** (`Shader.Find(srp ? "Universal Render Pipeline/Lit" : "Standard")`). The look of the
  reference asks for three things Standard does not give by itself: paint that does not fall to black in the shadow
  (part of the colour unlit), wrapped light and a cool rim on the silhouette. `blender/paint_look.py` has that shader
  as a rehearsal (`mini`: 60 % unlit albedo + 40 % lit + a rim from the GEOMETRY normal — through the normal map the
  rim scratches white lines on the inner edges). **In Unity it exists since the healer v2**: `CharacterFactory/Mini`,
  switched on per material in the manifest (§2j). The painted albedo (`cf/tex_paint.py`) still pays off with Standard —
  in the brute's A/B (the `lit` render of `paint_look.py`, a Principled that imitates Standard) the painted one already
  reads better than the original: face, cracks and muscles.
- The painted albedo goes from the body material in Blender through `export.py` and `to_unity.py` into
  `<Mat>_basecolor.png`. The Warden verified this path under Built-in Standard in Play Mode with shared paint,
  zero metallic, a 0.88 roughness floor, specular highlights and glossy reflections disabled, and 0.35 normal strength.
  Confirm the material on the prefab as well as texture import. Adjust the paint pass if creases or shadows become too
  strong under scene lighting. Capture a close-up plus the Game camera and LOD transitions after import.
  See the [painted matte miniature guide](../character-design/references/painted-miniatures.md) for the diagnosis and checks.

## 2j. The mini look IN Unity, garments as worn props and Unity without a session tool (the healer v2)

- **`CharacterFactory/Mini`** (`Assets/CharacterFactory/Shaders/CFMini.shader`, Built-in, one pass + shadow, no extra
  texture): `_Paint` of the albedo drawn UNLIT (the colour never goes down to black), a wrapped lambert (`_Wrap`), the
  shadow lifted with a cool tint (`_ShadowTint` / `_ShadowLift`), a cool rim from the GEOMETRY normal (`viewDir.z` in
  tangent space; `_RimUp` fades the rim underneath), normal map × 0.6, a small highlight from the smoothness map. An
  added light only ADDS (the ForwardAdd pass is scissored to the light's rectangle: a fill there draws a pale square).
  Property names match Standard's — the importer fills the same maps.
- **Path**: `bl.py run blender/look.py --arg name=<NAME> --arg look=mini [--arg paint=0.5 --arg rim=0.32]` writes the
  `cf_look` tag on the painted materials (effects are skipped) → `export.py` → manifest `materials[].look` →
  `cf/to_unity.py` → `CFImporter.BuildMaterial`. `look=off` goes back to Standard.
- **Tune in the engine scene, record in Blender**: the defaults (paint 0.6 / rim 0.55) washed a pale grey skin — a white
  outline and flat volume; 0.5 / 0.32 hold the form. Change the materials by `execute_code`, capture, and ONLY THEN
  pass the numbers to `look.py` and re-export: the next `Import` rewrites the material.
- **Garments** (`character-rig` §4h) arrive as worn props: one skinned mesh per piece + a LOD1 of each. The floor gate
  reads EVERY renderer, LOD1 included — the skirt's LOD1 went 9.1 cm into the floor in the death with the body clean.
- **The manifest on the Unity side**: `Assets/Characters/<NAME>/<NAME>.cf.json`.
- **`python3 cf/unity.py`** when the session's Unity MCP tool does not connect (ECONNREFUSED) but the editor is open
  with the server: `read mcpforunity://editor/state` · `code '<C# 6>'` (or `code @file.cs`) · `call refresh_unity
  '{"mode":"force","scope":"assets","compile":"none","wait_for_ready":true}'`. It is a minimal MCP streamable-HTTP
  client: initialize, then one call.
- **Another session's editor**: read the state first (in Play → do not import). If a scene of other work is open and
  clean, note its path, do yours (BuildTraining opens your scene), and REOPEN the previous scene at the end; never
  save someone else's scene.
- **Capture in edit mode**: `cam.targetTexture = RenderTexture 1280×720` → `cam.Render()` → `ReadPixels` →
  `cam.ResetAspect()`; for a close-up, change the camera's position / FOV, capture and put it back. Sampling a clip
  without Play: `clip.SampleAnimation(object, t)` (it dirties the scene — do not save).

## 2k. A cast drawn by the ENGINE: ribbon, burst, heal bubble (`CFCastFx` / `CFFx`; the healer in the Squad scene)

The request it came from: "this attack VFX has to be more fluid… the attack and the heal much like the video".
- **A baked projectile does not read at the game camera**: effect bones keyed at 30 fps (a head + a tail that cross
  the field in 5 frames) are 2–3 loose blobs from above at 60 Hz. What reads is a continuous RIBBON from the hand to
  the target on every frame of the screen. `Profile.streakFx` → `CFBattle.Register` puts a `CFCastFx` on the caster
  (one `Cast` per `shots[]`; the `healClip` one is a heal): on the fire event (`hit`) the ribbon is born where the
  baked head was (glued to the nearest body bone: it follows the hand's follow-through), aims at
  `CFProjectileRetarget.target` every frame and lands on the `land` event. The baked renderer (`<NAME>_<Fx>`) is
  hidden from the fire event to the end of the clip; its charge in the hand, before that, stays.
- **The anatomy, measured on the reference video (a 60 fps sheet)** — count frames, do not "feel":
  attack = the hand flares ~3 frames → the ribbon extends in ~3 → stays tied ~3, waving → goes from the tail in ~2; a
  star on the target and the target flashes. Heal = ribbon ~4 frames → bubble on the 1st ally → jumps to the 2nd 2
  frames later → a thin line for ~0.13 s → the bubbles hold and fade; ~0.6 s in all. Our approved round: 4–5 of travel,
  tied until `land` (10 frames after the fire event), 3 of fade = 14 frames against ~8.
- **Ribbon** (`CFStreak`): LineRenderers over the SAME ~30 points; width by a curve (thin at the hand, fat near the
  head, a point); the wave = travelling sines × an envelope sin(πs)^0.7, zero at both ends (it leaves the hand and
  reaches the target on the line). `Mathf.Pow(Mathf.Sin(Mathf.PI * s), 0.7f)` is NaN at s = 1 (sin π = −8.7e-8):
  `Mathf.Max(0, …)`. The symptom was "Invalid worldAABB / Invalid localAABB" in the console, not a script error.
- **Additive light disappears on a bright floor**: orange added to a sunlit meadow = a pale pink-yellow; a green heal
  on grass = invisible. The ribbon's body and the rings in ALPHA (`CharacterFactory/FxAlpha`, the twin of
  `FxAdditive`) under the additive core; the heal in cyan; the scene's own darker ground. Bloom only on what is hot
  (threshold 1.1, 0.32).
- **Heal bubble** (`CharacterFactory/FxBubble` + `CFBubble`): a sphere in 2 passes — glass in alpha (the colour stays)
  + a fresnel rim and turning crescents in additive; it follows the unit (grows 0.11 s, holds 0.30, fades 0.32), a
  four-point glint in its middle, '+' rising, a ring on the ground. Colour / alpha / spin by `MaterialPropertyBlock`.
- **Sprites without an object per blow** (`CFFx.Emit`): ONE ParticleSystem per kind (glow, flash, ring, spark, plus),
  procedural textures, particles emitted by hand (`EmitParams`: position, velocity, colour, size, life). Pooled ribbons.
- **An offset that ACCUMULATES on an effect bone**: the Animator rewrites a bone's position only if SOME clip animates
  it. `CFProjectileRetarget` added its offset every LateUpdate: OCASO's hex mark (a bone that only SCALES) climbed
  3.49 m — a huge green ring near the camera at ~10 s — and the heal aura carried to the ally was 60 m away by the 3rd
  heal. The fix (in both): keep the local position from before the move and the one written; next frame, if the bone
  is still where it was written (nobody rewrote it), put it back before moving it again. Checked on the recording (2nd
  heal: the aura under the ally, no stray ring).
- **A further pass is compiled and NOT captured** (the user approved the round above and asked for Unity back): a
  four-layer ribbon (dark fringe + alpha body + glow + core), the ribbon leaves late so it ARRIVES on `land` (the hand
  flares first), embers off the ribbon, a flash on the target's body (`CFFlash`: a `FxFlash` material appended to
  `sharedMaterials` — a mesh of one submesh is drawn again — with the colour in a `MaterialPropertyBlock`, the same
  trick as `CFStunFx`'s rim), a smaller, shorter bubble. Record it (skill `character-show` §9e) before trusting it.

## 3. What the engine doesn't fix

A trigger on the wrong foot still drags 23–30 cm without a transition clip: that is a declared limit, not an importer
bug. If the game demands less, the way out is to author the transition clip or to wait for the phase (`leave_phase`).
