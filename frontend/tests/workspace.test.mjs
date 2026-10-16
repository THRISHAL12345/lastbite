import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { resolve } from 'node:path';
import { pathToFileURL } from 'node:url';
import { JSDOM } from 'jsdom';
import { build } from 'esbuild';
import { act } from 'react';

test('workspace creates, updates, comments, resolves, reopens and deletes a ticket', async () => {
  const dom = new JSDOM('<!doctype html><div id="root"></div>', {url: 'http://localhost'});
  for (const name of ['window','document','HTMLElement','HTMLInputElement','HTMLTextAreaElement','Event','MouseEvent','FormData']) {
    globalThis[name] = name === 'window' ? dom.window : dom.window[name];
  }
  globalThis.IS_REACT_ACT_ENVIRONMENT = true;
  dom.window.HTMLDialogElement.prototype.showModal = function () { this.open = true; };
  dom.window.confirm = () => true;
  let tickets = [], events = [], id = 0;
  const response = value => ({ok: true, status: 200, json: async () => structuredClone(value)});
  globalThis.fetch = async (url, options = {}) => {
    const {pathname, searchParams} = new URL(url, 'http://localhost');
    const method = options.method || 'GET';
    const body = options.body ? JSON.parse(options.body) : null;
    if (pathname === '/api/tickets/stats') return response({total:tickets.length,open:tickets.filter(t=>t.status==='OPEN').length,in_progress:tickets.filter(t=>t.status==='IN_PROGRESS').length,resolved:tickets.filter(t=>t.status==='RESOLVED').length,overdue:0});
    if (pathname === '/api/activity') return response(events);
    if (pathname === '/api/tickets' && method === 'POST') {
      const now = new Date().toISOString();
      tickets.push({...body,id:++id,created_at:now,updated_at:now,due_at:new Date(Date.now()+86400000).toISOString(),resolved_at:null,overdue:false});
      return response(tickets.at(-1));
    }
    if (pathname === '/api/tickets') {
      const filtered = tickets.filter(t=>(!searchParams.get('status')||t.status===searchParams.get('status')) && (!searchParams.get('priority')||t.priority===searchParams.get('priority')) && (!searchParams.get('q')||t.title.toLowerCase().includes(searchParams.get('q').toLowerCase())));
      return response({items:filtered,total:filtered.length});
    }
    if (pathname.endsWith('/events')) return response(events);
    if (pathname.endsWith('/comments')) {
      events.unshift({id:events.length+1,ticket_id:id,kind:'COMMENT',message:body.message,created_at:new Date().toISOString()});
      return response(events[0]);
    }
    if (method === 'PUT') {
      tickets[0] = {...tickets[0],...body,resolved_at:body.status==='RESOLVED'?new Date().toISOString():null};
      return response(tickets[0]);
    }
    if (method === 'DELETE') {tickets=[];events=[];return {ok:true,status:204};}
    throw new Error(`Unexpected API call: ${method} ${url}`);
  };
  const dir = await mkdtemp(resolve('.test-build-'));
  try {
    const bundle = await build({entryPoints:['src/main.jsx'],bundle:true,write:false,format:'esm',loader:{'.css':'empty'},external:['react','react-dom/client'],logLevel:'silent'});
    const file = resolve(dir,'app.mjs');
    await writeFile(file,bundle.outputFiles[0].text);
    await act(async () => {await import(pathToFileURL(file));});
    const byText = text => [...document.querySelectorAll('button')].find(el=>el.textContent.trim()===text);
    const click = async el => {assert.ok(el,'button exists'); await act(async()=>el.dispatchEvent(new MouseEvent('click',{bubbles:true})));};
    const fill = (selector,value) => {
      const el=document.querySelector(selector);assert.ok(el,selector);
      const proto=el.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;
      Object.getOwnPropertyDescriptor(proto,'value').set.call(el,value);
      el.dispatchEvent(new Event('input',{bubbles:true}));
    };
    const submit = async selector => {await act(async()=>document.querySelector(selector).dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));};
    assert.match(document.body.textContent,/A fresh start for your service desk/);
    await click(byText('New ticket'));
    await act(async()=>{fill('[name="title"]','Broken VPN');fill('[name="requester"]','Alex');});
    await submit('dialog form');
    assert.equal(tickets.length,1);
    assert.equal(document.querySelector('dialog'),null);
    assert.match(document.body.textContent,/Ticket saved/);
    await click(document.querySelector('.ticket-link'));
    assert.match(document.querySelector('dialog').textContent,/Broken VPN/);
    await click(byText('Start working'));
    assert.equal(tickets[0].status,'IN_PROGRESS');
    await act(async()=>fill('#comment','Checking network logs'));
    await submit('.comment-form');
    assert.match(document.querySelector('.history').textContent,/Checking network logs/);
    await click(byText('Mark resolved'));
    assert.equal(tickets[0].status,'RESOLVED');
    await click(byText('Reopen ticket'));
    assert.equal(tickets[0].status,'OPEN');
    await click(byText('Edit details'));
    await act(async()=>fill('[name="title"]','VPN connection restored'));
    await submit('dialog form');
    assert.equal(tickets[0].title,'VPN connection restored');
    await click(document.querySelector('.ticket-link'));
    await click(byText('Delete'));
    assert.equal(tickets.length,0);
    assert.equal(document.querySelector('dialog'),null);
    assert.match(document.body.textContent,/A fresh start for your service desk/);
    await act(async () => { await new Promise(resolve => setTimeout(resolve, 300)); });
  } finally {
    await rm(dir,{recursive:true,force:true});
    dom.window.close();
  }
});
