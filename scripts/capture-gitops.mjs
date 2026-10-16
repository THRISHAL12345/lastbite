import {chromium} from '../frontend/node_modules/playwright/index.mjs';
import {execFileSync} from 'node:child_process';
const secret = JSON.parse(execFileSync('kubectl', ['get','secret','argocd-initial-admin-secret','-n','argocd','-o','json'], {encoding:'utf8'}));
const password = Buffer.from(secret.data.password, 'base64').toString();
const browser = await chromium.launch();
try {
  const context = await browser.newContext({ignoreHTTPSErrors:true,viewport:{width:1600,height:1100}});
  let token;
  for (let attempt=0; attempt<30; attempt++) {
    try {
      const response = await context.request.post('https://127.0.0.1:8443/api/v1/session', {data:{username:'admin',password}});
      if (response.ok()) { token=(await response.json()).token; break; }
    } catch {}
    await new Promise(resolve=>setTimeout(resolve,2000));
  }
  if (!token) throw new Error('Argo CD session could not be established');
  await context.addCookies([{name:'argocd.token',value:token,url:'https://127.0.0.1:8443',httpOnly:true,secure:true,sameSite:'Lax'}]);
  const page = await context.newPage();
  await page.goto('https://127.0.0.1:8443/applications/argocd/lastbite?view=tree');
  await page.getByText('Healthy', {exact:true}).first().waitFor({timeout:60000});
  await page.getByText('Synced', {exact:true}).first().waitFor({timeout:60000});
  await page.screenshot({path:'artifacts/gitops/argocd-synced-healthy.png',fullPage:true});
  console.log('Saved the live Argo CD Synced/Healthy application screenshot.');
} finally { await browser.close(); }
