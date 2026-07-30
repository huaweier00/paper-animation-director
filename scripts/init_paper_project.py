#!/usr/bin/env python3
"""Initialize a paper-animation HyperFrames project from a story manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from validate_story_manifest import validate_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    manifest = args.manifest.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if output.exists() and any(output.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty output directory: {output}")
    data = json.loads(manifest.read_text(encoding="utf-8"))
    errors = [item for item in validate_manifest(data) if item["severity"] == "error"]
    if errors:
        details = "\n".join(f"{item['path']}: {item['message']}" for item in errors)
        raise SystemExit(f"Manifest has blocking errors:\n{details}")

    skill_root = Path(__file__).resolve().parent.parent
    template = skill_root / "assets" / "project-template"
    output.mkdir(parents=True, exist_ok=True)
    for source in template.iterdir():
        if source.name == "manifests":
            continue
        target = output / source.name
        if source.is_dir():
            shutil.copytree(source, target, dirs_exist_ok=True)
        else:
            shutil.copy2(source, target)

    package_path = output / "package.json"
    package_path.write_text(package_path.read_text(encoding="utf-8").replace("__PROJECT_ID__", data["project"]), encoding="utf-8")
    (output / "compositions" / "scene-template.html").unlink(missing_ok=True)
    shutil.copy2(manifest, output / "story-manifest.json")
    for relative in (
        "assets/references/characters",
        "assets/source-atlases",
        "assets/characters",
        "assets/backgrounds",
        "assets/props",
        "assets/effects",
        "assets/audio",
        "shots",
        "snapshots",
        "renders",
    ):
        (output / relative).mkdir(parents=True, exist_ok=True)

    build_script = Path(__file__).with_name("build_hyperframes_timeline.py")
    subprocess.run(
        [sys.executable, str(build_script), "--manifest", str(output / "story-manifest.json"), "--project", str(output)],
        check=True,
    )
    print(f"Initialized {output}")
    print("Next: approve frontal reference-only identities, then generate the hardest benchmark shot only after its spatial contract passes.")


if __name__ == "__main__":
    main()
