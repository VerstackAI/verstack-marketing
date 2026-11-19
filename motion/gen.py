"""Generate the generic motion example clips (HTML, 1920 x 1080).

Each clip is one HTML page with inline drawings and a renderAt(t) function.
Open it in a browser to watch it loop; render.py turns it into an MP4.

The look follows verstack.ai: light (mist) cards with a 40px radius on the dark
ground, ink drawings inside the cards, white type on the dark. Sparse and bold:
big headlines that fill their column, at most two callouts, no text under 28px,
no index numbers, no small marks. The scan gradient appears once per video at
most: one faint sweep, here only in draw-highlight.

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
INK, LIME, MIST = "#30303a", "#a5fc22", "#f8fafc"

# Two-panel frame: a light card on the left, white type on the dark at the right.
CX, CY, CW, CH = SEAM, SEAM, 1110, H - 2 * SEAM
RX, RW = CX + CW + 80, 600  # right column on the dark ground
TOP = 96                    # top of the type column


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


def lockup(x, y, h=34, color="white"):
    return f'<img class="abs" src="../brand/logos/verstack-lockup-{color}.svg" style="left:{x}px; top:{y}px; height:{h}px" alt="Verstack">'


def headline(hid, text, x=RX, y=TOP, w=RW, color="var(--mist)"):
    """A headline fitted to its column by fitText() in setup()."""
    return (f'<h1 id="{hid}" class="abs hide fit" style="left:{x}px; top:{y}px; width:{w}px; line-height:0.98; text-wrap:balance; '
            f'letter-spacing:-0.05em; font-weight:400; color:{color}">{text}</h1>')


def support(sid, text, y, x=RX, w=RW, color="var(--fg-muted)"):
    return f'<p id="{sid}" class="abs hide" style="left:{x}px; top:{y}px; width:{w}px; font-size:34px; line-height:1.28; letter-spacing:-0.015em; color:{color}">{text}</p>'


def popup(pid, x, y, name, sub, width=360):
    """Callout text: bold name, one plain line under it. Ink, on a light card."""
    return (f'<div id="{pid}" class="abs hide" style="left:{x}px; top:{y}px; width:{width}px; color:var(--ink-700)">'
            f'<div style="font-size:40px; line-height:1.05; font-weight:600; letter-spacing:-0.03em">{name}</div>'
            f'<div style="font-size:28px; line-height:1.25; margin-top:10px; color:var(--ink-500)">{sub}</div></div>')


PUI = json.loads((ROOT / "product-ui" / "anchors.json").read_text())


def app_part(pid, src, x, y, w, crop_h=None, radius=24):
    """A real app part (PNG from product-ui/) on the dark, as a light card. crop_h cuts its bottom."""
    h = f"height:{crop_h}px; " if crop_h else ""
    return (f'<div id="{pid}" class="abs hide" style="left:{x}px; top:{y}px; width:{w}px; {h}overflow:hidden; border-radius:{radius}px; background:#fff">'
            f'<img src="../product-ui/{src}" style="display:block; width:{w}px" alt=""></div>')


def phone(pid, screen, x, y, h):
    """A real mobile screen (with its device shell) from product-ui/mobile/screens/. Returns html, scale, box(name)."""
    sw, sh = PUI["mobile"][screen]["size"]
    k = h / sh
    # WHY: the capture is the device shell's bounding box; rounding hides the canvas behind its corners.
    html = f'<img id="{pid}" class="abs hide" src="../product-ui/mobile/screens/{screen}.png" style="left:{x}px; top:{y}px; height:{h}px; border-radius:{60 * k:.0f}px" alt="">'

    def box(name):
        bx, by, bw, bh = PUI["mobile"][screen]["boxes"][name]
        return x + bx * k, y + by * k, bw * k, bh * k
    return html, k, box


def ring(rid, box, pad=8, radius=14):
    """The frame's one lime element: a ring around a real UI element."""
    x, y, w, h = box
    return (f'<div id="{rid}" class="abs ring" style="left:{x - pad:.0f}px; top:{y - pad:.0f}px; width:{w + 2 * pad:.0f}px; height:{h + 2 * pad:.0f}px; '
            f'border-radius:{radius}px"></div>')


def fit_js(hid, maxpx, minpx, maxh):
    return f'fitText(document.getElementById("{hid}"), {maxpx}, {minpx}, {maxh});'


