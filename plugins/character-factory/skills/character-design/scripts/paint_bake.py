"""PAINT MAPS for the texture pass (rig-safe: same mesh, same UV, nothing of the character is touched): bake what a painter
needs from the Tripo 2 M HD sculpt onto the game mesh's Smart UV, straight from the two GLBs (they share one space).
  ao_fine / ao_broad   occlusion of the HD sculpt at 3 % and 30 % of the height (cavities / volumes)
  normal_obj           object-space normal of the HD sculpt (a fixed painted key light needs no tangent frame)
  paint_emit           R fine curvature (lines: wrinkle, seam, crack), G broad curvature (bulge / hollow), B height 0..1
  normal_tan           tangent normal (only to compare with the one Tripo ships in the game GLB)
  basecolor_orig.png   the game GLB's own albedo, written once as PNG (Tripo ships it as JPEG) - never overwritten
BACKGROUND Blender, no character .blend involved (run it before or after the rig; the live session is not touched):
  Blender -b --factory-startup --python blender/paint_bake.py -- <id>_hi.glb <id>_game.glb characters/<id>/model/tex/paint [size=2048]
Then: .venv/bin/python cf/tex_paint.py <outdir>/basecolor_orig.png <outdir> <outdir>/basecolor_painted.png
Measured (a brute, 1.95 M -> 18.9k tris, M-series GPU): 51 s for everything, 2 M import included.
"""
import os
import sys
import time

import bpy
import numpy as np

argv = sys.argv[sys.argv.index("--") + 1:]
HI, GAME, OUT = argv[:3]
SIZE = int(argv[3]) if len(argv) > 3 else 2048
os.makedirs(OUT, exist_ok=True)
T0 = time.time()


def log(*a):
    print("[paint_bake %6.1fs]" % (time.time() - T0), *a, flush=True)


bpy.ops.wm.read_factory_settings(use_empty=True)


def imp(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=path)
    new = [o for o in bpy.data.objects if o not in before and o.type == 'MESH']
    o = max(new, key=lambda x: len(x.data.polygons))
    bpy.context.view_layer.objects.active = o
    for x in bpy.data.objects:
        x.select_set(x is o)
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return o


