"""Generate the generic motion example clips (HTML, 1920 x 1080).

Each clip is one HTML page with inline drawings and a renderAt(t) function.
Open it in a browser to watch it loop; render.py turns it into an MP4.

The look follows verstack.ai: light (mist) cards with a 40px radius on the dark
ground, ink drawings inside the cards, white type on the dark. The scan gradient
(white to lime) only appears while moving: a sweep across a card or a tile scan.

Run: python3 motion/gen.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "illustrations" / "anchors.json").read_text())
SVG = ROOT / "illustrations" / "svg"
OUT = ROOT / "motion"
W, H = 1920, 1080
SEAM = 16  # dark ground showing between and around cards
INK, INK_SOFT, MIST, LIME, GROUND = "#30303a", "#6d6d78", "#f8fafc", "#a5fc22", "#171a19"


def place(name, left, top, width=None, height=None):
    x0, y0, w, h = A[name]["viewBox"]
    k = width / w if width else height / h
    pts = A[name]["points"]

    def point(a):
        ax, ay = pts[a]
        return round(left + (ax - x0) * k, 1), round(top + (ay - y0) * k, 1)

    return (left, top, w * k, h * k), point


def inline(name, theme, box, sid):
    l, t, w, h = box
    s = (SVG / f"{name}-{theme}.svg").read_text().strip()
    return s.replace("<svg ", f'<svg id="{sid}" class="abs" style="left:{l:.0f}px; top:{t:.0f}px; width:{w:.0f}px; height:{h:.0f}px; overflow:visible" ', 1)


def card(x, y, w, h, cid, radius=40):
    return f'<div id="{cid}" class="card" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px; border-radius:{radius}px"></div>'


def sweep_layer(x, y, w, h, sid, radius=40):
    """Overlay that clips the sweep band to a card's shape. Goes above the card's contents."""
    return (f'<div class="sweep-clip" style="left:{x}px; top:{y}px; width:{w}px; height:{h}px; border-radius:{radius}px">'
            f'<div id="{sid}" class="sweep"></div></div>')


def lockup(x, y, h=26, color="white"):
    return f'<img class="abs" src="../brand/logos/verstack-lockup-{color}.svg" style="left:{x}px; top:{y}px; height:{h}px" alt="Verstack">'


def headline(x, y, w, text, hid, size=72):
    return (f'<h1 id="{hid}" class="abs hide" style="left:{x}px; top:{y}px; width:{w}px; font-size:{size}px; line-height:1.02; '
            f'letter-spacing:-0.045em; font-weight:400; color:var(--mist)">{text}</h1>')


def page(title, duration, body, script):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="../templates/line.css">
<script src="motion.js"></script>
<style>body {{ background: var(--ground-900); margin: 0; }} .frame {{ width: {W}px; height: {H}px; background: var(--ground-900); }}
.hide {{ opacity: 0; }}
.card {{ position: absolute; background: var(--mist); }}
.sweep-clip {{ position: absolute; overflow: hidden; pointer-events: none; }}
.sweep {{ position: absolute; top: 0; bottom: 0; left: -20%; width: 140%; opacity: 0.22; visibility: hidden;
  background: linear-gradient(90deg, #f8fafc 0%, #eefbd7 12%, #d8f7a3 26%, #baf85d 42%, #a5fc22 58%, #8ff741 74%, #7ff553 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, rgba(0,0,0,.15) 7%, #000 22%, #000 78%, rgba(0,0,0,.15) 93%, transparent 100%); }}
.scan {{ position: absolute; inset: 0; border-radius: inherit; opacity: 0;
  background: linear-gradient(180deg, #f8fafc 0%, #eefbd7 12%, #d8f7a3 26%, #baf85d 42%, #a5fc22 58%, #8ff741 74%, #7ff553 100%); }}
.leader {{ fill: none; stroke: {INK}; stroke-width: 1; }}
.ink {{ color: var(--ink-700); }} .ink-soft {{ color: var(--ink-500); }}
.ink .dot.live::before, .dot.live.ink::before {{ box-shadow: inset 0 0 0 1.25px var(--ink-700); }}
</style></head>
<body><div class="frame">
{body}
</div>
<script>
window.DURATION = {duration};
{script}
window.addEventListener("load", () => {{
  document.fonts.ready.then(() => {{
    setup();
    window.READY = true;
    if (!location.search.includes("render")) {{
      const start = performance.now();
      const loop = () => {{ renderAt(((performance.now() - start) / 1000) % (DURATION + 1.2)); requestAnimationFrame(loop); }};
      loop();
    }} else {{ renderAt(0); }}
  }});
}});
</script>
</body></html>
"""


