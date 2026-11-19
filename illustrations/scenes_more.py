"""More library drawings: appliances, fixtures, building systems, tools, devices.

Front faces sit on the y = max face (the one facing down-left), like the dishwasher.
Each function draws into an iso.Drawing.
"""
import math
from iso import rounded_rect


def fridge(d):
    W, D, H = 6, 6.6, 14
    d.box(0, 0, 0, W, D, H)
    d.rect_on("y", D, 0.15, 5.6, 2.95, H - 0.15)
    d.rect_on("y", D, 3.05, 5.6, W - 0.15, H - 0.15)
    d.rect_on("y", D, 0.15, 0.7, W - 0.15, 5.45)
    d.rect_on("y", D, 2.55, 8.2, 2.72, 11.6)
    d.rect_on("y", D, 3.28, 8.2, 3.45, 11.6)
    d.rect_on("y", D, 1.6, 4.75, 4.4, 4.95)
    d.rect_on("y", D, 0.75, 8.6, 1.95, 10.8, fill="accent")
    d.line3((0.95, D, 9.2), (1.75, D, 9.2), stroke="muted", sw=1)
    for u in (0.6, 1.2, 1.8, 2.4, 3.0, 3.6, 4.2, 4.8, 5.4):
        d.line3((u, D, 0.12), (u + 0.3, D, 0.12 + 0.36), stroke="muted", sw=1)
    d.line3((W, 0.3, H - 0.4), (W, D - 0.3, H - 0.4), stroke="muted", sw=1)
    d.anchor("dispenser", (1.35, D, 9.7))
    d.anchor("freezer", (3.0, D, 3.0))


def range_stove(d):
    W, D, H = 6, 5.6, 7.2
    # backguard first: it stands behind the cooktop
    d.box(0, 0, 0, W, 0.6, H + 1.6)
    for u in (0.9, 1.9, 4.1, 5.1):
        d.circle_on("y", (u, 0.6, H + 0.85), 0.3)
    d.rect_on("y", 0.6, 2.4, H + 0.55, 3.6, H + 1.15)
    d.box(0, 0.6, 0, W, D - 0.6, H)
    d.rect_on("y", D, 0.2, 0.75, W - 0.2, 5.7)
    d.rect_on("y", D, 0.9, 2.0, W - 0.9, 4.7, fill="accent", stroke="muted")
    d.rect_on("y", D, 1.4, 5.15, 4.6, 5.35)
    d.rect_on("y", D, 0.2, 0.08, W - 0.2, 0.62)
    for (cx, cy, r) in ((1.5, 1.85, 0.85), (4.5, 1.85, 0.7), (1.5, 4.1, 0.7), (4.5, 4.1, 0.85)):
        d.circle_on("z", (cx, cy, H), r)
        d.circle_on("z", (cx, cy, H), r * 0.45, stroke="muted", sw=1)
    d.anchor("burner", (1.5, 1.85, H))
    d.anchor("hob", (2.1, 1.85, H))  # inside the burner ring, outside its centre: the whole ring
    d.anchor("oven", (3.0, D, 3.3))


def washer_dryer(d):
    W, D, H = 6, 6.3, 6.4
    for k, z0 in enumerate((0, H)):
        d.box(0, 0, z0, W, D, H)
        d.rect_on("y", D, 0.2, z0 + H - 1.15, W - 0.2, z0 + H - 0.2)
        d.rect_on("y", D, 0.5, z0 + H - 0.95, 2.2, z0 + H - 0.4, stroke="muted")
        d.circle_on("y", (4.6, D, z0 + H - 0.67), 0.24)
        d.circle_on("y", (3.0, D, z0 + 2.65), 1.95)
        d.circle_on("y", (3.0, D, z0 + 2.65), 1.45, fill="accent", stroke="muted", sw=1)
        if k == 0:
            d.rect_on("y", D, 4.8, z0 + 0.25, 5.6, z0 + 0.65)
    d.anchor("washer", (3.0, D, 2.65))
    d.anchor("dryer", (3.0, D, H + 2.65))


