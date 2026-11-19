"""Generate the line-drawing layout templates from the illustration anchors.

Each template is plain HTML (edit the words freely). This script places the
drawings and computes where leader lines attach. Re-run it after changing a
drawing: python3 templates/gen.py
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "illustrations" / "anchors.json").read_text())
OUT = ROOT / "templates"
PRIVATE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
if PRIVATE and (PRIVATE / "anchors.json").exists():
    A.update(json.loads((PRIVATE / "anchors.json").read_text()))


def place(name, left, top, width=None, height=None):
    """Return (img_html, point(anchor)->(x, y)) for a drawing placed in a frame."""
    x0, y0, w, h = A[name]["viewBox"]
    k = width / w if width else height / h
    W, H = w * k, h * k
    pts = A[name]["points"]

    def point(a):
        ax, ay = pts[a]
        return round(left + (ax - x0) * k, 1), round(top + (ay - y0) * k, 1)

    return (left, top, W, H), point


def img(name, theme, box, base="../illustrations/svg"):
    l, t, w, h = box
    return f'<img class="abs" src="{base}/{name}-{theme}.svg" style="left:{l:.0f}px; top:{t:.0f}px; width:{w:.0f}px; height:{h:.0f}px" alt="">'


def node(x, y, color, size=7, fill=None):
    """Kept for the private layout's signature; public layouts draw no nodes."""
    return ""


