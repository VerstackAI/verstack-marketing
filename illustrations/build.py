"""Build the Verstack line illustration set.

Writes svg/<name>-dark.svg and svg/<name>-light.svg plus anchors.json (screen
points that layouts use to attach leader lines). Run: python3 build.py
"""
import json
import math
import pathlib
import sys
from iso import Drawing, rounded_rect
from scenes_more import MORE
import phone_site

OUT = pathlib.Path(__file__).parent / "svg"
OUT.mkdir(exist_ok=True)
# Planned hardware stays out of this public repo. Its scenes live in a private
# folder (scenes_private.py); pass that folder to build them there.
PRIVATE = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
PRIVATE_SCENES = {}
if PRIVATE:
    sys.path.insert(0, str(PRIVATE))
    from scenes_private import PRIVATE as PRIVATE_SCENES


def building(d, hi=True):
    W, D, F, FH = 12, 7, 5, 1.3
    H = F * FH
    d.box(0, 0, 0, W, D, H)
    # the highlighted unit: a corner of the third floor, both outside faces
    hz0, hz1, hx0, hy0 = 2 * FH, 3 * FH, 7.3, 3.6
    if hi:
        d.rect_on("y", D, hx0, hz0, W, hz1, fill="hi_l", stroke="hi_stroke")
        d.rect_on("x", W, hy0, hz0, D, hz1, fill="hi_r", stroke="hi_stroke")
    for k in range(1, F):
        z = k * FH
        d.line3((0, D, z), (W, D, z))
        d.line3((W, 0, z), (W, D, z))
    for k in range(F):
        z0, z1 = k * FH + 0.35, k * FH + 1.0
        for i in range(8):
            u0 = 0.5 + i * 1.42
            if k == 0 and i == 3:
                continue
            on_hi = hi and k == 2 and u0 >= hx0
            d.rect_on("y", D, u0, z0, u0 + 0.72, z1, stroke="hi_stroke" if on_hi else "stroke")
        for j in range(4):
            u0 = 0.55 + j * 1.6
            on_hi = hi and k == 2 and u0 >= hy0
            d.rect_on("x", W, u0, z0, u0 + 0.8, z1, stroke="hi_stroke" if on_hi else "stroke")
    # entrance and canopy
    d.rect_on("y", D, 4.55, 0, 5.65, 1.0)
    d.line3((5.1, D, 0), (5.1, D, 1.0))
    d.box(4.3, D, 1.05, 1.6, 0.55, 0.08)
    # roof: parapet line, two condensers, stair bulkhead
    d.rect_on("z", H, 0.22, 0.22, W - 0.22, D - 0.22)
    for x in (1.6, 3.6):
        d.box(x, 1.2, H, 1.5, 1.3, 0.7)
        d.circle_on("z", (x + 0.75, 1.85, H + 0.7), 0.42)
    d.box(8.6, 0.9, H, 2.2, 2.4, 1.15)
    d.rect_on("y", 3.3, 9.2, H, 9.95, H + 0.95)
    d.anchor("unit", ((hx0 + W) / 2 + 0.6, D, (hz0 + hz1) / 2))
    d.anchor("unit-right", (W, (hy0 + D) / 2, (hz0 + hz1) / 2))
    d.anchor("roof", (4.35, 1.85, H + 0.7))
    d.anchor("entrance", (5.1, D, 0.5))