game = imp(GAME); game.name = "GAME"
log("game", len(game.data.polygons), "faces")
_orig = os.path.join(OUT, "basecolor_orig.png")
if not os.path.exists(_orig):                                   # the ORIGINAL is written once and never again
    _b = next(n for n in game.material_slots[0].material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    _t = _b.inputs["Base Color"].links[0].from_node
    while _t.type != 'TEX_IMAGE':
        _t = next(l.from_node for i in _t.inputs for l in i.links)
    _w, _h = _t.image.size
    _px = np.empty(_w * _h * 4, dtype=np.float32); _t.image.pixels.foreach_get(_px)
    _n = bpy.data.images.new("basecolor_orig", _w, _h, alpha=False)
    _n.colorspace_settings.name = _t.image.colorspace_settings.name
    _n.pixels.foreach_set(_px); _n.filepath_raw = _orig; _n.file_format = 'PNG'; _n.save()
    bpy.data.images.remove(_n)
    log("albedo", _w, "x", _h, "->", _orig)
hi = imp(HI); hi.name = "HI"
log("hi", len(hi.data.polygons), "faces")

# ------------------------------------------------------------------ curvature on the HD vertices (numpy, welded)
me = hi.data
nv = len(me.vertices)
P = np.zeros(nv * 3); me.vertices.foreach_get("co", P); P = P.reshape(-1, 3)
Nn = np.zeros(nv * 3); me.vertices.foreach_get("normal", Nn); Nn = Nn.reshape(-1, 3)
H = float(np.ptp(P[:, 2]))
key = np.round(P / (H * 2e-5)).astype(np.int64)
_, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
inv = inv.ravel()
nu = len(first)
E = np.zeros(len(me.edges) * 2, dtype=np.int32); me.edges.foreach_get("vertices", E); E = inv[E.reshape(-1, 2)]
E = E[E[:, 0] != E[:, 1]]
log("welded", nv, "->", nu, "verts;", len(E), "edges; H = %.3f" % H)
Pu = P[first].copy()
# welded normal = mean of the split copies
Nu = np.stack([np.bincount(inv, weights=Nn[:, k], minlength=nu) for k in range(3)], axis=1)
Nu /= np.maximum(np.linalg.norm(Nu, axis=1, keepdims=True), 1e-9)
deg = np.bincount(E[:, 0], minlength=nu) + np.bincount(E[:, 1], minlength=nu)
deg = np.maximum(deg, 1)[:, None].astype(np.float64)
elen = float(np.linalg.norm(Pu[E[:, 0]] - Pu[E[:, 1]], axis=1).mean())


def smooth(V, iters):
    for _ in range(iters):
        A = np.stack([np.bincount(E[:, 0], weights=V[E[:, 1], k], minlength=nu)
                      + np.bincount(E[:, 1], weights=V[E[:, 0], k], minlength=nu) for k in range(3)], axis=1)
        V = 0.5 * V + 0.5 * A / deg
    return V


K_FINE, K_BROAD = 24, 220                                   # ~ edge * sqrt(k/2): the scale of a crack / of a volume
Vf = smooth(Pu, K_FINE)
cf = np.einsum("ij,ij->i", Nu, Pu - Vf)
Vb = smooth(Vf, K_BROAD - K_FINE)
cb = np.einsum("ij,ij->i", Nu, Pu - Vb)
sf = float(np.percentile(np.abs(cf), 97)); sb = float(np.percentile(np.abs(cb), 97))
log("mean edge %.2f mm of H=1; curv p97 fine %.3g broad %.3g" % (1000 * elen / H, sf / H, sb / H))
col = np.ones((nv, 4), dtype=np.float32)
col[:, 0] = np.clip(0.5 + 0.5 * cf[inv] / sf, 0, 1)
col[:, 1] = np.clip(0.5 + 0.5 * cb[inv] / sb, 0, 1)
col[:, 2] = (P[:, 2] - P[:, 2].min()) / H
attr = me.color_attributes.new("cf_paint", 'FLOAT_COLOR', 'POINT')
attr.data.foreach_set("color", col.ravel())

# HD material: emission of the attribute (EMIT bake) - AO / NORMAL bakes ignore the shader
hm = bpy.data.materials.new("HI_paint"); hm.use_nodes = True
nt = hm.node_tree; nt.nodes.clear()
a = nt.nodes.new("ShaderNodeAttribute"); a.attribute_name = "cf_paint"; a.attribute_type = 'GEOMETRY'
em = nt.nodes.new("ShaderNodeEmission"); o = nt.nodes.new("ShaderNodeOutputMaterial")
nt.links.new(a.outputs["Color"], em.inputs["Color"]); nt.links.new(em.outputs[0], o.inputs["Surface"])
hi_mat_orig = hi.material_slots[0].material
hi.material_slots[0].material = hm

# ------------------------------------------------------------------ bake setup
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for d in pr.devices:
        d.use = True
    sc.cycles.device = 'GPU'
except Exception as ex:                                        # CPU is fine, only slower
    log("gpu off:", ex)
sc.cycles.use_denoising = False
if sc.world is None:
    sc.world = bpy.data.worlds.new("bake")
bk = sc.render.bake
bk.use_selected_to_active = True
bk.cage_extrusion = 0.008 * H
bk.max_ray_distance = 0.02 * H
bk.margin = 16
bk.use_clear = True

gm = game.material_slots[0].material
gnt = gm.node_tree
node = gnt.nodes.new("ShaderNodeTexImage")
gnt.nodes.active = node
for x in bpy.data.objects:
    x.select_set(False)
hi.select_set(True); game.select_set(True)
bpy.context.view_layer.objects.active = game


def bake(tag, btype, samples, **kw):
    img = bpy.data.images.new(tag, SIZE, SIZE, alpha=False, float_buffer=False)
    img.colorspace_settings.name = 'Non-Color'
    node.image = img; gnt.nodes.active = node
    sc.cycles.samples = samples
    t = time.time()
    bpy.ops.object.bake(type=btype, **kw)
    fn = os.path.join(OUT, tag + ".png")
    img.filepath_raw = fn; img.file_format = 'PNG'; img.save()
    log("baked", tag, "%.1fs" % (time.time() - t))


bake("paint_emit", 'EMIT', 4)                                  # R curv fine, G curv broad, B height
sc.world.light_settings.distance = 0.03 * H
bake("ao_fine", 'AO', 48)
sc.world.light_settings.distance = 0.30 * H
bake("ao_broad", 'AO', 48)
bake("normal_obj", 'NORMAL', 4, normal_space='OBJECT')
bake("normal_tan", 'NORMAL', 4, normal_space='TANGENT')
gnt.nodes.remove(node)

# save the game mesh + its textures for the render run (HD dropped: the .blend stays small)
bpy.data.objects.remove(hi, do_unlink=True)
for im in bpy.data.images:
    if im.packed_file is None and im.source == 'FILE' and not im.filepath:
        pass
bpy.ops.file.pack_all()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "game_scratch.blend"), compress=True)
log("done; H", H)