def page(w, h, body, bg, css_extra=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="line.css">
<style>body {{ background: {bg}; }} .frame {{ width: {w}px; height: {h}px; background: {bg}; }} {css_extra}</style></head>
<body><div class="frame">
{body}
</div></body></html>
"""


# Shared pieces. Sparse and bold: headlines fill their space, at most two callouts,
# no text under 28px at full size, no index numbers, no small marks.
def card(x, y, w, h, radius=40, bg="var(--mist)"):
    return f'<div class="abs" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px; background:{bg}; border-radius:{radius}px"></div>'


def headline(text, x, y, w, size, color="var(--mist)"):
    return (f'<h1 class="abs" style="left:{x}px; top:{y}px; width:{w}px; font-size:{size}px; line-height:0.98; text-wrap:balance; '
            f'letter-spacing:-0.05em; font-weight:400; color:{color}">{text}</h1>')


def popup(x, y, name, sub, width=360, name_px=40, sub_px=28, ink=True):
    c1, c2 = ("var(--ink-700)", "var(--ink-500)") if ink else ("var(--mist)", "var(--fg-muted)")
    return (f'<div class="abs" style="left:{x}px; top:{y}px; width:{width}px; color:{c1}">'
            f'<div style="font-size:{name_px}px; line-height:1.05; font-weight:600; letter-spacing:-0.03em">{name}</div>'
            f'<div style="font-size:{sub_px}px; line-height:1.25; margin-top:10px; color:{c2}">{sub}</div></div>')


def leaders(W, H, *pts, color="#30303a", width=1.5):
    lines = "".join(f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}"/>' for p in pts)
    return f'<svg class="leaders" width="{W}" height="{H}">{lines}</svg>'


def lockup(x, y, h=34, color="white", side="left"):
    pos = f"left:{x}px" if side == "left" else f"right:{x}px"
    return f'<img class="abs" src="../brand/logos/verstack-lockup-{color}.svg" style="{pos}; top:{y}px; height:{h}px" alt="Verstack">'


# 1. Spec sheet (LinkedIn feed), 1080 x 1350: light card with the drawing, headline on the dark
def spec_sheet():
    W, H = 1080, 1350
    parts = [card(16, 16, W - 32, 830)]
    box, pt_of = place("unit-plan", 74, 150, width=900)
    parts.append(img("unit-plan", "light", box))
    dx, dy = pt_of("dishwasher")
    parts.append(leaders(W, H, f"{dx},{dy} {dx},{dy - 120} {dx + 140},{dy - 120}"))
    parts.append(popup(dx + 162, dy - 146, "Dishwasher", "Flagged as a repeat repair", width=380))
    parts.append(headline("Repeat repairs get flagged first.", 56, 900, 968, 104))
    parts.append(lockup(56, 1262))
    parts.append('<div class="abs dot live" style="right:56px; top:1260px; font-size:32px; gap:14px; color:var(--mist)">Live</div>')
    return page(W, H, "\n".join(parts), "var(--ground-900)", ".dot::before { width: 14px; height: 14px; }")


# 2. Data plate, 1080 x 1350, light: a big title, the building, three bold rows
def data_plate():
    W, H = 1080, 1350
    parts = []
    parts.append('<h1 class="abs" style="left:56px; top:48px; font-size:230px; line-height:0.9; letter-spacing:-0.06em; font-weight:400; color:var(--ink-900)">Turns</h1>')
    box, pt_of = place("building", 36, 420, width=560)
    parts.append(img("building", "light", box))
    rows = [("Unit 214", "Make ready", "Ready by 1 Sep"), ("Unit 118", "Scheduled", "Ready by 29 Aug"), ("Unit 402", "Review", "Ready by 28 Aug")]
    x0, y = 612, 400
    for unit, stage, ready in rows:
        parts.append(f'<div class="abs" style="left:{x0}px; top:{y}px; width:412px; border-top:1.5px solid var(--ink-700)"></div>')
        parts.append(f'<div class="abs" style="left:{x0}px; top:{y + 24}px; width:412px; color:var(--ink-900)">'
                     f'<div style="font-size:44px; font-weight:600; letter-spacing:-0.03em; line-height:1.05">{unit}</div>'
                     f'<div style="font-size:34px; letter-spacing:-0.02em; margin-top:10px">{stage}</div>'
                     f'<div style="font-size:28px; margin-top:6px; color:var(--ink-500)">{ready}</div></div>')
        y += 230
    parts.append(f'<div class="abs" style="left:{x0}px; top:{y}px; width:412px; border-top:1.5px solid var(--ink-700)"></div>')
    parts.append(lockup(56, 1260, color="black"))
    return page(W, H, "\n".join(parts), "var(--surface-100)")


# 3. Annotated drawing, 1920 x 1080: one full light card, a headline, two callouts
def annotated():
    W, H = 1920, 1080
    parts = [card(16, 16, W - 32, H - 32)]
    parts.append(headline("Every job lands on the room it belongs to.", 112, 112, 780, 104, color="var(--ink-700)"))
    box, pt_of = place("unit-plan", 760, 290, width=1060)
    parts.append(img("unit-plan", "light", box))
    dx, dy = pt_of("dishwasher")
    bx, by = pt_of("bath")
    parts.append(leaders(W, H, f"{dx},{dy} {dx},{dy - 150} {dx + 200},{dy - 150}", f"{bx},{by} 520,{by}"))
    parts.append(popup(dx + 224, dy - 176, "Dishwasher", "Repeat repair, flagged"))
    parts.append(popup(112, by - 24, "Bathroom", "Leak fixed, photos on file", width=380))
    parts.append(lockup(112, 950, color="black"))
    return page(W, H, "\n".join(parts), "var(--ground-900)")


# 4. Email hero, 1104 x 552 (shown at 552 x 276), dark: the plan and one big callout
def email_hero():
    W, H = 1104, 552
    parts = []
    box, pt_of = place("unit-plan", 24, 44, width=700)
    parts.append(img("unit-plan", "dark", box))
    dx, dy = pt_of("dishwasher")
    lx, ly = 770, 120
    parts.append(leaders(W, H, f"{dx},{dy} {dx},{ly + 24} {lx - 22},{ly + 24}", color="#f8fafc", width=2.5))
    parts.append(f'<div class="callout" style="left:{lx}px; top:{ly - 4}px; width:320px; color:var(--mist)"><div class="dot live" style="font-size:44px; gap:16px; letter-spacing:-0.02em">Dishwasher</div><div class="s" style="font-size:34px; line-height:1.3; color:var(--fg-muted); margin-top:12px">Unit 214<br>Repeat repair</div></div>')
    return page(W, H, "\n".join(parts), "var(--ground-900)", ".dot::before { width: 18px; height: 18px; }")


# 5. Link preview, 1200 x 630: headline on the dark, the building on a light card
def link_preview():
    W, H = 1200, 630
    parts = [card(600, 16, 584, 598, radius=32)]
    box, pt_of = place("building", 640, 60, height=500)
    parts.append(img("building", "light", box))
    parts.append(lockup(64, 64))
    parts.append(headline("Autonomous maintenance management.", 64, 150, 500, 80))
    parts.append('<div class="abs" style="left:64px; top:530px; font-size:30px; letter-spacing:-0.01em; color:var(--fg-muted)">verstack.ai</div>')
    return page(W, H, "\n".join(parts), "var(--ground-900)")


(OUT / "spec-sheet-1080x1350.html").write_text(spec_sheet())
(OUT / "data-plate-1080x1350.html").write_text(data_plate())
(OUT / "annotated-1920x1080.html").write_text(annotated())
(OUT / "email-hero-1104x552.html").write_text(email_hero())
(OUT / "link-preview-1200x630.html").write_text(link_preview())
if PRIVATE:
    PRIVATE.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(PRIVATE))
    from exploded_layout import exploded
    html = exploded(str(PRIVATE / "svg"), place, img, node, page).replace('href="line.css"', f'href="{OUT / "line.css"}"').replace("../brand/", f"{ROOT}/brand/")
    (PRIVATE / "exploded-1080x1350.html").write_text(html)
print("templates written")
