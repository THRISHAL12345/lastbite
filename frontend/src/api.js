export async function api(path, options = {}) {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers },
  });
  if (!response.ok) {
    let detail;
    try { detail = (await response.json()).detail; } catch { /* Non-JSON proxy error. */ }
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail)
      ? detail.map(item => `${item.loc.at(-1)}: ${item.msg}`).join('; ')
      : `Request failed (${response.status}). Check that the API is running.`);
  }
  return response.status === 204 ? null : response.json();
}
export const labels = { OPEN: 'Open', IN_PROGRESS: 'In progress', RESOLVED: 'Resolved',
  LOW: 'Low', MEDIUM: 'Medium', HIGH: 'High', URGENT: 'Urgent',
  ACCESS: 'Access', HARDWARE: 'Hardware', SOFTWARE: 'Software', NETWORK: 'Network', OTHER: 'Other' };
export const writeFields = ticket => Object.fromEntries(
  ['title', 'description', 'requester', 'assignee', 'category', 'priority', 'status'].map(key => [key, ticket[key]]),
);
export function date(value) { return new Date(value).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }); }
