# Verstack marketing design system

## Purpose

The look of everything Verstack puts in front of the market: release emails, LinkedIn posts, release videos and explainer graphics. It sits beside the app's design systems in `VerstackAI/verstack-mvp/apps/design-system` (desktop and mobile) and shows the app exactly as it is.

Two kinds of picture carry the story:

- **Line drawings** of the real things maintenance happens to (buildings, units, appliances), with one lime part.
- **The real app**: phone screens, the board and its cards, captured from the running apps.

## Principles

**Cards on the dark, in two modes.** Every frame is cards on the dark ground, like verstack.ai. Light mode: mist cards, ink lines. Dark mode: dark scene cards, light lines, the way the site shows dark product scenes.

**Clips are pictures.** A motion clip is imagery only, centred in its card: a drawing drawing itself, a building opening, a phone screen changing. The words go on in the video edit or in the post, never inside the clip.

**Sparse and bold in stills.** A big headline, one picture, two callouts at most. Nothing under 28 px. Headlines fill their column; never an empty band under them.

**One lime thing.** The lime part of a drawing, the trace dot, or a ring around one app element, one at a time. The scan gradient is rare: one faint sweep.

**The app as it is.** App UI is captured, not drawn. It keeps the app's names, tokens and wording.

**Code is the source.** Tokens, components and every clip are code in `design-system/src`, rendered live in the catalog and checked by `scripts/verify.py`.

## Foundations

### Colour

