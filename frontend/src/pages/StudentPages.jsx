import { useState } from 'react'
import { fields, termLabel } from '../data'
import { Panel, Title, Chip, card, input, button, outline } from '../ui'
import RecommendationChat from './RecommendationChat'
import { apiRequest } from '../api'

export function StudentHome({ data, user, onMentor }) {
  const [field, setField] = useState('All fields')
  const [industry, setIndustry] = useState('')
  const [role, setRole] = useState('')
  const [mode, setMode] = useState('')
  const availableMentors = data.mentors.filter(
    (item) =>
      item.active &&
      item.approved &&
      !data.blacklisted.some((account) => account.name === item.name && (!account.role || account.role === 'mentor')) &&
      item.slots -
        data.requests.filter((request) => request.mentor === item.name && request.status === 'Accepted').length >
        0,
  )
  const mentors = availableMentors.filter(
    (item) =>
      (field === 'All fields' || item.field.includes(field)) &&
      (!industry || item.industry === industry) &&
      (!role || item.role === role) &&
      (!mode || item.mode === mode),
  )

  return (
    <>
      <Title>Browse mentors</Title>
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <Panel title="Available mentors">
          <b className="text-3xl font-semibold text-slate-900">{availableMentors.length}</b>
          <p className="mt-1 text-xs text-slate-500">Approved & active mentors</p>
        </Panel>
        <Panel title="My requests">
          <b className="text-3xl font-semibold text-slate-900">{data.requests.filter((item) => item.student === user.name).length}</b>
          <p className="mt-1 text-xs text-slate-500">Submitted this workspace</p>
        </Panel>
        <Panel title="Current term">
          <b className="text-base">{termLabel(data.term)}</b>
          <p className="mt-1 text-xs text-slate-500">Request deadline: {data.term.close}</p>
        </Panel>
      </div>
      <RecommendationChat mentors={availableMentors} onMentor={onMentor} />
      <div className="grid gap-4 lg:grid-cols-[180px_1fr]">
        <Panel title="Fields">
          <div className="grid gap-1">
            {['All fields', ...fields].map((item) => (
              <button
                key={item}
                onClick={() => setField(item)}
                className={`rounded px-2 py-1.5 text-left text-sm ${field === item ? 'bg-indigo-50 text-indigo-900' : 'hover:bg-slate-50'}`}
              >
                {item}
              </button>
            ))}
          </div>
        </Panel>
        <div className="grid content-start gap-4">
          <Panel title="Filters">
            <div className="grid gap-2 sm:grid-cols-3">
              <select className={input} value={industry} onChange={(e) => setIndustry(e.target.value)}>
                <option value="">Industry</option>
                {[...new Set(data.mentors.map((item) => item.industry))].map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
              <select className={input} value={role} onChange={(e) => setRole(e.target.value)}>
                <option value="">Role</option>
                {[...new Set(data.mentors.map((item) => item.role))].map((item) => (
                  <option key={item}>{item}</option>
                ))}
              </select>
              <select className={input} value={mode} onChange={(e) => setMode(e.target.value)}>
                <option value="">Interaction mode</option>
                <option>Online</option>
                <option>Hybrid</option>
                <option>In person</option>
              </select>
            </div>
          </Panel>
          {mentors.length ? (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
              {mentors.map((item) => (
                <MentorCard
                  key={item.id}
                  mentor={{
                    ...item,
                    slots:
                      item.slots -
                      data.requests.filter((request) => request.mentor === item.name && request.status === 'Accepted')
                        .length,
                  }}
                  onClick={() => onMentor(item)}
                />
              ))}
            </div>
          ) : (
            <Panel>
              <p className="text-sm text-slate-500">No mentors match these filters.</p>
            </Panel>
          )}
        </div>
      </div>
    </>
  )
}

function MentorCard({ mentor, onClick }) {
  return (
    <article className={`${card} flex flex-col p-5 transition duration-200 hover:-translate-y-0.5 hover:shadow-card-hover`}>
      <div className="flex items-start gap-3">
        <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-indigo-50 text-sm font-semibold text-indigo-900">
          {mentor.name
            .split(' ')
            .map((part) => part[0])
            .slice(0, 2)
            .join('')}
        </div>
        <div className="min-w-0 flex-1">
          <h2 className="truncate font-semibold">{mentor.name}</h2>
          <p className="text-sm text-slate-500">{mentor.title}</p>
        </div>
        <span className="rounded-full bg-indigo-50 px-2 py-1 text-xs font-semibold text-indigo-800">{mentor.slots} spots</span>
      </div>
      <div className="my-3 flex flex-wrap gap-1">
        <Chip>{mentor.field}</Chip>
        <Chip>{mentor.industry}</Chip>
        <Chip>{mentor.mode}</Chip>
      </div>
      <p className="mb-4 min-h-10 text-sm leading-5 text-slate-600">{mentor.bio}</p>
      <button className={`${outline} mt-auto w-full`} onClick={onClick}>
        View profile
      </button>
    </article>
  )
}

export function MentorDetails({ mentor, onClose, onRequest }) {
  const [goal, setGoal] = useState('')
  const [message, setMessage] = useState('')
  return (
    <div className="fixed inset-0 z-20 grid place-items-center bg-slate-950/50 p-4 animate-fade-in">
      <section className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-card">
        <div className="mb-3 flex justify-between">
          <div>
            <h2 className="text-lg font-semibold">{mentor.name}</h2>
            <p className="text-sm text-slate-500">
              {mentor.title} · {mentor.industry}
            </p>
          </div>
          <button onClick={onClose}>Close</button>
        </div>
        <p className="text-sm">{mentor.background}</p>
        <div className="my-3 flex gap-2">
          <Chip>{mentor.field}</Chip>
          <Chip>{mentor.mode}</Chip>
          <Chip>{mentor.slots} slots</Chip>
        </div>
        {mentor.matchReason && (
          <p className="mt-3 rounded-xl bg-indigo-50 p-3 text-xs leading-5 text-indigo-900">{mentor.matchReason}</p>
        )}
        {mentor.ai_profile?.summary && !mentor.matchReason && (
          <p className="mt-3 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-600">{mentor.ai_profile.summary}</p>
        )}
        {mentor.linkedin && (
          <a className="text-sm text-indigo-700 underline" href={mentor.linkedin} target="_blank" rel="noreferrer">
            LinkedIn
          </a>
        )}
        <label className="mt-4 block text-sm">
          What would you like guidance on?
          <textarea className={`${input} mt-1`} value={goal} onChange={(e) => setGoal(e.target.value)} required />
        </label>
        <label className="mt-3 block text-sm">
          Optional message
          <textarea className={`${input} mt-1`} value={message} onChange={(e) => setMessage(e.target.value)} />
        </label>
        <button className={`${button} mt-3`} disabled={!goal.trim()} onClick={() => onRequest(mentor, goal, message)}>
          Send request
        </button>
      </section>
    </div>
  )
}

export function StudentProfile({ user, data, profile = {}, onSave }) {
  const request = data.requests.filter((item) => item.student === user.name)
  const assigned = request.find((item) => item.status === 'Accepted')
  const meetings = data.meetings.filter((item) => item.student === user.name && new Date(item.date) >= new Date())
  const tasks = data.tasks.filter((item) => item.student === user.name && !item.done)
  return (
    <>
      <Title>Student profile</Title>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title="Your details">
          <form
            className="grid gap-3"
            onSubmit={(event) => {
              event.preventDefault()
              onSave(new FormData(event.currentTarget))
            }}
          >
            <label className="text-sm">
              Name
              <input className={`${input} mt-1`} value={user.name} readOnly />
            </label>
            <label className="text-sm">
              Email
              <input className={`${input} mt-1`} value={user.email} readOnly />
            </label>
            <label className="text-sm">
              Program
              <input className={`${input} mt-1`} name="program" defaultValue={profile.program || 'BS Data Science'} />
            </label>
            <label className="text-sm">
              Career goals
              <textarea
                className={`${input} mt-1`}
                name="goals"
                defaultValue={profile.goals || 'Product analytics and data science'}
              />
            </label>
            <button className={button}>Save profile</button>
          </form>
        </Panel>
        <Panel title="Mentor by term">
          <p className="text-sm">
            {termLabel(data.term)}: {assigned?.mentor || 'Not assigned'}
          </p>
          <h3 className="mb-2 mt-5 font-medium">Requests</h3>
          {request.map((item) => (
            <p key={item.id} className="border-t py-2 text-sm">
              {item.term} · {item.mentor} · {item.status}
            </p>
          ))}
        </Panel>
        <Panel title="Notifications">
          {meetings.length ? (
            meetings.map((item, index) => (
              <p key={index} className="border-t py-2 text-sm">
                Meeting: {item.date}
              </p>
            ))
          ) : (
            <p className="text-sm text-slate-500">No upcoming meetings.</p>
          )}
          {tasks.map((item) => (
            <p key={item.id} className="border-t py-2 text-sm">
              Task: {item.title}
            </p>
          ))}
        </Panel>
      </div>
    </>
  )
}

export function MyMentorship({ user, data, updateData, onChat }) {
  const request =
    data.requests.find((item) => item.student === user.name && item.status === 'Accepted') ||
    data.requests.find((item) => item.student === user.name && item.status === 'Ended')
  const tasks = data.tasks.filter((item) => item.student === user.name)
  const meetingsHeld = request
    ? data.meetings.filter(
        (item) => item.student === user.name && item.mentor === request.mentor && new Date(item.date) < new Date(),
      ).length
    : 0
  const messages = data.messages.filter(
    (item) =>
      (item.from === user.name && item.to === request?.mentor) ||
      (item.to === user.name && item.from === request?.mentor),
  )
  if (!request)
    return (
      <>
        <Title>My mentorship</Title>
        <Panel>
          <p className="text-sm">No assigned mentor.</p>
          {data.requests
            .filter((item) => item.student === user.name)
            .map((item) => (
              <p key={item.id} className="mt-2 text-sm">
                {item.mentor} · {item.status}
              </p>
            ))}
        </Panel>
      </>
    )
  return (
    <>
      <Title>My mentorship</Title>
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title={`Mentor: ${request.mentor}`}>
          <p className="text-sm">
            Meetings held this term: {meetingsHeld} / {data.term.minMeetings}
          </p>
          <h3 className="mb-2 mt-4 font-medium">Chat</h3>
          <div className="mb-2 flex max-h-36 flex-col gap-2 overflow-auto">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`rounded-2xl px-3 py-2 text-sm ${item.from === user.name ? 'ml-auto bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-700'}`}
              >
                <b>{item.from}:</b> {item.text}
              </div>
            ))}
          </div>
          <form className="flex gap-2" onSubmit={(event) => onChat(event, request.mentor)}>
            <input className={input} name="message" placeholder="Message" required />
            <button className={button}>Send</button>
          </form>
          <form
            className="mt-4 grid gap-2 border-t pt-3 sm:grid-cols-[1fr_auto]"
            onSubmit={(event) => {
              event.preventDefault()
              const date = new FormData(event.currentTarget).get('date')
              updateData((current) => ({
                ...current,
                meetings: [...current.meetings, { student: user.name, mentor: request.mentor, date }],
              }))
              event.currentTarget.reset()
            }}
          >
            <label className="text-sm">
              Schedule meeting
              <input className={`${input} mt-1`} name="date" type="datetime-local" required />
            </label>
            <button className={`${outline} self-end`}>Schedule</button>
          </form>
        </Panel>
        <Panel title="Tasks">
          <div className="grid gap-2">
            {tasks.map((item) => (
              <label key={item.id} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={item.done}
                  onChange={() =>
                    updateData((current) => ({
                      ...current,
                      tasks: current.tasks.map((task) => (task.id === item.id ? { ...task, done: !task.done } : task)),
                    }))
                  }
                />
                {item.title}
              </label>
            ))}
          </div>
          <h3 className="mb-2 mt-5 font-medium">End of term feedback</h3>
          {request.status === 'Ended' ? (
            <form
              className="grid gap-2"
              onSubmit={(event) => {
                event.preventDefault()
                const form = new FormData(event.currentTarget)
                updateData((current) => ({
                  ...current,
                  students: current.students.map((item) =>
                    item.name === user.name
                      ? {
                          ...item,
                          feedback: `${form.get('rating')} / 5`,
                          feedbackComment: form.get('comment'),
                        }
                      : item,
                  ),
                }))
                alert('Feedback submitted.')
              }}
            >
              <div className="flex gap-2">
                <select className={input} name="rating" aria-label="Rating">
                  <option>5</option>
                  <option>4</option>
                  <option>3</option>
                  <option>2</option>
                  <option>1</option>
                </select>
                <input className={input} name="comment" placeholder="Comment" />
              </div>
              <button className={button}>Submit</button>
            </form>
          ) : (
            <p className="text-sm text-slate-500">Available after the mentorship ends.</p>
          )}
        </Panel>
      </div>
    </>
  )
}

