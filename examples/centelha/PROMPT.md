# CENTELHA — the prompts that built her

CENTELHA ("spark") is a short WoW-style mage. Her signature spell is the light-and-lightning version of an ice area
spell: a sigil falls from the sky, lightning rises from the floor, and glass crystals pin a pack of skeletons from
below. She was the seventh character through the pipeline. She went from an empty folder to an approved Unity scene in
about 17 hours of `/loop`, with a 1.2 m body, a one-handed staff, living eyes and six clips (idle, walk, cast, hit,
death, victory).

Below are the user's prompts, verbatim (pt-BR, typos included), each with an English translation. Only the reference
video's path was replaced. Prompts about operating the machine (restarting Blender, reconnecting MCP) are left out.

## The reference

A short screen recording (a few seconds) of a blizzard-style ice area spell from a game: the caster raises the staff,
a sigil lands on the ground, and ice locks the enemies in place. It is NOT in this repo. Use any clip of an area spell
you want to translate into another element. The pipeline reads it for timing and staging only, never for the design.

## 1. The request

As typed (it was queued while another character was still in progress):

> QUANDO TERMINAR. CRIE UMA MAGA `<reference-video.mp4>` ESTILO WOW E que solta esta animação de gelo mas como se fosse
> de luz e eletricidade... dando um efeito de stun prendendo os inimigos em baixo. Siga todo nosso workflow tripo e de
> animacao e coloque ela contra 5 esqueletinhos e ela soltando essa magia. Nao pare ate ficar nota >=9.5 /loop

*WHEN YOU'RE DONE. CREATE A WOW-STYLE MAGE that casts this ice animation, but as if it were light and electricity...
giving a stun effect that traps the enemies from below. Follow our whole Tripo and animation workflow and put her
against 5 little skeletons, casting this spell. Don't stop until the score is >= 9.5.*

As the `/loop` command that ran it (self-paced, re-entered on every wake-up):

```text
/loop CRIE UMA MAGA (<reference-video.mp4>) ESTILO WOW que solta a animação de gelo do vídeo mas como se fosse de LUZ e
ELETRICIDADE, dando um efeito de STUN prendendo os inimigos por baixo. Seguir todo o workflow Tripo e de animação da
Character Factory, colocar ela contra 5 esqueletinhos (OSSINHO) soltando essa magia. Não parar até nota >= 9.5. Estado
das rodadas: factory/characters/centelha/loop.json
```

The last sentence matters. Each wake-up starts with only the prompt, so the round's plan, progress and scores live in
`loop.json`, and every wake-up reads it first. `OSSINHO` is the skeleton made earlier with the necromancer (OCASO).

## 2. Follow-ups during the loop

Each one became a round of its own: recorded in `loop.json`, built, measured, and shown to the next critics.

| When | Prompt (verbatim) | Translation | What it became |
|---|---|---|---|
| model ready | trabalhe bem nos olho e sua animacao para nao ficar estatico. | *work well on the eyes and their animation so they don't look static.* | one leaf bone per eye on a single textured mesh: blinks, squints, glances that lead the head (`character-rig` §0, `character-clips` §6b "Eyes") |
| first scene | Esta faltando cair do ceu a magia | *the spell falling from the sky is missing* | three sky beats tied to existing poses: the call, a spear on the strike frame, a rain of impacts (`character-clips` §2h) |
| round 12 | DEpois disso, melhore o vfx do ataque dela criando assets no tripo que ajudem isto e tambem, na spell de chuva dela, tambem criar mais assets dos crystais de luz caindo. | *after that, improve her attack VFX by creating assets in Tripo that help with it, and also, in her rain spell, create more assets of falling light crystals.* | Tripo effect assets: a crystal cage and falling shards (`character-design` §5c) |
| round 13 | os cristais tem que que prendem os esqueletos e que caem do ceu tem que ser muito mais clean e cartonistico que nem dp video de referencia da spell de de nevasca | *the crystals that trap the skeletons and that fall from the sky have to be much cleaner and more cartoony, like in the reference video of the blizzard spell* | procedural crystals with flat facets and a 3-tone atlas, replacing the scans (`character-design` §5c) |
| round 14 | os cristais que prendem tem que ser mais translucidos e cartunisticos | *the trapping crystals have to be more translucent and cartoony* | cartoon glass: a translucent core, an opaque outline, and a multiply + add shader in Unity (`character-engine` §2g) |
| round 15 | acho que ja esta muito bom pode parar | *I think it's already very good, you can stop* | loop stopped, critics cancelled, approval recorded in `state.json → approved` |

## 3. What the loop did each round

1. Read `loop.json`, then fix the previous verdict's items in order: blockers, then majors on the attack, then what all
   three critics repeated. Each fix is measured (cm, m/s, px at game size), not just "keyed".
2. Rebuild the clips, export to Unity, rebuild the spell scene (`CFSpellBuilder.BuildSpell`) and record the takes.
3. Build the evidence pack and a README whose numbers are printed by a script (`character-review` §1).
4. Launch three read-only critics (principles, body mechanics, tech art); weighted score 0.40 / 0.35 / 0.25.
5. Write the score to `state.json`, then `ScheduleWakeup` for the next round.

Rounds 1–6 built her: concept, model, rig, clips, spell, Unity scene. The critics graded from round 7 on:

| Critic round | Principles | Mechanics | Tech | Weighted |
|---|---|---|---|---|
| 7 | 7.6 | 7.5 | 7.8 | 7.62 (1 blocker) |
| 8 | 8.0 | 8.4 | 8.1 | 8.16 |
| 9 | 8.1 | 8.6 | 8.5 | 8.375 |
| 10 | 8.4 | 8.6 | 8.5 | 8.495 |
| 11 | 8.5 | 8.9 | 8.6 | 8.665 |
| 12 | 8.6 | 9.0 | 8.4 | 8.69 |

The user approved at the round-15 build, during critic round 13, which was stopped without a score. The skills say
that the artist's eye is the final gate: the score exists to find defects, not to argue with the person who approved.

Tripo: 376 credits of a 5,000 budget. That covered the concept, the views, the mage, the staff, remesh + smart UV +
texture, and the two effect assets.

## 4. Reusing it

Swap the element, the target and the reference; keep the structure:

```text
/loop Create a <style> <class> (<reference-video>) that casts the <element A> spell from the video as <element B>,
with <gameplay effect>. Follow the whole Character Factory Tripo and animation workflow, put them against <N> <unit>
casting the spell. Don't stop until score >= 9.5. Round state: factory/characters/<id>/loop.json
```

- Name an existing unit as the target, so the scene can be built from manifests.
- Give the state file, so a self-paced loop survives every wake-up and every context compaction.
- Send style changes in the middle of the loop as short follow-ups. Each becomes a round the critics see.
