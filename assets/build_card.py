#!/usr/bin/env python3
"""Build the neofetch-style profile card in a dark and a light variant.

Reads the ASCII portrait from assets/portrait.txt and writes assets/dark_mode.svg and
assets/light_mode.svg. The four GitHub figures are placeholders here: assets/stats.py
fills them in by element id. Standard library only.

To use a different portrait, regenerate assets/portrait.txt (for example with
`jp2a --width=50 --background=dark image.jpg > assets/portrait.txt`) and rerun this script.
"""
from __future__ import annotations

import os
from html import escape

HERE = os.path.dirname(os.path.abspath(__file__))

W, H = 1000, 600
# monospace advance is 0.6 em; every run below is pinned with textLength so the layout
# holds even when the viewer falls back to a different monospace font
ART_X, ART_Y, ART_FS, ART_LH = 28, 42, 14, 16.8
ART_CW = ART_FS * 0.6
INFO_X, INFO_RIGHT, INFO_FS, ROW_H = 486, 972, 15, 28
INFO_CW = INFO_FS * 0.6

THEMES = {
    "dark": dict(
        bg="#161b22", border="none", muted="#6e7681", text="#c9d1d9",
        key="#ffa657", value="#a5d6ff", art="#c9d1d9", name="#ffffff",
    ),
    "light": dict(
        bg="#f6f8fa", border="#d0d7de", muted="#8c959f", text="#24292f",
        key="#bc4c00", value="#0969da", art="#24292f", name="#1f2328",
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
STATS = [
    ("Repos", "v_repos"),
    ("Contributed", "v_contrib"),
    ("Stars", "v_stars"),
    ("Followers", "v_followers"),
]


def portrait(c: dict) -> str:
    rows = []
    with open(os.path.join(HERE, "portrait.txt"), encoding="utf-8") as fh:
        for i, line in enumerate(fh.read().split("\n")):
            body = line.lstrip(" ")
            if not body:
                continue
            x = ART_X + (len(line) - len(body)) * ART_CW
            y = ART_Y + i * ART_LH
            rows.append(
                f'<tspan x="{x:.1f}" y="{y:.1f}" textLength="{len(body) * ART_CW:.1f}" '
                f'lengthAdjust="spacing">{escape(body, quote=False)}</tspan>'
            )
    return (
        f'<text font-size="{ART_FS}" fill="{c["art"]}" font-weight="600" xml:space="preserve">\n    '
        + "\n    ".join(rows)
        + "\n  </text>"
    )


def leader(c: dict, x1: float, x2: float, y: int) -> str:
    return (
        f'<line x1="{x1:.1f}" y1="{y - 4}" x2="{x2:.1f}" y2="{y - 4}" stroke="{c["muted"]}" '
        'stroke-width="1.6" stroke-linecap="round" stroke-dasharray="0.1 6.5"/>'
    )


def title(c: dict, label: str, y: int, color: str) -> str:
    end = INFO_X + len(label) * INFO_CW
    return (
        f'<text x="{INFO_X}" y="{y}" fill="{color}" textLength="{len(label) * INFO_CW:.1f}" '
        f'lengthAdjust="spacing">{escape(label, quote=False)}</text>'
        f'<line x1="{end + 10:.1f}" y1="{y - 5}" x2="{INFO_RIGHT}" y2="{y - 5}" stroke="{c["muted"]}"/>'
    )


def row(c: dict, key: str, value: str, y: int) -> str:
    key_end = INFO_X + len(key) * INFO_CW + 4
    value_w = len(value) * INFO_CW
    value_x = INFO_RIGHT - value_w
    return (
        f'<text x="{INFO_X}" y="{y}" fill="{c["key"]}" textLength="{len(key) * INFO_CW:.1f}" '
        f'lengthAdjust="spacing">{escape(key, quote=False)}</text>'
        + leader(c, key_end + 6, value_x - 10, y)
        + f'<text x="{value_x:.1f}" y="{y}" fill="{c["value"]}" textLength="{value_w:.1f}" '
        f'lengthAdjust="spacing">{escape(value, quote=False)}</text>'
    )


def stat(c: dict, label: str, element_id: str, y: int) -> str:
    key_end = INFO_X + len(label) * INFO_CW + 4
    return (
        f'<text x="{INFO_X}" y="{y}" fill="{c["key"]}" textLength="{len(label) * INFO_CW:.1f}" '
        f'lengthAdjust="spacing">{label}</text>'
        + leader(c, key_end + 6, INFO_RIGHT - 70, y)
        + f'<text x="{INFO_RIGHT}" y="{y}" text-anchor="end" fill="{c["value"]}" '
        f'font-weight="600"><tspan id="{element_id}">0</tspan></text>'
    )


def build(name: str) -> str:
    c = THEMES[name]
    stroke = "" if c["border"] == "none" else f' stroke="{c["border"]}" stroke-width="1.5"'
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        f'role="img" aria-labelledby="t d" font-family="ui-monospace, SFMono-Regular, Menlo, '
        f"Consolas, 'Liberation Mono', monospace\">",
        '  <title id="t">unax@github — profile card</title>',
        '  <desc id="d">ASCII portrait, role, focus, languages, tools, contact and public GitHub '
        "statistics for UnaxAlonso0.</desc>",
        f'  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="14" fill="{c["bg"]}"{stroke}/>',
        f"  {portrait(c)}",
        f'  <g font-size="{INFO_FS}" xml:space="preserve">',
    ]
    y = 98
    out.append("    " + title(c, "unax@github", y, c["name"]))
    y += ROW_H + 4
    for key, value in INFO:
        out.append("    " + row(c, key, value, y))
        y += ROW_H
    y += ROW_H - 4
    out.append("    " + title(c, "- Contact", y, c["text"]))
    y += ROW_H + 4
    for key, value in CONTACT:
        out.append("    " + row(c, key, value, y))
        y += ROW_H
    y += ROW_H - 4
    out.append("    " + title(c, "- GitHub Stats", y, c["text"]))
    y += ROW_H + 4
    for label, element_id in STATS:
        out.append("    " + stat(c, label, element_id, y))
        y += ROW_H
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
