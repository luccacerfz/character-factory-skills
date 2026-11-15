---
name: character-show
description: Scenes with MORE THAN ONE character and game rules in the Character Factory — rehearsed summoner + summoned units, arena (spells and strikes on a training dummy), round with health (patrol, the target dies and topples, a summoned unit is born from the body, a new target rises) — simulated by rules in live Blender (the user films it) and mirrored in Unity (CFTraining, CFWobble, CFSummoner, CFPath, CFRoundProbe). ALWAYS use when the user asks for characters acting together ("he summons and the skeletons attack", "attack the dummy", "walk back and forth and then attack", "when the dummy dies another one comes up", "training scene", "show the two together", "show", "round"), when the characters VANISH from the show, when a foot slides on a curve or on an arrival, or when taking one of these scenes to Unity — including a BATTLE in an environment (two characters + summoned units fighting with all their animations and skills, rounds that alternate the winner: CFBattleBuilder / CFBattle / CFUnit, Battle_Meadow). Includes the 1x1 arena test LAB (CFDuelLab, key L): Death Ray, attack / hit / walk / summon buttons, slow motion and frame by frame, 1:1 game view with silhouette and tuning the Animator transitions — use when the user asks to "test the animations", "death ray", "buttons to trigger them", "see it at game size".
---

# Shows and rounds: characters together, game rules

A show animates nothing new: every pose comes from an approved clip. What it does is REHEARSE the engine contract in the
viewport (who triggers what, where, on which frame) so that the defect shows up in Blender before it shows up in the game.
Operating rules: skill `character-factory`. Each character's clips: `character-clips`. Export/import:
`character-engine`. Examples: `characters/ocaso` (summoner), `characters/ossinho` (summoned unit), `characters/toco` (target).