# Two-panel frame: a light card on the left, white type on the dark at the right.
CX, CY, CW, CH = SEAM, SEAM, 1236, H - 2 * SEAM
RX, RW = CX + CW + 84, 500  # right column on the dark ground


def callout_html(cid, x, y, name, sub, live=False, width=230):
    dot = "dot live" if live else "dot"
    return (f'<div id="{cid}" class="abs hide ink" style="left:{x}px; top:{y}px; width:{width}px">'
            f'<div class="{dot}" style="font-size:19px">{name}</div>'
            f'<div class="ink-soft" style="font-size:16px; line-height:1.35; margin-top:6px">{sub}</div></div>')


def caption(text):
    return f'<div id="cap" class="abs mono hide ink-soft" style="left:{CX + 56}px; top:{CY + 52}px; font-size:15px; font-weight:500">{text}</div>'


# A. Draw, then highlight --------------------------------------------------------
def draw_highlight():
    box, pt = place("building", CX + 70, CY + 120, height=800)
    ux, uy = pt("unit-right")
    lx = CX + CW - 270
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("building", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 16},{uy}"/>'
        f'<rect id="nd" x="{ux - 3.5}" y="{uy - 3.5}" width="7" height="7" fill="{LIME}" stroke="{INK}" opacity="0"/></svg>',
        callout_html("t3", lx, uy - 14, "Unit 214", "Make ready. Paint and clean, ready by 1 Sep.", live=True),
        caption("1.0&nbsp;&nbsp;Mill Court"),
        sweep_layer(CX, CY, CW, CH, "sw"),
        f'<div id="t1" class="abs dot hide" style="left:{RX}px; top:128px; color:var(--mist); font-size:20px">Product update</div>',
        headline(RX, 184, RW, "Every unit, on one record.", "t2"),
        f'<p id="t4" class="abs hide" style="left:{RX}px; top:372px; width:440px; font-size:20px; line-height:1.45; color:var(--fg-muted)">Work orders, quotes and inspections land on the unit they belong to.</p>',
        lockup(RX, 990),
    ])
    script = """
let items;
function setup() { items = prepDraw(document.getElementById("d")); }
function renderAt(t) {
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  sweep(document.getElementById("sw"), t, 0.25, 1.7);
  enter(document.getElementById("cap"), t, 0.4);
  drawAt(items, t, 0.5, 2.2, 0.7, "#f8fafc", 3.6);
  enter(document.getElementById("t1"), t, 0.3);
  leaderAt(document.getElementById("ld"), t, 4.0);
  document.getElementById("nd").setAttribute("opacity", t >= 4.0 ? 1 : 0);
  enter(document.getElementById("t3"), t, 4.2, 0.48, 8);
  enter(document.getElementById("t2"), t, 4.7);
  enter(document.getElementById("t4"), t, 5.1);
}"""
    return page("Draw and highlight", 7.0, body, script)


