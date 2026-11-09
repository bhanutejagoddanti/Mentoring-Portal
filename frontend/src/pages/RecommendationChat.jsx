import { useState } from 'react'
import { Panel, input, button } from '../ui'
import { apiRequest } from '../api'

const SUGGESTIONS = [
  'Hi',
  'What is deep learning?',
  'How do I become an ML engineer?',
  '/find ML engineer mentor',
  '/find mentor for Python and data science projects',
]

function initials(name = '') {
  return name.split(' ').map((part) => part[0]).slice(0, 2).join('')
}

function expertiseOf(mentor) {
  const ai = mentor.ai_profile || {}
  const bits = [...(ai.skills || []), ...(ai.mentoring_topics || [])].filter(Boolean).slice(0, 3)
  return bits.length ? bits.join(' · ') : [mentor.field, mentor.industry].filter(Boolean).join(' · ')
}

function MentorCard({ mentor, onMentor, featured = false }) {
  const reason = mentor.matchReason || mentor.match_explanation || mentor.reason || ''
  return (
    <div className={`flex w-full items-start gap-3 rounded-xl border p-3 text-left ${featured ? 'border-indigo-300 bg-indigo-50/60' : 'border-slate-200 bg-white'}`}>
      <span className="grid size-11 shrink-0 place-items-center rounded-xl bg-indigo-100 text-xs font-semibold text-indigo-900">{initials(mentor.name)}</span>
      <span className="min-w-0 flex-1">
        <b className="block truncate text-sm">{mentor.name}{featured ? ' · Best match' : ''}</b>
        <span className="block truncate text-xs text-slate-500">{mentor.title || mentor.role}{mentor.field ? ` · ${mentor.field}` : ''}</span>
        {expertiseOf(mentor) && <span className="mt-1 block text-[11px] font-medium text-slate-600">{expertiseOf(mentor)}</span>}
        {reason && <span className="mt-1 block text-[11px] leading-4 text-slate-600">{reason}</span>}
        <button onClick={() => onMentor(mentor)} className="mt-2 inline-flex rounded-lg border border-indigo-200 bg-white px-3 py-1 text-[11px] font-semibold text-indigo-700 transition hover:border-indigo-600 hover:bg-indigo-50">
          View Profile
        </button>
      </span>
    </div>
  )
}

export default function RecommendationChat({ mentors, onMentor }) {
  const [text, setText] = useState('')
  const [loading, setLoading] = useState(false)
  const [phase, setPhase] = useState('')
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Hi! I’m your AI Career Assistant. Ask me questions, get roadmaps — or type `/find ...` to search for mentors (e.g. `/find ML engineer mentor`).' },
  ])

  async function sendMessage(value) {
    const message = value.trim()
    if (!message) return
    setMessages((current) => [...current, { role: 'student', text: message }])
    setText('')
    setLoading(true)
    setPhase(message.startsWith('/find') ? 'Finding mentors that fit your goals…' : 'Thinking…')
    try {
      const history = messages.map((m) => ({ role: m.role, text: m.text })).filter((m) => m.text)
      const result = await apiRequest('/mentors/chat', {
        method: 'POST',
        body: JSON.stringify({ message, history: history.slice(-8), limit: 5 }),
      })
      if (result.mode === 'find') {
        const recommendations = (result.items || []).map((item) => ({
          ...item.mentor,
          matchReason: item.match_explanation || item.reason,
        }))
        setMessages((current) => [...current, {
          role: 'assistant',
          text: result.reply || result.message || (recommendations.length ? 'Here are some mentors you might like.' : 'No suitable mentor found. Try broadening your question.'),
          mentors: recommendations,
          topExplanation: result.top_explanation || '',
          mode: 'find',
        }])
      } else {
        setMessages((current) => [...current, { role: 'assistant', text: result.reply || 'I’m here to help with career guidance.' }])
      }
    } catch (error) {
      setMessages((current) => [...current, { role: 'assistant', text: `Sorry, that didn’t go through (${error.message}). Please try again.` }])
    } finally {
      setLoading(false)
      setPhase('')
    }
  }

  function submit(event) {
    event.preventDefault()
    sendMessage(text)
  }

  return (
    <Panel title="AI Career Assistant">
      <div className="overflow-hidden rounded-2xl border border-slate-200">
        <div className="flex items-center gap-3 border-b border-slate-200 bg-white px-4 py-3">
          <div className="grid size-9 place-items-center rounded-lg bg-indigo-600 text-xs font-semibold text-white">AI</div>
          <div>
            <b className="block text-sm">AI Career Assistant</b>
            <span className="text-xs text-slate-500">Chat for guidance · `/find` for mentor search</span>
          </div>
          <span className="ml-auto flex items-center gap-2 text-xs text-slate-500">
            <span className="size-2 animate-breathe rounded-full bg-indigo-500" /> Online
          </span>
        </div>

        <div className="max-h-[520px] min-h-64 space-y-4 overflow-y-auto bg-slate-50 p-4" aria-live="polite">
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.role === 'student' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-[92%] ${message.role === 'student' ? 'text-right' : ''}`}>
                <span className="mb-1 block text-[11px] text-slate-500">{message.role === 'student' ? 'You' : 'Career Assistant'}</span>
                <p className={`inline-block whitespace-pre-wrap rounded-2xl px-3 py-2 text-left text-sm leading-5 ${message.role === 'student' ? 'bg-indigo-600 text-white' : 'border border-slate-200 bg-white text-slate-700'}`}>
                  {message.text}
                </p>
                {message.mode === 'find' && message.topExplanation && (
                  <div className="mt-2 rounded-xl border border-indigo-200 bg-indigo-50 p-3 text-left">
                    <b className="block text-xs font-semibold text-indigo-900">Our top recommendation</b>
                    <p className="mt-1 text-xs leading-5 text-indigo-950">{message.topExplanation}</p>
                  </div>
                )}
                {message.mentors?.length > 0 && (
                  <div className="mt-2 grid gap-2">
                    {message.mentors.map((mentor, i) => (
                      <MentorCard key={`${mentor.id}-${i}`} mentor={mentor} onMentor={onMentor} featured={i === 0} />
                    ))}
                  </div>
                )}
                {message.mode === 'find' && message.mentors?.length === 0 && (
                  <p className="mt-1 text-xs text-slate-500">Try `/find mentor for Python and data science projects` with broader skills.</p>
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="border-t border-slate-200 bg-white p-3">
          <div className="mb-3 flex flex-wrap gap-2">
            {SUGGESTIONS.map((prompt) => (
              <button key={prompt} onClick={() => sendMessage(prompt)} className="rounded-full border border-slate-200 px-3 py-1.5 text-xs text-slate-600 transition hover:border-indigo-600 hover:text-indigo-800">
                {prompt}
              </button>
            ))}
          </div>
          {loading && <p className="mb-2 flex items-center gap-2 text-xs text-slate-500"><span className="size-2 animate-breathe rounded-full bg-indigo-500" />{phase || 'Thinking…'}</p>}
          <form onSubmit={submit} className="flex gap-2">
            <input className={input} value={text} onChange={(event) => setText(event.target.value)} placeholder="Ask a career question, or type `/find mentor for Python projects`…" aria-label="Message to Career Assistant" />
            <button className={button} type="submit" disabled={!text.trim() || loading}>Send</button>
          </form>
          <p className="mt-2 text-[11px] text-slate-400">Normal messages = career chat. Messages starting with `/find` = mentor search.</p>
        </div>
      </div>
    </Panel>
  )
}
