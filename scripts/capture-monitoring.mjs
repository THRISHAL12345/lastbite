// Capture actual monitoring UIs after the API verification proves live data.
import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import {execFileSync} from 'node:child_process';
import {mkdir} from 'node:fs/promises';
const output = 'artifacts/monitoring';
await mkdir(output, {recursive: true});
const secret = JSON.parse(execFileSync('kubectl', ['get','secret','monitoring-grafana','-n','monitoring','-o','json'], {encoding:'utf8'})).data;
const username = Buffer.from(secret['admin-user'], 'base64').toString();
const password = Buffer.from(secret['admin-password'], 'base64').toString();
const browser = await chromium.launch();
try {
  const context = await browser.newContext({viewport:{width:1600,height:1100}});
  const login = await context.request.post('http://127.0.0.1:3001/login', {data:{user:username,password}});
  if (!login.ok()) throw new Error(`Grafana login failed: ${login.status()}`);
  const page = await context.newPage();
  await page.goto('http://127.0.0.1:3001/d/relaydesk-health/relaydesk?orgId=1&from=now-15m&to=now&timezone=utc');
  await page.getByText('Requests per second', {exact:true}).waitFor({timeout:60000});
  // A fresh cluster can show replica data before the request-rate range query
  // has enough samples. Let the dashboard's 15-second refresh fill all panels.
  await page.getByRole('button', {name:'Cancel',exact:true}).waitFor({state:'hidden',timeout:90000});
  await page.locator('.uplot canvas').nth(3).waitFor({state:'visible',timeout:180000});
  if (await page.getByText('No data', {exact:true}).count()) {
    throw new Error('Grafana must display data in all four panels before evidence is captured');
  }
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${output}/grafana-dashboard.png`, fullPage:true});
  await page.goto('http://127.0.0.1:9090/targets?search=relaydesk-backend');
  await page.getByText(/relaydesk/).first().waitFor({timeout:60000});
  await page.waitForTimeout(2000);
  await page.screenshot({path:`${output}/prometheus-targets.png`, fullPage:true});
  console.log('Saved live Prometheus and Grafana screenshots.');
} finally { await browser.close(); }
