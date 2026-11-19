# Canonical marketing component index

Use these names exactly in briefs, reviews and changelog entries. App UI keeps the app's own canonical names; see the last table.

## Frame

| Canonical name | Owner | Meaning |
|---|---|---|
| Ground | `templates/line.css` (`ground-900`) | The dark background of every frame |
| Light Card | `motion/gen.py` `card()`, `templates/gen.py` `card()` | Mist surface, 40 px radius (24 px for tiles), holding a drawing or app screen |
| Type Column | `motion/gen.py` (`RX`, `RW`) | The 600 px column on the dark at the right of a 1920 x 1080 frame |
| Headline | `headline()` + `fitText()` | Inter 400, tracking -0.05em, fitted to fill its column in two to four balanced lines |
| Supporting Line | `support()` | One 30–34 px line in `fg-muted`, directly under the headline or the App Part |
| Lockup | `lockup()`, `brand/logos/` | White on dark, black on a Light Card, 34 px tall in video |
| Status Word | `.dot` in `templates/line.css` | "● Live", "○ In pilot". Status only |

## Drawing

| Canonical name | Owner | Meaning |
|---|---|---|
| Illustration | `illustrations/svg/` (built by `illustrations/build.py`, `scenes_more.py`) | Isometric hairline drawing, dark and light versions |
| Lime Part | `hi=True` in the scene function | The one subject of a drawing, filled lime |
| Callout | `popup()` + leader polyline | Bold name and one line, joined to a part by a plain leader line |
| Anchor | `illustrations/anchors.json` | Screen points where leader lines attach |

## App UI in graphics

| Canonical name | Owner | Meaning |
|---|---|---|
| Phone Shot | `phone()`; images in `product-ui/mobile/screens/` | A real mobile screen in its device shell, on a Light Card |
| Board Shot | `app_board()`; `product-ui/desktop/screens/` | A real desktop screen on a Light Card, usually moved in on one element |
| App Part | `app_part()`; `product-ui/*/parts/` | One real app component on the dark under the headline |
| Ring | `ring()` | The lime outline around one real app element; the frame's one lime element |
| Screen Push | `app_decide()` | One screen sliding in over another inside the phone, as the app navigates |
| Product UI Anchor | `product-ui/anchors.json` | Boxes of named elements inside each captured screen |

## Motion

| Canonical name | Owner | Meaning |
|---|---|---|
| Draw | `prepDraw`, `drawAt` in `motion/motion.js` | Lines draw on from nothing |
| Explode | `explode()` | Parts or floors separate up the z axis and close again |
| Highlight | `drawAt(..., highlightAt)` | The Lime Part fills lime once |
| Trace | `capture_walk()` | A lime marker moves along a route, places are logged |
| Gradient Sweep | `sweep()` | The one faint scan-gradient band across the opening card |

## Layouts and clips

| Canonical name | Build | Use |
|---|---|---|
| Spec Sheet | `templates/spec-sheet-1080x1350.html` | Default LinkedIn image for a product update |
| Data Plate | `templates/data-plate-1080x1350.html` | A short list with a status |
| Annotated Drawing | `templates/annotated-1920x1080.html` | A walkthrough frame |
| Email Hero | `templates/email-hero-1104x552.html` | Top image of the release email |
| Link Preview | `templates/link-preview-1200x630.html` | What social sites show for verstack.ai |
| Product Phone | `templates/product-phone-1080x1350.html` | Two real phone screens and a headline |
| Product Desktop | `templates/product-desktop-1920x1080.html` | The real board, one card ringed, an App Part |
| Exploded View | private folder only | Planned hardware, until announced |
| Clips | `motion/<name>.html` → `motion/out/<name>.mp4` | draw-highlight, explode, capture-walk, callouts, asset-tiles, app-decide, app-field-home, app-board, app-report |

## App parts and screens, by app canonical name

| File in `product-ui/` | App canonical names, closest match (from verstack-mvp `COMPONENT_INDEX.md`; check there before quoting) | Source |
|---|---|---|
| `mobile/screens/field-home.png` | Screen Header, Stat Tile, List Group / List Row, Section Header, Nav Dock | Design canvas, Field Home |
| `mobile/screens/manager-work.png` | Screen Header, Pill Switch, List Row, Generic Badge, Nav Dock | Design canvas, Manager Work |
| `mobile/screens/work-order.png` | Screen Back Button, Fact Chip, List Row, Card, Input Bar | Design canvas, Ticket |
| `mobile/screens/report.png` | Screen Back Button, Submit Gate, Card, Inspection Status Badge, Stat Tile | Design canvas, Field Report & Finding |
| `mobile/screens/manager-home.png` | Stat Tile, List Row, Nav Dock | Design canvas, Manager Home |
| `mobile/screens/inspections.png` | Search Field, Toggle Chip, List Row | Design canvas, Inspections |
| `mobile/parts/record-details.png` | Card with List Rows, Inspection Status Badge | Field Report & Finding |
| `mobile/parts/record-summary.png` | Card, Stat Tile (caution tone) | Field Report & Finding |
| `mobile/parts/waiting-on-you.png` | List Group / List Row, Icon Tile | Field Home |
| `mobile/parts/decision-list.png` | List Group / List Row, Generic Badge | Manager Work |
| `mobile/parts/work-order-details.png` | Card with List Rows | Ticket |
| `desktop/screens/maintenance-board.png` | App Sidebar, Page Header, Section Dropdown, Filter Bar, Search Field, Workspace Card | Web app (mock mode), Maintenance |
| `desktop/screens/reports.png` | Page Header, Data Table, Workflow Status Badge, Generic Badge | Web app (mock mode), Inspections → Reports |
| `desktop/screens/locations.png` | Page Header, Section Dropdown, Workspace Card | Web app (mock mode), Locations |
| `desktop/parts/work-order-card-*.png` | Workspace Card, Generic Badge | Maintenance board |
| `desktop/parts/home-decisions.png` | Section Card, Navigable Table Row | Home |
| `desktop/parts/location-card.png` | Workspace Card, Icon Tile | Locations |
