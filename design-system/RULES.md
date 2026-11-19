# Verstack marketing rules

These rules apply to every release email image, LinkedIn post, release video and explainer graphic. The app's own rules live in `VerstackAI/verstack-mvp/apps/design-system/RULES.md` (desktop) and `apps/design-system/mobile/RULES.md` (mobile); this system follows them wherever it shows the app.

## Everything

1. Cards on the dark ground (`ground-900`), with 16 px of ground showing around and between them. Every clip comes in two modes: light (mist cards, ink lines) and dark (`card-dark` cards with a faint edge, mist lines). Stills use light cards.
2. One lime element on screen at a time: the lime part of a drawing, the trace dot, or a ring around one real app element. Nothing else is lime.
3. No index numbers or section keys ("1.0", "1.1", "01"), no numbered badges, no square nodes, no grids or plus marks, no file-name title bars, no corner meta lines, no monospace type.
4. The scan gradient is rare: one faint sweep (14% opacity) across a card. Never held on screen, never on every card, never as the cut between beats.
5. App UI is the real app. Every phone screen, board and card comes from `product-ui/`, captured from the running apps with `product-ui/capture.py`. Never redraw, restyle or retouch app UI, and never invent screens.
6. Name app UI with its canonical name from the app's `COMPONENT_INDEX.md` (Card, Workflow Status Badge, Pill Switch, Nav Dock, List Row and so on).
7. Status is honest: Live, Rolling out or In pilot, in words. A screen from the design canvas is a design until the feature ships; check before posting it.
8. Sample data only (Maple Court, King West Residences, Unit 4B). Never a customer's.
9. Planned hardware stays private until announced.
10. Line weight follows the isometric phone on verstack.ai: proportional to the drawing's size, outer contour heavier than the lines inside it. Never a uniform hairline. Appliances have softly rounded corners; buildings and plans stay square.
11. The phone is the website's phone (`illustrations/sources/phone-site.svg`). Never draw another.

## Motion clips

12. Clips are imagery only. No headlines, labels, callouts, captions, numbers or keys in a clip. The words go on in the video edit or in the post.
13. Every drawing, phone, screen and part is centred both ways in its card. Nothing is pushed aside to make room for anything.
14. Cards are on screen from the first frame, so clips cut together cleanly. The imagery moves; the frame does not.
15. In dark mode the lime part's outline, and every line drawn on the part, turn dark as it lights, so its details stay visible.
16. Every clip is code in `design-system/src/clips.js`, built from the components in `src/components.js`, and must pass `python3 design-system/scripts/verify.py`. No hand-made clip pages.

## Still layouts (posts and email)

17. Drawings and app screens sit on the light cards. Headlines sit on the dark.
18. Nothing under 28 px at full size. If a line only works small, cut it.
19. Headlines fill their space: sized to the column, two to four balanced lines. Under the headline goes a real app part or one supporting line, never an empty band.
20. Two callouts at most. A callout is bold pop-up text: name 40 px weight 600, one 28 px line under it, a plain leader line, no node.

## Do not use

- Drop shadows, glows, photos or stock imagery.
- A second accent colour, or lime as text on light.
- Text of any kind inside a motion clip.
- Imagery placed off centre in its card.
- A uniform hairline, or a phone drawn any other way than the website's.
- Two lime elements on screen at once.
- App UI drawn by hand, recoloured, or cropped so a component reads as something else.
- "AI-powered", deposit, chargeback or deposit recovery.

## Review checklist

- `python3 design-system/scripts/verify.py` passes in both modes (clips).
- One lime element at a time.
- Imagery centred in every card.
- No text in a clip; every word 28 px or larger in a still.
- App UI from `product-ui/`, named canonically, and live or clearly marked.
- At most one gradient sweep.
- Changelog updated.
