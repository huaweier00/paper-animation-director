#!/usr/bin/env python3
"""Fail closed unless every ordered shot and the final master are release-bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from audit_audio_mode import load_json as load_audio_contract
from audit_audio_mode import validate_audio_contract
from audit_medium_contract import load_json as load_medium_contract
from audit_medium_contract import validate_medium_contract
from audit_pose_reuse import validate_pose_reuse
from audit_shot_release import load_json as load_shot_release
from audit_shot_release import validate as validate_shot_release
from validate_story_manifest import validate_manifest


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVIEW_FIELDS = (
    "sequence_continuity",
    "performance_regression",
    "sound_picture",
    "phone_size",
    "ending",
)


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def load_json(path: Path, label: str = "release index") -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"{label} does not exist: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} invalid JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{label} root must be an object")
    return data


def project_path(project: Path, value: Any, label: str) -> Path:
    if not nonempty(value):
        raise ValueError(f"{label}: expected a local project path")
    raw = str(value)
    if raw.startswith(("http://", "https://", "//", "data:")):
        raise ValueError(f"{label}: runtime-network paths are forbidden")
    path = (project / raw.removeprefix("./")).resolve()
    try:
        path.relative_to(project.resolve())
    except ValueError as exc:
        raise ValueError(f"{label}: path escapes the project root") from exc
    return path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_release_index(
    data: dict[str, Any],
    *,
    project: Path,
    ffprobe: str = "ffprobe",
) -> tuple[list[str], list[str], dict[str, Any]]:
    errors: list[str] = []
    warnings: list[str] = []
    derived: dict[str, Any] = {"released_shots": 0}

    if data.get("schema_version") != 1:
        errors.append("schema_version: expected 1")
    if data.get("phase") != "release":
        errors.append("phase: expected release")
    if data.get("decision") != "approved":
        errors.append("decision: expected approved")

    paths: dict[str, Path] = {}
    for field in ("story_manifest", "medium_contract", "audio_contract"):
        try:
            path = project_path(project, data.get(field), field)
        except ValueError as exc:
            errors.append(str(exc))
            continue
        paths[field] = path
        if not path.is_file():
            errors.append(f"{field}: file does not exist: {path}")

    manifest: dict[str, Any] | None = None
    medium: dict[str, Any] | None = None
    audio: dict[str, Any] | None = None
    if paths.get("story_manifest", Path()).is_file():
        try:
            manifest = load_json(paths["story_manifest"], "story manifest")
            findings = validate_manifest(manifest, project_dir=project, phase="release")
            errors.extend(
                f"story_manifest.{item['path']}: {item['message']}"
                for item in findings
                if item.get("severity") == "error"
            )
            warnings.extend(
                f"story_manifest.{item['path']}: {item['message']}"
                for item in findings
                if item.get("severity") == "warning"
            )
        except ValueError as exc:
            errors.append(str(exc))
    if paths.get("medium_contract", Path()).is_file():
        try:
            medium = load_medium_contract(paths["medium_contract"])
            medium_errors, medium_warnings = validate_medium_contract(medium, phase="release")
            errors.extend(f"medium_contract: {message}" for message in medium_errors)
            warnings.extend(f"medium_contract: {message}" for message in medium_warnings)
        except ValueError as exc:
            errors.append(str(exc))
    if paths.get("audio_contract", Path()).is_file():
        try:
            audio = load_audio_contract(paths["audio_contract"])
        except ValueError as exc:
            errors.append(str(exc))

    project_id = data.get("project_id")
    if not nonempty(project_id):
        errors.append("project_id: required")
    if manifest is not None and project_id != manifest.get("project"):
        errors.append("project_id: must match story-manifest.json project")
    if medium is not None and project_id != medium.get("project_id"):
        errors.append("project_id: must match medium-contract.json project_id")
    if audio is not None and project_id != audio.get("project_id"):
        errors.append("project_id: must match audio-contract.json project_id")

    ordered = data.get("ordered_shots")
    if not isinstance(ordered, list) or not ordered:
        errors.append("ordered_shots: expected a non-empty list")
        ordered = []
    declared_ids = [item.get("shot_id") for item in ordered if isinstance(item, dict)]
    manifest_ids = []
    if manifest is not None:
        manifest_ids = [
            scene.get("id")
            for scene in manifest.get("scenes", [])
            if isinstance(scene, dict) and nonempty(scene.get("id"))
        ]
        if declared_ids != manifest_ids:
            errors.append(
                "ordered_shots: must exactly match story-manifest scene order; "
                f"expected {manifest_ids}, got {declared_ids}"
            )

    for index, item in enumerate(ordered):
        prefix = f"ordered_shots[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: expected object")
            continue
        shot_id = item.get("shot_id")
        if not nonempty(shot_id):
            errors.append(f"{prefix}.shot_id: required")
        try:
            release_path = project_path(project, item.get("release"), f"{prefix}.release")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if not release_path.is_file():
            errors.append(f"{prefix}.release: file does not exist: {release_path}")
            continue
        digest = item.get("release_sha256")
        if not isinstance(digest, str) or not SHA256_RE.match(digest):
            errors.append(f"{prefix}.release_sha256: expected a lowercase SHA-256")
        elif sha256(release_path) != digest:
            errors.append(f"{prefix}.release_sha256: evidence is stale because the release record changed")
        try:
            release_data = load_shot_release(release_path)
            if release_data.get("schema_version") != 5:
                errors.append(f"{prefix}.release: final film requires shot-release schema_version 5")
            if release_data.get("shot_id") != shot_id:
                errors.append(f"{prefix}.release.shot_id: must match the ordered shot id")
            release_errors, release_warnings = validate_shot_release(
                release_data,
                release_path.parent,
                strict=True,
                require_approved=True,
                check_paths=True,
            )
            errors.extend(f"{prefix}.release: {message}" for message in release_errors)
            warnings.extend(f"{prefix}.release: {message}" for message in release_warnings)
            if not release_errors:
                derived["released_shots"] += 1
        except ValueError as exc:
            errors.append(f"{prefix}.release: {exc}")

    pose_errors, pose_warnings, pose_derived = validate_pose_reuse(project)
    errors.extend(f"pose_reuse: {message}" for message in pose_errors)
    warnings.extend(f"pose_reuse: {message}" for message in pose_warnings)
    derived["pose_reuse"] = pose_derived

    master = data.get("master")
    if not isinstance(master, dict):
        errors.append("master: required object")
        master = {}
    master_path: Path | None = None
    try:
        master_path = project_path(project, master.get("path"), "master.path")
    except ValueError as exc:
        errors.append(str(exc))
    if master_path is not None:
        if not master_path.is_file():
            errors.append(f"master.path: file does not exist: {master_path}")
        else:
            digest = master.get("sha256")
            if not isinstance(digest, str) or not SHA256_RE.match(digest):
                errors.append("master.sha256: expected a lowercase SHA-256")
            elif sha256(master_path) != digest:
                errors.append("master.sha256: evidence is stale because the master changed")
    if master.get("decode_verified") is not True:
        errors.append("master.decode_verified: expected true")
    if master.get("audio_verified") is not True:
        errors.append("master.audio_verified: expected true")
    if audio is not None and medium is not None:
        audio_errors, audio_warnings, audio_derived = validate_audio_contract(
            audio,
            medium=medium,
            phase="release",
            project=project,
            video=master_path,
            ffprobe=ffprobe,
        )
        errors.extend(f"audio_contract: {message}" for message in audio_errors)
        warnings.extend(f"audio_contract: {message}" for message in audio_warnings)
        derived["audio"] = audio_derived

    review = data.get("review")
    if not isinstance(review, dict):
        errors.append("review: required object")
        review = {}
    for field in REVIEW_FIELDS:
        if review.get(field) != "approved":
            errors.append(f"review.{field}: expected approved")

    if data.get("decision") == "approved" and errors:
        errors.append("decision: cannot remain approved while final release checks fail")
    return errors, warnings, derived


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("index", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--ffprobe", default="ffprobe")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    index = args.index.expanduser().resolve()
    project = args.project.expanduser().resolve() if args.project else index.parent
    try:
        data = load_json(index)
        errors, warnings, derived = validate_release_index(data, project=project, ffprobe=args.ffprobe)
    except (OSError, ValueError) as exc:
        errors, warnings, derived = [str(exc)], [], {}
    result = {
        "ok": not errors and (not warnings or not args.strict),
        "errors": errors,
        "warnings": warnings,
        "derived": derived,
    }
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for warning in warnings:
            print(f"WARNING: {warning}")
        for error in errors:
            print(f"ERROR: {error}")
        print("PASS: final film may be released" if result["ok"] else "FAIL: final film remains locked")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
