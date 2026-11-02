import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from debloatkit import adb as adb_mod
from debloatkit.cli import main


class FakeResult:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout, self.stderr, self.returncode = stdout, stderr, returncode


class FakeAdb:
    """Records commands; pretends to be a TV with a fixed package list."""

    PACKAGES = (
        "package:com.android.systemui\n"
        "package:com.netflix.ninja\n"
        "package:com.google.android.apps.assistant\n"
        "package:com.example.unknown\n"
    )

    def __init__(self):
        self.commands = []

    def __call__(self, argv):
        self.commands.append(argv)
        if argv[:2] == ["adb", "version"]:
            return FakeResult("Android Debug Bridge version 1.0.41\n")
        if argv[:2] == ["adb", "connect"]:
            return FakeResult("connected to 192.168.1.50:5555\n")
        if argv == ["adb", "shell", "getprop", "ro.product.model"]:
            return FakeResult("Google TV Streamer\n")
        if argv == ["adb", "shell", "pm", "list", "packages"]:
            return FakeResult(self.PACKAGES)
        if "disable-user" in argv or "enable" in argv:
            return FakeResult("Package enabled\n")
        return FakeResult("")


class Tests(unittest.TestCase):
    def test_list_packages_parses_pm_output(self):
        self.assertEqual(
            adb_mod.list_packages(FakeAdb()),
            [
                "com.android.systemui",
                "com.netflix.ninja",
                "com.google.android.apps.assistant",
                "com.example.unknown",
            ],
        )

    def test_disable_builds_safe_argv_no_shell(self):
        fake = FakeAdb()
        cmd = adb_mod.disable_package("com.netflix.ninja", fake, dry_run=True)
        self.assertEqual(cmd, "adb shell pm disable-user --user 0 com.netflix.ninja")
        self.assertEqual(fake.commands, [])  # dry run runs nothing

    def test_scan_does_not_mutate(self):
        fake = FakeAdb()
        self.assertEqual(main(["scan", "--host", "192.168.1.50"], runner=fake), 0)
        self.assertFalse(any("disable-user" in c for c in fake.commands))

    def test_apply_requires_yes_and_writes_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = FakeAdb()
            backup = str(Path(tmp) / "backup.json")
            # Without --yes: dry run, no backup, no disable.
            self.assertEqual(
                main(["apply", "--host", "192.168.1.50", "--backup", backup], runner=fake), 0
            )
            self.assertFalse(Path(backup).exists())
            # With --yes: only the safe package is disabled, backup written.
            self.assertEqual(
                main(
                    ["apply", "--host", "192.168.1.50", "--backup", backup, "--yes"],
                    runner=fake,
                ),
                0,
            )
            disabled = [c[-1] for c in fake.commands if "disable-user" in c]
            self.assertEqual(disabled, ["com.netflix.ninja"])
            self.assertIn("com.netflix.ninja", Path(backup).read_text())

    def test_restore_reenables_from_backup(self):
        from debloatkit.backup import make_backup, save_backup

        with tempfile.TemporaryDirectory() as tmp:
            backup = str(Path(tmp) / "backup.json")
            save_backup(make_backup("Google TV Streamer", "tv-minimal", ["com.netflix.ninja"]), backup)
            fake = FakeAdb()
            self.assertEqual(
                main(["restore", "--host", "192.168.1.50", "--backup", backup, "--yes"], runner=fake),
                0,
            )
            self.assertTrue(any("enable" in c for c in fake.commands))

    def test_connect_failure_is_error_not_crash(self):
        def failing(argv):
            return FakeResult("", "cannot connect", 1)

        self.assertEqual(main(["scan", "--host", "10.0.0.1"], runner=failing), 1)


if __name__ == "__main__":
    unittest.main()
