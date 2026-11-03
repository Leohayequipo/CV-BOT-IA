import { ExternalLink as ExternalLinkIcon, LayoutGrid, Utensils } from 'lucide-react';
import { ExternalLink } from '../../../components/ui/ExternalLink';
import { Pill } from '../../../components/ui/Pill';
import type { Citation } from '../api';
import { InlineText } from '../AnswerText';
import { CardFrame } from './CardFrame';
import type { ProjectCardData } from './cardData';

// Projects with their own colours and logo icon in DESIGN.md; any other uses the teal set
const BRANDS: Partial<Record<string, typeof Utensils>> = { servime: Utensils };

export function ProjectCard({ data, citations }: { data: ProjectCardData; citations: Citation[] }) {
  const brandIcon = data.brand ? BRANDS[data.brand] : undefined;
  const Icon = brandIcon ?? LayoutGrid;
  const brandClass = brandIcon ? `brand-${data.brand}` : '';
  return (
    <CardFrame className={`project-brand ${brandClass}`}>
      <div
        aria-hidden="true"
        className="h-11 bg-(--brand-band)"
        style={{
          backgroundImage: 'radial-gradient(var(--brand-dot) 1.3px, transparent 1.5px)',
          backgroundSize: '14px 14px',
        }}
      />
      <div className="flex flex-col gap-2.5 px-4 pb-3.5">
        <span
          aria-hidden="true"
          className="-mt-[26px] flex size-[52px] items-center justify-center self-start rounded-card border-3 border-card bg-(--brand-tile) text-(--brand-ink)"
        >
          <Icon size={22} />
        </span>
        <div>
          <h3 className="text-card-title font-semibold">{data.name}</h3>
          <p className="text-small text-muted">{data.summary}</p>
        </div>
        <p className="text-small">
          {data.role} · {data.period}
        </p>
        <p className="text-small font-semibold text-accent">
          <InlineText text={data.highlight} citations={citations} />
        </p>
        <ul className="flex flex-wrap gap-1.5">
          {data.stack.map((technology) => (
            <Pill key={technology}>{technology}</Pill>
          ))}
        </ul>
        {data.url && (
          <ExternalLink
            href={data.url}
            className="inline-flex items-center gap-1.5 self-start text-small font-semibold text-accent hover:text-text"
          >
            {/* toCard only accepts addresses that parse */}
            {new URL(data.url).host}
            <ExternalLinkIcon size={14} aria-hidden="true" />
          </ExternalLink>
        )}
      </div>
    </CardFrame>
  );
}
