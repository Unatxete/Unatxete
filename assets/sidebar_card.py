#!/usr/bin/env python3
"""Build a GitHub-sidebar-style profile card (dark and light) placed below the portrait card.

Mirrors the look of GitHub's own profile sidebar: name, username, a decorative Follow
button, bio, followers count and a few icon rows (location, local time, email, LinkedIn).
Standard library only; the local-time row is only as fresh as the last regeneration
(see .github/workflows/profile-stats.yml, which reruns this weekly).
"""
from __future__ import annotations

import os
from datetime import datetime
from html import escape
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
W = 340
PAD = 24
INNER = W - 2 * PAD

THEMES = {
    "dark": dict(bg="#111d2b", border="#3c5b74", name="#cccfae", muted="#6b9d8c", text="#cccfae", icon="#3c5b74"),
    "light": dict(bg="#cccfae", border="#645038", name="#111d2b", muted="#645038", text="#111d2b", icon="#645038"),
}

NAME = "Unax Alonso"
USERNAME = "Unatxete"
BIO = (
    "Cybersecurity engineering student with a security-first approach to "
    "building software. I automate what can be automated."
)
LOCATION = "Basque Country, Spain"
EMAIL = "unax.aj@gmail.com"
LINKEDIN = "coming soon"

ICONS = {
    "location": '<path d="M8 15s5.5-4.36 5.5-8.5A5.5 5.5 0 0 0 2.5 6.5C2.5 10.64 8 15 8 15Z"/>'
                '<circle cx="8" cy="6.5" r="2"/>',
    "clock": '<circle cx="8" cy="8" r="6.25"/><path d="M8 4.5V8l2.5 1.5"/>',
    "mail": '<rect x="1.5" y="3.5" width="13" height="9" rx="1.5"/><path d="M1.5 4.5 8 9l6.5-4.5"/>',
    "linkedin": '<rect x="1.5" y="1.5" width="13" height="13" rx="2"/>'
                '<path d="M5 6.5v5.5M5 4.3v.1M8 12V6.5m0 2.3c0-1.5 3.5-1.7 3.5.3v3" '
                'stroke-linecap="round"/>',
    "people": '<circle cx="5.5" cy="5.5" r="2.2"/><path d="M1.5 14c0-2.5 1.8-4 4-4s4 1.5 4 4"/>'
              '<circle cx="11.5" cy="6.5" r="1.8"/><path d="M9.8 10.2c.5-.3 1.1-.5 1.7-.5 2 0 3.5 1.5 3.5 4"/>',
}


def icon(name: str, x: float, y: float, c: dict) -> str:
    return (f'<g transform="translate({x:.1f},{y:.1f})" fill="none" stroke="{c["icon"]}" '
            f'stroke-width="1.3" stroke-linejoin="round">{ICONS[name]}</g>')


def wrap(text: str, max_chars: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) > max_chars and cur:
            lines.append(cur)
            cur = w
        else:
            cur = cand
    if cur:
        lines.append(cur)
    return lines


def local_time() -> str:
    now = datetime.now(ZoneInfo("Europe/Madrid"))
    offset = int(now.utcoffset().total_seconds() // 3600)
    return f'{now.strftime("%H:%M")} · UTC{offset:+d}'


def build(name: str, followers: int = 0) -> str:
    c = THEMES[name]
    bio_lines = wrap(BIO, 38)

    y = PAD
    y += 26  # name baseline
    name_y = y
    y += 22  # username baseline
    user_y = y
    y += 30  # gap before button
    btn_y = y
    y += 36 + 22  # button height + gap before bio
    bio_start_y = y
    y += 20 * len(bio_lines)
    y += 18  # gap before followers
    followers_y = y
    y += 32  # gap before icon rows

    rows = [("location", LOCATION), ("clock", local_time()), ("mail", EMAIL), ("linkedin", f"in/ {LINKEDIN}")]
    row_h = 26
    rows_start_y = y
    y += row_h * len(rows)
    y += PAD

    H = round(y)

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="st sd" font-family="{FONT}">',
        '  <title id="st">Unax Alonso — profile sidebar</title>',
        '  <desc id="sd">Bio, followers, location, local time, email and LinkedIn for Unatxete.</desc>',
        f'  <rect x="0.75" y="0.75" width="{W - 1.5}" height="{H - 1.5}" rx="12" '
        f'fill="{c["bg"]}" stroke="{c["border"]}" stroke-width="1.5"/>',
        f'  <text x="{PAD}" y="{name_y}" font-size="26" font-weight="700" fill="{c["name"]}">{escape(NAME)}</text>',
        f'  <text x="{PAD}" y="{user_y}" font-size="15" fill="{c["muted"]}">{escape(USERNAME)}</text>',
        f'  <rect x="{PAD}" y="{btn_y - 24}" width="{INNER}" height="36" rx="8" fill="none" '
        f'stroke="{c["border"]}" stroke-width="1.3"/>',
        f'  <text x="{PAD + INNER / 2}" y="{btn_y}" font-size="14" font-weight="600" fill="{c["text"]}" '
        f'text-anchor="middle">Follow</text>',
    ]

    for i, line in enumerate(bio_lines):
        out.append(f'  <text x="{PAD}" y="{bio_start_y + 20 * i}" font-size="14" fill="{c["text"]}">{escape(line)}</text>')

    out.append(
        f'  {icon("people", PAD, followers_y - 12, c)}'
        f'<text x="{PAD + 22}" y="{followers_y}" font-size="14" fill="{c["text"]}">'
        f'<tspan font-weight="700">{followers}</tspan> followers · <tspan font-weight="700">0</tspan> following</text>'
    )

    for i, (ic, label) in enumerate(rows):
        ry = rows_start_y + row_h * i
        out.append(
            f'  {icon(ic, PAD, ry - 12, c)}'
            f'<text x="{PAD + 22}" y="{ry}" font-size="14" fill="{c["text"]}">{escape(label)}</text>'
        )

    out += ["</svg>", ""]
    return "\n".join(out)


def main() -> None:
    for theme in THEMES:
        path = os.path.join(HERE, f"{theme}_sidebar.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build(theme))
        print("wrote", path)


if __name__ == "__main__":
    main()
