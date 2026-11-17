# verstack-marketing

Public home for Verstack's marketing files: release graphics, email images, logos and the templates that make them.

**This repo is public.** Email apps and LinkedIn can only show images they can load without a login, so everything here can be seen by anyone. Only put finished, public marketing material here. No customer names, no internal numbers, no drafts that say things that are not live yet.

## Links

GitHub Pages serves this repo at:

```
https://verstackai.github.io/verstack-marketing/<path in this repo>
```

For example, the white lockup for an email header:
`https://verstackai.github.io/verstack-marketing/brand/png/verstack-lockup-white-240x48.png`

## What is where

| Folder | What |
| --- | --- |
| `brand/` | Logos (SVG and PNG), fonts (Inter, IBM Plex Sans, with licences) and `tokens.json`, the colour, type and spacing values |
| `templates/` | HTML templates for release graphics: `release-1080x1350.html` (LinkedIn feed) and `release-1200x630.html` (email and link previews) |
| `email/` | Source of the Resend template `verstack-product-update`, plus sample values |
| `releases/` | One folder per release, holding its rendered images |
| `scripts/render.sh` | Turns a template into a PNG with headless Chrome |

The design rules live in the **Verstack Marketing** design system on claude.ai. `brand/tokens.json` is a copy of its tokens.

## Making the images for a release

1. Copy each template inside `templates/`, keeping the size in the name: `templates/2026-11-repeat-repairs-1080x1350.html`.
2. Edit the text where the template says `EDIT`.
3. Render each one into the release folder:
   `scripts/render.sh templates/2026-11-repeat-repairs-1080x1350.html releases/2026-11-repeat-repairs/linkedin-1080x1350.png`
4. Commit and push. The images are live at the Pages link a minute or two later.
5. Use the 1200 x 630 image link in the email and attach the 1080 x 1350 PNG to the LinkedIn post.

`releases/_sample/` shows what the templates produce with sample copy.
