const { test, expect } = require('@playwright/test');
const { openPage } = require('./helpers');

const FALLBACK = '[FALLBACK EMAIL — Ed to supply]';

async function fillValid(page) {
  await page.getByLabel('Your name').fill('Sam Example');
  await page.getByLabel('Email address').fill('sam@example.org');
  await page.getByLabel('Event link 1').fill('https://example.org/my-meetup');
}

// Serve a copy of config.js with an endpoint set, as the next build will.
async function setEndpoint(page, endpoint) {
  await page.route('**/js/config.js', (route) => route.fulfill({
    contentType: 'text/javascript',
    body: `window.TFGON_CONFIG = { applicationEndpoint: ${JSON.stringify(endpoint)}, fallbackEmail: ${JSON.stringify(FALLBACK)} };`,
  }));
}

test('the form has the three fields and a hidden trap field, and no location field', async ({ page }) => {
  await openPage(page, '/#join');
  const names = await page.locator('#apply-form input').evaluateAll((i) => i.map((n) => n.name));
  expect([...new Set(names)].sort()).toEqual(['email', 'eventLinks', 'name', 'website']);
  await expect(page.locator('#apply-website')).not.toBeInViewport();
  await page.getByRole('button', { name: 'Add another link' }).click();
  await expect(page.getByLabel('Event link 2')).toBeFocused();
});

test('with no endpoint set, the form says it has not sent and shows the fallback address', async ({ page }) => {
  const posts = [];
  page.on('request', (r) => { if (r.method() !== 'GET') posts.push(r.url()); });
  await openPage(page, '/#join');
  await fillValid(page);
  await page.getByRole('button', { name: 'Send application' }).click();
  const status = page.locator('#apply-status');
  await expect(status).toContainText('Your application has not been sent.');
  await expect(status).toContainText(FALLBACK);
  await expect(status).not.toContainText('Thank you');
  await expect(status).toHaveClass(/is-error/);
  expect(posts).toEqual([]);
});

test('an empty form shows what is missing and sends nothing', async ({ page }) => {
  await openPage(page, '/#join');
  await page.getByRole('button', { name: 'Send application' }).click();
  await expect(page.locator('.field-error')).toHaveText([
    /Enter your name/, /Enter an email address/, /Add a link/,
  ]);
  await expect(page.getByLabel('Your name')).toBeFocused();
  await expect(page.locator('#apply-status')).toBeEmpty();
});

test('when sending fails, the form says so and shows the fallback address', async ({ page }) => {
  await setEndpoint(page, '/test-endpoint');
  await page.route('**/test-endpoint', (route) => route.fulfill({ status: 500, body: 'error' }));
  await openPage(page, '/#join');
  await fillValid(page);
  await page.getByRole('button', { name: 'Send application' }).click();
  const status = page.locator('#apply-status');
  await expect(status).toContainText('Your application has not been sent. Sending failed.');
  await expect(status).toContainText(FALLBACK);
  await expect(status).not.toContainText('Thank you');
});

test('when sending works, the form posts the application as JSON and says thank you', async ({ page }) => {
  await setEndpoint(page, '/test-endpoint');
  let sent;
  await page.route('**/test-endpoint', (route) => {
    sent = { method: route.request().method(), type: route.request().headers()['content-type'], body: route.request().postDataJSON() };
    return route.fulfill({ status: 201, body: '{}' });
  });
  await openPage(page, '/#join');
  await fillValid(page);
  await page.getByRole('button', { name: 'Add another link' }).click();
  await page.getByLabel('Event link 2').fill('https://example.org/second');
  await page.getByRole('button', { name: 'Send application' }).click();
  await expect(page.locator('#apply-status')).toContainText('Thank you. Your application has been sent.');
  expect(sent).toEqual({
    method: 'POST',
    type: 'application/json',
    body: { name: 'Sam Example', email: 'sam@example.org', eventLinks: ['https://example.org/my-meetup', 'https://example.org/second'] },
  });
});

test('a filled trap field sends nothing and does not claim success', async ({ page }) => {
  await setEndpoint(page, '/test-endpoint');
  let called = false;
  await page.route('**/test-endpoint', (route) => { called = true; return route.fulfill({ status: 201 }); });
  await openPage(page, '/#join');
  await fillValid(page);
  await page.locator('#apply-website').fill('spam', { force: true });
  await page.getByRole('button', { name: 'Send application' }).click();
  await expect(page.locator('#apply-status')).toContainText('has not been sent');
  expect(called).toBe(false);
});
