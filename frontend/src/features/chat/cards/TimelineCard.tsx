import { InitialsTile } from '../../../components/ui/InitialsTile';
import { messages } from '../../../i18n';
import { CardFrame } from './CardFrame';
import type { TimelineCardData } from './cardData';

export function TimelineCard({ data }: { data: TimelineCardData }) {
  return (
    <CardFrame className="px-4 py-3.5">
      <h3 className="mb-3 text-card-title font-semibold">{messages.cards.experience}</h3>
      <ol className="flex flex-col gap-3">
        {data.items.map((item) => (
          <li key={`${item.company}-${item.period}`} className="flex gap-3">
            <InitialsTile initials={item.initials} size="sm" />
            <div className="min-w-0">
              <p className="font-semibold">{item.role}</p>
              <p className="text-small">{item.company}</p>
              <p className="text-label text-muted">{item.period}</p>
            </div>
          </li>
        ))}
      </ol>
    </CardFrame>
  );
}
