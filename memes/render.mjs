#!/usr/bin/env node
// Render a meme from a labels file onto the factory picture.
//
//   node memes/render.mjs memes/identity-01.json <output.jpg|output.png>
//
// Needs Playwright with Chromium (`npm i -g playwright && npx playwright install chromium`).
// It is not a site dependency, so it isn't in package.json. Fonts load from Google Fonts.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const [labelsPath, outPath] = process.argv.slice(2);
if (!labelsPath || !outPath) {
  console.error("usage: node memes/render.mjs <labels.json> <output.jpg|output.png>");
  process.exit(1);
}

const here = dirname(fileURLToPath(import.meta.url));
const repo = resolve(here, "..");
const labels = JSON.parse(readFileSync(labelsPath, "utf8"));
const base = resolve(repo, labels.base ?? "ai-assisted-sdlc/docs/blog/images/01-from-arm-assembly-to-ai-1.png");

const browser = await chromium.launch();
try {
  const page = await browser.newPage({ viewport: { width: 1222, height: 1287 }, deviceScaleFactor: 1 });
  await page.goto(pathToFileURL(join(here, "factory.html")).href);
  await page.evaluate(([L, src]) => window.fill(L, src), [labels, pathToFileURL(base).href]);
  await page.waitForLoadState("networkidle");
  await page.evaluate(() => document.fonts.ready);
  await page.waitForFunction(() => document.getElementById("base").complete);
  const type = outPath.endsWith(".png") ? "png" : "jpeg";
  await page.screenshot({ path: outPath, type, ...(type === "jpeg" ? { quality: 88 } : {}) });
  console.log(`wrote ${outPath}`);
} finally {
  await browser.close();
}
