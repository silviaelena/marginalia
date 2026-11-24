// Opens every lessons/*/demo/index.html in a headless browser and fails on any
// page error, console error or failed request.
import { chromium } from "playwright";
import { createServer } from "node:http";
import { readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const types = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg", ".wasm": "application/wasm" };

const server = createServer(async (req, res) => {
  let file = path.join(root, decodeURIComponent(new URL(req.url, "http://x").pathname));
  if (!file.startsWith(root)) return res.writeHead(403).end();
  try {
    if ((await stat(file)).isDirectory()) file = path.join(file, "index.html");
    res.writeHead(200, { "content-type": types[path.extname(file)] ?? "application/octet-stream" });
    res.end(await readFile(file));
  } catch {
    res.writeHead(404).end();
  }
});
await new Promise(resolve => server.listen(0, "127.0.0.1", resolve));
const base = `http://127.0.0.1:${server.address().port}`;

const demos = [];
for (const lesson of (await readdir(path.join(root, "lessons"))).sort()) {
  if (lesson.startsWith("_")) continue;
  try { await stat(path.join(root, "lessons", lesson, "demo", "index.html")); demos.push(lesson); }
  catch { console.error(`✗ ${lesson}: missing demo/index.html`); process.exitCode = 1; }
}

const browser = await chromium.launch();
for (const lesson of demos) {
  const page = await browser.newPage();
  const problems = [];
  page.on("pageerror", e => problems.push(`page error: ${e.message}`));
  page.on("console", m => m.type() === "error" && problems.push(`console error: ${m.text()}`));
  page.on("requestfailed", r => problems.push(`request failed: ${r.url()}`));
  page.on("response", r => r.status() >= 400 && problems.push(`HTTP ${r.status()}: ${r.url()}`));
  await page.goto(`${base}/lessons/${lesson}/demo/`, { waitUntil: "load" });
  await page.waitForTimeout(1000);
  if (problems.length) {
    process.exitCode = 1;
    console.error(`✗ ${lesson}\n  ${problems.join("\n  ")}`);
  } else {
    console.log(`✓ ${lesson}`);
  }
  await page.close();
}
await browser.close();
server.close();
