/**
 * The profile card's cover: a dot pattern and the assistant's real graph, the guardrail, the
 * supervisor as a filled hub and the three agents (ADR-018).
 *
 * While the assistant thinks, the graph lights up the path of the question as the API's node
 * events arrive (ADR-020), and it rests again when the answer starts. Under reduced motion,
 * only the agent that answers fills.
 */
import { AGENTS, type Agent, litPath } from './graphPath';

const edge = 'fill-none stroke-cover-line stroke-[1.5]';
const edgeLit = 'motion-safe:stroke-accent motion-safe:stroke-2';
const node = 'stroke-accent stroke-2';
const nodeLit = 'motion-safe:fill-accent';
// Colours change in 200 ms, the duration of the graph's steps (DESIGN.md)
const step = 'transition-[fill,stroke,stroke-width] duration-(--duration-base) ease-move';

export function CoverGraph({ activeNode = null }: { activeNode?: string | null }) {
  const lit = litPath(activeNode);
  return (
    <div
      aria-hidden="true"
      className="relative h-16 bg-(--color-cover)"
      style={{
        backgroundImage: 'radial-gradient(var(--color-cover-dot) 1.3px, transparent 1.5px)',
        backgroundSize: '14px 14px',
      }}
    >
      <svg
        viewBox="0 0 280 64"
        preserveAspectRatio="xMaxYMid meet"
        className="absolute inset-0 block size-full"
      >
        <path
          data-part="guardrail-supervisor"
          data-lit={lit.supervisor}
          className={`${edge} ${step} ${lit.supervisor ? edgeLit : ''}`}
          d="M124 42 168 30"
        />
        {(Object.keys(AGENTS) as Agent[]).map((agent) => (
          <path
            key={agent}
            data-part={`supervisor-${agent}`}
            data-lit={lit.agent === agent}
            className={`${edge} ${step} ${lit.agent === agent ? edgeLit : ''}`}
            d={`M168 30 ${AGENTS[agent].x} ${AGENTS[agent].y}`}
          />
        ))}
        <circle
          data-part="guardrail"
          data-lit={lit.guardrail}
          className={`${node} ${step} fill-card ${lit.guardrail ? nodeLit : ''}`}
          cx="124"
          cy="42"
          r="4"
        />
        <circle
          data-part="supervisor"
          data-lit={lit.supervisor}
          className={`origin-center fill-accent [transform-box:fill-box] ${lit.supervisor && !lit.agent ? 'motion-safe:animate-hub-pulse' : ''}`}
          cx="168"
          cy="30"
          r="6"
        />
        {(Object.keys(AGENTS) as Agent[]).map((agent) => (
          <circle
            key={agent}
            data-part={agent}
            data-lit={lit.agent === agent}
            className={`${node} ${step} ${lit.agent === agent ? 'fill-accent' : 'fill-card'}`}
            cx={AGENTS[agent].x}
            cy={AGENTS[agent].y}
            r="4"
          />
        ))}
      </svg>
    </div>
  );
}
