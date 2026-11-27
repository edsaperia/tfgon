const { test, expect } = require('@playwright/test');
const { readdirSync, readFileSync, statSync } = require('node:fs');
const path = require('node:path');

// Anything shaped like a UK phone number: 0 or +44 (optionally (0)), then
// 9 or 10 more digits, with optional spaces, dots or hyphens between them.
const UK_PHONE = /(?:\+\s*44\s*(?:\(0\)\s*)?|\b0)(?:[\s.-]?\d){9,10}\b/g;

function files(dir) {
  return readdirSync(dir).flatMap((name) => {
    const full = path.join(dir, name);
    return statSync(full).isDirectory() ? files(full) : [full];
  });
}

test('the pattern catches the usual ways of writing a UK number', () => {
  for (const sample of ['020 7946 0958', '07700 900123', '+44 7700 900123', '+44 (0)20 7946 0958', '01632-960-123', '0117.496.0123']) {
    expect(sample.match(UK_PHONE), sample).not.toBeNull();
  }
  for (const sample of ['M12.3 45.6L305.1 208.7', '2026-11-27', '12:00–13:00', '£4,500']) {
    expect(sample.match(UK_PHONE), sample).toBeNull();
  }
});

test('no file under /docs contains anything shaped like a UK phone number', () => {
  const docs = path.join(__dirname, '..', 'docs');
  const checked = files(docs);
  expect(checked.length).toBeGreaterThan(0);
  const found = [];
  for (const file of checked) {
    const text = readFileSync(file, 'latin1');
    for (const match of text.match(UK_PHONE) || []) found.push(`${path.relative(docs, file)}: ${match}`);
  }
  expect(found).toEqual([]);
});
