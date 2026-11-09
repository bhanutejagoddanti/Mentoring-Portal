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