def unit_plan(d, hi=True):
    W, D, T, H, HF = 12, 8, 0.14, 1.45, 0.42

    def wall_x(x0, x1, y, h=H, z0=0):  # wall running along x at y
        d.box(x0, y - T / 2, z0, x1 - x0, T, h)

    def wall_y(y0, y1, x, h=H, z0=0):  # wall running along y at x
        d.box(x - T / 2, y0, z0, T, y1 - y0, h)

    d.box(0, 0, -0.3, W, D, 0.3)
    # Floor-level marks (rug, door swing), then the floor layer: the walk trail goes there,
    # so every wall and piece of furniture drawn after it hides the trail behind it.
    d.rect_on("z", 0.001, 6.2, 1.5, 10.0, 3.7, stroke="muted")
    arc = [(3.55 + 1.0 * math.cos(math.radians(a)), D - 1.0 * math.sin(math.radians(a)), 0.002) for a in range(0, 91, 5)]
    d.poly3(arc, close=False, stroke="muted", dash="3 4")
    d.line3((3.55, D, 0.002), (3.55, D - 1.0, 0.002), stroke="muted")
    d.layer("floor")
    # back walls, with a window in the living room
    wall_x(0, 6.6, 0)
    wall_x(6.6, 10.4, 0, h=0.62)
    wall_x(6.6, 10.4, 0, h=0.2, z0=H - 0.2)
    wall_x(10.4, W, 0)
    wall_y(0, D, 0)
    # kitchen run along the back wall: corner cabinet, dishwasher, sink run, fridge
    d.box(0.1, 0.1, 0, 1.5, 0.8, 0.9)
    d.box(1.6, 0.1, 0, 0.75, 0.8, 0.9, hi=hi)
    d.box(2.35, 0.1, 0, 1.5, 0.8, 0.9)
    d.rect_on("z", 0.9, 2.6, 0.25, 3.5, 0.75)
    d.box(3.95, 0.1, 0, 0.9, 0.85, 1.9)
    d.line3((3.95, 0.95, 1.25), (4.85, 0.95, 1.25))
    # run along the side wall with a cooktop, then the island
    d.box(0.1, 0.9, 0, 0.8, 2.1, 0.9)
    for cy in (1.4, 2.4):
        d.circle_on("z", (0.5, cy, 0.9), 0.22)
    d.box(2.2, 2.3, 0, 1.7, 1.0, 0.85)
    # living room: rug, sofa, coffee table
    d.box(6.45, 0.25, 0, 3.1, 0.95, 0.42)
    d.box(6.45, 0.25, 0.42, 3.1, 0.28, 0.38)
    d.box(6.2, 0.25, 0, 0.25, 0.95, 0.62)
    d.box(9.55, 0.25, 0, 0.25, 0.95, 0.62)
    d.box(7.3, 2.1, 0, 1.5, 0.85, 0.32)
    # wall between the day rooms and the night rooms
    wall_x(0, 3.0, 4.5)
    wall_x(5.0, W, 4.5)
    # bathroom: tub, toilet
    d.box(0.1, 4.6, 0, 1.0, 2.4, 0.6)
    d.rect_on("z", 0.6, 0.24, 4.74, 0.96, 6.86)
    d.box(2.15, 4.6, 0, 0.6, 0.32, 0.75)
    d.cylinder_z(2.45, 5.25, 0.27, 0, 0.42)
    wall_y(4.5, 5.1, 3.0)
    wall_y(6.0, D, 3.0)
    wall_y(4.5, 5.3, 5.0)
    wall_y(6.2, D, 5.0)
    # bedroom: headboard, bed, pillows, side tables
    d.box(6.0, 0.0 + 4.0 + 0.6, 0, 0.6, 0.5, 0.5)
    d.box(7.0, 4.58, 0, 2.6, 0.16, 0.95)
    d.box(7.0, 4.74, 0, 2.6, 2.9, 0.45)
    d.line3((7.0, 6.0, 0.45), (9.6, 6.0, 0.45))
    d.box(7.25, 4.95, 0.45, 0.95, 0.5, 0.14)
    d.box(8.4, 4.95, 0.45, 0.95, 0.5, 0.14)
    d.box(10.0, 4.6, 0, 0.6, 0.5, 0.5)
    # front walls, cut low so the rooms read
    wall_x(0, 3.55, D, h=HF)
    wall_x(4.55, W, D, h=HF)
    wall_y(0, D, W, h=HF)
    d.anchor("dishwasher", (1.975, 0.5, 0.9))
    d.anchor("kitchen", (2.9, 3.0, 0.85))
    d.anchor("bath", (0.6, 5.8, 0.6))
    d.anchor("bed", (8.3, 6.6, 0.45))
    d.anchor("entry", (4.05, D, 0.2))
    d.anchor("living", (8.0, 2.5, 0.32))
    # capture route through the unit, for the capture-walk motion
    route = [(4.05, 7.6), (4.05, 5.75), (2.9, 5.75), (1.8, 6.3), (2.9, 5.75), (4.05, 5.75), (4.05, 4.0), (1.5, 4.0),
             (1.5, 1.6), (10.6, 1.6), (10.6, 3.8), (4.4, 3.8), (4.4, 5.75), (6.3, 5.75), (6.3, 6.6)]
    for i, (x, y) in enumerate(route):
        d.anchor(f"route-{i}", (x, y, 0.02))


def dishwasher(d, hi=False):
    W, D, H = 6, 6.2, 8.5
    d.box(0, 0, 0, W, D, H, hi=hi)
    st = "hi_stroke" if hi else "stroke"
    d.rect_on("y", D, 0.18, 0.75, W - 0.18, H - 0.18, stroke=st)
    d.line3((0.18, D, 7.45), (W - 0.18, D, 7.45), stroke=st)
    d.rect_on("y", D, 0.6, 7.7, 2.5, 8.08, fill="accent", stroke=st)
    for u in (3.4, 4.0, 4.6, 5.2):
        d.circle_on("y", (u, D, 7.89), 0.14, stroke=st)
    d.rect_on("y", D, 1.6, 6.75, 4.4, 7.05, stroke=st)
    d.rect_on("y", D, 0.18, 0.0, W - 0.18, 0.6, stroke="muted")
    d.line3((W, 0.25, H - 0.35), (W, D - 0.25, H - 0.35), stroke=st)
    d.anchor("controls", (4.3, D, 7.9))
    d.anchor("display", (1.55, D, 7.89))
    d.anchor("door", (3.0, D, 4.0))


