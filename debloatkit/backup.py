"""Backup / restore files.

A backup is a plain JSON file: the device, the profile, the timestamp,
and the exact list of disabled packages. Restore reads that file and
re-enables every package in it — nothing more, nothing less. The format
is versioned so future releases can migrate old backups.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

FORMAT_VERSION = 1


def make_backup(device: str, profile: str, packages: list[str]) -> dict:
    return {
        "format": "debloatkit-backup",
        "version": FORMAT_VERSION,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "device": device,
        "profile": profile,
        "disabled_packages": sorted(set(packages)),
    }


def save_backup(backup: dict, path: str) -> str:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(backup, handle, indent=2)
        handle.write("\n")
    return path


def load_backup(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if data.get("format") != "debloatkit-backup":
        raise ValueError(f"{path} is not a debloatkit backup file")
    if data.get("version") != FORMAT_VERSION:
        raise ValueError(f"unsupported backup version: {data.get('version')!r}")
    if not isinstance(data.get("disabled_packages"), list):
        raise ValueError("backup is missing its disabled_packages list")
    return data
