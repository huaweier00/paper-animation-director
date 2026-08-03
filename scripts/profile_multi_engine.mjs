#!/usr/bin/env node

import { existsSync, createReadStream } from "node:fs";
import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { homedir } from "node:os";
import { extname, join, resolve, sep } from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[index + 1];
    if (!next || next.startsWith("--")) result[key] = true;
    else {
      result[key] = next;
      index += 1;
    }
  }
  return result;
}


async function chromePath(explicit) {
  for (const candidate of [
    explicit,
    process.env.PUPPETEER_EXECUTABLE_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  ].filter(Boolean)) {
    if (existsSync(candidate)) return candidate;
  }
  async function walk(directory, depth = 0) {
    if (depth > 7) return null;
    let entries;
    try {
      entries = await readdir(directory, { withFileTypes: true });
    } catch {
      return null;
    }
    for (const entry of entries) {
      const path = join(directory, entry.name);
      if (entry.isFile() && entry.name === "chrome-headless-shell") return path;
      if (entry.isDirectory()) {
        const found = await walk(path, depth + 1);
        if (found) return found;
      }
    }
    return null;
  }
  const cached = await walk(join(homedir(), ".cache", "hyperframes", "chrome"));
  if (cached) return cached;
  throw new Error("Chrome executable not found; pass --chrome");
}


function percentile(values, fraction) {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.min(sorted.length - 1, Math.ceil(sorted.length * fraction) - 1)];
}


