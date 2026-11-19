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

/* The scan gradient from verstack.ai: white to lime. It only ever appears while moving. */
const SCAN = "#f8fafc 0%, #eefbd7 12%, #d8f7a3 26%, #baf85d 42%, #a5fc22 58%, #8ff741 74%, #7ff553 100%";

/** Sweep: a feathered band of the scan gradient crossing a card left to right
    (the site's closing tile). el is a .sweep div inside a .sweep-clip overlay. */
function sweep(el, t, t0, dur = 1.6) {
  const p = prog(t, t0, dur);
  const x = -100 + 200 * (p * p * (3 - 2 * p));
  el.style.transform = `translateX(${x}%)`;
  el.style.visibility = p > 0 && p < 1 ? "visible" : "hidden";
}

/** Scan: a tile fades to the scan gradient and back (the site's hero tiles, pv-scan). */
function scanAt(el, t, t0, dur = 1.3, peak = 1) {
  const p = prog(t, t0, dur);
  let o = 0;
  if (p > 0 && p < 0.16) o = p / 0.16;
  else if (p >= 0.16 && p <= 0.6) o = 1;
  else if (p > 0.6 && p < 1) o = 1 - (p - 0.6) / 0.4;
  el.style.opacity = peak * (o * o * (3 - 2 * o));
}

/** Fit: the largest font size (step 2px) at which the text keeps every word inside its
    box width and stays within maxH. Headlines fill their column instead of floating in it. */
function fitText(el, maxPx, minPx, maxH) {
  for (let px = maxPx; px >= minPx; px -= 2) {
    el.style.fontSize = px + "px";
    if (el.scrollWidth <= el.clientWidth + 1 && el.scrollHeight <= maxH) return px;
  }
  return minPx;
}

/** Put element id just under ref (after ref has been fitted). */
function below(id, ref, gap) {
  const r = document.getElementById(ref);
  document.getElementById(id).style.top = (r.offsetTop + r.scrollHeight + gap) + "px";
}

/** Sit element id with its bottom gap px above y. */
function above(id, y, gap) {
  const el = document.getElementById(id);
  el.style.top = (y - gap - el.scrollHeight) + "px";
}

/** Draw a leader polyline from its first point. */
function leaderAt(el, t, t0, dur = 0.24) {
  if (!el._len) { el._len = el.getTotalLength() + 2; el.style.strokeDasharray = `${el._len} ${el._len}`; }
  el.style.strokeDashoffset = el._len * (1 - ease(prog(t, t0, dur)));
}