def water_heater(d):
    R = 2.4
    d.cylinder_z(0, 0, R + 0.1, 0, 0.45)
    d.cylinder_z(0, 0, R, 0.45, 9.0)

    def band(z, a0=-45, a1=135, r=R):
        pts = [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)), z) for a in range(a0, a1 + 1, 3)]
        d.poly3(pts, close=False)

    band(1.3)
    band(8.2)
    # rating plate wrapped on the front of the tank
    top = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 6.4) for a in range(25, 66, 2)]
    bot = [(R * math.cos(math.radians(a)), R * math.sin(math.radians(a)), 5.0) for a in range(65, 24, -2)]
    d.poly3(top + bot)
    # gas control and pipes
    c = math.cos(math.radians(45)) * R
    d.box(c - 0.2, c - 0.2, 1.7, 0.75, 0.75, 0.8)
    d.cylinder_z(1.05, -1.05, 0.22, 9.0, 10.2)
    d.cylinder_z(-1.05, 1.05, 0.22, 9.0, 10.2)
    d.cylinder_z(0, 0, 0.95, 9.0, 9.35)
    d.cylinder_z(0, 0, 0.55, 9.35, 11.0)
    d.anchor("plate", (R * math.cos(math.radians(45)), R * math.sin(math.radians(45)), 5.7))
    d.anchor("valve", (c + 0.2, c + 0.2, 2.1))


def condenser(d):
    W = 8
    d.box(0.35, 0.35, 0, W - 0.7, W - 0.7, 0.3)
    d.box(0, 0, 0.3, W, W, 6.6)
    zt = 6.9
    for i in range(1, 30):
        u = 0.27 * i
        if u > W - 0.3:
            break
        d.line3((u, W, 0.75), (u, W, zt - 0.45), stroke="muted", sw=1)
        if u < 5.0:
            d.line3((W, u, 0.75), (W, u, zt - 0.45), stroke="muted", sw=1)
    d.rect_on("x", W, 5.1, 0.75, 7.6, zt - 0.45)
    for v in (1.1, zt - 0.8):
        d.circle_on("x", (W, 5.4, v), 0.08)
        d.circle_on("x", (W, 7.3, v), 0.08)
    for r in (3.1, 2.45, 1.8):
        d.circle_on("z", (4, 4, zt), r)
    d.circle_on("z", (4, 4, zt), 0.55)
    for a in (45, 135, 225, 315):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line3((4 + 0.55 * ca, 4 + 0.55 * sa, zt), (4 + 3.1 * ca, 4 + 3.1 * sa, zt))
    d.anchor("fan", (4, 4, zt))
    d.anchor("fan-ring", (5.2, 4, zt))  # between the hub and the second ring
    d.anchor("panel", (W, 6.35, 3.5))


SCENES = {
    "building": (building, 34),
    "unit-plan": (unit_plan, 46),
    "dishwasher": (dishwasher, 40),
    "water-heater": (water_heater, 40),
    "condenser": (condenser, 36),
}
SCENES.update(MORE)
SCENES.update(PRIVATE_SCENES)

# Corner rounding (drawing units) and outer-contour weight per scene; the defaults suit objects.
# Architecture stays square-cornered; plans keep a lighter contour so walls do not shout.
ROUND = {"building": 0, "building-floors": 0, "unit-plan": 0, "ladder": 0, "paint": 0}
SIL = {"building": 1.5, "building-floors": 1.5, "unit-plan": 1.3}

anchors, private_anchors = {}, {}
for name, (fn, scale) in SCENES.items():
    private = name in PRIVATE_SCENES
    if private and not PRIVATE:
        continue
    out = (PRIVATE / "svg") if private else OUT
    out.mkdir(parents=True, exist_ok=True)
    for theme in ("dark", "light"):
        d = Drawing(theme, scale=scale, sw=1.25, round=ROUND.get(name, 0.22), sil=SIL.get(name, 1.6))
        fn(d)
        svg, box = d.svg(pad=28)
        (out / f"{name}-{theme}.svg").write_text(svg)
        if theme == "dark":
            x0, y0, w, h = box
            entry = {"viewBox": [round(x0, 1), round(y0, 1), round(w, 1), round(h, 1)],
                     "points": {k: [round(v[0], 1), round(v[1], 1)] for k, v in d.anchors.items()}}
            (private_anchors if private else anchors)[name] = entry
# The phone is the website's own isometric phone (see phone_site.py), not drawn here.
light, dark, anchors["phone"] = phone_site.build()
(OUT / "phone-light.svg").write_text(light)
(OUT / "phone-dark.svg").write_text(dark)
(OUT.parent / "anchors.json").write_text(json.dumps(anchors, indent=1))
if PRIVATE:
    (PRIVATE / "anchors.json").write_text(json.dumps(private_anchors, indent=1))
print("built", [n for n in SCENES if PRIVATE or n not in PRIVATE_SCENES])
