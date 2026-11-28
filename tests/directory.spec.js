const { test, expect } = require('@playwright/test');
const { readFileSync } = require('node:fs');
const path = require('node:path');
const { openPage } = require('./helpers');

// Written by hand, not read from the data file, so a missing or stray
// community in the file fails these tests.
const ON_MAP = [
  'Tech for Good Scotland',
  'Tech for Good Cymru',
  'Tech4Good South West',
  'Newspeak House',
  'TechSoup Connect England',
  'Digital Leads Network',
  'North West England',
  'North East England',
];
const PAST = [
  'Tech for Good London / Global',
  'Tech for Good Live',
  'Tech for Good Oxford',
  'Digital for Good',
  'Tech for Good Exeter',
  'Social Tech North East',
  'NetSquared Midlands',
];

const data = JSON.parse(readFileSync(path.join(__dirname, '..', 'docs', 'data', 'communities.json'), 'utf8'));

test('the data file holds exactly the expected current and past communities', () => {
  const current = data.communities.filter((c) => c.status !== 'past').map((c) => c.name);
  const past = data.communities.filter((c) => c.status === 'past').map((c) => c.name);
  expect(current.sort()).toEqual([...ON_MAP].sort());
  expect(past.sort()).toEqual([...PAST].sort());
});

test('no organiser has an email address or photo yet (consent not given)', () => {
  for (const c of data.communities) {
    for (const o of c.organisers) {
      expect(o.email, `${o.name}'s email`).toBe('');
      expect(o.photo, `${o.name}'s photo`).toBe('');
    }
  }
});

test('every current community has exactly one pin and one entry', async ({ page }) => {
  await openPage(page, '/#directory');
  await expect(page.locator('.pin')).toHaveCount(ON_MAP.length);
  await expect(page.locator('#community-list > .community')).toHaveCount(ON_MAP.length);
  for (const name of ON_MAP) {
    await expect(page.locator('.pin').filter({ has: page.locator(`xpath=self::*[@title=${JSON.stringify(name)}]`) })).toHaveCount(1);
    await expect(page.locator('#community-list .community-name').getByText(name, { exact: true })).toHaveCount(1);
  }
});

test('no past community has a pin, and each is in the folded list', async ({ page }) => {
  await openPage(page, '/#directory');
  const titles = await page.locator('.pin').evaluateAll((pins) => pins.map((p) => p.title));
  for (const name of PAST) expect(titles).not.toContain(name);
  const pastBody = page.locator('#past-body');
  await expect(pastBody).toBeHidden();
  await page.getByRole('button', { name: 'Communities that helped build the network' }).click();
  await expect(pastBody).toBeVisible();
  await expect(page.locator('#past-list .past-item h4')).toHaveText(PAST);
});

for (const name of ON_MAP) {
  test(`clicking the pin for ${name} opens its entry`, async ({ page }) => {
    await openPage(page, '/#directory');
    const pin = page.locator(`.pin[title=${JSON.stringify(name)}]`);
    await pin.click();
    const entry = page.locator('#community-list > .community').filter({ has: page.locator('.community-name').getByText(name, { exact: true }) });
    await expect(entry.locator('.fold-toggle')).toHaveAttribute('aria-expanded', 'true');
    await expect(entry.locator('.fold-body')).toBeVisible();
    await expect(entry.locator('.fold-toggle')).toBeFocused();
    await expect(pin).toHaveAttribute('aria-expanded', 'true');
    // Only that entry is open.
    await expect(page.locator('#community-list .fold-toggle[aria-expanded="true"]')).toHaveCount(1);
  });
}

test('clicking a name in the list opens that entry', async ({ page }) => {
  await openPage(page, '/#directory');
  await page.locator('#community-list').getByRole('button', { name: 'Newspeak House' }).click();
  const body = page.locator('#community-newspeak-house-body');
  await expect(body).toBeVisible();
  await expect(body).toContainText('Edward Saperia');
  await expect(body.getByRole('link', { name: 'newspeak.house/events' })).toHaveAttribute('href', 'https://newspeak.house/events');
});
