import { test, expect } from 'playwright/test';

test('publish, reserve, cancel and collect a meal box with PostgreSQL persistence',async({page,request},testInfo)=>{
  const title=`Browser supper ${Date.now()}`;
  let listingId;
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  try {
  await page.goto('/');
  await expect(page.getByRole('heading',{name:'Too good to say goodbye.'})).toBeVisible();
  await page.getByRole('button',{name:'Kitchen desk',exact:true}).click();
  await page.getByRole('button',{name:'New meal box',exact:true}).click();
  const dialog=page.getByRole('dialog');
  await dialog.getByLabel('Box name',{exact:true}).fill(title);
  await dialog.getByLabel('Kitchen name',{exact:true}).fill('Browser Kitchen');
  await dialog.getByLabel("What's inside?",{exact:true}).fill('A vegetarian supper for the live browser test.');
  await dialog.getByLabel('Pickup address',{exact:true}).fill('12 Test Lane, Hyderabad');
  await dialog.getByLabel('Total boxes',{exact:true}).fill('5');
  const created=page.waitForResponse(r=>r.url().endsWith('/api/listings')&&r.request().method()==='POST');
  await dialog.getByRole('button',{name:'Publish meal box',exact:true}).click();
  const response=await created;expect(response.status()).toBe(201);listingId=(await response.json()).id;
  await expect(dialog).toHaveCount(0);
  await page.reload();
  await page.getByRole('textbox',{name:'Search meals or kitchens'}).fill(title);
  const card=page.locator('.meal-card').filter({hasText:title});
  await expect(card).toBeVisible();
  await card.getByRole('button',{name:'Rescue box',exact:true}).click();
  await dialog.getByLabel('Your name',{exact:true}).fill('Browser Guest');
  await dialog.getByLabel('Boxes',{exact:true}).fill('2');
  const reserved=page.waitForResponse(r=>r.url().endsWith(`/listings/${listingId}/reservations`)&&r.request().method()==='POST');
  await dialog.getByRole('button',{name:'Confirm reservation',exact:true}).click();
  const reservation=(await (await reserved).json());
  await expect(dialog).toHaveCount(0);
  let reservationCard=page.locator('.reservation-card').filter({hasText:title});
  await expect(reservationCard).toContainText(reservation.pickup_code);
  await page.reload();
  await page.getByRole('button',{name:'Reservations',exact:true}).click();
  await expect(reservationCard).toContainText(reservation.pickup_code);
  page.once('dialog',d=>d.accept());
  await reservationCard.getByRole('button',{name:'Cancel reservation',exact:true}).click();
  await expect(reservationCard).toContainText('Cancelled');
  expect((await (await request.get(`/api/listings/${listingId}`)).json()).quantity_available).toBe(5);
  await page.getByRole('button',{name:'Explore boxes',exact:true}).first().click();
  await page.getByRole('textbox',{name:'Search meals or kitchens'}).fill(title);
  await card.getByRole('button',{name:'Rescue box',exact:true}).click();
  await dialog.getByLabel('Your name',{exact:true}).fill('Browser Guest');
  const again=page.waitForResponse(r=>r.url().endsWith(`/listings/${listingId}/reservations`)&&r.request().method()==='POST');
  await dialog.getByRole('button',{name:'Confirm reservation',exact:true}).click();
  const pickup=(await (await again).json());
  reservationCard=page.locator('.reservation-card').filter({hasText:pickup.pickup_code});
  await reservationCard.getByRole('button',{name:'Confirm handover',exact:true}).click();
  await dialog.getByLabel('Pickup code',{exact:true}).fill('WRONG');
  await dialog.getByRole('button',{name:'Confirm pickup',exact:true}).click();
  await expect(dialog.getByRole('alert')).toContainText('does not match');
  await dialog.getByLabel('Pickup code',{exact:true}).fill(pickup.pickup_code);
  await dialog.getByRole('button',{name:'Confirm pickup',exact:true}).click();
  await expect(dialog).toHaveCount(0);
  await expect(reservationCard).toContainText('Picked up');
  await page.screenshot({path:testInfo.outputPath('pickup-confirmed.png'),fullPage:true});
  await page.getByRole('button',{name:'Kitchen desk',exact:true}).click();
  await page.getByRole('textbox',{name:'Search meals or kitchens'}).fill(title);
  await card.getByRole('button',{name:'Edit box',exact:true}).click();
  await dialog.getByLabel('Total boxes',{exact:true}).fill('6');
  await dialog.getByRole('button',{name:'Save changes',exact:true}).click();
  await expect(dialog).toHaveCount(0);
  await expect(card).toContainText('5 left to rescue');
  await page.getByRole('button',{name:'Explore boxes',exact:true}).first().click();
  await expect(page.locator('.meal-card').first()).toBeVisible();
  await page.screenshot({path:testInfo.outputPath('desktop-marketplace.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  await page.screenshot({path:testInfo.outputPath('mobile-marketplace.png'),fullPage:true});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth)).toBe(true);
  await page.getByRole('button',{name:'Reservations',exact:true}).click();
  await expect(page.getByRole('heading',{name:'Your next good deed.'})).toBeVisible();
  expect(errors).toEqual([]);
  } finally {
    if(listingId) {
      const response=await request.get(`/api/listings/${listingId}`);
      if(response.ok()) {
        const item=await response.json();
        const {writeFields}=await import('../src/api.js');
        await request.put(`/api/listings/${listingId}`,{data:{...writeFields(item),status:'PAUSED'}});
      }
    }
  }
});

test('kitchen can edit and delete a listing without reservation history',async({page,request})=>{
  const now=Date.now();
  const data={title:`Disposable bakery ${now}`,restaurant:'Test bakery',category:'BAKERY',dietary:'VEGETARIAN',address:'Demo street',price_paise:5000,original_price_paise:15000,quantity_total:2,pickup_start:new Date(now-60000).toISOString(),pickup_end:new Date(now+3600000).toISOString()};
  const item=await (await request.post('/api/listings',{data})).json();
  try{
    await page.goto('/');await page.getByRole('button',{name:'Kitchen desk',exact:true}).click();
    await page.getByRole('textbox',{name:'Search meals or kitchens'}).fill(data.title);
    const card=page.locator('.meal-card').filter({hasText:data.title});
    await card.getByRole('button',{name:'Edit box',exact:true}).click();
    await page.getByRole('dialog').getByLabel('Rescue price (₹)',{exact:true}).fill('45');
    await page.getByRole('button',{name:'Save changes',exact:true}).click();
    await expect(page.getByRole('dialog')).toHaveCount(0);
    await expect(card).toContainText('₹45');
    page.once('dialog',d=>d.accept());await card.getByRole('button',{name:'Delete',exact:true}).click();
    await expect(card).toHaveCount(0);expect((await request.get(`/api/listings/${item.id}`)).status()).toBe(404);
  }finally{await request.delete(`/api/listings/${item.id}`);}
});
