import { test, expect } from 'playwright/test';

// These tests require the real Compose/Kubernetes demo stack; no API mocks.
test('ticket lifecycle persists across reloads and mobile layout', async ({page, request}, testInfo) => {
  const title = `Browser evidence ${Date.now()}`;
  let ticketId;
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  try {
    await page.goto('/');
    await expect(page.getByRole('heading', {name: 'Keep support moving.'})).toBeVisible();
    await page.getByRole('button', {name: 'New ticket', exact: true}).click();
    const dialog = page.getByRole('dialog');
    await dialog.getByLabel('Subject', {exact:true}).fill(title);
    await dialog.getByLabel('Description', {exact:true}).fill('Disposable ticket created by the real-browser integration suite.');
    await dialog.getByLabel('Requester', {exact:true}).fill('Browser test');
    await dialog.getByLabel('Assigned to', {exact:true}).fill('Support team');
    await dialog.getByRole('combobox', {name:'Priority', exact:true}).selectOption('HIGH');
    const created = page.waitForResponse(r => r.url().endsWith('/api/tickets') && r.request().method()==='POST');
    await dialog.getByRole('button', {name:'Create ticket', exact:true}).click();
    const response = await created;
    expect(response.status()).toBe(201);
    ticketId = (await response.json()).id;
    await expect(dialog).toHaveCount(0);
    await page.reload();
    await page.getByRole('textbox', {name:'Search by subject or requester'}).fill(title);
    const ticket = page.locator('.ticket-link').filter({hasText:title});
    await expect(ticket).toBeVisible();
    await page.screenshot({path:testInfo.outputPath('desktop-queue.png'),fullPage:true});
    await ticket.click();
    await page.getByRole('button', {name:'Start working',exact:true}).click();
    await expect(page.getByRole('button', {name:'Mark resolved',exact:true})).toBeVisible();
    await page.getByRole('textbox', {name:'Add a note',exact:true}).fill('Checked the connection and confirmed access.');
    await page.getByRole('button', {name:'Add note',exact:true}).click();
    await expect(page.locator('.history')).toContainText('Checked the connection and confirmed access.');
    await page.getByRole('button', {name:'Mark resolved',exact:true}).click();
    await expect(page.getByRole('button', {name:'Reopen ticket',exact:true})).toBeVisible();
    await page.screenshot({path:testInfo.outputPath('resolved-ticket.png'),fullPage:true});
    await page.getByRole('button', {name:'Reopen ticket',exact:true}).click();
    await expect(page.getByRole('button', {name:'Start working',exact:true})).toBeVisible();
    await page.getByRole('button', {name:'Close dialog',exact:true}).click();
    await page.setViewportSize({width:390,height:844});
    await page.screenshot({path:testInfo.outputPath('mobile-queue.png'),fullPage:true});
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
    await page.locator('.ticket-link').filter({hasText:title}).click();
    page.once('dialog', dialog => dialog.accept());
    await page.getByRole('button', {name:'Delete',exact:true}).click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    expect((await request.get(`/api/tickets/${ticketId}`)).status()).toBe(404);
    expect(errors).toEqual([]);
  } finally {
    if (ticketId) await request.delete(`/api/tickets/${ticketId}`);
  }
});
