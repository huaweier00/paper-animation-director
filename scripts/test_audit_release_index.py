#!/usr/bin/env python3
"""Tests for ordered, hash-bound final release indexing."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from audit_release_index import sha256, validate_release_index
from bind_release_index import bind as bind_release_index


class ReleaseIndexTests(unittest.TestCase):
    def test_binder_refreshes_shot_and_master_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="release-index-bind-") as directory:
            root = Path(directory)
            index, master = self.make_project(root)
            index["ordered_shots"][0]["release_sha256"] = "0" * 64
            index["master"]["sha256"] = "0" * 64
            bound = bind_release_index(index, project=root)
            self.assertEqual(
                bound["ordered_shots"][0]["release_sha256"],
                sha256(root / "shots" / "a" / "shot-release.json"),
            )
            self.assertEqual(bound["master"]["sha256"], sha256(master))

    def make_project(self, root: Path) -> tuple[dict, Path]:
        (root / "shots" / "a").mkdir(parents=True)
        (root / "shots" / "b").mkdir(parents=True)
        manifest = {"project": "test-film", "scenes": [{"id": "a"}, {"id": "b"}]}
        medium = {"project_id": "test-film", "route": "cutout-paper"}
        audio = {"project_id": "test-film", "medium_route": "cutout-paper"}
        (root / "story-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        (root / "medium-contract.json").write_text(json.dumps(medium), encoding="utf-8")
        (root / "audio-contract.json").write_text(json.dumps(audio), encoding="utf-8")
        shots = []
        for shot_id in ("a", "b"):
            release_path = root / "shots" / shot_id / "shot-release.json"
            release_path.write_text(
                json.dumps({"schema_version": 5, "shot_id": shot_id}),
                encoding="utf-8",
            )
            shots.append(
                {
                    "shot_id": shot_id,
                    "release": f"shots/{shot_id}/shot-release.json",
                    "release_sha256": sha256(release_path),
                }
            )
        master = root / "master.mp4"
        master.write_bytes(b"master")
        index = {
            "schema_version": 1,
            "project_id": "test-film",
            "phase": "release",
            "decision": "approved",
            "story_manifest": "story-manifest.json",
            "medium_contract": "medium-contract.json",
            "audio_contract": "audio-contract.json",
            "ordered_shots": shots,
            "master": {
                "path": "master.mp4",
                "sha256": sha256(master),
                "decode_verified": True,
                "audio_verified": True,
            },
            "review": {
                "sequence_continuity": "approved",
                "performance_regression": "approved",
                "sound_picture": "approved",
                "phone_size": "approved",
                "ending": "approved",
            },
        }
        return index, master

    @patch("audit_release_index.validate_audio_contract", return_value=([], [], {"audio_streams": 1}))
    @patch("audit_release_index.validate_pose_reuse", return_value=([], [], {"contracts": 2}))
    @patch("audit_release_index.validate_shot_release", return_value=([], []))
    @patch("audit_release_index.validate_medium_contract", return_value=([], []))
    @patch("audit_release_index.validate_manifest", return_value=[])
    def test_valid_index_passes(
        self,
        _manifest,
        _medium,
        _shot,
        _pose,
        _audio,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="release-index-") as directory:
            root = Path(directory)
            index, _ = self.make_project(root)
            errors, warnings, derived = validate_release_index(index, project=root)
            self.assertEqual(errors, [])
            self.assertEqual(warnings, [])
            self.assertEqual(derived["released_shots"], 2)

    @patch("audit_release_index.validate_audio_contract", return_value=([], [], {}))
    @patch("audit_release_index.validate_pose_reuse", return_value=([], [], {}))
    @patch("audit_release_index.validate_shot_release", return_value=([], []))
    @patch("audit_release_index.validate_medium_contract", return_value=([], []))
    @patch("audit_release_index.validate_manifest", return_value=[])
    def test_wrong_shot_order_fails(
        self,
        _manifest,
        _medium,
        _shot,
        _pose,
        _audio,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="release-index-") as directory:
            root = Path(directory)
            index, _ = self.make_project(root)
            index["ordered_shots"].reverse()
            errors, _, _ = validate_release_index(index, project=root)
            self.assertTrue(any("exactly match" in item for item in errors), errors)

    @patch("audit_release_index.validate_audio_contract", return_value=([], [], {}))
    @patch("audit_release_index.validate_pose_reuse", return_value=([], [], {}))
    @patch("audit_release_index.validate_shot_release", return_value=([], []))
    @patch("audit_release_index.validate_medium_contract", return_value=([], []))
    @patch("audit_release_index.validate_manifest", return_value=[])
    def test_stale_release_hash_fails(
        self,
        _manifest,
        _medium,
        _shot,
        _pose,
        _audio,
    ) -> None:
        with tempfile.TemporaryDirectory(prefix="release-index-") as directory:
            root = Path(directory)
            index, _ = self.make_project(root)
            (root / "shots" / "a" / "shot-release.json").write_text("{}", encoding="utf-8")
            errors, _, _ = validate_release_index(index, project=root)
            self.assertTrue(any("evidence is stale" in item for item in errors), errors)


if __name__ == "__main__":
    unittest.main()
