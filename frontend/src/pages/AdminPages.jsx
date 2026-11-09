import { useState } from 'react'
import { fields, termLabel } from '../data'
import { Panel, Title, DataTable, Chip, input, button, outline, StatCard } from '../ui'
import { apiRequest } from '../api'

export function AdminDashboard({ data }) {
  const open = (data.tickets || []).filter((item) => !['Resolved', 'Closed', 'Approved', 'Rejected'].includes(item.status))
  return (
    <>
      <Title>Admin dashboard</Title>
      <div className="mb-4 grid gap-3 sm:grid-cols-3">
        <StatCard label="Students" value={data.students.length} />
        <StatCard label="Mentors" value={data.mentors.length} hint="Total listed mentors" />
        <StatCard label="Open tickets" value={open.length} hint="Awaiting response" />
      </div>
      <Panel title="Latest help tickets">
        {open.slice(0, 4).map((item) => (
          <p key={item.id} className="border-t py-2 text-sm">
            {item.name} · {item.type}
          </p>
        ))}
      </Panel>
    </>
  )
}

export function Approvals({ data, updateData, onActivate }) {
  return (
    <>
      <Title>Account approvals</Title>
      <Panel title="Mentors">
        <DataTable
          headers={['Name', 'Field', 'Status', 'Action']}
          rows={data.mentors.map((mentor) => [
            mentor.name,
            mentor.field,
            data.blacklisted.some((item) => item.name === mentor.name && (!item.role || item.role === 'mentor'))
              ? 'Blacklisted'
              : mentor.approved
                ? mentor.active
                  ? 'Approved'
                  : 'Inactive'
                : 'Pending',
            data.blacklisted.some((item) => item.name === mentor.name && (!item.role || item.role === 'mentor')) ? (
              <button className={outline} onClick={() => onActivate(mentor.name, 'mentor')}>
                Activate
              </button>
            ) : (
              <button
                className={outline}
                onClick={() =>
                  updateData((current) => ({
                    ...current,
                    mentors: current.mentors.map((item) =>
                      item.id === mentor.id
                        ? {
                            ...item,
                            approved: true,
                            active: !item.approved || !item.active,
                          }
                        : item,
                    ),
                  }))
                }
              >
                {mentor.approved ? (mentor.active ? 'Deactivate' : 'Activate') : 'Approve'}
              </button>
            ),
          ])}
        />
      </Panel>
      <Panel title="Blacklisted accounts">
        {data.blacklisted.length ? (
          data.blacklisted.map((item) => (
            <p key={`${item.name}-${item.email}`} className="flex items-center justify-between border-t py-2 text-sm">
              {item.name} · {item.email || 'No email'}
              <button className={outline} onClick={() => onActivate(item.name, item.role)}>
                Activate
              </button>
            </p>
          ))
        ) : (
          <p className="text-sm text-slate-500">No blacklisted accounts.</p>
        )}
      </Panel>
    </>
  )
}

function blacklistAction(data, name, role, onBlacklist, onActivate) {
  const inactive = data.blacklisted.some((item) => item.name === name && (!item.role || item.role === role))
  return (
    <button className={outline} onClick={() => (inactive ? onActivate(name, role) : onBlacklist(name, role))}>
      {inactive ? 'Activate' : 'Blacklist'}
    </button>
  )
}

export function AdminStudents({ data, onBlacklist, onActivate }) {
  return (
    <>
      <Title>Students</Title>
      <Panel>
        <DataTable
          headers={['Name', 'Program', 'Mentor', 'Feedback', 'Action']}
          rows={data.students.map((item) => [
            item.name,
            item.program,
            item.mentor || 'None',
            item.feedback,
            blacklistAction(data, item.name, 'student', onBlacklist, onActivate),
          ])}
        />
      </Panel>
    </>
  )
}

