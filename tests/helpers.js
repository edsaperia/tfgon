// Open the page and wait until its data has been drawn.
async function openPage(page, path = '/') {
  await page.goto(path);
  await page.locator('html[data-ready]').waitFor({ state: 'attached' });
}
module.exports = { openPage };
