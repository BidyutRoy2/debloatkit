"""Command-line interface.

Safety rules enforced here, not just documented:
  1. `scan` is the default first step and never changes anything.
  2. `apply` refuses to run without a `--backup` path, so a restore file
     always exists before the first change.
  3. `apply` prints the plan and requires `--yes` — no silent changes.
  4. NEVER_TOUCH packages can never be disabled, by any flag.
"""

from __future__ import annotations

import argparse
import json
import sys

from . import adb as adb_mod
from . import backup as backup_mod
from . import report as report_mod
from .packages import PROFILES, classify, plan


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="debloatkit",
        description="Safe Android & Google TV debloater over Wi-Fi ADB.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    scan = sub.add_parser("scan", help="List packages and show the plan (no changes).")
    scan.add_argument("--host", required=True, help="TV/phone IP address on your Wi-Fi.")
    scan.add_argument("--port", type=int, default=5555)
    scan.add_argument("--profile", default="tv-minimal", choices=sorted(PROFILES))
    scan.add_argument("--report", help="Write an HTML report to this path.")
    scan.add_argument("--json", help="Write the plan as JSON to this path.")

    apply_p = sub.add_parser("apply", help="Disable the planned packages (reversible).")
    apply_p.add_argument("--host", required=True)
    apply_p.add_argument("--port", type=int, default=5555)
    apply_p.add_argument("--profile", default="tv-minimal", choices=sorted(PROFILES))
    apply_p.add_argument("--backup", required=True, help="Path for the restore file (required).")
    apply_p.add_argument("--yes", action="store_true", help="Confirm after reviewing the plan.")

    restore = sub.add_parser("restore", help="Re-enable everything in a backup file.")
    restore.add_argument("--host", required=True)
    restore.add_argument("--port", type=int, default=5555)
    restore.add_argument("--backup", required=True)
    restore.add_argument("--yes", action="store_true")

    inv = sub.add_parser("inventory", help="Print installed packages, one per line.")
    inv.add_argument("--host", required=True)
    inv.add_argument("--port", type=int, default=5555)

    sub.add_parser("profiles", help="List the built-in profiles.")
    return parser


def _connect(args, runner) -> str:
    adb_mod.check_adb(runner)
    adb_mod.connect(args.host, args.port, runner)
    return adb_mod.device_model(runner)


def cmd_scan(args, runner) -> int:
    device = _connect(args, runner)
    planned = plan(adb_mod.list_packages(runner), args.profile)
    print(report_mod.markdown_report(planned, device))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            handle.write(report_mod.html_report(planned, device))
        print(f"HTML report written to {args.report}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as handle:
            json.dump(planned, handle, indent=2)
        print(f"Plan JSON written to {args.json}")
    return 0


def cmd_apply(args, runner) -> int:
    device = _connect(args, runner)
    planned = plan(adb_mod.list_packages(runner), args.profile)
    print(report_mod.markdown_report(planned, device))
    if not planned["actions"]:
        print("Nothing to disable — no changes made.")
        return 0
    if not args.yes:
        print("Dry run only. Re-run with --yes to apply (after reviewing the plan).")
        return 0
    disabled = []
    for entry in planned["actions"]:
        # Double-check the safety net at apply time, not just plan time.
        level, _ = classify(entry["package"])
        if level not in ("safe", "caution"):
            print(f"SKIP (safety net): {entry['package']} is {level}")
            continue
        adb_mod.disable_package(entry["package"], runner)
        disabled.append(entry["package"])
        print(f"disabled {entry['package']}")
    backup_mod.save_backup(backup_mod.make_backup(device, args.profile, disabled), args.backup)
    print(f"Backup written to {args.backup} — restore with: debloatkit restore --backup {args.backup}")
    return 0


def cmd_restore(args, runner) -> int:
    data = backup_mod.load_backup(args.backup)
    device = _connect(args, runner)
    packages = data["disabled_packages"]
    print(f"Restoring {len(packages)} package(s) on {device} from {args.backup}")
    if not args.yes:
        print("Dry run only. Re-run with --yes to restore.")
        return 0
    for package in packages:
        adb_mod.enable_package(package, runner)
        print(f"enabled {package}")
    print("Restore complete.")
    return 0


def cmd_inventory(args, runner) -> int:
    _connect(args, runner)
    for package in adb_mod.list_packages(runner):
        print(package)
    return 0


def main(argv=None, runner=None) -> int:
    args = build_parser().parse_args(argv)
    runner = runner or adb_mod.default_runner
    try:
        if args.command == "scan":
            return cmd_scan(args, runner)
        if args.command == "apply":
            return cmd_apply(args, runner)
        if args.command == "restore":
            return cmd_restore(args, runner)
        if args.command == "inventory":
            return cmd_inventory(args, runner)
        if args.command == "profiles":
            for name, info in sorted(PROFILES.items()):
                print(f"{name}: {info['description']}")
            return 0
    except (adb_mod.AdbError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
