"""Curated package knowledge base.

Risk levels:
  - "safe":    widely reported as safe to disable; no core function depends on it.
  - "caution": safe on most devices, but may affect a feature (e.g. a remote
               button, casting, or an OEM launcher extra). Disabled only with
               --include-caution or an explicit profile that lists it.
  - "never":   critical system package. debloatkit REFUSES to touch these,
               even if the user asks. This list is the safety net.

The lists below are conservative starting points, not an exhaustive
database: OEMs rename packages between models. Anything not listed here
is classified "unknown" and is never touched automatically — it only
appears in reports so the user can decide.

Nothing here is copied from another debloat list: entries were chosen
from first principles (is it a launcher-critical service? a telephony
stack? a removable preload?) and each entry carries the reason.
"""

from __future__ import annotations

NEVER_TOUCH = {
    # Core Android runtime — disabling any of these can brick boot or UI.
    "android": "The Android system itself.",
    "com.android.systemui": "Status bar, navigation, lock screen.",
    "com.android.launcher3": "Default launcher fallback.",
    "com.android.settings": "Settings app.",
    "com.android.packageinstaller": "App installer.",
    "com.android.providers.settings": "Settings storage provider.",
    "com.android.providers.media": "Media storage provider.",
    "com.android.externalstorage": "External storage access.",
    "com.android.inputmethod.latin": "Default keyboard fallback.",
    "com.google.android.gms": "Google Play services — many apps depend on it.",
    "com.google.android.gsf": "Google Services Framework.",
    "com.android.vending": "Google Play Store (removing it strands updates).",
    "com.android.phone": "Telephony stack (phones; harmless to keep on TVs).",
    "com.android.bluetooth": "Bluetooth stack (remotes, gamepads, audio).",
    "com.android.wifi": "Wi-Fi stack (debloatkit connects over Wi-Fi!).",
    "com.android.nfc": "NFC stack.",
    "com.google.android.tvlauncher": "Google TV launcher (TVs).",
    "com.google.android.leanbacklauncher": "Android TV leanback launcher.",
    "com.google.android.tvrecommendations": "TV home recommendations (launcher feed).",
}

SAFE_TO_DISABLE = {
    # Preloaded streaming / shopping / demo apps commonly shipped on TVs
    # and phones. Disabling (not uninstalling) keeps them restorable.
    "com.netflix.ninja": "Preloaded Netflix for TV (user can reinstall from Play).",
    "com.amazon.amazonvideo.livingroom": "Preloaded Prime Video for TV.",
    "com.disney.disneyplus": "Preloaded Disney+ (TV builds).",
    "com.hulu.livingroomplus": "Preloaded Hulu for TV.",
    "com.google.android.youtube.tv": "Preloaded YouTube for TV.",
    "com.spotify.tv.android": "Preloaded Spotify for TV.",
    "com.amazon.venezia": "Amazon Appstore preload on some TVs.",
    "com.tubitv": "Preloaded Tubi app.",
    "com.plexapp.android": "Preloaded Plex app.",
    # OEM demo / retail / feedback preloads
    "com.google.android.apps.tv.dreamx": "TV screensaver demo content pack.",
    "com.oem.demo": "Generic retail demo mode placeholder (OEM builds).",
    "com.facebook.appmanager": "Facebook app manager preload (phones).",
    "com.facebook.system": "Facebook system preload (phones).",
    "com.facebook.services": "Facebook services preload (phones).",
    "com.microsoft.skydrive": "OneDrive preload (some OEM phones).",
    "com.booking": "Booking.com preload (some OEM phones).",
    "com.linkedin.android": "LinkedIn preload (some OEM phones).",
}

CAUTION = {
    "com.google.android.tv.remote.service": "TV remote service — affects phone-as-remote on some TVs.",
    "com.google.android.gms.cast": "Cast receiver pieces — affects Chromecast built-in on some TVs.",
    "com.android.tv.settings": "TV-specific settings panels (keep unless you know why).",
    "com.google.android.apps.mediashell": "Media shell used by some cast flows.",
    "com.samsung.android.bixby.agent": "Bixby voice (Samsung) — breaks voice button if removed.",
    "com.google.android.apps.assistant": "Google Assistant app — breaks voice button if removed.",
    "com.android.chrome": "Chrome preload — harmless to disable, but some apps open links in it.",
}

# Profile presets: which risk levels each profile acts on.
PROFILES = {
    "tv-minimal": {
        "description": "TVs only: disable safe streaming preloads, keep everything else.",
        "levels": ("safe",),
    },
    "tv-balanced": {
        "description": "TVs: safe preloads + caution items the user confirms one by one.",
        "levels": ("safe", "caution"),
    },
    "phone-minimal": {
        "description": "Phones/tablets: disable safe third-party preloads only.",
        "levels": ("safe",),
    },
    "aggressive": {
        "description": "Safe + caution, no prompts. Still never touches NEVER_TOUCH.",
        "levels": ("safe", "caution"),
    },
}


def classify(package: str) -> tuple[str, str]:
    """Return (risk_level, reason) for a package name."""
    if package in NEVER_TOUCH:
        return "never", NEVER_TOUCH[package]
    if package in SAFE_TO_DISABLE:
        return "safe", SAFE_TO_DISABLE[package]
    if package in CAUTION:
        return "caution", CAUTION[package]
    return "unknown", "Not in the curated database — never auto-touched."


def plan(installed: list[str], profile: str = "tv-minimal") -> dict:
    """Build an action plan for a list of installed package names.

    Returns a dict with one list per risk level plus a summary. The plan
    never includes "never" or "unknown" packages in the action list.
    """
    if profile not in PROFILES:
        raise ValueError(f"unknown profile {profile!r}; choose from {sorted(PROFILES)}")
    levels = set(PROFILES[profile]["levels"])
    actions, kept, report = [], [], []
    for pkg in sorted(set(installed)):
        level, reason = classify(pkg)
        entry = {"package": pkg, "level": level, "reason": reason}
        report.append(entry)
        if level in levels:
            actions.append(entry)
        else:
            kept.append(entry)
    return {
        "profile": profile,
        "actions": actions,
        "kept": kept,
        "report": report,
        "summary": {
            "installed": len(report),
            "to_disable": len(actions),
            "kept": len(kept),
            "never_touch_blocked": sum(1 for e in report if e["level"] == "never"),
            "unknown": sum(1 for e in report if e["level"] == "unknown"),
        },
    }
