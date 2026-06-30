import { spawn } from 'node:child_process';
import { createRequire } from 'node:module';
import { mkdir, rm, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const requireFromWeb = createRequire(path.join(ROOT, 'web', 'package.json'));
const { chromium } = requireFromWeb('@playwright/test');

const args = parseArgs(process.argv.slice(2));
const outputDir = path.resolve(args.out);
const apiUrl = process.env.ALGORITHM_GIF_API_URL ?? 'http://127.0.0.1:8000';
const baseUrl = args.baseUrl || 'http://localhost:5173';
const startedProcesses = [];

try {
  await ensureServers(apiUrl, baseUrl, Boolean(args.baseUrl));
  const payload = await fetchJson(`${apiUrl}/api/algorithm-groups`);
  const algorithms = flattenAlgorithms(payload).filter((item) => args.only.length === 0 || args.only.includes(item.alias));
  const missing = args.only.filter((alias) => !algorithms.some((item) => item.alias === alias));
  if (missing.length) throw new Error(`Aliases missing from web API: ${missing.join(', ')}`);

  await rm(outputDir, { recursive: true, force: true });
  await mkdir(outputDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 }, deviceScaleFactor: 1 });
  await page.goto(baseUrl, { waitUntil: 'networkidle' });
  await page.locator('div.relative button[aria-haspopup="listbox"]').first().waitFor({ state: 'visible' });

  const manifest = [];
  for (const info of algorithms) {
    await selectOption(page, 'Nhóm thuật toán', info.groupVi);
    await selectOption(page, 'Thuật toán', info.name);

    const gifImage = page.locator(`[data-testid="algorithm-gif"][data-algorithm="${info.alias}"]`);
    await gifImage.waitFor({ state: 'visible' });

    const runButton = page.getByRole('button', { name: 'Chạy thuật toán' });
    await runButton.click();
    await page.locator(`[data-testid="algorithm-analysis"][data-algorithm="${info.alias}"]`).waitFor({ state: 'visible', timeout: 30_000 });

    const tracePanel = page.locator(`[data-testid="algorithm-trace"][data-algorithm="${info.alias}"]`);
    await tracePanel.waitFor({ state: 'visible' });
    await tracePanel.scrollIntoViewIfNeeded();
    const rows = tracePanel.locator('tr[data-trace-step]');
    const frameCount = Math.min(await rows.count(), 8);
    if (frameCount === 0) throw new Error(`No trace rows rendered for ${info.alias}`);

    const algorithmDir = path.join(outputDir, info.alias);
    await mkdir(algorithmDir, { recursive: true });
    const frames = [];
    for (let index = 0; index < frameCount; index += 1) {
      const row = rows.nth(index);
      const className = (await row.getAttribute('class')) ?? '';
      if (!className.includes('bg-evidence/20')) await row.click();
      await tracePanel.getByText('Step detail').waitFor({ state: 'visible' });
      const filename = `frame-${String(index + 1).padStart(2, '0')}.png`;
      await tracePanel.screenshot({ path: path.join(algorithmDir, filename), animations: 'disabled' });
      frames.push(`${info.alias}/${filename}`);
    }

    manifest.push({
      alias: info.alias,
      algorithm: info.alias,
      display: info.name,
      group: info.group,
      frames,
      source: 'web-ui-playwright',
    });
    process.stdout.write(`captured ${info.alias}: ${frames.length} frame(s)\n`);
  }

  await browser.close();
  await writeFile(path.join(outputDir, 'capture-manifest.json'), JSON.stringify(manifest, null, 2), 'utf8');
} finally {
  await stopStartedProcesses();
}

function parseArgs(argv) {
  const parsed = { out: '', baseUrl: '', only: [] };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--out') parsed.out = argv[++index];
    else if (value === '--base-url') parsed.baseUrl = argv[++index];
    else if (value === '--only') parsed.only = argv.slice(index + 1);
  }
  if (!parsed.out) throw new Error('--out is required');
  return parsed;
}

function flattenAlgorithms(payload) {
  const groupLabels = new Map(payload.groups.map((group) => [group.name, group.name_vi]));
  return Object.entries(payload.algorithms_by_group).flatMap(([group, items]) =>
    items.map((item) => ({ ...item, group, groupVi: groupLabels.get(group) ?? group })),
  );
}

async function selectOption(page, label, optionName) {
  const wrapper = page.locator(`[data-select-label="${label}"]`);
  const button = wrapper.locator('button[aria-haspopup="listbox"]');
  await button.click();
  await page.getByRole('option').filter({ hasText: optionName }).first().click();
  await page.waitForTimeout(100);
}

async function ensureServers(api, web, reuseOnly) {
  if (!(await isReachable(`${api}/healthz`))) {
    if (reuseOnly) throw new Error(`Backend is not reachable at ${api}`);
    const backend = spawn(
      process.env.PYTHON_EXECUTABLE ?? 'python',
      ['-m', 'uvicorn', 'main:app', '--app-dir', 'api', '--host', '127.0.0.1', '--port', '8000'],
      {
        cwd: ROOT,
        env: { ...process.env, CORS_ORIGINS: 'http://localhost:5173,http://127.0.0.1:5173' },
        stdio: 'ignore',
        windowsHide: true,
      },
    );
    startedProcesses.push(backend);
  }
  await waitFor(`${api}/healthz`, 30_000);

  if (!(await isReachable(web))) {
    if (reuseOnly) throw new Error(`Web is not reachable at ${web}`);
    const viteEntry = path.join(ROOT, 'web', 'node_modules', 'vite', 'bin', 'vite.js');
    const frontend = spawn(process.execPath, [viteEntry, '--host', '127.0.0.1', '--port', '5173'], {
      cwd: path.join(ROOT, 'web'),
      env: { ...process.env, VITE_API_URL: api },
      stdio: 'ignore',
      windowsHide: true,
    });
    startedProcesses.push(frontend);
  }
  await waitFor(web, 30_000);
}

async function fetchJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`${url} returned HTTP ${response.status}`);
  return response.json();
}

async function isReachable(url) {
  try {
    const response = await fetch(url);
    return response.ok;
  } catch {
    return false;
  }
}

async function waitFor(url, timeoutMs) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (await isReachable(url)) return;
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error(`Timed out waiting for ${url}`);
}

async function stopStartedProcesses() {
  for (const child of startedProcesses.reverse()) {
    if (!child.killed) child.kill();
  }
  await new Promise((resolve) => setTimeout(resolve, 250));
}
