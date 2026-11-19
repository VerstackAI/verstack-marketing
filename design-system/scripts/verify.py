"""Check every library clip against the motion rules, in a real browser.

For each clip in design-system/src/clips.js:
  1. no text: the frame holds no visible text and no SVG <text>;
  2. centred: in every card, the imagery (drawings, phones, screens, parts) is centred
     both ways within 1.5% of the card, measured with the camera at rest;
  3. one lime element at a time: sampled every 0.1 s, at most one of: a drawing with a
     lime part showing, a visible ring, a visible trace dot.
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
  for (let t = 0; t <= window.DURATION + 1e-6; t += 0.1) {
    window.renderAt(t);
    let n = 0;
    frame.querySelectorAll('svg.vs-drawing').forEach((svg) => {
      const lit = [...svg.querySelectorAll('[data-lime]')].some((p) => parseFloat(p.dataset.lime) > 0.5 && parseFloat(p.style.fillOpacity || 1) > 0.5 && op(p.parentElement) > 0.5);
      if (lit) n++;
    });
    frame.querySelectorAll('.vs-ring').forEach((r) => { if (op(r) > 0.5) n++; });
    frame.querySelectorAll('.vs-dot').forEach((d) => { if (parseFloat(d.style.opacity || 0) * op(d.parentElement) > 0.5) n++; });
    if (n > 1) { out.lime.push(`${n} lime at ${t.toFixed(1)}s`); break; }
  }
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
            print(f"{'FAIL' if problems else 'ok  '}  {theme:5} {cid:28} {dur:5.1f}s  {'; '.join(problems)}")
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