# B. Explode -----------------------------------------------------------------------
def explode():
    box, pt = place("building-floors", CX + 150, CY + 280, height=620)
    ux, uy = pt("unit-right")
    lx = CX + CW - 270
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("building-floors", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 16},{uy}"/>'
        f'<rect id="nd" x="{ux - 3.5}" y="{uy - 3.5}" width="7" height="7" fill="{LIME}" stroke="{INK}" opacity="0"/></svg>',
        callout_html("t3", lx, uy - 14, "Floor 3, Unit 214", "2 open work orders.", live=True),
        caption("1.0&nbsp;&nbsp;Mill Court, 5 floors"),
        sweep_layer(CX, CY, CW, CH, "sw"),
        f'<div id="t1" class="abs dot hide" style="left:{RX}px; top:128px; color:var(--mist); font-size:20px">Portfolio</div>',
        headline(RX, 184, RW, "Open any floor.", "t2"),
        f'<p id="t4" class="abs hide" style="left:{RX}px; top:300px; width:440px; font-size:20px; line-height:1.45; color:var(--fg-muted)">Every floor and unit keeps its own history.</p>',
        lockup(RX, 990),
    ])
    script = f"""
let items, floors, roof, ld, nd, t3;
const GAP = 44, UY = {uy}, UX = {ux}, LX = {lx};
function setup() {{
  items = prepDraw(document.getElementById("d"));
  floors = [0, 1, 2, 3, 4].map((k) => document.getElementById("floor-" + k));
  roof = document.getElementById("roof");
  ld = document.getElementById("ld"); nd = document.getElementById("nd"); t3 = document.getElementById("t3");
}}
function amount(t, k) {{
  const out = ease(prog(t, 1.3 + (5 - k) * 0.08, 0.64));
  const back = ease(prog(t, 5.0 + k * 0.06, 0.64));
  return out * (1 - back);
}}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  sweep(document.getElementById("sw"), t, 0.25, 1.7);
  enter(document.getElementById("cap"), t, 0.4);
  drawAt(items, t, 0.4, 0.9, 0.45, "#f8fafc", 2.5);
  const svg = document.getElementById("d");
  const scale = svg.getBoundingClientRect().height / svg.viewBox.baseVal.height;
  floors.forEach((g, k) => g.setAttribute("transform", `translate(0 ${{-k * GAP * amount(t, k) / scale}})`));
  roof.setAttribute("transform", `translate(0 ${{-5 * GAP * amount(t, 5) / scale}})`);
  const y = UY - 2 * GAP * amount(t, 2);
  ld.setAttribute("points", `${{UX}},${{y}} ${{LX - 16}},${{y}}`);
  nd.setAttribute("y", y - 3.5);
  leaderAt(ld, t, 2.9);
  nd.setAttribute("opacity", t >= 2.9 && t < 4.9 ? 1 : 0);
  ld.style.opacity = t < 4.9 ? 1 : 0;
  enter(t3, t, 3.1, 0.48, 8);
  if (t >= 4.6) t3.style.opacity = 1 - prog(t, 4.6, 0.3);
  t3.style.top = (y - 14) + "px";
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("t2"), t, 5.6);
  enter(document.getElementById("t4"), t, 6.0);
}}"""
    return page("Explode", 7.4, body, script)


