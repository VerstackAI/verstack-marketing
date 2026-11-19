/* Verstack motion helpers. Every clip exposes renderAt(t): the frame at t seconds.
   Pure function of t, so a renderer can step frame by frame and a browser can play it live. */

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
const ease = bezier(0.2, 0, 0, 1); // ease-standard
const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
const prog = (t, t0, dur) => clamp((t - t0) / dur);
const hex = (h) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
const mix = (a, b, p) => { const A = hex(a), B = hex(b); return `rgb(${A.map((v, i) => Math.round(v + (B[i] - v) * p)).join(",")})`; };
const LIME = /#a5fc22|#7ff553|#8ff741/i;

/** Prepare every outline in an inline SVG to be drawn on. */
function prepDraw(svg) {
  const k = svg.getBoundingClientRect().width / svg.viewBox.baseVal.width;
  const els = [...svg.querySelectorAll("polygon,polyline,line")];
  // The lime part's outlines use the ground colour. Until the highlight lands they must
  // read as normal outlines, or the part shows up as a hole in the drawing.
  const counts = {};
  els.forEach((el) => { const s = el.getAttribute("stroke"); counts[s] = (counts[s] || 0) + 1; });
  const normal = Object.keys(counts).sort((a, b) => counts[b] - counts[a])[0];
  const limeEl = els.find((el) => LIME.test(el.getAttribute("fill") || ""));
  const hiStroke = limeEl ? limeEl.getAttribute("stroke") : null;
  return els.map((el) => {
    const len = el.getTotalLength() * k + 2;
    el.style.strokeDasharray = `${len} ${len}`;
    const fill = el.getAttribute("fill") || "none";
    const stroke = el.getAttribute("stroke");
    return { el, len, fill, lime: LIME.test(fill), hi: hiStroke && stroke === hiStroke, stroke, normal };
  });
}

/** Draw outlines on in order over [t0, t0 + span], each taking dur. Faces fill as they close.
    Lime faces stay ground-coloured until highlightAt, then fill lime over 0.48 s. */
function drawAt(items, t, t0, span, dur, ground, highlightAt = Infinity) {
  const n = items.length;
  items.forEach((it, i) => {
    const s = t0 + (n > 1 ? i / (n - 1) : 0) * span;
    const p = ease(prog(t, s, dur));
    it.el.style.strokeDashoffset = it.len * (1 - p);
    if (it.fill !== "none") it.el.style.fillOpacity = prog(t, s + dur * 0.55, dur * 0.45);
    const h = ease(prog(t, highlightAt, 0.48));
    if (it.lime) it.el.style.fill = mix(ground, it.fill, h);
    if (it.hi) it.el.style.stroke = mix(it.normal, it.stroke, h);
  });
}

/** Fade and rise an element (enter move). */
function enter(el, t, t0, dur = 0.48, rise = 16) {
  const p = ease(prog(t, t0, dur));
  el.style.opacity = p;
  el.style.transform = `translateY(${(1 - p) * rise}px)`;
}

/** Draw a leader polyline from its first point. */
function leaderAt(el, t, t0, dur = 0.24) {
  if (!el._len) { el._len = el.getTotalLength() + 2; el.style.strokeDasharray = `${el._len} ${el._len}`; }
  el.style.strokeDashoffset = el._len * (1 - ease(prog(t, t0, dur)));
}
