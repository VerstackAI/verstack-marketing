"""Render motion clips to MP4 (1920 x 1080, 30 fps) or to still frames.

Each clip page exposes renderAt(t) and DURATION. This script steps t frame by
frame in headless Chrome, screenshots each frame, then encodes with ffmpeg.

Run:  python3 motion/render.py                  all clips to motion/out/*.mp4
      python3 motion/render.py capture-walk     one clip
      python3 motion/render.py capture-walk --stills 1 3.5 8   PNG frames only
"""
import pathlib
import shutil
import subprocess
import sys
import tempfile

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "out"
FPS = 30
HOLD = 0.8  # seconds of still end frame so the claim can be read


def render(page, name, stills=None):
    page.goto((ROOT / f"{name}.html").as_uri() + "?render")
    page.wait_for_function("window.READY === true")
    duration = page.evaluate("window.DURATION")
    OUT.mkdir(exist_ok=True)
    if stills:
        for t in stills:
            page.evaluate(f"renderAt({t})")
            page.screenshot(path=str(OUT / f"{name}-t{t}.png"))
        return
    tmp = pathlib.Path(tempfile.mkdtemp(dir="/home/claude"))
    frames = int(round((duration + HOLD) * FPS))
    for i in range(frames):
        page.evaluate(f"renderAt({min(i / FPS, duration)})")
        page.screenshot(path=str(tmp / f"f{i:04d}.png"))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(tmp / "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-preset", "veryfast",
                    "-movflags", "+faststart", str(OUT / f"{name}.mp4")], check=True)
    shutil.rmtree(tmp)
    print(f"{name}.mp4  {frames} frames")


def main():
    args = sys.argv[1:]
    stills = None
    if "--stills" in args:
        i = args.index("--stills")
        stills = [float(x) for x in args[i + 1:]]
        args = args[:i]
    names = args or ["draw-highlight", "explode", "capture-walk", "callouts", "asset-tiles"]
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.on("pageerror", lambda e: print("page error:", e))
        for name in names:
            render(page, name, stills)
        browser.close()


main()
