"""Reusable Blender paper-physics action primitives.

Import this module inside Blender scripts. The preset table is also safe to
import from ordinary Python for validation and tests.
"""

from __future__ import annotations

import math
from typing import Any


ACTION_PRESETS: dict[str, dict[str, Any]] = {
    "rigid-drop": {
        "kind": "rigid-body",
        "mass": 0.45,
        "friction": 0.58,
        "restitution": 0.18,
        "linear_damping": 0.12,
        "angular_damping": 0.18,
    },
    "paper-impact": {
        "kind": "rigid-body-collision",
        "substeps_per_frame": 12,
        "solver_iterations": 20,
        "planar_constraint": True,
    },
    "hinged-swing": {
        "kind": "hinge",
        "axis": "Y",
        "lower_degrees": -35,
        "upper_degrees": 35,
        "planar_constraint": True,
    },
}


def preset(action_id: str) -> dict[str, Any]:
    try:
        return dict(ACTION_PRESETS[action_id])
    except KeyError as exc:
        raise ValueError(f"unknown Blender paper action: {action_id}") from exc


def configure_active_rigid_body(
    bpy: Any,
    obj: Any,
    *,
    mass: float = 0.45,
    friction: float = 0.58,
    restitution: float = 0.18,
    linear_damping: float = 0.12,
    angular_damping: float = 0.18,
) -> Any:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.rigidbody.object_add()
    body = obj.rigid_body
    body.type = "ACTIVE"
    body.collision_shape = "BOX"
    body.mass = mass
    body.friction = friction
    body.restitution = restitution
    body.linear_damping = linear_damping
    body.angular_damping = angular_damping
    obj.select_set(False)
    return body


def configure_passive_rigid_body(
    bpy: Any,
    obj: Any,
    *,
    friction: float = 0.72,
    restitution: float = 0.16,
) -> Any:
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.rigidbody.object_add()
    body = obj.rigid_body
    body.type = "PASSIVE"
    body.collision_shape = "BOX"
    body.friction = friction
    body.restitution = restitution
    obj.select_set(False)
    return body


def add_planar_constraint(bpy: Any, obj: Any, name: str) -> Any:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=(obj.location.x, 0.0, obj.location.z))
    anchor = bpy.context.object
    anchor.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint = anchor.rigid_body_constraint
    constraint.type = "GENERIC"
    constraint.object1 = obj
    constraint.use_limit_lin_y = True
    constraint.limit_lin_y_lower = 0.0
    constraint.limit_lin_y_upper = 0.0
    constraint.use_limit_ang_x = True
    constraint.limit_ang_x_lower = 0.0
    constraint.limit_ang_x_upper = 0.0
    constraint.use_limit_ang_y = True
    constraint.limit_ang_y_lower = 0.0
    constraint.limit_ang_y_upper = 0.0
    return anchor


def add_hinge_constraint(
    bpy: Any,
    obj: Any,
    *,
    name: str,
    location: tuple[float, float, float],
    lower_degrees: float = -35,
    upper_degrees: float = 35,
) -> Any:
    bpy.ops.object.empty_add(type="PLAIN_AXES", location=location)
    anchor = bpy.context.object
    anchor.name = name
    bpy.ops.rigidbody.constraint_add()
    constraint = anchor.rigid_body_constraint
    constraint.type = "HINGE"
    constraint.object1 = obj
    constraint.use_limit_ang_z = True
    constraint.limit_ang_z_lower = math.radians(lower_degrees)
    constraint.limit_ang_z_upper = math.radians(upper_degrees)
    return anchor


def configure_world(bpy: Any, *, substeps_per_frame: int = 12, solver_iterations: int = 20) -> Any:
    scene = bpy.context.scene
    if scene.rigidbody_world is None:
        bpy.ops.rigidbody.world_add()
    world = scene.rigidbody_world
    world.substeps_per_frame = substeps_per_frame
    world.solver_iterations = solver_iterations
    world.time_scale = 1.0
    world.point_cache.frame_start = scene.frame_start
    world.point_cache.frame_end = scene.frame_end
    return world
