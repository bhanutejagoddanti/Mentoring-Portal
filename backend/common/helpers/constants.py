"""Shared constants for the IITM BS Mentoring Portal backend."""

DEFAULT_TERM = {
    'start': '2026-09-01',
    'close': '2026-11-30',
    'end': '2026-12-20',
    'minMeetings': 3,
}

TERM_MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

HELP_STATUSES = [
    'Submitted',
    'Under Review',
    'Additional Information Required',
    'Approved',
    'Rejected',
    'Resolved',
    'Closed',
]

HELP_CATEGORIES = [
    'Mentor Change',
    'Mentor Not Responding',
    'Mentor Unavailable',
    'Scheduling',
    'Mentorship Concern',
    'Conduct',
    'Technical',
    'Academic or Career',
    'Other',
]

PRIORITIES = ['Low', 'Medium', 'High', 'Urgent']

COMMUNITY_STATUSES = ['Pending', 'Approved', 'Rejected', 'Archived']
COMMUNITY_VISIBILITIES = ['public', 'private']
MENTOR_DECISIONS = ['Approved', 'Rejected', 'Requested Changes']
