const { test, expect } = require('@playwright/test');
const { openPage } = require('./helpers');

test('events are listed upcoming first, then past, on 27 November 2026', async ({ page }) => {
  await page.clock.setFixedTime(new Date('2026-11-27T12:00:00'));
  await openPage(page, '/#events');
  const upcoming = page.locator('#events-upcoming .event');
  const past = page.locator('#events-past .event');
  // Written by hand from the brief.
  await expect(upcoming).toHaveText([
    /Wednesday 3 March 2027.*Online quarterly meeting.*12:00–13:00/,
    /2027, dates to be confirmed.*National retreat 2027.*Bristol/,
  ]);
  await expect(past).toHaveText([
    /Wednesday 25 November 2026.*Online quarterly meeting/,
    /Wednesday 2 September 2026.*Online quarterly meeting/,
    /18–19 May 2026.*National retreat.*Newcastle.*statement of purpose/,
  ]);
});
