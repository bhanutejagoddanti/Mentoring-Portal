export const localAccounts = [
  {
    name: 'Ananya Menon',
    email: 'student@iitm.ac.in',
    password: 'student123',
    role: 'student',
  },
  {
    name: 'Arjun Nair',
    email: 'mentor@iitm.ac.in',
    password: 'mentor123',
    role: 'mentor',
  },
  {
    name: 'IIC Admin',
    email: 'admin@iitm.ac.in',
    password: 'admin123',
    role: 'admin',
  },
]

export const starterData = {
  mentors: [
    {
      id: 1,
      name: 'Arjun Nair',
      title: 'Product Analyst',
      field: 'Data & Product',
      industry: 'Finance',
      role: 'Product Analyst',
      mode: 'Online',
      slots: 2,
      bio: 'Product analytics and data strategy.',
      background: 'Product analytics at a fintech company.',
      linkedin: 'https://linkedin.com',
      approved: true,
      active: true,
    },
    {
      id: 2,
      name: 'Kavya Iyer',
      title: 'Software Engineer',
      field: 'IT',
      industry: 'Technology',
      role: 'Engineer',
      mode: 'Online',
      slots: 1,
      bio: 'Software engineering and cloud systems.',
      background: 'Builds cloud services for a technology company.',
      linkedin: '',
      approved: true,
      active: true,
    },
    {
      id: 3,
      name: 'Meera Shah',
      title: 'Research Scientist',
      field: 'ML',
      industry: 'Healthcare',
      role: 'Research',
      mode: 'Online',
      slots: 2,
      bio: 'Machine learning, research and higher studies.',
      background: 'Applied machine learning in healthcare.',
      linkedin: 'https://linkedin.com',
      approved: true,
      active: true,
    },
    {
      id: 4,
      name: 'Rohan Das',
      title: 'Founder',
      field: 'Business',
      industry: 'Education',
      role: 'Founder',
      mode: 'Hybrid',
      slots: 3,
      bio: 'Starting a company and building products.',
      background: 'Founder in education technology.',
      linkedin: '',
      approved: true,
      active: true,
    },
    {
      id: 6,
      name: 'Nikhil Varma',
      title: 'Business Analyst',
      field: 'Finance',
      industry: 'Consulting',
      role: 'Analyst',
      mode: 'Online',
      slots: 2,
      bio: 'Consulting, finance and case interviews.',
      background: 'Business analysis and consulting.',
      linkedin: '',
      approved: true,
      active: true,
    },
    {
      id: 5,
      name: 'Sana Ahmed',
      title: 'UX Researcher',
      field: 'Design',
      industry: 'Technology',
      role: 'Research',
      mode: 'Online',
      slots: 2,
      bio: 'User research and product design.',
      background: 'Research lead for consumer products.',
      linkedin: '',
      approved: false,
      active: true,
    },
  ],
  requests: [
    {
      id: 1,
      student: 'Ishita Rao',
      email: 'ishita@iitm.ac.in',
      mentor: 'Arjun Nair',
      goal: 'I want to explore product analytics roles.',
      message: 'Can we discuss portfolio projects?',
      status: 'Pending',
      term: 'Sep–Dec 2026',
    },
  ],
  students: [
    {
      name: 'Ananya Menon',
      program: 'BS Data Science',
      mentor: '',
      feedback: '—',
    },
    {
      name: 'Ishita Rao',
      program: 'BS Data Science',
      mentor: '',
      feedback: '—',
    },
    {
      name: 'Rohan Singh',
      program: 'BS Electronic Systems',
      mentor: 'Kavya Iyer',
      feedback: '4 / 5',
    },
  ],
  tasks: [
    {
      id: 1,
      student: 'Ananya Menon',
      title: 'Update my project portfolio',
      done: false,
    },
  ],
  meetings: [],
  messages: [],
  profiles: {},
  history: [
    {
      role: 'student',
      term: 'Jan–Apr 2026',
      person: 'Kavya Iyer',
      meetings: 3,
      note: 'Software engineering and cloud systems',
    },
    {
      role: 'mentor',
      term: 'Jan–Apr 2026',
      person: 'Dev Patel',
      meetings: 3,
      note: 'Career planning and project work',
    },
  ],
  tickets: [
    {
      id: 1,
      name: 'Rohan Singh',
      role: 'student',
      type: 'Meeting issue',
      description: 'Need help finding a time for the next meeting.',
      status: 'Open',
      reply: '',
    },
    {
      id: 2,
      name: 'Kavya Iyer',
      role: 'mentor',
      type: 'Other',
      description: 'Student has not replied to the last message.',
      status: 'Open',
      reply: '',
    },
  ],
  blacklisted: [{ name: 'Inactive account', email: 'old@iitm.ac.in' }],
  term: {
    start: '2026-09-01',
    close: '2026-11-30',
    end: '2026-12-20',
    minMeetings: 3,
  },
}

export const fields = ['IT', 'ML', 'Finance', 'Data & Product', 'Business', 'Design']
export const navByRole = {
  student: ['Home', 'Profile', 'Chat', 'My Mentorship', 'Communities', 'History', 'Help'],
  mentor: ['Requests', 'My Students', 'Chat', 'Profile', 'Communities', 'History', 'Help'],
  admin: ['Dashboard', 'Approvals', 'Students', 'Mentors', 'Chat', 'Communities', 'Help Tickets', 'Statistics', 'Term Settings'],
}

export function loadData() {
  try {
    const saved = JSON.parse(localStorage.getItem('mentoringData'))
    return saved ? { ...starterData, ...saved } : starterData
  } catch {
    return starterData
  }
}

export function termLabel(term) {
  if (!term?.start || !term?.end) return 'Current term'
  const start = new Date(`${term.start}T12:00:00`)
  const end = new Date(`${term.end}T12:00:00`)
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return 'Current term'
  const month = (date) => date.toLocaleString('en', { month: 'short' })
  const startYear = start.getFullYear()
  const endYear = end.getFullYear()
  return `${month(start)}–${month(end)} ${startYear === endYear ? endYear : `${startYear}–${endYear}`}`
}
