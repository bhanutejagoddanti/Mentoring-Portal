const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5001/api'
let token = localStorage.getItem('mentoringToken') || ''

export function getToken() {
  return token || localStorage.getItem('mentoringToken') || ''
}

export function setToken(value) {
  token = value || ''
  if (token) localStorage.setItem('mentoringToken', token)
  else localStorage.removeItem('mentoringToken')
}

export async function apiRequest(path, options = {}) {
  const currentToken = getToken()
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) }
  if (currentToken) headers.Authorization = `Bearer ${currentToken}`
  const response = await fetch(`${API_BASE}${path}`, { ...options, headers })
  const payload = await response.json().catch(() => ({}))
  if (!response.ok) throw new Error(payload.error || `API request failed (${response.status})`)
  return payload
}

export async function apiLogin(email, password) {
  const result = await apiRequest('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) })
  setToken(result.access_token)
  return result.user
}

export async function apiRegister(data) {
  return apiRequest('/auth/register', { method: 'POST', body: JSON.stringify(data) })
}

export async function apiMe() {
  return apiRequest('/auth/me')
}

export async function apiLogout() {
  try {
    await apiRequest('/auth/logout', { method: 'POST' })
  } catch (err) {
    console.warn('Logout API failed:', err)
  } finally {
    setToken('')
  }
}

export async function apiResetPassword(email) {
  return apiRequest('/auth/password-reset', { method: 'POST', body: JSON.stringify({ email }) })
}

// ------------------------- Messaging (Inbox / DMs) -------------------------

export async function apiInbox() {
  return apiRequest('/messaging/inbox')
}

export async function apiCreateConversation(participant_id) {
  return apiRequest('/messaging/conversations', { method: 'POST', body: JSON.stringify({ participant_id }) })
}

export async function apiGetConversation(conversation_id) {
  return apiRequest(`/messaging/conversations/${conversation_id}`)
}

export async function apiSendDm(conversation_id, content, reply_to_id, attachments) {
  return apiRequest(`/messaging/conversations/${conversation_id}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content, reply_to_id, attachments }),
  })
}

export async function apiMarkRead(conversation_id, message_id) {
  return apiRequest(`/messaging/conversations/${conversation_id}/read`, {
    method: 'POST',
    body: JSON.stringify({ message_id }),
  })
}

export async function apiReactDm(conversation_id, message_id, reaction) {
  return apiRequest(`/messaging/conversations/${conversation_id}/messages/${message_id}/reaction`, {
    method: 'POST',
    body: JSON.stringify({ reaction }),
  })
}

export async function apiSearchUsers(query, role) {
  const params = new URLSearchParams()
  if (query) params.set('q', query)
  if (role) params.set('role', role)
  const qs = params.toString()
  return apiRequest(`/messaging/users${qs ? `?${qs}` : ''}`)
}

export async function apiCommunityMessages(cid) {
  return apiRequest(`/communities/${cid}/messages`)
}

export async function apiSendCommunityMessage(cid, content, reply_to_id, attachments) {
  return apiRequest(`/communities/${cid}/messages`, {
    method: 'POST',
    body: JSON.stringify({ content, reply_to_id, attachments }),
  })
}

export async function apiReactCommunity(cid, message_id, reaction) {
  return apiRequest(`/communities/${cid}/messages/${message_id}/reaction`, {
    method: 'POST',
    body: JSON.stringify({ reaction }),
  })
}

export async function apiCommunityMembers(cid) {
  return apiRequest(`/communities/${cid}/members`)
}

// ------------------------- Notifications -------------------------

export async function apiNotifications() {
  return apiRequest('/notifications')
}

export async function apiMarkNotificationRead(id) {
  return apiRequest(`/notifications/${id}/read`, { method: 'POST' })
}

export async function apiMarkAllNotificationsRead() {
  return apiRequest('/notifications/read-all', { method: 'POST' })
}

export async function apiUnreadNotificationCount() {
  return apiRequest('/notifications/unread-count')
}
