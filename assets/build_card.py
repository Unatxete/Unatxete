#!/usr/bin/env python3
"""Build the neofetch-style profile card in a dark and a light variant.

Reads the ASCII portrait from assets/portrait.txt and writes assets/dark_mode.svg and
assets/light_mode.svg. The four GitHub figures are placeholders here: assets/stats.py
fills them in by element id. Standard library only.

To use a different portrait, regenerate assets/portrait.txt (for example with
`jp2a --width=76 --background=dark image.jpg > assets/portrait.txt`) and rerun this script.
"""
from __future__ import annotations

import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1000, 596
PORTRAIT_X, PORTRAIT_Y = 36, 74
FONT_PX, CHAR_W, LINE_H = 9, 5.4, 9.6
INFO_X = 496
VALUE_X = 606

THEMES = {
    "dark": dict(
        bg="#0d1117", bar="#161b22", line="#30363d", muted="#8b949e", text="#c9d1d9",
        key="#a78bfa", accent="#7ee787", section="#f0883e", link="#a5d6ff", art="#c4b5fd",
    ),
    "light": dict(
        bg="#ffffff", bar="#f6f8fa", line="#d0d7de", muted="#57606a", text="#24292f",
        key="#6d28d9", accent="#1a7f37", section="#bc4c00", link="#0969da", art="#5b21b6",
    ),
}

INFO = [
    ("Role", "Cybersecurity Engineering undergraduate"),
    ("Focus", "Secure dev · Networks · Databases"),
    ("Languages", "Java · Python · PowerShell · MicroPython"),
    ("Tools", "Git · Linux · WireGuard · Snort · sqlmap"),
    ("Learning", "CCNA · Cryptography · MySQL · RGPD"),
]
CONTACT = [("Email", "unax.aj@gmail.com"), ("GitHub", "UnaxAlonso0")]


def portrait(c: dict) -> str:
    rows = []
    with open(os.path.join(HERE, "portrait.txt"), encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().split("\n")):
            body = line.lstrip(" ")
            if not body:
                continue
            x = PORTRAIT_X + (len(line) - len(body)) * CHAR_W
            y = PORTRAIT_Y + i * LINE_H
            # textLength pins every row to the same advance width in any monospace fallback font
            rows.append(
                f'<tspan x="{x:.1f}" y="{y:.1f}" textLength="{len(body) * CHAR_W:.1f}" '
                f'lengthAdjust="spacing">{escape(body, quote=False)}</tspan>'
            )
    return (
        f'<text font-size="{FONT_PX}" fill="{c["art"]}" xml:space="preserve">\n    '
        + "\n    ".join(rows)
        + "\n  </text>"
    )


def rule(c: dict, label: str, y: int, color_key: str) -> str:
    return (
        f'<text x="{INFO_X}" y="{y}"><tspan fill="{c[color_key]}">{label} </tspan>'
        f'<tspan fill="{c["muted"]}">{"─" * (52 - len(label))}</tspan></text>'
    )


def kv(c: dict, key: str, value: str, y: int, link: bool = False) -> str:
    fill = c["link"] if link else c["text"]
    return (
        f'<text x="{INFO_X}" y="{y}" fill="{c["key"]}">{key}</text>'
        f'<text x="{VALUE_X}" y="{y}" fill="{fill}">{escape(value, quote=False)}</text>'
    )


def stat(c: dict, label: str, element_id: str, x: int, y: int) -> str:
    return (
        f'<text x="{x}" y="{y}" fill="{c["key"]}">{label}<tspan fill="{c["text"]}">: </tspan>'
        f'<tspan fill="{c["accent"]}" font-weight="600" id="{element_id}">0</tspan></text>'
    )


def build(name: str) -> str:
    c = THEMES[name]
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d" font-family="ui-monospace, SFMono-Regular, Menlo, '
        f"Consolas, 'Liberation Mono', monospace\">",
        '  <title id="t">unax@github — profile card</title>',
        '  <desc id="d">ASCII portrait, role, focus, languages, tools, contact and public GitHub '
        "statistics for UnaxAlonso0.</desc>",
        f'  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="12" fill="{c["bg"]}" '
        f'stroke="{c["line"]}" stroke-width="1.5"/>',
        f'  <path d="M1 13 A12 12 0 0 1 13 1 H{W - 13} A12 12 0 0 1 {W - 1} 13 V44 H1 Z" fill="{c["bar"]}"/>',
        f'  <line x1="1" y1="44" x2="{W - 1}" y2="44" stroke="{c["line"]}"/>',
        '  <circle cx="26" cy="22.5" r="6" fill="#ff5f56"/>',
        '  <circle cx="46" cy="22.5" r="6" fill="#ffbd2e"/>',
        '  <circle cx="66" cy="22.5" r="6" fill="#27c93f"/>',
        f'  <text x="{W // 2}" y="27" text-anchor="middle" font-size="13" fill="{c["muted"]}">unax@github: ~</text>',
        f"  {portrait(c)}",
        f'  <line x1="470" y1="64" x2="470" y2="{H - 24}" stroke="{c["line"]}"/>',
        '  <g font-size="15" xml:space="preserve">',
        f'    <text x="{INFO_X}" y="96"><tspan fill="{c["accent"]}">unax@github</tspan>'
        f'<tspan fill="{c["muted"]}"> {"─" * 40}</tspan></text>',
    ]
    y = 132
    for key, value in INFO:
        out.append("    " + kv(c, key, value, y))
        y += 30
    y += 22
    out.append("    " + rule(c, "- Contact", y, "section"))
    y += 32
    for key, value in CONTACT:
        out.append("    " + kv(c, key, value, y, link=True))
        y += 30
    y += 22
    out.append("    " + rule(c, "- GitHub Stats", y, "section"))
    y += 32
    out.append("    " + stat(c, "Repos", "v_repos", INFO_X, y))
    out.append("    " + stat(c, "Contributed", "v_contrib", 700, y))
    y += 30
    out.append("    " + stat(c, "Stars", "v_stars", INFO_X, y))
    out.append("    " + stat(c, "Followers", "v_followers", 700, y))
    out += ["  </g>", "</svg>", ""]
    return "\n".join(out)


def main() -> None:
    for name in THEMES:
        path = os.path.join(HERE, f"{name}_mode.svg")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(build(name))
        print("wrote", path)


if __name__ == "__main__":
    main()
