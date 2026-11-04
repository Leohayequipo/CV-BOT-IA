/** The path of a question through the assistant's graph, as the cover draws it. */

// The agents' places on the cover; the guardrail and the supervisor come before all three
export const AGENTS = {
  profile: { x: 214, y: 14 },
  job_fit: { x: 222, y: 48 },
  contact: { x: 258, y: 28 },
} as const;

export type Agent = keyof typeof AGENTS;

function isAgent(node: string): node is Agent {
  return node in AGENTS;
}

/** Which parts of the path are lit, for the graph step now working. */
export function litPath(node: string | null) {
  return {
    guardrail: node !== null,
    supervisor: node !== null && node !== 'guardrail',
    agent: node !== null && isAgent(node) ? node : null,
  };
}
