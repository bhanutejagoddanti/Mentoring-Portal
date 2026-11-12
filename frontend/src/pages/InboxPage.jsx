import { useCallback, useEffect, useMemo, useState } from 'react'
import { Panel, Title, input, button } from '../ui'
import { apiInbox, apiGetConversation, apiSendDm, apiMarkRead, apiReactDm } from '../api'

const EMOJIS = ['👍', '❤️', '😂', '😮', '😢', '🙏']

const ROLE_COLORS = {
  student: { badge: 'bg-blue-50 text-blue-700 border-blue-200', text: 'text-blue-600', solid: 'bg-blue-600' },
  mentor: { badge: 'bg-green-50 text-green-700 border-green-200', text: 'text-green-600', solid: 'bg-green-600' },
  admin: { badge: 'bg-purple-50 text-purple-700 border-purple-200', text: 'text-purple-600', solid: 'bg-purple-600' },
}

function initials(name) {
  return String(name || '?')
    .split(' ')
    .map((p) => p[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

function fmtTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

export default function InboxPage({ user, focusConversationId, onConsumeFocus }) {
  const [conversations, setConversations] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [activeId, setActiveId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [sending, setSending] = useState(false)
  const [text, setText] = useState('')
  const [replyTo, setReplyTo] = useState(null)
  const [mobileChatOpen, setMobileChatOpen] = useState(false)
  const [search, setSearch] = useState('')

  const loadInbox = useCallback(async () => {
    try {
      const res = await apiInbox()
      const items = res?.items || []
      const sorted = [...items].sort(
        (a, b) =>
          String(b.last_message_at || b.updated_at || b.created_at || '').localeCompare(
            String(a.last_message_at || a.updated_at || a.created_at || ''),
          ),
      )
      setConversations(sorted)
      setError('')
    } catch (err) {
      setError(err.message || 'Failed to load conversations')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadInbox()
    const timer = setInterval(() => {
      if (document.visibilityState === 'visible') loadInbox()
    }, 15000)
    return () => clearInterval(timer)
  }, [loadInbox])

  async function openConversation(cid) {
    setActiveId(cid)
    setMobileChatOpen(true)
    setReplyTo(null)
    setText('')
    setError('')
    try {
      const res = await apiGetConversation(cid)
      if (res?.conversation) {
        setDetail(res)
        const lastId = (res.messages || []).slice(-1)[0]?.id
        await apiMarkRead(cid, lastId)
      }
    } catch (err) {
      setDetail(null)
    }
  }

  useEffect(() => {
    if (focusConversationId) {
      openConversation(focusConversationId)
      onConsumeFocus?.()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [focusConversationId])

  async function sendMessage(e) {
    e.preventDefault()
    if (!text.trim() || !activeId) return
    const content = text.trim()
    const replyId = replyTo?.id || null
    setSending(true)
    const optimisticId = Date.now()
    const optimistic = {
      id: optimisticId,
      conversation_id: activeId,
      sender_id: user.id,
      sender_name: user.name,
      sender_role: user.role,
      content,
      reply_to_id: replyId,
      attachments: [],
      created_at: new Date().toISOString(),
      reactions: [],
    }
    const prev = detail?.messages || []
    setDetail((d) => (d ? { ...d, messages: [...(d.messages || []), optimistic] } : d))
    setText('')
    setReplyTo(null)
    try {
      const res = await apiSendDm(activeId, content, replyId, [])
      setDetail((d) => ({ ...d, messages: (d?.messages || []).map((m) => (m.id === optimisticId ? res?.message || m : m)) }))
      await loadInbox()
    } catch (err) {
      setDetail((d) => ({ ...d, messages: prev }))
      setError(err.message)
    } finally {
      setSending(false)
    }
  }

  async function toggleReaction(message) {
    if (!activeId || !message?.id) return
    const already = (message.reactions || []).some((r) => r.user_id === user.id && r.reaction === '👍')
    const finalReaction = already ? null : '👍'
    try {
      const res = await apiReactDm(activeId, message.id, finalReaction || '👍')
      const reactions = finalReaction
        ? res?.message?.reactions || [...(message.reactions || []), { user_id: user.id, user_name: user.name, reaction: finalReaction }]
        : (message.reactions || []).filter((r) => !(r.user_id === user.id && r.reaction === '👍'))
      setDetail((d) => ({ ...d, messages: (d?.messages || []).map((m) => (m.id === message.id ? { ...m, reactions } : m)) }))
    } catch (err) {
      console.warn('Reaction failed', err)
    }
  }

  const messages = detail?.messages || []
  const conversation = detail?.conversation || conversations.find((c) => c.conversation_id === activeId) || null
  const peer = activeId && detail?.other ? detail.other : conversation?.other || null
  const peerColor = peer ? ROLE_COLORS[peer.role] || ROLE_COLORS.student : null

  const filtered = useMemo(
    () =>
      conversations.filter((c) => {
        const name = c?.other?.name || ''
        const q = search.trim().toLowerCase()
        if (!q) return true
        return name.toLowerCase().includes(q) || (c.last_message?.content || '').toLowerCase().includes(q)
      }),
    [conversations, search],
  )

  function ConversationList() {
    if (loading) return <Panel><p className="text-sm text-slate-500">Loading conversations…</p></Panel>
    if (error) return <Panel><p className="text-sm text-red-600">{error}</p><button className={button} onClick={loadInbox}>Retry</button></Panel>
    return (
      <Panel>
        <input className={input} placeholder="Search conversations…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <div className="mt-3 max-h-[520px] overflow-y-auto md:max-h-[560px]">
          {filtered.length === 0 ? (
            <p className="py-8 text-center text-sm text-slate-400">No conversations found.</p>
          ) : (
            filtered.map((c) => (
              <button
                key={c.conversation_id}
                onClick={() => openConversation(c.conversation_id)}
                className={`flex w-full items-center gap-3 border-b border-slate-100 px-3 py-3 text-left transition last:border-b-0 hover:bg-slate-50 ${c.conversation_id === activeId ? 'bg-indigo-50' : ''}`}
              >
                <div className="grid size-11 shrink-0 place-items-center rounded-full text-xs font-bold text-white" style={{ backgroundColor: peerColor?.solid || '#4f46e5' }}>
                  {initials(c?.other?.name || 'U')}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center justify-between gap-2">
                    <b className="truncate text-sm text-slate-900">{c?.other?.name || 'Conversation'}</b>
                    <span className="shrink-0 text-[10px] text-slate-400">{fmtTime(c.last_message_at || c.updated_at)}</span>
                  </div>
                  <div className="mt-0.5 flex items-center justify-between gap-2">
                    <span className="truncate text-xs text-slate-500">
                      {c.last_message ? `${c.last_message.sender_id === user.id ? 'You: ' : ''}${c.last_message.content}` : 'No messages yet'}
                    </span>
                    {c.unread_count > 0 && <span className="shrink-0 rounded-full bg-red-500 px-2 py-0.5 text-[10px] font-semibold text-white">{c.unread_count}</span>}
                  </div>
                  {c.other?.role && (
                    <div className="mt-0.5">
                      <span className={`rounded-full border px-2 py-0.5 text-[10px] font-semibold capitalize ${ROLE_COLORS[c.other.role]?.badge || 'bg-slate-100 text-slate-600'}`}>
                        {c.other.role}
                      </span>
                    </div>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </Panel>
    )
  }

  function ChatWindow() {
    return (
      <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card md:h-[640px]">
        <div className="flex items-center gap-3 border-b border-slate-200 bg-slate-50 px-4 py-3">
          <button className="rounded-lg border border-slate-200 bg-white px-2 py-1 text-sm text-slate-600 md:hidden" onClick={() => setMobileChatOpen(false)}>
            ← Back
          </button>
          <div className="grid size-10 place-items-center rounded-full text-xs font-bold text-white" style={{ backgroundColor: peerColor?.solid || '#4f46e5' }}>
            {initials(peer?.name || user.name)}
          </div>
          <div className="min-w-0 flex-1">
            <b className="block truncate text-sm text-slate-900">{peer?.name || conversation?.name || 'Conversation'}</b>
            <span className={`text-xs font-semibold ${peerColor?.text || 'text-slate-500'}`}>
              {peer?.role ? peer.role.charAt(0).toUpperCase() + peer.role.slice(1) : 'Member'}
            </span>
          </div>
        </div>
        <div className="min-h-0 flex-1 space-y-2 overflow-y-auto px-4 py-4">
          {messages.length === 0 ? (
            <p className="py-10 text-center text-sm text-slate-400">No messages yet. Say hello 👋</p>
          ) : (
            messages.map((m) => {
              const mine = m.sender_id === user.id
              const original = m.reply_to_id ? messages.find((x) => x.id === m.reply_to_id) : null
              return (
                <div key={m.id} className={`flex ${mine ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-2xl px-3 py-2 text-sm shadow-sm ${mine ? 'bg-indigo-600 text-white' : 'border border-slate-200 bg-white text-slate-800'}`}>
                    {!mine && <div className="mb-0.5 text-[11px] font-semibold" style={{ color: peerColor?.text || '#4f46e5' }}>{m.sender_name}</div>}
                    {original && (
                      <div className={`mb-1 rounded-lg px-2 py-1 text-[11px] ${mine ? 'bg-indigo-700/40' : 'bg-slate-100'}`}>
                        <b>{original.sender_name}:</b> {original.content}
                      </div>
                    )}
                    <p>{m.content}</p>
                    <div className="mt-1 flex items-center justify-between gap-2 text-[10px] opacity-70">
                      <span>{fmtTime(m.created_at)}</span>
                      {mine && <span>✓✓ Read</span>}
                    </div>
                    {(m.reactions || []).length > 0 && (
                      <div className="mt-1 flex flex-wrap gap-1">
                        {(m.reactions || []).map((r, i) => (
                          <button
                            key={i}
                            type="button"
                            onClick={() => toggleReaction(m)}
                            className={`rounded-full border px-2 py-0.5 text-xs transition ${r.user_id === user.id ? 'border-indigo-400 bg-indigo-50' : 'border-slate-200 bg-white'}`}
                          >
                            {r.reaction}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )
            })
          )}
        </div>
        <form className="flex items-center gap-2 border-t border-slate-200 p-3" onSubmit={sendMessage}>
          {replyTo && (
            <div className="flex items-center justify-between gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs">
              <span className="truncate">
                Replying to <b>{replyTo.sender_name}</b>: {replyTo.content}
              </span>
              <button type="button" className="text-slate-500" onClick={() => setReplyTo(null)}>✕</button>
            </div>
          )}
          <input className={input} value={text} onChange={(e) => setText(e.target.value)} placeholder="Type a message…" />
          <button className={button} disabled={sending || !text.trim()}>Send</button>
        </form>
      </div>
    )
  }

  const chatPanel = (
    <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card md:h-[640px]">
      {activeId ? (
        ChatWindow()
      ) : (
        <div className="flex flex-1 items-center justify-center p-6">
          <p className="max-w-sm text-center text-sm text-slate-400">Select a conversation to start messaging.</p>
        </div>
      )}
    </div>
  )

  return (
    <>
      <Title>Chat</Title>
      {mobileChatOpen && activeId && (
        <div className="flex min-h-[520px] flex-1 flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card md:hidden" style={{ height: 'calc(100vh - 230px)' }}>
          {ChatWindow()}
        </div>
      )}
      <div className={`${mobileChatOpen && activeId ? 'hidden md:flex' : 'flex'} min-h-[520px] flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-card md:h-[640px] md:flex-row`}>
        {ConversationList()}
        {activeId ? chatPanel : null}
      </div>
    </>
  )
}
