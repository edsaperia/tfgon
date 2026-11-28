// Screenshots of the design sheet, one per section, at desktop width and deviceScaleFactor 2.
// Run from the repository root: node design/tools/shoot.js
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 2 });
  const outside = [];
  p.on("request", (r) => { if (!r.url().startsWith("file:")) outside.push(r.url()); });
  p.on("console", (m) => console.log("console:", m.text()));
  p.on("pageerror", (e) => console.log("pageerror:", e.message));
  await p.goto("file://" + path.resolve(__dirname, "../index.html"));
  await p.evaluate(() => document.fonts.ready);
  await p.waitForTimeout(300); // let the canvas icons draw (images load asynchronously)
  const fonts = await p.evaluate(() => [...document.fonts].filter((f) => f.status === "loaded").map((f) => `${f.family} ${f.weight}`));
  console.log("fonts loaded:", fonts.join(", "));
  const dir = path.resolve(__dirname, "../screenshots");
  for (const id of ["marks2", "marks", "colours-neon", "colours", "type"]) {
    await p.locator("#" + id).screenshot({ path: `${dir}/${id}.png` });
  }
  console.log("requests outside the page's own files:", outside.length ? outside : "none");
  await b.close();
})();