export function HistoryPage({ role, user, data }) {
  const ended = data.requests.filter(
    (item) => item.status === 'Ended' && (role === 'student' ? item.student === user.name : item.mentor === user.name),
  )
  const records = ended.map((item) => {
    const person = role === 'student' ? item.mentor : item.student
    const meetings = data.meetings.filter(
      (meeting) => meeting.student === item.student && meeting.mentor === item.mentor,
    ).length
    const messages = data.messages.filter(
      (message) =>
        (message.from === item.student && message.to === item.mentor) ||
        (message.from === item.mentor && message.to === item.student),
    ).length
    return {
      term: item.term,
      person,
      meetings,
      note: `${messages} chat messages`,
    }
  })
  return (
    <>
      <Title>History</Title>
      <Panel title="Previous terms">
        {[...records, ...data.history.filter((item) => item.role === role)].map((item, index) => (
          <div key={`${item.term}-${item.person}-${index}`} className="border-t py-3 text-sm">
            <b>{item.term}</b>
            <p className="mt-1">
              {role === 'student' ? 'Mentor' : 'Student'}: {item.person} · {item.meetings} meetings
            </p>
            <p className="mt-1 text-slate-500">{item.note}</p>
          </div>
        ))}
      </Panel>
    </>
  )
}

const STUDENT_HELP_TYPES = ['Mentor change request', 'Mentor not responding', 'Mentor unavailable or inactive', 'Scheduling or meeting problems', 'Mentorship-related complaints', 'Technical issues', 'Academic or career guidance concerns', 'Other issues']
const MENTOR_HELP_TYPES = ['Student disciplinary or misconduct concerns', 'Student not attending meetings', 'Student not responding', 'Inappropriate behaviour', 'Mentorship conflicts', 'Mentee reassignment requests', 'Scheduling problems', 'Student participation concerns', 'Technical issues', 'Other mentorship-related problems']
const PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']
const HELP_STATUSES = ['Submitted', 'Under Review', 'Additional Information Required', 'Approved', 'Rejected', 'Resolved', 'Closed']

