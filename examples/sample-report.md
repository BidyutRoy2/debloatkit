# debloatkit report — Example Google TV

Profile: `tv-minimal` · Installed: 6 · Would disable: 2 · Kept: 4 · Protected (never-touch): 2 · Unknown: 1

## Would disable

- `com.amazon.amazonvideo.livingroom` (safe) — Preloaded Prime Video for TV.
- `com.netflix.ninja` (safe) — Preloaded Netflix for TV (user can reinstall from Play).

## Kept / protected

- `com.android.systemui` (never) — Status bar, navigation, lock screen.
- `com.example.oem.weather` (unknown) — Not in the curated database — never auto-touched.
- `com.google.android.apps.assistant` (caution) — Google Assistant app — breaks voice button if removed.
- `com.google.android.tvlauncher` (never) — Google TV launcher (TVs).

> Restore any time with: `debloatkit restore --backup backup.json`
