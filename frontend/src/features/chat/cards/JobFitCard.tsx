import { CircleCheck, CircleMinus, Contrast, FileText } from 'lucide-react';
import { messages } from '../../../i18n';
import type { Citation } from '../api';
import { InlineText } from '../AnswerText';
import { CardFrame } from './CardFrame';
import type { JobFitCardData, RequirementStatus } from './cardData';

const STATUS = {
  met: { icon: CircleCheck, tone: 'text-accent', bar: 'bg-accent' },
  partial: { icon: Contrast, tone: 'text-text', bar: 'bg-cover-dot' },
  missing: { icon: CircleMinus, tone: 'text-muted', bar: 'bg-border' },
} satisfies Record<RequirementStatus, unknown>;

/** The fit with a job offer. The totals are counted here from the rows, so they can't
 * disagree with them (docs/API.md); gaps show as plainly as strengths. */
export function JobFitCard({ data, citations }: { data: JobFitCardData; citations: Citation[] }) {
  const { cards } = messages;
  const count = (status: RequirementStatus) =>
    data.requirements.filter((row) => row.status === status).length;
  const summary = cards.jobFitSummary(count('met'), data.requirements.length, count('partial'));
  return (
    <CardFrame>
      <div className="flex items-center gap-3 border-b border-border px-4 py-3.5">
        <span
          aria-hidden="true"
          className="flex size-10 shrink-0 items-center justify-center rounded-tile bg-accent-soft text-accent"
        >
          <FileText size={20} />
        </span>
        <div className="min-w-0">
          <h3 className="text-card-title font-semibold">{cards.jobFit}</h3>
          <p className="text-small text-muted">{data.title}</p>
        </div>
      </div>
      <div className="px-4 pt-3 pb-1">
        <p className="text-small font-semibold">{summary}</p>
        <div
          aria-hidden="true"
          className="mt-2 grid gap-[3px]"
          style={{ gridTemplateColumns: `repeat(${data.requirements.length}, minmax(0, 1fr))` }}
        >
          {data.requirements.map((row, index) => (
            <span key={index} className={`h-1.5 rounded-[3px] ${STATUS[row.status].bar}`} />
          ))}
        </div>
      </div>
      <ul className="px-4 py-1">
        {data.requirements.map((row) => {
          const { icon: Icon, tone } = STATUS[row.status];
          return (
            <li
              key={row.requirement}
              className="flex gap-2.5 border-border py-2.5 not-first:border-t"
            >
              <Icon size={18} aria-hidden="true" className={`mt-px shrink-0 ${tone}`} />
              <div className="min-w-0 flex-1">
                <p className="flex items-baseline justify-between gap-2 font-semibold">
                  <span>{row.requirement}</span>
                  <span className={`text-label whitespace-nowrap ${tone}`}>
                    {cards[row.status]}
                  </span>
                </p>
                <p className="mt-0.5 text-small text-muted">
                  <InlineText text={row.evidence} citations={citations} />
                </p>
              </div>
            </li>
          );
        })}
      </ul>
      <p className="border-t border-border px-4 py-3 text-label text-muted">{cards.jobFitNote}</p>
    </CardFrame>
  );
}
