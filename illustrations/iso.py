"""Small isometric line-drawing engine for Verstack illustrations.

Draws hairline isometric solids as SVG. Faces are filled with the ground colour so
nearer solids hide farther lines (painter's order: add far things first). One
optional lime highlight per drawing. No shading, no gradients.
"""
import math

C30 = math.cos(math.radians(30))
S30 = math.sin(math.radians(30))

THEMES = {
    # stroke on ground, faces filled with the ground they sit on
    "dark": {"bg": "#171a19", "stroke": "#f8fafc", "muted": "#8b8f8d", "hi_top": "#a5fc22", "hi_l": "#7ff553", "hi_r": "#8ff741", "hi_stroke": "#171a19"},
    "light": {"bg": "#f8fafc", "stroke": "#30303a", "muted": "#9a9aa3", "hi_top": "#a5fc22", "hi_l": "#7ff553", "hi_r": "#8ff741", "hi_stroke": "#30303a"},
}


def proj(x, y, z, s):
    """Project a 3D point to 2D isometric screen space (y down)."""
    return ((x - y) * C30 * s, (x + y) * S30 * s - z * s)


def hull(points):
    """Convex hull (monotone chain) of 2D points, counter-clockwise."""
    pts = sorted(set((round(p[0], 3), round(p[1], 3)) for p in points))
    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def rounded_rect(x0, y0, x1, y1, r, n=8):
    """Footprint points of a rounded rectangle in the x-y plane."""
    pts = []
    corners = [(x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)]
    for cx, cy, a0 in corners:
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