| Script (`blender/`) | What it stages | Unity mirror |
|---|---|---|
| `summon_show.py --arg host=<HOST>` | the host's `summon` + each unit's `spawn` at the `landmarks.summon.points`, NLA strips | `CFSummoner` + `CFImporter.BuildShowcase` |
| `arena_show.py` | summons, casts at the target, units walk to the target and strike — WRITTEN plan (`host_plan`, `walk_start`) | `CFImporter.BuildTraining` (version without health) |
| `training_show.py` | round SIMULATED by rules: patrol → summon → spells/strikes → health → death → raise → new target | `CFTraining` (current) |
| `spell_show.py` | AREA spell on a squad (CENTELHA × 5 OSSINHO): marching in phases (each one reaches ITS slot, the clip's `spots`, on the explosion frame; planted foot ≤ 0.076 cm/frame), the sigil falls, the explosion LOCKS each one in its slot (stun: frozen pose = 2-frame action taken from the walk at that frame, 11° chest recoil + 4.5° tremors every 2–3 frames that fade; effects held: the seal / shackles / bolts channels repeat a window of the cast for 48 frames, then sink), they are released and move on | (round 6: battle in Unity) |

Shared base: `showlib.py` (`stop`, `play`, `reveal`, `drop_show`, `compose`, `fillet_path`, `path_at`, `pin_root`,
`heading`). Read the script's header before passing arguments — the defaults are already the approved ones.

## 1. Operating the `CF_Show` scene

- Everything lives in the `CF_Show` scene (collections `CF_Show_Host` / `_Units` / `_Stage` / `_Target` / `_UI`); the
  character being worked on stays untouched in the main scene. Modes: `build` (default; already plays) · `play` · `stop`
  · `off` · `remove`.
- **`--arg mode=off` before any pipeline script** (`clip.sh`, probes, renders): they act on the context scene.
- **`--arg mode=remove [--arg host_too=true]` before saving the `.blend`**, otherwise the show (and the appended host)
  goes along into the character's file.
- **"They vanished from the screen"** → `--arg mode=play`. It calls `showlib.reveal`: a collection's eye in the Outliner
  (`layer_collection.hide_viewport` / `exclude`) hides everything inside it while `obj.hide_get()` keeps saying
  "visible" (2026-11-12: 7 of 34 objects in view, the whole show vanished). Diagnosis: `o.visible_get()` × `hide_get()`
  and the collection's flags in the view layer. Check with `python3 cf/bl.py shot <png>` before saying it is back.
- One show scene at a time: the `build` of any of the three deletes the previous `CF_Show` and its collections
  (`drop_show`; `summon_show` also takes `_Target` / `_UI`), keeping only the appended host.
- The host is APPENDED from its own `.blend`, without the export `<HOST>_skeleton` or what it deforms (a second staff
  lying on the stage was that). The unit is COPIED per point: `obj.copy()` of a rig re-targets what is internal (IK,
  drivers); what points from OUTSIDE (armature modifier, parent of the meshes) is swapped by hand (`showlib.remap`).
- A script that runs another one inside it (`training_show` runs `wobble.py`) reads the result from `cflib.last_out` and
  passes `"scene": show.name` — the child has to work in the show's scene, not in the context's.
- **A stray copy shadows the module**: a backup `showlib.py` left in a scratch folder that is on Blender's `sys.path`
  shadowed the real module (`cannot import name 'build_field'`). Keep backups under another extension, and
  `del sys.modules["showlib"]` before importing again.

## 2. Compose, don't animate (`showlib.compose`)

- ONE baked action per character, assembled from `(action, start, phase)` items: a loop wraps around the period (n − 1),
  a one-shot holds its last frame, consecutive clips CROSS-FADE over `xf` = 5 frames (quaternions by nlerp). A hard cut
  pops: the 1st frame of the walk is 31 cm from the base pose on the free hand. NLA tracks with `blend_in` blend with the
  REST pose on the track below — hence one composed action, not strips (only `summon_show` uses strips, without blending).
- **After every one-shot, add an idle item**: without it the action holds the last frame frozen until the next
  clip.
- `override(out, frames, plan)` is the hook for editing frame by frame after composing (moving the rune column).
- A hand-written plan (`arena_show`) is fine for a 10 s rehearsal. With a game rule (health, death, who attacks when),
  SIMULATE (`training_show`): frame by frame, the same rules as `CFTraining.cs`, and only then bake. Read the result's
  JSON (`patrol`, `units`, `deaths`, `raises`, `life`, `wasted`, `target_falls`) — it is the screenplay that Unity
  has to repeat.

## 3. Walking over the floor without sliding

- Walking in place + a dragged root only works in a straight line. On a curve the planted foot slides (0.7 cm/frame on a
  0.3 m arc) and a unit that arrives and turns in place slides much more (65° in 6 frames = 4.4 cm/frame).
- **`pin_root(rig, scene, design, fa, fb, toes)`**: every frame the planted foot stays where it was and the root goes
  where that puts it (root = previous position − R(yaw)·toe_local); the end error (13.9 cm on a 2.58 m patrol) is spread
  over the walk → 0.03–0.07 cm/frame on straights, curves and stops.
  - Planted foot = the one that moves LEAST in the world under the planned root, NOT the lowest one: the robe drags both
    feet low, the pin picked the swinging foot and the root walked backwards (end error 56 cm).
  - Read the pose through the show scene's depsgraph: `rig.evaluated_get(scene.view_layers[0].depsgraph)`. `pose_bones`
    only updates in the context's ACTIVE scene — with the scene switched in the same script the samples froze (error
    85 cm). A freshly positioned object: `matrix_basis` (no parent), not `matrix_world` (it waits for the depsgraph).
- **Path** = `fillet_path(points, radius)`: straights + arcs of a single radius (the same construction as `CFPath.Fillet`).
  Stretch it to last WHOLE walk cycles and start the walk on the phase that ends it on the exit frame that slides the
  least (`walk->idle best_frame` from the export manifest; OCASO frame 21): phase = (h_exit − 1 − n_walk) % period.
- **Arrival**: the path's last leg already points at the target (`fillet_path([P0, S − d·0.3, S], 0.25)`; in Unity the
  intermediate point `unitLead` 0.3) and the unit is BORN facing where it is going to walk. No turning in place.
