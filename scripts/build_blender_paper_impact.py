#!/usr/bin/env python3
"""Build, bake, save, and render a deterministic 2.5D paper-impact Blender scene.

Run this script through Blender:

    blender --background --factory-startup --python build_blender_paper_impact.py -- \
      --output /absolute/output/directory
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

# Blender's --python launcher does not consistently add the launched script's
# directory to sys.path. Resolve the adjacent reusable action module explicitly
# so the same command works from any current working directory.
SCRIPT_DIRECTORY = Path(__file__).resolve().parent
if str(SCRIPT_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIRECTORY))

from blender_action_library import (
    add_planar_constraint,
    configure_active_rigid_body,
    configure_passive_rigid_body,
    configure_world,
)


def script_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--fps", type=int, default=24)
    parser.add_argument("--frames", type=int, default=48)
    parser.add_argument("--samples", type=int, default=32)
    return parser.parse_args(argv)


def material(name: str, rgba: tuple[float, float, float, float], roughness: float = 0.8) -> bpy.types.Material:
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = rgba
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def cube(
    name: str,
    location: tuple[float, float, float],
    dimensions: tuple[float, float, float],
    mat: bpy.types.Material,
    bevel: float = 0.04,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new("Paper edge softness", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    obj.data.materials.append(mat)
    return obj


def sphere(
    name: str,
    location: tuple[float, float, float],
    scale: tuple[float, float, float],
    mat: bpy.types.Material,
) -> bpy.types.Object:
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj


def parent_preserving_world(child: bpy.types.Object, parent: bpy.types.Object) -> None:
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def aim_camera(camera: bpy.types.Object, target: tuple[float, float, float]) -> None:
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def configure_scene(args: argparse.Namespace) -> tuple[bpy.types.Object, bpy.types.Object]:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for block in list(datablocks):
            if block.users == 0:
                datablocks.remove(block)

    scene = bpy.context.scene
    render_engines = {item.identifier for item in scene.render.bl_rna.properties["engine"].enum_items}
    scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in render_engines else "BLENDER_EEVEE"
    scene.render.resolution_x = args.width
    scene.render.resolution_y = args.height
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.fps = args.fps
    scene.render.fps_base = 1.0
    scene.frame_start = 1
    scene.frame_end = args.frames
    scene.render.filepath = str(args.output / "frames" / "frame_")
    scene.render.image_settings.color_depth = "8"
    scene.render.image_settings.compression = 35
    scene.render.use_file_extension = True
    scene.render.image_settings.color_mode = "RGBA"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = args.samples
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        try:
            scene.view_settings.look = "Medium High Contrast"
        except TypeError:
            pass

    scene.world.color = (0.025, 0.018, 0.012)
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.025, 0.018, 0.012, 1.0)
    background.inputs["Strength"].default_value = 0.25

    paper = material("Warm handmade paper", (0.73, 0.47, 0.22, 1.0), 0.93)
    ink = material("Oxide ink", (0.18, 0.055, 0.035, 1.0), 0.88)
    edge = material("Cut paper edge", (0.91, 0.72, 0.43, 1.0), 0.96)
    ground_mat = material("Ground paper", (0.34, 0.15, 0.07, 1.0), 1.0)

    ground = cube("Passive paper ground", (0.0, 0.35, -0.22), (10.0, 2.2, 0.35), ground_mat, 0.06)
    configure_passive_rigid_body(bpy, ground)

    card = cube("Active illustrated paper card", (-1.25, 0.0, 3.5), (3.15, 0.11, 1.68), paper, 0.09)
    configure_active_rigid_body(bpy, card, restitution=0.28)

    # A simple high-contrast horse-and-rider paper motif. These shallow pieces
    # remain children of the simulated card and make rotation/contact readable.
    body = sphere("Horse motif body", (-1.38, -0.09, 3.52), (0.78, 0.035, 0.34), ink)
    neck = cube("Horse motif neck", (-0.66, -0.09, 3.78), (0.22, 0.055, 0.62), ink, 0.06)
    neck.rotation_euler[1] = math.radians(-18)
    head = sphere("Horse motif head", (-0.49, -0.09, 4.0), (0.28, 0.035, 0.2), ink)
    rider = sphere("Rider motif head", (-1.25, -0.09, 4.03), (0.17, 0.035, 0.17), edge)
    torso = cube("Rider motif torso", (-1.23, -0.09, 3.78), (0.35, 0.055, 0.42), edge, 0.08)
    for index, x in enumerate((-1.83, -1.25, -0.84)):
        leg = cube(f"Horse motif leg {index + 1}", (x, -0.09, 3.18), (0.12, 0.055, 0.48), ink, 0.04)
        parent_preserving_world(leg, card)
    for motif in (body, neck, head, rider, torso):
        parent_preserving_world(motif, card)
    # Rotate only after parenting so the ink motif is physically attached to
    # the same paper plane from frame one.
    card.rotation_euler = (0.0, 0.0, math.radians(18))
    add_planar_constraint(bpy, card, "Card 2.5D plane constraint")

    # A second rigid paper shard strikes the card shortly before ground contact,
    # yielding an actual baked multi-body collision rather than a keyframed fall.
    shard = cube("Active paper shard", (-0.25, 0.04, 5.7), (1.05, 0.09, 0.48), edge, 0.07)
    shard.rotation_euler = (0.0, 0.0, math.radians(-31))
    configure_active_rigid_body(
        bpy,
        shard,
        mass=0.2,
        friction=0.44,
        restitution=0.36,
        linear_damping=0.08,
        angular_damping=0.1,
    )
    add_planar_constraint(bpy, shard, "Shard 2.5D plane constraint")

    bpy.ops.object.camera_add(location=(0.1, -12.5, 3.05))
    camera = bpy.context.object
    camera.name = "Locked orthographic camera"
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 7.1
    camera.data.lens = 55
    aim_camera(camera, (0.0, 0.0, 2.0))
    scene.camera = camera

    bpy.ops.object.light_add(type="AREA", location=(-3.5, -4.5, 7.5))
    key = bpy.context.object
    key.name = "Softbox key"
    key.data.energy = 950
    key.data.shape = "DISK"
    key.data.size = 5.0
    aim_camera(key, (0.0, 0.0, 1.4))

    bpy.ops.object.light_add(type="AREA", location=(4.0, -1.5, 4.3))
    fill = bpy.context.object
    fill.name = "Warm rim"
    fill.data.energy = 520
    fill.data.color = (1.0, 0.36, 0.15)
    fill.data.size = 3.2
    aim_camera(fill, (0.0, 0.0, 1.7))

    configure_world(bpy, substeps_per_frame=12, solver_iterations=20)
    return card, shard


def bake_save_render(args: argparse.Namespace, card: bpy.types.Object, shard: bpy.types.Object) -> None:
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "frames").mkdir(parents=True, exist_ok=True)
    scene = bpy.context.scene
    blend_path = args.output / "paper-impact.blend"
    # Save first so the baked cache has a stable source owner. Blender 5.2.0 on
    # macOS can crash while toggling rigid-body use_disk_cache in background
    # mode, so the portable contract stores the baked cache in the .blend.
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))
    scene.frame_set(scene.frame_start)
    bpy.ops.ptcache.free_bake_all()
    bpy.ops.ptcache.bake_all(bake=True)
    scene.frame_set(scene.frame_end)
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_path))

    proof_frames = sorted(
        {
            scene.frame_start,
            max(scene.frame_start, round(args.frames * 0.42)),
            max(scene.frame_start, round(args.frames * 0.68)),
            scene.frame_end,
        }
    )
    positions: dict[str, dict[str, list[float]]] = {}
    for frame in proof_frames:
        scene.frame_set(frame)
        positions[str(frame)] = {
            "card": [round(value, 6) for value in card.matrix_world.translation],
            "shard": [round(value, 6) for value in shard.matrix_world.translation],
        }
    scene.frame_set(scene.frame_start)

    build_record = {
        "schema_version": 1,
        "engine": "blender",
        "scene": "paper-impact-2.5d",
        "frame_start": scene.frame_start,
        "frame_end": scene.frame_end,
        "frame_count": args.frames,
        "fps": args.fps,
        "width": args.width,
        "height": args.height,
        "film_transparent": bool(scene.render.film_transparent),
        "physics": {
            "kind": "rigid-body",
            "baked": bool(scene.rigidbody_world.point_cache.is_baked),
            "cache_external": bool(scene.rigidbody_world.point_cache.use_disk_cache),
            "cache_preserved_in_blend": True,
            "substeps_per_frame": scene.rigidbody_world.substeps_per_frame,
            "solver_iterations": scene.rigidbody_world.solver_iterations,
        },
        "proof_transforms": positions,
    }
    (args.output / "blender-build.json").write_text(
        json.dumps(build_record, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    scene.render.filepath = str(args.output / "frames" / "frame_")
    bpy.ops.render.render(animation=True)


def main() -> None:
    args = script_args()
    if args.width <= 0 or args.height <= 0 or args.fps <= 0 or args.frames < 12:
        raise SystemExit("width, height, and fps must be positive; frames must be at least 12")
    card, shard = configure_scene(args)
    bake_save_render(args, card, shard)


if __name__ == "__main__":
    main()
