"""Check every library clip against the motion rules, in a real browser.

For each clip in design-system/src/clips.js:
  1. no text: the frame holds no visible text and no SVG <text>;
  2. centred: in every card, the imagery (drawings, phones, screens, parts) is centred
     both ways within 1.5% of the card, measured with the camera at rest;
  3. one lime element at a time: sampled every 0.1 s, at most one of: a drawing with a
     lime part showing, a visible ring, a visible trace dot;
  4. a little lime: a lit part covers at most 20% of its drawing (area against the
     drawing's outline).
Each clip is checked in the light and the dark theme.
Prints one line per clip and exits 1 if any clip fails.

Run: python3 design-system/scripts/verify.py [clip-id ...] [--theme light|dark|both]
"""
import asyncio
import pathlib
import sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
PLAYER = (ROOT / "design-system" / "player.html").as_uri()

CHECK = """
async (restAt) => {
  const frame = document.querySelector('.vs-frame');
  const out = { text: [], centre: [], lime: [] };
  // 1. text
  const txt = frame.innerText.replace(/\\s+/g, '');
  if (txt) out.text.push(txt.slice(0, 40));
  if (frame.querySelector('text')) out.text.push('<text> element');
  // 2. centring, with the camera at rest
  window.renderAt(restAt);
  frame.querySelectorAll('.vs-card').forEach((card, ci) => {
    const cw = card.clientWidth, ch = card.clientHeight;
    let x0 = Infinity, y0 = Infinity, x1 = -Infinity, y1 = -Infinity;
    const add = (x, y, w, h) => { x0 = Math.min(x0, x); y0 = Math.min(y0, y); x1 = Math.max(x1, x + w); y1 = Math.max(y1, y + h); };
    card.querySelectorAll('svg.vs-drawing').forEach((svg) => {
      const vb = svg.viewBox.baseVal, k = cw / vb.width;
      let bx0 = Infinity, by0 = Infinity, bx1 = -Infinity, by1 = -Infinity;
      svg.querySelectorAll('polygon, polyline:not(.vs-trail), line, path, ellipse, circle:not(.vs-dot)').forEach((e) => {
        const b = e.getBBox(); bx0 = Math.min(bx0, b.x); by0 = Math.min(by0, b.y); bx1 = Math.max(bx1, b.x + b.width); by1 = Math.max(by1, b.y + b.height);
      });
      add((bx0 - vb.x) * k, (by0 - vb.y) * k, (bx1 - bx0) * k, (by1 - by0) * k);
    });
    card.querySelectorAll('.vs-phone, .vs-screen, .vs-part').forEach((e) => add(e.offsetLeft, e.offsetTop, e.offsetWidth, e.offsetHeight));
    if (x0 === Infinity) return;
    const dx = ((x0 + x1) / 2 - cw / 2) / cw, dy = ((y0 + y1) / 2 - ch / 2) / ch;
    if (Math.abs(dx) > 0.015 || Math.abs(dy) > 0.015) out.centre.push(`card ${ci}: off by ${(dx * 100).toFixed(1)}% x, ${(dy * 100).toFixed(1)}% y`);
  });
  // 3. one lime element at a time
  const op = (e) => { let o = 1; for (let n = e; n && n !== frame; n = n.parentElement) o *= parseFloat(getComputedStyle(n).opacity); return o; };
  // 4. lime share: area of the lit shapes against the area inside the drawing's outline
  const pts = (e) => {
    if (e.points && e.points.numberOfItems) return [...Array(e.points.numberOfItems)].map((_, i) => [e.points.getItem(i).x, e.points.getItem(i).y]);
    if (e.tagName === 'line') return [[e.x1.baseVal.value, e.y1.baseVal.value], [e.x2.baseVal.value, e.y2.baseVal.value]];
    const b = e.getBBox(); return [[b.x, b.y], [b.x + b.width, b.y], [b.x + b.width, b.y + b.height], [b.x, b.y + b.height]];
  };
  const area = (p) => Math.abs(p.reduce((s, [x, y], i) => { const [x2, y2] = p[(i + 1) % p.length]; return s + x * y2 - x2 * y; }, 0)) / 2;
  const hull = (p) => {
    p = p.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cross = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const q of p) { while (lo.length > 1 && cross(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (const q of p.reverse()) { while (up.length > 1 && cross(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  };
  const shapeArea = (e) => (e.points && e.points.numberOfItems > 2 ? area(pts(e)) : (() => { const b = e.getBBox(); return b.width * b.height * Math.PI / 4; })());
  const share = new Map();
  for (let t = 0; t <= window.DURATION + 1e-6; t += 0.1) {
    window.renderAt(t);
    let n = 0;
    frame.querySelectorAll('svg.vs-drawing').forEach((svg) => {
      const lit = [...svg.querySelectorAll('[data-lime]')].some((p) => parseFloat(p.dataset.lime) > 0.5 && parseFloat(p.style.fillOpacity || 1) > 0.5 && op(p.parentElement) > 0.5);
      if (lit) n++;
      const full = [...svg.querySelectorAll('[data-lime]')].filter((p) => parseFloat(p.dataset.lime) > 0.99);
      if (full.length && !share.has(svg)) {
        const all = [...svg.querySelectorAll('polygon, polyline:not(.vs-trail), line, path, ellipse, circle:not(.vs-dot)')].flatMap(pts);
        share.set(svg, full.reduce((s, e) => s + shapeArea(e), 0) / area(hull(all)));
      }
    });
    frame.querySelectorAll('.vs-ring').forEach((r) => { if (op(r) > 0.5) n++; });
    frame.querySelectorAll('.vs-dot').forEach((d) => { if (parseFloat(d.style.opacity || 0) * op(d.parentElement) > 0.5) n++; });
    if (n > 1) { out.lime.push(`${n} lime at ${t.toFixed(1)}s`); break; }
  }
  share.forEach((r) => { if (r > 0.2) out.lime.push(`lime part is ${Math.round(r * 100)}% of its drawing`); });
  out.share = Math.max(0, ...share.values());
  return out;
}
"""


async def main(ids, themes):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1920, "height": 1080})
        await page.goto(PLAYER + "?render")
        await page.wait_for_function("window.READY === true")
        ids = ids or await page.evaluate("window.CLIPS")
        failed = 0
        runs = [(cid, th) for th in themes for cid in ids]
        for cid, theme in runs:
            await page.goto(PLAYER + f"?clip={cid}&theme={theme}&render")
            await page.wait_for_function("window.READY === true", timeout=20000)
            dur = await page.evaluate("window.DURATION")
            # WHY: a clip that starts zoomed in is checked where its camera comes to rest, at the end.
            rest = dur if cid.startswith("zoom-out") else 0
            r = await page.evaluate(CHECK, rest)
            problems = [f"text {r['text']}"] * bool(r["text"]) + r["centre"] + r["lime"]
            failed += bool(problems)
            print(f"{'FAIL' if problems else 'ok  '}  {theme:5} {cid:28} {dur:5.1f}s  lime {r['share'] * 100:4.1f}%  {'; '.join(problems)}")
        await browser.close()
        print(f"\n{len(runs) - failed}/{len(runs)} clip renders pass ({', '.join(themes)})")
        return failed


if __name__ == "__main__":
    args = sys.argv[1:]
    themes = ["light", "dark"]
    if "--theme" in args:
        i = args.index("--theme")
        themes = ["light", "dark"] if args[i + 1] == "both" else [args[i + 1]]
        del args[i:i + 2]
    sys.exit(1 if asyncio.run(main(args, themes)) else 0)
