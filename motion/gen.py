"""Generate the generic motion example clips (HTML, 1920 x 1080).

Each clip is one HTML page with inline drawings and a renderAt(t) function.
Open it in a browser to watch it loop; render.py turns it into an MP4.
Run: python3 motion/gen.py
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = json.loads((ROOT / "illustrations" / "anchors.json").read_text())
SVG = ROOT / "illustrations" / "svg"
OUT = ROOT / "motion"
W, H = 1920, 1080


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


def page(title, duration, body, script, bg="var(--ground-900)"):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="../templates/line.css">
<script src="motion.js"></script>
<style>body {{ background: {bg}; margin: 0; }} .frame {{ width: {W}px; height: {H}px; background: {bg}; }}
.hide {{ opacity: 0; }} .leader {{ fill: none; stroke: #f8fafc; stroke-width: 1; }}</style></head>
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


def lockup(x, y, h=26, color="white"):
    return f'<img class="abs" src="../brand/logos/verstack-lockup-{color}.svg" style="left:{x}px; top:{y}px; height:{h}px" alt="Verstack">'


# A. Draw, then highlight --------------------------------------------------------
def draw_highlight():
    box, pt = place("building", 150, 120, height=840)
    ux, uy = pt("unit-right")
    lx = 1220
    body = "\n".join([
        inline("building", "dark", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 16},{uy}"/>'
        f'<rect id="nd" x="{ux - 3.5}" y="{uy - 3.5}" width="7" height="7" fill="#a5fc22" stroke="#f8fafc" opacity="0"/></svg>',
        '<div id="t1" class="abs dot hide" style="left:1220px; top:150px; color:var(--mist); font-size:20px">Mill Court</div>',
        '<h1 id="t2" class="abs hide" style="left:1220px; top:206px; width:560px; font-size:78px; line-height:0.98; letter-spacing:-0.05em; font-weight:400; color:var(--mist)">Every unit, on one record.</h1>',
        f'<div id="t3" class="abs callout hide" style="left:{lx}px; top:{uy - 16}px; width:420px; color:var(--mist)"><div class="dot live" style="font-size:20px">Unit 214</div><div class="s" style="font-size:18px; color:var(--fg-muted)">Make ready. Paint and clean, ready by 1 Sep.</div></div>',
        lockup(1220, 990),
    ])
    script = """
let items;
function setup() { items = prepDraw(document.getElementById("d")); }
function renderAt(t) {
  drawAt(items, t, 0.2, 2.4, 0.7, "#171a19", 3.5);
  enter(document.getElementById("t1"), t, 0.3);
  leaderAt(document.getElementById("ld"), t, 3.9);
  document.getElementById("nd").setAttribute("opacity", t >= 3.9 ? 1 : 0);
  enter(document.getElementById("t3"), t, 4.1);
  enter(document.getElementById("t2"), t, 4.8);
}"""
    return page("Draw and highlight", 6.5, body, script)


# B. Explode -----------------------------------------------------------------------
def explode():
    box, pt = place("building-floors", 260, 330, height=640)
    ux, uy = pt("unit-right")
    lx = 1220
    body = "\n".join([
        inline("building-floors", "dark", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="ld" class="leader" points="{ux},{uy} {lx - 16},{uy}"/>'
        f'<rect id="nd" x="{ux - 3.5}" y="{uy - 3.5}" width="7" height="7" fill="#a5fc22" stroke="#f8fafc" opacity="0"/></svg>',
        '<div id="t1" class="abs dot hide" style="left:1220px; top:150px; color:var(--mist); font-size:20px">Mill Court, 5 floors</div>',
        '<h1 id="t2" class="abs hide" style="left:1220px; top:206px; width:560px; font-size:78px; line-height:0.98; letter-spacing:-0.05em; font-weight:400; color:var(--mist)">Open any floor.</h1>',
        f'<div id="t3" class="abs callout hide" style="left:{lx}px; top:{uy - 16}px; width:420px; color:var(--mist)"><div class="dot live" style="font-size:20px">Floor 3, Unit 214</div><div class="s" style="font-size:18px; color:var(--fg-muted)">2 open work orders.</div></div>',
        lockup(1220, 990),
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
  const out = ease(prog(t, 1.0 + (5 - k) * 0.08, 0.64));
  const back = ease(prog(t, 4.7 + k * 0.06, 0.64));
  return out * (1 - back);
}}
function renderAt(t) {{
  drawAt(items, t, 0.1, 0.9, 0.45, "#171a19", 2.2);
  const scale = document.getElementById("d").getBoundingClientRect().height / document.getElementById("d").viewBox.baseVal.height;
  floors.forEach((g, k) => g.setAttribute("transform", `translate(0 ${{-k * GAP * amount(t, k) / scale}})`));
  roof.setAttribute("transform", `translate(0 ${{-5 * GAP * amount(t, 5) / scale}})`);
  const y = UY - 2 * GAP * amount(t, 2);
  ld.setAttribute("points", `${{UX}},${{y}} ${{LX - 16}},${{y}}`);
  nd.setAttribute("y", y - 3.5);
  leaderAt(ld, t, 2.6);
  const show = t >= 2.6 && t < 4.6;
  nd.setAttribute("opacity", show ? 1 : 0);
  ld.style.opacity = t < 4.6 ? 1 : 0;
  enter(t3, t, 2.8);
  if (t >= 4.3) t3.style.opacity = 1 - prog(t, 4.3, 0.3);
  t3.style.top = (y - 16) + "px";
  enter(document.getElementById("t1"), t, 0.3);
  enter(document.getElementById("t2"), t, 5.3);
}}"""
    return page("Explode", 6.8, body, script)


