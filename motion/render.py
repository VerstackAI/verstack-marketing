"""Render library clips to MP4 (30 fps) or to still frames.

Each clip is defined in design-system/src/clips.js and played by
design-system/player.html, which exposes renderAt(t) and DURATION. This script
steps t frame by frame in headless Chrome and pipes each frame into ffmpeg.

Run:  python3 motion/render.py                         all 50 clips, light and dark -> motion/out/<theme>/<id>.mp4
      python3 motion/render.py draw-dishwasher         one clip (several ids are fine)
      python3 motion/render.py --theme dark            one mode only (light, dark or both)
      python3 motion/render.py --size 1080x1080        square -> motion/out/<theme>/1080x1080/<id>.mp4
      python3 motion/render.py --jobs 4                clips rendered in parallel
      python3 motion/render.py zoom-unit --stills 1 3.5   PNG frames only
"""
import argparse
import asyncio
import os
import pathlib
import shutil

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAYER = (ROOT / "design-system" / "player.html").as_uri()
OUT = ROOT / "motion" / "out"
FPS = 30
sub = ""  # size folder under each theme; empty for 1920 x 1080
# A local Chrome if there is one (set CHROME to choose), else Playwright's own Chromium.
CHROME = os.environ.get("CHROME") or shutil.which("google-chrome") or shutil.which("chromium")


async def render(page, cid, theme, W, H, out, stills):
    await page.goto(f"{PLAYER}?clip={cid}&w={W}&h={H}&theme={theme}&render")
    await page.wait_for_function("window.READY === true", timeout=30000)
    duration = await page.evaluate("window.DURATION")
    if stills:
        for t in stills:
            await page.evaluate(f"renderAt({t})")
            await page.screenshot(path=str(out / f"{cid}-{theme}-t{t}.png"))
        return
    frames = int(round(duration * FPS)) + 1
    ff = await asyncio.create_subprocess_exec(
        "ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png", "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "veryfast", "-movflags", "+faststart",
        str(out / theme / sub / f"{cid}.mp4"), stdin=asyncio.subprocess.PIPE)
    for i in range(frames):
        await page.evaluate(f"renderAt({min(i / FPS, duration)})")
        ff.stdin.write(await page.screenshot(type="png"))
        await ff.stdin.drain()
    ff.stdin.close()
    await ff.wait()
    print(f"{theme}/{cid}.mp4  {duration:.1f}s  {frames} frames", flush=True)


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clips", nargs="*")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--theme", default="both", choices=["light", "dark", "both"])
    ap.add_argument("--stills", nargs="*", type=float)
    a = ap.parse_args()
    W, H = (int(v) for v in a.size.split("x"))
    global sub
    sub = "" if (W, H) == (1920, 1080) else a.size
    themes = ["light", "dark"] if a.theme == "both" else [a.theme]
    out = OUT
    for th in themes:
        (out / th / sub).mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(**({"executable_path": CHROME} if CHROME else {}))
        pages = [await browser.new_page(viewport={"width": W, "height": H}) for _ in range(a.jobs)]
        for pg in pages:
            pg.on("pageerror", lambda e: print("page error:", e))
        await pages[0].goto(PLAYER + "?render")
        await pages[0].wait_for_function("window.READY === true")
        queue = asyncio.Queue()
        for th in themes:
            for cid in a.clips or await pages[0].evaluate("window.CLIPS"):
                queue.put_nowait((cid, th))

        async def worker(pg):
            while not queue.empty():
                cid, th = queue.get_nowait()
                await render(pg, cid, th, W, H, out, a.stills)

        await asyncio.gather(*(worker(pg) for pg in pages))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
