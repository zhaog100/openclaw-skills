// MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
// AutoFlow Dashboard API 封装

const BASE = window.location.origin

function getToken() {
  return localStorage.getItem('af_token')
}

async function request(path, opts = {}) {
  const token = getToken()
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) }
  if (token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${BASE}${path}`, { ...opts, headers })
  if (res.status === 401) {
    localStorage.removeItem('af_token')
    window.location.hash = '#/login'
    throw new Error('登录已过期')
  }
  if (!res.ok) {
    const e = await res.json().catch(() => ({}))
    throw new Error(e.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

const api = {
  // Auth
  login(username, password) { return request('/api/auth/login', { method: 'POST', body: JSON.stringify({ username, password }) }) },

  // Dashboard
  dashboard() { return request('/api/v1/admin/dashboard').catch(() => ({ data: { clients: 0, today_convs: 0, today_msgs: 0, cost_today: 0, recent_msgs: [] } })) },

  // Clients
  listClients() { return request('/api/v1/clients').catch(() => ({ data: [] })) },
  getClient(id) { return request(`/api/v1/clients/${id}`) },
  createClient(body) { return request('/api/v1/clients', { method: 'POST', body: JSON.stringify(body) }) },
  getClientUsage(id, days = 7) { return request(`/api/v1/clients/${id}/usage?days=${days}`).catch(() => ({ data: {} })) },
  getClientCosts(id, days = 30) { return request(`/api/v1/clients/${id}/costs?days=${days}`).catch(() => ({ data: {} })) },

  // Conversations & Messages
  listConversations(clientId, page = 1) {
    let url = `/api/v1/conversations?page=${page}&limit=20`
    if (clientId) url += `&client_id=${clientId}`
    return request(url).catch(() => ({ data: { items: [], total: 0 } }))
  },
  getMessages(convId) { return request(`/api/v1/conversations/${convId}/messages`).catch(() => ({ data: [] })) },

  // Knowledge Base
  listKB() { return request('/api/v1/kb').catch(() => ({ data: [] })) },
  createKB(body) { return request('/api/v1/kb', { method: 'POST', body: JSON.stringify(body) }) },
  getKB(id) { return request(`/api/v1/kb/${id}`) },
  addEntry(kbId, body) { return request(`/api/v1/kb/${kbId}/documents`, { method: 'POST', body: JSON.stringify(body) }) },
  searchKB(kbId, query, topK = 5) { return request(`/api/v1/kb/${kbId}/search`, { method: 'POST', body: JSON.stringify({ query, top_k: topK }) }) },
  listEntries(kbId, limit = 20, offset = 0) { return request(`/api/v1/kb/${kbId}/entries?limit=${limit}&offset=${offset}`).catch(() => ({ data: [] })) },
  deleteEntry(kbId, entryId) { return request(`/api/v1/kb/${kbId}/entries/${entryId}`, { method: 'DELETE' }) },

  // Reports
  listReports() { return request('/api/v1/reports/templates').catch(() => ({ data: [] })) },
  generateReport(templateId, params) { return request(`/api/v1/reports/generate`, { method: 'POST', body: JSON.stringify({ template_id: templateId, ...params }) }) },
  listSnapshots() { return request('/api/v1/reports/snapshots').catch(() => ({ data: [] })) },

  // Crawl Tasks
  listCrawls() { return request('/api/v1/crawl/tasks').catch(() => ({ data: [] })) },
  createCrawl(body) { return request('/api/v1/crawl/tasks', { method: 'POST', body: JSON.stringify(body) }) },
  getCrawl(id) { return request(`/api/v1/crawl/tasks/${id}`) },

  // Cost Tracking
  costByModel(days = 30) { return request(`/api/v1/admin/costs/by-model?days=${days}`).catch(() => ({ data: [] })) },
  costByDate(days = 30) { return request(`/api/v1/admin/costs/by-date?days=${days}`).catch(() => ({ data: [] })) },
}
