// Renders the browser-tab icons from the mark's SVGs into docs/img.
// Run it only when the mark changes: `npm run build:icons`.
//   icon-16.png, icon-32.png  from mark-small.svg (the pixel icon)
//   apple-touch-icon.png      from mark.svg (the full mark), 180 px
import { chromium } from '@playwright/test';
import { readFileSync } from 'node:fs';

const img = (name) => new URL(`../docs/img/${name}`, import.meta.url);
const jobs = [
  ['mark-small.svg', 16, 'icon-16.png'],
  ['mark-small.svg', 32, 'icon-32.png'],
  ['mark.svg', 180, 'apple-touch-icon.png'],
];

const browser = await chromium.launch();
for (const [source, size, out] of jobs) {
  const page = await browser.newPage({ viewport: { width: size, height: size }, deviceScaleFactor: 1 });
  const svg = readFileSync(img(source), 'utf8');
  await page.setContent(`<style>html,body{margin:0;background:transparent}svg{display:block;width:${size}px;height:${size}px}</style>${svg}`);
  await page.screenshot({ path: img(out).pathname, omitBackground: true, clip: { x: 0, y: 0, width: size, height: size } });
  await page.close();
  console.log(`${out}: ${size}×${size} from ${source}`);
}
await browser.close();