# C. Capture walk -------------------------------------------------------------------
def capture_walk():
    box, pt = place("unit-plan", CX + 68, CY + 150, width=1100)
    route = [pt(f"route-{i}") for i in range(15)]
    rooms = [("Entry", "0:00", 0, "entry"), ("Bathroom", "0:48", 3, "bath"), ("Kitchen", "1:52", 8, "kitchen"),
             ("Living room", "3:10", 9.6, "living"), ("Bedroom", "4:25", 14, "bed")]
    pts = " ".join(f"{x},{y}" for x, y in route)
    nodes = "".join(f'<rect id="n{i}" x="{pt(a)[0] - 3.5}" y="{pt(a)[1] - 3.5}" width="7" height="7" fill="{MIST}" stroke="{INK}" opacity="0"/>' for i, (_, _, _, a) in enumerate(rooms))
    rows = []
    for i, (name, time, _, _) in enumerate(rooms):
        y = 330 + i * 92
        rows.append(f'<div id="r{i}" class="abs hide" style="left:{RX}px; top:{y}px; width:{RW}px; height:92px; border-top:1px solid var(--line-dark); color:var(--mist)">'
                    f'<span class="abs mono" style="left:0; top:32px; font-size:14px; color:var(--fg-subtle)">0{i + 1}</span>'
                    f'<span class="abs" style="left:56px; top:25px; font-size:28px; letter-spacing:-0.02em">{name}</span>'
                    f'<span class="abs mono" style="right:0; top:32px; font-size:16px; color:var(--fg-muted)">{time}</span></div>')
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("unit-plan", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="trail" points="{pts}" fill="none" stroke="rgb(48 48 58 / 0.55)" stroke-width="1.5" stroke-linejoin="round"/>{nodes}'
        f'<circle id="ring" r="16" fill="none" stroke="{INK}" stroke-width="1"/><circle id="dotm" r="9" fill="{LIME}" stroke="{INK}" stroke-width="1.5"/></svg>',
        caption("1.0&nbsp;&nbsp;Unit 214, Mill Court"),
        sweep_layer(CX, CY, CW, CH, "sw"),
        f'<div id="t1" class="abs hide" style="left:{RX}px; top:128px; color:var(--mist)"><div class="dot" style="font-size:20px">Capture walk</div>'
        f'<div style="margin-top:10px; font-size:18px; line-height:1.4; color:var(--fg-subtle)">Phone video, room by room.</div></div>',
        *rows,
        f'<div id="t2" class="abs hide" style="left:{RX}px; top:802px; width:{RW}px; border-top:1px solid var(--line-dark); padding-top:22px; color:var(--mist); font-size:32px; letter-spacing:-0.03em">5 rooms, 6 minutes.'
        f'<div class="dot" style="display:flex; font-size:18px; letter-spacing:0; margin-top:14px; color:var(--fg-muted)">Record ready for review</div></div>',
        lockup(RX, 990),
    ])
    stops = json.dumps([r[2] for r in rooms])
    script = f"""
let items, trail, total, cum, ring, dotm;
const STOPS = {stops};
function setup() {{
  items = prepDraw(document.getElementById("d"));
  trail = document.getElementById("trail"); ring = document.getElementById("ring"); dotm = document.getElementById("dotm");
  total = trail.getTotalLength();
  const p = trail.points; cum = [0];
  for (let i = 1; i < p.numberOfItems; i++) {{ const a = p.getItem(i - 1), b = p.getItem(i); cum.push(cum[i - 1] + Math.hypot(b.x - a.x, b.y - a.y)); }}
  trail.style.strokeDasharray = `${{total + 2}} ${{total + 2}}`;
}}
const at = (idx) => {{ const i = Math.floor(idx), f = idx - i; return i + 1 < cum.length ? cum[i] + (cum[i + 1] - cum[i]) * f : cum[i]; }};
const smooth = (x) => x * x * (3 - 2 * x);
function invSmooth(y) {{ let lo = 0, hi = 1; for (let i = 0; i < 30; i++) {{ const m = (lo + hi) / 2; if (smooth(m) < y) lo = m; else hi = m; }} return (lo + hi) / 2; }}
const T0 = 1.6, TD = 6.0;
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  sweep(document.getElementById("sw"), t, 0.25, 1.7);
  enter(document.getElementById("cap"), t, 0.4);
  drawAt(items, t, 0.4, 1.0, 0.5, "#f8fafc");
  enter(document.getElementById("t1"), t, 0.3);
  const L = total * smooth(prog(t, T0, TD));
  trail.style.strokeDashoffset = total + 2 - L;
  const q = trail.getPointAtLength(Math.max(0.01, L));
  const vis = t >= T0 - 0.2 ? 1 : 0;
  dotm.setAttribute("cx", q.x); dotm.setAttribute("cy", q.y); dotm.setAttribute("opacity", vis);
  const pulse = (t * 1.25) % 1;
  ring.setAttribute("cx", q.x); ring.setAttribute("cy", q.y); ring.setAttribute("r", 10 + 18 * pulse); ring.setAttribute("opacity", vis * (1 - pulse) * 0.8);
  STOPS.forEach((s, i) => {{
    const reached = L >= at(s) - 0.5 && t >= T0 - 0.2;
    document.getElementById("n" + i).setAttribute("opacity", reached ? 1 : 0);
    enter(document.getElementById("r" + i), t, T0 + TD * invSmooth(at(s) / total), 0.4, 12);
  }});
  enter(document.getElementById("t2"), t, 7.9);
}}"""
    return page("Capture walk", 9.4, body, script)


