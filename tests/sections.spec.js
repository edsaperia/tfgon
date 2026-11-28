const { test, expect } = require('@playwright/test');
const { openPage } = require('./helpers');

// Written by hand: the four sections, in order, and the one open at the start.
const SECTIONS = [
  { id: 'intro', heading: 'About the network', openAtStart: true },
  { id: 'events', heading: 'TFGON events', openAtStart: false },
  { id: 'join', heading: 'Join the network', openAtStart: false },
  { id: 'directory', heading: 'Directory', openAtStart: false },
];

test('the four sections are on the page, in order', async ({ page }) => {
  await openPage(page);
  const ids = await page.locator('main > section.fold').evaluateAll((s) => s.map((n) => n.id));
  expect(ids).toEqual(SECTIONS.map((s) => s.id));
});

for (const section of SECTIONS) {
  test(`the ${section.id} section folds and unfolds`, async ({ page }) => {
    await openPage(page);
    const toggle = page.getByRole('button', { name: section.heading, exact: true });
    const body = page.locator(`#${section.id}-body`);

    await expect(toggle).toHaveAttribute('aria-expanded', String(section.openAtStart));
    await (section.openAtStart ? expect(body).toBeVisible() : expect(body).toBeHidden());

    await toggle.click();
    await expect(toggle).toHaveAttribute('aria-expanded', String(!section.openAtStart));
    await (section.openAtStart ? expect(body).toBeHidden() : expect(body).toBeVisible());

    // and back again, this time from the keyboard
    await toggle.focus();
    await page.keyboard.press('Enter');
    await expect(toggle).toHaveAttribute('aria-expanded', String(section.openAtStart));
    await (section.openAtStart ? expect(body).toBeVisible() : expect(body).toBeHidden());
  });

  test(`a #${section.id} link opens the ${section.id} section`, async ({ page }) => {
    await openPage(page, `/#${section.id}`);
    await expect(page.getByRole('button', { name: section.heading, exact: true })).toHaveAttribute('aria-expanded', 'true');
    await expect(page.locator(`#${section.id}-body`)).toBeVisible();
  });
}

test('a link within the page opens a closed section', async ({ page }) => {
  await openPage(page);
  await expect(page.locator('#join-body')).toBeHidden();
  await page.locator('#intro-body').getByRole('link', { name: 'Find out how to join' }).click();
  await expect(page.locator('#join-body')).toBeVisible();

  // Closing it and following the same link again (no hash change) opens it again.
  await page.getByRole('button', { name: 'Join the network', exact: true }).click();
  await expect(page.locator('#join-body')).toBeHidden();
  await page.locator('#intro-body').getByRole('link', { name: 'Find out how to join' }).click();
  await expect(page.locator('#join-body')).toBeVisible();
});