def furnace(d):
    W, D, H = 5.6, 6.0, 11.5
    d.cylinder_z(1.4, 1.6, 0.8, H, H + 2.6)
    d.box(0, 0, 0, W, D, H)
    d.rect_on("y", D, 0.2, 6.2, W - 0.2, H - 0.25)
    for i in range(9):
        z = 6.8 + i * 0.45
        d.line3((0.8, D, z), (W - 0.8, D, z), stroke="muted", sw=1)
    d.rect_on("y", D, 0.2, 0.25, W - 0.2, 6.0)
    d.rect_on("y", D, 2.2, 3.6, 3.4, 4.4)
    d.circle_on("y", (4.4, D, 4.0), 0.22)
    d.rect_on("x", W, 0.8, 0.9, 5.2, 1.3)
    d.line3((W, 0.8, 1.1), (W, 5.2, 1.1), stroke="muted", sw=1)
    d.anchor("filter", (W, 3.0, 1.1))
    d.anchor("burner", (2.8, D, 4.0))


def vanity(d):
    W, D = 6.4, 4.2
    d.box(0.2, 0.3, 7.0 - 0.6, W - 0.4, 0.35, 1.3)
    d.box(0.2, 0.3, 0, W - 0.4, D - 0.3, 6.0)
    d.box(0, 0.3, 6.0, W, D - 0.1, 0.45)
    d.circle_on("z", (W / 2, 2.2, 6.45), 1.35)
    d.circle_on("z", (W / 2, 2.2, 6.45), 0.95, stroke="muted", sw=1)
    d.cylinder_z(W / 2, 0.85, 0.2, 6.45, 7.6)
    d.box(W / 2 - 0.12, 0.85, 7.35, 0.24, 0.85, 0.22)
    d.rect_on("y", D + 0.2, 0.45, 0.4, W / 2 - 0.08, 5.7)
    d.rect_on("y", D + 0.2, W / 2 + 0.08, 0.4, W - 0.45, 5.7)
    for u in (W / 2 - 0.45, W / 2 + 0.45):
        d.circle_on("y", (u, D + 0.2, 4.6), 0.13)
    d.anchor("basin", (W / 2, 2.2, 6.45))
    d.anchor("trap", (W / 2, D + 0.2, 3.0))


def toilet(d):
    d.box(0.2, 0, 3.4, 4.0, 1.7, 3.6)
    d.box(0.05, -0.1, 7.0, 4.3, 1.9, 0.35)
    d.box(0.5, 1.7, 6.1, 0.55, 0.12, 0.2)
    ell = lambda cx, cy, rx, ry: [(cx + rx * math.cos(2 * math.pi * i / 48), cy + ry * math.sin(2 * math.pi * i / 48)) for i in range(48)]
    d.slab(ell(2.2, 3.4, 1.05, 1.5), 0, 1.6)
    d.slab(ell(2.2, 3.7, 1.7, 2.25), 1.6, 3.6)
    d.poly3([(x, y, 3.6) for x, y in ell(2.2, 3.85, 1.2, 1.7)], stroke="muted")
    d.anchor("tank", (2.2, 1.7, 5.4))
    d.anchor("seat", (2.2, 3.7, 3.6))


def electrical_panel(d):
    W, D, H = 5.2, 1.0, 8.6
    for x in (1.2, 2.6, 4.0):
        d.cylinder_z(x, 0.5, 0.28, H, H + 1.8)
    d.box(0, 0, 0, W, D, H)
    d.rect_on("y", D, 0.25, 0.25, W - 0.25, H - 0.25)
    d.rect_on("y", D, 1.7, 6.9, 3.5, 7.9)
    d.line3((2.6, D, 7.15), (2.6, D, 7.65))
    for col in (0.75, 2.85):
        for i in range(11):
            z = 0.8 + i * 0.52
            d.rect_on("y", D, col, z, col + 1.6, z + 0.38, stroke="muted", sw=1)
            d.line3((col + 0.65, D, z + 0.19), (col + 0.95, D, z + 0.19))
    d.anchor("main", (2.6, D, 7.4))
    d.anchor("breakers", (3.65, D, 3.6))