# D. Callouts ----------------------------------------------------------------------
def callouts():
    x0, y0, w0, h0 = SEAM, SEAM, W - 2 * SEAM, H - 2 * SEAM
    grid = ("background-image: linear-gradient(rgb(48 48 58 / 0.05) 1px, transparent 1px), linear-gradient(90deg, rgb(48 48 58 / 0.05) 1px, transparent 1px);"
            " background-size: 60px 60px; background-position: -1px -1px;")
    pluses = "".join(f'<path d="M{x - 5} {y}h10M{x} {y - 5}v10"/>' for x in range(120, W, 240) for y in range(120, H, 240))
    box, pt = place("unit-plan", 560, 262, width=1060)
    items = [("dishwasher", "1.1", "Kitchen", "Dishwasher, repeat repair", True, (1480, 260)),
             ("bath", "1.2", "Bathroom", "No open findings", False, (150, 520)),
             ("entry", "1.3", "Entry", "Move-out walk recorded", False, (150, 860)),
             ("bed", "1.4", "Bedroom", "Paint, ready by 1 Sep", False, (1560, 900))]
    lines, labels = [], []
    for i, (a, k, n, s, live, (lx, ly)) in enumerate(items):
        ax, ay = pt(a)
        end = lx - 14 if lx > ax else lx + 250
        lines.append(f'<polyline id="l{i}" class="leader" points="{ax},{ay} {ax},{ly + 10} {end},{ly + 10}"/>'
                     f'<rect id="n{i}" x="{ax - 3.5}" y="{ay - 3.5}" width="7" height="7" fill="{LIME if live else MIST}" stroke="{INK}" opacity="0"/>')
        labels.append(f'<div id="c{i}" class="callout hide ink" style="left:{lx}px; top:{ly - 2}px; width:236px">'
                      f'<div class="k ink-soft">{k}</div><div class="n">{n}</div><div class="s ink-soft">{s}</div></div>')
    body = "\n".join([
        card(x0, y0, w0, h0, "card"),
        f'<div id="grid" class="abs" style="left:{x0}px; top:{y0}px; width:{w0}px; height:{h0}px; border-radius:40px; {grid}"></div>',
        f'<svg id="plus" class="leaders" width="{W}" height="{H}"><g stroke="rgb(48 48 58 / 0.2)" stroke-width="1">{pluses}</g></svg>',
        '<p id="t1" class="abs hide ink" style="left:560px; top:64px; width:800px; text-align:center; font-size:18px; line-height:1.55">Every work order, quote and inspection lands on the unit&#8217;s record, room by room.</p>',
        '<div class="abs" style="left:120px; top:200px; width:1680px; border-top:1px solid var(--line-light)"></div>',
        '<div id="t2" class="abs mono hide ink" style="left:120px; top:244px; font-size:15px; font-weight:500">1.0&nbsp;&nbsp;Unit record</div>',
        inline("unit-plan", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}">{"".join(lines)}</svg>',
        *labels,
        sweep_layer(x0, y0, w0, h0, "sw"),
        lockup(120, 990, color="black"),
    ])
    script = """
let items;
function setup() { items = prepDraw(document.getElementById("d")); }
function renderAt(t) {
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("grid"), t, 0.1, 0.6, 0);
  enter(document.getElementById("plus"), t, 0.1, 0.6, 0);
  sweep(document.getElementById("sw"), t, 0.25, 1.8);
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("t2"), t, 0.5);
  drawAt(items, t, 0.6, 1.6, 0.6, "#f8fafc", 2.8);
  [2.8, 3.5, 4.2, 4.9].forEach((s, i) => {
    leaderAt(document.getElementById("l" + i), t, s);
    document.getElementById("n" + i).setAttribute("opacity", t >= s ? 1 : 0);
    enter(document.getElementById("c" + i), t, s + 0.2, 0.4, 8);
  });
}"""
    return page("Callouts", 6.4, body, script)