function friendlyDate(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return String(value).slice(0, 10)
  return d.toLocaleString()
}

export function HelpPage({ user, data, onSubmit, updateData }) {
  const isMentor = user.role === 'mentor'
  const types = isMentor ? MENTOR_HELP_TYPES : STUDENT_HELP_TYPES
  const tickets = (data.tickets || []).filter((item) => item.name === user.name && item.role === user.role)
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const [priority, setPriority] = useState('')
  const [infoText, setInfoText] = useState({})
  const [msg, setMsg] = useState('')
  const [saving, setSaving] = useState(false)
  const [selectedType, setSelectedType] = useState(types[0])
  const isMentorChange = /mentor change|reassignment/i.test(selectedType)
  const isConduct = /disciplinary|misconduct/i.test(selectedType)

  const filtered = tickets.filter(
    (item) =>
      (!category || (item.type || '').toLowerCase().includes(category.toLowerCase())) &&
      (!status || item.status === status) &&
      (!priority || (item.priority || '') === priority),
  )

  async function handleSubmit(event) {
    event.preventDefault()
    setSaving(true)
    setMsg('')
    try {
      await onSubmit(event)
      setMsg('Ticket submitted. Track its status below — IIC updates will appear on this page.')
    } catch (err) {
      setMsg(`Saved locally, but server sync failed: ${err.message}`)
    } finally {
      setSaving(false)
      event.currentTarget?.reset?.()
    }
  }

  async function sendInfo(ticketId) {
    const text = (infoText[ticketId] || '').trim()
    if (!text) return
    try {
      const res = await apiRequest(`/help-requests/${ticketId}/messages`, {
        method: 'POST',
        body: JSON.stringify({ message: text }),
      })
      const message = res.message || { sender_name: user.name, message: text, created_at: new Date().toISOString() }
      if (updateData) {
        updateData((current) => ({
          ...current,
          tickets: (current.tickets || []).map((item) =>
            item.id === ticketId ? { ...item, messages: [...(item.messages || []), message] } : item,
          ),
        }))
      }
      setInfoText((prev) => ({ ...prev, [ticketId]: '' }))
      setMsg('Additional information shared with IIC.')
    } catch (err) {
      setMsg(err.message)
    }
  }

  return (
    <>
      <Title>Help &amp; Contact IIC</Title>
      {msg && <div className="mb-4 rounded-xl bg-indigo-50 p-3 text-sm font-medium text-indigo-800">{msg}</div>}
      <div className="grid gap-4 lg:grid-cols-2">
        <Panel title={isMentor ? 'Contact IIC — Mentor' : 'Contact IIC — Student'} subtitle="Requests go to IIC administrators. You can track status, replies and history here.">
          <form className="grid gap-3" onSubmit={handleSubmit}>
            <label className="text-sm">
              Request type
              <select className={`${input} mt-1`} name="type" value={selectedType} onChange={(e) => setSelectedType(e.target.value)}>
                {types.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </label>
            <label className="text-sm">
              Priority / urgency
              <select className={`${input} mt-1`} name="priority">
                {PRIORITIES.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </label>
            {isMentorChange && (
              <>
                <label className="text-sm">
                  Current mentor
                  <input className={`${input} mt-1`} name="current_mentor" placeholder="Current mentor name" />
                </label>
                <label className="text-sm">
                  Reason for change
                  <input className={`${input} mt-1`} name="reason_change" placeholder="e.g. Mentor unavailable, not responding" />
                </label>
              </>
            )}
            {isConduct && (
              <>
                <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
                  <b>Confidential:</b> disciplinary reports are reviewed only by authorized IIC administrators. Nothing is decided automatically — the intervention and decision history is recorded for audit.
                </div>
                <label className="text-sm">
                  Student involved
                  <input className={`${input} mt-1`} name="student_involved" placeholder="Student name" required />
                </label>
                <label className="text-sm">
                  Related mentorship
                  <input className={`${input} mt-1`} name="mentorship_related" placeholder="Which mentorship / term" />
                </label>
                <label className="text-sm">
                  Incident category
                  <input className={`${input} mt-1`} name="incident_category" placeholder="e.g. Missed meetings, misconduct" />
                </label>
                <label className="text-sm">
                  Incident date
                  <input className={`${input} mt-1`} type="date" name="incident_date" />
                </label>
              </>
            )}
            <label className="text-sm">
              Detailed explanation
              <textarea className={`${input} mt-1`} name="description" placeholder="Describe the issue in detail" required rows={5} />
            </label>
            <label className="text-sm">
              Supporting documents / evidence (optional)
              <input className={`${input} mt-1`} type="file" name="supporting_files" multiple />
            </label>
            <button className={button} disabled={saving}>{saving ? 'Submitting…' : 'Submit request'}</button>
          </form>
        </Panel>

        <div className="grid content-start gap-4">
          <Panel title="Request tracking" subtitle="Filter by category, status and priority.">
            <div className="mb-3 grid gap-2 sm:grid-cols-3">
              <select className={input} value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">All categories</option>
                {types.map((t) => (
                  <option key={t} value={t}>{t}</option>
                ))}
              </select>
              <select className={input} value={status} onChange={(e) => setStatus(e.target.value)}>
                <option value="">All statuses</option>
                {HELP_STATUSES.map((s) => (
                  <option key={s}>{s}</option>
                ))}
              </select>
              <select className={input} value={priority} onChange={(e) => setPriority(e.target.value)}>
                <option value="">All priorities</option>
                {PRIORITIES.map((p) => (
                  <option key={p}>{p}</option>
                ))}
              </select>
            </div>
            {filtered.length ? (
              filtered.map((item) => (
                <div key={item.id} className="border-t py-3 text-sm">
                  <div className="flex flex-wrap items-center gap-2">
                    <b>{item.type}</b>
                    <Chip>{item.status || 'Submitted'}</Chip>
                    {item.priority && <Chip>{item.priority}</Chip>}
                    {item.confidential && <Chip>Confidential</Chip>}
                  </div>
                  <p className="mt-1 whitespace-pre-wrap">{item.description}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    {friendlyDate(item.created_at)}
                    {item.assigned_admin ? ` · Assigned to ${item.assigned_admin}` : ''}
                  </p>
                  {item.current_mentor && <p className="mt-1 text-xs">Current mentor: {item.current_mentor}</p>}
                  {item.reason_change && <p className="mt-1 text-xs">Reason: {item.reason_change}</p>}
                  {item.student_involved && <p className="mt-1 text-xs">Student involved: {item.student_involved}</p>}
                  {item.reply && <p className="mt-2 rounded-lg bg-slate-50 p-2 text-xs">IIC: {item.reply}</p>}
                  {item.resolution_notes && <p className="mt-1 text-xs">Resolution: {item.resolution_notes}</p>}
                  {item.messages?.length > 0 && (
                    <div className="mt-2 grid gap-1">
                      {item.messages.map((m, idx) => (
                        <p key={idx} className="text-xs">
                          <b>{m.sender_name}:</b> {m.message}
                        </p>
                      ))}
                    </div>
                  )}
                  {item.interventions?.length > 0 && (
                    <details className="mt-2 text-xs">
                      <summary className="cursor-pointer font-medium">Resolution history ({item.interventions.length})</summary>
                      {item.interventions.map((iv, idx) => (
                        <p key={idx} className="mt-1">
                          {friendlyDate(iv.performed_at)} · {iv.action} · {iv.decision || iv.resolution || ''}
                        </p>
                      ))}
                    </details>
                  )}
                  <div className="mt-2 flex gap-2">
                    <input
                      className={input}
                      placeholder="Provide additional information…"
                      value={infoText[item.id] || ''}
                      onChange={(e) => setInfoText((prev) => ({ ...prev, [item.id]: e.target.value }))}
                    />
                    <button className={outline} onClick={() => sendInfo(item.id)}>Share</button>
                  </div>
                </div>
              ))
            ) : (
              <p className="text-sm text-slate-500">No requests match.</p>
            )}
          </Panel>
        </div>
      </div>
    </>
  )
}
