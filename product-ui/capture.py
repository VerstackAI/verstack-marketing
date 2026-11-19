"""Capture real Verstack app UI for marketing graphics.

Screens and parts come from the running apps in VerstackAI/verstack-mvp, not from
redrawn copies: the web app in mock mode (desktop) and the design canvas (mobile).
Writes PNGs to product-ui/{desktop,mobile}/{screens,parts}/ and anchors.json, the
boxes (CSS px, relative to each image) that motion and layouts point at.

Start the two apps from a verstack-mvp checkout first:
  cd apps/web && VITE_MOCK_API=true npx vite --port 4670 --host 127.0.0.1
  cd apps/design-canvas && npx vite --port 4680 --host 127.0.0.1
Then run: python3 product-ui/capture.py
Add --mobile-only to re-capture the phone screens and parts and keep the desktop ones.
Mock mode signs in with the app's built-in demo account; no real data is shown.

Phone screens keep the app and the phone shell only: the canvas's home indicator and
shell shadow are hidden before the shot, and everything outside the shell's rounded
corners is made transparent, so no canvas background shows at the corners.
"""
import json
import pathlib
import sys

import os
import shutil

from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright

# A local Chrome if there is one (set CHROME to choose), else Playwright's own Chromium.
CHROME = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")

ARGS = [a for a in sys.argv[1:] if not a.startswith("--")]
MOBILE_ONLY = "--mobile-only" in sys.argv
WEB = ARGS[0] if len(ARGS) > 0 else "http://127.0.0.1:4670"
CANVAS = ARGS[1] if len(ARGS) > 1 else "http://127.0.0.1:4680"
OUT = pathlib.Path(__file__).resolve().parent
for d in ("desktop/screens", "desktop/parts", "mobile/screens", "mobile/parts"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

# Mobile: (canvas area, frame index, file name, {anchor: text inside the frame})
MOBILE_SCREENS = [
    ("field-home", 0, "field-home", {"needs-you": "Needs you", "waiting": "Unit 4B · Maple Court"}),
    ("manager-work", 0, "manager-work", {"water-heater": "Leaking water heater", "decision-tab": "Needs a decision"}),
    ("manager-work-order-read", 0, "work-order", {"quote": "Decide this quote", "title": "Leaking water heater"}),
    ("field-reports", 0, "report", {"status": "Needs review", "to-decide": "To decide"}),
    ("manager-home", 0, "manager-home", {"urgent": "Urgent"}),
    ("inspection-flow", 0, "inspections", {"first": "Unit 4B · Maple Court"}),
]
# Mobile parts: (canvas area, frame index, text inside the part, min width, min height, file name)
MOBILE_PARTS = [
    ("field-reports", 0, "Inspected by", 330, 200, "record-details"),
    ("field-reports", 0, "To decide", 330, 80, "record-summary"),
    ("field-home", 0, "Unit 4B · Maple Court", 330, 150, "waiting-on-you"),
    ("manager-work", 0, "Leaking water heater", 330, 120, "decision-list"),
    ("manager-work-order-read", 0, "Assigned to", 330, 150, "work-order-details"),
]
# Desktop parts: (route, text inside the part, min width, max width, file name)
DESKTOP_PARTS = [
    ("/maintenance", "Kitchen faucet leaking at base", 200, 400, "work-order-card-leak"),
    ("/maintenance", "Replace door closer, entry", 200, 400, "work-order-card-door"),
    ("/maintenance", "Bathroom fan rattles", 200, 400, "work-order-card-parts"),
    ("/home", "Needs your decision", 300, 900, "home-decisions"),
    ("/locations", "King West Residences", 200, 400, "location-card"),
]
# Desktop screens: (route, file name, {anchor: text})
DESKTOP_SCREENS = [
    ("/maintenance", "maintenance-board", {"leak": "Kitchen faucet leaking at base", "new": "New work order"}),
    ("/inspections?layout=reports", "reports", {"blocker": "1 blocker"}),
    ("/locations", "locations", {"first": "King West Residences"}),
]

FIND_FRAMES = """
() => {
  const c = document.querySelector('.react-transform-component');
  c.style.transition = 'none'; c.style.transform = 'translate(0px, 0px) scale(1)';
  const out = [];
  document.querySelectorAll('div').forEach((el) => {
    const cs = getComputedStyle(el); const r = el.getBoundingClientRect();
    if (parseFloat(cs.borderTopLeftRadius) >= 30 && r.width > 300 && r.width < 520 && r.height > r.width * 1.7 && r.height < r.width * 2.4) out.push(el);
  });
  const keep = out.filter((el) => !out.some((o) => o !== el && o.contains(el)));
  keep.forEach((el, i) => el.setAttribute('data-shot', String(i)));
  return keep.length;
}
"""
# WHY: the canvas rail covers the left of the viewport, so each frame is moved clear of it.
SHOW_FRAME = """
(i) => {
  const c = document.querySelector('.react-transform-component');
  const el = document.querySelector(`[data-shot="${i}"]`);
  c.style.transform = 'translate(0px, 0px) scale(1)';
  const r = el.getBoundingClientRect(), cr = c.getBoundingClientRect();
  c.style.transform = `translate(${-(r.x - cr.x) + 500}px, ${-(r.y - cr.y) + 60}px) scale(1)`;
}
"""
# WHY: the home indicator and the shell's drop shadow are canvas chrome, not app UI. The
# indicator is the only absolute bar of its size in the frame (iOS 144 x 5, Android 108 x 4).
CLEAN_FRAME = """
(i) => {
  const el = document.querySelector(`[data-shot="${i}"]`);
  el.style.boxShadow = 'none';
  el.querySelectorAll('div').forEach((d) => {
    const cs = getComputedStyle(d); const r = d.getBoundingClientRect();
    const bar = (Math.round(r.width) === 144 && Math.round(r.height) === 5) || (Math.round(r.width) === 108 && Math.round(r.height) === 4);
    if (bar && cs.position === 'absolute' && cs.pointerEvents === 'none') d.style.display = 'none';
  });
  return parseFloat(getComputedStyle(el).borderTopLeftRadius);
}
"""
BOXES = """
([rootSel, anchors]) => {
  const root = document.querySelector(rootSel); const rr = root.getBoundingClientRect(); const out = {};
  for (const [name, text] of Object.entries(anchors)) {
    const el = [...root.querySelectorAll('*')].find((e) => e.children.length === 0 && e.textContent.trim() === text);
    if (!el) continue;
    let box = el;
    // WHY: point at the row, tile or badge the text belongs to, not the bare text run.
    for (let p = el; p && p !== root; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)' || parseFloat(cs.borderTopWidth) > 0) { box = p; break; }
    }
    const r = box.getBoundingClientRect();
    out[name] = [Math.round(r.x - rr.x), Math.round(r.y - rr.y), Math.round(r.width), Math.round(r.height)];
  }
  return [Math.round(rr.width), Math.round(rr.height), out];
}
"""
PART = """
([rootSel, text, minW, minH, maxW]) => {
  document.querySelectorAll('[data-crop]').forEach((e) => e.removeAttribute('data-crop'));
  const root = document.querySelector(rootSel);
  const el = [...root.querySelectorAll('*')].find((e) => e.children.length === 0 && e.textContent.trim() === text);
  for (let p = el; p && p !== root; p = p.parentElement) {
    const cs = getComputedStyle(p); const r = p.getBoundingClientRect();
    const surface = cs.backgroundColor === 'rgb(255, 255, 255)' || parseFloat(cs.borderTopWidth) > 0;
    if (surface && r.width >= minW && r.height >= minH && r.width <= maxW) { p.setAttribute('data-crop', '1'); return true; }
  }
  return false;
}
"""


def clip_to_shell(path, radius):
    """Make everything outside the phone shell's rounded rectangle transparent.

    Args:
        path: The captured screen PNG; the image is exactly the shell's bounding box.
        radius: The shell's corner radius in image pixels.
    """
    shot = Image.open(path).convert("RGBA")
    w, h = shot.size
    # WHY: drawn at 4x and scaled down so the corner edge is anti-aliased, not stepped.
    big = Image.new("L", (w * 4, h * 4), 0)
    ImageDraw.Draw(big).rounded_rectangle([0, 0, w * 4 - 1, h * 4 - 1], radius=radius * 4, fill=255)
    shell_mask = big.resize((w, h), Image.LANCZOS)
    shot.putalpha(shell_mask)
    shot.save(path)


def main():
    anchors = {"mobile": {}, "desktop": {}}
    if MOBILE_ONLY:
        anchors["desktop"] = json.loads((OUT / "anchors.json").read_text())["desktop"]
    with sync_playwright() as p:
        browser = p.chromium.launch(**({"executable_path": CHROME} if CHROME else {}))
        mob = browser.new_context(viewport={"width": 1000, "height": 1040}, device_scale_factor=3).new_page()
        for area, i, name, boxes in MOBILE_SCREENS:
            mob.goto(f"{CANVAS}/?area={area}", wait_until="load", timeout=90000)
            mob.wait_for_timeout(3500)
            mob.evaluate(FIND_FRAMES)
            mob.evaluate(SHOW_FRAME, i)
            shell_radius = mob.evaluate(CLEAN_FRAME, i)
            mob.wait_for_timeout(300)
            w, h, b = mob.evaluate(BOXES, [f'[data-shot="{i}"]', boxes])
            shot_path = OUT / "mobile/screens" / f"{name}.png"
            mob.locator(f'[data-shot="{i}"]').screenshot(path=str(shot_path), omit_background=True)
            clip_to_shell(shot_path, shell_radius * 3)
            anchors["mobile"][name] = {"size": [w, h], "scale": 3, "boxes": b}
        for area, i, text, mw, mh, name in MOBILE_PARTS:
            mob.goto(f"{CANVAS}/?area={area}", wait_until="load", timeout=90000)
            mob.wait_for_timeout(3500)
            mob.evaluate(FIND_FRAMES)
            mob.evaluate(SHOW_FRAME, i)
            mob.wait_for_timeout(300)
            if mob.evaluate(PART, [f'[data-shot="{i}"]', text, mw, mh, 10000]):
                mob.locator('[data-crop="1"]').first.screenshot(path=str(OUT / "mobile/parts" / f"{name}.png"))

        if MOBILE_ONLY:
            browser.close()
            (OUT / "anchors.json").write_text(json.dumps(anchors, indent=1))
            print("captured the mobile screens and parts")
            return
        web = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2).new_page()
        web.goto(WEB + "/home", wait_until="load", timeout=90000)
        web.wait_for_timeout(5000)
        for route, name, boxes in DESKTOP_SCREENS:
            web.goto(WEB + route, wait_until="load", timeout=60000)
            web.wait_for_timeout(4000)
            w, h, b = web.evaluate(BOXES, ["body", boxes])
            web.screenshot(path=str(OUT / "desktop/screens" / f"{name}.png"))
            anchors["desktop"][name] = {"size": [1440, 900], "scale": 2, "boxes": {**b, **FIXED_BOXES.get(name, {})}}
        # WHY: parts are shown large on their own, so they are captured at 3x; screens at 2x.
        part = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=3).new_page()
        part.goto(WEB + "/home", wait_until="load", timeout=90000)
        part.wait_for_timeout(5000)
        for route, text, mn, mx, name in DESKTOP_PARTS:
            part.goto(WEB + route, wait_until="load", timeout=60000)
            part.wait_for_timeout(4000)
            if part.evaluate(PART, ["body", text, mn, 60, mx]):
                part.locator('[data-crop="1"]').first.screenshot(path=str(OUT / "desktop/parts" / f"{name}.png"))
        browser.close()
    (OUT / "anchors.json").write_text(json.dumps(anchors, indent=1))
    print("captured", sum(1 for _ in OUT.rglob("*.png")), "images")


main()
