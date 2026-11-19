/* Verstack motion engine: timing maths and the moves.
   Data flow: a clip's build() makes components (components.js), then returns
   render(t). Every move here is a pure function of t, so the renderer can step
   frame by frame and the catalog can play the same clip live. */
window.VS = window.VS || {};

(() => {
  const bezier = (x1, y1, x2, y2) => (t) => {
    let u = t;
    for (let i = 0; i < 10; i++) {
      const x = 3 * (1 - u) * (1 - u) * u * x1 + 3 * (1 - u) * u * u * x2 + u * u * u - t;
      const dx = 3 * (1 - u) * (1 - u) * x1 + 6 * (1 - u) * u * (x2 - x1) + 3 * u * u * (1 - x2);
      if (Math.abs(dx) < 1e-6) break;
      u = Math.min(1, Math.max(0, u - x / dx));
    }
    return 3 * (1 - u) * (1 - u) * u * y1 + 3 * (1 - u) * u * u * y2 + u * u * u;
  };
  const ease = bezier(0.2, 0, 0, 1); // ease-standard, shared with the app
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const prog = (t, t0, dur) => (dur <= 0 ? (t >= t0 ? 1 : 0) : clamp((t - t0) / dur));
  const lerp = (a, b, p) => a + (b - a) * p;
  const smooth = (x) => x * x * (3 - 2 * x);
  const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
  const mix = (a, b, p) => {
    const A = hex(a), B = hex(b);
    return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * p)).join(",")})`;
  };
  /** 0 before t0, 1 between in and out, back to 0 after out; eased both ways. */
  const window_ = (t, t0, t1, dur) => ease(prog(t, t0, dur)) * (1 - ease(prog(t, t1, dur)));

  /** Draw outlines on in order over [t0, t0 + span]; each outline takes dur.
      Faces fill as they close. The lime part fills over 0.48 s from highlightAt
      and clears again from clearAt. */
  function draw(d, t, t0, span, dur, highlightAt = Infinity, clearAt = Infinity) {
    const n = d.items.length;
    d.items.forEach((it, i) => {
      const s = t0 + (n > 1 ? i / (n - 1) : 0) * span;
      const p = ease(prog(t, s, dur));
      // WHY: a finished outline drops its dash, so a later camera zoom cannot open gaps in it.
      if (p >= 1) { it.el.style.strokeDasharray = "none"; it.el.style.strokeDashoffset = 0; }
      else { it.el.style.strokeDasharray = `${it.len} ${it.len}`; it.el.style.strokeDashoffset = it.len * (1 - p); }
      if (it.fill !== "none") it.el.style.fillOpacity = prog(t, s + dur * 0.55, dur * 0.45);
    });
    lime(d, t, highlightAt, clearAt);
  }

  /** Fill the drawing's lime part (if any) from ground to lime at t0, back at t1. */
  function lime(d, t, t0 = Infinity, t1 = Infinity) {
    const h = ease(prog(t, t0, 0.48)) * (1 - ease(prog(t, t1, 0.4)));
    d.limeItems.forEach((it) => {
      it.el.style.fill = mix(it.groundFill, it.limeFill, h);
      // Dark mode: the lit part's outline turns dark so the lime keeps its edge.
      if (d.theme.limeStroke) {
        if (it.stroke && it.stroke[0] === "#") it.el.style.stroke = mix(it.stroke, d.theme.limeStroke, h);
        it.over.forEach((o) => { o.el.style.stroke = mix(o.stroke, d.theme.limeStroke, h); });
      }
      it.el.dataset.lime = h.toFixed(3);
    });
  }

  /** Show a drawing complete, no draw-on (for clips that start mid-story). */
  function shown(d) {
    d.items.forEach((it) => { it.el.style.strokeDasharray = "none"; it.el.style.fillOpacity = 1; });
  }

  /** Fade and rise an element in (the enter move: 16px at 1080p, 0.48 s). */
  function rise(el, t, t0, dur = 0.48, dist = 16) {
    const p = ease(prog(t, t0, dur));
    el.style.opacity = p;
    el.style.transform = `translateY(${(1 - p) * dist}px)`;
  }

  /** Fade an element out over dur from t0 (keeps any transform). */
  function fadeOut(el, t, t0, dur = 0.4) {
    el.style.opacity = Math.min(parseFloat(el.style.opacity || 1), 1 - ease(prog(t, t0, dur)));
  }

  /** Camera on a drawing: from its centred view to scale s around anchor point (user units). */
  function zoom(d, t, t0, dur, s, focus, back = Infinity) {
    const p = ease(prog(t, t0, dur)) * (1 - ease(prog(t, back, dur)));
    d.camera(lerp(1, s, p), focus, p);
  }

  /** The lime ring around one real app element: lands at t0, holds, leaves at t1. */
  function ring(el, t, t0, t1 = Infinity) {
    const p = ease(prog(t, t0, 0.36));
    const q = ease(prog(t, t1, 0.3));
    el.style.opacity = p * (1 - q);
    el.style.transform = `scale(${lerp(1.06, 1, p)})`;
  }

  VS.engine = { bezier, ease, clamp, prog, lerp, smooth, mix, window: window_ };
  VS.moves = { draw, lime, shown, rise, fadeOut, zoom, ring };
})();
