"""HTML + Markdown report generation.

The report is the whole point of dry-run mode: before anything changes,
the user gets a readable page showing exactly what would be disabled,
what is protected, and what is unknown — plus the one-command restore.
"""

from __future__ import annotations

import html

_CSS = """
:root{color-scheme:light dark}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0 auto;
max-width:880px;padding:24px;line-height:1.55}
h1{font-size:1.7rem}table{width:100%;border-collapse:collapse}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid #8884}
.badge{padding:2px 8px;border-radius:999px;font-size:.8rem}
.safe{background:#dcfce7;color:#14532d}.caution{background:#fef9c3;color:#713f12}
.never{background:#fee2e2;color:#7f1d1d}.unknown{background:#e5e7eb;color:#374151}
@media(prefers-color-scheme:dark){body{background:#0f172a;color:#e2e8f0}}
"""


def markdown_report(plan: dict, device: str) -> str:
    summary = plan["summary"]
    lines = [
        f"# debloatkit report — {device}",
        "",
        f"Profile: `{plan['profile']}` · Installed: {summary['installed']} · "
        f"Would disable: {summary['to_disable']} · Kept: {summary['kept']} · "
        f"Protected (never-touch): {summary['never_touch_blocked']} · "
        f"Unknown: {summary['unknown']}",
        "",
        "## Would disable",
        "",
    ]
    if plan["actions"]:
        for entry in plan["actions"]:
            lines.append(f"- `{entry['package']}` ({entry['level']}) — {entry['reason']}")
    else:
        lines.append("_Nothing to disable under this profile._")
    lines += ["", "## Kept / protected", ""]
    for entry in plan["kept"]:
        lines.append(f"- `{entry['package']}` ({entry['level']}) — {entry['reason']}")
    lines += [
        "",
        "> Restore any time with: `debloatkit restore --backup backup.json`",
    ]
    return "\n".join(lines) + "\n"


def html_report(plan: dict, device: str) -> str:
    summary = plan["summary"]

    def row(entry: dict) -> str:
        pkg = html.escape(entry["package"])
        lvl = html.escape(entry["level"])
        reason = html.escape(entry["reason"])
        return f"<tr><td><code>{pkg}</code></td><td><span class='badge {lvl}'>{lvl}</span></td><td>{reason}</td></tr>"

    action_rows = "".join(row(e) for e in plan["actions"]) or (
        "<tr><td colspan='3'><i>Nothing to disable under this profile.</i></td></tr>"
    )
    kept_rows = "".join(row(e) for e in plan["kept"])
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>debloatkit report — {html.escape(device)}</title><style>{_CSS}</style></head>
<body><h1>🧹 debloatkit report</h1>
<p><strong>Device:</strong> {html.escape(device)} · <strong>Profile:</strong> {html.escape(plan["profile"])}</p>
<p>Installed: {summary["installed"]} · Would disable: {summary["to_disable"]} ·
Kept: {summary["kept"]} · Protected: {summary["never_touch_blocked"]} ·
Unknown: {summary["unknown"]}</p>
<h2>Would disable</h2>
<table><tr><th>Package</th><th>Level</th><th>Why</th></tr>{action_rows}</table>
<h2>Kept / protected</h2>
<table><tr><th>Package</th><th>Level</th><th>Why</th></tr>{kept_rows}</table>
<p>Restore any time with: <code>debloatkit restore --backup backup.json</code></p>
</body></html>
"""
