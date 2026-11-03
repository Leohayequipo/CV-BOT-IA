/** The interface copy in English, the default language (ADR-015). */
export const en = {
  site: {
    monogram: 'LM',
    subtitle: 'Conversational CV',
    downloadCv: 'Download CV',
    opensInNewTab: '(opens in a new tab)',
  },
  nav: {
    label: 'Sections',
    chat: 'Chat',
    experience: 'Experience',
    projects: 'Projects',
    skills: 'Skills',
    contact: 'Contact',
  },
  theme: {
    toDark: 'Switch to dark mode',
    toLight: 'Switch to light mode',
  },
  profile: {
    label: "Leonardo's profile",
    euBadge: 'EU citizen, no visa needed',
    euBadgeShort: 'EU citizen',
    worksAt: 'Works today at',
    contact: 'Contact',
    whatsapp: 'WhatsApp',
    linkedin: 'LinkedIn',
    github: 'GitHub',
    leaveMessage: 'Leave him a message',
    workMode: 'Work mode',
  },
  workModes: {
    remote: 'Remote',
    hybrid: 'Hybrid',
    onsite: 'On-site',
  },
  chat: {
    label: "Chat with Leonardo's assistant",
    assistant: "Leonardo's assistant",
    subtitle: 'Answers from his CV and cites every source',
    visitor: 'You',
    newConversation: 'New conversation',
    greeting:
      "Hi, I'm Leonardo's assistant. I can tell you about his experience, his projects and his " +
      'stack, check how he fits a job offer, or help you contact him. Everything comes from his ' +
      'CV, and I cite the source of every fact.',
  },
  shortcuts: {
    label: 'Shortcuts',
    start: 'To get started',
    ai: { title: 'AI experience', subtitle: 'RAG, agents and voice' },
    servime: { title: 'ServiME', subtitle: 'His SaaS in production' },
    eu: { title: 'Working in the EU', subtitle: 'Citizenship and work mode' },
    leadership: { title: 'Leadership', subtitle: 'A team of 8 developers' },
    experience: 'Experience',
    wholeCareer: 'See his whole career',
    openSource: 'Open-source project',
    seeHowItsBuilt: "See how it's built",
  },
  // What the shortcuts ask the assistant
  questions: {
    ai: 'What AI experience does he have?',
    servime: 'What is ServiME?',
    eu: 'Can he work in the EU?',
    leadership: 'Has he led teams?',
    experience: 'Show me his experience',
    projects: 'See his projects',
    skills: "What's his stack?",
    contact: "I'd like to leave him a message",
  },
} as const;
