# Brief: TFGON website, first version (the page itself)

You are a builder on **TFGON**, the Tech for Good Organisers Network, in the public repository `edsaperia/tfgon`. Your coordinator is the cloud session https://claude.ai/code/session_018uvzSPGKyoiNguMwg4To3h (session id `session_018uvzSPGKyoiNguMwg4To3h`).

## Read first

1. This repository's `CLAUDE.md`. It records every decision Ed (the owner) has made about the site, and its glossary names the parts: **community**, **organiser**, **directory**, **application**. Use those words in the code and in your PR.
2. From `edsaperia/dev-ops` on `main` (public: `git clone --depth 1 https://github.com/edsaperia/dev-ops` into your scratchpad): `AGENTS.md`, `owner/PROFILE.md`, `CONVENTIONS.md`. Follow CONVENTIONS.md for the draft PR, the `REPORT:` / `QUESTION:` / `FINAL:` comments, *Tests that tell the truth* and *Done means seen working*.
3. **TFGON is off Ed's questions page.** Put nothing on it. Anything that needs Ed goes to your coordinator as a `QUESTION:` on your PR.

## The work: one piece

Build the site's single page in this repository, on your own branch, with a draft PR titled **"TFGON website: first version — do not merge"**, opened at the start. Subscribe to its activity (`subscribe_pr_activity`).

**Do not enable GitHub Pages, change repository settings or touch DNS.** Deploying is Ed's decision, taken after review.

### What the page is

- **One page, with folding sections** in this order: **intro**, **TFGON events**, **join**, **directory**. Open sections can be linked to directly (for example `#directory`), and the page works with keyboard and screen reader.
- **Audience:** organisers who might join the network, and funders and partners. It is not aimed at the general public.
- **Plain static files in `/docs`**, which is the folder Pages will publish from: HTML, CSS and a little JavaScript, with no framework and no build step. The site must load nothing from any outside server at runtime (no web fonts from a CDN, no map tiles, no analytics). Ed wants as few services as possible.
- **Design:** a fresh, simple design that reads well at phone and desktop width, following the decisions under *Old-site assets* in `CLAUDE.md`. A separate designer is drafting the new logo mark, the retuned colours and the typeface **at the same time as you**, so build in a way that lets their results drop in afterwards, each changed in one place:
  - **Logo:** a visibly marked placeholder mark (a plain square is fine) beside the name "Tech for Good Organisers Network" set as real text. Do not reuse the old mark.
  - **Colours:** every colour defined once, as CSS custom properties. For now use the old four (pink `#EF476F`, yellow `#FFD166`, green `#06D6A0`, blue `#118AB2`) for shapes only: pins, highlights, accents. Use a dark ink for all text and links, passing WCAG AA contrast.
  - **Typeface:** one font stack, defined once, using the device's system font for now. The designer's open-licence font will be self-hosted in `/docs` later.
  - The old site's logo, colours and words are in `reference/old-site/` for context. Do not copy its layout or wording.

### The sections

