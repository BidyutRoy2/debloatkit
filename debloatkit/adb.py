"""Minimal ADB wrapper.

Only the `adb` binary from Google's platform-tools is used; no extra
dependencies. Every command is built as an argument list (never a shell
string) and every mutating command goes through ``--dry-run`` first in
the CLI, so a typo can never become a device change.

The ``runner`` parameter exists so tests can inject a fake ADB without
a device attached.
"""

from __future__ import annotations

import re
import subprocess

_PKG_LINE = re.compile(r"^package:(\S+)$")


class AdbError(RuntimeError):
    """Raised when adb is missing or a command fails."""


def default_runner(argv: list[str]) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(argv, capture_output=True, text=True, timeout=60)
    except FileNotFoundError as exc:
        raise AdbError(
            "adb not found. Install Android platform-tools and make sure "
            "`adb` is on your PATH (see docs/getting-started.md)."
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise AdbError(f"adb timed out: {' '.join(argv)}") from exc


def check_adb(runner=default_runner) -> str:
    result = runner(["adb", "version"])
    if result.returncode != 0:
        raise AdbError(f"adb failed: {result.stderr.strip()}")
    return result.stdout.splitlines()[0] if result.stdout else "adb"


def connect(host: str, port: int = 5555, runner=default_runner) -> str:
    result = runner(["adb", "connect", f"{host}:{port}"])
    out = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 or "connected" not in out.lower():
        raise AdbError(f"could not connect to {host}:{port}: {out.strip()}")
    return out.strip()


def list_packages(runner=default_runner) -> list[str]:
    result = runner(["adb", "shell", "pm", "list", "packages"])
    if result.returncode != 0:
        raise AdbError(f"could not list packages: {result.stderr.strip()}")
    packages = []
    for line in result.stdout.splitlines():
        match = _PKG_LINE.match(line.strip())
        if match:
            packages.append(match.group(1))
    return packages


def device_model(runner=default_runner) -> str:
    result = runner(["adb", "shell", "getprop", "ro.product.model"])
    if result.returncode != 0:
        return "unknown device"
    return result.stdout.strip() or "unknown device"


def disable_package(package: str, runner=default_runner, dry_run: bool = False) -> str:
    """Disable a user-visible app reversibly (pm disable-user).

    System apps are *disabled*, not uninstalled, so `restore` can always
    bring them back. Returns the command that would run (dry-run) or ran.
    """
    argv = ["adb", "shell", "pm", "disable-user", "--user", "0", package]
    if dry_run:
        return " ".join(argv)
    result = runner(argv)
    if result.returncode != 0:
        raise AdbError(f"failed to disable {package}: {result.stderr.strip()}")
    return " ".join(argv)


def enable_package(package: str, runner=default_runner, dry_run: bool = False) -> str:
    argv = ["adb", "shell", "pm", "enable", package]
    if dry_run:
        return " ".join(argv)
    result = runner(argv)
    if result.returncode != 0:
        raise AdbError(f"failed to enable {package}: {result.stderr.strip()}")
    return " ".join(argv)
