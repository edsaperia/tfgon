// Ed's second design pass (2026-11-28): a dark page throughout, the directory
// map as a large version of the mark with black circles and desktop leader
// lines, and the old site's three member photos. Expected values are written
// by hand.
const { test, expect } = require('@playwright/test');
const { openPage } = require('./helpers');

const INK = 'rgb(30, 42, 54)'; // #1E2A36
const BLACK = 'rgb(0, 0, 0)';
const MEMBERS = {
  'tech-for-good-scotland': 'Tech for Good Scotland',
  'tech-for-good-cymru': 'Tech for Good Cymru',
  'tech4good-south-west': 'Tech4Good South West',
  'newspeak-house': 'Newspeak House',
  'techsoup-connect-england': 'TechSoup Connect England',
  'digital-leads-network': 'Digital Leads Network',
};
const EMERGING = {
  'north-west-england': 'North West England',
  'north-east-england': 'North East England',
};
const PAST = ['Tech for Good London / Global', 'Tech for Good Live', 'Tech for Good Oxford', 'Digital for Good', 'Tech for Good Exeter', 'Social Tech North East', 'NetSquared Midlands'];
const PHOTOS = ['img/members-street.jpg', 'img/members-table.jpg', 'img/member-flipchart.jpg'];

async function openEverything(page) {
  const closed = await page.locator('.fold-toggle[aria-expanded="false"]').evaluateAll((ts) => ts.map((t) => t.getAttribute('aria-controls')));
  for (const id of closed) {
    const toggle = page.locator(`.fold-toggle[aria-controls="${id}"]`);
    if (await toggle.getAttribute('aria-expanded') === 'false') await toggle.click();
  }
}

const isDesktop = (page) => page.viewportSize().width >= 832; // 52rem

test('the page background is dark throughout', async ({ page }) => {
  await openPage(page);
  await openEverything(page);
  expect(await page.locator('body').evaluate((b) => getComputedStyle(b).backgroundColor)).toBe(INK);
  // No element may paint a light background, except these, which carry ink text on neon yellow.
  const light = await page.locator('body *').evaluateAll((nodes) => nodes.filter((n) => {
    const m = getComputedStyle(n).backgroundColor.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/);
    if (!m || (m[4] !== undefined && Number(m[4]) === 0)) return false;
    const lum = (0.2126 * m[1] + 0.7152 * m[2] + 0.0722 * m[3]) / 255;
    return lum > 0.5 && !n.matches('.placeholder, .button-primary, .skip-link');
  }).map((n) => `${n.tagName}.${n.className}`));
  expect(light).toEqual([]);
  // and nothing makes the page scroll sideways
  expect(await page.evaluate(() => document.documentElement.scrollWidth)).toBeLessThanOrEqual(page.viewportSize().width);
});

test('every current community has exactly one black circle on the logo map, and no past community has one', async ({ page }) => {
  await openPage(page, '/#directory');
  // The map is the mark's low-poly shape, not a coastline.
  await expect(page.locator('#map svg.map-drawing polygon').first()).toBeAttached();
  expect(await page.locator('#map svg.map-drawing polygon').count()).toBeGreaterThan(20);
  await expect(page.locator('#map path.map-land')).toHaveCount(0);

  const circles = page.locator('#map .pin');
  await expect(circles).toHaveCount(Object.keys(MEMBERS).length + Object.keys(EMERGING).length);
  for (const [id, name] of Object.entries(MEMBERS)) {
    const c = page.locator(`#map .pin[data-community="${id}"]`);
    await expect(c, name).toHaveCount(1);
    expect(await c.evaluate((n) => getComputedStyle(n).backgroundColor), name).toBe(BLACK);
  }
  for (const [id, name] of Object.entries(EMERGING)) {
    const c = page.locator(`#map .pin[data-community="${id}"]`);
    await expect(c, name).toHaveCount(1);
    const style = await c.evaluate((n) => { const s = getComputedStyle(n); return [s.borderTopStyle, s.borderTopColor]; });
    expect(style, name).toEqual(['dashed', BLACK]);
  }
  const titles = await circles.evaluateAll((cs) => cs.map((c) => c.title));
  for (const name of PAST) expect(titles).not.toContain(name);
});

// The lines are redrawn on the next animation frame after anything moves;
// wait for that frame (and one more) rather than retrying.
const nextFrames = (page) => page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));