def page(title, duration, body, script):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="../templates/line.css">
<script src="motion.js"></script>
<style>body {{ background: var(--ground-900); margin: 0; }} .frame {{ width: {W}px; height: {H}px; background: var(--ground-900); }}
.hide {{ opacity: 0; }}
.fit {{ overflow: hidden; }}
.card {{ position: absolute; background: var(--mist); }}
.sweep-clip {{ position: absolute; overflow: hidden; pointer-events: none; }}
.sweep {{ position: absolute; top: 0; bottom: 0; left: -20%; width: 140%; opacity: 0.14; visibility: hidden;
  background: linear-gradient(90deg, #f8fafc 0%, #eefbd7 12%, #d8f7a3 26%, #baf85d 42%, #a5fc22 58%, #8ff741 74%, #7ff553 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, rgba(0,0,0,.15) 7%, #000 22%, #000 78%, rgba(0,0,0,.15) 93%, transparent 100%); }}
.leader {{ fill: none; stroke: {INK}; stroke-width: 1.5; }}
.ring {{ border: 4px solid {LIME}; box-shadow: inset 0 0 0 1.5px {INK}; opacity: 0; }}
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


# A. Draw, then highlight --------------------------------------------------------
def draw_highlight():
    box, pt = place("building", CX + 50, CY + 170, height=720)
    ux, uy = pt("unit-right")
    lx = CX + CW - 250
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("building", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 24},{uy}"/></svg>',
        popup("t3", lx, uy - 26, "Unit 203", "Needs review", width=230),
        sweep_layer(CX, CY, CW, CH, "sw"),
        lockup(CX + 56, 984, color="black"),
        headline("t2", "Every unit, on one record."),
        app_part("p1", "mobile/parts/record-details.png", RX, 0, RW, crop_h=538),
    ])
    script = f"""
let items;
function setup() {{ items = prepDraw(document.getElementById("d")); {fit_js("t2", 170, 60, 330)} below("p1", "t2", 44); }}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  sweep(document.getElementById("sw"), t, 0.25, 1.7);
  enter(document.getElementById("t2"), t, 0.4);
  drawAt(items, t, 0.5, 2.2, 0.7, "#f8fafc", 3.4);
  leaderAt(document.getElementById("ld"), t, 3.8);
  enter(document.getElementById("p1"), t, 1.0, 0.6, 24);
  enter(document.getElementById("t3"), t, 4.0, 0.48, 8);
}}"""
    return page("Draw and highlight", 6.4, body, script)


# B. Explode -----------------------------------------------------------------------
def explode():
    box, pt = place("building-floors", CX + 110, CY + 290, height=600)
    ux, uy = pt("unit-right")
    lx = CX + CW - 250
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("building-floors", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 24},{uy}"/></svg>',
        popup("t3", lx, uy - 26, "Floor 3", "2 open jobs", width=230),
        lockup(CX + 56, 984, color="black"),
        headline("t2", "Open any floor."),
        app_part("p1", "desktop/parts/location-card.png", RX, 0, RW),
        support("t4", "Every floor and unit keeps its own history.", 0),
    ])
    script = f"""
let items, floors, roof, ld, t3;
const GAP = 44, UY = {uy}, UX = {ux}, LX = {lx};
function setup() {{
  items = prepDraw(document.getElementById("d"));
  floors = [0, 1, 2, 3, 4].map((k) => document.getElementById("floor-" + k));
  roof = document.getElementById("roof");
  ld = document.getElementById("ld"); t3 = document.getElementById("t3");
  {fit_js("t2", 170, 60, 300)} below("p1", "t2", 44); below("t4", "p1", 36);
}}
function amount(t, k) {{
  const out = ease(prog(t, 1.3 + (5 - k) * 0.08, 0.64));
  const back = ease(prog(t, 5.0 + k * 0.06, 0.64));
  return out * (1 - back);
}}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t2"), t, 0.4);
  drawAt(items, t, 0.3, 0.9, 0.45, "#f8fafc", 2.5);
  const svg = document.getElementById("d");
  const scale = svg.getBoundingClientRect().height / svg.viewBox.baseVal.height;
  floors.forEach((g, k) => g.setAttribute("transform", `translate(0 ${{-k * GAP * amount(t, k) / scale}})`));
  roof.setAttribute("transform", `translate(0 ${{-5 * GAP * amount(t, 5) / scale}})`);
  const y = UY - 2 * GAP * amount(t, 2);
  ld.setAttribute("points", `${{UX}},${{y}} ${{LX - 24}},${{y}}`);
  leaderAt(ld, t, 2.9);
  ld.style.opacity = t < 4.9 ? 1 : 0;
  enter(t3, t, 3.1, 0.48, 8);
  if (t >= 4.6) t3.style.opacity = 1 - prog(t, 4.6, 0.3);
  t3.style.top = (y - 26) + "px";
  enter(document.getElementById("p1"), t, 0.9, 0.6, 24);
  enter(document.getElementById("t4"), t, 1.3);
}}"""
    return page("Explode", 6.6, body, script)


