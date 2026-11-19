# Agent context: Verstack marketing

Read `RULES.md`, then `COMPONENT_INDEX.md`, before making or changing any graphic or clip.

## What lives where

- `brand/`: logos, fonts (Inter, IBM Plex Sans), `tokens.json`.
- `illustrations/`: the drawing engine and the 21 public drawings. Private scenes load only from a folder passed on the command line.
- `templates/`: still layouts. `python3 templates/gen.py`, then `scripts/render.sh templates/<name>.html <out.png>`.
- `motion/`: clips. `python3 motion/gen.py`, then `python3 motion/render.py [clip] [--stills t ...]`.
- `product-ui/`: real app screens and parts with `anchors.json`. Regenerate with `python3 product-ui/capture.py` while the web app (mock mode, port 4670) and the design canvas (port 4680) run from a verstack-mvp checkout.
- `email/`: the release email source.

## Before you call it done

1. Render it and look at the frames (`--stills`), not just the code.
2. Check every item in the RULES.md review checklist.
3. Add a line to `CHANGELOG.md`.

## Boundaries

- Never edit `product-ui/` images by hand; re-capture.
- Never commit private scenes or planned hardware.
- Nothing here changes the app or its design systems; those live in verstack-mvp and have their own owners.
