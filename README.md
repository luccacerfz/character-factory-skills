# Character Factory — Claude Code skills

Seven Claude Code skills that run a game-character pipeline end to end: an artist describes a character, and
Claude takes it from a one-page brief to a rigged, animated, measured prefab inside Unity. The look is a chunky
collectible mini in the Clash Royale or Warcraft Rumble style. All the work happens live in Blender, through MCP, so
every stage can be watched and filmed.

Six characters went through the pipeline with these skills:

- a dwarf with a two-handed hammer;
- an ice ogre;
- a sword-and-shield paladin;
- a necromancer who summons skeletons;
- an unarmed mining automaton;
- a wolf, the first quadruped.

The skills grew out of what broke along the way. Each rule comes with the number that proved it.

*Português: veja [abaixo](#português).*

## Install

```bash
claude plugin marketplace add luccacerfz/character-factory-skills
claude plugin install character-factory@character-factory-skills
```

Or copy `plugins/character-factory/skills/*` into your project's `.claude/skills/`.

## The skills

| Skill | Stage | Exit gate (a number, not an impression) |
|---|---|---|
| `character-factory` | Orchestrator: stage order, operating rules, which skill comes next | each stage passes only with its gate measured |
| `character-design` | One-page brief, design rules that fit animation, T-pose concept and multi-view 3D model in Tripo, props as separate objects | real T-pose, empty hands, a left/right marker; model gates `overhead`, `corridor`, `wrap` and `cuff` |
| `character-rig` | Import into live Blender, game mesh, landmarks measured on the mesh, Rigify, weights by region, props on their own bones, pose test | no stretched edges in the pose test; close-ups of shoulders, wrists and hips |
| `character-clips` | Base pose, attack, idle, walk, hit and death, plus specials: spells, projectiles, summons, spawn from the ground, quadruped gaits. Includes the 12 Disney principles checked at game size (64 px). | no mesh-to-mesh penetration (6 mm probe); nothing under the floor; loops close within 2 mm; all clips start on the same pose |
| `character-review` | Evidence pack: 6 fixed cameras, full-rate windows, 64 px silhouettes, weapon arcs, travel and contact tables. Three independent, read-only critic agents grade it: principles, body mechanics, tech art. | weighted score ≥ 9.5 with no blocker, or the artist's approval |
| `character-engine` | FBX export with a contract manifest, automatic Unity import (materials, events, Animator, LODs, additive FX), transitions that stop on the right foot | FBX round trip ≤ 0.05 cm; import `ok=True`; foot-slide table per transition |
| `character-show` | Several characters together: summoner and summons, a training dummy that topples, rounds with health, duels and battles. Game rules are simulated in Blender and mirrored in Unity. | planted foot ≤ 0.1 cm per frame in curves; the script of events matches in both engines |

## Read this before using them

- **The skills are in Portuguese (pt-BR).** Claude follows them fine. The tables, numbers and file names read the same
  in any language.
- **They drive a private toolchain that is not in this repo:**
  - Python tools: `factory/cf/*.py` and `factory/blender/*.py`;
  - shell scripts: `clip.sh`, `contacts.sh` and others;
  - the Unity C# namespace `CharacterFactory.*`.

  Read the skills as a playbook: stage order, gates with numbers, and lessons with the measurement behind them. Use
  them as a template for your own pipeline. Where a skill names a script, the paragraph around it says what the
  script measures and why.
- **External tools:**
  - Blender 4.5 with an MCP add-on;
  - Unity 6 with MCP for Unity;
  - Tripo, in the browser;
  - an image/video API for the per-character reference videos.

  Keys stay in a local `.env`. The skills tell Claude never to send personal data to outside services.

## Ideas worth stealing

- **Gates are numbers.** "The foot doesn't slide" becomes "planted foot ≤ 0.1 cm per frame", and "it reads" becomes
  "the body moves ≥ 2 px at 64 px". Most of the first character's rework came from a problem that stage 1 or 3 would
  have shown in seconds.
- **Critics see only evidence.** They never see the code. They are told to look first and then measure, and the
  image wins over the README. In the first rounds, the critics caught 7 or 8 wrong claims in the README each time.
- **Judge at game size.** The unit is about 64 px on screen, so 1 px is roughly 2 cm. A motion smaller than 2 px
  does not exist for the player.
- **No character names in the code.** Everything that differs between characters is data: landmarks, the clip
  recipe (`clip.json`) and the export manifest. The second character went from the brief to Unity in one session
  without touching the importer.

## License

MIT.

---

## Português

Sete skills do Claude Code que levam um personagem de jogo do brief de uma página até o prefab animado e medido
dentro da Unity. O estilo é o de uma miniatura atarracada, como em Clash Royale ou Warcraft Rumble. Tudo acontece ao
vivo no Blender, via MCP.

- **Instalação:** use os comandos da seção *Install* acima.
- **O que você precisa saber:**
  - as skills estão em português;
  - elas comandam ferramentas que não estão neste repositório (`factory/cf`, `factory/blender` e o C# da Unity).

  Leia as skills como um manual: a ordem dos estágios, os portões com número e as lições com a medida que as provou.
