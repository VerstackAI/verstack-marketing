# Agent context: Verstack marketing

Read `RULES.md`, then `COMPONENT_INDEX.md`, before making or changing any graphic or clip.

## What lives where

- `brand/`: logos, fonts (Inter, IBM Plex Sans), `tokens.json` (the token source).
- `design-system/`: the code-based design system. `src/` holds tokens, assets, the engine, components and the clip library; `index.html` is the catalog; `player.html` plays one clip; `scripts/verify.py` checks clips.
- `illustrations/`: the drawing engine and the 21 public drawings. Private scenes load only from a folder passed on the command line.
- `product-ui/`: real app screens and parts with `anchors.json`. Regenerate with `python3 product-ui/capture.py` while the web app (mock mode, port 4670) and the design canvas (port 4680) run from a verstack-mvp checkout.
- `motion/`: `render.py` and the rendered MP4s in `out/`. Clips are defined in `design-system/src/clips.js`, not here.
- `templates/`: still layouts. `python3 templates/gen.py`, then `scripts/render.sh templates/<name>.html <out.png>`.
- `email/`: the release email source.

## Build order

1. `python3 illustrations/build.py` (drawings changed)
2. `python3 product-ui/capture.py` (app changed)
3. `python3 design-system/build.py` (always after 1 or 2, or after editing `brand/tokens.json`)
4. `python3 design-system/scripts/verify.py`
5. `python3 motion/render.py [ids] [--size 1080x1080] [--jobs 2]`

## Before you call it done

1. Watch the clip in `player.html` and look at stills (`motion/render.py <id> --stills 1 3`), not just the code.
2. `verify.py` passes and every item in the RULES.md review checklist holds.
3. Add a line to `CHANGELOG.md`.

## Boundaries

- No text inside clips. Headlines and callouts belong to still layouts only.
- Never edit `product-ui/` images or the generated files in `design-system/src/` by hand.
- Never commit private scenes or planned hardware.
- Nothing here changes the app or its design systems; those live in verstack-mvp and have their own owners.
