// Draws the directory map: mark I8's low-poly UK (docs/img/mark.svg), large,
// without its ink tile (the page is the same ink). It writes the facets into
// docs/index.html between the <!-- map:start --> and <!-- map:end --> markers.
//
// Run it only if the mark changes: `npm run build:map`. The page needs
// nothing at runtime. Community circles are placed by site.js from each
// community's "pin" ({ "x", "y" }, in the mark's own 0–10 grid), so they line
// up with the shape whatever size it is drawn.

import { readFileSync, writeFileSync } from 'node:fs';

const mark = readFileSync(new URL('../docs/img/mark.svg', import.meta.url), 'utf8');
const polygons = [...mark.matchAll(/<polygon\b[^>]*\/>/g)].map((m) => m[0]);
if (polygons.length < 20) throw new Error(`Expected the mark's facets, found ${polygons.length} polygons`);

// The part of the mark's 10 × 10 grid to show: the shape with a little room,
// including the sea to the east where the "Online and UK-wide" box sits.
const VIEW = { x: 0.6, y: 0.3, width: 8.9, height: 9.4 };

const svg = `<svg class="map-drawing" viewBox="${VIEW.x} ${VIEW.y} ${VIEW.width} ${VIEW.height}" role="img" aria-labelledby="map-title">
          <title id="map-title">The network's mark, a low-poly map of the UK, with a circle for each community</title>
          ${polygons.map((p) => p.replace(/\s+/g, ' ')).join('\n          ')}
        </svg>`;

const file = new URL('../docs/index.html', import.meta.url);
const html = readFileSync(file, 'utf8');
const pattern = /(<!-- map:start -->)[\s\S]*?(<!-- map:end -->)/;
if (!pattern.test(html)) throw new Error('Map markers not found in docs/index.html');
writeFileSync(file, html.replace(pattern, `$1\n        ${svg}\n        $2`));
console.log(`Map written: ${polygons.length} facets.`);
