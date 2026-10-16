// Capture actual monitoring UIs after the API verification proves live data.
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import {execFileSync} from 'node:child_process';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
const output = 'artifacts/monitoring';
await mkdir(output, {recursive: true});
const secret = JSON.parse(execFileSync('kubectl', ['get','secret','monitoring-grafana','-n','monitoring','-o','json'], {encoding:'utf8'})).data;
const username = Buffer.from(secret['admin-user'], 'base64').toString();
const password = Buffer.from(secret['admin-password'], 'base64').toString();
const browser = await chromium.launch();
let page;
const browserErrors = [];
try {
  const verification = JSON.parse(await readFile(`${output}/verification.json`, 'utf8'));
  if (!verification.passed || verification.panels?.length !== 4 || !verification.datasource_uid) {
    throw new Error('Run check-monitoring.py to verify all four panels before capturing evidence');
  }
  const context = await browser.newContext({viewport:{width:1600,height:1100}});
  const login = await context.request.post('http://127.0.0.1:3001/login', {data:{user:username,password}});
  if (!login.ok()) throw new Error(`Grafana login failed: ${login.status()}`);
  page = await context.newPage();
  page.on('pageerror', error => browserErrors.push(error.message));
  const params = new URLSearchParams({orgId:'1', from:'now-15m', to:'now', timezone:'utc',
    'var-DS_PROMETHEUS':verification.datasource_uid});
  await page.goto(`http://127.0.0.1:3001/d/${verification.dashboard_uid}/lastbite?${params}`);
  for (const panel of verification.panels) {
    const chart = page.getByTestId(`timeseries-panel-${panel.id}`);
    await chart.waitFor({state:'visible', timeout:60000});
    // Grafana defers off-screen panels; reveal each before waiting for its plot.
    await chart.scrollIntoViewIfNeeded();
    await chart.getByTestId('uplot-main-div').locator('canvas').waitFor({state:'visible', timeout:90000});
    await chart.getByText('No data', {exact:true}).waitFor({state:'hidden', timeout:30000});
    console.log(`Rendered Grafana panel: ${panel.title}`);
  }
  if (await page.getByText('No data', {exact:true}).count()) {
    throw new Error('Grafana must display data in all four panels before evidence is captured');
  }
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${output}/grafana-dashboard.png`, fullPage:true});
  await page.goto('http://127.0.0.1:9090/targets?search=lastbite-backend');
  await page.getByText(/lastbite/).first().waitFor({timeout:60000});
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${output}/prometheus-targets.png`, fullPage:true});
  console.log('Saved live Prometheus and Grafana screenshots.');
} catch (error) {
  if (page) {
    await page.screenshot({path:`${output}/monitoring-failure.png`, fullPage:true}).catch(() => {});
    await writeFile(`${output}/monitoring-failure.txt`, [
      String(error), ...browserErrors, await page.locator('body').innerText().catch(() => ''),
    ].join('\n\n'));
  }
  throw error;
} finally { await browser.close(); }