def thermostat(d):
    d.box(0, 0, 0, 4.4, 0.3, 4.4)
    d.box(0.45, 0.3, 0.45, 3.5, 0.45, 3.5)
    d.circle_on("y", (2.2, 0.75, 2.2), 1.45)
    d.circle_on("y", (2.2, 0.75, 2.2), 1.05, stroke="muted", sw=1)
    d.rect_on("y", 0.75, 1.6, 2.0, 2.8, 2.5, fill="accent")
    d.anchor("dial", (2.2, 0.75, 2.2))


def smoke_detector(d):
    d.cylinder_z(0, 0, 2.6, 0, 0.25)
    d.cylinder_z(0, 0, 2.3, 0.25, 1.0)
    for r in (1.8, 1.2):
        d.circle_on("z", (0, 0, 1.0), r, stroke="muted", sw=1)
    for a in range(0, 360, 30):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        d.line3((1.25 * ca, 1.25 * sa, 1.0), (1.75 * ca, 1.75 * sa, 1.0), stroke="muted", sw=1)
    d.circle_on("z", (0, 0, 1.0), 0.35, fill="accent")
    d.anchor("sensor", (0, 0, 1.0))


def rooftop_unit(d):
    W, D, H = 11, 7, 5.2
    d.box(0.3, 0.3, 0, W - 0.6, D - 0.6, 0.6)
    d.box(0, 0, 0.6, W, D, H)
    for i in range(1, 34):
        u = 0.3 * i
        if u > 6.2:
            break
        d.line3((u, D, 1.2), (u, D, H - 0.1), stroke="muted", sw=1)
    d.rect_on("y", D, 6.6, 1.2, W - 0.4, H - 0.1)
    for v in (1.6, 2.4, 3.2, 4.0, 4.8):
        d.line3((6.9, D, v), (W - 0.7, D, v), stroke="muted", sw=1)
    d.box(W, 1.2, 1.4, 0.9, 4.6, 3.0)
    for v in (2.0, 2.6, 3.2, 3.8):
        d.line3((W + 0.9, 1.5, v), (W + 0.9, 5.5, v), stroke="muted", sw=1)
    zt = H + 0.6
    for cx in (2.6, 6.0):
        d.circle_on("z", (cx, 3.5, zt), 1.5)
        d.circle_on("z", (cx, 3.5, zt), 0.35)
        for a in (0, 90, 180, 270):
            ca, sa = math.cos(math.radians(a + 45)), math.sin(math.radians(a + 45))
            d.line3((cx + 0.35 * ca, 3.5 + 0.35 * sa, zt), (cx + 1.5 * ca, 3.5 + 1.5 * sa, zt))
    d.anchor("fans", (4.3, 3.5, zt))
    d.anchor("hood", (W + 0.9, 3.5, 3.0))