# C. Capture walk -------------------------------------------------------------------
def capture_walk():
    box, pt = place("unit-plan", 80, 230, width=1120)
    route = [pt(f"route-{i}") for i in range(15)]
    rooms = [("Entry", "0:00", 0, "entry"), ("Bathroom", "0:48", 3, "bath"), ("Kitchen", "1:52", 8, "kitchen"),
             ("Living room", "3:10", 9.6, "living"), ("Bedroom", "4:25", 14, "bed")]
    pts = " ".join(f"{x},{y}" for x, y in route)
    nodes = "".join(f'<rect id="n{i}" x="{pt(a)[0] - 3.5}" y="{pt(a)[1] - 3.5}" width="7" height="7" fill="#171a19" stroke="#f8fafc" opacity="0"/>' for i, (_, _, _, a) in enumerate(rooms))
    rows = []
    for i, (name, time, _, _) in enumerate(rooms):
        y = 330 + i * 92
        rows.append(f'<div id="r{i}" class="abs hide" style="left:1320px; top:{y}px; width:480px; height:92px; border-top:1px solid var(--line-dark); color:var(--mist)">'
                    f'<span class="abs mono" style="left:0; top:30px; font-size:14px; color:var(--fg-subtle)">0{i + 1}</span>'
                    f'<span class="abs" style="left:56px; top:24px; font-size:26px; letter-spacing:-0.02em">{name}</span>'
                    f'<span class="abs mono" style="right:0; top:30px; font-size:16px; color:var(--fg-muted)">{time}</span></div>')
    body = "\n".join([
        inline("unit-plan", "dark", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}"><polyline id="trail" points="{pts}" fill="none" stroke="rgb(248 250 252 / 0.6)" stroke-width="1.5" stroke-linejoin="round"/>{nodes}'
        '<circle id="ring" r="16" fill="none" stroke="#a5fc22" stroke-width="1.5"/><circle id="dotm" r="8" fill="#a5fc22" stroke="#171a19" stroke-width="1.5"/></svg>',
        '<div id="t1" class="abs hide" style="left:1320px; top:150px; color:var(--mist)"><div class="dot" style="font-size:20px">Capture walk</div><div class="meta" style="margin-top:8px; font-size:16px; color:var(--fg-subtle)">Unit 214, Mill Court. Phone video, room by room.</div></div>',
        *rows,
        '<div id="t2" class="abs hide" style="left:1320px; top:802px; width:480px; border-top:1px solid var(--line-dark); padding-top:22px; color:var(--mist); font-size:30px; letter-spacing:-0.02em">5 rooms, 6 minutes.<div class="dot" style="display:flex; font-size:18px; margin-top:14px; color:var(--fg-muted)">Record ready for review</div></div>',
        lockup(80, 990),
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
function renderAt(t) {{
  drawAt(items, t, 0.1, 1.0, 0.5, "#171a19");
  enter(document.getElementById("t1"), t, 0.3);
  const p = smooth(prog(t, 1.2, 6.0));
  const L = total * p;
  trail.style.strokeDashoffset = total + 2 - L;
  const q = trail.getPointAtLength(Math.max(0.01, L));
  const vis = t >= 1.0 ? 1 : 0;
  dotm.setAttribute("cx", q.x); dotm.setAttribute("cy", q.y); dotm.setAttribute("opacity", vis);
  const pulse = (t * 1.25) % 1;
  ring.setAttribute("cx", q.x); ring.setAttribute("cy", q.y); ring.setAttribute("r", 10 + 18 * pulse); ring.setAttribute("opacity", vis * (1 - pulse));
  STOPS.forEach((s, i) => {{
    const reached = L >= at(s) - 0.5 && t >= 1.0;
    const tr = 1.2 + 6.0 * invSmooth(at(s) / total);
    document.getElementById("n" + i).setAttribute("opacity", reached ? 1 : 0);
    enter(document.getElementById("r" + i), t, tr, 0.4, 12);
  }});
  enter(document.getElementById("t2"), t, 7.5);
}}
function invSmooth(y) {{ let lo = 0, hi = 1; for (let i = 0; i < 30; i++) {{ const m = (lo + hi) / 2; if (smooth(m) < y) lo = m; else hi = m; }} return (lo + hi) / 2; }}"""
    return page("Capture walk", 9.0, body, script)


# D. Callouts ----------------------------------------------------------------------
def callouts():
    grid = ("background-image: linear-gradient(rgb(255 255 255 / 0.035) 1px, transparent 1px), linear-gradient(90deg, rgb(255 255 255 / 0.035) 1px, transparent 1px);"
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
                     f'<rect id="n{i}" x="{ax - 3.5}" y="{ay - 3.5}" width="7" height="7" fill="{"#a5fc22" if live else "#171a19"}" stroke="#f8fafc" opacity="0"/>')
        labels.append(f'<div id="c{i}" class="callout hide" style="left:{lx}px; top:{ly - 2}px; width:236px; color:var(--mist)"><div class="k" style="color:var(--fg-subtle)">{k}</div><div class="n">{n}</div><div class="s" style="color:var(--fg-muted)">{s}</div></div>')
    body = "\n".join([
        f'<div class="abs" style="inset:0; {grid}"></div>',
        f'<svg class="leaders" width="{W}" height="{H}"><g stroke="rgb(255 255 255 / 0.22)" stroke-width="1">{pluses}</g></svg>',
        '<p id="t1" class="abs hide" style="left:560px; top:64px; width:800px; text-align:center; font-size:18px; line-height:1.55; color:var(--mist)">Every work order, quote and inspection lands on the unit&#8217;s record, room by room.</p>',
        '<div class="abs" style="left:120px; top:200px; width:1680px; border-top:1px solid var(--line-dark)"></div>',
        '<div id="t2" class="abs mono hide" style="left:120px; top:244px; font-size:15px; font-weight:500; color:var(--mist)">1.0&nbsp;&nbsp;Unit record</div>',
        inline("unit-plan", "dark", box, "d"),
        f'<svg class="leaders" width="{W}" height="{H}">{"".join(lines)}</svg>',
        *labels,
        lockup(120, 990),
    ])
    script = """
let items;
function setup() { items = prepDraw(document.getElementById("d")); }
function renderAt(t) {
  enter(document.getElementById("t1"), t, 0.1);
  enter(document.getElementById("t2"), t, 0.3);
  drawAt(items, t, 0.4, 1.6, 0.6, "#101312", 2.6);
  [2.6, 3.3, 4.0, 4.7].forEach((s, i) => {
    leaderAt(document.getElementById("l" + i), t, s);
    document.getElementById("n" + i).setAttribute("opacity", t >= s ? 1 : 0);
    enter(document.getElementById("c" + i), t, s + 0.2, 0.4, 8);
  });
}"""
    return page("Callouts", 6.2, body, script, bg="var(--ground-950)")


# E. Asset tiles -------------------------------------------------------------------
def asset_tiles():
    names = [("fridge", "Fridge"), ("range", "Range"), ("washer-dryer", "Washer and dryer"),
             ("furnace", "Furnace"), ("water-heater", "Water heater"), ("electrical-panel", "Electrical panel")]
    tw, th, gap, x0, y0 = 552, 330, 12, 120, 330
    parts, ids = [], []
    for i, (n, label) in enumerate(names):
        c, r = i % 3, i // 3
        l, t = x0 + c * (tw + gap), y0 + r * (th + gap)
        x, y, vw, vh = A[n]["viewBox"]
        ih = 250
        iw = vw * ih / vh
        parts.append(f'<div id="tile{i}" class="tile hide" style="left:{l}px; top:{t}px; width:{tw}px; height:{th}px"><span class="dot" style="font-size:17px">{label}</span></div>')
        parts.append(inline(n, "dark", (l + (tw - iw) / 2, t + 62, iw, ih), f"d{i}"))
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
    enter(document.getElementById("tile" + i), t, 0.5 + i * 0.12);
    document.getElementById("d" + i).style.opacity = document.getElementById("tile" + i).style.opacity;
    document.getElementById("d" + i).style.transform = document.getElementById("tile" + i).style.transform;
    drawAt(items, t, 0.75 + i * 0.15, 1.0, 0.45, "#1c201f");
  }});
}}"""
    return page("Asset tiles", 5.4, body, script)


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
