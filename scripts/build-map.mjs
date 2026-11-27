// Builds the drawn UK map for the directory and writes it into docs/index.html,
// between the <!-- map:start --> and <!-- map:end --> markers.
//
// Run it only when the map's look needs to change: `npm run build:map`.
// The page itself needs nothing at runtime; the result is checked in.
//
// Source: Natural Earth 1:50m Admin 0 country boundaries (public domain),
// via the world-atlas npm package (ISC licence), version 2.0.2.
//
// Projection: a plain equirectangular projection centred on the UK
// (longitude scaled by cos 54.5°). It is simple enough that the page's
// JavaScript places the pins with the same sum, reading the constants from
// the <svg>'s data- attributes.

import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import { feature } from 'topojson-client';

const require = createRequire(import.meta.url);
const topology = require('world-atlas/countries-50m.json');

const WEST = -8.8, EAST = 2.0, NORTH = 61.0, SOUTH = 49.8;
const LAT0 = 54.5;
const SCALE = 60; // SVG units per degree of latitude
const KX = Math.cos((LAT0 * Math.PI) / 180) * SCALE;
const width = Math.round((EAST - WEST) * KX);
const height = Math.round((NORTH - SOUTH) * SCALE);

const project = ([lon, lat]) => [(lon - WEST) * KX, (NORTH - lat) * SCALE];

// Douglas–Peucker simplification on projected points.
function simplify(points, tolerance) {
  if (points.length < 3) return points;
  const keep = new Uint8Array(points.length);
  keep[0] = keep[points.length - 1] = 1;
  const stack = [[0, points.length - 1]];
  while (stack.length) {
    const [a, b] = stack.pop();
    const [ax, ay] = points[a], [bx, by] = points[b];
    const dx = bx - ax, dy = by - ay, len = Math.hypot(dx, dy) || 1;
    let worst = -1, index = -1;
    for (let i = a + 1; i < b; i++) {
      const [px, py] = points[i];
      // Distance from the segment a–b, or from point a when a and b coincide
      // (a closed ring starts and ends on the same point).
      const d = dx === 0 && dy === 0
        ? Math.hypot(px - ax, py - ay)
        : Math.abs(dy * px - dx * py + bx * ay - by * ax) / len;
      if (d > worst) { worst = d; index = i; }
    }
    if (worst > tolerance) {
      keep[index] = 1;
      stack.push([a, index], [index, b]);
    }
  }
  return points.filter((_, i) => keep[i]);
}

const area = (ring) => {
  let s = 0;
  for (let i = 0; i < ring.length; i++) {
    const [x1, y1] = ring[i], [x2, y2] = ring[(i + 1) % ring.length];
    s += x1 * y2 - x2 * y1;
  }
  return Math.abs(s / 2);
};

function pathFor(countryId, { minArea = 2, tolerance = 0.6 } = {}) {
  const countries = feature(topology, topology.objects.countries).features;
  const country = countries.find((f) => f.id === countryId);
  if (!country) throw new Error(`No country with id ${countryId}`);
  const polygons = country.geometry.type === 'Polygon'
    ? [country.geometry.coordinates]
    : country.geometry.coordinates;
  const parts = [];
  for (const polygon of polygons) {
    const ring = simplify(polygon[0].map(project), tolerance);
    if (ring.length < 4 || area(ring) < minArea) continue;
    parts.push('M' + ring.slice(0, -1).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join('L') + 'Z');
  }
  return parts.join('');
}

const uk = pathFor('826');
const ireland = pathFor('372');

const svg = `<svg class="map-drawing" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="map-title"
          data-west="${WEST}" data-north="${NORTH}" data-lat0="${LAT0}" data-scale="${SCALE}">
          <title id="map-title">Map of the United Kingdom showing where the network's communities are</title>
          <path class="map-neighbour" d="${ireland}"/>
          <path class="map-land" d="${uk}"/>
        </svg>`;

const file = new URL('../docs/index.html', import.meta.url);
const html = readFileSync(file, 'utf8');
const pattern = /(<!-- map:start -->)[\s\S]*?(<!-- map:end -->)/;
if (!pattern.test(html)) throw new Error('Map markers not found in docs/index.html');
writeFileSync(file, html.replace(pattern, `$1\n        ${svg}\n        $2`));
console.log(`Map written: ${width}×${height}, ${uk.length + ireland.length} characters of path data.`);
