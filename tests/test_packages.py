import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from debloatkit.packages import PROFILES, classify, plan

class Tests(unittest.TestCase):
    def test_never_touch_is_never(self):
            level, _ = classify("com.android.systemui")
            assert level == "never"
            level, _ = classify("com.google.android.gms")
            assert level == "never"
    def test_safe_and_caution_levels(self):
            assert classify("com.netflix.ninja")[0] == "safe"
            assert classify("com.google.android.apps.assistant")[0] == "caution"
            assert classify("com.example.something.unknown")[0] == "unknown"
    def test_plan_never_includes_never_or_unknown(self):
            installed = [
                "com.android.systemui",
                "com.netflix.ninja",
                "com.example.unknown",
                "com.google.android.apps.assistant",
            ]
            planned = plan(installed, "tv-minimal")
            action_pkgs = {e["package"] for e in planned["actions"]}
            assert action_pkgs == {"com.netflix.ninja"}
            assert planned["summary"]["never_touch_blocked"] == 1
            assert planned["summary"]["unknown"] == 1
    def test_plan_deduplicates_and_rejects_bad_profile(self):
            planned = plan(["com.netflix.ninja", "com.netflix.ninja"], "tv-minimal")
            assert planned["summary"]["to_disable"] == 1
            try:
                plan([], "nope")
            except ValueError:
                pass
            else:
                raise AssertionError("bad profile should raise")
    def test_every_profile_has_levels(self):
            assert set(PROFILES) >= {"tv-minimal", "phone-minimal", "aggressive"}
            for info in PROFILES.values():
                assert info["levels"] and info["description"]

if __name__ == "__main__":
    unittest.main()
