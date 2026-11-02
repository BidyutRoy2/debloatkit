import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from debloatkit.backup import load_backup, make_backup, save_backup
from debloatkit.packages import plan
from debloatkit.report import html_report, markdown_report


class Tests(unittest.TestCase):
    def test_backup_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = str(Path(tmp) / "b.json")
            save_backup(make_backup("TV", "tv-minimal", ["b.pkg", "a.pkg", "a.pkg"]), path)
            data = load_backup(path)
            self.assertEqual(data["disabled_packages"], ["a.pkg", "b.pkg"])
            self.assertEqual(data["format"], "debloatkit-backup")

    def test_backup_rejects_foreign_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.json"
            path.write_text('{"format": "other"}')
            with self.assertRaises(ValueError):
                load_backup(str(path))

    def test_reports_include_everything(self):
        planned = plan(
            ["com.android.systemui", "com.netflix.ninja", "com.example.unknown"], "tv-minimal"
        )
        md = markdown_report(planned, "Test TV")
        self.assertIn("com.netflix.ninja", md)
        self.assertIn("com.android.systemui", md)
        self.assertIn("debloatkit restore", md)
        html_doc = html_report(planned, "Test TV")
        self.assertIn("<table>", html_doc)
        self.assertIn("com.netflix.ninja", html_doc)
        self.assertIn("color-scheme", html_doc)


if __name__ == "__main__":
    unittest.main()
