"""LOOK of a texture pass: render the game mesh saved by blender/paint_bake.py (<maps>/game_scratch.blend) with a given albedo
under ONE fixed light rig, to A/B two albedos (original x painted). BACKGROUND Blender:
  Blender -b <maps>/game_scratch.blend --python blender/paint_look.py -- <albedo.png> <out_prefix> <lit|mini> [normal.png]
shader  lit   Principled, roughness 0.85 (what Unity's Standard shows)
        mini  40 % lit + 60 % unlit paint + a cool fresnel rim from the GEOMETRY normal (the collectible-mini look; through the
              normal map the rim draws a white line on every inner edge)
Shots: <prefix>_card.png (3/4 front, 15 deg above), _back.png, _game.png (game camera 60 deg above, character 64 px tall).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
ALB, OUT, SHADER = argv[:3]
NRM = argv[3] if len(argv) > 3 else None
game = bpy.data.objects["GAME"]
sc = bpy.context.scene
bb = [game.matrix_world @ Vector(c) for c in game.bound_box]
zmin = min(p.z for p in bb); zmax = max(p.z for p in bb); H = zmax - zmin
cx = sum(p.x for p in bb) / 8; cy = sum(p.y for p in bb) / 8

mat = game.material_slots[0].material
nt = mat.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
outn = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
tex = bsdf.inputs["Base Color"].links[0].from_node
while tex.type != 'TEX_IMAGE':
    tex = next(l.from_node for i in tex.inputs for l in i.links)
tex.image = bpy.data.images.load(ALB)
bsdf.inputs["Roughness"].default_value = 0.85
bsdf.inputs["Metallic"].default_value = 0.0
if NRM:
    nm = next((n for n in nt.nodes if n.type == 'NORMAL_MAP'), None)
    if nm is not None:
        nt_tex = nm.inputs["Color"].links[0].from_node
        img = bpy.data.images.load(NRM); img.colorspace_settings.name = 'Non-Color'
        nt_tex.image = img

if SHADER == "mini":
    # a collectible-mini look: most of the colour is the PAINT (unlit), a soft lit part and a rim on top
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Strength"].default_value = 1.0
    nt.links.new(tex.outputs["Color"], em.inputs["Color"])
    mix = nt.nodes.new("ShaderNodeMixShader"); mix.inputs[0].default_value = 0.40
    nt.links.new(em.outputs[0], mix.inputs[1]); nt.links.new(bsdf.outputs[0], mix.inputs[2])
    lw = nt.nodes.new("ShaderNodeLayerWeight"); lw.inputs["Blend"].default_value = 0.30
    # rim from the GEOMETRY normal (silhouette only): through the normal map it draws white lines on every inner edge
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.55; ramp.color_ramp.elements[1].position = 0.85
    nt.links.new(lw.outputs["Facing"], ramp.inputs[0])
    rim = nt.nodes.new("ShaderNodeEmission"); rim.inputs["Color"].default_value = (0.75, 0.85, 1.0, 1); rim.inputs["Strength"].default_value = 0.55
    add = nt.nodes.new("ShaderNodeAddShader")
    mrim = nt.nodes.new("ShaderNodeMixShader")
    blk = nt.nodes.new("ShaderNodeEmission"); blk.inputs["Strength"].default_value = 0.0
    nt.links.new(ramp.outputs[0], mrim.inputs[0]); nt.links.new(blk.outputs[0], mrim.inputs[1]); nt.links.new(rim.outputs[0], mrim.inputs[2])
    nt.links.new(mix.outputs[0], add.inputs[0]); nt.links.new(mrim.outputs[0], add.inputs[1])
    nt.links.new(add.outputs[0], outn.inputs["Surface"])

# ---- light rig (the same for every render)
for o in [o for o in bpy.data.objects if o.type in ('LIGHT', 'CAMERA')]:
    bpy.data.objects.remove(o, do_unlink=True)
if sc.world is None:
    sc.world = bpy.data.worlds.new("w")
sc.world.use_nodes = True
bg = sc.world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.62, 0.68, 0.80, 1); bg.inputs["Strength"].default_value = 0.55


def sun(name, rot, energy, color=(1, 1, 1)):
    d = bpy.data.lights.new(name, 'SUN'); d.energy = energy; d.color = color; d.angle = math.radians(8)
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o); o.rotation_euler = [math.radians(a) for a in rot]
    return o


sun("key", (50, 0, -35), 2.6, (1.0, 0.96, 0.90))          # front-left, above
sun("rim", (-55, 0, 150), 1.6, (0.75, 0.85, 1.0))         # behind
cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d); sc.collection.objects.link(cam); sc.camera = cam

sc.render.engine = 'CYCLES'
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = 'METAL'; pr.get_devices()
    for dv in pr.devices:
        dv.use = True
    sc.cycles.device = 'GPU'
except Exception:
    pass
sc.cycles.samples = 64; sc.cycles.use_denoising = True
sc.render.film_transparent = True
sc.view_settings.view_transform = 'Standard'; sc.view_settings.look = 'None'
sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'


def shot(tag, az, el, fov, px_h, frame=0.80):
    """camera on a sphere round the body's middle; `frame` = fraction of the image height the body takes"""
    cam_d.lens_unit = 'FOV'; cam_d.angle = math.radians(fov)
    dist = (H / frame) / (2 * math.tan(math.radians(fov) / 2))
    tgt = Vector((cx, cy, zmin + H * 0.5))
    a, e = math.radians(az), math.radians(el)
    cam.location = tgt + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (tgt - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.resolution_x = sc.render.resolution_y = px_h
    sc.render.resolution_percentage = 100
    sc.render.filepath = "%s_%s.png" % (OUT, tag)
    bpy.ops.render.render(write_still=True)


shot("card", -28, 15, 28, 900)
shot("back", 150, 15, 28, 900)
shot("game", -20, 60, 30, 80, frame=0.80)                  # 64 px of character in an 80 px frame
print("rendered", OUT)
