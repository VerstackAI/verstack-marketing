# Verstack marketing design system

## Purpose

The look of everything Verstack puts in front of the market: release emails, LinkedIn posts, release videos and explainer graphics. It sits beside the app's design systems in `VerstackAI/verstack-mvp/apps/design-system` (desktop and mobile) and shows the app exactly as it is.

Two kinds of picture carry the story:

- **Line drawings** of the real things maintenance happens to (buildings, units, appliances), with one lime part.
- **The real app**: phone screens, the board and its cards, captured from the running apps.

## Principles

**Light cards on the dark.** Every frame has at least one light card on the dark ground, like the cards on verstack.ai. Pictures go on the cards; headlines go on the dark.

**Sparse and bold.** A big headline, one picture, two callouts at most. Nothing under 28 px. When in doubt, take something away.

**Fill the space.** Headlines are sized to their column. Under the headline sits a real app part or the supporting line, never an empty band.

**One lime thing.** The lime part of a drawing or a ring around one app element. The scan gradient appears at most once per video, as a faint sweep.

**The app as it is.** App UI is captured, not drawn. It keeps the app's names, tokens and wording.

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

- 16 px of ground around and between cards. Cards 40 px radius, tiles 24 px.
- 1920 x 1080: Light Card 1110 x 1048 at left, Type Column 600 px at right, starting 96 px from the top.
- 1080 x 1350: Light Card across the top (about 830–880 px tall), headline below on the dark, lockup bottom left.
- Flat. No shadows.

## Drawings

Isometric, 1.25 px hairlines, faces filled with the surface they sit on, built by `illustrations/build.py` so every line matches. 21 public drawings, dark and light; use the light version on a Light Card. One Lime Part per drawing that has a subject. See `illustrations/` and the claude.ai design system's Drawing section.

## App UI

`product-ui/capture.py` captures the running apps from a verstack-mvp checkout:

- **Desktop**: the web app in mock mode (`VITE_MOCK_API=true`), signed in with its built-in demo account. Screens at 2x, parts at 3x.
- **Mobile**: the design canvas, each screen in its device shell at 3x.

It writes `product-ui/anchors.json` with the boxes of named elements so a Ring or a callout can point at them. Re-run it when the app changes; never edit the images.

Use a Phone Shot or Board Shot on the Light Card, an App Part under the headline, and a Ring around the one element the story is about. Name what you show with the app's canonical names (see `COMPONENT_INDEX.md`).

Design-canvas screens show designs; some features are not live. Check status before posting.

## Motion

Moves: Draw, Explode, Highlight, Trace, plus the Screen Push for app UI and one optional Gradient Sweep. Ease `cubic-bezier(0.2, 0, 0, 1)`; draw 1.2–1.6 s; enter 480 ms with an 8–24 px rise; no bounce. Every clip is an HTML page with `renderAt(t)`, rendered to MP4 by `motion/render.py` at 30 fps.

## Voice

Headlines are claims in sentence case with a full stop. Sequence before benefit: who does what, what Verstack does, what changes. One action: Book a demo (`https://cal.com/nathaniel-rudichuk-qmkbt8/30min`). Status in words, numbers real or absent.

## Implementation ownership

| Concern | Owner |
|---|---|
| Tokens | `brand/tokens.json` (copy of the claude.ai design system) |
| Drawings | `illustrations/` |
| Still layouts | `templates/` |
| Video | `motion/` |
| App UI images and anchors | `product-ui/` |
| Release email | `email/`, Resend template `verstack-product-update` |
| Rules and names | `design-system/` |
