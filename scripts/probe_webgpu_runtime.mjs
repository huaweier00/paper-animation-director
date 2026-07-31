#!/usr/bin/env node

import { existsSync, createReadStream } from "node:fs";
import { readFile, readdir, stat, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { homedir } from "node:os";
import { extname, join, resolve, sep } from "node:path";
import { createRequire } from "node:module";
import { pathToFileURL } from "node:url";


const MIME = {
  ".html": "text/html",
  ".js": "text/javascript",
  ".mjs": "text/javascript",
  ".json": "application/json",
  ".wasm": "application/wasm",
};


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


async function findChrome(explicit) {
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


function serveProject(project) {
  const probeHtml = `<!doctype html><meta charset="utf-8"><canvas id="probe" width="64" height="64"></canvas>`;
  const server = createServer(async (request, response) => {
    if (request.url === "/__paper_webgpu_probe__") {
      response.writeHead(200, { "content-type": "text/html" });
      response.end(probeHtml);
      return;
    }
    const pathname = decodeURIComponent((request.url || "/").split("?")[0]);
    const target = resolve(project, `.${pathname}`);
    if (target !== project && !target.startsWith(`${project}${sep}`)) {
      response.writeHead(403).end();
      return;
    }
    try {
      const info = await stat(target);
      if (!info.isFile()) throw new Error("not file");
      response.writeHead(200, { "content-type": MIME[extname(target)] || "application/octet-stream" });
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
  const capability = typeof args.capability === "string"
    ? JSON.parse(await readFile(resolve(args.capability), "utf8"))
    : null;
  const packagePath = join(project, "node_modules", "puppeteer-core", "package.json");
  if (!existsSync(packagePath)) throw new Error("project-local puppeteer-core is required; run npm ci");
  const requireFromProject = createRequire(pathToFileURL(packagePath));
  const puppeteer = requireFromProject("puppeteer-core");
  const executablePath = await findChrome(args.chrome);
  const server = await serveProject(project);
  const address = server.address();
  const browser = await puppeteer.launch({
    executablePath,
    headless: true,
    args: [
      "--enable-unsafe-webgpu",
      "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding",
      "--no-first-run",
    ],
  });
  let payload;
  try {
    const page = await browser.newPage();
    await page.goto(`http://127.0.0.1:${address.port}/__paper_webgpu_probe__`, {
      waitUntil: "domcontentloaded",
    });
    payload = await page.evaluate(async () => {
      const navigatorGpu = Boolean(navigator.gpu);
      let adapterInfo = null;
      let adapterLimits = null;
      if (navigatorGpu) {
        const adapter = await navigator.gpu.requestAdapter();
        adapterInfo = adapter?.info ? { ...adapter.info } : null;
        adapterLimits = adapter?.limits
          ? Object.fromEntries(
              ["maxTextureDimension2D", "maxBindGroups"].map((key) => [key, Number(adapter.limits[key])]),
            )
          : null;
      }
      const THREE = await import("/node_modules/three/build/three.webgpu.js");
      const canvas = document.getElementById("probe");
      const renderer = new THREE.WebGPURenderer({ canvas, antialias: false, alpha: true });
      await renderer.init();
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, 1, 0.1, 10);
      camera.position.z = 2;
      scene.add(new THREE.Mesh(
        new THREE.PlaneGeometry(1, 1),
        new THREE.MeshBasicMaterial({ color: 0xc48b52 }),
      ));
      renderer.render(scene, camera);
      const backend = renderer.backend?.isWebGPUBackend === true ? "webgpu" : "webgl2";
      renderer.dispose();
      return { navigatorGpu, adapterInfo, adapterLimits, threeBackend: backend };
    });
  } finally {
    await browser.close();
    await new Promise((resolveClosed) => server.close(resolveClosed));
  }
  const policy = capability?.release_policy;
  const requiredBackend = String(
    args["required-backend"]
      || (policy?.webgpu_required === false ? "any" : capability?.required_backend)
      || "webgpu",
  );
  const backendOk = requiredBackend === "any"
    ? ["webgpu", "webgl2"].includes(payload.threeBackend)
    : payload.navigatorGpu && payload.threeBackend === requiredBackend;
  const errors = [];
  if (!backendOk) {
    errors.push(`required backend ${requiredBackend} is unavailable; actual ${payload.threeBackend}`);
  }
  if (payload.threeBackend === "webgpu") {
    for (const [name, minimum] of Object.entries(capability?.minimum_limits || {})) {
      const actual = Number(payload.adapterLimits?.[name]);
      if (!Number.isFinite(actual) || actual < Number(minimum)) {
        errors.push(`adapter limit ${name}=${actual} is below required ${minimum}`);
      }
    }
  }
  const report = {
    schema_version: 1,
    project,
    chrome: executablePath,
    required_backend: requiredBackend,
    minimum_limits: capability?.minimum_limits || {},
    ...payload,
    errors,
    ok: errors.length === 0,
  };
  const output = `${JSON.stringify(report, null, 2)}\n`;
  if (typeof args.output === "string") await writeFile(resolve(args.output), output, "utf8");
  process.stdout.write(output);
  process.exitCode = report.ok ? 0 : 1;
}


main().catch((error) => {
  process.stderr.write(`${error?.stack || error}\n`);
  process.exitCode = 1;
});