| Token | Value | Use |
|---|---|---|
| `ground-900` | `#171a19` | Frame background |
| `mist` | `#f8fafc` | Light Card; white text on the ground |
| `fg-muted` | `#c2c4c5` | Supporting line on the dark |
| `ink-700` | `#30303a` | Drawing lines and callouts on a Light Card |
| `ink-500` | `#6d6d78` | The line under a callout name on a Light Card |
| `lime-electric` | `#a5fc22` | The one lime element |
| `card-dark` | `#141416` | Dark mode card (the website's scene-dark) |
| `tone-top` / `tone-left` / `tone-right` / `tone-side` / `tone-accent` | light `#ffffff` `#ecebe7` `#d6d5d0` `#e1e0dc` `#3f3e3e`; dark `#2d3130` `#232726` `#1a1d1c` `#1e2120` `#0b0c0c` | Face tones of drawings |
| `scan-1`…`scan-7` | `#f8fafc` → `#7ff553` | The gradient sweep only |

Full values are in `brand/tokens.json`. The app's own semantic tokens (slate structure, status colours) stay inside the app UI images.

### Type

Inter throughout marketing frames. IBM Plex Sans appears only inside app UI, because it is the app's face.

| Role | Size (1920 x 1080 / 1080 x 1350) | Weight |
|---|---|---|
| Headline | fitted, usually 100–170 px | 400, tracking -0.05em |
| Plate title | 230 px | 400 |
| Callout name | 40 px | 600 |
| Callout line, supporting line | 28–34 px | 400 |
| Status Word, URL | 28–32 px | 500 |

### Space and shape

- 16 px of ground around and between cards (the `seam` token). Cards 40 px radius at 1080p.
- Clips: one card filling the frame, or a row or grid of cards (`VS.layout`). Imagery fills 68% of its card's height (at most 80% of its width) and sits dead centre; phones fill 86%.
- Clips scale with the frame's short side, so the same clip renders at 1920 x 1080, 1080 x 1080 or 1080 x 1350.
- Stills at 1920 x 1080: Light Card 1110 x 1048 at left, headline column 600 px at right. At 1080 x 1350: Light Card across the top, headline below on the dark.
- Flat. No shadows.

## Drawings

Isometric, faces filled with the surface they sit on, built by `illustrations/build.py` so every line matches. 21 public drawings, dark and light. One Lime Part per drawing that has a subject: a small piece, at most 20% of the drawing (a display, a burner ring, a dispenser, a filter slot).

- **Line weight** follows the isometric phone on verstack.ai (0.5 contour, 0.3 inside on a 198-unit drawing): proportional to the drawing's size on screen, with each solid's outer contour about 1.6 times the weight of the lines inside it. In clips the weight is set from the drawing's size: 0.3% of its longer side, 1.7 to 2.8 px at 1080p.
- **Tones**: faces are filled with flat tones like the phone on verstack.ai, by which way they face: top (`tone-top`, lightest), turned left (`tone-left`), turned right (`tone-right`, darker), curved sides (`tone-side`), and a dark `tone-accent` for glass and displays (oven window, washer glass, laptop bezel, thermostat display, fridge dispenser, dishwasher display, smoke detector sensor). Light and dark mode each have their own values. No gradients, no shading beyond the face tones.
- **Layering**: drawings are opaque solids drawn far to near, so nearer parts hide farther ones. Parts with thickness are solids (ladder rails are bars with a front, a side and a top). Anything on a floor goes in the drawing's floor layer (`d.layer("floor")` in `iso.py`); the walk trail and its dot are placed there, so walls and furniture in front of them hide them.
- **Rounding**: appliance boxes have softly rounded vertical corners (0.22 units on a 6-unit appliance), with no crease line where the corner turns. Buildings, plans, ladders and paint stay square.
- **The phone** is the website's own isometric phone (`illustrations/sources/phone-site.svg`, from `public/media/phones/iphone-outline.svg` on the site), with its silver, rim and bezel tones, plus the capture record button as its lime part.
- **Modes**: every element of a drawing carries its role (`data-f` for its fill tone, `data-s` for its stroke). Clips recolour by role for the mode; the website phone's own colours are mapped by value.

## App UI

`product-ui/capture.py` captures the running apps from a verstack-mvp checkout:

- **Desktop**: the web app in mock mode (`VITE_MOCK_API=true`), signed in with its built-in demo account. Screens at 2x, parts at 3x.
- **Mobile**: the design canvas, each screen in its device shell at 3x.

It writes `product-ui/anchors.json` with the boxes of named elements so a Ring can land on them. Re-run it when the app changes; never edit the images.

In clips, use a Phone or Screen centred on the Light Card and a Ring around the one element the story is about. In stills, an app part can also sit under the headline. Name what you show with the app's canonical names (see `COMPONENT_INDEX.md`).

Design-canvas screens show designs; some features are not live. Check status before posting.

## Motion

The library is 50 clips in seven families: Draw (20), Explode (3), Zoom (4), Trace (3), Swap (6), Tiles (6) and App (8). Each is a short definition in `src/clips.js` built from the components in `src/components.js` and the moves in `src/engine.js`.

- Moves: Draw, Highlight, Explode, Assemble, Zoom, Trace, Swap, Rise, Push, Ring In. Ease `cubic-bezier(0.2, 0, 0, 1)`; no bounce.
- Timing: a drawing draws on in 0.8–2.2 s depending on how many outlines it has; the lime part fills in 0.48 s; app UI rises 40 px in 0.7 s; every clip holds its last frame about 1.5 s.
- Every clip exposes `renderAt(t)`. `player.html` plays one; `motion/render.py` steps it at 30 fps into an MP4; the catalog loops all of them.
- `scripts/verify.py` checks every clip in a real browser, in both modes: no text, imagery centred in every card, one lime element at a time.
- Every clip renders in two modes: `motion/out/light/<id>.mp4` and `motion/out/dark/<id>.mp4`.

## Voice

Headlines are claims in sentence case with a full stop. Sequence before benefit: who does what, what Verstack does, what changes. One action: Book a demo (`https://cal.com/nathaniel-rudichuk-qmkbt8/30min`). Status in words, numbers real or absent.

## Implementation ownership

| Concern | Owner |
|---|---|
| Tokens | `brand/tokens.json` (copy of the claude.ai design system) |
| Drawings | `illustrations/` |
| Still layouts | `templates/` |
| Motion components, moves and the clip library | `design-system/src/` |
| Catalog and player | `design-system/index.html`, `design-system/player.html` |
| Rendered video | `motion/render.py` → `motion/out/` |
| App UI images and anchors | `product-ui/` |
| Release email | `email/`, Resend template `verstack-product-update` |
| Rules and names | `design-system/` |
