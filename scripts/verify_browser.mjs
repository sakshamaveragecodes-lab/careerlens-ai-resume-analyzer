/** Optional local browser acceptance test. Requires npm package playwright.
 * Run: node scripts/verify_browser.mjs
 * TEST_PYTHON may point to a virtualenv Python; BROWSER_EXECUTABLE is optional.
 */
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';

const require = createRequire(import.meta.url);
const { chromium } = require('playwright');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const images = path.join(root, 'docs', 'screenshots');
const videoDir = path.join(root, 'docs', 'demo');
await mkdir(images, { recursive: true });
await mkdir(videoDir, { recursive: true });
const python = process.env.TEST_PYTHON || (process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python');
const url = 'http://127.0.0.1:8512';
const server = spawn(python, ['-m', 'streamlit', 'run', 'app.py', '--server.address=127.0.0.1', '--server.port=8512', '--server.headless=true'], { cwd: root, stdio: ['ignore', 'pipe', 'pipe'] });
let logs = '';
server.stdout.on('data', chunk => { logs += chunk; });
server.stderr.on('data', chunk => { logs += chunk; });
let browser;
let page;
const checks = [];
const errors = [];
function passed(name) { checks.push({ check: name, status: 'PASS' }); console.log('PASS: ' + name); }
const pause = ms => new Promise(resolve => setTimeout(resolve, ms));
try {
  let healthy = false;
  for (let i = 0; i < 120; i++) {
    try { healthy = (await fetch(url + '/_stcore/health')).ok; } catch { /* Startup in progress. */ }
    if (healthy) break;
    await pause(150);
  }
  assert.ok(healthy, 'Streamlit health endpoint did not become ready');
  passed('HTTP health endpoint');
  browser = await chromium.launch({ headless: true, executablePath: process.env.BROWSER_EXECUTABLE || undefined, args: process.env.BROWSER_SINGLE_PROCESS ? ['--single-process', '--no-zygote'] : [] });
  const context = await browser.newContext({ viewport: { width: 1440, height: 1000 }, recordVideo: { dir: videoDir, size: { width: 1440, height: 1000 } }, acceptDownloads: true, reducedMotion: 'reduce' });
  page = await context.newPage();
  page.on('pageerror', error => errors.push(error.message));
  await page.goto(url);
  await page.getByRole('button', { name: 'Analyze resume', exact: true }).waitFor();
  assert.ok(await page.getByRole('button', { name: 'Analyze resume', exact: true }).isDisabled());
  await pause(900);
  await page.screenshot({ path: path.join(images, '01_home.png'), fullPage: true });
  passed('Home renders with disabled Analyze before upload');

  await page.locator('input[type=file]').first().setInputFiles(path.join(root, 'sample_resumes', 'data_analyst.pdf'));
  await page.getByRole('button', { name: 'Analyze resume', exact: true }).click();
  await page.getByRole('heading', { name: 'Your strongest role matches', exact: true }).waitFor();
  assert.equal(await page.locator('.role-card').count(), 3);
  await page.getByRole('heading', { name: '02 / See where you stand', exact: true }).evaluate(el => el.scrollIntoView({ block: 'start' }));
  await pause(1000);
  await page.screenshot({ path: path.join(images, '02_overview.png'), fullPage: true });
  passed('PDF upload, analyze, top three roles and ranking chart');

  const targetCombo = page.getByRole('combobox', { name: 'Target job role' });
  await targetCombo.evaluate(el => el.scrollIntoView({ block: 'center' }));
  await targetCombo.click();
  await targetCombo.fill('Machine Learning Engineer');
  await page.getByRole('option', { name: 'Machine Learning Engineer', exact: true }).click();
  await page.getByRole('tab', { name: 'Skills & gaps', exact: true }).click();
  await page.getByText('A clear view of the gaps', { exact: true }).waitFor();
  await page.getByRole('tab', { name: 'Skills & gaps', exact: true }).evaluate(el => el.scrollIntoView({ block: 'start' }));
  await pause(1000);
  await page.screenshot({ path: path.join(images, '03_skills.png'), fullPage: true });
  passed('Target role change and required/preferred skill gaps');

  await page.getByRole('tab', { name: 'Learning plan', exact: true }).click();
  await page.getByText('Make the next step a small one.', { exact: true }).waitFor();
  await page.getByRole('tab', { name: 'Learning plan', exact: true }).evaluate(el => el.scrollIntoView({ block: 'start' }));
  assert.ok((await page.locator('body').innerText()).includes('Week 01'));
  await pause(900);
  await page.screenshot({ path: path.join(images, '04_roadmap.png'), fullPage: true });
  passed('Dependency-ordered learning plan renders');

  await page.getByRole('tab', { name: 'Resume insights', exact: true }).click();
  await page.getByText('Tell the story behind your skills.', { exact: true }).waitFor();
  passed('Resume feedback and section inspection');
  await pause(700);
  await page.getByRole('tab', { name: 'Custom job', exact: true }).click();
  await page.getByRole('textbox', { name: 'Job description', exact: true }).fill(await readFile(path.join(root, 'sample_resumes', 'custom_job.txt'), 'utf8'));
  await page.getByRole('button', { name: 'Compare with job description', exact: true }).click();
  await page.getByText('Custom job skill alignment', { exact: true }).waitFor();
  await page.getByRole('tab', { name: 'Custom job', exact: true }).evaluate(el => el.scrollIntoView({ block: 'start' }));
  await pause(1000);
  await page.screenshot({ path: path.join(images, '05_custom_job.png'), fullPage: true });
  passed('Pasted custom job description analysis');

  await page.locator('input[type=file]').nth(1).setInputFiles(path.join(root, 'sample_resumes', 'custom_job.txt'));
  await page.getByRole('button', { name: 'Compare with job description', exact: true }).click();
  await page.getByText('Custom job skill alignment', { exact: true }).waitFor();
  passed('Uploaded TXT job description analysis');

  await page.getByRole('tab', { name: 'Report', exact: true }).click();
  await page.getByText('Custom job description', { exact: true }).click();
  await page.getByRole('button', { name: 'Prepare PDF report', exact: true }).click();
  const downloadButton = page.getByRole('button', { name: 'Download analysis PDF', exact: true });
  await downloadButton.waitFor();
  const pendingDownload = page.waitForEvent('download');
  await downloadButton.click();
  const download = await pendingDownload;
  const downloadedPath = path.join(root, 'reports', 'Browser_Download_Analysis.pdf');
  await download.saveAs(downloadedPath);
  assert.ok((await readFile(downloadedPath)).subarray(0, 5).toString() === '%PDF-');
  passed('Custom-target PDF report download has valid signature');
  await pause(900);
  await page.screenshot({ path: path.join(images, '06_report.png'), fullPage: true });

  await page.locator('input[type=file]').first().setInputFiles(path.join(root, 'sample_resumes', 'ml_engineer.docx'));
  await page.getByText('ml_engineer.docx', { exact: true }).waitFor();
  await page.getByRole('heading', { name: 'From upload to a practical next step.', exact: true }).waitFor();
  await page.getByRole('button', { name: 'Analyze resume', exact: true }).click();
  await page.getByText(/Analyzing ml_engineer.docx/).waitFor();
  await page.getByRole('tab', { name: 'Overview', exact: true }).click();
  await page.getByRole('heading', { name: 'Your strongest role matches', exact: true }).waitFor();
  assert.ok((await page.locator('.role-card').first().innerText()).includes('Machine Learning Engineer'));
  passed('DOCX replacement clears previous results and analyzes successfully');

  await page.getByText('How it works', { exact: true }).click();
  await page.getByRole('heading', { name: 'Clarity behind every score.', exact: true }).waitFor();
  await pause(1000);
  await page.screenshot({ path: path.join(images, '07_methodology.png'), fullPage: true });
  passed('Methodology navigation');
  await page.getByText('Resume analyzer', { exact: true }).click();

  await page.locator('input[type=file]').first().setInputFiles({ name: 'broken.pdf', mimeType: 'application/pdf', buffer: Buffer.from('%PDF-1.7 broken') });
  await page.getByRole('heading', { name: 'From upload to a practical next step.', exact: true }).waitFor();
  await page.getByRole('button', { name: 'Analyze resume', exact: true }).click();
  await page.getByText(/document could not be read/i).waitFor();
  assert.equal(await page.locator('[data-testid=stException]').count(), 0);
  passed('Corrupted PDF displays recoverable error without a crash');

  await page.getByRole('button', { name: 'Clear session', exact: true }).click();
  await page.getByText('broken.pdf', { exact: true }).waitFor({ state: 'hidden' });
  await page.getByRole('button', { name: 'Analyze resume', exact: true }).and(page.locator(':disabled')).waitFor();
  assert.ok(await page.getByRole('button', { name: 'Analyze resume', exact: true }).isDisabled());
  assert.equal(await page.locator('.role-card').count(), 0);
  passed('Clear session resets upload, results and report');

  await page.setViewportSize({ width: 390, height: 844 });
  await pause(650);
  await page.screenshot({ path: path.join(images, '08_mobile_home.png'), fullPage: true });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 2));
  await page.getByRole('button', { name: 'Try Data Analyst', exact: true }).click();
  await page.getByRole('heading', { name: 'Your strongest role matches', exact: true }).waitFor();
  await page.getByRole('heading', { name: '02 / See where you stand', exact: true }).evaluate(el => el.scrollIntoView({ block: 'start' }));
  await pause(650);
  await page.screenshot({ path: path.join(images, '09_mobile_analysis.png'), fullPage: true });
  assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 2));
  passed('390px mobile home and analysis have no horizontal page overflow');
  assert.equal(errors.length, 0, errors.join('\n'));
  assert.equal(await page.locator('[data-testid=stException]').count(), 0);
  passed('No browser page errors or Streamlit exception overlays');

  const video = page.video();
  await context.close();
  await video.saveAs(path.join(videoDir, 'CareerLens_Demo.webm'));
  await video.delete();
  await writeFile(path.join(root, 'reports', 'browser_verification.json'), JSON.stringify({ checkedAt: new Date().toISOString(), browser: await browser.version(), viewport: '1440x1000 and 390x844', checks, errors }, null, 2));
} catch (error) {
  if (page) {
    await page.screenshot({ path: path.join(root, 'reports', 'browser_error.png') });
    await writeFile(path.join(root, 'reports', 'browser_error_dom.txt'), await page.locator('body').innerText());
  }
  await writeFile(path.join(root, 'reports', 'browser_failure.txt'), String(error) + '\n' + logs.slice(-3000));
  await writeFile(path.join(root, 'reports', 'browser_partial_checks.json'), JSON.stringify({ checks, errors }, null, 2));
  console.error(error.message);
  process.exitCode = 1;
} finally {
  if (browser) await browser.close();
  server.kill('SIGTERM');
}