# C. Capture walk -------------------------------------------------------------------
def capture_walk():
    box, pt = place("unit-plan", CX + 55, CY + 170, width=1000)
    route = [pt(f"route-{i}") for i in range(15)]
    rooms = [("Entry", "0:00", 0), ("Bathroom", "0:48", 3), ("Kitchen", "1:52", 8),
             ("Living room", "3:10", 9.6), ("Bedroom", "4:25", 14)]
    pts = " ".join(f"{x},{y}" for x, y in route)
    rows = []
    for i, (name, time, _) in enumerate(rooms):
        y = 300 + i * 104
        rows.append(f'<div id="r{i}" class="abs hide" style="left:{RX}px; top:{y}px; width:{RW}px; height:104px; border-top:1px solid var(--line-dark); color:var(--mist)">'
                    f'<span class="abs" style="left:0; top:26px; font-size:40px; letter-spacing:-0.03em">{name}</span>'
                    f'<span class="abs" style="right:0; top:30px; font-size:34px; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; color:var(--fg-muted)">{time}</span></div>')
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        inline("unit-plan", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="trail" points="{pts}" fill="none" stroke="rgb(48 48 58 / 0.55)" stroke-width="2" stroke-linejoin="round"/>'
        f'<circle id="ring" r="18" fill="none" stroke="{INK}" stroke-width="1.5"/><circle id="dotm" r="12" fill="{LIME}" stroke="{INK}" stroke-width="2"/></svg>',
        headline("t1", "Capture walk"),
        *rows,
        f'<div id="t2" class="abs hide" style="left:{RX}px; top:{300 + 5 * 104}px; width:{RW}px; border-top:1px solid var(--line-dark); padding-top:28px; color:var(--mist); font-size:48px; line-height:1.05; letter-spacing:-0.04em">5 rooms, 6 minutes.</div>',
        lockup(RX, 950),
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
  {fit_js("t1", 140, 60, 170)}
}}
const at = (idx) => {{ const i = Math.floor(idx), f = idx - i; return i + 1 < cum.length ? cum[i] + (cum[i + 1] - cum[i]) * f : cum[i]; }};
const smooth = (x) => x * x * (3 - 2 * x);
function invSmooth(y) {{ let lo = 0, hi = 1; for (let i = 0; i < 30; i++) {{ const m = (lo + hi) / 2; if (smooth(m) < y) lo = m; else hi = m; }} return (lo + hi) / 2; }}
const T0 = 1.4, TD = 6.0;
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  drawAt(items, t, 0.3, 1.0, 0.5, "#f8fafc");
  enter(document.getElementById("t1"), t, 0.3);
  const L = total * smooth(prog(t, T0, TD));
  trail.style.strokeDashoffset = total + 2 - L;
  const q = trail.getPointAtLength(Math.max(0.01, L));
  const vis = t >= T0 - 0.2 ? 1 : 0;
  dotm.setAttribute("cx", q.x); dotm.setAttribute("cy", q.y); dotm.setAttribute("opacity", vis);
  const pulse = (t * 1.1) % 1;
  ring.setAttribute("cx", q.x); ring.setAttribute("cy", q.y); ring.setAttribute("r", 14 + 18 * pulse); ring.setAttribute("opacity", vis * (1 - pulse) * 0.7);
  STOPS.forEach((s, i) => enter(document.getElementById("r" + i), t, T0 + TD * invSmooth(at(s) / total), 0.4, 12));
  enter(document.getElementById("t2"), t, 7.7);
}}"""
    return page("Capture walk", 9.0, body, script)


# D. Callouts ----------------------------------------------------------------------
def callouts():
    x0, y0, w0, h0 = SEAM, SEAM, W - 2 * SEAM, H - 2 * SEAM
    box, pt = place("unit-plan", 760, 290, width=1060)
    dx, dy = pt("dishwasher")
    bx, by = pt("bath")
    body = "\n".join([
        card(x0, y0, w0, h0, "card"),
        headline("t1", "Every job lands on the room it belongs to.", x=112, y=112, w=780, color="var(--ink-700)"),
        inline("unit-plan", "light", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}">'
        f'<polyline id="l0" class="leader" points="{dx},{dy} {dx},{dy - 150} {dx + 200},{dy - 150}"/>'
        f'<polyline id="l1" class="leader" points="{bx},{by} {520},{by}"/></svg>',
        popup("c0", dx + 224, dy - 176, "Dishwasher", "Repeat repair, flagged"),
        popup("c1", 112, by - 24, "Bathroom", "Leak fixed, photos on file", width=380),
        lockup(112, 950, color="black"),
    ])
    script = f"""
