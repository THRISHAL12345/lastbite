export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {...options, headers: {'Content-Type':'application/json', ...options.headers}});
  if (!response.ok) {
    let detail;
    try { detail = (await response.json()).detail; } catch { /* Proxy errors may not be JSON. */ }
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail)
      ? detail.map(item => `${item.loc.at(-1)}: ${item.msg}`).join('; ')
      : `Could not reach the kitchen (${response.status}). Please try again.`);
  }
  return response.status === 204 ? null : response.json();
}
export const labels = {BAKERY:'Bakery', MEALS:'Meals', PRODUCE:'Produce', DESSERTS:'Sweet treats', VEGETARIAN:'Vegetarian', VEGAN:'Vegan', MIXED:'Mixed', AVAILABLE:'Available', SOLD_OUT:'Sold out', EXPIRED:'Expired', PAUSED:'Paused', RESERVED:'Awaiting pickup', PICKED_UP:'Picked up', CANCELLED:'Cancelled'};
export const money = paise => new Intl.NumberFormat('en-IN', {style:'currency',currency:'INR',maximumFractionDigits:2}).format(paise/100);
export const time = value => new Date(value).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'});
export const date = value => new Date(value).toLocaleDateString([], {month:'short',day:'numeric'});
export function remaining(value, now = Date.now()) {
  const minutes = Math.ceil((new Date(value).getTime()-now)/60000);
  return minutes <= 0 ? 'Pickup ended' : minutes < 60 ? `${minutes}m left` : `${Math.floor(minutes/60)}h ${minutes%60}m left`;
}
export function localInput(value) {
  const d = new Date(value);
  return new Date(d.getTime()-d.getTimezoneOffset()*60000).toISOString().slice(0,16);
}
export const writeFields = item => Object.fromEntries(['title','restaurant','description','category','dietary','allergens','address','price_paise','original_price_paise','quantity_total','pickup_start','pickup_end','status'].map(key=>[key,item[key]]));

export function pickupWindow(start, end) {
  const sameDay = new Date(start).toDateString() === new Date(end).toDateString();
  return `${date(start)} · ${time(start)}–${sameDay ? '' : date(end) + ' · '}${time(end)}`;
}