export function AdminMentors({ data, onBlacklist, onActivate }) {
  const [field, setField] = useState('')
  const mentors = data.mentors.filter((item) => !field || item.field === field)
  return (
    <>
      <Title>Mentors</Title>
      <Panel>
        <select className={`${input} mb-3 max-w-xs`} value={field} onChange={(event) => setField(event.target.value)}>
          <option value="">All fields</option>
          {fields.map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <DataTable
          headers={['Name', 'Field', 'Max students', 'Assigned', 'Action']}
          rows={mentors.map((item) => [
            item.name,
            item.field,
            item.slots,
            data.requests.filter((request) => request.mentor === item.name && request.status === 'Accepted').length,
            blacklistAction(data, item.name, 'mentor', onBlacklist, onActivate),
          ])}
        />
      </Panel>
    </>
  )
}

export function HelpTickets({ data, updateData }) {
  const [selected, setSelected] = useState(null)
  const [category, setCategory] = useState('')
  const [status, setStatus] = useState('')
  const [priority, setPriority] = useState('')
  const [date, setDate] = useState('')
  const [banner, setBanner] = useState('')
  const [view, setView] = useState('all')
  const STATUSES = ['Submitted', 'Under Review', 'Additional Information Required', 'Approved', 'Rejected', 'Resolved', 'Closed']

  function notify(text) {
    setBanner(text)
    setTimeout(() => setBanner(''), 5000)
  }

  function patchTicket(id, patch) {
    updateData((current) => ({
      ...current,
      tickets: (current.tickets || []).map((item) => (item.id === id ? { ...item, ...patch } : item)),
    }))
  }

  async function callApi(path, method, body, successMsg) {
    try {
      await apiRequest(path, { method, body: body ? JSON.stringify(body) : undefined })
      notify(successMsg)
    } catch (err) {
      notify(err.message)
    }
  }

  async function changeStatus(ticket, nextStatus) {
    const resolution = window.prompt(`Resolution notes for "${nextStatus}" (optional):`, '')
    if (resolution === null) return
    await callApi(`/admin/help-requests/${ticket.id}/status`, 'PATCH', { status: nextStatus, resolution_notes: resolution, decision: nextStatus === 'Approved' ? 'Approved' : nextStatus === 'Rejected' ? 'Rejected' : '' }, `Status set to ${nextStatus}`)
    patchTicket(ticket.id, { status: nextStatus, resolution_notes: resolution, reply: nextStatus === 'Resolved' ? resolution : ticket.reply })
    if (selected?.id === ticket.id) setSelected({ ...selected, status: nextStatus, resolution_notes: resolution })
  }

  async function assignTicket(ticket) {
    const name = window.prompt('Assign to administrator (name):', ticket.assigned_admin || 'IIC Admin')
    if (name === null) return
    await callApi(`/admin/help-requests/${ticket.id}/assign`, 'POST', { assigned_admin: name }, 'Ticket assigned')
    patchTicket(ticket.id, { assigned_admin: name })
    if (selected?.id === ticket.id) setSelected({ ...selected, assigned_admin: name })
  }

  async function sendInternal(ticket, message, internal) {
    if (!message?.trim()) return
    await callApi(`/help-requests/${ticket.id}/messages`, 'POST', { message, is_internal: internal }, internal ? 'Internal note added' : 'Message sent to requester')
    patchTicket(ticket.id, { reply: internal ? ticket.reply : message, messages: [...(ticket.messages || []), { sender_name: 'IIC Admin', message, is_internal: internal, created_at: new Date().toISOString() }] })
    if (selected?.id === ticket.id) setSelected({ ...selected, reply: internal ? selected.reply : message })
  }

  async function logIntervention(ticket, form) {
    const performed_by = form.get('performed_by') || ''
    const action = form.get('action') || 'Note'
    const notes = form.get('notes') || ''
    const decision = form.get('decision') || ''
    const resolution = form.get('resolution') || ''
    await callApi(`/admin/help-requests/${ticket.id}/interventions`, 'POST', { performed_by, action, notes, decision, resolution }, 'Intervention logged')
    patchTicket(ticket.id, { interventions: [...(ticket.interventions || []), { performed_by, action, notes, decision, resolution, performed_at: new Date().toISOString() }] })
  }

  const base = data.tickets || []
  const byView = view === 'mentor-change'
    ? base.filter((t) => /mentor change/i.test(t.type || ''))
    : view === 'disciplinary'
      ? base.filter((t) => /conduct|disciplinary|misconduct/i.test(t.type || '') || t.confidential)
      : base
  const filtered = byView.filter(
    (item) =>
      (!category || (item.type || '').toLowerCase().includes(category.toLowerCase())) &&
      (!status || item.status === status) &&
      (!priority || (item.priority || '') === priority) &&
      (!date || String(item.created_at || '').slice(0, 10) === date),
  )

  if (selected) {
    const t = selected
    return (
      <>
        <Title>Help request detail</Title>
        {banner && <div className="mb-4 rounded-xl bg-indigo-50 p-3 text-sm text-indigo-800">{banner}</div>}
        <Panel title={`${t.name} · ${t.type}`}>
          <button className={outline} onClick={() => setSelected(null)}>Back</button>
          {t.confidential && <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900"><b>Confidential disciplinary report.</b> Only authorized administrators may review. No automatic punishment — record your decision and intervention history.</div>}
          <dl className="mt-3 grid gap-2 text-sm">
            <div>Status: <Chip>{t.status || 'Submitted'}</Chip> {t.priority ? <Chip>{t.priority}</Chip> : null}</div>
            <div>Requester: {t.name} ({t.role || ''}) · {t.user_email || ''}</div>
            <div>Reported: {t.created_at ? new Date(t.created_at).toLocaleString() : '—'}</div>
            <div>Assigned: {t.assigned_admin || 'Unassigned'}</div>
            <div>Description: {t.description}</div>
            {t.current_mentor && <div>Current mentor: {t.current_mentor}</div>}
            {t.reason_change && <div>Reason: {t.reason_change}</div>}
            {t.student_involved && <div>Student involved: {t.student_involved} · Mentorship: {t.mentorship_related || '—'}</div>}
            {t.incident_category && <div>Incident: {t.incident_category} on {t.incident_date || '—'}</div>}
            {t.supporting_info && <div>Supporting info: {t.supporting_info}</div>}
            {t.reply && <div>IIC reply: {t.reply}</div>}
            {t.resolution_notes && <div>Resolution: {t.resolution_notes}</div>}
          </dl>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            <div>
              <label className="text-sm">Change status
                <select className={`${input} mt-1`} value={t.status || 'Submitted'} onChange={(e) => changeStatus(t, e.target.value)}>
                  {STATUSES.map((s) => <option key={s}>{s}</option>)}
                </select>
              </label>
              <div className="mt-2 flex flex-wrap gap-2">
                <button className={outline} onClick={() => changeStatus(t, 'Approved')}>Approve</button>
                <button className={outline} onClick={() => changeStatus(t, 'Rejected')}>Reject</button>
                <button className={outline} onClick={() => changeStatus(t, 'Additional Information Required')}>Request more info</button>
                <button className={outline} onClick={() => changeStatus(t, 'Resolved')}>Resolve</button>
                <button className={outline} onClick={() => changeStatus(t, 'Closed')}>Close</button>
                <button className={button} onClick={() => assignTicket(t)}>Assign admin</button>
              </div>
            </div>
            <form onSubmit={(e) => { e.preventDefault(); sendInternal(t, new FormData(e.currentTarget).get('message'), e.currentTarget.is_internal?.checked) }}>
              <label className="text-sm">Communicate with requester
                <textarea className={`${input} mt-1`} name="message" rows={2} placeholder="Reply or internal note" required />
              </label>
              <label className="mt-2 flex items-center gap-2 text-xs">
                <input type="checkbox" name="is_internal" /> Internal note (not shown to requester)
              </label>
              <button className={`${button} mt-2`} type="submit">Send</button>
            </form>
          </div>

          <form className="mt-4 grid gap-2 rounded-xl border p-3 sm:grid-cols-2" onSubmit={(e) => { e.preventDefault(); logIntervention(t, new FormData(e.currentTarget)); e.currentTarget.reset() }}>
            <b className="text-sm sm:col-span-2">Record intervention &amp; decision (audit trail)</b>
            <input className={input} name="performed_by" placeholder="Performed by" />
            <select className={input} name="action"><option>Review</option><option>Note</option><option>Decision</option><option>Reassignment</option></select>
            <input className={input} name="decision" placeholder="Decision (e.g. Warning issued, Mentor reassigned)" />
            <input className={input} name="resolution" placeholder="Resolution summary" />
            <textarea className={`${input} sm:col-span-2`} name="notes" placeholder="Intervention notes" rows={2} />
            <button className={`${button} sm:col-span-2`}>Log intervention</button>
          </form>

          {(t.messages || []).length > 0 && (
            <div className="mt-4">
              <b className="text-sm">Conversation</b>
              {(t.messages || []).map((m, i) => (
                <p key={i} className="text-sm">{m.sender_name}: {m.message} {m.is_internal ? '(internal)' : ''}</p>
              ))}
            </div>
          )}
          {(t.interventions || []).length > 0 && (
            <div className="mt-4">
              <b className="text-sm">Intervention history</b>
              {(t.interventions || []).map((iv, i) => (
                <p key={i} className="text-sm">{iv.performed_at ? new Date(iv.performed_at).toLocaleString() : ''} · {iv.action} · {iv.performed_by} · {iv.notes} · {iv.decision || iv.resolution || ''}</p>
              ))}
            </div>
          )}
        </Panel>
      </>
    )
  }

  return (
    <>
      <Title>Help Request Management</Title>
      {banner && <div className="mb-4 rounded-xl bg-indigo-50 p-3 text-sm text-indigo-800">{banner}</div>}
      <div className="mb-3 flex flex-wrap gap-2">
        {[['all', 'All requests'], ['mentor-change', 'Mentor change approvals'], ['disciplinary', 'Disciplinary reports']].map(([key, label]) => (
          <button key={key} className={view === key ? button : outline} onClick={() => setView(key)}>{label}</button>
        ))}
      </div>
      <Panel subtitle="Unified support dashboard: filter by category, status, priority and date; assign, communicate, decide and log interventions.">
        <div className="mb-3 grid gap-2 sm:grid-cols-4">
          <select className={input} value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">All categories</option>
            <option value="Mentor change">Mentor change</option>
            <option value="Conduct">Conduct</option>
            <option value="Technical">Technical</option>
            <option value="Scheduling">Scheduling</option>
            <option value="Other">Other</option>
          </select>
          <select className={input} value={status} onChange={(e) => setStatus(e.target.value)}>
            <option value="">All statuses</option>
            {STATUSES.map((s) => <option key={s}>{s}</option>)}
          </select>
          <select className={input} value={priority} onChange={(e) => setPriority(e.target.value)}>
            <option value="">All priorities</option>
            <option>Low</option><option>Medium</option><option>High</option><option>Urgent</option>
          </select>
          <input className={input} type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <DataTable
          headers={['Requester', 'Type', 'Priority', 'Description', 'Status', 'Assigned', '']}
          rows={filtered.map((item) => [
            item.name,
            item.type,
            item.priority || '—',
            item.description,
            item.status || 'Submitted',
            item.assigned_admin || '—',
            <button className={outline} onClick={() => setSelected(item)}>Open</button>,
          ])}
        />
        {!filtered.length && <p className="py-3 text-sm text-slate-500">No requests match.</p>}
      </Panel>
    </>
  )
}

export function Statistics({ data, onDownload }) {
  const [term, setTerm] = useState(termLabel(data.term))
  const termRequests = data.requests.filter((item) => item.term === term)
  const termHistory = data.history.filter((item) => item.term === term)
  const termStudents = new Set([
    ...termRequests.map((item) => item.student),
    ...termHistory.filter((item) => item.role === 'student').map((item) => item.person),
  ]).size
  const termMentorNames = new Set([
    ...termRequests.filter((item) => ['Accepted', 'Ended'].includes(item.status)).map((item) => item.mentor),
    ...termHistory.filter((item) => item.role === 'student').map((item) => item.person),
  ])
  const termMentors = termMentorNames.size
  const ratings = data.students.map((item) => Number.parseFloat(item.feedback)).filter(Number.isFinite)
  const average = ratings.length
    ? `${(ratings.reduce((sum, item) => sum + item, 0) / ratings.length).toFixed(1)} / 5`
    : '—'
  return (
    <>
      <Title>Statistics</Title>
      <div className="mb-3 flex gap-2">
        <select className={`${input} max-w-xs`} value={term} onChange={(event) => setTerm(event.target.value)}>
          {[
            ...new Set([
              termLabel(data.term),
              ...data.requests.map((item) => item.term),
              ...data.history.map((item) => item.term),
            ]),
          ].map((item) => (
            <option key={item}>{item}</option>
          ))}
        </select>
        <button className={outline} onClick={onDownload}>
          Download report
        </button>
      </div>
      <div className="grid gap-3 sm:grid-cols-3">
        <Panel title="Students this term">
          <b className="text-2xl">{termStudents}</b>
        </Panel>
        <Panel title="Mentors assigned">
          <b className="text-2xl">{termMentors}</b>
        </Panel>
        <Panel title="Average feedback">
          <b className="text-2xl">{average}</b>
        </Panel>
      </div>
      <Panel title={`Mentors by field · ${term}`}>
        <div className="grid gap-3">
          {fields.map((field) => {
            const count = data.mentors.filter(
              (mentor) => mentor.field === field && (term === termLabel(data.term) || termMentorNames.has(mentor.name)),
            ).length
            const maxCount = Math.max(
              1,
              ...fields.map((f) =>
                data.mentors.filter(
                  (mentor) => mentor.field === f && (term === termLabel(data.term) || termMentorNames.has(mentor.name)),
                ).length,
              ),
            )
            return (
              <div key={field}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">{field}</span>
                  <span className="text-slate-500">{count}</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-all duration-500"
                    style={{ width: `${(count / maxCount) * 100}%` }}
                  />
                </div>
              </div>
            )
          })}
        </div>
      </Panel>
    </>
  )
}

export function TermSettings({ data, updateData }) {
  const [saved, setSaved] = useState(false)
  function save(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    updateData((current) => ({
      ...current,
      term: {
        start: form.get('start'),
        close: form.get('close'),
        end: form.get('end'),
        minMeetings: Number(form.get('minMeetings')),
      },
    }))
    setSaved(true)
  }
  return (
    <>
      <Title>Term settings</Title>
      <Panel>
        <form className="grid gap-3 sm:grid-cols-2" onSubmit={save}>
          <label className="text-sm">
            Request window opens
            <input className={`${input} mt-1`} name="start" type="date" defaultValue={data.term.start} />
          </label>
          <label className="text-sm">
            Request window closes
            <input className={`${input} mt-1`} name="close" type="date" defaultValue={data.term.close} />
          </label>
          <label className="text-sm">
            Term end
            <input className={`${input} mt-1`} name="end" type="date" defaultValue={data.term.end} />
          </label>
          <label className="text-sm">
            Minimum meetings
            <input
              className={`${input} mt-1`}
              name="minMeetings"
              type="number"
              min="1"
              defaultValue={data.term.minMeetings}
            />
          </label>
          <button className={`${button} sm:col-span-2`}>Save settings</button>
          {saved && <p className="text-sm text-indigo-700 sm:col-span-2">Settings saved.</p>}
        </form>
      </Panel>
    </>
  )
}