def ladder(d):
    """A stepladder built as solids, drawn far to near so nearer parts hide farther ones:
    back legs, their braces, the left front rail, the steps, the right front rail, the top."""
    H, yb_f, yt, yb_b = 10.0, 4.0, 2.0, 0.0
    w, rail, t = 3.0, 0.26, 0.5  # rail width across (x) and thickness front to back (y)

    def rail_bar(x, yb, ytop, zt):
        """A slanted rail from (yb, z=0) to (ytop, zt): its front face, its outer side, its top."""
        lo = [(x, yb - t / 2, 0), (x + rail, yb - t / 2, 0), (x + rail, yb + t / 2, 0), (x, yb + t / 2, 0)]
        hi = [(x, ytop - t / 2, zt), (x + rail, ytop - t / 2, zt), (x + rail, ytop + t / 2, zt), (x, ytop + t / 2, zt)]
        d.quad([lo[3], lo[2], hi[2], hi[3]], "left")    # front face (y max)
        d.quad([lo[1], lo[2], hi[2], hi[1]], "right")   # outer side (x max)
        d.quad(hi, "top")                               # top end
        d.outline(lo + hi)

    def rail_y(yb, ytop, zt, z):
        return yb + (ytop - yb) * z / zt

    # back legs and the braces between them
    rail_bar(0, yb_b, yt - 0.35, H - 0.4)
    rail_bar(w - rail, yb_b, yt - 0.35, H - 0.4)
    for z in (2.2, 4.6):
        y = rail_y(yb_b, yt - 0.35, H - 0.4, z)
        d.line3((rail, y, z), (w - rail, y, z), stroke="muted", sw=1)
    # left front rail, then the steps (their right ends run into the right rail), then the right rail
    rail_bar(0, yb_f, yt, H)
    for k in range(1, 5):
        z = k * 2.0
        y = rail_y(yb_f, yt, H, z)
        d.box(rail, y - t / 2 + 0.04, z - 0.14, w - rail * 1.5, t - 0.08, 0.14)
    rail_bar(w - rail, yb_f, yt, H)
    # the top platform sits over all four rails
    d.box(-0.1, yt - 0.9, H, w + 0.2, 1.2, 0.35)
    d.anchor("top", (w / 2, yt - 0.3, H + 0.35))


def toolbox(d):
    W, D, H = 7.4, 3.6, 2.8
    d.box(0, 0, 0, W, D, H)
    d.box(-0.1, -0.1, H, W + 0.2, D + 0.2, 0.55)
    for x in (2.4, 4.8):
        d.box(x, D / 2 - 0.15, H + 0.55, 0.25, 0.3, 0.8)
    d.box(2.4, D / 2 - 0.15, H + 1.35, 2.65, 0.3, 0.25)
    for u in (0.9, W - 1.5):
        d.rect_on("y", D + 0.1, u, H - 0.3, u + 0.6, H + 0.35)
    d.line3((0, D, 1.0), (W, D, 1.0), stroke="muted", sw=1)
    d.anchor("handle", (3.7, D / 2, H + 1.6))


def paint(d):
    d.box(0, 0, 0, 5.4, 6.4, 0.5)
    d.quad([(0.4, 0.4, 0.5), (5.0, 0.4, 0.5), (5.0, 3.8, 0.15), (0.4, 3.8, 0.15)], stroke="muted")
    for k in range(1, 6):
        y = 3.8 + k * 0.42
        d.line3((0.5, y, 0.5), (4.9, y, 0.5), stroke="muted", sw=1)
    d.cylinder_x(4.8, 1.05, 0.55, 1.0, 4.4)
    d.line3((4.4, 4.8, 1.05), (5.1, 4.8, 1.05))
    d.line3((5.1, 4.8, 1.05), (5.1, 6.3, 1.9))
    d.box(4.95, 6.3, 1.7, 0.3, 2.0, 0.4)
    d.cylinder_z(8.6, 2.4, 1.7, 0, 3.6)
    d.circle_on("z", (8.6, 2.4, 3.6), 1.45, stroke="muted", sw=1)
    d.anchor("roller", (2.7, 4.8, 1.6))
    d.anchor("can", (8.6, 2.4, 3.6))