- Unity: `CFCharacter.WalkPinStep` (on by default, `pinWhileWalking`, cap `walkPinMaxStep` 0.03 m) does the same pin in
  real time; `stopLead` 0.18 m because the step ends and the cross-fade carries on (without it the unit stopped
  0.16–0.24 m too far and the cleaver went 17 cm into the sack; with it, 0.699 / 0.763 m from the axis for 0.70 asked).

## 4. The target: position, springs, health, fall

- **The target is born from the projectile**: axis = projectile target + the depth of the painted disc (TOCO at 2.79 m =
  2.60 + 0.19). A bolt aiming at empty space at 3.2 m is what showed this. The damage comes in on the frame the
  projectile LANDS (the flight is in the action: `cf_fx_<fx>`; `land` event in the export), not on `hit` (on `hit` it LEAVES).
- Springs that read at 64 px: 2 Hz, damping 0.13, cap 22° → spell 13.6° (the top moves ~26 cm), bolt ~8°, cleaver ~7°.
  The first tuning (peak 12, cap 16, 0.15) gave 8.5° = 2 px: "it wasn't hit". Rig and springs: skill `character-rig` §4d.
- **Health**: hp 16; spell 5, bolt 3, cleaver 1 (defaults of `training_show` and `CFTraining`). With hp ≤ 0 no NEW spell
  or strike starts (a strike already in the air is counted in `wasted`).
- **Death = a rigid body toppling over the edge of the foot** (`wobble.py` `life`, `CFWobble.Fall`): per-direction table
  from `topple_fit.py` (rig §4d), φ'' = g L sin φ / (k² + L²), kick = 1.3 × the minimum that clears the edge → TOCO: 25
  frames to the floor, 2 bounces (restitution 0.22). Gate: `lowest_mm_after_impact` ≤ 5 mm (got 0.6).
- **Clear fall lane**: the target falls away from whoever killed it; the summoner kills from the front, so the body falls
  BEHIND (180°). Slots `[65, −65, 125, −125]`. With someone at 180° the 2nd body fell on top of the skeleton and the 3rd
  was born 3 cm inside it (Unity, 3 deaths in 36 s).
- The health bar is UI, not a character: two quads, keyed scale and emission color (green ≥ 0.67, yellow, red
  < 0.34), hidden while the target is down, turned toward the camera (in Unity, toward `Camera.main`).

## 4b. Melee and death explosion (`melee_show.py`, FERRUGEM × TOCO)

- Where the unit STOPS is measured: claw points (hand/finger groups) of each event against the target's `collider`
  (`landmarks.collider`: radius per height + boxes); distance × turn grid, bite ≤ 45 mm. The BVH nearest-normal test gave
  absurd depths (40 cm) on thin planks.
