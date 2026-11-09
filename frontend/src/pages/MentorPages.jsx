import { useState } from 'react'
import { Panel, Title, Chip, DataTable, input, button, outline } from '../ui'

export function MentorRequests({ user, data, setStatus }) {
  const requests = data.requests.filter((item) => item.mentor === user.name)
  return (
    <>
      <Title>Requests</Title>
      <Panel>
        {requests.length ? (
          <div className="grid gap-3">
            {requests.map((item) => (
              <div key={item.id} className="rounded-xl border border-slate-200 p-4 transition hover:border-slate-300 hover:shadow-card">
                <div className="flex items-center justify-between">
                  <b>{item.student}</b>
                  <Chip>{item.status}</Chip>
                </div>
                <p className="mt-2 text-sm">Goal: {item.goal}</p>
                <p className="mt-1 text-sm text-slate-500">Message: {item.message || '—'}</p>
                {item.status === 'Pending' && (
                  <div className="mt-3 flex gap-2">
                    <button className={button} onClick={() => setStatus(item.id, 'Accepted')}>
                      Accept
                    </button>
                    <button className={outline} onClick={() => setStatus(item.id, 'Declined')}>
                      Decline
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No requests.</p>
        )}
      </Panel>
    </>
  )
}

export function MyStudents({ user, data, updateData, onChat, setStatus }) {
  const students = data.requests.filter(
    (item) => item.mentor === user.name && ['Accepted', 'Ended'].includes(item.status),
  )
  const [selected, setSelected] = useState('')
  const [task, setTask] = useState('')
  const messages = data.messages.filter((item) => item.from === selected || item.to === selected)

  function assignTask(event) {
    event.preventDefault()
    if (!task.trim()) return
    updateData((current) => ({
      ...current,
      tasks: [...current.tasks, { id: Date.now(), student: selected, title: task, done: false }],
    }))
    setTask('')
  }

  return (
    <>
      <Title>My students</Title>
      <div className="grid gap-4 lg:grid-cols-[250px_1fr]">
        <Panel title="This term">
          {students.length ? (
            students.map((item) => (
              <button
                key={item.id}
                onClick={() => setSelected(item.student)}
                className={`mb-2 w-full rounded-xl border p-3 text-left text-sm transition ${selected === item.student ? 'border-indigo-600 bg-indigo-50' : 'border-slate-200 hover:border-slate-300'}`}
              >
                <b className="block">{item.student}</b>
                <span className="text-slate-500">{item.term}</span>
              </button>
            ))
          ) : (
            <p className="text-sm text-slate-500">No students yet.</p>
          )}
        </Panel>
        {selected ? (
          <div className="grid gap-4">
            <Panel title="Tasks">
              <div className="grid gap-2">
                {data.tasks
                  .filter((item) => item.student === selected)
                  .map((item) => (
                    <p key={item.id} className="text-sm">
                      {item.done ? '✓' : '○'} {item.title}
                    </p>
                  ))}
              </div>
              <form className="mt-3 flex gap-2" onSubmit={assignTask}>
                <input
                  className={input}
                  value={task}
                  onChange={(event) => setTask(event.target.value)}
                  placeholder="New task"
                />
                <button className={button}>Assign</button>
              </form>
            </Panel>
            <Panel title="Chat">
              <div className="mb-3 max-h-36 overflow-auto">
                {messages.map((item, index) => (
                  <p key={index} className="text-sm">
                    <b>{item.from}:</b> {item.text}
                  </p>
                ))}
              </div>
              <form className="flex gap-2" onSubmit={(event) => onChat(event, selected)}>
                <input className={input} name="message" placeholder="Message" required />
                <button className={button}>Send</button>
              </form>
              <button
                className={`${outline} mt-3`}
                onClick={() => {
                  const request = students.find((item) => item.student === selected)
                  if (request?.status === 'Accepted') setStatus(request.id, 'Ended')
                }}
              >
                End mentorship
              </button>
            </Panel>
          </div>
        ) : (
          <Panel>
            <p className="text-sm text-slate-500">Select a student.</p>
          </Panel>
        )}
      </div>
    </>
  )
}

export function MentorProfile({ user, data, updateData }) {
  const mentor = data.mentors.find((item) => item.name === user.name) || data.mentors[0]
  function save(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    updateData((current) => ({
      ...current,
      mentors: current.mentors.map((item) =>
        item.id === mentor.id
          ? {
              ...item,
              title: form.get('title'),
              field: form.get('field'),
              industry: form.get('industry'),
              background: form.get('background'),
              bio: form.get('background'),
              linkedin: form.get('linkedin'),
              mode: form.get('mode'),
              hours: form.get('hours'),
              slots: Number(form.get('slots')),
            }
          : item,
      ),
    }))
  }
  return (
    <>
      <Title>Mentor profile</Title>
      <Panel>
        <form className="grid gap-4 sm:grid-cols-2" onSubmit={save}>
          <label className="text-sm">
            Name
            <input className={`${input} mt-1`} value={user.name} readOnly />
          </label>
          <label className="text-sm">
            Role
            <input className={`${input} mt-1`} name="title" defaultValue={mentor.title} />
          </label>
          <label className="text-sm">
            Expertise
            <input className={`${input} mt-1`} name="field" defaultValue={mentor.field} />
          </label>
          <label className="text-sm">
            Industry
            <input className={`${input} mt-1`} name="industry" defaultValue={mentor.industry} />
          </label>
          <label className="text-sm">
            LinkedIn
            <input className={`${input} mt-1`} name="linkedin" defaultValue={mentor.linkedin} />
          </label>
          <label className="text-sm">
            Weekly hours
            <select className={`${input} mt-1`} name="hours">
              <option>3-5 hours</option>
              <option>1-2 hours</option>
              <option>5+ hours</option>
            </select>
          </label>
          <label className="text-sm">
            Interaction mode
            <select className={`${input} mt-1`} name="mode">
              <option>Online</option>
              <option>Hybrid</option>
              <option>In person</option>
            </select>
          </label>
          <label className="text-sm">
            Max students
            <input className={`${input} mt-1`} name="slots" type="number" min="1" defaultValue={mentor.slots} />
          </label>
          <label className="text-sm sm:col-span-2">
            Background
            <textarea className={`${input} mt-1`} name="background" defaultValue={mentor.background} />
          </label>
          <button className={button}>Save profile</button>
          <p className="self-center text-sm text-slate-500">
            Status: {mentor.approved ? 'Approved' : 'Waiting for approval'}
          </p>
        </form>
      </Panel>
    </>
  )
}