let items;
function setup() {{ items = prepDraw(document.getElementById("d")); {fit_js("t1", 120, 60, 340)} }}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t1"), t, 0.3);
  drawAt(items, t, 0.5, 1.6, 0.6, "#f8fafc", 2.7);
  leaderAt(document.getElementById("l0"), t, 3.0);
  enter(document.getElementById("c0"), t, 3.2, 0.48, 8);
  leaderAt(document.getElementById("l1"), t, 4.0);
  enter(document.getElementById("c1"), t, 4.2, 0.48, 8);
}}"""
    return page("Callouts", 6.0, body, script)


# E. Asset tiles -------------------------------------------------------------------
def asset_tiles():
    names = [("fridge", "Fridge"), ("range", "Range"), ("washer-dryer", "Washer and dryer"),
             ("furnace", "Furnace"), ("water-heater", "Water heater"), ("electrical-panel", "Electrical panel")]
    tw, gap, x0 = 552, SEAM, 120
    th, y0 = 336, 312
    parts, ids = [], []
    for i, (n, label) in enumerate(names):
        c, r = i % 3, i // 3
        l, t = x0 + c * (tw + gap), y0 + r * (th + gap)
        x, y, vw, vh = A[n]["viewBox"]
        ih = 250
        iw = vw * ih / vh
        parts.append(f'<div id="tile{i}" class="card hide" style="left:{l}px; top:{t}px; width:{tw}px; height:{th}px; border-radius:24px">'
                     f'<span style="position:absolute; left:28px; top:24px; font-size:30px; font-weight:600; letter-spacing:-0.02em; color:var(--ink-700)">{label}</span></div>')
        parts.append(inline(n, "light", (l + tw - iw - 48, t + th - ih - 30, iw, ih), f"d{i}"))
        ids.append(f"d{i}")
    body = "\n".join([
        headline("t1", "Every asset, with its own history.", x=120, y=96, w=1400),
        *parts,
        lockup(1640, 118),
    ])
    script = f"""
let sets;
function setup() {{ sets = {json.dumps(ids)}.map((id) => prepDraw(document.getElementById(id))); {fit_js("t1", 120, 60, 200)} }}
function renderAt(t) {{
  enter(document.getElementById("t1"), t, 0.1);
  sets.forEach((items, i) => {{
    const s = 0.5 + i * 0.22;
    enter(document.getElementById("tile" + i), t, s, 0.36, 10);
    document.getElementById("d" + i).style.transform = document.getElementById("tile" + i).style.transform;
    drawAt(items, t, s + 0.3, 0.9, 0.45, "#f8fafc");
  }});
}}"""
    return page("Asset tiles", 5.0, body, script)


# F. App: decide from the phone (screen push) ----------------------------------------
def app_decide():
    ph1, k, box1 = phone("ph1", "manager-work", CX + 130, CY + 54, 940)
    _, _, box2 = phone("ph2x", "work-order", CX + 130, CY + 54, 940)
    sx, sy, sw_, sh_ = CX + 130 + 14 * k, CY + 54 + 14 * k, 393 * k, 852 * k
    bx, by, bw, bh = box1("water-heater")
    qx, qy, qw, qh = box2("quote")
    tx = CX + 130 + 421 * k + 70
    tw = CX + CW - tx - 50
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        ph1,
        # WHY: the incoming screen slides inside its own screen-sized clip, so its device shell never shows.
        f'<div class="abs" style="left:{sx:.0f}px; top:{sy:.0f}px; width:{sw_:.0f}px; height:{sh_:.0f}px; overflow:hidden; border-radius:{46 * k:.0f}px">'
        f'<div id="ph2" style="position:absolute; inset:0; overflow:hidden; opacity:0">'
        f'<img src="../product-ui/mobile/screens/work-order.png" style="position:absolute; left:{-14 * k:.0f}px; top:{-14 * k:.0f}px; height:940px" alt=""></div></div>',
        ring("r1", box1("water-heater")),
        ring("r2", box2("quote")),
        popup("c1", tx, by - 10, "Owner asked", "Leaking water heater, Unit 4B", width=tw),
        popup("c2", tx, qy - 10, "Decide the quote", "From the job, in one tap", width=tw),
        lockup(CX + CW - 226, 984, color="black"),
        headline("t1", "Decide quotes from anywhere."),
        support("t2", "Requests that need an owner or manager wait in one list on their phone.", 0),
    ])
    script = f"""