- Death with an `"explosion"` block in `death.clip.json` (radius, damage, `push_deg`, `squash`, `stun_s`): on the event,
  a target inside the radius (measured from the body's CENTROID on the previous frame) takes damage, is pushed away and is
  STUNNED = the target's own `shock` effect (its landmarks, built on the show copy by `fx.py` with `scene=` and `frames=`)
  + random 3° jolts every 2–3 frames on the springs. `attacks_after 1` so it survives (4/16) and the stun shows.
- A channel that ONE clip keys (the `root` scale that hides the exploded body), ALL of them key: without that the show
  inherited the vanished body and found no contact at all.
- Outside the context scene, object AND bone are read through the scene's depsgraph (`evaluated_get`): the original's
  `matrix_world` stayed at the origin and the explosion center came out 0.8 m off.
- Unity: `CFImporter.BuildMelee(hostDir, targetDir, standDistance, standTurnDeg, walkMeters)` → `<HOST>_Melee.unity` with
  `CFMelee` (walks on its own heading to the stand MEASURED in Blender — FERRUGEM 1.17 m, turn 0 —, strikes on the `hit` /
  `rake2` events, new target, `attacksAfter`, ending with hit + death). The explosion is `CFExplosion` on the prefab (from
  the manifest); the stun is `CFWobble.Stun` + `CFStunFx` (procedural additive arcs over the surface, the same level curve
  as the show).

## 5. Raising a summoned unit from the body (reads as necromancy)

1. The summoner plays its OWN summon again (`raise_delay` 18 frames after the fall).
2. The rune column of the 1st point goes to the body: location offset on the `DEF-fx_rise_l_*` bones
   (+= R_rest⁻¹·Δ, through `override`); the other column stays at scale 0.001. Move it to where the unit COMES OUT
   (`rises_at` = the body), not to the final slot — the first version got this wrong.
3. ONE unit comes out of the body's center of mass (C = T + d·(r + (−r cos θ + h sin θ))), 3 cm from it on OCASO, and
   walks to the nearest free slot (0.85 m), with the path from §3.
4. The body sinks inside the column (u^1.7 over 28 frames, 1.25 m); the new target rises ((1 − u)^2.2 over 10 frames,
   stretched 7 % on the way up, squash 0.08 + a 5° forward nod on landing) with full health.
5. Full ring (4 slots; Unity only for now): the oldest summoned unit crumbles (`CFSummoner.Dismiss`, death clip) and the
   new one takes the slot. Every death still spawns a summoned unit.
- `after_respawn` 120: frames shown with the new target standing — with fewer, a second death started before the end.

## 6. Camera

- Round with a lateral patrol: **az 135°, el 32°** (high, behind the host's left shoulder, à la Clash Royale),
  distance = box diagonal × 1.42, `view_shift` (−0.12, −0.12, −0.25): the patrol crosses the screen, the painted disc
  faces the camera, the fallen body and the new skeleton behind the target stay in frame. From the side (az 88°) the
  patrol turns into depth — that angle suits a lob's arc (`arena_show`).
- Title turned toward the camera (`cflib.label` faces −Y). A camera behind the target shows the disc from the back.
- Unity (`BuildTraining`): center = Lerp(host, target, 0.62), behind = (−forward − right), distance 2.75 × span,
  elevation 32°. The Game window may be in portrait: capture through a 1280×720 `RenderTexture`.

## 7. Unity: the same round

`CFImporter.BuildTraining(hostDir, targetDir)` → `Assets/Scenes/<HOST>_Training.unity` (Training object with only
Transform + `CFTraining`). Import the unit and the target BEFORE the host.
- `CFTraining` ([DefaultExecutionOrder(50)]): host 0 idle → 1 pure pursuit on the `CFPath` → 2 stopping → 3 turns to the
  target → 4 summons → 5 fights/raises; units 0 being born → 1 route and then slot → 2 stopping → 3 strikes while
  `target.IsUp`. Counters `Kills`, `Raised`, `Dismissed`, `UnitCount`.
- `CFWobble`: `Hit(push, peak, squash, damage)` returns whether it died; `Fall`, `Sink`, `Rise`; events `Died(pos)`,
  `Landed`, `Risen`; the fall table comes from the manifest (`wobble.topple`; the importer adds 180° to Blender's angle).
- `CFSummoner.RaiseAt(pos, rot, fxSeconds)`: the NEXT summon event raises ONE unit there and takes the column of the
  1st point (`Fx*` bones grouped by effect and matched to the point by rest position). Names with a serial (`R1`,
  `R2`…: they all came out as `R3`).
- **Proof = `CFRoundProbe`** (on the Training object before Play; remove it afterwards and save the scene without it):
  events, planted-foot slide in cm per 1/30 s per character, the host's path, captures at the requested times →
  `characters/<id>/review/unity/round_probe.json`. OCASO, 48 s: 5 deaths, 4 raised, 61 hits, stops 7 cm from the point;
  planted foot 0.009 (host) / ≤ 0.05 (units) cm per frame, peaks of 1–2.7 only on isolated transition frames.
- Play advanced without focus on this machine; if `Time.frameCount` does not move, `Application.runInBackground`.
  `execute_code` compiles C# 6.

## 8. Gates before showing it to the user

| What | Number | Where |
|---|---|---|
| planted foot while walking (Blender) | ≤ 0.1 cm/frame (0.03–0.07) | result of `pin_root` / of `training_show` |
| planted foot (Unity) | mean ≤ 0.1 cm per 1/30 s; peak only on a transition frame | `round_probe.json → slide_cm` |
| target after impact | ≤ 5 mm below the floor | `life.lowest_mm_after_impact` |
| nobody in the fall lane | 0 units within ±30° of 180° | slots used |
| screenplay | deaths, raised units, target standing again before the end | result JSON / probe events |
| eye | a ~15-frame sheet of the round + the viewport playing | `review/work/training_round_sheet.jpg`, `bl.py shot` |

Close with the host's `state.json` (`training_round`, with what was NOT done), one line in `docs/TECHNIQUES.md` per
new lesson, the show PLAYING on screen and, if the file is going to be saved, `mode=remove` first.

## 9. Battle in an environment (Unity): two characters and what one of them summons

`CharacterFactory.EditorTools.CFBattleBuilder.Build("<FIRST>", "<SECOND>")` (menu *Character Factory ▸ Build Battle
Meadow*) → `Assets/Scenes/Battle_Meadow.unity`: ORIGINAL painted meadow (procedural texture + bushes, flower bed, rocks,
trees as generated meshes, shader `CharacterFactory/Foliage`), warm sun + trilight ambient, high camera (52°, 10 m,
FOV 30) following the center of the fight, and the `Battle` object with `CFBattle`. Import the three characters first
(the summoned unit before the summoner).
- **Nothing is typed per character**: height and radius come from the baked idle; the strike's reach is the forwardmost
  point of body + props at each hit event of the clip (the smallest gives the reach, the mean of the angles gives the
  heading); projectiles and summon come from the manifest. What is a RULE (health, damage, cooldown) lives in `Tune` —
  balance, not measurement.
- **Rules** (`CFBattle`): target = nearest enemy every 0.5 s, but whoever is striking does not drop its target; the
  summoner advances 0.7 m, summons when it has no living summoned units, cooldown 11 s, enemy at ≥ 1.5 m; damage ≥
  `bigHit` interrupts an attack; summoned units crumble with their master; explosion = damage + `Stun` + reaction + push
  within the radius; bodies push apart.
- **Rounds that tell the story**: the first side's health vector decides who wins (`firstHealthByRound` 60 / 19: the
  brute kills the summoner; weakened, it dies and explodes). Check that the effect you want to SHOW finds the target
  alive: with 26 the explosion killed OCASO and the stun never appeared.
- **Proof**: record in Play with `Time.captureFramerate = 30` and an `EditorApplication.update` that renders `CFBattle.cam`
  into a 1280×720 RT per new `Time.frameCount`, with a log every 15 frames (health, clip, `IsStunned`, position) and the
  `CFBattle.Log`. Play reloads the domain: arm it AFTER Play and restart the round by reflection (`_round = 0`,
  `NewRound`). Assemble the sheet of the moments (entry, summon, strikes, death, explosion, stun) and the mp4.
- Traps of this scene (numbers in `docs/TECHNIQUES.md`): vertex color in a Linear project (`.linear`);
  `Mathf.SmoothStep` is not an edge; shadow fill only in the base pass (point light = square); `Pow` of a negative
  sine = NaN.

### 9b. Teams and a kit environment (dungeon: ALVOR + FERRUGEM × OCASO + OSSINHOs + BRASA + GRANIZO)

`CFDungeonBuilder.Build()` (menu *Character Factory ▸ Build Battle Dungeon*) → `Assets/Scenes/Battle_Dungeon.unity`.
Everything comes from `factory/env/dungeon/layout.json` (floor, pits, each prop with position / turn / scale / light,
walls, light types, spawns) and `pools.json` (outline of the pits, written by `env/tools/dungeon_floor.py`). Changed the
layout? Run the floor generator BEFORE the builder (the floor paints the pits that the builder sinks).
- **Teams** (`CFBattle.firstTeam` / `secondTeam`, `Entry` = prefab + profile + spawn + advance): each unit is born
  facing the center of the other team; per round, `first/secondTeamHealthScale` (health) and
  `first/secondTeamDamageScale` (damage AND healing); summoned units follow their side's scale. With healing on a team,
  scaling HEALTH does not alternate: ALVOR's aura restored ~18 health in 30 s and humans ×0.45 against undead ×1.6 still
  gave "blue wins". Health ×0.5 / ×1.3 + damage ×0.55 / ×1.5 alternates: round 1 blue in 31.4 s, round 2 red in 25.2 s
  (FERRUGEM explodes at the end).
- A summon in progress when the summoner dies: the 2nd summoned unit arrived 0.03 s AFTER the death and stayed alive;
  now it crumbles in 0.45 s (`OnSummoned` checks the master).
- **Healing aura** (`Profile.auraHeal / auraRadius / auraPeriod / auraColor`): heals wounded allies within the radius
  (ring + rising sparks, `CFBattleFx.HealRing / HealMotes`); with nobody wounded it tries again in 0.5 s.
- **Pace**: teams 11.7 m apart (FERRUGEM walks 0.26 m/s) spent 10 s just walking and the round took ~50 s; at 6.5 m and
  with 5-health skeletons (with 8 the brute got stuck in the summon waves), ~26 s.
- **Reference camera** (portrait, almost top-down): 68°, FOV 32, 44 m, `camFollowX` 0.2 (it stays on the lane's line).
  Record 720×1560 (portrait `RenderTexture`), not 1280×720.
- **Height changes and bridge** (`layout.json → terrain`): a wall-to-wall goo moat crossed by a Tripo root, raised edges
  and plateaus with stairs. The builder reads the top of the root from its OWN mesh (raycast) and builds the `CFGround`
  (20 cm grid: height + walkable; 8-neighbor A*, no corner cutting, max step 0.22 m; string-pulls the path through
  `Line`). `CFBattle` uses a straight line when it can and `Steer` when it cannot; `Keep` slides along the edge; `Height`
  only adds walkable cells.
- **5 heroes, 3 × 2**: BRASA and GRANIZO join the crypt side (`TuneHammers`). With `Time.captureFramerate = 30` the
  round is DETERMINISTIC (round 3 repeated round 1 frame by frame): calibrate in the editor and trust it. Health ×0.8 /
  damage ×0.85 on the crypt → blue wins round 1 in 46.9 s (ALVOR at 10/40); humans ×0.85 / ×0.85 → red wins round 2 in
  38.5 s.
- **Clean battle** (request: "too much loud color"): the environment is the stage, the minis are the show. Dark goo with
  a subtle vein (the vein's glow was 0.43 linear in blue = lilac blotches at sRGB 0.68: emission > albedo × light in a
  dark scene); bloom only on what is hot (threshold 1.3, intensity 0.3: the health bars blew out); props' glow ÷ 3; moat
  lights 1.7 → 0.55; team colors blue × RED (magenta = the goo's color). None of this touches the characters.
- **Demo as a game**: `CFDemoDirector` (intro, 5 cameras, automatic cutting, HUD) + `CFDemoBuild.Build()` →
  `Builds/MasmorraDemo.app` (resizable 540×960 portrait window, Retina, 14 s build). The build fails in Play.
  Recording WITH the HUD: the app with `-cfrecord <dir> -cfseconds N` (`CFDemoRecorder`: `ScreenCapture` at the end of
  the frame catches OnGUI; `Camera.Render` into a RenderTexture does not).

### 9c. 1x1 test arena (everyone against everyone, in takes)

`CFDuelBuilder.Build()` (menu *Character Factory ▸ Build Duel Arena (1x1)*) → `Assets/Scenes/Duel_Arena.unity`: flat
green field (40 m painted square, worn ring at 4.6 m, start marks at ±2.6 m; brush only beyond 7.5 m, trees at
21–43 m), procedural sky, linear fog. `CFBattle` in team mode with ONE entry per side + `CFDuelDirector`:
- roster and pairs on the component (empty = all pairs); the queue sets up the next pair right on `RoundOver`
  (`NewTeamRound` reads `firstTeam/secondTeam` only when the round starts); W/L score, knockout = slow motion 0.3 for
  1.2 s + Perto take;
- takes 1 Jogo (game) · 2 Lateral (side) · 3/4 Ombro A/B (shoulder) · 5 Órbita (orbit) · 6 Topo (top) · 7 Perto (close)
  · 8 Livre (free) · 9 Retrato (portrait); keys C, A (auto), N, R, Space, H, F, L (lab);
  `Cut(t)` / `TakeName` public for tools; the duel axis turns slowly and never turns more than 110°;
- capture: `cam.Render` into an RT of 1000 × 1000/aspect and `cam.ResetAspect()` afterwards; HUD only via `ScreenCapture`.
- Grass: measure the rendered pixel (target ~ (99, 168, 75), sat 0.55) — light + post raise R/G ×1.3 over the albedo.
- **Feeling the strike** (2026-11-14): every hit freezes attacker and victim (`hitStop` 0.06 s; `killStop` 0.13 s on a
  death; a spell freezes only the target) and sends `CFBattle.Struck` → angular shake 0.35–0.9° (1.5° on a death) + FOV
  punch. Details and the proof by numbers in skill `character-engine` §2e.
- **Take 9 Retrato** (the personality close-up): after the knockout slow motion the director cuts to the winner, who
  turns to the camera and leans `portraitTilt` 7° back around the feet (fov 28, pitch 10, face in the upper third, its
  health bar hidden); plays `victory` / `celebrate` / `cheer` if the character has one. The VITÓRIA (victory) card moved
  down to the lower third (central band 56 % of the width, a thin rule in the winner's color) — it never covers the face.
  Reference capture: `env/duel/shots/lab/retrato_alvor_s.jpg`.
- Summoned units vary (`varySquad`): the OSSINHOs of one summon are born with their own rhythm and size (×1.04 / 0.97
  and ×0.98 / 1.05).

### 9d. Test lab (`CFDuelLab`, key L) — the "Death Ray" and every animation on a button

The quick test in the engine: the duel rules stop (`CFBattle.hold`: no AI, no round end; the action clocks keep
running) and the arena pair becomes a test bench. Same `Duels` object in the scene (`CFDuelBuilder` already adds the
component). Outside the lab there is a "LAB (L)" button in the lower right corner. Button labels below are the literal
UI strings (Portuguese), with an English gloss.

| Where | Button / key | What it does |
|---|---|---|
| panel A / B | **Atacar** (attack; T = A, Y = B) | the hero's next attack clip, turned by the measured strike heading, at the other hero (out of reach the melee misses, as in the game) |
| | **Dano** (hit) | the hero takes a blow without damage: spark, hit-stop, `hit` clip, camera shake |
| | **RAIO DA MORTE** (Death Ray; K = on B) | beam from the sky + ring on the floor + 1.8× spark; dies ON THE SPOT, from any state (standing, walking, mid-attack) — the death from any clip without needing a fight. The body stays 2.5 s in the final pose before sinking |
| | **Andar / Parar** (walk / stop) | the walk IN PLACE (treadmill: the foot pin is switched off so nobody leaves the mark), the hero and its summoned units together — where the squad variation shows; Parar uses the stop on the right foot |
| | **Invocar** (summon) | the summon clip (only for those with a `summonClip`) |
| bar | **< Par / Par >** (pair), **Reviver** (revive) | switches pair / respawns the current pair on the marks |
| | **Encostar / Afastar** (close in / back off) | to strike distance (the pair's SHORTEST melee reach: both strikes land) / to the marks (±2.6 m) |
| | **Lateral / Jogo / Retrato** | director takes (Lateral is the lab's default) |
| | **G Jogo 1:1** (game 1:1) | the GAME view on a 360 × 640 px phone drawn in real pixels on the right: camera 55°, fov 38, distance solved for 1.4 m = 64 px at the center (12.1 m), 64 px ruler, and each hero's on-screen height MEASURED (a silhouette render of that hero alone, box of the dark pixels) |
| | **V Silhueta** (silhouette) | the same view in flat silhouettes (effects and UI off: replacement shader `CharacterFactory/Silhouette`, units on layer 30) |
| | **Transicoes** (transitions; editor) | the 6 Animator blend times of hero A or B, Aplicar (apply) live / Salvar JSON (save) (skill `character-engine` §2e) |
| | **tempo** (time) 1x · 1/2 · 1/4 · 1/10 · Pausa (Space) · **+1 quadro** (.) | +1 quadro = 1/30 s of game time, then pause again |
| | **hit-stop −/+**, **morte −/+** (death) | 20 ms per click |

Each hero's readout shows state, clip and frame (`attack 25/58`, 1-based as in Blender), the transition in progress
(`-> hit 63%`), `[HIT-STOP]` while frozen and, with G on, `na tela do jogo: L × A px` (on the game screen).

**Routine per new character** (the review package carries the captures, skill `character-review` §0):
1. Encostar → speed 1/10 → Atacar → `+1 quadro` until `[HIT-STOP]`: the frozen frame HAS to be the contact pose.
   Repeat from the other side (the victim holds its contact pose too).
2. 1x: Atacar and Dano a few times — does the strike have "weight"? Adjust hit-stop −/+ and note it if the character
   asks for another value.
3. Death ray standing, walking (Andar → Raio) and mid-attack (Atacar → Raio on the wind-up frame): the death starts
   clean from all three states (the 0.06–0.15 s transition must not pop).
4. Andar / Parar 5× in a row: stops on the right foot, without sliding (the treadmill does not move the unit; whatever
   moves is sliding).
5. Invocar 2–3× and Andar: the summoned units in different phases after 2 s.
6. G and V: on-screen height, the silhouette standing and in the key poses (pause on the wind-up, on contact, on the
   floor). Compare with ALVOR 113 × 123 px / OCASO 97 × 88 / FERRUGEM 72.
7. Retrato: face in the upper third, nothing in front of it.
8. Transitions: only if something popped or dragged in 3/4 — Aplicar, check, Salvar JSON, reimport, `MeasureTransitions`.

**By script** (`execute_code`, in Play): `var lab = Object.FindObjectOfType<CharacterFactory.CFDuelLab>();` →
`lab.SetOn(true)`, `Attack(side)`, `Hit(side)`, `Ray(side)`, `Summon(side)`, `Walk(side)`, `Close(bool)`, `Revive()`,
`Pair(±1)`, `SetSpeed(v)`, `Pause()`, `Step()`, `SetInset(bool)`, `SetSilhouette(bool)`, `TuneApply(side, tune)`,
`TuneSave(side, tune)`; reading: `lab.battle.LabState(side)`, `lab.HeroPx[side]`, `lab.HeroWidthPx[side]`,
`lab.CamDistance`, `lab.director.PairName`. `PairName` only updates on the next `Update`; and the pair may already have
advanced when the lab turns on (the previous duel ended between two calls): check the pair before acting.
- `Restart()` restarts the round count at 1: the director resets `_seenRound` in `Next/Prev/Repeat`, otherwise the new
  duel is not seen as new (wrong names and score).
- Capture with the panel and the inset: `ScreenCapture.CaptureScreenshot` (the inset is a camera with a viewport, so it
  comes out in the screen capture; in an RT of the main camera it does NOT).

## Hunter with a dash against the dummy (UIVO + TOCO)

`CFImporter.BuildHunt("Assets/Characters/<HOST>", "Assets/Characters/TOCO")` → `Assets/Scenes/<HOST>_Hunt.unity` with
`CFHunt`: idle → run → gallop → DASH (the character drives it: `PlayDash` / `DashStep`) that lands within reach → bites
(hit-stop 0.06 s) → odd round: the dummy falls, VICTORY, it sinks and another one rises; even round: one attack, HIT and
DEATH. The eight clips show up in ~19 s, with the clip's caption on screen (`captions`, pt-BR) and a side camera that
follows. The dummy's position is measured (skill `character-engine` §2f). To record: Play → `CFHunt.RestartFromTop()` +
`CFFrameRecorder` (fixed 60 fps, capture of the Game window with the caption) → `ffmpeg`. The user's scene that was open
before (if dirty) goes to a copy `<scene>_unsaved_<date>.unity` before `BuildHunt` — it opens a new scene.
