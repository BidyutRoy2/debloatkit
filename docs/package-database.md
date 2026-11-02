# Package database

All classifications live in `debloatkit/packages.py`. Each entry has a
human-readable reason — a package without a reason doesn't get classified.

## Risk levels

| Level | Meaning | Auto-action |
|---|---|---|
| `safe` | Widely reported safe to disable; reinstallable from Play | Disabled by every profile |
| `caution` | Safe on most devices, but may affect a feature (voice button, cast) | Only `tv-balanced` / `aggressive` |
| `never` | Critical system package | Refused, always |
| `unknown` | Not in the database | Reported only, never touched |

## Proposing a new entry

Open an issue (or PR) with:

1. The exact package name (from `debloatkit inventory --host <IP>`).
2. Device model + Android/TV OS version.
3. What the app does, and what broke (or didn't) when you disabled it manually.
4. Which level you propose, and why.

Entries are accepted conservatively: "I disabled it and nothing broke in
a day" earns `caution` at most; `safe` needs a clear reason the package
can't affect core functions (e.g. it's a reinstallable third-party app).
