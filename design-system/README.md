# Design system

The code-based design system for Verstack marketing, in the same shape as the app's design systems in `VerstackAI/verstack-mvp/apps/design-system`: rules and names in Markdown, and a catalog that renders the real components from code.

## Open it

Open `design-system/index.html` in a browser. It works straight from disk and from GitHub Pages, with no server or build tool:

```
https://verstackai.github.io/verstack-marketing/design-system/
```

The catalog shows the tokens, every component working, all 50 motion clips playing live (at 16:9, 1:1 or 4:5), every drawing, every captured app screen and the still layouts. Click a clip to open it full size in `player.html`.

## Files

| File | What |
| --- | --- |
| `index.html`, `catalog.css`, `catalog.js` | The catalog page |
| `player.html` | Plays one clip full size: `player.html?clip=draw-dishwasher&w=1920&h=1080` |
| `src/tokens.css`, `src/tokens.js` | Tokens as CSS variables and as `VS.tokens`. Generated from `brand/tokens.json` |
| `src/assets.js` | Drawings, anchors, product UI boxes and image sizes as `VS.assets`. Generated |
| `src/engine.js` | Timing maths and the moves (`VS.engine`, `VS.moves`) |
| `src/components.js` | Frame, Layout, Card, Drawing, Phone, Push Screen, Screen, Part, Ring, Tracer, Sweep |
| `src/runtime.js` | The clip registry, `VS.mount` and `VS.play` |
| `src/clips.js` | The 50-clip motion library |
| `build.py` | Writes the generated files in `src/` |
| `scripts/verify.py` | Checks every clip against the motion rules in a real browser |
| `RULES.md`, `COMPONENT_INDEX.md`, `DESIGN_SYSTEM.md`, `CHANGELOG.md`, `AGENT_CONTEXT.md` | Rules, canonical names, principles, history, agent notes |

## Add a clip

1. Add a `VS.clip({ id, group, name, build })` to `src/clips.js`, using the components. Keep it imagery only and centred.
2. Open `player.html?clip=<id>` and watch it.
3. Run `python3 design-system/scripts/verify.py <id>`.
4. Render it: `python3 motion/render.py <id>` (MP4 in `motion/out/`).
5. Add a line to `CHANGELOG.md`.

After changing `brand/tokens.json`, a drawing, or a product UI capture, run `python3 design-system/build.py` first.