class Drawing:
    """Collects SVG elements in draw order and tracks the bounding box."""

    def __init__(self, theme="dark", scale=40, sw=1.25, round=0.0, sil=1.6):
        self.t = THEMES[theme]
        self.s = scale
        self.sw = sw
        # Website phone weights: the outer contour is heavier than the lines inside it
        # (0.5 against 0.3 on verstack.ai). sil is that ratio; round softens box corners.
        self.round = round
        self.sil = sil
        self.els = []
        self.xs, self.ys = [], []
        self.anchors = {}

    # --- low level -------------------------------------------------------
    def _pt(self, p):
        X, Y = proj(*p, self.s)
        self.xs.append(X)
        self.ys.append(Y)
        return X, Y

    def _attrs(self, fill, stroke, sw, dash=None):
        fill = self.t.get(fill, fill) if fill else "none"
        stroke = self.t.get(stroke, stroke) if stroke else "none"
        a = f'fill="{fill}" stroke="{stroke}" stroke-width="{sw or self.sw}" stroke-linejoin="round" stroke-linecap="round" vector-effect="non-scaling-stroke"'
        if dash:
            a += f' stroke-dasharray="{dash}"'
        return a

    def poly3(self, pts, fill="bg", stroke="stroke", sw=None, close=True, dash=None):
        p2 = [self._pt(p) for p in pts]
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in p2)
        tag = "polygon" if close else "polyline"
        if not close:
            fill = None
        self.els.append(f'<{tag} points="{d}" {self._attrs(fill, stroke, sw, dash)}/>')

    def poly2(self, p2, fill="bg", stroke="stroke", sw=None, close=True):
        for x, y in p2:
            self.xs.append(x)
            self.ys.append(y)
        d = " ".join(f"{x:.2f},{y:.2f}" for x, y in p2)
        tag = "polygon" if close else "polyline"
        self.els.append(f'<{tag} points="{d}" {self._attrs(fill if close else None, stroke, sw)}/>')
        # (fill None on a closed shape draws an outline only)

    def line3(self, a, b, stroke="stroke", sw=None, dash=None):
        (x1, y1), (x2, y2) = self._pt(a), self._pt(b)
        self.els.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" {self._attrs(None, stroke, sw, dash)}/>')

    def anchor(self, name, p):
        self.anchors[name] = proj(*p, self.s)

    def group(self, gid):
        """Open an SVG group (for motion: floors, parts). Close with end()."""
        self.els.append(f'<g id="{gid}">')

    def end(self):
        self.els.append("</g>")

    def quad(self, pts, fill="bg", stroke="stroke"):
        """Any flat four-sided face given as 3D points (slanted parts)."""
        self.poly3(pts, fill, stroke)

    # --- solids ----------------------------------------------------------
    def outline(self, pts3, stroke="stroke"):
        """The heavy outer contour of a solid: the hull of its projected points, no fill."""
        sil = hull([proj(*p, self.s) for p in pts3])
        self.poly2(sil, None, stroke, self.sw * self.sil)

    def box(self, x, y, z, w, d, h, fill="bg", hi=False, stroke=None):
        """Axis-aligned box; draws the two front faces and the top, then its outer contour.
        With Drawing(round=r) a box at least 1 unit across gets rounded vertical edges."""
        x1, y1, z1 = x + w, y + d, z + h
        st = stroke or ("hi_stroke" if hi else "stroke")
        r = min(self.round, 0.18 * min(w, d))
        if r > 0.05 and min(w, d) >= 1.0 and not hi:
            self.slab(rounded_rect(x, y, x1, y1, r), z, z1, fill, stroke=st)
            return
        f_l, f_r, f_t = ("hi_l", "hi_r", "hi_top") if hi else (fill, fill, fill)
        # face looking down-left (y = y1)
        self.poly3([(x, y1, z), (x1, y1, z), (x1, y1, z1), (x, y1, z1)], f_l, st)
        # face looking down-right (x = x1)
        self.poly3([(x1, y, z), (x1, y1, z), (x1, y1, z1), (x1, y, z1)], f_r, st)
        self.poly3([(x, y, z1), (x1, y, z1), (x1, y1, z1), (x, y1, z1)], f_t, st)
        if self.sil > 1:
            self.outline([(a, b, c) for a in (x, x1) for b in (y, y1) for c in (z, z1)], st)

    def slab(self, foot, z0, z1, fill="bg", hi=False, stroke=None):
        """Convex prism from a footprint: silhouette, then the top outline."""
        st = stroke or ("hi_stroke" if hi else "stroke")
        bottom = [(x, y, z0) for x, y in foot]
        top = [(x, y, z1) for x, y in foot]
        sil = hull([proj(*p, self.s) for p in bottom + top])
        self.poly2(sil, "hi_l" if hi else fill, st, self.sw * self.sil)
        self.poly3(top, "hi_top" if hi else fill, st)

    def cylinder_z(self, cx, cy, r, z0, z1, fill="bg", stroke="stroke", n=72, top=True):
        """Upright cylinder."""
        circ = lambda z: [(cx + r * math.cos(2 * math.pi * i / n), cy + r * math.sin(2 * math.pi * i / n), z) for i in range(n)]
        sil = hull([proj(*p, self.s) for p in circ(z0) + circ(z1)])
        self.poly2(sil, fill, stroke, self.sw * self.sil)
        if top:
            self.poly3(circ(z1), fill, stroke)

    def cylinder_x(self, cy, cz, r, x0, x1, fill="bg", stroke="stroke", n=72):
        """Cylinder lying along x (e.g. a battery cell)."""
        circ = lambda x: [(x, cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]
        sil = hull([proj(*p, self.s) for p in circ(x0) + circ(x1)])
        self.poly2(sil, fill, stroke, self.sw * self.sil)
        self.poly3(circ(x1), fill, stroke)

    def circle_on(self, plane, c, r, fill=None, stroke="stroke", sw=None, n=64):
        """Circle lying in a plane: 'z' (horizontal), 'x' or 'y' (vertical faces)."""
        pts = []
        for i in range(n):
            a = 2 * math.pi * i / n
            u, v = r * math.cos(a), r * math.sin(a)
            if plane == "z":
                pts.append((c[0] + u, c[1] + v, c[2]))
            elif plane == "x":
                pts.append((c[0], c[1] + u, c[2] + v))
            else:
                pts.append((c[0] + u, c[1], c[2] + v))
        self.poly3(pts, fill, stroke, sw)

    def rect_on(self, plane, at, u0, v0, u1, v1, fill=None, stroke="stroke", sw=None):
        """Rectangle on a face. plane 'x': u=y, v=z. plane 'y': u=x, v=z. plane 'z': u=x, v=y."""
        if plane == "x":
            pts = [(at, u0, v0), (at, u1, v0), (at, u1, v1), (at, u0, v1)]
        elif plane == "y":
            pts = [(u0, at, v0), (u1, at, v0), (u1, at, v1), (u0, at, v1)]
        else:
            pts = [(u0, v0, at), (u1, v0, at), (u1, v1, at), (u0, v1, at)]
        self.poly3(pts, fill, stroke, sw)

    # --- output ----------------------------------------------------------
    def svg(self, pad=24, width=None):
        x0, y0 = min(self.xs) - pad, min(self.ys) - pad
        w, h = max(self.xs) - x0 + pad, max(self.ys) - y0 + pad
        attrs = f'viewBox="{x0:.1f} {y0:.1f} {w:.1f} {h:.1f}"'
        if width:
            attrs += f' width="{width}" height="{width * h / w:.0f}"'
        body = "\n".join(self.els)
        return f'<svg xmlns="http://www.w3.org/2000/svg" {attrs}>\n{body}\n</svg>\n', (x0, y0, w, h)
