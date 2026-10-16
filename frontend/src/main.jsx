import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api, labels, money, time, date, remaining, localInput, pickupWindow } from './api';
import './styles.css';

function Icon({name, size=20}) {
  const paths = {
    arrow:<path d="M5 12h14m-6-6 6 6-6 6"/>, plus:<path d="M12 5v14M5 12h14"/>,
    clock:<><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    leaf:<><path d="M20 3C7 1 2 8 5 15s17 8 15-12ZM5 20 16 8"/></>,
    bag:<><path d="M5 7h14l2 14H3L5 7Z"/><path d="M8 8V6a4 4 0 0 1 8 0v2"/></>,
    search:<><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></>,
    pin:<><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z"/><circle cx="12" cy="10" r="2"/></>,
    check:<path d="m5 12 4 4L19 6"/>, kitchen:<><path d="M4 21h16M6 21V10h12v11M4 10h16L18 3H6L4 10ZM10 21v-6h4v6"/></>,
    refresh:<><path d="M20 6v5h-5M4 18v-5h5M5 8a8 8 0 0 1 13-3l2 6M4 13l2 6a8 8 0 0 0 13-3"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]||paths.leaf}</svg>;
}
function FoodArt({category='MEALS',hero=false}) {
  return <svg className={hero?'food-art hero-art':'food-art'} viewBox="0 0 360 230" aria-hidden="true">
    <ellipse cx="180" cy="191" rx="114" ry="16" fill="#111827" opacity=".12"/>
    {category==='BAKERY' ? <g transform="rotate(-12 180 120)"><path d="M68 147C72 63 282 40 297 138l-40 25-22-31-95-3-31 38Z" fill="#c9792d"/><path d="M92 129c10-65 163-67 181-9l-35 24-24-25-71 2-25 23Z" fill="#f4be68"/><path d="m133 80 15 64 39-4-3-71Z" fill="#ffe0a1"/><path d="m190 69 11 68 37 5-9-60Z" fill="#ffcf83"/><path d="m93 118 32 35M245 101l30 37" stroke="#ffe0a1" strokeWidth="10" strokeLinecap="round"/><g fill="#75411b"><ellipse cx="158" cy="93" rx="2" ry="5"/><ellipse cx="209" cy="97" rx="2" ry="5"/></g></g>
    : category==='DESSERTS' ? <g><path d="m99 171 163 0-16-61H115Z" fill="#6c392e"/><path d="m115 110 131 0-13-30H131Z" fill="#f7a7b0"/><path d="M115 111c22 12 28-13 45 0s28-13 45 0 27 6 41 0" fill="none" stroke="#ffe9d1" strokeWidth="13"/><path d="m99 171 163 0" stroke="#ffe9d1" strokeWidth="13"/><circle cx="183" cy="66" r="19" fill="#e94d56"/><path d="M184 50q-4-20 15-25" fill="none" stroke="#305747" strokeWidth="5"/><g fill="#fff3cf"><circle cx="140" cy="145" r="4"/><circle cx="218" cy="141" r="4"/><circle cx="179" cy="149" r="4"/></g></g>
    : <g><ellipse cx="180" cy="138" rx="112" ry="58" fill="#f1e4ce"/><ellipse cx="180" cy="126" rx="112" ry="58" fill="#fff8e9"/><ellipse cx="180" cy="124" rx="94" ry="45" fill="#d4c5a6"/>
      <g fill="#4e8c53"><ellipse cx="140" cy="112" rx="39" ry="24" transform="rotate(-25 140 112)"/><ellipse cx="184" cy="103" rx="35" ry="24"/><ellipse cx="219" cy="123" rx="32" ry="29"/></g>
      <g fill="#80b95c"><ellipse cx="117" cy="130" rx="22" ry="16"/><ellipse cx="178" cy="137" rx="32" ry="20"/></g>
      <g fill="#e97741"><circle cx="146" cy="109" r="18"/><circle cx="220" cy="119" r="19"/><circle cx="159" cy="145" r="13"/></g><g fill="#f5ca61"><path d="m171 89 29 7-13 25-27-7Z"/><path d="m185 130 28 6-12 20-25-6Z"/></g>
      <g fill="#fff3bd"><circle cx="130" cy="116" r="4"/><circle cx="192" cy="120" r="4"/><circle cx="215" cy="140" r="4"/><circle cx="163" cy="97" r="4"/></g><path d="m118 103 16 10m65-24 8 18m-56 24 20 5m34-4 15-8" stroke="#c8df9a" strokeWidth="3" strokeLinecap="round"/>
      {category==='PRODUCE' && <g><path d="m248 72 20 53 16-65Z" fill="#ed9045"/><path d="m269 66-13-30m17 29 13-31" stroke="#387b4c" strokeWidth="8" strokeLinecap="round"/></g>}
    </g>}
  </svg>;
}
function Modal({title,subtitle,onClose,children}) {
  const ref=useRef(null);
  useEffect(()=>{ref.current.showModal();},[]);
  return <dialog ref={ref} onCancel={onClose} aria-labelledby="dialog-title" onClick={e=>{if(e.target===ref.current)onClose();}}><div className="modal-head"><div><p className="eyebrow">{subtitle}</p><h2 id="dialog-title">{title}</h2></div><button className="icon-button" aria-label="Close dialog" onClick={onClose}>×</button></div>{children}</dialog>;
}
function ListingForm({item,onClose,onSaved}) {
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  async function save(e) {
    e.preventDefault();setBusy(true);setError('');
    const data=Object.fromEntries(new FormData(e.currentTarget));
    data.price_paise=Math.round(Number(data.price)*100);data.original_price_paise=Math.round(Number(data.original_price)*100);
    delete data.price;delete data.original_price;data.quantity_total=Number(data.quantity_total);
    // Preserve seconds when an existing pickup window wasn't edited.
    for(const k of ['pickup_start','pickup_end'])data[k]=item&&data[k]===localInput(item[k])?item[k]:new Date(data[k]).toISOString();
    try {await api(item?`/listings/${item.id}`:'/listings',{method:item?'PUT':'POST',body:JSON.stringify(data)});onSaved('Meal box saved.');}
    catch(e){setError(e.message);}finally{setBusy(false);}
  }
  return <Modal title={item?'Edit meal box':'Give good food a second chance.'} subtitle="KITCHEN DESK" onClose={onClose}><form onSubmit={save}>
    {error&&<p className="alert" role="alert">{error}</p>}
    <label>Box name<input name="title" required maxLength={160} defaultValue={item?.title} placeholder="The sunset supper box" autoFocus/></label>
    <div className="form-row"><label>Kitchen name<input name="restaurant" required maxLength={120} defaultValue={item?.restaurant} placeholder="Your restaurant or bakery"/></label><label>Category<select name="category" defaultValue={item?.category||'MEALS'}>{['MEALS','BAKERY','PRODUCE','DESSERTS'].map(x=><option key={x} value={x}>{labels[x]}</option>)}</select></label></div>
    <label>What's inside?<textarea name="description" rows={2} maxLength={3000} defaultValue={item?.description} placeholder="Describe the portions and what customers can expect."/></label>
    <label>Pickup address<input name="address" required maxLength={240} defaultValue={item?.address} placeholder="Street, neighbourhood, city"/></label>
    <div className="form-row"><label>Dietary information<select name="dietary" defaultValue={item?.dietary||'VEGETARIAN'}>{['VEGETARIAN','VEGAN','MIXED'].map(x=><option key={x} value={x}>{labels[x]}</option>)}</select></label><label>Allergens<input name="allergens" required maxLength={300} defaultValue={item?.allergens||'Ask the kitchen'}/></label></div>
    <div className="form-row three"><label>Rescue price (₹)<input name="price" type="number" min="0.01" max="10000" step="0.01" required defaultValue={item?item.price_paise/100:99}/></label><label>Original value (₹)<input name="original_price" type="number" min="0.01" max="10000" step="0.01" required defaultValue={item?item.original_price_paise/100:299}/></label><label>Total boxes<input name="quantity_total" type="number" min="1" max="1000" required defaultValue={item?.quantity_total||5}/></label></div>
    <div className="form-row"><label>Pickup starts<input name="pickup_start" type="datetime-local" required defaultValue={localInput(item?.pickup_start||Date.now()-300000)}/></label><label>Pickup ends<input name="pickup_end" type="datetime-local" required defaultValue={localInput(item?.pickup_end||Date.now()+10800000)}/></label></div>
    <label>Availability<select name="status" defaultValue={item?.status||'ACTIVE'}><option value="ACTIVE">Accepting reservations</option><option value="PAUSED">Paused</option></select></label>
    {item&&<p className="hint">Once a reservation exists, only total stock and availability can change. Existing pickup promises stay intact.</p>}
    <div className="modal-actions"><button className="button secondary" type="button" onClick={onClose}>Cancel</button><button className="button primary" disabled={busy}>{busy?'Saving…':item?'Save changes':'Publish meal box'}<Icon name="arrow" size={16}/></button></div>
  </form></Modal>;
}
function ReserveForm({item,onClose,onSaved}) {
  const [quantity,setQuantity]=useState(1),[busy,setBusy]=useState(false),[error,setError]=useState('');
  async function reserve(e){e.preventDefault();setBusy(true);setError('');try{const r=await api(`/listings/${item.id}/reservations`,{method:'POST',body:JSON.stringify({customer:new FormData(e.currentTarget).get('customer'),quantity})});onSaved(r);}catch(e){setError(e.message);}finally{setBusy(false);}}
  return <Modal title={item.title} subtitle={item.restaurant} onClose={onClose}>
    <div className={`detail-art art-${item.category.toLowerCase()}`}><FoodArt category={item.category}/><span className="diet-badge">{labels[item.dietary]}</span></div>
    <p className="description">{item.description||'A surprise selection of surplus food from this kitchen.'}</p>
    <div className="pickup-info"><Icon name="pin"/><span>{item.address}</span></div><div className="pickup-info"><Icon name="clock"/><span>{pickupWindow(item.pickup_start,item.pickup_end)}</span></div>
    <p className="allergens"><strong>Allergens:</strong> {item.allergens}</p>
    <form onSubmit={reserve}>{error&&<p className="alert" role="alert">{error}</p>}
      <div className="form-row"><label>Your name<input name="customer" autoFocus required maxLength={120} placeholder="Name for pickup"/></label><label>Boxes<input type="number" min="1" max={Math.min(20,item.quantity_available)} required value={quantity} onChange={e=>setQuantity(Number(e.target.value))}/></label></div>
      <div className="checkout-total"><span>Pay at pickup <small>No online payment</small></span><strong>{money(item.price_paise*quantity)}</strong></div>
      <p className="hint">Collect before the pickup window ends. You can cancel before then to release your boxes.</p>
      <button className="button primary full" disabled={busy||item.state!=='AVAILABLE'}>{busy?'Reserving…':'Confirm reservation'}<Icon name="arrow" size={17}/></button>
    </form>
  </Modal>;
}
function PickupForm({reservation,onClose,onSaved}) {
  const [busy,setBusy]=useState(false),[error,setError]=useState('');
  async function submit(e){e.preventDefault();setBusy(true);setError('');try{await api(`/reservations/${reservation.id}/pickup`,{method:'POST',body:JSON.stringify({pickup_code:new FormData(e.currentTarget).get('pickup_code')})});onSaved('Pickup confirmed. Another meal rescued!');}catch(e){setError(e.message);}finally{setBusy(false);}}
  return <Modal title="One last check. Then dig in." subtitle="CONFIRM PICKUP" onClose={onClose}><p>{reservation.customer} · {reservation.quantity} box{reservation.quantity===1?'':'es'} · {reservation.listing_title}</p><form onSubmit={submit}>{error&&<p className="alert" role="alert">{error}</p>}<label>Pickup code<input name="pickup_code" autoFocus required maxLength={12} autoComplete="off" placeholder="Enter the customer's code"/></label><p className="hint">Confirm only when the food has been handed over. This updates the meals-rescued total.</p><button className="button primary full" disabled={busy}>{busy?'Confirming…':'Confirm pickup'}<Icon name="check" size={18}/></button></form></Modal>;
}
function App(){
  const [view,setView]=useState('market'),[category,setCategory]=useState(''),[dietary,setDietary]=useState(''),[search,setSearch]=useState(''),[query,setQuery]=useState(''),[state,setState]=useState('');
  const [page,setPage]=useState({items:[],total:0}),[reservations,setReservations]=useState([]),[stats,setStats]=useState(null),[offset,setOffset]=useState(0),[reservationOffset,setReservationOffset]=useState(0);
  const [loading,setLoading]=useState(true),[error,setError]=useState(''),[notice,setNotice]=useState(''),[revision,setRevision]=useState(0),[form,setForm]=useState(null),[selected,setSelected]=useState(null),[pickup,setPickup]=useState(null),[busy,setBusy]=useState(false),[now,setNow]=useState(Date.now());
  useEffect(()=>{const t=setTimeout(()=>{setQuery(search);setOffset(0);},220);return()=>clearTimeout(t);},[search]);
  useEffect(()=>{const t=setInterval(()=>{setNow(Date.now());setRevision(x=>x+1);},30000);return()=>clearInterval(t);},[]);
  useEffect(()=>{
    const controller=new AbortController();setLoading(true);setError('');
    const params=new URLSearchParams({limit:'9',offset:String(offset),q:query});
    if(category)params.set('category',category);if(dietary)params.set('dietary',dietary);
    if(view==='market')params.set('state','AVAILABLE');else if(state)params.set('state',state);
    Promise.all([api(`/listings?${params}`,{signal:controller.signal}),api('/stats',{signal:controller.signal}),api(`/reservations?limit=12&offset=${reservationOffset}`,{signal:controller.signal})])
      .then(([p,s,r])=>{setPage(p);setStats(s);setReservations(r);if(offset&&!p.items.length)setOffset(Math.max(0,offset-9));})
      .catch(e=>{if(e.name!=='AbortError')setError(e.message);}).finally(()=>{if(!controller.signal.aborted)setLoading(false);});
    return()=>controller.abort();
  },[view,category,dietary,query,state,offset,reservationOffset,revision]);
  const refresh=()=>setRevision(x=>x+1);
  const navigate=v=>{setView(v);setOffset(0);setSearch('');setQuery('');setCategory('');setDietary('');setState('');};
  const saved=message=>{setForm(null);setPickup(null);setNotice(message);refresh();};
  async function cancel(r){if(!window.confirm(`Cancel ${r.quantity} box${r.quantity===1?'':'es'} from ${r.restaurant}?`))return;setBusy(true);try{await api(`/reservations/${r.id}/cancel`,{method:'POST'});saved('Reservation cancelled. The boxes are available again.');}catch(e){setError(e.message);}finally{setBusy(false);}}
  async function remove(item){if(!window.confirm(`Delete “${item.title}”?`))return;setBusy(true);try{await api(`/listings/${item.id}`,{method:'DELETE'});saved('Meal box deleted.');}catch(e){setError(e.message);}finally{setBusy(false);}}
  return <div className="app"><header className="site-header"><a href="/" className="brand" aria-label="LastBite home"><span className="brand-symbol"><Icon name="leaf" size={23}/></span>lastbite<span className="brand-dot">.</span></a><nav aria-label="Main navigation">{[['market','Explore boxes'],['reservations','Reservations'],['kitchen','Kitchen desk']].map(([v,label])=><button className={view===v?'active':''} aria-current={view===v?'page':undefined} key={v} onClick={()=>navigate(v)}>{label}</button>)}</nav><span className="demo-pill"><span/> Shared demo</span></header>
    <main>
      {view==='market'?<section className="hero"><div className="hero-copy"><p className="eyebrow"><span className="tiny-star">✳</span> GOOD FOOD. SECOND CHANCE.</p><h1>Too good<br/>to <em>say goodbye.</em></h1><p className="hero-description">Your next great meal is a rescue mission.<br/>Discover surplus food from local kitchens for less.</p><button className="button primary" onClick={()=>document.getElementById('browse').scrollIntoView({behavior:'smooth'})}>Find your next bite<Icon name="arrow"/></button><span className="hero-footnote">Reserve a box. Pick it up. Make it count.</span></div><div className="hero-visual"><div className="orbit orbit-one"/><div className="orbit orbit-two"/><span className="floating-note note-top"><span>✦</span> A little less waste.<br/><strong>A lot more taste.</strong></span><FoodArt hero/><span className="rescue-sticker">GOOD<br/>FOOD<br/><span>↗</span></span><span className="floating-note note-bottom"><Icon name="bag"/><span>Fresh from the kitchen.<br/><strong>Ready for a second chance.</strong></span></span></div></section>:<section className="section-intro"><p className="eyebrow">{view==='kitchen'?'FROM YOUR KITCHEN, WITH PURPOSE':'SMALL ACTIONS. DELICIOUS IMPACT.'}</p><h1>{view==='kitchen'?'The kitchen desk.':'Your next good deed.'}</h1><p>{view==='kitchen'?'List the surplus. Manage your stock. Turn pickups into impact.':'All reservations in this shared demo. Keep your code handy at pickup.'}</p>{view==='kitchen'&&<button className="button primary" onClick={()=>setForm({})}><Icon name="plus"/>New meal box</button>}</section>}
      <section className="impact-strip" aria-label="Food rescue statistics">{[['bag','Boxes to rescue',stats?.boxes_available],['check','Meals rescued',stats?.meals_rescued],['kitchen','Kitchens sharing',stats?.active_kitchens],['leaf','Saved at pickup',stats?money(stats.savings_paise):null]].map(([icon,label,value])=><div className="impact" key={label}><span className="impact-icon"><Icon name={icon}/></span><div><strong>{value??'—'}</strong><span>{label}</span></div></div>)}</section>
      {notice&&<div className="notice" role="status"><span><Icon name="check"/>{notice}</span><button aria-label="Dismiss notification" onClick={()=>setNotice('')}>×</button></div>}
      {error&&<div className="alert" role="alert">{error}<button onClick={refresh}>Try again</button></div>}
      <section className="browse-section" id="browse"><div className="section-heading"><div><p className="eyebrow">{view==='market'?'LESS WASTE. MORE ON YOUR PLATE.':view==='kitchen'?'YOUR SURPLUS, SORTED':'RESERVED WITH PURPOSE'}</p><h2>{view==='market'?'Good things come in boxes.':view==='kitchen'?'Every box has potential.':'From reservation to rescue.'}</h2></div><button className="icon-button" aria-label="Refresh" disabled={loading} onClick={refresh}><Icon name="refresh"/></button></div>
      {view!=='reservations'&&<><div className="browse-toolbar"><div className="category-tabs" aria-label="Food category">{[['','All boxes'],['MEALS','Meals'],['BAKERY','Bakery'],['PRODUCE','Produce'],['DESSERTS','Sweet treats']].map(([v,label])=><button key={v} aria-pressed={category===v} className={category===v?'selected':''} onClick={()=>{setCategory(v);setOffset(0);}}>{label}</button>)}</div><div className="search-box"><Icon name="search" size={18}/><input aria-label="Search meals or kitchens" placeholder="Find a meal or kitchen…" value={search} onChange={e=>setSearch(e.target.value)}/></div></div><div className="results-toolbar"><span>{page.total} {view==='market'?'boxes worth rescuing':'listings'} <span className="muted">· refreshed every 30 seconds</span></span><div><select aria-label="Dietary filter" value={dietary} onChange={e=>{setDietary(e.target.value);setOffset(0);}}><option value="">Any dietary preference</option>{['VEGETARIAN','VEGAN','MIXED'].map(x=><option key={x} value={x}>{labels[x]}</option>)}</select>{view==='kitchen'&&<select aria-label="Availability filter" value={state} onChange={e=>{setState(e.target.value);setOffset(0);}}><option value="">All availability</option>{['AVAILABLE','SOLD_OUT','PAUSED','EXPIRED'].map(x=><option key={x} value={x}>{labels[x]}</option>)}</select>}</div></div></>}
      {loading?<div className="empty" role="status"><span className="loader"/>Finding the good stuff…</div>:error?<div className="empty">We couldn't refresh the kitchen. Please try again.</div>:view==='reservations'?<><div className="reservation-grid">{reservations.map(r=><article className="reservation-card" key={r.id}><div className="reservation-top"><span className={`status ${r.status.toLowerCase()}`}>{labels[r.status]}</span><small>LB-{String(r.id).padStart(3,'0')}</small></div><h3>{r.listing_title}</h3><p>{r.restaurant} · {r.customer}</p><div className="reservation-summary"><strong>{r.quantity} box{r.quantity===1?'':'es'}</strong><strong>{money(r.total_paise)}</strong></div><div className="pickup-info"><Icon name="clock" size={16}/>{pickupWindow(r.pickup_start,r.pickup_end)}</div><div className="pickup-info"><Icon name="pin" size={16}/>{r.address}</div><div className="pickup-code"><span>PICKUP CODE</span><strong>{r.pickup_code}</strong></div>{r.status==='RESERVED'&&<div className="reservation-actions"><button className="button primary" onClick={()=>setPickup(r)}>Confirm handover<Icon name="check" size={16}/></button><button className="text-button" disabled={busy} onClick={()=>cancel(r)}>Cancel reservation</button></div>}{r.status==='PICKED_UP'&&<p className="success-note"><Icon name="leaf" size={16}/>Rescued, collected, and counted.</p>}{r.status==='EXPIRED'&&<p className="hint">Pickup window ended. This wasn't counted as a rescue.</p>}</article>)}</div>{!reservations.length&&<div className="empty"><Icon name="bag" size={34}/><h3>No reservations here yet.</h3><p>Your first food rescue is waiting.</p><button className="button primary" onClick={()=>navigate('market')}>Explore boxes<Icon name="arrow" size={16}/></button></div>}<div className="pagination"><span>Reservations {reservations.length?`${reservationOffset+1}–${reservationOffset+reservations.length}`:'0'}</span><div><button aria-label="Previous reservations" disabled={!reservationOffset} onClick={()=>setReservationOffset(x=>Math.max(0,x-12))}>←</button><button aria-label="Next reservations" disabled={reservations.length<12} onClick={()=>setReservationOffset(x=>x+12)}>→</button></div></div></>:<><div className="meal-grid">{page.items.map(item=><article className="meal-card" key={item.id}><div className={`card-art art-${item.category.toLowerCase()}`}><span className="discount-badge">{item.discount_percent}% less</span><span className="diet-badge">{labels[item.dietary]}</span><FoodArt category={item.category}/><span className={`stock-badge ${item.quantity_available<=2?'low-stock':''}`}>{item.state==='AVAILABLE'?`${item.quantity_available} left to rescue`:labels[item.state]}</span></div><div className="card-body"><p className="kitchen-name"><span className="kitchen-avatar">{item.restaurant.charAt(0)}</span>{item.restaurant}<Icon name="check" size={13}/></p><h3>{item.title}</h3><p className="card-description">{item.description||'A little surprise. A lot of good food.'}</p><div className="pickup-row"><span><Icon name="clock" size={14}/>{time(item.pickup_start)}–{time(item.pickup_end)}</span><span>{remaining(item.pickup_end,now)}</span></div><div className="card-bottom"><div className="price"><strong>{money(item.price_paise)}</strong><del>{money(item.original_price_paise)}</del><small>per box</small></div>{view==='market'?<button className="button primary small" onClick={()=>setSelected(item)}>Rescue box<Icon name="arrow" size={16}/></button>:<div className="manage-actions"><button className="button secondary small" onClick={()=>setForm(item)}>Edit box</button><button className="text-button" disabled={busy} onClick={()=>remove(item)}>Delete</button></div>}</div></div></article>)}</div>{!page.items.length&&<div className="empty"><Icon name="bag" size={36}/><h3>{view==='kitchen'?'Your next surplus has a home.':'Nothing on the menu just yet.'}</h3><p>{search||category||dietary?'Try another search or filter.':'Publish a meal box from the kitchen desk to get started.'}</p><button className="button secondary" onClick={()=>{navigate('kitchen');setForm({});}}>Publish a meal box<Icon name="plus" size={16}/></button></div>}<div className="pagination"><span>{page.total?`${offset+1}–${Math.min(offset+9,page.total)} of ${page.total} listings`:'No listings to show'}</span><div><button aria-label="Previous page" disabled={!offset} onClick={()=>setOffset(x=>x-9)}>←</button><button aria-label="Next page" disabled={offset+9>=page.total} onClick={()=>setOffset(x=>x+9)}>→</button></div></div></>}
      </section>
      {view==='market'&&<section className="how-it-works"><div><p className="eyebrow">A BETTER ENDING FOR GOOD FOOD</p><h2>Three steps.<br/><em>One delicious difference.</em></h2></div>{[['01','Find your flavour','Pick a box, check the details, and find something you’ll love.'],['02','Make it yours','Reserve your boxes. Save your code. Pay at pickup.'],['03','Pick up. Dig in.','Visit the kitchen in your pickup window. Good food, rescued.']].map(([n,title,body])=><div className="step" key={n}><span>{n}</span><h3>{title}</h3><p>{body}</p></div>)}</section>}
    </main><footer><a className="brand" href="/">lastbite<span className="brand-dot">.</span></a><p>Good food deserves a second chance.</p><small>Demo workspace · fictional kitchens · no online payments</small></footer>
    {form&&<ListingForm item={form.id?form:null} onClose={()=>setForm(null)} onSaved={saved}/>}
    {selected&&<ReserveForm item={selected} onClose={()=>setSelected(null)} onSaved={r=>{setSelected(null);navigate('reservations');setReservationOffset(0);saved(`You're on the list! Your pickup code is ${r.pickup_code}.`);}}/>}
    {pickup&&<PickupForm reservation={pickup} onClose={()=>setPickup(null)} onSaved={saved}/>}
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