def laptop(d):
    W, D = 8, 5.6
    d.quad([(0, 0.2, 0.3), (W, 0.2, 0.3), (W, -0.9, 5.5), (0, -0.9, 5.5)], fill="accent")
    d.quad([(0.35, 0.12, 0.75), (W - 0.35, 0.12, 0.75), (W - 0.35, -0.82, 5.15), (0.35, -0.82, 5.15)], fill="top", stroke="muted")
    for i, (x0, x1) in enumerate(((0.9, 4.2), (0.9, 6.6), (0.9, 6.6), (0.9, 5.4))):
        f = 0.2 + i * 0.18
        z = 0.75 + (5.15 - 0.75) * (1 - f)
        y = 0.12 + (-0.82 - 0.12) * (1 - f)
        d.line3((x0, y, z), (x1, y, z), stroke="muted" if i else "stroke", sw=1)
    d.box(0, 0.2, 0, W, D, 0.3)
    d.rect_on("z", 0.3, 0.7, 0.8, W - 0.7, 3.1, stroke="muted")
    for i in range(1, 4):
        y = 0.8 + i * 0.575
        d.line3((0.7, y, 0.3), (W - 0.7, y, 0.3), stroke="muted", sw=1)
    d.rect_on("z", 0.3, 2.9, 3.6, 5.1, 5.2)
    d.anchor("screen", (4.0, -0.4, 3.4))
    d.anchor("trackpad", (4.0, 4.4, 0.3))


def building_floors(d, hi=True):
    """The building as separate floor groups (f0..f4, roof) for the explode motion."""
    W, D, F, FH = 12, 7, 5, 1.3
    for k in range(F):
        z0 = k * FH
        d.group(f"floor-{k}")
        d.box(0, 0, z0, W, D, FH)
        if hi and k == 2:
            d.rect_on("y", D, 7.3, z0, W, z0 + FH, fill="hi_l", stroke="hi_stroke")
            d.rect_on("x", W, 3.6, z0, D, z0 + FH, fill="hi_r", stroke="hi_stroke")
        for i in range(8):
            u0 = 0.5 + i * 1.42
            if k == 0 and i == 3:
                continue
            on_hi = hi and k == 2 and u0 >= 7.3
            d.rect_on("y", D, u0, z0 + 0.35, u0 + 0.72, z0 + 1.0, stroke="hi_stroke" if on_hi else "stroke")
        for j in range(4):
            u0 = 0.55 + j * 1.6
            on_hi = hi and k == 2 and u0 >= 3.6
            d.rect_on("x", W, u0, z0 + 0.35, u0 + 0.8, z0 + 1.0, stroke="hi_stroke" if on_hi else "stroke")
        if k == 0:
            d.rect_on("y", D, 4.55, 0, 5.65, 1.0)
        d.end()
        d.anchor(f"floor-{k}", (W, D, z0 + FH / 2))
    d.group("roof")
    # A thin lid, so the roof reads as a solid plate when it lifts off.
    H = F * FH + 0.14
    d.box(0, 0, F * FH, W, D, 0.14)
    d.rect_on("z", H, 0.22, 0.22, W - 0.22, D - 0.22)
    for x in (1.6, 3.6):
        d.box(x, 1.2, H, 1.5, 1.3, 0.7)
        d.circle_on("z", (x + 0.75, 1.85, H + 0.7), 0.42)
    d.box(8.6, 0.9, H, 2.2, 2.4, 1.15)
    d.end()
    d.anchor("unit", (9.65 + 0.6, D, 2 * FH + FH / 2))
    d.anchor("unit-right", (W, 5.3, 2 * FH + FH / 2))


MORE = {
    "fridge": (fridge, 30),
    "range": (range_stove, 38),
    "washer-dryer": (washer_dryer, 32),
    "furnace": (furnace, 34),
    "vanity": (vanity, 40),
    "toilet": (toilet, 44),
    "electrical-panel": (electrical_panel, 40),
    "thermostat": (thermostat, 60),
    "smoke-detector": (smoke_detector, 60),
    "rooftop-unit": (rooftop_unit, 30),
    "ladder": (ladder, 32),
    "toolbox": (toolbox, 40),
    "paint": (paint, 36),
    "laptop": (laptop, 38),
    "building-floors": (building_floors, 34),
}
