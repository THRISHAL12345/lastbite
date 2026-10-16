import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { api, labels, writeFields, date } from './api';
import './styles.css';

function Icon({ name, size = 20 }) {
  const paths = {
    inbox: <><path d="M4 4h16v16H4zM4 14h5l2 3h2l2-3h5"/></>,
    pulse: <path d="M3 12h4l3-8 4 16 3-8h4"/>,
    check: <><circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
    search: <><circle cx="10" cy="10" r="6"/><path d="m15 15 5 5"/></>,
    plus: <path d="M12 5v14M5 12h14"/>,
    arrow: <path d="M5 12h14m-5-5 5 5-5 5"/>,
    refresh: <><path d="M20 6v5h-5M4 18v-5h5"/><path d="M5 9a7 7 0 0 1 12-4l3 6M4 13l3 6a7 7 0 0 0 12-4"/></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name] || paths.inbox}</svg>;
}
function Badge({ value }) { return <span className={`badge ${value.toLowerCase()}`}>{labels[value]}</span>; }
function Modal({ title, eyebrow, onClose, children, wide = false }) {
  const ref = useRef(null);
  useEffect(() => { ref.current.showModal(); }, []);
  return <dialog ref={ref} className={wide ? 'modal wide' : 'modal'} onCancel={onClose} onClick={e => { if (e.target === ref.current) onClose(); }} aria-labelledby="dialog-title">
    <div className="modal-head"><div><p className="eyebrow">{eyebrow}</p><h2 id="dialog-title">{title}</h2></div><button className="close" onClick={onClose} aria-label="Close dialog">×</button></div>{children}
  </dialog>;
}
function TicketForm({ ticket, onClose, onSaved }) {
  const [busy, setBusy] = useState(false), [error, setError] = useState('');
  async function save(event) {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true); setError('');
    try {
      await api(ticket ? `/tickets/${ticket.id}` : '/tickets', { method: ticket ? 'PUT' : 'POST', body: JSON.stringify(data) });
      onSaved();
    } catch (error) { setError(error.message); } finally { setBusy(false); }
  }
  return <Modal title={ticket ? 'Edit ticket' : 'A little context goes a long way.'} eyebrow={ticket ? `TICKET RD-${ticket.id}` : 'NEW SUPPORT REQUEST'} onClose={onClose}>
    <form onSubmit={save}>
      {error && <p className="alert" role="alert">{error}</p>}
      <label>Subject<input name="title" autoFocus required maxLength={200} defaultValue={ticket?.title} placeholder="What do you need help with?"/></label>
      <label>Description<textarea name="description" maxLength={5000} defaultValue={ticket?.description} placeholder="What happened, and what have you tried?" rows={4}/></label>
      <div className="form-row"><label>Requester<input name="requester" required maxLength={120} defaultValue={ticket?.requester} placeholder="Full name"/></label><label>Assigned to<input name="assignee" required maxLength={120} defaultValue={ticket?.assignee || 'Unassigned'}/></label></div>
      <div className="form-row"><label>Category<select name="category" defaultValue={ticket?.category || 'OTHER'}>{['ACCESS','HARDWARE','SOFTWARE','NETWORK','OTHER'].map(x => <option key={x} value={x}>{labels[x]}</option>)}</select></label><label>Priority<select name="priority" defaultValue={ticket?.priority || 'MEDIUM'}>{['LOW','MEDIUM','HIGH','URGENT'].map(x => <option key={x} value={x}>{labels[x]}</option>)}</select></label></div>
      <label>Status<select name="status" defaultValue={ticket?.status || 'OPEN'}>{['OPEN','IN_PROGRESS','RESOLVED'].map(x => <option key={x} value={x}>{labels[x]}</option>)}</select></label>
      <p className="hint">Resolution target: urgent 4h · high 8h · medium 24h · low 72h. The clock starts when the ticket is created.</p>
      <div className="modal-actions"><button type="button" className="button secondary" onClick={onClose}>Cancel</button><button className="button primary" disabled={busy}>{busy ? 'Saving…' : ticket ? 'Save changes' : 'Create ticket'}<Icon name="arrow" size={16}/></button></div>
    </form>
  </Modal>;
}
function TicketDetail({ initial, onClose, onEdit, onChanged }) {
  const [ticket, setTicket] = useState(initial), [events, setEvents] = useState([]), [error, setError] = useState(''), [busy, setBusy] = useState(false);
  const loadEvents = () => api(`/tickets/${initial.id}/events`).then(setEvents).catch(e => setError(e.message));
  useEffect(() => { loadEvents(); }, [initial.id]);
  async function changeStatus(status) {
    setBusy(true); setError('');
    try { setTicket(await api(`/tickets/${ticket.id}`, { method: 'PUT', body: JSON.stringify({ ...writeFields(ticket), status }) })); await loadEvents(); onChanged(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function addComment(e) {
    e.preventDefault(); const form = e.currentTarget; const message = new FormData(form).get('message');
    setBusy(true); setError('');
    try { await api(`/tickets/${ticket.id}/comments`, { method: 'POST', body: JSON.stringify({ message }) }); form.reset(); await loadEvents(); onChanged(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  async function remove() {
    if (!window.confirm(`Delete RD-${ticket.id} and its entire history? This cannot be undone.`)) return;
    setBusy(true); setError('');
    try { await api(`/tickets/${ticket.id}`, { method: 'DELETE' }); onChanged(); onClose(); }
    catch (e) { setError(e.message); } finally { setBusy(false); }
  }
  return <Modal title={ticket.title} eyebrow={`RD-${ticket.id} / ${labels[ticket.category]}`} onClose={onClose} wide>
    {error && <p className="alert" role="alert">{error}</p>}
    <div className="detail-badges"><Badge value={ticket.status}/><Badge value={ticket.priority}/><span className={ticket.overdue ? 'overdue-text' : 'muted'}>{ticket.status === 'RESOLVED' ? `Resolved ${date(ticket.resolved_at)}` : `${ticket.overdue ? 'Overdue · ' : 'Due '}${date(ticket.due_at)}`}</span></div>
    <p className="description">{ticket.description || 'No additional description.'}</p>
    <div className="detail-meta"><div><small>REQUESTER</small><strong>{ticket.requester}</strong></div><div><small>ASSIGNED TO</small><strong>{ticket.assignee}</strong></div><div><small>CREATED</small><strong>{date(ticket.created_at)}</strong></div></div>
    <div className="detail-actions"><button className="button secondary" onClick={() => onEdit(ticket)}>Edit details</button>{ticket.status !== 'RESOLVED' ? <button className="button primary" disabled={busy} onClick={() => changeStatus(ticket.status === 'OPEN' ? 'IN_PROGRESS' : 'RESOLVED')}>{ticket.status === 'OPEN' ? 'Start working' : 'Mark resolved'}<Icon name="check" size={16}/></button> : <button className="button secondary" disabled={busy} onClick={() => changeStatus('OPEN')}>Reopen ticket</button>}<button className="delete" disabled={busy} onClick={remove}>Delete</button></div>
    <h3>Conversation & history</h3><form className="comment-form" onSubmit={addComment}><label className="sr-only" htmlFor="comment">Add a note</label><textarea id="comment" name="message" required maxLength={2000} placeholder="Add an update for the team…" rows={2}/><button className="button secondary" disabled={busy}>Add note</button></form>
    <div className="history">{events.map(event => <div key={event.id}><span className="timeline-dot"/><p>{event.message}<small>{event.kind === 'COMMENT' ? 'Team note' : 'Ticket update'} · {date(event.created_at)}</small></p></div>)}</div>
  </Modal>;
}
function App() {
  const [filter, setFilter] = useState('ALL'), [priority, setPriority] = useState(''), [search, setSearch] = useState(''), [query, setQuery] = useState('');
  const [page, setPage] = useState({items: [], total: 0}), [stats, setStats] = useState(null), [activity, setActivity] = useState([]);
  const [offset, setOffset] = useState(0), [revision, setRevision] = useState(0), [loading, setLoading] = useState(true), [error, setError] = useState('');
  const [form, setForm] = useState(null), [selected, setSelected] = useState(null), [notice, setNotice] = useState('');
  useEffect(() => { const timer = setTimeout(() => { setQuery(search); setOffset(0); }, 250); return () => clearTimeout(timer); }, [search]);
  useEffect(() => {
    const controller = new AbortController();
    const params = new URLSearchParams({ limit: '10', offset: String(offset), q: query });
    if (filter === 'OVERDUE') params.set('overdue', 'true'); else if (filter !== 'ALL') params.set('status', filter);
    if (priority) params.set('priority', priority);
    setLoading(true); setError('');
    Promise.all([api(`/tickets?${params}`, {signal: controller.signal}), api('/tickets/stats', {signal: controller.signal}), api('/activity', {signal: controller.signal})])
      .then(([page, stats, activity]) => { setPage(page); setStats(stats); setActivity(activity); if (offset && !page.items.length) setOffset(Math.max(0, offset-10)); })
      .catch(error => { if (error.name !== 'AbortError') setError(error.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [filter, priority, query, offset, revision]);
  const refresh = () => setRevision(x => x + 1);
  const chooseFilter = value => { setFilter(value); setOffset(0); };
  const nav = [['ALL','inbox','All tickets',stats?.total],['OPEN','pulse','Open queue',stats?.open],['IN_PROGRESS','clock','In progress',stats?.in_progress],['RESOLVED','check','Resolved',stats?.resolved]];
  return <div className="workspace">
    <aside className="sidebar"><a className="brand" href="/" aria-label="RelayDesk home"><span className="brand-mark">r<span>↗</span></span>relaydesk<span className="brand-period">.</span></a><div className="workspace-label"><span className="workspace-avatar">IT</span><div>Support workspace<small>Internal service desk</small></div><span className="workspace-chevron">⌄</span></div><p className="nav-label">WORKSPACE</p><nav aria-label="Ticket queues">{nav.map(([value,icon,label,count]) => <button key={value} className={filter===value?'nav-item active':'nav-item'} onClick={() => chooseFilter(value)}><Icon name={icon}/><span>{label}</span><b>{count ?? '—'}</b></button>)}</nav><div className="sidebar-note"><span className="note-icon"><Icon name="pulse"/></span><h3>Good support.<br/>Less back-and-forth.</h3><p>One place for every request, update, and resolution.</p><span className="note-line"/></div><div className="sidebar-footer"><span className="avatar">SD</span><div>Service desk<small>Team workspace</small></div><span className="online-dot"/></div></aside>
    <div className="main"><div className="topbar"><div>Workspace <span>/</span> <strong>Support overview</strong></div><span className="topbar-label">IT OPERATIONS</span></div><main>
      <header className="page-header"><div><p className="eyebrow">A CLEARER PICTURE, A CALMER QUEUE</p><h1>Keep support moving<span>.</span></h1><p className="subtitle">Every request accounted for. Every teammate in the loop.</p></div><button className="button primary" onClick={() => { setNotice(''); setForm({}); }}><Icon name="plus" size={18}/> New ticket</button></header>
      {notice && <div className="notice" role="status">{notice}<button onClick={() => setNotice('')} aria-label="Dismiss notification">×</button></div>}
      {error && <div className="alert" role="alert">{error}<button onClick={refresh}>Retry</button></div>}
      <section className="stats" aria-label="Workspace statistics">{[['Total tickets',stats?.total,'inbox','ALL','Every request in one place'],['In progress',stats?.in_progress,'pulse','IN_PROGRESS','Currently with the team'],['Resolved',stats?.resolved,'check','RESOLVED','Back to business as usual'],['Past SLA',stats?.overdue,'clock','OVERDUE','A little extra attention']].map(([label,value,icon,f,caption]) => <button className={`stat ${f === 'OVERDUE' ? 'attention' : ''} ${filter===f ? 'stat-selected' : ''}`} key={label} onClick={() => chooseFilter(f)}><div className="stat-top"><span>{label}</span><Icon name={icon}/></div><strong>{value ?? '—'}</strong><small>{caption}</small></button>)}</section>
      <div className="content-grid"><section className="panel queue"><div className="panel-heading"><div><h2>Your support queue <span className="count">{page.total}</span></h2><p>The right context to take the next step.</p></div><button className="icon-button" aria-label="Refresh tickets" onClick={refresh} disabled={loading}><Icon name="refresh" size={18}/></button></div><div className="tabs" aria-label="Filter by status">{[['ALL','All tickets'],['OPEN','Open'],['IN_PROGRESS','In progress'],['RESOLVED','Resolved'],['OVERDUE','Past SLA']].map(([value,label]) => <button key={value} aria-pressed={filter===value} className={filter===value?'selected':''} onClick={() => chooseFilter(value)}>{label}</button>)}</div><div className="toolbar"><div className="search"><Icon name="search" size={18}/><input aria-label="Search by subject or requester" placeholder="Search subject or requester…" value={search} onChange={e => setSearch(e.target.value)}/></div><select aria-label="Filter by priority" value={priority} onChange={e => {setPriority(e.target.value);setOffset(0);}}><option value="">All priorities</option>{['URGENT','HIGH','MEDIUM','LOW'].map(x => <option key={x} value={x}>{labels[x]}</option>)}</select></div>
        {loading ? <div className="empty" role="status"><span className="loader"/>Getting your queue ready…</div> : error ? <div className="empty">The queue could not be refreshed. Please try again.</div> : !page.items.length ? <div className="empty"><div className="empty-icon"><Icon name="inbox" size={30}/></div><h3>{stats?.total ? 'Nothing in this queue.' : 'A fresh start for your service desk.'}</h3><p>{stats?.total ? 'Try another filter or search term.' : 'Create your first ticket and give every request a home.'}</p><button className="button secondary" onClick={() => setForm({})}>Create a ticket <Icon name="plus" size={16}/></button></div> : <div className="table-wrap"><table><thead><tr><th>Ticket / Requester</th><th>Priority</th><th>Status</th><th>Assigned to</th><th>Target</th></tr></thead><tbody>{page.items.map(ticket => <tr key={ticket.id}><td><button className="ticket-link" onClick={() => setSelected(ticket)}><small>RD-{String(ticket.id).padStart(3,'0')} <span>· {labels[ticket.category]}</span></small><strong>{ticket.title}</strong></button><span className="requester">{ticket.requester}</span></td><td><Badge value={ticket.priority}/></td><td><Badge value={ticket.status}/></td><td><span className="assignee"><span className="tiny-avatar">{ticket.assignee.split(' ').map(s=>s[0]).slice(0,2).join('')}</span>{ticket.assignee}</span></td><td><span className={ticket.overdue?'due overdue-text':'due'}>{ticket.status==='RESOLVED' ? 'Resolved' : ticket.overdue ? 'Past SLA' : new Date(ticket.due_at).toLocaleDateString([], {month:'short',day:'numeric'})}<small>{ticket.status==='RESOLVED' ? 'Closed' : new Date(ticket.due_at).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit'})}</small></span></td></tr>)}</tbody></table></div>}
        <div className="table-footer"><span>{page.total ? `${offset+1}–${Math.min(offset+10,page.total)} of ${page.total} tickets` : 'No tickets to show'}</span><div><button disabled={offset===0||loading} onClick={() => setOffset(x=>x-10)} aria-label="Previous page">←</button><button disabled={offset+10>=page.total||loading} onClick={() => setOffset(x=>x+10)} aria-label="Next page">→</button></div></div></section>
      <aside className="right-column"><section className="panel activity"><div className="panel-heading"><div><h2>Latest updates</h2><p>The story behind the queue.</p></div><span className="activity-dot"/></div><div className="activity-list">{!activity.length ? <p className="activity-empty">Ticket activity will appear here as your team gets to work.</p> : activity.slice(0,6).map(event => <div className="activity-item" key={event.id}><span className={`event-icon ${event.kind==='COMMENT'?'comment':''}`}>{event.kind==='COMMENT'?'↳':'↗'}</span><div><span className="event-ticket">RD-{String(event.ticket_id).padStart(3,'0')}</span><p>{event.message}</p><small>{date(event.created_at)}</small></div></div>)}</div></section><section className="sla-card"><div className="sla-title"><Icon name="clock"/><span>RESOLUTION TARGETS</span></div><h3>Time matters.<br/>Context does, too.</h3><p>Targets run continuously from ticket creation.</p><div className="sla-grid">{[['Urgent','4h'],['High','8h'],['Medium','24h'],['Low','72h']].map(([a,b])=><div key={a}><span>{a}</span><strong>{b}</strong></div>)}</div></section></aside></div>
      <footer className="page-footer"><span>RelayDesk <span> / </span> A little more clarity for your team.</span><span>Built for the work behind the work.</span></footer>
    </main></div>
    {form && <TicketForm ticket={form.id?form:null} onClose={() => setForm(null)} onSaved={() => {setForm(null);refresh();setNotice('Ticket saved. Your queue is up to date.');}}/>}
    {selected && !form && <TicketDetail initial={selected} onClose={() => setSelected(null)} onEdit={ticket => {setSelected(null);setForm(ticket);}} onChanged={refresh}/>}
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