- **Intro.** Lead with the statement of purpose, quoted exactly from `CLAUDE.md`, and the one-line definition of tech for good recorded there. There are no principles and no "how we work" list (Ed dropped them). Add a short "the network at a glance": its communities and regions, and its rhythm of three online quarterlies and one in-person retreat a year. Add one line each for would-be members (pointing to *join*) and for funders and partners. For the funders and partners contact, use the placeholder **`[FUNDERS CONTACT — Ed to supply]`**, visibly marked.
- **TFGON events.** The network's own meetings, upcoming first, then past. Leave out any meeting links. Upcoming: online quarterly, Wednesday 3 March 2027, 12:00–13:00; national retreat 2027 in Bristol, dates to be confirmed. Past: online quarterly, 25 November 2026; online quarterly, 2 September 2026; national retreat, 18–19 May 2026, Newcastle (where the statement of purpose was agreed). Keep events in one plain data file, so adding one means editing one entry.
- **Join.** Explain how joining works. You apply with a short form. The network looks at the tech-for-good events you have organised, passes your application to the nearest organiser, and discusses it at the next quarterly meeting. Joining is mostly by invitation, for people who run tech-for-good communities. The **application form** has three fields, *name*, *email* and *links to tech-for-good events you've organised* (one or more), plus a hidden trap field for bots. It does not ask for location. The form posts JSON to an endpoint URL set in one obvious place, which is empty for now. While the endpoint is empty, or if sending fails, the form must not pretend to succeed. It tells the applicant plainly and shows the fallback address **`[FALLBACK EMAIL — Ed to supply]`**. The endpoint (a DigitalOcean Function writing to a private repository) is the next build. Do not build it.
- **Directory.** A **drawn map of the UK** built into the page as inline SVG, with one pin per **community**. Clicking a pin, or its name in the list beside or below the map, unfolds that community's entry. For the coastline, use an openly licensed source you can install through npm, such as Natural Earth data, which is public domain. Simplify it and check the result into `/docs`, so the page needs nothing at runtime. Name the source and its licence in the PR. Each entry has: community name; region; a line on what it does; website; events link; organisers' names. Email and photo fields stay empty for now, because publishing them needs each organiser's consent. **Never put a phone number or personal email in the repository.** Keep all communities in one plain data file. Draft data (Ed will check every line; mark it as draft in the PR):
  - **Tech for Good Scotland**, run by ThirdSectorLab. Scotland. https://thirdsectorlab.co.uk/techforgood/. Organiser: Ross McCulloch.
  - **Tech for Good Cymru**, run by ProMo Cymru. Wales. https://www.promo.cymru. Organiser: Arielle Tye.
  - **Tech4Good South West**, Tech4Good South West CIC. South West England. https://www.tech4goodsouthwest.org, events https://luma.com/tech4goodsouthwest. Organisers: Annie Legge, Ed Howarth.
  - **Newspeak House**. London. https://newspeak.house, events https://newspeak.house/events. Organiser: Edward Saperia.
  - **TechSoup Connect England**, run by Superhighways. England (its events are now online). Website to be confirmed. Organisers: Kate White, Siddharth Bannerjee.
  - **Digital Leads Network**, run by CAST. UK-wide, online. Website to be confirmed. Organiser: David Scurr.
  - **Emerging:** North West England (Manchester) and North East England (Newcastle). Show these as emerging, with no organisers named yet.

  How communities that are online or UK-wide appear on a map is your call. List that call in your FINAL.

  **Past members**, at the foot of the directory: a folded list headed along the lines of "Communities that helped build the network". These communities are **not** on the map. Each entry has the community's name, region, rough years if known, a link if its site still exists, and its founding organiser's name. Keep them in the same data file, marked as past, so moving one back is a one-word change. Draft list, from the old site's founding members (Ed is confirming which are past; mark it as draft). You can read the old site's one-page-per-network descriptions at `https://www.techforgoodorganisers.uk/networks/<slug>` if your environment allows that host. If it doesn't, leave the descriptions out and say so in your FINAL.
  - Tech for Good London / Global (`tech-for-good-london`): Dama Sathianathan
  - Tech for Good Live, Manchester (`rebecca-rae-evans`): Rebecca Rae-Evans
  - Tech for Good Oxford (`tech-for-good-oxford`): Chris Ashworth
  - Digital for Good, Scotland (`digital-for-good-scotland`): Barry O'Kane
  - Tech for Good Exeter (`tech-for-good-exeter`): Micheal McAndrew (spelled as on the old site; flag it as unverified)
  - Social Tech North East (`social-tech-north-east`): David Van der Velde
  - NetSquared Midlands (`netsquared-midlands`): Pauline Roche

### Tests

Add a small Playwright suite (`@playwright/test`; Chromium is preinstalled, see your environment notes) and a GitHub Actions workflow that runs it on pull requests. At minimum, and each seen failing once before it passes:

- each section folds and unfolds, and a `#section` link opens it;
- every current community in the data file has exactly one pin and one entry, and no past community has a pin, and clicking a pin opens the right entry (the expected community names are written by hand in the test);
- the form, with no endpoint set, shows the failure message and the fallback address and does not claim success;
- the page makes no request to any other origin;
- no file under `/docs` contains anything shaped like a UK phone number.

Put in your FINAL the exact commands to run the tests, for the coordinator to write into `CLAUDE.md`. Do not edit `CLAUDE.md` yourself: it is the coordinator's.

## Finishing

Post `FINAL:` on your PR, as CONVENTIONS.md describes. Include: screenshots at phone and desktop width (deviceScaleFactor 2), with every section open; every user-visible string; the draft data, marked as draft; your calls, numbered; and a *Rough or unverified* section. Then wake your coordinator: `create_trigger` with `persistent_session_id: "session_018uvzSPGKyoiNguMwg4To3h"` and the prompt *"TFGON PR #n: FINAL posted, please review — <link to the comment>"*, then `fire_trigger`, then `delete_trigger`. Do the same with a blocking `QUESTION:`. Never merge your PR.

A subagent builder in a cloud session: make your worktree with `git worktree add` into your scratchpad (CONVENTIONS.md, *Briefing a builder*).