# E. Asset tiles -------------------------------------------------------------------
def asset_tiles():
    names = [("fridge", "Fridge"), ("range", "Range"), ("washer-dryer", "Washer and dryer"),
             ("furnace", "Furnace"), ("water-heater", "Water heater"), ("electrical-panel", "Electrical panel")]
    tw, th, gap, x0, y0 = 552, 330, SEAM, 120, 330
    parts, ids = [], []
    for i, (n, label) in enumerate(names):
        c, r = i % 3, i // 3
        l, t = x0 + c * (tw + gap), y0 + r * (th + gap)
        x, y, vw, vh = A[n]["viewBox"]
        ih = 250
        iw = vw * ih / vh
        parts.append(f'<div id="tile{i}" class="card hide" style="left:{l}px; top:{t}px; width:{tw}px; height:{th}px; border-radius:24px">'
                     f'<span class="dot ink" style="position:absolute; left:22px; top:20px; font-size:17px">{label}</span></div>')
        parts.append(inline(n, "light", (l + (tw - iw) / 2, t + 62, iw, ih), f"d{i}"))
        parts.append(f'<div class="abs" style="left:{l}px; top:{t}px; width:{tw}px; height:{th}px; border-radius:24px; pointer-events:none"><div id="s{i}" class="scan"></div></div>')
        ids.append(f"d{i}")
    body = "\n".join([
        '<h1 id="t1" class="abs title hide" style="left:120px; top:100px; font-size:96px; color:var(--mist)">Assets</h1>',
        '<div id="t2" class="abs dot hide" style="left:124px; top:236px; color:var(--fg-muted); font-size:18px">Unit 214, Mill Court. Six tracked assets, each with its own history.</div>',
        *parts,
        lockup(1640, 110),
    ])
    script = f"""
let sets;
function setup() {{ sets = {json.dumps(ids)}.map((id) => prepDraw(document.getElementById(id))); }}
function renderAt(t) {{
  enter(document.getElementById("t1"), t, 0.1);
  enter(document.getElementById("t2"), t, 0.3);
  sets.forEach((items, i) => {{
    const s = 0.5 + i * 0.32;
    enter(document.getElementById("tile" + i), t, s, 0.32, 10);
    const tile = document.getElementById("tile" + i), d = document.getElementById("d" + i);
    d.style.transform = tile.style.transform;
    scanAt(document.getElementById("s" + i), t, s + 0.15, 1.3, 0.3 * parseFloat(tile.style.opacity));
    drawAt(items, t, s + 0.55, 0.9, 0.45, "#f8fafc");
  }});
}}"""
    return page("Asset tiles", 5.6, body, script)


CLIPS = {
    "draw-highlight": draw_highlight,
    "explode": explode,
    "capture-walk": capture_walk,
    "callouts": callouts,
    "asset-tiles": asset_tiles,
}
for name, fn in CLIPS.items():
    (OUT / f"{name}.html").write_text(fn())
print("clips written:", list(CLIPS))
