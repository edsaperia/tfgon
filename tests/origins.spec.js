const { test, expect } = require('@playwright/test');
const { openPage } = require('./helpers');

test('the page makes no request to any other origin', async ({ page, baseURL }) => {
  const origin = new URL(baseURL).origin;
  const requests = [];
  page.on('request', (r) => requests.push(r.url()));
  await openPage(page);
  // Open everything and use the map and form, so lazy loads would show up too.
  const closed = await page.locator('.fold-toggle[aria-expanded="false"]').evaluateAll((ts) => ts.map((t) => t.getAttribute('aria-controls')));
  for (const id of closed) {
    const toggle = page.locator(`.fold-toggle[aria-controls="${id}"]`);
    if (await toggle.getAttribute('aria-expanded') === 'false') await toggle.click();
  }
  await page.locator('.pin').first().click();
  await page.getByRole('button', { name: 'Send application' }).click();
  await page.waitForLoadState('networkidle');

  expect(requests.length).toBeGreaterThan(0);
  const elsewhere = requests.filter((u) => !u.startsWith('data:') && new URL(u).origin !== origin);
  expect(elsewhere).toEqual([]);
});
