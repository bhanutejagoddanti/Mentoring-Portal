import { useState, useEffect } from 'react'
import { Panel, Title, Chip, input, button, outline } from '../ui'
import { apiRequest } from '../api'

const defaultCommunities = [
  {
    id: 1,
    name: 'Data Science & ML Hub',
    description: 'Discussions on ML algorithms, deep learning, kaggle competitions, and research.',
    category: 'ML',
    visibility: 'public',
    member_count: 42,
    joined: true,
  },
  {
    id: 2,
    name: 'FinTech & Quant Careers',
    description: 'Career prep for quantitative finance, financial analytics, and product strategy.',
    category: 'Finance',
    visibility: 'public',
    member_count: 28,
    joined: false,
  },
  {
    id: 3,
    name: 'Higher Studies & PhD Circle',
    description: 'Guidance on MS/PhD admissions, SOP writing, and faculty outreach.',
    category: 'Academia',
    visibility: 'public',
    member_count: 19,
    joined: false,
  },
  {
    id: 4,
    name: 'Founders & Startups Lab',
    description: 'Mentor-led incubator for student founders and early stage projects.',
    category: 'Business',
    visibility: 'public',
    member_count: 35,
    joined: false,
  },
]

export default function CommunityPage({ user, data, updateData }) {
  const [communities, setCommunities] = useState([])
  const [activeCommunity, setActiveCommunity] = useState(null)
  const [messages, setMessages] = useState([])
  const [events, setEvents] = useState([
    {
      id: 1,
      title: 'ML in Industry: Live Q&A with Senior Engineers',
      event_date: '2026-11-20T18:00',
      meeting_link: 'https://meet.google.com/bs-ml-qna',
    },
    {
      id: 2,
      title: 'Resume Review & Portfolio Showcase Webinar',
      event_date: '2026-11-25T17:00',
      meeting_link: 'https://meet.google.com/bs-resume-rev',
    },
  ])
  const [resources, setResources] = useState([
    { id: 1, title: 'IITM BS Placement Preparation Guide', url: 'https://example.com/guide.pdf' },
    { id: 2, title: 'Recommended ML Roadmap & Courses', url: 'https://example.com/ml-roadmap' },
  ])
  const [messageText, setMessageText] = useState('')
  const [creating, setCreating] = useState(false)
  const [reportModal, setReportModal] = useState(null)
  const [reportReason, setReportReason] = useState('')
  const [statusMsg, setStatusMsg] = useState('')
  const [communityRequests, setCommunityRequests] = useState([])
  const [approveModerators, setApproveModerators] = useState({})

  useEffect(() => {
    loadCommunities()
    loadRequests()
  }, [])

  async function loadRequests() {
    try {
      const res = await apiRequest('/community-requests')
      setCommunityRequests(res.items || res.requests || [])
    } catch {
      setCommunityRequests([])
    }
  }

  async function loadCommunities() {
    try {
      const res = await apiRequest('/communities')
      if (res && Array.isArray(res.items) && res.items.length > 0) {
        setCommunities(res.items)
        if (!activeCommunity) setActiveCommunity(res.items[0])
      } else {
        setCommunities(defaultCommunities)
        if (!activeCommunity) setActiveCommunity(defaultCommunities[0])
      }
    } catch {
      setCommunities(defaultCommunities)
      if (!activeCommunity) setActiveCommunity(defaultCommunities[0])
    }
  }

  useEffect(() => {
    if (activeCommunity) {
      loadMessages(activeCommunity.id)
    }
  }, [activeCommunity])

  async function loadMessages(cid) {
    try {
      const res = await apiRequest(`/communities/${cid}/messages`)
      if (res && Array.isArray(res.items)) {
        setMessages(res.items)
      } else {
        setMessages([])
      }
    } catch {
      setMessages([])
    }
  }

  async function handleJoinLeave(comm) {
    try {
      if (comm.joined) {
        await apiRequest(`/communities/${comm.id}/leave`, { method: 'POST' })
        setCommunities((prev) =>
          prev.map((c) => (c.id === comm.id ? { ...c, joined: false, member_count: Math.max(0, c.member_count - 1) } : c))
        )
      } else {
        await apiRequest(`/communities/${comm.id}/join`, { method: 'POST' })
        setCommunities((prev) =>
          prev.map((c) => (c.id === comm.id ? { ...c, joined: true, member_count: (c.member_count || 0) + 1 } : c))
        )
      }
    } catch (err) {
      // Local fallback for optimistic update
      setCommunities((prev) =>
        prev.map((c) =>
          c.id === comm.id
            ? {
                ...c,
                joined: !c.joined,
                member_count: c.joined ? Math.max(0, c.member_count - 1) : (c.member_count || 0) + 1,
              }
            : c
        )
      )
    }
  }

  async function handleSendMessage(e) {
    e.preventDefault()
    if (!messageText.trim() || !activeCommunity) return
    const newMsg = {
      id: Date.now(),
      community_id: activeCommunity.id,
      sender_name: user.name,
      content: messageText.trim(),
      created_at: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    }
    setMessages((prev) => [...prev, newMsg])
    const textToSend = messageText.trim()
    setMessageText('')
    try {
      await apiRequest(`/communities/${activeCommunity.id}/messages`, {
        method: 'POST',
        body: JSON.stringify({ content: textToSend }),
      })
    } catch (err) {
      console.warn('Message send API failed:', err)
    }
  }

  async function handleCreateCommunity(e) {
    e.preventDefault()
    const form = new FormData(e.currentTarget)
    const payload = {
      name: form.get('name'),
      community_name: form.get('name'),
      description: form.get('description'),
      category: form.get('category'),
      visibility: form.get('visibility'),
      purpose: form.get('purpose') || '',
      target_audience: form.get('target_audience') || '',
      community_type: form.get('community_type') || 'Discussion',
      reason: form.get('reason') || '',
      suggested_moderators: (form.get('suggested_moderators') || '').split(',').map((x) => x.trim()).filter(Boolean),
      supporting_info: form.get('supporting_info') || '',
    }
    try {
      if (user.role === 'admin') {
        const created = await apiRequest('/communities', { method: 'POST', body: JSON.stringify(payload) })
        const newComm = created.community || { id: Date.now(), ...payload, member_count: 1, joined: true }
        setCommunities((prev) => [newComm, ...prev])
        setActiveCommunity(newComm)
        setCreating(false)
        setStatusMsg('Community created successfully!')
      } else {
        const res = await apiRequest('/community-requests', { method: 'POST', body: JSON.stringify(payload) })
        setCommunityRequests((prev) => [res.request || payload, ...prev])
        setCreating(false)
        setStatusMsg('Community request submitted for IIC approval. Track its status below.')
      }
      setTimeout(() => setStatusMsg(''), 5000)
    } catch (err) {
      setStatusMsg(`Submission failed: ${err.message}`)
    }
  }

  async function handleCommunityDecision(req, decision) {
    const reason = decision === 'approved'
      ? ''
      : window.prompt(decision === 'rejected' ? 'Rejection reason:' : 'Modification note:', '')
    if (reason === null) return
    if (!window.confirm(`Confirm ${decision} for "${req.community_name}"?`)) return
    try {
      if (decision === 'approved') {
        const moderators = (approveModerators[req.id] || '').split(',').map((x) => x.trim()).filter(Boolean)
        const res = await apiRequest(`/community-requests/${req.id}/approve`, { method: 'POST', body: JSON.stringify({ moderators }) })
        if (res.community) setCommunities((prev) => [res.community, ...prev])
        setStatusMsg('Community approved and activated!')
      } else if (decision === 'rejected') {
        await apiRequest(`/community-requests/${req.id}/reject`, { method: 'POST', body: JSON.stringify({ reason }) })
        setStatusMsg('Community request rejected.')
      } else {
        await apiRequest(`/community-requests/${req.id}/request-changes`, { method: 'POST', body: JSON.stringify({ note: reason }) })
        setStatusMsg('Modifications requested.')
      }
      await loadRequests()
      await loadCommunities()
      setTimeout(() => setStatusMsg(''), 5000)
    } catch (err) {
      setStatusMsg(err.message)
    }
  }

  async function handleReportSubmit(e) {
    e.preventDefault()
    if (!reportModal || !reportReason.trim()) return
    try {
      await apiRequest(`/communities/${activeCommunity?.id}/report`, {
        method: 'POST',
        body: JSON.stringify({ message_id: reportModal.id, reason: reportReason.trim() }),
      })
      setStatusMsg('Content report submitted for admin review.')
    } catch {
      setStatusMsg('Report submitted.')
    }
    setReportModal(null)
    setReportReason('')
    setTimeout(() => setStatusMsg(''), 4000)
  }

  return (
    <>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Title>Communities & Networking</Title>
        <button className={button} onClick={() => setCreating(!creating)}>
          {creating ? 'Cancel' : user.role === 'admin' ? '+ Create Community' : '+ Request New Community'}
        </button>
      </div>

      {statusMsg && (
        <div className="mb-4 rounded-xl bg-indigo-50 p-3 text-sm font-medium text-indigo-800">{statusMsg}</div>
      )}

      {creating && (
        <Panel title={user.role === 'admin' ? 'Create a New Community' : 'Request New Community (IIC approval required)'}>
          <form className="grid gap-3 sm:grid-cols-2" onSubmit={handleCreateCommunity}>
            <label className="text-sm">
              Community Name
              <input className={`${input} mt-1`} name="name" placeholder="e.g. Web3 Developers Circle" required />
            </label>
            <label className="text-sm">
              Category
              <select className={`${input} mt-1`} name="category">
                <option>General</option>
                <option>ML</option>
                <option>IT</option>
                <option>Finance</option>
                <option>Business</option>
                <option>Academia</option>
              </select>
            </label>
            <label className="text-sm">
              Visibility
              <select className={`${input} mt-1`} name="visibility">
                <option value="public">Public (Open to all students & mentors)</option>
                <option value="private">Private (Invite & approval only)</option>
              </select>
            </label>
            <label className="text-sm">
              Purpose & Objectives
              <input className={`${input} mt-1`} name="purpose" placeholder="What will members achieve?" />
            </label>
            <label className="text-sm">
              Community Type
              <select className={`${input} mt-1`} name="community_type">
                <option>Discussion</option>
                <option>Study Group</option>
                <option>Project Team</option>
                <option>Club</option>
              </select>
            </label>
            <label className="text-sm sm:col-span-2">
              Description
              <textarea
                className={`${input} mt-1`}
                name="description"
                placeholder="What is this community about?"
                required
              />
            </label>
            <label className="text-sm">
              Target Audience
              <input className={`${input} mt-1`} name="target_audience" placeholder="e.g. BS Data Science students" />
            </label>
            <label className="text-sm">
              Suggested Moderators
              <input className={`${input} mt-1`} name="suggested_moderators" placeholder="Comma-separated names" />
            </label>
            <label className="text-sm">
              Reason for creating
              <input className={`${input} mt-1`} name="reason" placeholder="Why is this community needed?" />
            </label>
            <label className="text-sm">
              Supporting Information
              <input className={`${input} mt-1`} name="supporting_info" placeholder="Optional links or context" />
            </label>
            <button className={`${button} sm:col-span-2`}>{user.role === 'admin' ? 'Create Community' : 'Submit for Approval'}</button>
          </form>
        </Panel>
      )}

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <Panel title={user.role === 'admin' ? 'Community Creation Approvals' : 'My Community Requests'} subtitle={user.role === 'admin' ? 'Review, approve, reject or request changes. Only approved communities appear in discovery.' : 'Track your pending requests — IIC decision updates appear here.'}>
          {communityRequests.length ? communityRequests.map((req) => (
            <div key={req.id} className="border-t py-3 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <b>{req.community_name}</b>
                <Chip>{req.status || 'Pending'}</Chip>
                {req.category && <Chip>{req.category}</Chip>}
              </div>
              <p className="mt-1">{req.description}</p>
              <p className="mt-1 text-xs text-slate-500">{req.requester_name || ''} · {req.purpose || ''}</p>
              {req.rejection_reason && <p className="mt-1 text-xs text-red-700">Rejected: {req.rejection_reason}</p>}
              {req.moderation_note && <p className="mt-1 text-xs text-amber-700">Changes requested: {req.moderation_note}</p>}
              {req.reviewed_by && <p className="mt-1 text-xs text-slate-500">Reviewed by {req.reviewed_by} {req.reviewed_at ? new Date(req.reviewed_at).toLocaleString() : ''}</p>}
              {user.role === 'admin' && req.status === 'Pending' && (
                <div className="mt-2 grid gap-2">
                  <input
                    className={input}
                    placeholder="Assign moderators (comma-separated)"
                    value={approveModerators[req.id] || (req.suggested_moderators || []).join(', ')}
                    onChange={(e) => setApproveModerators((prev) => ({ ...prev, [req.id]: e.target.value }))}
                  />
                  <div className="flex flex-wrap gap-2">
                    <button className={button} onClick={() => handleCommunityDecision(req, 'approved')}>Approve & Activate</button>
                    <button className={outline} onClick={() => handleCommunityDecision(req, 'rejected')}>Reject</button>
                    <button className={outline} onClick={() => handleCommunityDecision(req, 'request-changes')}>Request Modifications</button>
                  </div>
                </div>
              )}
            </div>
          )) : <p className="text-sm text-slate-500">No community requests.</p>}
        </Panel>
      </div>

      <div className="mt-4 grid gap-6 lg:grid-cols-[300px_1fr]">
        <div className="space-y-4">
          <Panel title="Browse Groups">
            <div className="space-y-2">
              {communities.map((comm) => (
                <div
                  key={comm.id}
                  onClick={() => setActiveCommunity(comm)}
                  className={`cursor-pointer rounded-lg border p-3 transition ${
                    activeCommunity?.id === comm.id ? 'border-indigo-700 bg-indigo-50' : 'border-slate-200 bg-white hover:bg-slate-50'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <b className="text-sm text-slate-800">{comm.name}</b>
                    <Chip>{comm.category}</Chip>
                  </div>
                  <p className="mt-1 line-clamp-2 text-xs text-slate-600">{comm.description}</p>
                  <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                    <span>{comm.member_count || 1} members</span>
                    <button
                      className={`text-xs font-semibold ${comm.joined ? 'text-red-700 hover:underline' : 'text-indigo-700 hover:underline'}`}
                      onClick={(e) => {
                        e.stopPropagation()
                        handleJoinLeave(comm)
                      }}
                    >
                      {comm.joined ? 'Leave' : '+ Join'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Upcoming Events">
            <div className="space-y-3">
              {events.map((evt) => (
                <div key={evt.id} className="border-t pt-2 text-xs">
                  <b className="block text-slate-800">{evt.title}</b>
                  <span className="text-slate-500">{new Date(evt.event_date).toLocaleString()}</span>
                  <a
                    href={evt.meeting_link}
                    target="_blank"
                    rel="noreferrer"
                    className="mt-1 block text-indigo-700 underline"
                  >
                    Join Meeting
                  </a>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title="Shared Resources">
            <div className="space-y-2">
              {resources.map((res) => (
                <div key={res.id} className="border-t pt-2 text-xs">
                  <b className="block text-slate-800">{res.title}</b>
                  <a href={res.url} target="_blank" rel="noreferrer" className="text-indigo-700 underline">
                    Download Resource
                  </a>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        <div>
          {activeCommunity ? (
            <Panel
              title={activeCommunity.name}
              action={
                <div className="flex items-center gap-2">
                  <Chip>{activeCommunity.visibility}</Chip>
                  <button
                    className={activeCommunity.joined ? outline : button}
                    onClick={() => handleJoinLeave(activeCommunity)}
                  >
                    {activeCommunity.joined ? 'Leave Group' : 'Join Community'}
                  </button>
                </div>
              }
            >
              <p className="mb-4 text-xs text-slate-600">{activeCommunity.description}</p>

              <div className="mb-4 flex flex-col justify-between rounded-lg border border-slate-200 bg-slate-50 p-4 min-h-[360px]">
                <div className="space-y-3 overflow-y-auto max-h-[320px] pr-1">
                  {messages.length === 0 ? (
                    <p className="text-center text-sm text-slate-400 py-10">
                      No messages yet. Start the conversation!
                    </p>
                  ) : (
                    messages.map((m) => (
                      <div
                        key={m.id}
                        className={`rounded-2xl p-2.5 text-sm max-w-[85%] ${
                          m.sender_name === user.name
                            ? 'self-end bg-indigo-600 text-white border-indigo-600'
                            : 'self-start bg-white text-slate-800 border-slate-200'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 text-[11px] opacity-75 mb-1">
                          <b>{m.sender_name}</b>
                          <span>{m.created_at || 'Just now'}</span>
                        </div>
                        <p>{m.content}</p>
                        {m.sender_name !== user.name && (
                          <div className="mt-1 text-right">
                            <button
                              onClick={() => setReportModal(m)}
                              className="text-[10px] text-slate-400 hover:text-red-600"
                            >
                              Report
                            </button>
                          </div>
                        )}
                      </div>
                    ))
                  )}
                </div>

                <form className="mt-4 flex gap-2 border-t pt-3" onSubmit={handleSendMessage}>
                  <input
                    className={input}
                    value={messageText}
                    onChange={(e) => setMessageText(e.target.value)}
                    placeholder={activeCommunity.joined ? 'Write a message to the community...' : 'Join to participate in chat...'}
                    disabled={!activeCommunity.joined}
                  />
                  <button className={button} disabled={!activeCommunity.joined || !messageText.trim()}>
                    Send
                  </button>
                </form>
              </div>
            </Panel>
          ) : (
            <Panel>
              <p className="text-sm text-slate-500">Select a community from the left to view discussions.</p>
            </Panel>
          )}
        </div>
      </div>

      {reportModal && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4">
          <div className="w-full max-w-md rounded-xl bg-white p-5 shadow-xl">
            <h3 className="text-base font-semibold text-slate-800">Report Inappropriate Content</h3>
            <p className="mt-1 text-xs text-slate-500">
              Reporting message from <b>{reportModal.sender_name}</b>: &quot;{reportModal.content}&quot;
            </p>
            <form onSubmit={handleReportSubmit} className="mt-4 space-y-3">
              <label className="block text-xs font-medium text-slate-700">
                Reason for report:
                <textarea
                  className={`${input} mt-1`}
                  rows="3"
                  value={reportReason}
                  onChange={(e) => setReportReason(e.target.value)}
                  placeholder="Spam, harassment, violation of code of conduct..."
                  required
                />
              </label>
              <div className="flex justify-end gap-2">
                <button type="button" className={outline} onClick={() => setReportModal(null)}>
                  Cancel
                </button>
                <button type="submit" className="rounded-lg bg-red-700 px-4 py-2 text-sm text-white hover:bg-red-800">
                  Submit Report
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

