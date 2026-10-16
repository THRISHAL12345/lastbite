import { test } from 'node:test';
import assert from 'node:assert/strict';
import { api, remaining, money, writeFields } from '../src/api.js';

test('API errors preserve stock-conflict messages for the customer',async()=>{
  const old=globalThis.fetch;
  try{globalThis.fetch=async()=>({ok:false,status:409,json:async()=>({detail:'Not enough boxes left'})});await assert.rejects(api('/listings/1/reservations',{method:'POST'}),/Not enough boxes left/);}finally{globalThis.fetch=old;}
});
test('validation and non-JSON proxy errors remain readable',async()=>{
  const old=globalThis.fetch;
  try{globalThis.fetch=async()=>({ok:false,status:422,json:async()=>({detail:[{loc:['body','quantity'],msg:'Must be positive'}]})});await assert.rejects(api('/listings'),/quantity: Must be positive/);
  globalThis.fetch=async()=>({ok:false,status:502,json:async()=>{throw Error('HTML');}});await assert.rejects(api('/listings'),/502/);}finally{globalThis.fetch=old;}
});
test('delete responses do not try to parse an empty body',async()=>{
  const old=globalThis.fetch;
  try{globalThis.fetch=async()=>({ok:true,status:204,json:async()=>{throw Error('No body');}});assert.equal(await api('/listings/1',{method:'DELETE'}),null);}finally{globalThis.fetch=old;}
});
test('countdown handles future, boundary and expired windows',()=>{
  const now=Date.UTC(2026,9,16,12);
  assert.equal(remaining(now+90000,now),'2m left');
  assert.equal(remaining(now+3660000,now),'1h 1m left');
  assert.equal(remaining(now,now),'Pickup ended');
  assert.equal(remaining(now-1,now),'Pickup ended');
  assert.match(money(9900),/99/);
});
test('listing updates exclude stock counters and derived state',()=>{
  const clean=writeFields({id:1,title:'Supper',quantity_available:2,state:'AVAILABLE',quantity_total:3});
  assert.equal(clean.quantity_total,3);assert.ok(!('quantity_available' in clean));assert.ok(!('state' in clean));assert.ok(!('id' in clean));
});
