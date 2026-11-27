# Brief: TFGON logo mark, colours and typeface (drafts for Ed to choose from)

You are a designer-builder on **TFGON**, the Tech for Good Organisers Network, in the public repository `edsaperia/tfgon`. Your coordinator is the cloud session https://claude.ai/code/session_018uvzSPGKyoiNguMwg4To3h (session id `session_018uvzSPGKyoiNguMwg4To3h`).

## Read first

1. This repository's `CLAUDE.md`, especially *The website*, *Old-site assets*. Ed has decided to refresh each old asset, never reuse it as it was. Also read the glossary.
2. `reference/old-site/`: the old logo (SVG), its colours, and a rendered sheet (`logo-sheet.png`).
3. From `edsaperia/dev-ops` on `main` (public: `git clone --depth 1 https://github.com/edsaperia/dev-ops` into your scratchpad): `AGENTS.md`, `owner/PROFILE.md`, `CONVENTIONS.md`. Follow CONVENTIONS.md for the draft PR, the `QUESTION:` / `FINAL:` comments and *Done means seen working*.
4. **TFGON is off Ed's questions page.** Put nothing on it. Anything that needs Ed goes to your coordinator as a `QUESTION:` on your PR.

## The work: one piece

Draft options for Ed to choose from. **You do not choose, and you build no site code.** A separate builder is building the site at the same time with placeholders, and your chosen results will drop into it later. Work on your own branch, with a draft PR titled **"TFGON logo, colours and typeface: drafts — do not merge"**, opened at the start. Subscribe to its activity (`subscribe_pr_activity`). Put everything in `/design` (Pages publishes only `/docs`, so nothing here goes live).

### 1. The logo mark: three or four concepts

Ed's decision: **a new mark built on the old idea, not the old drawing.** The idea is several communities coming together. It could be tied to the directory's UK map, but that's optional. The old mark (four overlapping strokes) is the starting point for the idea, not something to trace.

For each concept:
- a simple, hand-editable SVG (plain shapes, no embedded images or fonts);
- shown full size, with the name "Tech for Good Organisers Network" set beside it in each typeface candidate (see 3);
- shown at header size (about 32 px tall), at browser-tab size (16 px and 32 px), and on a dark background;
- a version that still reads at 16 px. If the full mark can't, draw a simplified one;
- one sentence on what it says, and its main weakness.

### 2. The colours: the old four, retuned

Ed's decision: **keep the four-colour family (pink, yellow, green, blue), retuned** so the colours sit well together. The bright tones are for shapes (the mark, map pins, highlights), and a dark ink is for words and links. Old values: pink `#EF476F`, yellow `#FFD166`, green `#06D6A0`, blue `#118AB2`, words `#393E46`. Propose one retuned set, with:
- each colour's value and role;
- a contrast table against white and against the ink, marking which pairs pass WCAG AA for normal text, which pass only for large text or shapes, and which fail;
- the four colours side by side as map pins on a light background, checked for colour-blind distinguishability (a simulation is fine; say which you used).

Show every concept in this palette.

### 3. The typeface: two candidates

Ed's decision: **one open-licence typeface in the old site's geometric, friendly spirit, shipped with the site's own files.** It is never loaded from a font service. Propose two, for example Figtree or Outfit, but you choose. Each must be under the SIL Open Font License or similar and available as `woff2` from an npm package or another source you can reach. For each:
- the name beside each mark concept;
- a sample of a heading, body text and a link, using the real statement of purpose from `CLAUDE.md`;
- its licence, where you got it, and the total `woff2` size for the weights needed (regular and bold, plus italic if you think it's needed);
- the font files committed in `/design/fonts/`, with the licence file.

### The sheet

Make one HTML page, `/design/index.html`, that shows all of the above, loads nothing from outside, and is laid out for Ed to compare concepts side by side. Take screenshots of it at desktop width (deviceScaleFactor 2), split into readable sections, committed in `/design/screenshots/` and attached to your FINAL.

## Finishing

Post `FINAL:` on your PR, as CONVENTIONS.md describes. Include the screenshots, each concept's sentence and weakness, the contrast table, both typefaces with their licences and sizes, the numbered calls you made, and a *Rough or unverified* section. Then wake your coordinator: `create_trigger` with `persistent_session_id: "session_018uvzSPGKyoiNguMwg4To3h"` and the prompt *"TFGON PR #n: FINAL posted (design drafts), please review — <link to the comment>"*, then `fire_trigger`, then `delete_trigger`. Do the same with a blocking `QUESTION:`. Never merge your PR.
