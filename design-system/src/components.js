/* Verstack marketing components: the parts every motion clip is built from.
   Data flow: Frame (dark ground) holds Cards (light, radius 40 at 1080p) laid out by
   VS.layout; each Card holds one piece of imagery, always centred both ways:
   a Drawing (line art from VS.assets.drawings), a Phone or Screen (real app captures
   from product-ui/), with an optional Ring. Sizes scale with the frame's short side,
   so the same clip renders at 1920 x 1080, 1080 x 1080 or 1080 x 1350.
   No component draws text: clips are imagery only. */
window.VS = window.VS || {};
VS.base = VS.base || "../";

(() => {
  const MIST = "#f8fafc", LIME = "#a5fc22", INK = "#30303a";
  const LIME_RE = /#a5fc22|#7ff553|#8ff741/i;

  /** Light and dark modes. Light: light cards on the dark ground. Dark: dark scene cards
      (the website's scene-dark) on the same ground, drawn in light lines. Drawings are toned
      like the phone on verstack.ai; `roles` gives each drawn role its colour in the mode
      (tones from brand/tokens.json tone-*), `map` recolours the website phone's own colours. */
  const T = (n) => VS.tokens[n];
  const roles = (mode, ink, muted) => ({
    top: T(`tone-top-${mode}`), left: T(`tone-left-${mode}`), right: T(`tone-right-${mode}`),
    side: T(`tone-side-${mode}`), accent: T(`tone-accent-${mode}`), bg: T(`tone-top-${mode}`),
    stroke: ink, muted, hi_stroke: ink, hi_top: "#a5fc22", hi_l: "#7ff553", hi_r: "#8ff741",
  });
  const THEMES = {
    light: {
      name: "light", ground: "#171a19", card: MIST, ink: INK, edge: INK, dot: INK, limeStroke: null,
      roles: roles("light", INK, "#9a9aa3"), map: {},
    },
    dark: {
      name: "dark", ground: "#171a19", card: "#141416", ink: MIST, edge: "rgb(248 250 252 / 0.24)", dot: "#141416", limeStroke: "#141416",
      cardEdge: "rgb(248 250 252 / 0.08)",
      roles: roles("dark", MIST, "#8b8f8d"),
      map: {
        "#b7b5af": "#3a3e3c", "#cecdcb": "#2a2e2c", "#3f3e3e": "#0c0d0d", "#ffffff": "#1e1e22",
        "#2c292a": MIST, "#282828": MIST, "#525151": "#c2c4c5", "#706f6e": "#8b8f8d",
      },
    },
  };
  const recolor = (theme, c) => (c && theme.map[c.toLowerCase()]) || c;
  const SCREEN = { size: [421, 880], inset: [14, 14, 393, 852], radius: 46, shell: 60, statusBar: 50 };

  const el = (tag, cls, style = {}, parent) => {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    Object.assign(e.style, style);
    if (parent) parent.appendChild(e);
    return e;
  };
  const px = (v) => `${Math.round(v * 100) / 100}px`;

  /** The dark ground. u is the scale unit: 1 at a 1080px short side. */
  function Frame(root, W, H, themeName = "light") {
    const theme = THEMES[themeName] || THEMES.light;
    const node = el("div", "vs-frame", { position: "relative", width: px(W), height: px(H), overflow: "hidden", background: theme.ground }, root);
    node.dataset.theme = theme.name;
    return { el: node, W, H, u: Math.min(W, H) / 1080, theme };
  }

  /** Card boxes on a frame, with the seam (16px at 1080p) around and between them. */
  const layout = {
    single(f) { const s = 16 * f.u; return [{ x: s, y: s, w: f.W - 2 * s, h: f.H - 2 * s }]; },
    row(f, n, weights) {
      const s = 16 * f.u, ws = weights || Array(n).fill(1), sum = ws.reduce((a, b) => a + b, 0);
      const free = f.W - (n + 1) * s;
      let x = s;
      return ws.map((w) => { const b = { x, y: s, w: (free * w) / sum, h: f.H - 2 * s }; x += b.w + s; return b; });
    },
    grid(f, cols, rows) {
      const s = 16 * f.u, w = (f.W - (cols + 1) * s) / cols, h = (f.H - (rows + 1) * s) / rows, out = [];
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) out.push({ x: s + c * (w + s), y: s + r * (h + s), w, h });
      return out;
    },
  };

  /** A light card. Children are positioned inside it and clipped to its corners. */
  function Card(frame, box, { radius = 40 } = {}) {
    const node = el("div", "vs-card", {
      position: "absolute", left: px(box.x), top: px(box.y), width: px(box.w), height: px(box.h),
      borderRadius: px(radius * frame.u), background: frame.theme.card, overflow: "hidden",
      boxShadow: frame.theme.cardEdge ? `inset 0 0 0 ${px(1 * frame.u)} ${frame.theme.cardEdge}` : "none",
    }, frame.el);
    return { el: node, box, w: box.w, h: box.h, u: frame.u, frame, theme: frame.theme };
  }

  /** A layer inside a card that fills it: lets a clip fade or swap one piece of imagery. */
  const Layer = (card) => el("div", "vs-layer", { position: "absolute", inset: "0" }, card.el);

  /** A line drawing, centred in its card both ways.
      The SVG covers the card and its viewBox is the camera: centred on the drawing's
      content box, fitted so the drawing fills `fill` of the card height (and at most
      `fillW` of its width). `lift` reserves extra room above, in drawing units, for
      moves that grow the drawing upward (explode), so the moving whole stays centred.
      `lime`: an anchor name whose part becomes the lime part (replacing any built in).
      `limeOff`: keep the drawing all ink. */
  function Drawing(card, name, { fill = 0.68, fillW = 0.8, lift = 0, lime = null, limeOff = false, parent = null } = {}) {
    const a = VS.assets.drawings[name];
    if (!a) throw new Error(`no drawing ${name}`);
    const host = parent || card.el;
    const tpl = document.createElement("template");
    tpl.innerHTML = a.svg;
    const svg = tpl.content.firstElementChild;
    svg.setAttribute("width", card.w);
    svg.setAttribute("height", card.h);
    Object.assign(svg.style, { position: "absolute", left: "0", top: "0", overflow: "hidden" });
    svg.classList.add("vs-drawing");
    host.appendChild(svg);

    const bb = svg.getBBox();
    // Fit on the room the move needs (lift), centre on the drawing at rest.
    const k = Math.min((fill * card.h) / (bb.height + lift), (fillW * card.w) / bb.width);
    const base = { cx: bb.x + bb.width / 2, cy: bb.y + bb.height / 2 };
    const d = { svg, card, name, k, kk: k, vx: 0, vy: 0, base, rest: bb, items: [], limeItems: [] };

    /** Point the camera: centre (cx, cy) in drawing units, scale s over the fitted view. */
    d.look = (cx, cy, s = 1) => {
      d.kk = k * s;
      const vw = card.w / d.kk, vh = card.h / d.kk;
      d.vx = cx - vw / 2; d.vy = cy - vh / 2;
      svg.setAttribute("viewBox", `${d.vx} ${d.vy} ${vw} ${vh}`);
    };
    /** Camera from the centred view (p = 0) to scale s around focus (p = 1). */
    d.camera = (s = 1, focus = null, p = 0) => {
      const cx = focus ? base.cx + (focus[0] - base.cx) * p : base.cx;
      const cy = focus ? base.cy + (focus[1] - base.cy) * p : base.cy;
      d.look(cx, cy, s);
    };
    d.camera();

    /** Anchor point in drawing units. */
    d.anchor = (n) => { const p = a.points[n]; if (!p) throw new Error(`${name} has no anchor ${n}`); return p; };
    /** Anchor point in card pixels (under the current camera). */
    d.point = (n) => { const [x, y] = d.anchor(n); return [(x - d.vx) * d.kk, (y - d.vy) * d.kk]; };

    const theme = card.theme || THEMES.light;
    d.theme = theme;
    const SHAPES = "polygon,polyline,line,path,ellipse,circle";
    const shapes = [...svg.querySelectorAll(SHAPES)];
    // Line weight follows the website phone: proportional to the drawing's size on screen,
    // with the outer contour heavier than the lines inside it (each shape's stroke-width
    // relative to the drawing's heaviest sets its share).
    const size = Math.max(bb.width, bb.height) * k, u = card.u;
    const L = Math.min(2.8 * u, Math.max(1.7 * u, 0.003 * size));
    const swMax = Math.max(...shapes.map((n) => parseFloat(n.getAttribute("stroke-width") || 1)));
    d.items = shapes.map((node) => {
      // Mode: colour each element by its role (data-f fill, data-s stroke); elements without a
      // role (the website phone) by their own colour. A lime part's pre-light colour likewise.
      const r = theme.roles;
      if (node.dataset.f) node.setAttribute("fill", r[node.dataset.f]);
      else if (node.getAttribute("fill")) node.setAttribute("fill", recolor(theme, node.getAttribute("fill")));
      if (node.dataset.s) node.setAttribute("stroke", r[node.dataset.s]);
      else if (node.getAttribute("stroke")) node.setAttribute("stroke", recolor(theme, node.getAttribute("stroke")));
      if (node.dataset.ground) node.dataset.ground = r[node.dataset.ground] || recolor(theme, node.dataset.ground);
      node.setAttribute("vector-effect", "non-scaling-stroke");
      node.style.strokeWidth = px(L * parseFloat(node.getAttribute("stroke-width") || 1) / swMax);
      const len = node.getTotalLength() * d.kk + 2;
      const fillAttr = node.getAttribute("fill") || "none";
      node.style.strokeDasharray = `${len} ${len}`;
      node.style.strokeDashoffset = len;
      if (fillAttr !== "none") node.style.fillOpacity = 0;
      return { el: node, len, fill: fillAttr, stroke: node.getAttribute("stroke") };
    });
    const asLime = (it, fillColour) => {
      it.limeFill = fillColour;
      // An outline-only part (a door panel drawn on a face) stays clear until it lights.
      it.clear = !it.el.dataset.ground && it.fill === "none";
      it.groundFill = it.el.dataset.ground || it.fill;
      if (!it.clear) it.el.style.fill = it.groundFill;
      // The lines drawn on top of the part (a handle, window frames): in dark mode they turn
      // dark with it, or they would vanish into the lime.
      const i = d.items.indexOf(it);
      it.over = d.items.slice(i + 1).filter((o) => {
        if (!o.stroke || o.stroke[0] !== "#") return false;
        const b = o.el.getBBox();
        return it.el.isPointInFill(new DOMPoint(b.x + b.width / 2, b.y + b.height / 2));
      });
      d.limeItems.push(it);
    };
    // WHY: the built-in lime part starts as its ground so it reads as a normal face until the highlight.
    d.items.forEach((it) => { if (LIME_RE.test(it.fill)) { const c = it.fill; it.fill = it.el.dataset.ground || theme.roles.top; asLime(it, c); } });

    /** Make the part under an anchor the lime part: the smallest closed shape containing it
        (a door panel, a dial, a drawer), filled or outline only. */
    d.part = (n) => {
      const [x, y] = d.anchor(n);
      const pt = new DOMPoint(x, y);
      let best = null, area = Infinity;
      d.items.forEach((it) => {
        if (!/^(polygon|path|ellipse|circle)$/.test(it.el.tagName) || !it.el.isPointInFill(pt)) return;
        const b = it.el.getBBox(), ar = b.width * b.height;
        if (ar > 0 && ar < area) { area = ar; best = it; }
      });
      if (best) asLime(best, LIME);
      return best;
    };
    /** Centre of the lime part in drawing units (null if the drawing has none). */
    d.limeCenter = () => {
      if (!d.limeItems.length) return null;
      const bs = d.limeItems.map((it) => it.el.getBBox());
      const x0 = Math.min(...bs.map((b) => b.x)), y0 = Math.min(...bs.map((b) => b.y));
      const x1 = Math.max(...bs.map((b) => b.x + b.width)), y1 = Math.max(...bs.map((b) => b.y + b.height));
      return [(x0 + x1) / 2, (y0 + y1) / 2];
    };
    if (limeOff || lime) { d.limeItems.forEach((it) => { if (!it.clear) it.el.style.fill = it.groundFill; }); d.limeItems = []; }
    if (lime) d.part(lime);
    return d;
  }

  /** A real phone screen (device shell included), centred in its card.
      box(name) gives a captured element's rectangle in card pixels. */
  function Phone(card, screen, { fill = 0.86, dx = 0, parent = null } = {}) {
    const [sw, sh] = SCREEN.size;
    const h = fill * card.h, k = h / sh, w = sw * k;
    const x = (card.w - w) / 2 + dx, y = (card.h - h) / 2;
    const wrap = el("div", "vs-phone", { position: "absolute", left: px(x), top: px(y), width: px(w), height: px(h) }, parent || card.el);
    const img = el("img", "", { position: "absolute", left: "0", top: "0", width: px(w), height: px(h), borderRadius: px(SCREEN.shell * k) }, wrap);
    img.src = `${VS.base}product-ui/mobile/screens/${screen}.png`;
    img.alt = "";
    const [ix, iy, iw, ih] = SCREEN.inset;
    const p = {
      el: wrap, img, x, y, w, h, k, screen,
      box(n) {
        const b = VS.assets.productUi.mobile[screen].boxes[n];
        if (!b) throw new Error(`${screen} has no box ${n}`);
        return { x: x + b[0] * k, y: y + b[1] * k, w: b[2] * k, h: b[3] * k };
      },
      /** The screen area inside the shell, for a push that keeps the shell still. */
      screenArea: { x: ix * k, y: iy * k, w: iw * k, h: ih * k, r: SCREEN.radius * k },
    };
    return p;
  }

  /** A second screen that slides in over a Phone's screen area. The shell and the
      status bar stay still; only the app content below the status bar moves. */
  function PushScreen(phone, screen) {
    const a = phone.screenArea, bar = SCREEN.statusBar * phone.k;
    const clip = el("div", "vs-push", { position: "absolute", left: px(a.x), top: px(a.y + bar), width: px(a.w), height: px(a.h - bar), overflow: "hidden", borderRadius: `0 0 ${px(a.r)} ${px(a.r)}` }, phone.el);
    // WHY: the slide clips its own image (corners a little rounder than the screen's), so the
    // incoming capture's device shell never shows as it moves.
    const slide = el("div", "", { position: "absolute", inset: "0", visibility: "hidden", overflow: "hidden", borderRadius: `0 0 ${px(a.r * 1.4)} ${px(a.r * 1.4)}` }, clip);
    const img = el("img", "", { position: "absolute", left: px(-a.x), top: px(-(a.y + bar)), height: px(phone.h) }, slide);
    img.src = `${VS.base}product-ui/mobile/screens/${screen}.png`;
    img.alt = "";
    const k = phone.k;
    return {
      el: slide, img,
      box(n) {
        const b = VS.assets.productUi.mobile[screen].boxes[n];
        return { x: phone.x + b[0] * k, y: phone.y + b[1] * k, w: b[2] * k, h: b[3] * k };
      },
      at(p) { slide.style.visibility = p > 0 ? "visible" : "hidden"; slide.style.transform = `translateX(${(1 - p) * a.w}px)`; },
    };
  }

  /** A real desktop screen, centred in its card, with a hairline edge.
      view(s, focus, p) zooms toward a captured element; box(name) follows the zoom. */
  function Screen(card, screen, { fill = 0.84, fillW = 0.8 } = {}) {
    const meta = VS.assets.productUi.desktop[screen];
    const [sw, sh] = meta.size;
    const k0 = Math.min((fill * card.h) / sh, (fillW * card.w) / sw);
    const w = sw * k0, h = sh * k0, x = (card.w - w) / 2, y = (card.h - h) / 2;
    const win = el("div", "vs-screen", { position: "absolute", left: px(x), top: px(y), width: px(w), height: px(h), overflow: "hidden",
      borderRadius: px(18 * card.u), boxShadow: `0 0 0 ${px(1.5 * card.u)} ${card.theme.edge}`, background: "#fff" }, card.el);
    const img = el("img", "", { position: "absolute", left: "0", top: "0", width: px(sw), transformOrigin: "0 0" }, win);
    img.src = `${VS.base}product-ui/desktop/screens/${screen}.png`;
    img.alt = "";
    const s = { el: win, img, x, y, w, h, k: k0, tx: 0, ty: 0 };
    s.view = (scale = 1, focusName = null, p = 0) => {
      const kk = k0 * (1 + (scale - 1) * p);
      let fx = sw / 2, fy = sh / 2;
      if (focusName) { const b = meta.boxes[focusName]; fx = sw / 2 + (b[0] + b[2] / 2 - sw / 2) * p; fy = sh / 2 + (b[1] + b[3] / 2 - sh / 2) * p; }
      s.k = kk;
      // WHY: never pan past the capture's edge, or blank window shows beside the app.
      s.tx = Math.min(0, Math.max(w - sw * kk, w / 2 - fx * kk));
      s.ty = Math.min(0, Math.max(h - sh * kk, h / 2 - fy * kk));
      img.style.transform = `translate(${s.tx}px, ${s.ty}px) scale(${kk})`;
    };
    s.box = (n) => { const b = meta.boxes[n]; return { x: x + s.tx + b[0] * s.k, y: y + s.ty + b[1] * s.k, w: b[2] * s.k, h: b[3] * s.k }; };
    s.view();
    return s;
  }

  /** A real app part (a captured card), centred in its card unless x/y are given. */
  function Part(card, src, { w, x = null, y = null, natural }) {
    const h = (natural[1] / natural[0]) * w;
    const left = x === null ? (card.w - w) / 2 : x, top = y === null ? (card.h - h) / 2 : y;
    const node = el("img", "vs-part", { position: "absolute", left: px(left), top: px(top), width: px(w), borderRadius: px(20 * card.u),
      boxShadow: `0 0 0 ${px(1.5 * card.u)} ${card.theme.edge}`, background: "#fff" }, card.el);
    node.src = `${VS.base}product-ui/${src}`;
    node.alt = "";
    return { el: node, x: left, y: top, w, h };
  }

  /** The lime ring: the frame's one lime element when the imagery is real app UI. */
  function Ring(card, box, { pad = 8, radius = 14 } = {}) {
    const u = card.u;
    const node = el("div", "vs-ring", {
      position: "absolute", left: px(box.x - pad * u), top: px(box.y - pad * u), width: px(box.w + 2 * pad * u), height: px(box.h + 2 * pad * u),
      borderRadius: px(radius * u), border: `${px(4 * u)} solid ${LIME}`, boxShadow: `inset 0 0 0 ${px(1.5 * u)} ${INK}`, opacity: "0",
    }, card.el);
    node.place = (b) => Object.assign(node.style, { left: px(b.x - pad * u), top: px(b.y - pad * u), width: px(b.w + 2 * pad * u), height: px(b.h + 2 * pad * u) });
    return node;
  }

  /** A lime dot that travels a route on a drawing (the trace move). Lives in the drawing's
      SVG (in its floor layer when it has one) so the camera moves it and walls hide it;
      its size stays fixed on screen. */
  function Tracer(d, route) {
    const NS = "http://www.w3.org/2000/svg";
    const pts = route.map((n) => d.anchor(n));
    const trail = document.createElementNS(NS, "polyline");
    trail.classList.add("vs-trail");
    trail.setAttribute("points", pts.map((p) => p.join(",")).join(" "));
    Object.assign(trail.style, { fill: "none", stroke: d.theme.ink, strokeWidth: "2", strokeLinejoin: "round", strokeLinecap: "round", opacity: "0.55" });
    trail.setAttribute("vector-effect", "non-scaling-stroke");
    const dot = document.createElementNS(NS, "circle");
    dot.classList.add("vs-dot");
    dot.setAttribute("fill", LIME); dot.setAttribute("stroke", d.theme.dot); dot.setAttribute("stroke-width", "2");
    dot.setAttribute("vector-effect", "non-scaling-stroke");
    // WHY: the trail and dot sit on the floor, so they go in the drawing's floor layer: every
    // wall and piece of furniture drawn after it hides the part of the walk behind it.
    const host = d.svg.querySelector('[data-layer="floor"]') || d.svg;
    host.appendChild(trail); host.appendChild(dot);
    const total = trail.getTotalLength();
    return {
      trail, dot, total,
      /** Route point at progress p, in drawing units. */
      pointAt(p) { return trail.getPointAtLength(Math.max(0.01, total * p)); },
      at(p, visible = 1) {
        const L = total * p, lenPx = total * d.kk + 2;
        trail.style.strokeDasharray = `${lenPx} ${lenPx}`;
        trail.style.strokeDashoffset = lenPx * (1 - p);
        const q = trail.getPointAtLength(Math.max(0.01, L));
        dot.setAttribute("cx", q.x); dot.setAttribute("cy", q.y);
        dot.setAttribute("r", (12 * d.card.u) / d.kk);
        dot.style.opacity = visible;
        trail.style.opacity = 0.55 * visible;
      },
    };
  }

  /** The scan gradient sweep (verstack.ai): one faint band crossing a card. Rare by rule. */
  function Sweep(card) {
    const band = el("div", "vs-sweep", {
      position: "absolute", top: "0", bottom: "0", left: "-20%", width: "140%", opacity: "var(--sweep)", visibility: "hidden", pointerEvents: "none",
      background: "linear-gradient(90deg, var(--scan-1) 0%, var(--scan-2) 12%, var(--scan-3) 26%, var(--scan-4) 42%, var(--scan-5) 58%, var(--scan-6) 74%, var(--scan-7) 100%)",
      webkitMaskImage: "linear-gradient(90deg, transparent 0%, rgba(0,0,0,.15) 7%, #000 22%, #000 78%, rgba(0,0,0,.15) 93%, transparent 100%)",
      maskImage: "linear-gradient(90deg, transparent 0%, rgba(0,0,0,.15) 7%, #000 22%, #000 78%, rgba(0,0,0,.15) 93%, transparent 100%)",
    }, card.el);
    return {
      el: band,
      at(t, t0, dur = 1.7) {
        const p = VS.engine.prog(t, t0, dur), s = p * p * (3 - 2 * p);
        band.style.transform = `translateX(${-100 + 200 * s}%)`;
        band.style.visibility = p > 0 && p < 1 ? "visible" : "hidden";
      },
    };
  }

  VS.themes = THEMES;
  VS.components = { Frame, Card, Layer, Drawing, Phone, PushScreen, Screen, Part, Ring, Tracer, Sweep };
  VS.layout = layout;
})();
