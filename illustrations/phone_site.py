"""The phone drawing, from the isometric phone on verstack.ai.

Source: sources/phone-site.svg, copied from the website (public/media/phones/iphone-outline.svg,
the phone in the record-capture visual). It keeps the site's geometry, rounding and line weights
(0.5 contour, 0.3 inside). This module adds the capture record button on the screen (the lime
part) and writes the light and dark versions plus the phone's anchors.

Data flow: sources/phone-site.svg -> build() -> (light svg, dark svg, anchors entry).
"""
import math
import pathlib
import re

SRC = pathlib.Path(__file__).parent / "sources" / "phone-site.svg"
LIME = "#a5fc22"

# The screen's corners on the source drawing (TL at the top end, then clockwise), the same
# quad the website warps its video into.
TL, TR, BR, BL = (130.49, 7.98), (190.73, 42.49), (70.83, 113.5), (9.08, 78.57)

# Dark version: the site's silver, rim, bezel and screen tones mapped onto the dark ground,
# lines turned light. Keys are the source colours.
DARK = {
    "#B7B5AF": "#3a3e3c", "#CECDCB": "#2a2e2c", "#3F3E3E": "#0c0d0d", "#FFFFFF": "#1e1e22",
    "#2C292A": "#f8fafc", "#282828": "#f8fafc", "#525151": "#c2c4c5", "#706F6E": "#8b8f8d",
}
SCREEN = {"light": "#FFFFFF", "dark": "#1e1e22"}


def _record_button():
    """Two ellipses lying on the screen near its bottom end: a ring and the lime button."""
    es = (BR[0] - BL[0], BR[1] - BL[1])                  # one phone width across
    el = ((TL[0] - BL[0]) / 2.0, (TL[1] - BL[1]) / 2.0)  # one phone width along (length is ~2 widths)
    mx, my = (BL[0] + BR[0]) / 2, (BL[1] + BR[1]) / 2
    cx, cy = mx + 0.34 * el[0], my + 0.34 * el[1]

    def ring(rho, n=64):
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            pts.append((cx + rho * (math.cos(a) * es[0] + math.sin(a) * el[0]),
                        cy + rho * (math.cos(a) * es[1] + math.sin(a) * el[1])))
        return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

    return (cx, cy), ring(0.13), ring(0.095)


def build():
    src = SRC.read_text()
    body = src[src.index(">", src.index("<svg")) + 1: src.rindex("</svg>")].strip()
    (cx, cy), outer, inner = _record_button()
    out = {}
    for theme in ("light", "dark"):
        b = body
        if theme == "dark":
            b = re.sub(r'#[0-9A-Fa-f]{6}', lambda m: DARK.get(m.group(0).upper(), m.group(0)), b)
        # WHY: data-ground tells the motion engine what the lime part shows before it lights.
        btn = (f'<polygon points="{outer}" fill="none" stroke="{"#f8fafc" if theme == "dark" else "#2C292A"}" stroke-width="0.3" stroke-linejoin="round"/>\n'
               f'  <polygon points="{inner}" fill="{LIME}" data-ground="{SCREEN[theme]}" stroke="{"#141416" if theme == "dark" else "#2C292A"}" stroke-width="0.3" stroke-linejoin="round"/>')
        out[theme] = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 198.4 130.6">\n  {b}\n  {btn}\n</svg>\n'
    sx = sum(p[0] for p in (TL, TR, BR, BL)) / 4
    sy = sum(p[1] for p in (TL, TR, BR, BL)) / 4
    anchors = {"viewBox": [0.0, 0.0, 198.4, 130.6],
               "points": {"record": [round(cx, 1), round(cy, 1)], "screen": [round(sx, 1), round(sy, 1)],
                          "viewfinder": [round(sx, 1), round(sy, 1)]}}
    return out["light"], out["dark"], anchors
