import type { Messages } from './en';

/**
 * The interface copy in Spanish, with voseo (ADR-018). It comes from the approved designs;
 * a text the designs don't show follows DESIGN.md's copy rules.
 */
export const es: Messages = {
  site: {
    monogram: 'LM',
    subtitle: 'CV conversacional',
    downloadCv: 'Descargar CV',
    opensInNewTab: '(se abre en una pestaña nueva)',
  },
  nav: {
    label: 'Secciones',
    chat: 'Chat',
    experience: 'Experiencia',
    projects: 'Proyectos',
    skills: 'Skills',
    contact: 'Contacto',
  },
  language: {
    label: 'Idioma',
  },
  theme: {
    toDark: 'Cambiar a modo oscuro',
    toLight: 'Cambiar a modo claro',
  },
  profile: {
    label: 'Perfil de Leonardo',
    euBadge: 'Ciudadano UE, sin visado',
    euBadgeShort: 'Ciudadano UE',
    worksAt: 'Trabaja hoy en',
    contact: 'Contacto',
    whatsapp: 'WhatsApp',
    linkedin: 'LinkedIn',
    github: 'GitHub',
    leaveMessage: 'Dejarle un mensaje',
    workMode: 'Modalidad',
  },
  workModes: {
    remote: 'Remoto',
    hybrid: 'Híbrido',
    onsite: 'Presencial',
  },
  chat: {
    label: 'Chat con el asistente de Leonardo',
    assistant: 'Asistente de Leonardo',
    subtitle: 'Responde con datos de su CV y cita cada fuente',
    visitor: 'Vos',
    newConversation: 'Nueva conversación',
    greeting:
      'Hola, soy el asistente de Leonardo. Te cuento sobre su experiencia, sus proyectos y su ' +
      'stack, analizo si encaja con una oferta de trabajo o te ayudo a contactarlo. Todo sale de ' +
      'su CV, y cito la fuente de cada dato.',
    firstSuggestions: [
      '¿Qué experiencia tiene con IA?',
      '¿Qué es ServiME?',
      '¿Puede trabajar en la UE?',
      '¿Lideró equipos?',
      'Analizar una oferta',
    ],
    suggestionsLabel: 'Preguntas sugeridas',
    questionLabel: 'Tu pregunta',
    placeholder: 'Preguntá algo o pegá una oferta de trabajo…',
    placeholderShort: 'Preguntá algo o pegá una oferta…',
    limitedPlaceholder: 'Vas a poder preguntar de nuevo en unos minutos',
    send: 'Enviar pregunta',
    stop: 'Detener respuesta',
    typing: 'Escribiendo',
    stopped: 'Detuviste esta respuesta.',
    analyseOffer: 'Analizar una oferta',
    contactHim: 'Contactarlo',
    onlyCv: 'Solo usa datos de su CV',
    retry: 'Reintentar',
    retrying: 'Reintentando…',
    source: 'Fuente',
    sources: 'Fuentes',
    newMessage: 'Nuevo mensaje',
    contactSent:
      'Listo, le envié tu mensaje a Leonardo. ¿Querés seguir preguntando algo mientras tanto?',
    afterContact: ['¿Qué experiencia tiene con IA?', 'Analizar una oferta'],
    networkError: 'No se pudo conectar. Revisá tu conexión y volvé a intentarlo.',
    limit:
      'Llegaste al límite de preguntas por ahora. Volvé a intentarlo en unos minutos; mientras ' +
      'tanto, podés escribirle por WhatsApp o LinkedIn.',
  },
  cards: {
    experience: 'Experiencia',
    mainStack: 'Stack principal',
    jobFit: 'Encaje con la oferta',
    met: 'Cumple',
    partial: 'En parte',
    missing: 'Sin evidencia',
    jobFitSummary: (met, total, partial) =>
      `Cumple ${met} de ${total} requisitos` + (partial > 0 ? `, ${partial} en parte` : ''),
    jobFitNote: 'Basado solo en su CV. Si algo no figura, podés preguntárselo a Leonardo.',
    contactTitle: 'Mensaje para Leonardo',
    contactFrom: 'De',
    contactEmail: 'Email',
    contactMessage: 'Mensaje',
    contactSend: 'Enviar mensaje',
    contactSending: 'Enviando…',
    contactCorrect: 'Corregir',
    contactPrivacy: 'Tu email solo se usa para que Leonardo pueda responderte.',
    contactConfirmed: (time) => `Confirmado a las ${time}`,
    sentTitle: 'Mensaje enviado',
    sentLine: 'Le llegó por email a Leonardo, con tu dirección para que pueda responderte.',
    sentToday: (time) => `Hoy, ${time}`,
  },
  shortcuts: {
    label: 'Atajos',
    start: 'Para empezar',
    ai: { title: 'Experiencia con IA', subtitle: 'RAG, agentes y voz' },
    servime: { title: 'ServiME', subtitle: 'Su SaaS en producción' },
    eu: { title: 'Trabajar en la UE', subtitle: 'Ciudadanía y modalidad' },
    leadership: { title: 'Liderazgo', subtitle: 'Un equipo de 8 desarrolladores' },
    experience: 'Experiencia',
    wholeCareer: 'Ver todo el recorrido',
    openSource: 'Proyecto de código abierto',
    seeHowItsBuilt: 'Ver cómo está hecho',
  },
  // What the shortcuts ask the assistant
  questions: {
    ai: '¿Qué experiencia tiene con IA?',
    servime: '¿Qué es ServiME?',
    eu: '¿Puede trabajar en la UE?',
    leadership: '¿Lideró equipos?',
    experience: 'Mostrame su experiencia',
    projects: 'Ver sus proyectos',
    skills: '¿Cuál es su stack?',
    contact: 'Quiero dejarle un mensaje',
    offer: 'Analizar una oferta',
    correct: 'Quiero cambiar algo del mensaje',
  },
};
