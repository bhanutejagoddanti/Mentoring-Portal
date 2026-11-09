import { useEffect, useState } from 'react'
import { apiLogin, apiRegister, apiRequest, setToken, apiLogout, apiMe } from './api'
import { localAccounts, loadData, navByRole, termLabel } from './data'
import { Panel, Title, input, button, outline } from './ui'
import { StudentHome, StudentProfile, MentorDetails, MyMentorship, HistoryPage, HelpPage } from './pages/StudentPages'
import { MentorRequests, MyStudents, MentorProfile } from './pages/MentorPages'
import CommunityPage from './pages/CommunityPage'
import {
  AdminDashboard,
  Approvals,
  AdminStudents,
  AdminMentors,
  HelpTickets,
  Statistics,
  TermSettings,
} from './pages/AdminPages'

function loadAccounts() {
  try {
    return JSON.parse(localStorage.getItem('mentoringAccounts')) || localAccounts
  } catch {
    return localAccounts
  }
}

export default function App() {
  const [data, setData] = useState(loadData)
  const [accounts, setAccounts] = useState(loadAccounts)
  const [user, setUser] = useState(null)
  const [page, setPage] = useState('Home')
  const [registering, setRegistering] = useState(false)
  const [registerRole, setRegisterRole] = useState('student')
  const [error, setError] = useState('')
  const [selectedMentor, setSelectedMentor] = useState(null)
  const [backendReady, setBackendReady] = useState(false)

  useEffect(() => {
    async function restoreSession() {
      try {
        const me = await apiMe()
        if (me?.user) {
          await login(me.user)
        }
      } catch {
        // Token expired or invalid, stay on login page
      }
    }
    restoreSession()
  }, [])

  useEffect(() => {
    if (!user || !backendReady) return
    apiRequest('/state', { method: 'PUT', body: JSON.stringify(data) }).catch((err) => console.error('Backend sync failed:', err))
  }, [data, user, backendReady])

  async function login(account) {
    setUser(account)
    try {
      const serverState = await apiRequest('/state')
      setData((current) => ({ ...current, ...serverState }))
      setBackendReady(true)
    } catch (err) {
      setError(`Backend connection failed: ${err.message}. Start the Flask server and try again.`)
      setUser(null)
      return
    }
    setPage(account.role === 'student' ? 'Home' : account.role === 'mentor' ? 'Requests' : 'Dashboard')
    setRegistering(false)
    setError('')
  }

  async function submitLogin(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    try {
      const account = await apiLogin(form.get('email'), form.get('password'))
      await login(account)
    } catch (err) {
      setError(err.message)
    }
  }

  function blacklistAccount(name, role) {
    const account = accounts.find((item) => item.name === name && item.role === role)
    setData((current) => ({
      ...current,
      blacklisted: current.blacklisted.some((item) => item.name === name && (!item.role || item.role === role))
        ? current.blacklisted
        : [...current.blacklisted, { name, email: account?.email || '', role }],
    }))
  }

  function activateAccount(name, role) {
    setData((current) => ({
      ...current,
      blacklisted: current.blacklisted.filter((item) => item.name !== name || (item.role && item.role !== role)),
    }))
  }

  async function submitRegistration(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const account = {
      name: form.get('name'), email: form.get('email'), password: form.get('password'), role: registerRole,
      program: form.get('program'), level: form.get('level'), goals: form.get('goals'),
      job: form.get('job'), industry: form.get('industry'), field: form.get('field'),
      linkedin: form.get('linkedin'), slots: Number(form.get('slots') || 0),
      background: form.get('background'), mode: form.get('mode'),
    }
    try {
      await apiRegister(account)
      if (registerRole === 'mentor') {
        setError('Mentor registration submitted. Your profile is pending IIC Admin approval. You can sign in after approval.')
        setRegistering(false)
        return
      }
      const signedIn = await apiLogin(account.email, account.password)
      await login(signedIn)
    } catch (err) {
      setError(err.message)
    }
  }

  async function createRequest(mentor, goal, message, preferences = []) {
    const currentTerm = termLabel(data.term)
    const today = new Date().toISOString().slice(0, 10)
    if ((data.term.start && today < data.term.start) || (data.term.close && today > data.term.close)) {
      alert('The mentoring request window is closed.')
      return
    }
    if (data.requests.some((item) => item.student === user.name && item.term === currentTerm)) {
      alert('You already sent a request this term.')
      return
    }
    const localRequest = {
      id: Date.now(),
      student: user.name,
      email: user.email,
      mentor: mentor.name,
      goal,
      message,
      preferences: preferences.length ? preferences : [mentor.name],
      status: 'Pending',
      term: currentTerm,
    }
    setData((current) => ({
      ...current,
      requests: [...current.requests, localRequest],
    }))
    setSelectedMentor(null)
    setPage('My Mentorship')
    // Persist formally via API (source of truth alongside app_state sync).
    try {
      const res = await apiRequest('/mentorship-requests', {
        method: 'POST',
        body: JSON.stringify({ mentor: mentor.name, goal, message, preferences: preferences.length ? preferences : [mentor.name] }),
      })
      const serverRequest = res.request || res
      setData((current) => ({
        ...current,
        requests: current.requests.map((item) => (item.id === localRequest.id ? { ...item, ...serverRequest, preferences: serverRequest.preferences || item.preferences } : item)),
      }))
    } catch (err) {
      alert(`Request saved locally, but server confirmation failed: ${err.message}`)
    }
  }

  function setRequestStatus(id, status) {
    const request = data.requests.find((item) => item.id === id)
    if (status === 'Accepted' && request) {
      const mentor = data.mentors.find((item) => item.name === request.mentor)
      const assigned = data.requests.filter(
        (item) => item.mentor === request.mentor && item.status === 'Accepted',
      ).length
      if (mentor && assigned >= mentor.slots) {
        alert('This mentor has reached their student limit.')
        return
      }
    }
    setData((current) => {
      return {
        ...current,
        requests: current.requests.map((item) => (item.id === id ? { ...item, status } : item)),
        students: request
          ? current.students.map((item) =>
              item.name === request.student
                ? {
                    ...item,
                    mentor: status === 'Accepted' ? request.mentor : status === 'Ended' ? '' : item.mentor,
                  }
                : item,
            )
          : current.students,
      }
    })
  }

  async function sendHelp(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const fileNames = Array.from(form.getAll('supporting_files') || []).map((f) => f?.name).filter(Boolean)
    const payload = {
      type: form.get('type'),
      description: form.get('description'),
      priority: form.get('priority') || 'Medium',
      urgency_level: form.get('urgency') || form.get('priority') || 'Medium',
      current_mentor: form.get('current_mentor') || '',
      reason_change: form.get('reason_change') || '',
      student_involved: form.get('student_involved') || '',
      mentorship_related: form.get('mentorship_related') || '',
      incident_category: form.get('incident_category') || '',
      incident_date: form.get('incident_date') || '',
      supporting_info: fileNames.join(', '),
    }
    try {
      const res = await apiRequest('/help-requests', { method: 'POST', body: JSON.stringify(payload) })
      const ticket = res.ticket || res
      setData((current) => ({
        ...current,
        tickets: [
          {
            ...ticket,
            name: ticket.name || ticket.user_name || user.name,
            role: ticket.role || user.role,
            type: ticket.type || ticket.ticket_type || payload.type,
            status: ticket.status || 'Submitted',
            reply: ticket.reply || '',
          },
          ...current.tickets,
        ],
      }))
      return ticket
    } catch (err) {
      // Fallback: keep local ticket so user can still track while offline
      setData((current) => ({
        ...current,
        tickets: [
          {
            id: Date.now(),
            name: user.name,
            role: user.role,
            type: payload.type,
            description: payload.description,
            priority: payload.priority,
            status: 'Submitted',
            reply: '',
          },
          ...current.tickets,
        ],
      }))
      throw err
    }
  }

  function sendChat(event, peer) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    setData((current) => ({
      ...current,
      messages: [
        ...current.messages,
        {
          from: user.name,
          to: peer,
          text: form.get('message'),
          date: new Date().toLocaleDateString(),
        },
      ],
    }))
    event.currentTarget.reset()
  }

  function saveProfile(form) {
    const profile = {
      name: user.name,
      program: form.get('program'),
      goals: form.get('goals'),
    }
    setData((current) => ({
      ...current,
      profiles: { ...(current.profiles || {}), [user.email]: profile },
      students: current.students.map((item) =>
        item.name === user.name ? { ...item, program: profile.program } : item,
      ),
    }))
  }

  function downloadReport() {
    const rows = [
      'Name,Program,Mentor,Feedback',
      ...data.students.map((item) => `${item.name},${item.program},${item.mentor || 'None'},${item.feedback}`),
    ]
    const url = URL.createObjectURL(new Blob([rows.join('\n')], { type: 'text/csv' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'mentoring-report.csv'
    link.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  function pageContent() {
    if (user.role === 'student') {
      if (page === 'Home') return <StudentHome data={data} user={user} onMentor={setSelectedMentor} />
      if (page === 'Profile')
        return <StudentProfile user={user} data={data} profile={data.profiles?.[user.email]} onSave={saveProfile} />
      if (page === 'My Mentorship')
        return <MyMentorship user={user} data={data} updateData={setData} onChat={sendChat} />
      if (page === 'Communities')
        return <CommunityPage user={user} data={data} updateData={setData} />
      if (page === 'History') return <HistoryPage role="student" user={user} data={data} />
      if (page === 'Help') return <HelpPage user={user} data={data} onSubmit={sendHelp} updateData={setData} />
    }
    if (user.role === 'mentor') {
      if (page === 'Requests') return <MentorRequests user={user} data={data} setStatus={setRequestStatus} />
      if (page === 'My Students')
        return (
          <MyStudents user={user} data={data} updateData={setData} onChat={sendChat} setStatus={setRequestStatus} />
        )
      if (page === 'Profile') return <MentorProfile user={user} data={data} updateData={setData} />
      if (page === 'Communities')
        return <CommunityPage user={user} data={data} updateData={setData} />
      if (page === 'History') return <HistoryPage role="mentor" user={user} data={data} />
      if (page === 'Help') return <HelpPage user={user} data={data} onSubmit={sendHelp} updateData={setData} />
    }
    if (user.role === 'admin') {
      if (page === 'Dashboard') return <AdminDashboard data={data} />
      if (page === 'Approvals') return <Approvals data={data} updateData={setData} onActivate={activateAccount} />
      if (page === 'Students')
        return <AdminStudents data={data} onBlacklist={blacklistAccount} onActivate={activateAccount} />
      if (page === 'Mentors')
        return <AdminMentors data={data} onBlacklist={blacklistAccount} onActivate={activateAccount} />
      if (page === 'Communities')
        return <CommunityPage user={user} data={data} updateData={setData} />
      if (page === 'Help Tickets') return <HelpTickets data={data} updateData={setData} />
      if (page === 'Statistics') return <Statistics data={data} onDownload={downloadReport} />
      if (page === 'Term Settings') return <TermSettings data={data} updateData={setData} />
    }
    return null
  }

  if (!user)
    return (
      <AuthPage
        registering={registering}
        setRegistering={setRegistering}
        registerRole={registerRole}
        setRegisterRole={setRegisterRole}
        error={error}
        setError={setError}
        onLogin={submitLogin}
        onRegister={submitRegistration}
      />
    )

  const navItems = navByRole[user.role] || []

  return (
    <div className="flex min-h-screen flex-col bg-slate-50 text-slate-900 md:grid md:grid-cols-[272px_1fr]">
      <aside className="flex flex-col gap-5 bg-gradient-to-b from-[#0f172a] via-[#131c33] to-[#1e1b4b] p-5 text-slate-100 md:sticky md:top-0 md:h-screen">
        <div className="flex items-center gap-3 px-1">
          <div className="grid size-10 place-items-center rounded-xl bg-indigo-500 text-sm font-bold text-white shadow-lg shadow-indigo-950/60">
            BS
          </div>
          <div>
            <b className="block text-sm">IITM BS</b>
            <span className="text-xs text-slate-400">Mentoring portal</span>
          </div>
        </div>
        <div className="hidden px-1 text-[10px] font-semibold uppercase tracking-widest text-slate-500 md:block">Menu</div>
        <nav className="flex gap-1 overflow-x-auto pb-1 md:grid">
          {navItems.map((item) => (
            <button
              key={item}
              onClick={() => setPage(item)}
              className={`whitespace-nowrap rounded-xl border-l-2 px-3 py-2.5 text-left text-sm transition ${
                page === item
                  ? 'border-indigo-400 bg-indigo-500/20 font-semibold text-white'
                  : 'border-transparent text-slate-300 hover:bg-white/5 hover:text-white'
              }`}
            >
              {item}
            </button>
          ))}
        </nav>
        <div className="mt-auto hidden rounded-2xl border border-white/10 bg-white/5 p-3 md:block">
          <span className="text-xs text-slate-400">Current term</span>
          <b className="mt-1 block text-sm text-slate-100">{termLabel(data.term)}</b>
          <span className="mt-1 block text-xs text-indigo-300">Requests close {data.term.close}</span>
        </div>
        <div className="mt-2 flex items-center gap-2 border-t border-white/10 pt-4 md:mt-auto md:pt-4">
          <div className="grid size-9 place-items-center rounded-full bg-indigo-500/20 text-xs font-semibold text-indigo-200">
            {user.name
              .split(' ')
              .map((part) => part[0])
              .slice(0, 2)
              .join('')}
          </div>
          <div className="min-w-0 flex-1">
            <b className="block truncate text-xs text-slate-100">{user.name}</b>
            <span className="text-xs capitalize text-slate-400">{user.role}</span>
          </div>
          <button
            title="Log out"
            className="rounded-lg px-2 py-1 text-xs text-slate-400 transition hover:bg-white/10 hover:text-white"
            onClick={async () => {
              await apiLogout()
              setUser(null)
              setBackendReady(false)
              setToken('')
              setPage('Home')
            }}
          >
            Log out
          </button>
        </div>
      </aside>
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-5 backdrop-blur lg:px-8">
          <div className="text-sm">
            <span className="text-slate-500">Mentoring / </span>
            <b className="text-slate-900">{page}</b>
          </div>
          <span className="rounded-full bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-800">
            {termLabel(data.term)}
          </span>
        </header>
        <main className="w-full flex-1 px-5 py-6 lg:px-8 lg:py-8">{pageContent()}</main>
      </div>
      {selectedMentor && (
        <MentorDetails mentor={selectedMentor} onClose={() => setSelectedMentor(null)} onRequest={createRequest} />
      )}
    </div>
  )
}

function AuthPage({
  registering,
  setRegistering,
  registerRole,
  setRegisterRole,
  error,
  setError,
  onLogin,
  onRegister,
}) {
  return (
    <main className="min-h-screen bg-slate-50 lg:grid lg:grid-cols-2">
      <section className="auth-panel relative hidden overflow-hidden px-6 py-10 text-white lg:flex lg:min-h-screen lg:flex-col lg:justify-between lg:p-14">
        <div className="hero-grid absolute inset-0 opacity-60" />
        <div className="relative z-10 flex items-center gap-3">
          <div className="grid size-11 place-items-center rounded-xl bg-indigo-500 font-bold shadow-lg shadow-indigo-950/60">BS</div>
          <div>
            <b className="block">IITM BS</b>
          </div>
        </div>
        <div className="relative z-10 mt-16 max-w-xl">
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-300">IIT Madras</p>
          <h1 className="mt-3 text-4xl font-semibold leading-tight tracking-tight xl:text-5xl">Mentoring Portal</h1>
          <p className="mt-4 text-base leading-7 text-slate-300">
            Career mentorship, community and support for BS students — connecting learners with industry mentors,
            guided by the IIC.
          </p>
          <div className="mt-8 grid gap-3 sm:grid-cols-3">
            {['Mentor matching', 'Term tracking', 'Community'].map((item) => (
              <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
                <b className="block text-sm">{item}</b>
                <span className="mt-1 block text-xs text-slate-400">IIC managed</span>
              </div>
            ))}
          </div>
        </div>
        <div className="relative z-10 text-xs text-slate-400">BS Degree Programme · Industry Interaction Council</div>
      </section>
      <section className="flex min-h-screen items-center justify-center p-5">
        <div className="w-full max-w-md animate-slide-up rounded-2xl border border-slate-200 bg-white p-7 shadow-card md:p-9">
          <div className="mb-6 lg:hidden">
            <b>IITM BS Mentoring</b>
          </div>
          <p className="text-xs font-semibold uppercase tracking-widest text-indigo-600">
            {registering ? 'Registration' : 'Account access'}
          </p>
          <h2 className="mt-2 text-2xl font-semibold">{registering ? 'Create account' : 'Sign in'}</h2>
          <p className="mb-6 mt-1 text-sm text-slate-500">
            {registering ? 'Register as a student or mentor.' : 'Use your registered email address.'}
          </p>
          {registering ? (
            <>
              <div className="mb-3 flex gap-2">
                {['student', 'mentor'].map((role) => (
                  <button
                    key={role}
                    className={registerRole === role ? button : outline}
                    onClick={() => {
                      setRegisterRole(role)
                      setError('')
                    }}
                  >
                    {role === 'student' ? 'Student' : 'Mentor'}
                  </button>
                ))}
              </div>
              <form className="grid gap-3" onSubmit={onRegister}>
                <input className={input} name="name" placeholder="Name" required />
                <input className={input} name="email" type="email" placeholder="Email" required />
                <input className={input} name="password" type="password" placeholder="Password" required />
                {registerRole === 'student' ? (
                  <>
                    <input className={input} name="program" placeholder="Degree program" required />
                    <select className={input} name="level">
                      <option>Level 1</option>
                      <option>Level 2</option>
                      <option>Level 3</option>
                      <option>Level 4</option>
                    </select>
                    <textarea className={input} name="goals" placeholder="Career goals" />
                  </>
                ) : (
                  <>
                    <input className={input} name="job" placeholder="Current role" required />
                    <input className={input} name="industry" placeholder="Industry" required />
                    <input className={input} name="field" placeholder="Expertise" required />
                    <input className={input} name="linkedin" placeholder="LinkedIn (optional)" />
                    <input className={input} name="slots" type="number" min="1" placeholder="Max students" required />
                    <textarea className={input} name="background" placeholder="Professional background" required />
                    <select className={input} name="mode">
                      <option>Online</option>
                      <option>Hybrid</option>
                      <option>In person</option>
                    </select>
                  </>
                )}
                {error && <p className="text-sm text-red-600">{error}</p>}
                <button className={button} type="submit">Create account</button>
              </form>
            </>
          ) : (
            <>
              <form className="grid gap-4" onSubmit={onLogin}>
                <label className="grid gap-1.5 text-sm font-medium">
                  Email
                  <input
                    className={input}
                    name="email"
                    type="email"
                    placeholder="name@iitm.ac.in"
                    autoComplete="username"
                    required
                  />
                </label>
                <label className="grid gap-1.5 text-sm font-medium">
                  Password
                  <input
                    className={input}
                    name="password"
                    type="password"
                    placeholder="Password"
                    autoComplete="current-password"
                    required
                  />
                </label>
                {error && <p className="text-sm text-red-600">{error}</p>}
                <button className={`${button} mt-1 w-full`} type="submit">Sign in</button>
              </form>
            </>
          )}
          <div className="mt-6 border-t border-slate-100 pt-4 text-sm text-slate-500">
            {registering ? 'Already registered?' : 'New student or mentor?'}{' '}
            <button
              className="font-medium text-indigo-700 hover:underline"
              onClick={() => {
                setRegistering(!registering)
                setError('')
              }}
            >
              {registering ? 'Sign in' : 'Register'}
            </button>
          </div>
        </div>
      </section>
    </main>
  )
}
