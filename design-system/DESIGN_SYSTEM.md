# Verstack marketing design system

## Purpose

The look of everything Verstack puts in front of the market: release emails, LinkedIn posts, release videos and explainer graphics. It sits beside the app's design systems in `VerstackAI/verstack-mvp/apps/design-system` (desktop and mobile) and shows the app exactly as it is.

Two kinds of picture carry the story:

- **Line drawings** of the real things maintenance happens to (buildings, units, appliances), with one lime part.
- **The real app**: phone screens, the board and its cards, captured from the running apps.

## Principles

**Light cards on the dark.** Every frame has at least one light card on the dark ground, like the cards on verstack.ai.

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

Isometric, 1.25 px hairlines, faces filled with the surface they sit on, built by `illustrations/build.py` so every line matches. 21 public drawings, dark and light; use the light version on a Light Card. One Lime Part per drawing that has a subject. See `illustrations/` and the claude.ai design system's Drawing section.

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
- `scripts/verify.py` checks every clip in a real browser: no text, imagery centred in every card, one lime element at a time.

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