async function expectLinesCorrect(page) {
  await nextFrames(page);
  for (const [id, name] of Object.entries({ ...MEMBERS, ...EMERGING })) {
    const line = page.locator(`.leader-lines line[data-community="${id}"]`);
    await expect(line, name).toHaveCount(1);
    const geo = await page.evaluate((cid) => {
      const layout = document.querySelector('.directory-layout').getBoundingClientRect();
      const l = document.querySelector(`.leader-lines line[data-community="${cid}"]`);
      const pin = document.querySelector(`#map .pin[data-community="${cid}"]`).getBoundingClientRect();
      const head = document.querySelector(`#community-${cid} .fold-toggle`).getBoundingClientRect();
      const n = (a) => Number(l.getAttribute(a));
      return {
        start: [n('x1') + layout.left, n('y1') + layout.top], end: [n('x2') + layout.left, n('y2') + layout.top],
        pin: [pin.left + pin.width / 2, pin.top + pin.height / 2],
        head: { left: head.left, top: head.top, bottom: head.bottom },
      };
    }, id);
    expect(Math.abs(geo.start[0] - geo.pin[0]), `${name}: line starts at its circle (x)`).toBeLessThan(2);
    expect(Math.abs(geo.start[1] - geo.pin[1]), `${name}: line starts at its circle (y)`).toBeLessThan(2);
    expect(Math.abs(geo.end[0] - geo.head.left), `${name}: line ends at its entry's left edge`).toBeLessThan(2);
    expect(geo.end[1], `${name}: line ends beside its entry's heading`).toBeGreaterThanOrEqual(geo.head.top);
    expect(geo.end[1], `${name}: line ends beside its entry's heading`).toBeLessThanOrEqual(geo.head.bottom);
  }
}

test('on desktop each circle has a line to its entry, and on a phone none does', async ({ page }) => {
  await openPage(page, '/#directory');
  await expect(page.locator('.leader-lines'), 'the lines layer exists').toHaveCount(1);
  if (!isDesktop(page)) {
    await expect(page.locator('#map .pin').first()).toBeVisible();
    await expect(page.locator('.leader-lines')).toBeHidden();
    // and the circles still open their entries
    await page.locator('#map .pin[data-community="newspeak-house"]').click();
    await expect(page.locator('#community-newspeak-house-body')).toBeVisible();
    return;
  }
  await expect(page.locator('.leader-lines')).toBeVisible();
  await expectLinesCorrect(page);

  // Still correct after entries unfold and fold, which moves the entries below them.
  await page.locator('#map .pin[data-community="tech-for-good-scotland"]').click();
  await page.locator('#community-list').getByRole('button', { name: 'Tech4Good South West' }).click();
  await expect(page.locator('.leader-lines line[data-community="tech-for-good-scotland"]')).toHaveClass(/is-open/);
  await expectLinesCorrect(page);
  await page.locator('#community-list').getByRole('button', { name: 'Tech for Good Scotland' }).click();
  await expectLinesCorrect(page);

  // And after the window is resized.
  await page.setViewportSize({ width: 1000, height: 800 });
  await expectLinesCorrect(page);
  await page.setViewportSize({ width: 1440, height: 900 });
  await expectLinesCorrect(page);
  // Down to phone width: the lines go.
  await page.setViewportSize({ width: 600, height: 800 });
  await expect(page.locator('.leader-lines')).toBeHidden();
});

test('each member photo loads from the page itself, with alt text and a fixed size', async ({ page, baseURL }) => {
  await openPage(page);
  await openEverything(page);
  const imgs = page.locator('main img');
  const srcs = await imgs.evaluateAll((is) => is.map((i) => i.getAttribute('src')));
  expect(srcs.sort()).toEqual([...PHOTOS].sort());
  for (const src of PHOTOS) {
    const img = page.locator(`main img[src="${src}"]`);
    await img.scrollIntoViewIfNeeded();
    const info = await img.evaluate(async (i) => { await i.decode(); return {
      url: i.currentSrc, alt: i.getAttribute('alt'), w: i.getAttribute('width'), h: i.getAttribute('height'), natural: i.naturalWidth,
    }; });
    expect(new URL(info.url).origin, src).toBe(new URL(baseURL).origin);
    expect(info.natural, src).toBeGreaterThan(0);
    expect((info.alt || '').trim().length, `${src} alt text`).toBeGreaterThan(20);
    expect(Number(info.w), `${src} width`).toBeGreaterThan(0);
    expect(Number(info.h), `${src} height`).toBeGreaterThan(0);
  }
});
