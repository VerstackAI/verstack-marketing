# Changelog

## 2026-11-19, layering

- The walk trail and its dot now sit in the unit plan's floor layer, so walls and furniture in front of them hide them. The rug and door swing moved below that layer.
- The ladder is rebuilt as solids: rails are bars with thickness, steps run into the rails, parts drawn far to near so the right rail hides the step ends and the back legs sit behind.
- New rule: nothing shows through a solid. 18 affected clips re-rendered; all pass.

## 2026-11-19, toned drawings, smaller lime parts

- Drawings are now toned like the phone on verstack.ai: flat fills by the way each face turns (top lightest, left light grey, right darker, curved sides between) and a dark accent for glass and displays. New `tone-*` tokens with light and dark values; every element carries its role so clips recolour it for the mode.
- Lime parts are now small: a display, a burner ring, a dispenser, a filter slot, a trackpad. `verify.py` fails any lime part over 20% of its drawing; the largest in the library is 9.7%.
- Still samples and all 100 clips re-rendered.

## 2026-11-19, light and dark modes, website line weights

- Every clip now has a light and a dark mode (`VS.mount(..., { theme })`, `player.html?theme=dark`, a Mode switch in the catalog). Dark mode: `card-dark` (#141416) cards with a faint edge on the dark ground, mist lines; the lime part's outline and the lines drawn on it turn dark as it lights. 100 MP4s: `motion/out/light/` and `motion/out/dark/`.
- Line weights now follow the isometric phone on verstack.ai: proportional to the drawing's size, with each solid's outer contour about 1.6 times the lines inside it. The uniform 1.25 px hairline is retired.
- Appliance boxes have softly rounded vertical corners (no crease line). Buildings, plans, ladder and paint stay square.
- The phone drawing is now the website's own isometric phone (`illustrations/sources/phone-site.svg`), with the capture record button as its lime part.
- Lime parts are now the smallest shape under the anchor (the door panel, the oven window, the washer glass, the smoke detector sensor), not the whole face.
- `verify.py` checks both modes: 100 of 100 pass.

## 2026-11-19, motion library as code

- The design system is now code: tokens (`src/tokens.css`, `src/tokens.js`, generated from `brand/tokens.json`), components (`src/components.js`), moves (`src/engine.js`) and the clip library (`src/clips.js`), with a live catalog (`index.html`) and a player (`player.html`).
- Clips are imagery only. Headlines, supporting lines, callouts, the lockup and app parts were taken out of every clip; the imagery is centred in its card. Words go on in the edit or the post.
- Motion library grown from 9 clips to 50 in seven families: Draw, Explode, Zoom, Trace, Swap, Tiles and App. The drawing moves from the first clips (draw, highlight, explode, trace, tiles) are all kept.
- New moves: Assemble, Zoom (drawing camera with fixed 1.25 px hairlines), camera-follow Trace, Swap, lime walking across tiles, desktop screen zoom that never shows past the capture's edge, a screen push with a still status bar.
- Every object drawing has a lime part chosen by anchor (dishwasher door, fridge freezer drawer, water heater rating plate and so on).
- `scripts/verify.py` checks every clip: no text, imagery centred, one lime element at a time. All 50 pass.
- `motion/render.py` renders from the player, at any size (`--size 1080x1080`) and in parallel (`--jobs`). Old per-clip pages and `motion/gen.py` removed.
- Reports screen ring now lands on the first report row (the old "1 blocker" box was empty).
- Added the `frame` token group (seam, card radius, fill, ring, sweep); removed the retired node-size token.

## 2026-11-19, app UI

- Added app UI to marketing graphics. `product-ui/capture.py` captures real screens and parts from the web app in mock mode and the mobile design canvas, with `product-ui/anchors.json` for rings and callouts.
- Added Phone Shot, Board Shot, App Part, Ring and Screen Push.
- Added four app clips: app-decide, app-field-home, app-board, app-report.
- Added two still layouts: Product Phone (1080 x 1350) and Product Desktop (1920 x 1080).
- Draw-highlight and explode now carry a real App Part under the headline; the lockup moved onto the Light Card. No empty Type Column.
- Added RULES.md, COMPONENT_INDEX.md, DESIGN_SYSTEM.md and AGENT_CONTEXT.md in the same shape as the app's design systems.

## 2026-11-18

- Sparse and bold: removed index numbers, section keys, square nodes, the drafting grid and IBM Plex Mono. Nothing under 28 px. Headlines fitted to their column. Two callouts at most.
- Gradient sweep limited to one per video at 14%.
- Light Cards on the dark ground for every frame.
- Library grown to 21 drawings; five drawing clips added.

## 2026-11-17

- Rebuilt around isometric line drawings; scan-tile graphics retired.

## 2026-11-16

- First version: brand files, release templates, release email.
