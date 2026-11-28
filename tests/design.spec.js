const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const { openPage } = require('./helpers');

// Written by hand from Ed's confirmed design (CLAUDE.md, Old-site assets).
const ICONS = [
  { rel: 'icon', type: 'image/svg+xml', size: null },
  { rel: 'icon', type: 'image/png', size: 16 },
  { rel: 'icon', type: 'image/png', size: 32 },
  { rel: 'apple-touch-icon', type: 'image/png', size: 180 },
];

async function openEverything(page) {
  const closed = await page.locator('.fold-toggle[aria-expanded="false"]').evaluateAll((ts) => ts.map((t) => t.getAttribute('aria-controls')));
  for (const id of closed) {
    const toggle = page.locator(`.fold-toggle[aria-controls="${id}"]`);
    if (await toggle.getAttribute('aria-expanded') === 'false') await toggle.click();
  }
}

test('the page sets its words in Outfit, loaded from its own origin', async ({ page, baseURL }) => {
  const fontResponses = [];
  page.on('response', (r) => { if (r.request().resourceType() === 'font') fontResponses.push(r); });
  await openPage(page);
  await page.evaluate(() => document.fonts.ready);

  const family = await page.locator('body').evaluate((b) => getComputedStyle(b).fontFamily);
  expect(family.split(',')[0].trim().replace(/["']/g, '')).toBe('Outfit');
  expect(await page.evaluate(() => document.fonts.check('400 16px Outfit') && document.fonts.check('700 16px Outfit'))).toBe(true);
  const loaded = await page.evaluate(() => [...document.fonts].filter((f) => f.family.replace(/["']/g, '') === 'Outfit' && f.status === 'loaded').map((f) => f.weight));
  expect(new Set(loaded)).toEqual(new Set(['400', '700']));

  expect(fontResponses.length).toBeGreaterThan(0);
  for (const r of fontResponses) {
    expect(new URL(r.url()).origin).toBe(new URL(baseURL).origin);
    expect(r.url()).toMatch(/\/fonts\/outfit-latin-(400|700)-normal\.woff2$/);
    expect(r.status()).toBe(200);
  }
});

test('the page has no italic text', async ({ page }) => {
  await openPage(page);
  await openEverything(page);
  const italic = await page.locator('body *').evaluateAll((nodes) => nodes
    .filter((n) => n.textContent.trim() && getComputedStyle(n).fontStyle !== 'normal')
    .map((n) => n.tagName + ': ' + n.textContent.trim().slice(0, 40)));
  expect(italic).toEqual([]);
});

test('each browser-tab icon the page links to exists and loads', async ({ page, request }) => {
  await openPage(page);
  const links = await page.locator('link[rel~="icon"], link[rel="apple-touch-icon"]').evaluateAll((ls) => ls.map((l) => ({
    rel: l.getAttribute('rel'), type: l.getAttribute('type'), sizes: l.getAttribute('sizes'), href: l.href,
  })));
  expect(links.map((l) => [l.rel, l.type, l.sizes])).toEqual(ICONS.map((i) => [i.rel, i.type, i.size ? `${i.size}x${i.size}` : null]));
  for (const [i, link] of links.entries()) {
    const response = await request.get(link.href);
    expect(response.status(), link.href).toBe(200);
    expect(response.headers()['content-type'], link.href).toContain(ICONS[i].type);
    const body = await response.body();
    if (ICONS[i].type === 'image/png') {
      // PNG width and height are big-endian at bytes 16 and 20.
      expect([body.readUInt32BE(16), body.readUInt32BE(20)], link.href).toEqual([ICONS[i].size, ICONS[i].size]);
    } else {
      expect(body.toString('utf8'), link.href).toContain('<svg');
    }
  }
});

// The test that the header and events section were dark bands is replaced by
// "the page background is dark throughout" in second-pass.spec.js (Ed's second
// design pass made the whole page dark).

test('the mark is in the header beside the name, and the placeholder is gone', async ({ page }) => {
  await openPage(page);
  await expect(page.locator('.site-header img.brand-mark')).toHaveAttribute('src', 'img/mark.svg');
  await expect(page.locator('.site-header .brand-name')).toHaveText(/Tech for Good\s*Organisers Network/);
  await expect(page.getByText('logo', { exact: true })).toHaveCount(0);
});

test('no colour-contrast problems with every section and entry open (axe)', async ({ page }) => {
  await openPage(page);
  await openEverything(page);
  await page.evaluate(() => document.fonts.ready);
  const results = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
  expect(results.passes.length + results.violations.length).toBeGreaterThan(0); // it checked something
  const problems = results.violations.flatMap((v) => v.nodes.map((n) => `${n.target.join(' ')}: ${n.failureSummary}`));
  expect(problems).toEqual([]);
});