function setup() {{ {fit_js("t1", 170, 60, 520)} below("t2", "t1", 40); }}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("t2"), t, 0.7);
  enter(document.getElementById("ph1"), t, 0.4, 0.7, 40);
  const r1 = document.getElementById("r1"), r2 = document.getElementById("r2"), c1 = document.getElementById("c1");
  r1.style.opacity = prog(t, 1.6, 0.3) * (1 - prog(t, 3.6, 0.2));
  enter(c1, t, 1.8, 0.48, 8);
  if (t >= 3.6) c1.style.opacity = 1 - prog(t, 3.6, 0.25);
  const push = ease(prog(t, 3.8, 0.55));
  const p2 = document.getElementById("ph2");
  p2.style.opacity = t >= 3.8 ? 1 : 0;
  p2.style.transform = `translateX(${{(1 - push) * {sw_:.0f}}}px)`;
  r2.style.opacity = prog(t, 4.7, 0.3);
  enter(document.getElementById("c2"), t, 4.9, 0.48, 8);
}}"""
    return page("Decide from the phone", 7.0, body, script)


# G. App: the day's work on the phone --------------------------------------------------
def app_field_home():
    ph, k, box = phone("ph1", "field-home", CX + 130, CY + 54, 940)
    bx, by, bw, bh = box("waiting")
    tx = CX + 130 + 421 * k + 70
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        ph,
        ring("r1", box("waiting")),
        popup("c1", tx, by - 10, "Ready to start", "Unit 4B, Maple Court", width=CX + CW - tx - 50),
        lockup(CX + CW - 226, 984, color="black"),
        headline("t1", "The day&#8217;s work, in one list."),
        app_part("p1", "mobile/parts/record-summary.png", RX, 0, RW),
        support("t2", "Inspections, uploads and comments that need you, first thing.", 0),
    ])
    script = f"""
function setup() {{ {fit_js("t1", 170, 60, 420)} below("p1", "t1", 44); below("t2", "p1", 36); }}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("ph1"), t, 0.4, 0.7, 40);
  enter(document.getElementById("p1"), t, 1.0, 0.6, 24);
  enter(document.getElementById("t2"), t, 1.4);
  document.getElementById("r1").style.opacity = prog(t, 2.4, 0.3);
  enter(document.getElementById("c1"), t, 2.6, 0.48, 8);
}}"""
    return page("Field home", 5.6, body, script)


# H. App: the maintenance board on desktop ---------------------------------------------
def app_board():
    bw_ = CW - 80
    k0 = bw_ / 1440
    bh_ = round(900 * k0)
    bx0, by0 = CX + 40, CY + 40
    lx, ly, lw, lh = PUI["desktop"]["maintenance-board"]["boxes"]["leak"]
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        f'<div id="b1" class="abs hide" style="left:{bx0}px; top:{by0}px; width:{bw_}px; height:{bh_}px; overflow:hidden; border-radius:18px; border:1px solid #e2e8f0">'
        f'<img id="bimg" src="../product-ui/desktop/screens/maintenance-board.png" style="position:absolute; left:0; top:0; width:1440px; transform-origin:0 0" alt=""></div>',
        '<div id="r1" class="abs ring" style="border-radius:12px"></div>',
        popup("c1", CX + 56, by0 + bh_ + 56, "Active leak", "Kitchen faucet at King West 1708, flagged before a trade is booked.", width=CW - 112),
        lockup(CX + 56, 984, color="black"),
        headline("t1", "Every work order on one board."),
        app_part("p1", "desktop/parts/work-order-card-leak.png", RX, 0, RW),
    ])
    script = f"""
