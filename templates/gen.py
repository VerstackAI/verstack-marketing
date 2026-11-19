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
    return f'<rect x="{x - size / 2:.1f}" y="{y - size / 2:.1f}" width="{size}" height="{size}" fill="{fill or color}" stroke="{color}" stroke-width="1"/>'


def page(w, h, body, bg, css_extra=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><link rel="stylesheet" href="line.css">
<style>body {{ background: {bg}; }} .frame {{ width: {w}px; height: {h}px; background: {bg}; }} {css_extra}</style></head>
<body><div class="frame">
{body}
</div></body></html>
"""


# 1. Spec sheet, 1080 x 1350, dark ------------------------------------------------
def spec_sheet():
    W, H = 1080, 1350
    wl, wt, ww, wh = 56, 88, 968, 1206
    pl, pt = wl + 10, wt + 40
    pw = ww - 20
    parts = []
    parts.append(f'<div class="abs" style="left:{wl}px; top:{wt}px; width:{ww}px; height:{wh}px; background:var(--ground-800); border:1px solid rgb(255 255 255 / 0.08); border-radius:22px"></div>')
    parts.append(f'<div class="abs dot meta" style="left:{wl + 18}px; top:{wt + 11}px; color:var(--fg-muted); font-size:13px">Repeat repair check.pdf</div>')
    parts.append(f'<div class="abs" style="left:{pl}px; top:{pt}px; width:{pw}px; height:{wh - 50}px; background:var(--ground-900); border-radius:14px"></div>')
    # header: title, meta, description
    parts.append(f'<h1 class="abs title" style="left:{pl + 28}px; top:{pt + 26}px; font-size:76px; color:var(--mist)">Repeat repair<br>check</h1>')
    parts.append(f'<div class="abs meta" style="left:{pl + 500}px; top:{pt + 30}px; color:var(--fg-subtle); font-size:12px">Verstack<br>Product update, November 2026</div>')
    parts.append(f'<p class="abs" style="left:{pl + 500}px; top:{pt + 138}px; width:390px; font-size:18px; line-height:1.45; color:var(--mist)">A resident reports a fault. Verstack checks the unit&#8217;s repair history and budget before a trade is booked, and flags the repeat work order for the manager.</p>')
    # three small tiles
    ty, th, gap = pt + 330, 300, 12
    tw = (pw - 2 * 28 - 2 * gap) / 3
    for i, (name, label, height) in enumerate([("dishwasher", "Dishwasher", 210), ("water-heater", "Water heater", 220), ("condenser", "Condenser", 196)]):
        tl = pl + 28 + i * (tw + gap)
        x0, y0, vw, vh = A[name]["viewBox"]
        iw = vw * height / vh
        parts.append(f'<div class="tile" style="left:{tl:.0f}px; top:{ty}px; width:{tw:.0f}px; height:{th}px"><span class="dot">{label}</span></div>')
        parts.append(img(name, "dark", (tl + (tw - iw) / 2, ty + 62, iw, height)))
    # big tile with the unit plan
    by = ty + th + gap
    bh = pt + wh - 50 - 28 - by
    bw = pw - 56
    bl = pl + 28
    parts.append(f'<div class="tile" style="left:{bl}px; top:{by}px; width:{bw}px; height:{bh}px"><span class="dot">Unit 214, Mill Court</span></div>')
    box, pt_of = place("unit-plan", bl + 36, by + 64, height=bh - 96)
    parts.append(img("unit-plan", "dark", box))
    dx, dy = pt_of("dishwasher")
    lx, ly = bl + bw - 210, by + 70
    parts.append(f'<svg class="leaders" width="{W}" height="{H}"><polyline points="{dx},{dy} {dx},{ly + 8} {lx - 12},{ly + 8}" stroke="#f8fafc"/>{node(dx, dy, "#f8fafc", 7, "#171a19")}</svg>')
    parts.append(f'<div class="callout" style="left:{lx}px; top:{ly - 4}px; width:190px; color:var(--mist)"><div class="dot live" style="font-size:15px">Dishwasher</div><div class="s" style="color:var(--fg-muted)">2 work orders since March. Flagged as a repeat repair.</div></div>')
    return page(W, H, "\n".join(parts), "var(--ground-950)")


# 2. Data plate, 1080 x 1350, light -----------------------------------------------
def data_plate():
    W, H = 1080, 1350
    parts = []
    parts.append('<h1 class="abs" style="left:56px; top:48px; font-size:230px; line-height:0.9; letter-spacing:-0.06em; font-weight:400; color:var(--ink-900)">Turns</h1>')
    box, pt_of = place("building", 36, 400, width=580)
    parts.append(img("building", "light", box))
    rows = [
        ("Unit 214", True, "Make ready", "Paint, clean", "Ready by 1 Sep"),
        ("Unit 118", False, "Scheduled", "Clean", "Ready by 29 Aug"),
        ("Unit 402", False, "Review", "Clean", "Ready by 28 Aug"),
    ]
    x0, y = 612, 430
    for i, (unit, live, stage, work, ready) in enumerate(rows):
        badge = (f'<span style="display:inline-grid; place-items:center; width:22px; height:22px; border-radius:50%; background:{"var(--lime)" if live else "transparent"}; '
                 f'box-shadow:{"none" if live else "inset 0 0 0 1.25px var(--ink-700)"}; font-size:12px; font-weight:600; color:#000; margin-left:10px">{i + 1}</span>')
        parts.append(f'<div class="abs" style="left:{x0}px; top:{y}px; width:412px; border-top:1px solid var(--ink-700)"></div>')
        parts.append(f'<div class="abs" style="left:{x0}px; top:{y + 16}px; font-size:22px; font-weight:400; letter-spacing:-0.02em; color:var(--ink-900); display:flex; align-items:center">{unit}{badge}</div>')
        parts.append(f'<div class="abs" style="left:{x0 + 210}px; top:{y + 16}px; width:214px; color:var(--ink-900)"><div style="font-size:22px; letter-spacing:-0.02em; line-height:1.15">{stage}</div>'
                     f'<div class="meta" style="margin-top:12px; color:var(--ink-500)">{work}</div><div class="meta" style="margin-top:4px; color:var(--ink-500)">{ready}</div></div>')
        y += 200
    parts.append(f'<div class="abs" style="left:{x0}px; top:{y}px; width:412px; border-top:1px solid var(--ink-700)"></div>')
    parts.append('<div class="abs meta" style="left:56px; bottom:56px; color:var(--ink-500)">Mill Court turns, this week</div>')
    parts.append('<img class="abs" src="../brand/logos/verstack-lockup-black.svg" style="right:56px; bottom:56px; height:24px" alt="Verstack">')
    return page(W, H, "\n".join(parts), "var(--surface-100)")


# 3. Annotated drawing, 1920 x 1080, dark grid ------------------------------------
def annotated():
    W, H = 1920, 1080
    grid = ("background-image: linear-gradient(rgb(255 255 255 / 0.035) 1px, transparent 1px), linear-gradient(90deg, rgb(255 255 255 / 0.035) 1px, transparent 1px);"
            " background-size: 60px 60px; background-position: -1px -1px;")
    parts = [f'<div class="abs" style="inset:0; {grid}"></div>']
    pluses = "".join(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10"/>' for x in range(120, W, 240) for y in range(120, H, 240))
    parts.append(f'<svg class="leaders" width="{W}" height="{H}"><g stroke="rgb(255 255 255 / 0.22)" stroke-width="1">{pluses}</g></svg>')
    parts.append('<p class="abs" style="left:560px; top:64px; width:800px; text-align:center; font-size:18px; line-height:1.55; color:var(--mist)">Unit 214, Mill Court. Every work order, quote and inspection lands on the unit&#8217;s record, room by room, so the next decision starts with the history.</p>')
    parts.append('<div class="abs" style="left:120px; top:200px; width:1680px; border-top:1px solid var(--line-dark)"></div>')
    box, pt_of = place("unit-plan", 560, 262, width=1060)
    parts.append(img("unit-plan", "dark", box))
    callouts = [
        ("dishwasher", "1.1", "Kitchen", "Dishwasher, repeat repair", True, (1480, 260)),
        ("bath", "1.2", "Bathroom", "No open findings", False, (150, 520)),
        ("entry", "1.3", "Entry", "Move-out walk recorded", False, (150, 860)),
        ("bed", "1.4", "Bedroom", "Paint, ready by 1 Sep", False, (1560, 900)),
    ]
    lines = []
    for anchor, k, name, sub, live, (lx, ly) in callouts:
        ax, ay = pt_of(anchor)
        if lx > ax:
            pts = f"{ax},{ay} {ax},{ly + 10} {lx - 14},{ly + 10}"
        else:
            pts = f"{ax},{ay} {ax},{ly + 10} {lx + 250},{ly + 10}"
        lines.append(f'<polyline points="{pts}" stroke="#f8fafc"/>' + node(ax, ay, "#f8fafc", 7, "#a5fc22" if live else "#171a19"))
        parts.append(f'<div class="callout" style="left:{lx}px; top:{ly - 2}px; width:236px; color:var(--mist)"><div class="k" style="color:var(--fg-subtle)">{k}</div><div class="n">{name}</div><div class="s" style="color:var(--fg-muted)">{sub}</div></div>')
    parts.append('<div class="abs mono" style="left:120px; top:244px; font-size:15px; font-weight:500; color:var(--mist)">1.0&nbsp;&nbsp;Unit record</div>')
    parts.append(f'<svg class="leaders" width="{W}" height="{H}">{"".join(lines)}</svg>')
    parts.append('<img class="abs" src="../brand/logos/verstack-lockup-white.svg" style="left:120px; bottom:72px; height:26px" alt="Verstack">')
    return page(W, H, "\n".join(parts), "var(--ground-950)")


# 4. Email hero, 1104 x 552 (shown at 552 x 276), dark ---------------------------
def email_hero():
    W, H = 1104, 552
    parts = []
    box, pt_of = place("unit-plan", 24, 44, width=700)
    parts.append(img("unit-plan", "dark", box))
    dx, dy = pt_of("dishwasher")
    lx, ly = 770, 120
    parts.append(f'<svg class="leaders" width="{W}" height="{H}"><polyline points="{dx},{dy} {dx},{ly + 24} {lx - 22},{ly + 24}" stroke="#f8fafc" stroke-width="2.5"/>{node(dx, dy, "#f8fafc", 14, "#171a19")}</svg>')
    parts.append(f'<div class="callout" style="left:{lx}px; top:{ly - 4}px; width:320px; color:var(--mist)"><div class="dot live" style="font-size:44px; gap:16px; letter-spacing:-0.02em">Dishwasher</div><div class="s" style="font-size:34px; line-height:1.3; color:var(--fg-muted); margin-top:12px">Unit 214<br>Repeat repair</div></div>')
    return page(W, H, "\n".join(parts), "var(--ground-900)", ".dot::before { width: 18px; height: 18px; }")


# 5. Link preview, 1200 x 630, dark ----------------------------------------------
def link_preview():
    W, H = 1200, 630
    parts = []
    box, pt_of = place("building", 610, 46, height=538)
    parts.append(img("building", "dark", box))
    parts.append('<h1 class="abs" style="left:64px; top:150px; width:560px; font-size:72px; line-height:0.98; letter-spacing:-0.05em; font-weight:400; color:var(--mist)">Autonomous maintenance management.</h1>')
    parts.append('<img class="abs" src="../brand/logos/verstack-lockup-white.svg" style="left:64px; top:64px; height:30px" alt="Verstack">')
    parts.append('<div class="abs meta" style="left:64px; bottom:60px; color:var(--fg-muted); font-size:16px">verstack.ai</div>')
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
