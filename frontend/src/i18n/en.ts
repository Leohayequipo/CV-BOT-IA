import { lowerFirst } from './format';

/** The interface copy in English, the default language (ADR-015). es.ts has the same shape. */
export const en = {
  site: {
    monogram: 'LM',
    subtitle: 'Conversational CV',
    downloadCv: 'Download CV',
    opensInNewTab: '(opens in a new tab)',
    skipToQuestion: 'Skip to the question box',
  },
  nav: {
    label: 'Sections',
    chat: 'Chat',
    experience: 'Experience',
    projects: 'Projects',
    skills: 'Skills',
    contact: 'Contact',
  },
  language: {
    label: 'Language',
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
    // How the profile's values read in a sentence (content/profile.yaml)
    citizenship: (location: string, citizenship: string) =>
      `${location} · Citizenship: ${citizenship}`,
    language: (name: string, level: string) => `${name} (${lowerFirst(level)})`,
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
    conversation: 'Conversation',
    newConversation: 'New conversation',
    greeting:
      "Hi, I'm Leonardo's assistant. I can tell you about his experience, his projects and his " +
      'stack, check how he fits a job offer, or help you contact him. Everything comes from his ' +
      'CV, and I cite the source of every fact.',
    firstSuggestions: [
      'What AI experience does he have?',
      'What is ServiME?',
      'Can he work in the EU?',
      'Has he led teams?',
      'Analyse a job offer',
    ],
    suggestionsLabel: 'Suggested questions',
    questionLabel: 'Your question',
    placeholder: 'Ask anything or paste a job offer…',
    // On a phone, where the box is narrower
    placeholderShort: 'Ask anything or paste a job offer…',
    limitedPlaceholder: 'You can ask again in a few minutes',
    send: 'Send question',
    stop: 'Stop answer',
    typing: 'Typing',
    stopped: 'You stopped this answer.',
    analyseOffer: 'Analyse a job offer',
    contactHim: 'Contact him',
    onlyCv: 'Only uses data from his CV',
    // Required by the privacy rules: what visitors type is traced, with contact details masked
    logged: 'Conversations may be logged to improve the assistant.',
    retry: 'Retry',
    retrying: 'Retrying…',
    source: 'Source',
    sources: 'Sources',
    newMessage: 'New message',
    contactSent:
      "Done, I've sent your message to Leonardo. Would you like to keep asking something meanwhile?",
    afterContact: ['What AI experience does he have?', 'Analyse a job offer'],
    // Two sentences, as every error: what happened, then what to do
    networkError: "Couldn't connect. Check your connection and try again.",
    limit:
      "You've reached the question limit for now. Try again in a few minutes; meanwhile, you " +
      'can write to him on WhatsApp or LinkedIn.',
  },
  cards: {
    experience: 'Experience',
    mainStack: 'Main stack',
    jobFit: 'Fit with the offer',
    met: 'Meets',
    partial: 'In part',
    missing: 'No evidence',
    jobFitSummary: (met: number, total: number, partial: number) =>
      `Meets ${met} of ${total} requirements` + (partial > 0 ? `, ${partial} in part` : ''),
    jobFitNote: "Based only on his CV. If something isn't there, you can ask Leonardo.",
    contactTitle: 'Message for Leonardo',
    contactFrom: 'From',
    contactEmail: 'Email',
    contactMessage: 'Message',
    contactSend: 'Send message',
    contactSending: 'Sending…',
    contactCorrect: 'Correct',
    contactPrivacy: 'Your email is only used so Leonardo can reply to you.',
    contactConfirmed: (time: string) => `Confirmed at ${time}`,
    sentTitle: 'Message sent',
    sentLine: 'Leonardo got it by email, with your address so he can reply.',
    sentToday: (time: string) => `Today, ${time}`,
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
    offer: 'Analyse a job offer',
    correct: "I'd like to change something in the message",
  },
};

export type Messages = typeof en;