const BW = {bw_}, BH = {bh_}, BX = {bx0}, BY = {by0}, K0 = {k0:.4f}, K1 = 1.45;
const L = [{lx}, {ly}, {lw}, {lh}];
function setup() {{ {fit_js("t1", 170, 60, 460)} below("p1", "t1", 44); }}
function board(t) {{
  // WHY: the full board at legible size is too small, so the camera moves in on the one card.
  const z = ease(prog(t, 1.4, 1.6));
  const s = K0 + (K1 - K0) * z;
  const fx = 720 + (L[0] + L[2] / 2 - 720) * z, fy = 450 + (L[1] + L[3] / 2 - 450) * z;
  let tx = BW / 2 - fx * s, ty = BH / 2 - fy * s;
  tx = Math.min(0, Math.max(BW - 1440 * s, tx)); ty = Math.min(0, Math.max(BH - 900 * s, ty));
  document.getElementById("bimg").style.transform = `translate(${{tx}}px, ${{ty}}px) scale(${{s}})`;
  const r = document.getElementById("r1"), pad = 6;
  r.style.left = (BX + tx + L[0] * s - pad) + "px"; r.style.top = (BY + ty + L[1] * s - pad) + "px";
  r.style.width = (L[2] * s + 2 * pad) + "px"; r.style.height = (L[3] * s + 2 * pad) + "px";
  r.style.opacity = prog(t, 3.2, 0.3);
}}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("b1"), t, 0.4, 0.7, 30);
  board(t);
  enter(document.getElementById("c1"), t, 3.4, 0.48, 8);
  enter(document.getElementById("p1"), t, 4.0, 0.6, 24);
}}"""
    return page("Maintenance board", 6.4, body, script)


# I. App: a report ready to review ------------------------------------------------------
def app_report():
    ph, k, box = phone("ph1", "report", CX + 130, CY + 54, 940)
    sx, sy, sw_, sh_ = box("status")
    dx, dy, dw, dh = box("to-decide")
    tx = CX + 130 + 421 * k + 70
    tw = CX + CW - tx - 50
    body = "\n".join([
        card(CX, CY, CW, CH, "card"),
        ph,
        ring("r1", box("status"), pad=7, radius=20),
        ring("r2", box("to-decide"), pad=7, radius=14),
        popup("c1", tx, sy - 30, "Needs review", "Set when the walk is processed", width=tw),
        popup("c2", tx, dy - 20, "2 to decide", "Only the calls a person has to make", width=tw),
        lockup(CX + CW - 226, 984, color="black"),
        headline("t1", "Reports arrive ready to review."),
        app_part("p1", "mobile/parts/record-summary.png", RX, 0, RW),
    ])
    script = f"""
function setup() {{ {fit_js("t1", 170, 60, 460)} below("p1", "t1", 44); }}
function renderAt(t) {{
  enter(document.getElementById("card"), t, 0, 0.5, 0);
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("ph1"), t, 0.4, 0.7, 40);
  enter(document.getElementById("p1"), t, 1.0, 0.6, 24);
  const r1 = document.getElementById("r1"), r2 = document.getElementById("r2"), c1 = document.getElementById("c1");
  r1.style.opacity = prog(t, 1.8, 0.3) * (1 - prog(t, 3.6, 0.2));
  enter(c1, t, 2.0, 0.48, 8);
  if (t >= 3.6) c1.style.opacity = 1 - prog(t, 3.6, 0.25);
  r2.style.opacity = prog(t, 3.9, 0.3);
  enter(document.getElementById("c2"), t, 4.1, 0.48, 8);
}}"""
    return page("Report ready", 6.2, body, script)


CLIPS = {
    "draw-highlight": draw_highlight,
    "explode": explode,
    "capture-walk": capture_walk,
    "callouts": callouts,
    "asset-tiles": asset_tiles,
    "app-decide": app_decide,
    "app-field-home": app_field_home,
    "app-board": app_board,
    "app-report": app_report,
}
for name, fn in CLIPS.items():
    (OUT / f"{name}.html").write_text(fn())
print("clips written:", list(CLIPS))
