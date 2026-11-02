/**
 * The profile card's cover: a dot pattern and the assistant's real graph, the guardrail, the
 * supervisor as a filled hub and the three agents (ADR-018). Step 4.7 lights up its path.
 */
export function CoverGraph() {
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
          className="fill-none stroke-cover-line stroke-[1.5]"
          d="M124 42 168 30M168 30 214 14M168 30 222 48M168 30 258 28"
        />
        <circle className="fill-card stroke-accent stroke-2" cx="124" cy="42" r="4" />
        <circle className="fill-accent" cx="168" cy="30" r="6" />
        <circle className="fill-card stroke-accent stroke-2" cx="214" cy="14" r="4" />
        <circle className="fill-card stroke-accent stroke-2" cx="222" cy="48" r="4" />
        <circle className="fill-card stroke-accent stroke-2" cx="258" cy="28" r="4" />
      </svg>
    </div>
  );
}
