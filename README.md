# verstack-marketing

Public home for Verstack's marketing files: release graphics, email images, logos and the templates that make them.

**This repo is public.** Email apps and LinkedIn can only show images they can load without a login, so everything here can be seen by anyone. Only put finished, public marketing material here. No customer names, no internal numbers, no drafts that say things that are not live yet.

## Links

GitHub Pages serves this repo at:

```
https://verstackai.github.io/verstack-marketing/<path in this repo>
```

For example, the white lockup for an email header:
`https://verstackai.github.io/verstack-marketing/brand/png/verstack-lockup-white-240x48.png`

## What is where

| Folder | What |
| --- | --- |
| `brand/` | Logos (SVG and PNG), fonts (Inter and IBM Plex Sans, with licences) and `tokens.json` |
| `design-system/` | The rules and canonical names (`RULES.md`, `COMPONENT_INDEX.md`, `DESIGN_SYSTEM.md`, `CHANGELOG.md`, `AGENT_CONTEXT.md`), in the same shape as the app's design systems |
| `product-ui/` | Real app screens and parts captured from the running apps (`capture.py`), with `anchors.json` |
| `illustrations/` | The isometric line drawings (`svg/`, 21 subjects, dark and light), the small engine that draws them (`iso.py`, `build.py`, `scenes_more.py`) and `anchors.json`, the points leader lines attach to |
| `motion/` | Video clips (`out/*.mp4`, 1920 x 1080): five drawing clips and four app clips, the HTML pages they are rendered from, and `render.py`, which turns a page into an MP4 |
| `templates/` | Still layouts: spec sheet and data plate (LinkedIn, 1080 x 1350), annotated drawing (1920 x 1080), email hero (1104 x 552), link preview (1200 x 630), product phone (1080 x 1350), product desktop (1920 x 1080). `gen.py` places drawings, app UI and leader lines |
| `email/` | Source of the Resend template `verstack-product-update`, plus sample values |
| `releases/` | One folder per release, holding its rendered images |
| `scripts/render.sh` | Turns a template into a PNG with headless Chrome |

The design rules live in the **Verstack Marketing** design system on claude.ai. `brand/tokens.json` is a copy of its tokens.

## Making the images for a release

1. Edit the words in `templates/gen.py` (or straight in the HTML for a one-off).
2. Run `python3 templates/gen.py` if you changed `gen.py`.
3. Render each one into the release folder:
   `scripts/render.sh templates/spec-sheet-1080x1350.html releases/2026-11-repeat-repairs/spec-sheet-1080x1350.png`
4. Commit and push. The images are live at the Pages link a minute or two later.

New drawing? Add a function to `illustrations/scenes_more.py`, run `python3 illustrations/build.py`, then `python3 templates/gen.py`.

New clip? Add a function to `motion/gen.py`, run it, then `python3 motion/render.py <clip>`. Check single frames first with `--stills 1.5 4`. Rendering needs Python Playwright and ffmpeg.

`releases/_sample/` shows what each template produces with sample copy taken from verstack.ai.

Unannounced work never goes in this repo. `build.py` and `gen.py` can load extra scenes from a private folder passed on the command line, and write their output there.

## Build

Needs Python 3 with `pip install -r requirements.txt`, then `python3 -m playwright install chromium` (or a local Google Chrome), and ffmpeg for video.

```
python3 illustrations/build.py          # drawings and illustrations/anchors.json
python3 product-ui/capture.py           # app UI (needs the web app in mock mode and the design canvas running; see the file)
python3 templates/gen.py                # still layouts
python3 motion/gen.py                   # clip pages
python3 motion/render.py                # all clips to motion/out/*.mp4
```

Read `design-system/RULES.md` before making anything new.
