#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync } from "node:fs";
import { readFile, readdir, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


function parseArgs(argv) {
  const result = {};
  for (let index = 0; index < argv.length; index += 1) {
    const token = argv[index];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const value = argv[index + 1];
    if (!value || value.startsWith("--")) {
      result[key] = true;
    } else {
      result[key] = value;
      index += 1;
    }
  }
  return result;
}


function requireArg(args, name) {
  const value = args[name];
  if (typeof value !== "string" || value.trim() === "") {
    throw new Error(`--${name} is required`);
  }
  return resolve(value);
}


async function findChrome(explicit) {
  const candidates = [
    explicit,
    process.env.PUPPETEER_EXECUTABLE_PATH,
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (existsSync(candidate)) return candidate;
  }
  const cache = join(homedir(), ".cache", "hyperframes", "chrome");
  async function walk(directory, depth = 0) {
    if (depth > 6) return null;
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
  const cached = await walk(cache);
  if (cached) return cached;
  throw new Error("Chrome executable not found; pass --chrome");
}


async function withAssetServer(runtimePath, assetPath, callback) {
  const runtimeBytes = await readFile(runtimePath);
  const assetBytes = await readFile(assetPath);
  const html = `<!doctype html><meta charset="utf-8"><title>Rive inspection</title>`;
  const server = createServer((request, response) => {
    if (request.url === "/runtime.mjs") {
      response.writeHead(200, { "content-type": "text/javascript" });
      response.end(runtimeBytes);
    } else if (request.url === "/asset.riv") {
      response.writeHead(200, { "content-type": "application/octet-stream" });
      response.end(assetBytes);
    } else {
      response.writeHead(200, { "content-type": "text/html" });
      response.end(html);
    }
  });
  await new Promise((resolveReady, reject) => {
    server.once("error", reject);
    server.listen(0, "127.0.0.1", resolveReady);
  });
  const address = server.address();
  try {
    return await callback(`http://127.0.0.1:${address.port}`);
  } finally {
    await new Promise((resolveClosed) => server.close(resolveClosed));
  }
}


async function inspect() {
  const args = parseArgs(process.argv.slice(2));
  const runtimePath = requireArg(args, "runtime");
  const assetPath = requireArg(args, "asset");
  const bytes = await readFile(assetPath);
  const requireFromRuntime = createRequire(pathToFileURL(runtimePath));
  const puppeteer = requireFromRuntime("puppeteer-core");
  const executablePath = await findChrome(args.chrome);
  const browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: [
      "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding",
      "--no-first-run",
      "--no-default-browser-check",
    ],
  });
  let artboards;
  try {
    artboards = await withAssetServer(runtimePath, assetPath, async (origin) => {
      const page = await browser.newPage();
      await page.goto(origin, { waitUntil: "domcontentloaded" });
      return page.evaluate(async () => {
        const { default: RiveCanvas } = await import("/runtime.mjs");
        const rive = await RiveCanvas();
        const response = await fetch("/asset.riv");
        const file = await rive.load(new Uint8Array(await response.arrayBuffer()));
        if (!file) throw new Error("Rive could not load asset");
        const result = [];
        try {
          for (let artboardIndex = 0; artboardIndex < file.artboardCount(); artboardIndex += 1) {
            const artboard = file.artboardByIndex(artboardIndex);
            if (!artboard) continue;
            const animations = [];
            const stateMachines = [];
            try {
              for (let index = 0; index < artboard.animationCount(); index += 1) {
                const animation = artboard.animationByIndex(index);
                if (animation) animations.push(animation.name);
              }
              for (let index = 0; index < artboard.stateMachineCount(); index += 1) {
                const machine = artboard.stateMachineByIndex(index);
                if (machine) stateMachines.push(machine.name);
              }
              result.push({
                name: artboard.name,
                width: artboard.artboardWidth,
                height: artboard.artboardHeight,
                animations,
                state_machines: stateMachines,
              });
            } finally {
              artboard.delete?.();
            }
          }
        } finally {
          file.delete?.();
        }
        return result;
      });
    });
  } finally {
    await browser.close();
  }
  const report = {
    schema_version: 1,
    asset: assetPath,
    asset_bytes: bytes.length,
    asset_sha256: createHash("sha256").update(bytes).digest("hex"),
    runtime: runtimePath,
    browser: executablePath,
    artboards,
    ok: artboards.length > 0,
  };
  const serialized = `${JSON.stringify(report, null, 2)}\n`;
  if (typeof args.output === "string") {
    await writeFile(resolve(args.output), serialized, "utf8");
  }
  process.stdout.write(serialized);
  process.exitCode = report.ok ? 0 : 1;
}


inspect().catch((error) => {
  process.stderr.write(`${error?.stack || error}\n`);
  process.exitCode = 1;
});
