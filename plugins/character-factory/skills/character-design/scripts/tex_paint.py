"""PAINT a "hand-painted mini" albedo from a Tripo albedo + the paint maps of blender/paint_bake.py (rig-safe: same UV).
  .venv/bin/python cf/tex_paint.py <basecolor_orig.png> <maps_dir> <out.png> [size=2048] [k=v ...]
Light is painted INTO the colour, the way a miniature is painted: a fixed top-front key (wrapped), occlusion of the sculpt,
dark lines in the fine cavities, a soft highlight on the convex edges that face the key, a ground gradient; shadows go
darker + MORE saturated + cooler, lights go warmer. Everything in LINEAR light. Writes <out>.png, <out>_dbg.jpg (light value
| edge/cavity mask | result) and prints one JSON line.
Why it exists (measured on a brute, 2026-11-16): the Tripo 4K albedo holds <= 2K of information (4096 -> 2048 -> 4096:
PSNR 49 dB, 0.1 % of the texels off by more than 8/255) and 68 % of it is flat colour - resolution was never the missing
"detail". What reads as detail in a collectible-mini look is shape + this painted shading + the rim of the shader.
Tune per character with k=v (JSON values): edge=0.3 cavity=0.5 grad=0.2 'light=[0.2,-0.5,1]' deadzone=0.2 ...
"""
import json
import os
import sys

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

Image.MAX_IMAGE_PIXELS = None
ALB, MAPS, OUT = sys.argv[1:4]
M = 2048
P = {
    "light": [0.0, -0.45, 1.0],      # object space (Blender: Z up, the character faces -Y): top-front key
    "wrap": 0.55,                    # half-lambert wrap of the key
    "key_lo": 0.66, "key_hi": 1.16,  # value under the key: unlit side .. fully lit
    "ao_broad": 0.85, "ao_fine": 0.55, "ao_floor": 0.38,
    "form": 0.10,                    # broad curvature: bulges a little lighter, hollows darker
    "cavity": 0.42,                  # fine concave lines (cracks, seams, between fingers)
    "edge": 0.40,                    # screen highlight on fine convex edges that face the key
    "shadow_tint": [0.80, 0.86, 1.12], "light_tint": [1.07, 1.02, 0.90],
    "shadow_sat": 0.40, "sat": 1.10,
    "smooth_px": 1.8,                # blur of the curvature maps (kills the facet noise of the HD mesh)
    "deadzone": 0.15,                # fine curvature below this is surface grain, not a line: ignored (no speckle)
    "grad": 0.14,                    # ground gradient: the bottom of the figure this much darker than the top
}
for a in sys.argv[4:]:
    k, v = a.split("=", 1)
    if k == "size":
        M = int(v)
    else:
        P[k] = json.loads(v)


def lin(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def srgb(x):
    x = np.clip(x, 0, 1)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * x ** (1 / 2.4) - 0.055)


def sstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def load(fn, mode="RGB"):
    im = Image.open(fn).convert(mode)
    if im.size[0] != M:
        im = im.resize((M, M), Image.LANCZOS)
    return np.asarray(im).astype(np.float32) / 255.0


alb = lin(load(ALB))
emit = load(os.path.join(MAPS, "paint_emit.png"))
aof = load(os.path.join(MAPS, "ao_fine.png"), "L")
aob = load(os.path.join(MAPS, "ao_broad.png"), "L")
nrm = load(os.path.join(MAPS, "normal_obj.png")) * 2 - 1
used = (emit.max(axis=2) > 0.02) | (aob > 0.02)

cf = ndi.gaussian_filter(emit[..., 0] * 2 - 1, P["smooth_px"])
cf = np.sign(cf) * np.clip((np.abs(cf) - P["deadzone"]) / (1 - P["deadzone"]), 0, 1)
cb = ndi.gaussian_filter(emit[..., 1] * 2 - 1, P["smooth_px"] * 2)
nrm /= np.maximum(np.linalg.norm(nrm, axis=2, keepdims=True), 1e-6)
L = np.array(P["light"], dtype=np.float32); L /= np.linalg.norm(L)
d = nrm @ L
w = np.clip((d + P["wrap"]) / (1 + P["wrap"]), 0, 1)
w = w * w * (3 - 2 * w)

occ = (1 - P["ao_broad"] * (1 - aob)) * (1 - P["ao_fine"] * (1 - aof))
occ = P["ao_floor"] + (1 - P["ao_floor"]) * occ
cav = np.clip(-cf, 0, 1) ** 0.8
edge = np.clip(cf, 0, 1) ** 1.1
v = (P["key_lo"] + (P["key_hi"] - P["key_lo"]) * w) * occ * (1 + P["form"] * cb) * (1 - P["cavity"] * cav)
v = v * (1 - P["grad"] * (1 - sstep(0.0, 0.65, emit[..., 2])))
v = v / np.median(v[used]) * 0.97                    # the painted light keeps the albedo's overall key

sh = np.clip(1 - v, 0, 1)[..., None]                 # how deep in shadow
li = np.clip(v - 1, 0, 0.4)[..., None] / 0.4         # how far into light
col = alb * v[..., None]
col = col * (1 + (np.array(P["shadow_tint"], dtype=np.float32) - 1) * sh)
col = col * (1 + (np.array(P["light_tint"], dtype=np.float32) - 1) * li)
lum = (col * np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)).sum(axis=2, keepdims=True)
col = lum + (col - lum) * (P["sat"] + P["shadow_sat"] * sh)
col = np.clip(col, 0, None)
hl = (P["edge"] * edge * sstep(0.35, 0.85, w))[..., None]     # edges that face the key
warm = np.array([1.0, 0.96, 0.86], dtype=np.float32)
col = col + (warm * np.maximum(col.max(axis=2, keepdims=True), 0.25) * 1.15 - col) * np.clip(hl, 0, 1) * 0.6
out = srgb(col)
out[~used] = srgb(alb)[~used]
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(OUT)
# debug sheet: light value | cavity+edge | result
dbg = np.concatenate([np.repeat(np.clip(v / 1.4, 0, 1)[..., None], 3, 2),
                      np.stack([edge, np.zeros_like(cav), cav], axis=2), out], axis=1)
Image.fromarray((dbg * 255).astype(np.uint8)).resize((M * 3 // 3, M // 3), Image.LANCZOS).save(OUT.replace(".png", "_dbg.jpg"), quality=85)
print(json.dumps({"out": OUT, "size": M, "v_p5_p50_p95": [round(float(x), 3) for x in np.percentile(v[used], [5, 50, 95])],
                  "edge_texels_pct": round(100 * float((edge[used] > 0.3).mean()), 2),
                  "cavity_texels_pct": round(100 * float((cav[used] > 0.3).mean()), 2)}))