async function compileProfileDocument(project) {
  let source = await readFile(join(project, "index.html"), "utf8");
  const hostPattern =
    /<([a-z][\w-]*)\b([^>]*\bdata-composition-src=(["'])([^"']+)\3[^>]*)>\s*<\/\1>/gi;
  const matches = [...source.matchAll(hostPattern)];
  for (const match of matches.reverse()) {
    const compositionPath = resolve(project, match[4]);
    if (compositionPath !== project && !compositionPath.startsWith(`${project}${sep}`)) {
      throw new Error(`composition escapes project root: ${match[4]}`);
    }
    const composition = await readFile(compositionPath, "utf8");
    const template = composition.match(/<template(?:\s[^>]*)?>([\s\S]*?)<\/template>/i);
    if (!template) throw new Error(`composition has no template root: ${match[4]}`);
    // Preserve the timing host used by hybrid-runtime to calculate local time,
    // but remove its id so the authored composition root remains the unique id.
    const hostAttributes = match[2].replace(/\s+id=(["'])[^"']*\1/i, "");
    const replacement = `<${match[1]}${hostAttributes}>${template[1]}</${match[1]}>`;
    source = `${source.slice(0, match.index)}${replacement}${source.slice(match.index + match[0].length)}`;
  }
  return source;
}


function serverFor(project, profileDocument) {
  const mime = {
    ".html": "text/html",
    ".js": "text/javascript",
    ".mjs": "text/javascript",
    ".json": "application/json",
    ".wasm": "application/wasm",
    ".riv": "application/octet-stream",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".mp3": "audio/mpeg",
  };
  const server = createServer(async (request, response) => {
    let pathname = decodeURIComponent((request.url || "/").split("?")[0]);
    if (pathname === "/__paper_profile__") {
      response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
      response.end(profileDocument);
      return;
    }
    if (pathname === "/") pathname = "/index.html";
    const target = resolve(project, `.${pathname}`);
    if (target !== project && !target.startsWith(`${project}${sep}`)) {
      response.writeHead(403).end();
      return;
    }
    try {
      const info = await stat(target);
      if (!info.isFile()) throw new Error("not file");
      response.writeHead(200, { "content-type": mime[extname(target)] || "application/octet-stream" });
      createReadStream(target).pipe(response);
    } catch {
      response.writeHead(404).end();
    }
  });
  return new Promise((resolveServer, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", () => resolveServer(server));
  });
}


async function main() {
  const args = parseArgs(process.argv.slice(2));
  const project = resolve(String(args.project || "."));
  const shotId = String(args["shot-id"] || "");
  if (!shotId) throw new Error("--shot-id is required");
  const budgetPath = resolve(String(args.budget || join(project, "shots", shotId, "performance-budget.json")));
  const budget = JSON.parse(await readFile(budgetPath, "utf8"));
  const plan = JSON.parse(await readFile(join(project, "shots", shotId, "engine-plan.json"), "utf8"));
  const selectedEmbedded = (plan.engines || []).filter((engine) =>
    ["rive", "pixijs-webgpu", "three-webgpu"].includes(engine)
  );
  const times = String(args.at || "0").split(",").map(Number).filter(Number.isFinite);
  if (times.length === 0) throw new Error("--at requires at least one finite timestamp");
  const packagePath = join(project, "node_modules", "puppeteer-core", "package.json");
  const requireFromProject = createRequire(pathToFileURL(packagePath));
  const puppeteer = requireFromProject("puppeteer-core");
  const executablePath = await chromePath(args.chrome);
  const profileDocument = await compileProfileDocument(project);
  const server = await serverFor(project, profileDocument);
  const address = server.address();
  const browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: [
      "--enable-unsafe-webgpu",
      "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding",
      "--autoplay-policy=no-user-gesture-required",
    ],
  });
  let raw;
  try {
    const page = await browser.newPage();
    const browserErrors = [];
    page.on("pageerror", (error) => browserErrors.push(String(error?.stack || error)));
    page.on("console", (message) => {
      if (message.type() === "error") browserErrors.push(message.text());
    });
    await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
    await page.goto(`http://127.0.0.1:${address.port}/__paper_profile__`, {
      waitUntil: "domcontentloaded",
    });
    try {
      await page.waitForFunction(
        () => window.__paperHybrid && typeof window.__paperHybrid.profileRenderers === "function",
        { timeout: 45000 },
      );
      await page.waitForFunction(
        (expected) => {
          const mounted = new Set(window.__paperHybrid.inventory().map((item) => item.engine));
          return expected.every((engine) => mounted.has(engine));
        },
        { timeout: 45000 },
        selectedEmbedded,
      );
    } catch (error) {
      const engineError = await page.evaluate(
        () => document.documentElement.dataset.hybridEngineError || null,
      );
      throw new Error(
        [
          error?.message || String(error),
          engineError ? `hybrid engine error: ${engineError}` : null,
          ...browserErrors,
        ].filter(Boolean).join("\n"),
      );
    }
    raw = await page.evaluate(({ times, iterations, warmups }) => {
      for (let index = 0; index < warmups; index += 1) {
        for (const time of times) window.__paperHybrid.profileRenderers(time);
      }
      const samples = [];
      for (let index = 0; index < iterations; index += 1) {
        for (const time of times) samples.push(window.__paperHybrid.profileRenderers(time));
      }
      return { inventory: window.__paperHybrid.inventory(), samples };
    }, {
      times,
      iterations: Number(budget.iterations || 5),
      warmups: Number(budget.warmup_iterations || 2),
    });
  } finally {
    await browser.close();
    await new Promise((resolveClosed) => server.close(resolveClosed));
  }
  const byEngine = new Map();
  const totals = [];
  for (const sample of raw.samples) {
    totals.push(sample.totalMilliseconds);
    for (const item of sample.samples) {
      const list = byEngine.get(item.engine) || [];
      list.push(item.milliseconds);
      byEngine.set(item.engine, list);
    }
  }
  const engines = Object.fromEntries(
    [...byEngine].map(([engine, values]) => [engine, {
      samples: values.length,
      average_ms: values.reduce((sum, value) => sum + value, 0) / values.length,
      p95_ms: percentile(values, 0.95),
      max_ms: Math.max(...values),
      budget_p95_ms: budget.engine_p95_ms?.[engine] ?? null,
    }]),
  );
  const errors = [];
  const mounted = new Set(raw.inventory.map((item) => item.engine));
  if (budget.missing_selected_renderer_blocks_release === true) {
    for (const engine of selectedEmbedded) {
      if (!mounted.has(engine)) errors.push(`selected renderer is not mounted: ${engine}`);
    }
  }
  if (raw.inventory.length > Number(budget.max_renderers || 4)) {
    errors.push(`renderer count ${raw.inventory.length} exceeds ${budget.max_renderers}`);
  }
  const totalP95 = percentile(totals, 0.95);
  if (totalP95 > Number(budget.total_p95_ms)) {
    errors.push(`total p95 ${totalP95.toFixed(3)}ms exceeds ${budget.total_p95_ms}ms`);
  }
  for (const [engine, metrics] of Object.entries(engines)) {
    if (metrics.budget_p95_ms != null && metrics.p95_ms > Number(metrics.budget_p95_ms)) {
      errors.push(`${engine} p95 ${metrics.p95_ms.toFixed(3)}ms exceeds ${metrics.budget_p95_ms}ms`);
    }
  }
  const report = {
    schema_version: 1,
    shot_id: shotId,
    budget: budgetPath,
    times,
    inventory: raw.inventory,
    total: {
      samples: totals.length,
      average_ms: totals.reduce((sum, value) => sum + value, 0) / totals.length,
      p95_ms: totalP95,
      max_ms: Math.max(...totals),
      budget_p95_ms: budget.total_p95_ms,
    },
    engines,
    errors,
    ok: errors.length === 0,
  };
  const output = `${JSON.stringify(report, null, 2)}\n`;
  const outputPath = resolve(String(args.output || join(project, "shots", shotId, "review", "engine-performance-report.json")));
  await writeFile(outputPath, output, "utf8");
  process.stdout.write(output);
  process.exitCode = report.ok ? 0 : 1;
}


main().catch((error) => {
  process.stderr.write(`${error?.stack || error}\n`);
  process.exitCode = 1;
});
