# Verstack marketing rules

These rules apply to every release email image, LinkedIn post, release video and explainer graphic. The app's own rules live in `VerstackAI/verstack-mvp/apps/design-system/RULES.md` (desktop) and `apps/design-system/mobile/RULES.md` (mobile); this system follows them wherever it shows the app.

## Non-negotiable

1. Balance light and dark the way verstack.ai does: light cards (`mist`, 40 px radius, 24 px for small tiles) on the dark ground (`ground-900`), with 16 px of ground showing around and between them. No all-dark frames.
2. Drawings and app screens sit on the light cards. Headlines sit on the dark.
3. Nothing under 28 px on any graphic or video frame at full size. If a line only works small, cut it.
4. Headlines fill their space: sized to the column, two to four balanced lines, as big as fits. A small headline floating in an empty column is wrong.
5. No empty type column. Under the headline goes a real app part or the supporting line, then the lockup. Never a headline at the top and one line at the bottom with nothing between.
6. One lime element per frame: the lime part of a drawing, or a ring around one real app element. Nothing else is lime.
7. Two callouts per frame at most. A callout is bold pop-up text: name 40 px weight 600, one 28 px line under it, a plain leader line, no node.
8. No index numbers or section keys ("1.0", "1.1", "01"), no numbered badges, no square nodes, no grids or plus marks, no file-name title bars, no corner meta lines, no monospace type.
9. The scan gradient appears once per video at most, as one faint sweep (14% opacity) across the opening card. Never on tiles, never as the cut between beats.
10. App UI is the real app. Every phone screen, board and card comes from `product-ui/`, captured from the running apps with `product-ui/capture.py`. Never redraw, restyle or retouch app UI, and never invent screens.
11. Name app UI with its canonical name from the app's `COMPONENT_INDEX.md` (Card, Workflow Status Badge, Pill Switch, Nav Dock, List Row and so on).
12. Status is honest: Live, Rolling out or In pilot, in words. A screen from the design canvas is a design until the feature ships; check before posting it.
13. Sample data only (Maple Court, King West Residences, Unit 4B). Never a customer's.
14. Planned hardware stays private until announced.

## Do not use

- Drop shadows, glows, photos or stock imagery.
- A second accent colour, or lime as text on light.
- Tiny captions on cards, keys on callouts, or labels on every tile.
- A gradient held on screen, or more than one sweep in a video.
- App UI drawn by hand, recoloured, or cropped so a component reads as something else.
- "AI-powered", deposit, chargeback or deposit recovery.

## Review checklist

- One lime element.
- Every word 28 px or larger at full size.
- Headline fills its column; no empty band under it.
- At least one light card; type on the dark.
- App UI from `product-ui/`, named canonically, and live or clearly marked.
- No numbers used as labels, no nodes, no grid.
- At most one gradient sweep.
- Changelog updated.
